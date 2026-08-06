#!/usr/bin/env python3
"""
push_process_new_to_todoist.py
-------------------------------
Reads daily_plan_YYYYMMDD.json and pushes the daily plan to Todoist.
Uses kill-and-fill: deletes old TODAY/SOON tasks, creates fresh ones.

Usage:
    python push_process_new_to_todoist.py [--date YYYYMMDD] [--dry-run]
"""

import requests
import json
import os
import sys
import argparse
from datetime import datetime

# ── Credential loading ──────────────────────────────────────────────────────

def load_todoist_token():
    """Load Todoist API token from environments.json or individual key file."""
    # Primary: individual key file (newer format)
    key_paths = [
        r'G:\My Drive\03_Areas\Keys\Environments\api-todoist.json',
        r'G:\My Drive\03_Areas\Keys\Environments\environments.json',
        os.path.expanduser('~/AppData/Roaming/todoist_token.txt'),
    ]
    for path in key_paths:
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            data = json.load(f) if path.endswith('.json') else f.read().strip()
        if isinstance(data, str):
            return data
        # Individual key file: {"apiToken": "..."}
        if 'apiToken' in data:
            return data['apiToken']
        if 'token' in data:
            return data['token']
        # environments.json: {"environments": {"todoist": {"credentials": {"apiToken": "..."}}}}
        try:
            return data['environments']['todoist']['credentials']['apiToken']
        except (KeyError, TypeError):
            pass
    raise RuntimeError(
        "Todoist token not found. Check G:\\My Drive\\03_Areas\\Keys\\Environments\\"
    )


# ── Todoist helpers ─────────────────────────────────────────────────────────

TODOIST_BASE = 'https://api.todoist.com/api/v1'
DAILY_MARKERS = ('🎯 TODAY:', '⏰ SOON:', '🎯 TODAY -', '⏰ SOON -')


def get_all_tasks(headers):
    resp = requests.get(f'{TODOIST_BASE}/tasks', headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data.get('results', data) if isinstance(data, dict) else data


def delete_old_daily_tasks(headers, dry_run=False):
    tasks = get_all_tasks(headers)
    deleted = []
    for task in tasks:
        content = task.get('content', '')
        if any(content.startswith(m) for m in DAILY_MARKERS):
            if dry_run:
                print(f'  [DRY RUN] Would delete: {content}')
            else:
                resp = requests.delete(
                    f'{TODOIST_BASE}/tasks/{task["id"]}', headers=headers
                )
                resp.raise_for_status()
                print(f'  🗑️  Deleted: {content}')
            deleted.append(content)
    return deleted


def create_task(headers, content, description='', priority=1, due_string=None, dry_run=False):
    task_data = {'content': content, 'priority': priority}
    if description:
        task_data['description'] = description
    if due_string:
        task_data['due_string'] = due_string

    if dry_run:
        print(f'  [DRY RUN] Would create: {content}')
        return {'id': 'dry-run', 'content': content}

    resp = requests.post(f'{TODOIST_BASE}/tasks', headers=headers, json=task_data)
    resp.raise_for_status()
    return resp.json()


# ── Plan → Todoist mapping ──────────────────────────────────────────────────

def push_plan(plan, headers, dry_run=False):
    created = []

    # ── DO NOW tasks (individual, high priority) ────────────────────────────
    do_now = plan.get('do_now', [])
    for item in do_now[:5]:  # cap at 5 individual DO NOW tasks for DakBoard
        title = f"🎯 TODAY: {item['title']}"
        desc = item.get('notes', '')
        task = create_task(
            headers,
            content=title,
            description=desc,
            priority=4,  # red/urgent in Todoist
            due_string='today',
            dry_run=dry_run,
        )
        print(f'  ✅ Created DO NOW: {title}')
        created.append(task)

    # ── DO SOON summary task ────────────────────────────────────────────────
    do_soon = plan.get('do_soon', [])
    if do_soon:
        soon_lines = '\n'.join(
            f"• {item['title']}" + (f" — due {item['due']}" if item.get('due') else '')
            for item in do_soon
        )
        soon_details = '\n\n'.join(
            f"**{item['title']}**\n{item.get('notes', '')}"
            for item in do_soon
        )
        task = create_task(
            headers,
            content=f"⏰ SOON: {len(do_soon)} items this week",
            description=soon_lines + '\n\n---\n\n' + soon_details,
            priority=2,  # yellow/medium
            due_string='this week',
            dry_run=dry_run,
        )
        print(f'  ✅ Created DO SOON summary: {len(do_soon)} items')
        created.append(task)

    return created


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Push daily plan to Todoist')
    parser.add_argument('--date', default=datetime.now().strftime('%Y%m%d'),
                        help='Plan date YYYYMMDD (default: today)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print what would happen without making API calls')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    plan_file = os.path.join(script_dir, f'daily_plan_{args.date}.json')

    if not os.path.exists(plan_file):
        print(f'❌ Plan file not found: {plan_file}')
        sys.exit(1)

    with open(plan_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    print(f'\n📋 Daily Plan: {args.date}')
    print(f'   DO NOW:    {len(plan.get("do_now", []))} items')
    print(f'   DO SOON:   {len(plan.get("do_soon", []))} items')
    print(f'   MONITOR:   {len(plan.get("monitor", []))} items')
    print(f'   REFERENCE: {len(plan.get("reference", []))} items')

    token = load_todoist_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    if args.dry_run:
        print('\n⚠️  DRY RUN mode — no changes will be made\n')

    # Kill old daily tasks
    print('\n🗑️  Removing old daily plan tasks...')
    deleted = delete_old_daily_tasks(headers, dry_run=args.dry_run)
    print(f'   Removed {len(deleted)} old tasks')

    # Create new tasks
    print('\n➕ Creating new daily plan tasks...')
    created = push_plan(plan, headers, dry_run=args.dry_run)
    print(f'\n✅ Done! Created {len(created)} Todoist tasks.')

    if not args.dry_run:
        print('\n📌 Summary pushed to Todoist:')
        do_now = plan.get('do_now', [])
        for item in do_now[:5]:
            print(f'   🎯 TODAY: {item["title"]}')
        do_soon = plan.get('do_soon', [])
        if do_soon:
            print(f'   ⏰ SOON:  {len(do_soon)} items this week')


if __name__ == '__main__':
    main()
