#!/usr/bin/env python3
import argparse, os
from pathlib import Path
from productive_common import DEFAULT_AUTHOR, add_common_args, base_result, emit, error_obj, run, window_from_args

def find_repos(root):
    repos = []
    root = Path(root).expanduser()
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames:
            repos.append(str(Path(dirpath)))
            dirnames[:] = []
        if len(Path(dirpath).relative_to(root).parts) >= 3:
            dirnames[:] = []
    return repos

def collect_repo(repo, a, b, author):
    cmd = ["git", "-C", repo, "log", f"--since={a.isoformat()}", f"--until={b.isoformat()}", "--date=short", "--pretty=format:%ad%x09%h%x09%an%x09%s", "--all", "--no-merges"]
    if author:
        cmd.insert(7, f"--author={author}")
    out = run(cmd)
    items = []
    for line in out.splitlines():
        if not line.strip():
            continue
        date, sha, name, subject = (line.split("\t", 3) + [""])[:4]
        items.append({"repo": repo, "date": date, "sha": sha, "author": name, "subject": subject})
    return items

def main():
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--repo", action="append"); p.add_argument("--repo-root", default="/Users/otis/projects"); p.add_argument("--author", default=DEFAULT_AUTHOR)
    args = p.parse_args(); a, b = window_from_args(args.after, args.before)
    r = base_result("github", "commits", a, b); repos = args.repo or find_repos(args.repo_root); r["repos"] = repos
    for repo in repos:
        try:
            r["items"].extend(collect_repo(repo, a, b, args.author))
        except Exception as exc:
            err = error_obj(repo, exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
