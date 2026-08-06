#!/usr/bin/env python3
"""
Push process_new analysis output to Todoist.
Reads the latest process_new_output_*.json from the output/ directory
and creates tasks in Todoist, deleting old daily-plan tasks first.

Usage:
    python push_to_todoist.py [--output-file path/to/output.json]
    python push_to_todoist.py --dry-run
"""

import json
import sys
import argparse
import urllib.request
import urllib.error
import ssl
import glob
import os
from pathlib import Path

TODOIST_API_BASE = "https://api.todoist.com/api/v1"
LEGACY_PREFIXES = ("📋", "🎯 TODAY:", "⏰ SOON:", "🎯 ")


def load_api_token():
    """Load Todoist API token from environments.json or env var."""
    token = os.environ.get("TODOIST_API_TOKEN")
    if token:
        return token

    # Try environments.json in known locations
    env_paths = [
        Path("G:/My Drive/03_Areas/Keys/Environments/environments.json"),
        Path.home() / "Google Drive/03_Areas/Keys/Environments/environments.json",
        Path(__file__).parent / "output/environments.json",
    ]
    for p in env_paths:
        if p.exists():
            with open(p) as f:
                data = json.load(f)
            creds = data.get("environments", {}).get("todoist", {}).get("credentials", {})
            if creds.get("apiToken"):
                return creds["apiToken"]

    raise RuntimeError(
        "No Todoist API token found. Set TODOIST_API_TOKEN env var or ensure "
        "environments.json is accessible."
    )


def todoist_request(method, path, body=None, token=None, dry_run=False):
    """Make a Todoist API v1 request."""
    if dry_run and method != "GET":
        print(f"  [DRY-RUN] {method} {path}" + (f" {json.dumps(body)[:80]}" if body else ""))
        return {"id": "dry-run-id"}

    url = f"{TODOIST_API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        resp_body = resp.read()
        return json.loads(resp_body) if resp_body else {}


def get_all_tasks(token, dry_run=False):
    if dry_run:
        return []
    result = todoist_request("GET", "/tasks", token=token)
    return result.get("results", result) if isinstance(result, dict) else result


def delete_old_daily_plan_tasks(token, dry_run=False):
    """Delete all tasks tagged daily-plan or matching legacy prefixes."""
    tasks = get_all_tasks(token, dry_run)
    deleted = 0
    for task in tasks:
        content = task.get("content", "")
        labels = task.get("labels", [])
        description = task.get("description", "")
        is_plan = (
            "daily-plan" in labels
            or any(content.startswith(p) for p in LEGACY_PREFIXES)
            or "Daily Planner" in description
            or "Source: Email" in description
        )
        if is_plan:
            print(f"  Deleting: {content[:60]}")
            todoist_request("DELETE", f"/tasks/{task['id']}", token=token, dry_run=dry_run)
            deleted += 1
    print(f"  Deleted {deleted} old daily-plan tasks")
    return deleted


def create_task(task_spec, token, dry_run=False):
    """Create a single Todoist task from a spec dict."""
    body = {
        "content": task_spec["content"],
        "description": task_spec.get("description", ""),
        "priority": task_spec.get("priority", 1),
        "labels": task_spec.get("labels", ["daily-plan"]),
    }
    due = task_spec.get("due_string")
    if due:
        body["due"] = {"string": due}

    result = todoist_request("POST", "/tasks", body=body, token=token, dry_run=dry_run)
    print(f"  ✅ Created (p{task_spec['priority']}, due {due}): {task_spec['content'][:70]}")
    return result


def find_latest_output():
    """Find the most recently created process_new_output_*.json."""
    output_dir = Path(__file__).parent / "output"
    files = sorted(output_dir.glob("process_new_output_*.json"), reverse=True)
    if not files:
        raise FileNotFoundError(f"No process_new_output_*.json found in {output_dir}")
    return files[0]


def main():
    parser = argparse.ArgumentParser(description="Push process_new results to Todoist")
    parser.add_argument("--output-file", help="Path to process_new output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without calling API")
    parser.add_argument("--token", help="Todoist API token (overrides auto-detect)")
    args = parser.parse_args()

    output_file = Path(args.output_file) if args.output_file else find_latest_output()
    print(f"📂 Loading: {output_file}")

    with open(output_file) as f:
        data = json.load(f)

    tasks_to_create = data.get("todoist_tasks_to_create", [])
    print(f"📋 Found {len(tasks_to_create)} tasks to create")

    token = args.token or (None if args.dry_run else load_api_token())

    print("\n🗑  Cleaning up old daily-plan tasks...")
    delete_old_daily_plan_tasks(token, dry_run=args.dry_run)

    print(f"\n✨ Creating {len(tasks_to_create)} new tasks...")
    created = 0
    for task in tasks_to_create:
        try:
            create_task(task, token, dry_run=args.dry_run)
            created += 1
        except Exception as e:
            print(f"  ❌ Failed to create '{task['content'][:50]}': {e}")

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}✅ Done: {created}/{len(tasks_to_create)} tasks created")

    print("\n📊 DAILY PLAN SUMMARY")
    print("=" * 60)
    print(f"\n🎯 DO NOW ({len(data.get('high_priority', []))} items):")
    for item in data.get("high_priority", []):
        for action in item.get("action_items", [])[:1]:
            print(f"  • {action[:80]}")

    print(f"\n⏰ DO SOON ({len(data.get('medium_priority', []))} items):")
    for item in data.get("medium_priority", []):
        actions = item.get("action_items", [])
        if actions and not actions[0].lower().startswith("none"):
            print(f"  • {actions[0][:80]}")

    print(f"\n📅 CALENDAR THIS WEEK:")
    for event in data.get("calendar_events_week", []):
        rsvp = f" [RSVP needed]" if event.get("rsvp_status") == "needsAction" else ""
        print(f"  • {event['date']} {event.get('time', '')} - {event['summary']}{rsvp}")

    print(f"\n📅 UPCOMING:")
    for event in data.get("upcoming_calendar", [])[:4]:
        print(f"  • {event['date']} {event.get('time', '')} - {event['summary']}")


if __name__ == "__main__":
    main()
