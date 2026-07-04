#!/usr/bin/env python3
import argparse
from triage_common import NOTION_MEETINGS_DATA_SOURCE_ID, add_common_args, base_result, compact_text, emit, error_obj, iso_utc, notion_blocks, notion_query, window_from_args
from notion_helpers import filter_created_or_edited, row_item

def blocks(pid):
    return notion_blocks(pid)

def text(b):
    node=b.get(b.get("type") or "") or {}
    return "".join(p.get("plain_text","") for p in node.get("rich_text") or []).strip()

def body_text(blocks_, seen=None, depth=0):
    seen = seen or set()
    lines = []
    for block in blocks_:
        block_id = block.get("id")
        if block_id in seen:
            continue
        if block_id:
            seen.add(block_id)

        if block.get("type") == "meeting_notes":
            children = ((block.get("meeting_notes") or {}).get("children") or {})
            for key in ("summary_block_id", "notes_block_id"):
                child_id = children.get(key)
                if child_id:
                    lines.append(body_text(blocks(child_id), seen, depth + 1))
            continue

        lines.append(text(block))
        if block.get("has_children") and block_id and depth < 6:
            lines.append(body_text(blocks(block_id), seen, depth + 1))
    return "\n".join(filter(None, lines))

def transcript_ids(blocks_, seen=None, depth=0):
    seen = seen or set()
    ids = []
    for block in blocks_:
        block_id = block.get("id")
        if block_id in seen:
            continue
        if block_id:
            seen.add(block_id)

        if block.get("type") == "meeting_notes":
            child_id = (((block.get("meeting_notes") or {}).get("children") or {}).get("transcript_block_id"))
            if child_id:
                ids.append(child_id)
            continue

        if block.get("has_children") and block_id and depth < 3:
            ids.extend(transcript_ids(blocks(block_id), seen, depth + 1))
    return ids

def collect(a,b):
    data=notion_query(NOTION_MEETINGS_DATA_SOURCE_ID,{"filter":{"or":[{"property":"Created","created_time":{"on_or_after":iso_utc(a),"before":iso_utc(b)}},{"property":"Edited","last_edited_time":{"on_or_after":iso_utc(a),"before":iso_utc(b)}}]},"sorts":[{"property":"Edited","direction":"descending"}],"page_size":100})
    items=[]
    for row in filter_created_or_edited(data.get("results",[]), a, b):
        item=row_item(row)
        try:
            page_blocks = blocks(row.get("id"))
            item["body_excerpt"]=compact_text(body_text(page_blocks),20000)
            transcripts = transcript_ids(page_blocks)
            if transcripts:
                item["transcript_block_ids"] = transcripts
        except Exception as exc: item["body_error"]=str(exc)
        items.append(item)
    return items
def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args(); a,b=window_from_args(args.after,args.before,require=True); r=base_result("meetings","created_or_edited_window",a,b)
    try: r["items"]=collect(a,b)
    except Exception as exc: err=error_obj("meetings",exc); r["ok"]=False; r["errors"].append(err)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
