#!/usr/bin/env python3
# Meeting collection for work-triage.
import argparse
from common import save_snapshot, NOTION_VERSION, json_cmd, NOTION_MEETINGS_DATA_SOURCE_ID, add_common_args, base_result, emit, error_obj, in_window_value, iso_utc, notion_blocks, notion_query, parse_iso, prop_time, relation_ids, row_item, window_from_args

from meeting_summary import source_markdown, source_fingerprint


def blocks(pid):
    return notion_blocks(pid)

def meeting_notes_metadata(blocks_, seen=None, depth=0):
    seen = seen or set()
    notes = []
    for block in blocks_:
        block_id = block.get("id")
        if block_id in seen:
            continue
        if block_id:
            seen.add(block_id)

        if block.get("type") == "meeting_notes":
            data = block.get("meeting_notes") or {}
            children = data.get("children") or {}
            transcript_id = children.get("transcript_block_id")
            item = {
                "block_id": block_id,
                "status": data.get("status"),
                "transcript_block_id": transcript_id,
                "summary_block_id": children.get("summary_block_id"),
                "notes_block_id": children.get("notes_block_id"),
            }
            notes.append(item)
            continue

        if block.get("has_children") and block_id and depth < 3:
            notes.extend(meeting_notes_metadata(blocks(block_id), seen, depth + 1))
    return notes

def date_prop(row, names=("When", "Meeting date", "Meeting Date", "Date")):
    props = row.get("properties") or {}
    for name in names:
        date = ((props.get(name) or {}).get("date") or {})
        if date.get("start"):
            return date.get("start")
    return None

def title_mention_date(row):
    title = (((row.get("properties") or {}).get("Name") or {}).get("title") or [])
    for part in title:
        mention = part.get("mention") or {}
        date = mention.get("date") or {}
        if date.get("start"):
            return date.get("start")
    return None

def meeting_date(row):
    return date_prop(row) or title_mention_date(row)

def dedupe_rows(rows):
    out=[]; seen=set()
    for row in rows:
        rid=row.get("id")
        if not rid or rid in seen:
            continue
        seen.add(rid); out.append(row)
    return out

def include_row(row,a,b):
    when=meeting_date(row)
    when_in_window = bool(when and (dt := parse_iso(when)) and a <= dt < b)
    changed_in_window = in_window_value(prop_time(row,"Created"),a,b) or in_window_value(prop_time(row,"Edited"),a,b)
    return when_in_window or changed_in_window

def query_pages(payload):
    rows, cursors = [], set()
    while True:
        data = notion_query(NOTION_MEETINGS_DATA_SOURCE_ID, payload)
        if "results" not in data:
            raise RuntimeError("Incomplete meeting query response")
        rows.extend(data["results"])
        cursor = data.get("next_cursor")
        if not data.get("has_more") and not cursor:
            return {"results": rows}
        if not cursor or cursor in cursors:
            raise RuntimeError("Incomplete meeting index: missing or repeated pagination cursor")
        cursors.add(cursor)
        payload["start_cursor"] = cursor


def collect(a,b, retry_items=()):
    when_data=query_pages({"filter":{"property":"When","date":{"on_or_after":iso_utc(a),"before":iso_utc(b)}},"sorts":[{"property":"When","direction":"descending"}],"page_size":100})
    changed_data=query_pages({"filter":{"or":[{"property":"Created","created_time":{"on_or_after":iso_utc(a),"before":iso_utc(b)}},{"property":"Edited","last_edited_time":{"on_or_after":iso_utc(a),"before":iso_utc(b)}}]},"sorts":[{"property":"Edited","direction":"descending"}],"page_size":100})
    rows=dedupe_rows((when_data.get("results") or []) + (changed_data.get("results") or []))
    items=[]
    retry_ids = {item["id"] for item in retry_items}
    for page_id in retry_ids - {row["id"] for row in rows}:
        try:
            rows.append(json_cmd(["ntn", "api", f"v1/pages/{page_id}", "--notion-version", NOTION_VERSION]))
        except Exception as exc:
            items.append({"id": page_id, "ok": False, "collection_error": str(exc)})
    for row in rows:
        if row["id"] not in retry_ids and not include_row(row,a,b):
            continue
        item=row_item(row)
        item["when"] = meeting_date(row)
        item["companies"] = relation_ids(row, "Companies")
        item["projects"] = relation_ids(row, "Projects")
        item["tasks"] = relation_ids(row, "Tasks")
        item["persons"] = relation_ids(row, "Persons")
        try:
            page_blocks = blocks(row.get("id"))
            meeting_notes = meeting_notes_metadata(page_blocks)
            markdown = json_cmd(["ntn", "api", f"v1/pages/{row['id']}/markdown", "include_transcript==true",
                                 "--notion-version", NOTION_VERSION])
            if "markdown" in markdown:
                item["content_file"] = save_snapshot("meetings", row["id"], source_markdown(markdown["markdown"]), ".md")
                item["content_kind"] = "meeting_source"
                item["content_complete"] = not markdown.get("truncated") and not markdown.get("unknown_block_ids")
                item["content_unknown_block_ids"] = markdown.get("unknown_block_ids") or []
            if item.get("content_complete"):
                item["content_fingerprint"] = source_fingerprint(markdown["markdown"])
            if meeting_notes:
                item["meeting_notes"] = meeting_notes
                item["transcript_ready"] = any(
                    note.get("status") == "notes_ready" and note.get("transcript_block_id")
                    for note in meeting_notes
                )
        except Exception as exc:
            item.update(ok=False, collection_error=str(exc))
        items.append(item)
    return items

def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args(); a,b=window_from_args(args.after,args.before,require=True); r=base_result("meetings","when_or_changed_window",a,b)
    try: r["items"]=collect(a,b)
    except Exception as exc: err=error_obj("meetings",exc); r["ok"]=False; r["errors"].append(err)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
