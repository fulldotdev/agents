#!/usr/bin/env python3
import argparse, json
from productive_common import add_common_args, base_result, emit, error_obj, json_cmd, window_from_args

MCP = "https://moneybird.com/mcp/v1/read_write"

def call(tool, args):
    return json_cmd(["mcporter", "call", f"{MCP}.{tool}", "--args", json.dumps(args), "--output", "json"])

def objects(value):
    found = []
    if isinstance(value, dict):
        if value.get("id"):
            found.append(value)
        for item in value.values():
            found.extend(objects(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(objects(item))
    return found

def collect(customer, period):
    contacts_raw = call("list_contacts", {"query": customer, "per_page": "20"})
    contacts = [x for x in objects(contacts_raw) if x.get("company_name") or x.get("firstname") or x.get("lastname")]
    contact = next((x for x in contacts if (x.get("company_name") or "").lower() == customer.lower()), contacts[0] if contacts else None)
    filt = f"state:all,period:{period}"
    if contact:
        filt += f",contact_id:{contact['id']}"
    invoices_raw = call("list_invoices", {"filter": filt, "per_page": "50"})
    invoices = []
    for inv in objects(invoices_raw):
        if not inv.get("details"):
            continue
        invoices.append({
            "id": inv.get("id"),
            "invoice_id": inv.get("invoice_id"),
            "state": inv.get("state"),
            "invoice_date": inv.get("invoice_date"),
            "reference": inv.get("reference"),
            "details": inv.get("details"),
        })
    return {"contact": contact, "invoices": invoices}

def main():
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--period")
    args = p.parse_args(); a, b = window_from_args(args.after, args.before)
    r = base_result("moneybird", "invoices", a, b)
    period = args.period or f"{a:%Y%m%d}..{b:%Y%m%d}"
    try:
        data = collect(args.customer, period); r.update(data); r["items"] = data["invoices"]
    except Exception as exc:
        err = error_obj("moneybird", exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
