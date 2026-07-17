#!/usr/bin/env bash

set -euo pipefail

lease_seconds=14400
script_dir=$(cd "$(dirname "$0")" && pwd)
script_path="$script_dir/$(basename "$0")"

fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

has_session() {
  tmux has-session -t "$1" 2>/dev/null
}

session_option() {
  tmux show-options -v -t "$1" "$2" 2>/dev/null || true
}

url_is_healthy() {
  curl -s -o /dev/null --max-time 2 "http://127.0.0.1:$1/"
}

watch_lease() {
  watch_session=$1

  while has_session "$watch_session"; do
    if ! tmux list-windows -t "$watch_session" -F '#{window_name}' 2>/dev/null | grep -Fxq server; then
      tmux kill-session -t "$watch_session" 2>/dev/null || true
      exit 0
    fi

    expires_at=$(session_option "$watch_session" @shared_dev_expires_at)
    now=$(date +%s)

    if [ -n "$expires_at" ] && [ "$expires_at" != 0 ] && [ "$now" -ge "$expires_at" ]; then
      tmux kill-session -t "$watch_session" 2>/dev/null || true
      exit 0
    fi

    sleep 60
  done
}

command_name=help
if [ "$#" -gt 0 ]; then
  command_name=$1
  shift
fi

if [ "$command_name" = __watch ]; then
  [ "$#" -eq 1 ] || fail 'watcher requires a session name'
  watch_lease "$1"
  exit 0
fi

for required_tool in tmux curl lsof; do
  command -v "$required_tool" >/dev/null 2>&1 || fail "missing required tool: $required_tool"
done

project=$(pwd -P)
session=$(basename "$project")
state_dir="$project/.dev"
env_file="$state_dir/server.env"
log_file="$state_dir/dev.log"

read_port() {
  [ -f "$env_file" ] || return 1
  port=$(sed -n 's/^DEV_PORT=//p' "$env_file" | tail -n 1)
  case "$port" in
    ''|*[!0-9]*) fail "invalid DEV_PORT in $env_file" ;;
  esac
  printf '%s\n' "$port"
}

choose_port() {
  candidate=4300
  while [ "$candidate" -le 4399 ]; do
    if ! lsof -nP -iTCP:"$candidate" -sTCP:LISTEN >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
    candidate=$((candidate + 1))
  done
  fail 'no free port found between 4300 and 4399'
}

prepare_state() {
  mkdir -p "$state_dir"

  common_git_dir=$(git -C "$project" rev-parse --git-common-dir 2>/dev/null || true)
  if [ -n "$common_git_dir" ]; then
    case "$common_git_dir" in
      /*) exclude_file="$common_git_dir/info/exclude" ;;
      *) exclude_file="$project/$common_git_dir/info/exclude" ;;
    esac
    mkdir -p "$(dirname "$exclude_file")"
    if ! grep -Fxq '.dev/' "$exclude_file" 2>/dev/null; then
      printf '\n.dev/\n' >> "$exclude_file"
    fi
  fi
}

assert_managed_session() {
  managed=$(session_option "$session" @shared_dev_managed)
  session_project=$(session_option "$session" @shared_dev_project)
  [ "$managed" = 1 ] || fail "tmux session '$session' exists but is not managed by this skill"
  [ "$session_project" = "$project" ] || fail "tmux session '$session' belongs to $session_project"
}

renew_lease() {
  current_expiry=$(session_option "$session" @shared_dev_expires_at)
  if [ "$current_expiry" != 0 ]; then
    tmux set-option -t "$session" @shared_dev_expires_at "$(( $(date +%s) + lease_seconds ))"
  fi
}

show_status() {
  has_session "$session" || fail "no managed dev server for $project"
  assert_managed_session
  port=$(session_option "$session" @shared_dev_port)
  expires_at=$(session_option "$session" @shared_dev_expires_at)

  if url_is_healthy "$port"; then
    health=healthy
  else
    health=unhealthy
  fi

  if [ "$expires_at" = 0 ]; then
    lease=kept
  else
    remaining=$((expires_at - $(date +%s)))
    if [ "$remaining" -lt 0 ]; then
      remaining=0
    fi
    lease="${remaining}s remaining"
  fi

  printf 'session=%s\nproject=%s\nurl=http://127.0.0.1:%s/\nhealth=%s\nlease=%s\n' \
    "$session" "$project" "$port" "$health" "$lease"
}

start_server() {
  prepare_state

  port=$(read_port || true)
  if [ -z "$port" ]; then
    port=$(choose_port)
    printf 'DEV_PORT=%s\n' "$port" > "$env_file"
  fi

  if has_session "$session"; then
    assert_managed_session
    existing_port=$(session_option "$session" @shared_dev_port)
    [ "$existing_port" = "$port" ] || fail "managed session uses port $existing_port but $env_file contains $port"
    url_is_healthy "$port" || fail "managed session is unhealthy; inspect $log_file"
    renew_lease
    show_status
    return 0
  fi

  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    fail "port $port is already in use by an unmanaged process"
  fi

  [ -f "$project/package.json" ] || fail "package.json not found in $project"

  if [ -f "$project/pnpm-lock.yaml" ]; then
    dev_command="pnpm run dev --port $port"
  elif [ -f "$project/bun.lock" ] || [ -f "$project/bun.lockb" ]; then
    dev_command="bun run dev --port $port"
  elif [ -f "$project/yarn.lock" ]; then
    dev_command="yarn run dev --port $port"
  elif [ -f "$project/package-lock.json" ]; then
    dev_command="npm run dev -- --port $port"
  else
    fail 'cannot determine package manager from a lockfile'
  fi

  : > "$log_file"
  tmux new-session -d -s "$session" -n server -c "$project" "$dev_command 2>&1 | tee -a .dev/dev.log"
  tmux set-window-option -t "$session:server" automatic-rename off
  tmux set-option -t "$session" @shared_dev_managed 1
  tmux set-option -t "$session" @shared_dev_project "$project"
  tmux set-option -t "$session" @shared_dev_port "$port"
  tmux set-option -t "$session" @shared_dev_expires_at "$(( $(date +%s) + lease_seconds ))"

  attempt=0
  while [ "$attempt" -lt 60 ]; do
    if url_is_healthy "$port"; then
      break
    fi
    if ! has_session "$session"; then
      printf 'startup failed; log retained at %s\n' "$log_file" >&2
      tail -n 40 "$log_file" >&2 || true
      exit 1
    fi
    sleep 0.5
    attempt=$((attempt + 1))
  done

  if ! url_is_healthy "$port"; then
    tmux kill-session -t "$session" 2>/dev/null || true
    printf 'startup timed out; log retained at %s\n' "$log_file" >&2
    tail -n 40 "$log_file" >&2 || true
    exit 1
  fi

  printf -v script_quoted '%q' "$script_path"
  printf -v session_quoted '%q' "$session"
  tmux new-window -d -t "$session" -n lease -c "$project" "$script_quoted __watch $session_quoted"
  show_status
}

case "$command_name" in
  start)
    start_server
    ;;
  status)
    show_status
    ;;
  logs)
    prepare_state
    if [ "$#" -gt 0 ] && [ "$1" = --follow ]; then
      tail -f "$log_file"
    else
      tail -n 80 "$log_file"
    fi
    ;;
  keep)
    has_session "$session" || fail "no managed dev server for $project"
    assert_managed_session
    tmux set-option -t "$session" @shared_dev_expires_at 0
    show_status
    ;;
  stop)
    has_session "$session" || fail "no managed dev server for $project"
    assert_managed_session
    tmux kill-session -t "$session"
    printf 'stopped=%s\n' "$session"
    ;;
  list)
    { tmux list-sessions -F '#{session_name}' 2>/dev/null || true; } | while IFS= read -r listed_session; do
      listed_managed=$(session_option "$listed_session" @shared_dev_managed)
      if [ "$listed_managed" = 1 ]; then
        listed_project=$(session_option "$listed_session" @shared_dev_project)
        listed_port=$(session_option "$listed_session" @shared_dev_port)
        listed_expiry=$(session_option "$listed_session" @shared_dev_expires_at)
        printf '%s\t%s\thttp://127.0.0.1:%s/\texpires=%s\n' \
          "$listed_session" "$listed_project" "$listed_port" "$listed_expiry"
      fi
    done
    ;;
  help|-h|--help)
    printf 'usage: %s {start|status|logs [--follow]|keep|stop|list}\n' "$0"
    ;;
  *)
    fail "unknown command: $command_name"
    ;;
esac
