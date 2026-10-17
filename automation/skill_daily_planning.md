# MASTER GUIDE: Daily Planning & Kanban System

**Fully Autonomous Holistic Daily Planning: Gmail + Calendar + Todoist → Prioritized Daily Plan**

**Last Updated:** April 9, 2026
**Version:** 3.0.0 - AI Thread Analysis with Content Quality

## Quick Reference
**Use when:** Morning planning session; need a prioritized action list pulled from email/calendar/tasks
**Don't use when:** Just need to check one task or one email — go to Todoist or Gmail directly
**Trigger phrases:** "plan my day", "process new", "daily planner", "what should I do today", "morning routine"
**Time:** ~60-120 seconds
**Command:** `/process-new` (Claude Code slash command) or `python run_process_new_v2.py` (in `_automation/`)

---

## V3 Architecture (Current)

### Pipeline

```
Gmail (30 days) + Calendar (7 days) + Todoist
        │
  ┌─────┴──────┐
  │ Email      │  GmailTools: fetch, filter skip_senders/skip_keywords,
  │ Fetching   │  whitelist domains (fcps.edu, fairfaxcounty.gov, etc.)
  └─────┬──────┘
        │ 49 urgent emails
  ┌─────┴──────┐
  │ Thread     │  GmailThreadTools: group by subject, score by
  │ Grouping   │  whitelisted sender (+100), priority keywords (+50),
  │ & Scoring  │  action keywords (+30), recency decay (-2/day)
  └─────┬──────┘
        │ 15 priority threads
  ┌─────┴──────┐
  │ Clustering │  Merge threads from same sender domain when
  │            │  subject similarity >= 40% word overlap
  └─────┬──────┘
        │ ~13 clustered groups
  ┌─────┴──────┐
  │ AI         │  OpenRouter (claude-haiku-5-5) per thread:
  │ Analysis   │  → ACTION ITEMS, DEADLINE (YYYY-MM-DD), PRIORITY,
  │            │  → CONTEXT (specific, not filler), FOLLOW_UP
  └─────┬──────┘
        │
  ┌─────┴──────┐
  │ Post-      │  1. Deduplicate actions across threads (60% word overlap)
  │ Processing │  2. Auto-expire past-deadline actions → filtered out
  │            │  3. Expire follow-ups referencing past dates
  │            │  4. Filter informational-only threads
  │            │  5. Cap DO NOW at 5, overflow to DO SOON
  └─────┬──────┘
        │
  ┌─────┴──────────────────────────────┐
  │                                    │
  ▼                                    ▼
Todoist Tasks                    Amplenote Note
• Clean title (action only)      • INSERT_NODES API (rich text)
• Concise description            • Today's Schedule (timed events)
• AI-extracted due date          • Tomorrow (sorted by time)
• daily-plan label               • Action Items (checkboxes)
• Calendar events included       • Stale — Review or Close
                                 • Rest of Week (calendar)
                                 • Follow-ups
```

### Key Files

| File | Purpose |
|------|-------|
| `_automation/run_process_new_v2.py` | Main orchestrator — all 9 steps |
| `_automation/gmail_tools.py` | Gmail fetch, sender filtering, priority keywords |
| `_automation/gmail_thread_tools.py` | Thread grouping, priority scoring, clustering |
| `_automation/comprehensive_analyzer.py` | AI prompt, response parsing, deduplication |
| `_automation/amplenote_tools.py` | Note creation via INSERT_NODES API |
| `_automation/todoist_tools.py` | Task CRUD with Todoist REST API |
| `_automation/calendar_tools.py` | Google Calendar event fetch |
| `_automation/auth_manager.py` | Credential resolution for all services |
| `_automation/credential_resolver.py` | Cascade credential lookup (env files → KeePass) |

### Content Quality Rules (V3)

**AI Prompt:**
- Provides today's date — past-deadline actions are rejected ("None - deadline passed")
- CONTEXT must be specific: "Mount Vernon trip May 12. $65 if chaperoning." not "This is an educational opportunity"
- Priority levels: High (7 days), Medium (7-30 days), Low (informational/expired)

**Post-processing:**
- Threads with `deadline < today` are auto-expired and filtered out
- Follow-ups referencing past dates are silently removed
- Stale Todoist tasks (>7 days overdue) shown in separate section

**Todoist tasks:**
- Title = action only (no summary appended)
- Description = context + sender (2-3 lines, no emoji field dumps)
- Due date = AI-extracted deadline, not hardcoded "today"

**Amplenote note:**
- Uses INSERT_NODES API (headings, bullet_list_item, check_list_item) for proper rich text
- "Tomorrow" section with events sorted by time
- Stale task titles truncated at " - " separator
- Footer with counts and generation timestamp

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Daily Planning Workflow](#daily-planning-workflow)
4. [Smart Prioritization Logic](#smart-prioritization-logic)
5. [Kanban Board Structure](#kanban-board-structure)
6. [Running the Daily Planner](#running-the-daily-planner)
7. [Updating and Maintaining Your Board](#updating-and-maintaining-your-board)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

---

## Overview

This system creates a **smart daily Kanban board** that aggregates your important tasks from multiple sources into a single, prioritized view.

### What It Does

**Inputs:**
- 📧 **Gmail emails** (past 1 month) - personal email, intelligent filtering
- 📅 **Google Calendar events** (next 7 days) - upcoming meetings and appointments
- 📋 **Todoist tasks** - active tasks with priorities
- 📄 **Google Drive documents** - recently modified files (last 7 days)

**Intelligent Processing:**
- 🧠 **AI-powered email analysis** - Detects actionable items vs spam/newsletters
- 🎯 **Deadline extraction** - Parses due dates from natural language
- ✅ **Auto-creates tasks in BOTH Todoist AND Amplenote** - For emails requiring action
- 📝 **Auto-creates Amplenote notes** - For important reference info (non-actionable)
- 🔍 **Missing item detection** - Flags potentially overlooked emails

**Output:**
- 🎯 **Action-Priority Daily Plan** with sections:
  - 🎯 **DO NOW** - Urgent & important (due today/tomorrow, high priority)
  - ⏰ **DO SOON** - Important (due this week, medium priority)
  - 👁 **MONITOR** - Awareness items (no immediate action needed)
  - 📌 **REFERENCE** - Important info saved (account numbers, confirmations)
  - 📄 **CONTEXT** - Recent documents and email summary
- 📝 **Reference email notes** - Auto-created in Amplenote for important info
- 📊 **Daily plan JSON** - Saved for Amplenote sync

### Key Features

✅ **Fully Autonomous Authentication** - Auto-refreshes tokens, triggers OAuth when needed, zero user prompts  
✅ **Gmail + Calendar Integration** - Scans 1 month of emails + 7 days of calendar events  
✅ **Smart Filtering** - Removes political emails, newsletters, shipping notifications automatically  
✅ **Reference Email Detection** - Auto-saves emails with account numbers, confirmations, credentials  
✅ **Action-Priority Categorization** - DO NOW/DO SOON/MONITOR (not time-based)  
✅ **Calendar Event Integration** - Meetings and appointments included in daily plan  
✅ **Document Tracking** - Shows recent Google Drive files you're working on  
✅ **Holistic View** - Combines personal Gmail, Calendar, Todoist, and Drive  
✅ **Intelligent Prioritization** - Analyzes urgency, deadlines, and importance  
✅ **Deduplication** - Removes duplicate items across sources  
✅ **Daily Refresh** - Generate new plan each day with updated priorities  
✅ **Zero Configuration** - Just run `python daily_planner.py` - everything else is automatic

### CRITICAL: Todoist vs Amplenote

**📋 Todoist = Permanent Task Storage**
- All tasks live here permanently
- Your single source of truth for tasks
- Add tasks here, complete tasks here
- Daily planner READS from Todoist (doesn't write to it)

**📝 Amplenote = Temporary Daily View + Reference Notes**
- Daily Kanban board is a VIEW of your tasks (not storage)
- Board is refreshed daily (old boards can be deleted)
- Also stores reference notes (passwords, receipts, guides)
- Checking off tasks in Kanban board doesn't sync back to Todoist

### Authentication Status

**✅ FULLY WORKING (Autonomous):**
- Gmail (1 month of emails) - OAuth auto-handled
- Google Calendar (7 days of events) - OAuth auto-handled
- Google Drive (7 days of documents) - OAuth auto-handled
- Todoist (all active tasks) - API token in environments.json

**OAuth Credentials Location:**
- Gmail/Calendar/Drive: `G:\My Drive\03_Areas\Keys\Gmail\credentials.json`
- Gmail Token: `G:\My Drive\03_Areas\Keys\Gmail\token.json` (auto-refreshed)

**OAuth Scopes:**
```python
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]
```

### CRITICAL: Daily Plan Reuse

**One plan per day - updated, not duplicated**

**How it works:**
- First run of the day → Creates new "Daily Plan - [Date]" note
- Subsequent runs same day → **Updates existing note** (doesn't create new one)
- Next day → Creates new note for new date

**Workflow (100% Autonomous):**
1. **Auto-authenticate** → Gmail/Calendar/Drive OAuth (auto-refresh or trigger new flow)
2. **Scan Gmail** → 1 month of emails, filter out political/newsletter/shipping
3. **Detect reference emails** → Auto-save account numbers, confirmations to Amplenote
4. **Scan Calendar** → Next 7 days of events
5. **Fetch Todoist** → All active tasks
6. **Scan Google Drive** → Last 7 days of document activity
7. **Categorize by Action-Priority** → DO NOW (urgent), DO SOON (important), MONITOR (awareness)
8. **Generate JSON plan** → Save to `daily_plan_YYYYMMDD.json`
9. **Sync to Amplenote** → Create daily note with Action-Priority sections
10. **Work from plan** → Clear priorities, full context, reference info linked

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            HOLISTIC DAILY PLANNER SYSTEM                     │
│         (Personal + Work Combined View)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     1. Data Collection (daily_planner.py)│
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┬───────────┬─────────┐
        │                     │           │         │
        ▼                     ▼           ▼         ▼
   ┌────────┐           ┌────────┐ ┌────────┐ ┌────────┐
   │ Gmail  │           │Todoist │ │ Google │ │Calendar│
   │  API   │           │ API v1 │ │ Drive  │ │(Future)│
   │Personal│           │ Tasks  │ │  Docs  │ │        │
   └────────┘           └────────┘ └────────┘ └────────┘
        │                     │           │         │
        └─────────────────────┴───────────┴─────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     2. Smart Filtering & Prioritization  │
        │     - Skip spam/shipping notifications   │
        │     - Detect urgency indicators          │
        │     - Extract due dates                  │
        │     - Remove duplicates                  │
        │     - Track document activity            │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     3. Time-Based Categorization         │
        │     - Today (due today or overdue)       │
        │     - Tomorrow (due tomorrow)            │
        │     - This Week (due within 7 days)      │
        │     - Backlog (no deadline or later)     │
        │     - Documents (recent activity)        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     4. Holistic Kanban Board Generation  │
        │     (sync_plan_to_amplenote.js)          │
        │     - Create/Update daily Amplenote note │
        │     - Add tasks with context             │
        │     - Add document tracking section      │
        │     - Add email summary section          │
        │     - Include due dates & priorities     │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     5. Daily Kanban Board in Amplenote   │
        │     ✅ Check off completed tasks         │
        │     🔄 Refresh daily for new priorities  │
        └─────────────────────────────────────────┘
```

---

## Daily Planning Workflow

### Morning Routine (5-10 minutes)

```powershell
# Navigate to automation folder
cd "G:\My Drive\06_Skills\_automation"

# Run daily planning (generates plan and creates Amplenote board)
python run_process_new_v2.py
```

**What Happens:**

1. **Email Collection** (30-45 seconds)
   - Scans Gmail (last 2 days) for actionable items
   - Fetches active Todoist tasks
   - Filters out spam, newsletters, automated alerts

2. **Intelligent Email Analysis** (15-20 seconds)
   - **Actionable vs Reference**: Classifies emails requiring action vs info-only
   - **Deadline extraction**: Parses "by Friday", "due tomorrow", "end of week"
   - **Urgency detection**: Identifies urgent, asap, deadline, today keywords
   - **Sender importance**: Prioritizes real people over automated systems
   - **Spam filtering**: Skips newsletters, marketing, social media, tracking
   - **Deduplication**: Removes duplicate items across Gmail, Todoist

3. **Auto-Task/Note Creation** (10-15 seconds)
   - **Creates tasks in BOTH Todoist AND Amplenote** for actionable emails
   - **Todoist**: Permanent storage with due date, priority, project, labels
   - **Amplenote**: Daily Kanban view with checkbox, section, context
   - **Creates Amplenote notes** for important reference emails (non-actionable)
   - **Adds context**: Links to original email, key details

4. **Categorization** (5 seconds)
   - Sorts into Today/Tomorrow/This Week/Backlog
   - Orders by priority within each category

5. **Board Creation** (45 seconds)
   - Creates/updates daily Amplenote note
   - Adds tasks with checkboxes
   - Includes due dates and priorities
   - Adds "📄 Documents in Progress" section
   - Shows Google Drive recent files
   - Adds "📧 Email Summary" section
   - Highlights newly created tasks from emails

**Result:** A clean, prioritized Kanban board showing exactly what you need to focus on.

---

## Smart Prioritization Logic

### Importance Filtering

**Automatically Skipped (Spam/Newsletter Patterns):**
- ❌ **Social Media**: TikTok, Facebook, Instagram, LinkedIn notifications
- ❌ **Marketing**: Promotional emails, sales, deals, newsletters
- ❌ **Financial Alerts**: Bank balance, credit score, transaction alerts
- ❌ **Shipping/Tracking**: USPS, FedEx, UPS, Amazon delivery updates
- ❌ **Automated Systems**: no-reply@, noreply@, do-not-reply@
- ❌ **Newsletters**: Substack, Medium, Mailchimp, Constant Contact
- ❌ **Community**: PTA, HOA, rescue alerts, community bulletins
- ❌ **Subscriptions**: Streaming services, app updates, software notifications
- ❌ **Receipts (unless flagged)**: Purchase confirmations without action needed

**Always Included (Actionable Patterns):**
- ✅ **Real People**: Emails from colleagues, clients, family (personal names)
- ✅ **Work Domains**: @reisystems.com, @company.com (your work domain)
- ✅ **Important Services**: DMV, IRS, school, healthcare, government
- ✅ **Action Required**: Contains "please review", "need you to", "can you"
- ✅ **Deadline Indicators**: "by [date]", "due [date]", "deadline"
- ✅ **Urgency Markers**: "urgent", "asap", "today", "tomorrow"
- ✅ **Meeting Requests**: Calendar invites, meeting confirmations
- ✅ **Todoist tasks** with priorities or due dates

### Deduplication

Items are deduplicated across all sources:
- **Gmail**: "Review Q1 budget by Friday"
- **Todoist**: "Review Q1 budget"
- **Result:** Single task in Today section (keeps most detailed version)

---

## Kanban Board Structure

### 🔥 Today Section

**Criteria:**
- Due date is today or overdue
- OR marked as high priority with no due date
- OR contains urgency keywords (urgent, asap)

### 📅 Tomorrow Section

**Criteria:**
- Due date is tomorrow

### 📆 This Week Section

**Criteria:**
- Due date is within the next 7 days
- After tomorrow but before next week

### 📦 Backlog Section

**Criteria:**
- No due date
- OR due date is more than 7 days away
- AND not marked as high priority

---

## Running the Daily Planner

### Daily Usage

```powershell
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

**Expected Output:**
```
📧 Scanning Gmail (last 2 days)...
   Total emails: 47
   Filtered spam/newsletters: 38
   Actionable items: 5
   Reference items: 4

✅ Auto-created Todoist tasks: 8
📝 Auto-created Amplenote notes: 3

📋 Fetching existing Todoist tasks...
   Found 12 active tasks

✨ Total unique items: 20 (deduplicated)

💾 Plan saved to: daily_plan_20260222.json
```

---

## Updating and Maintaining Your Board

### Throughout the Day

**In Amplenote:**
1. Open your daily plan note
2. Check off tasks as you complete them ✅
3. Completed tasks move to "Completed" section automatically
4. Add quick notes or updates to tasks as needed

### Next Morning

```powershell
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

---

## Best Practices

1. **Run every morning** — Priorities change daily
2. **Focus on Today section first** — Work through Today before Tomorrow
3. **Keep Todoist updated** — Add tasks throughout the day
4. **Weekly backlog review** — Every Friday, clear out stale tasks
5. **Don't create tasks for everything** — FYI emails don't need tasks

---

## Troubleshooting

### No Urgent Emails Found

**Solutions:**
1. Check if you actually have urgent emails
2. Review skip_senders list in daily_planner.py
3. Re-authenticate Gmail: `python email_processor.py --auth`

### Todoist Tasks Not Appearing

**Solutions:**
1. Verify Todoist token in environments.json
2. Add due dates or priorities to important tasks
3. Check internet connection

### Amplenote Sync Fails

**Symptom:** "API Error: 401 - invalid_token"

**Solution:**
```powershell
cd C:\Users\[username]\Desktop
node refresh_amplenote_token.js
```

---

## Advanced Usage

### Customizing Urgency Keywords

Edit `daily_planner.py`:

```python
is_urgent = any(word in text for word in [
    'urgent', 'asap', 'today', 'deadline', 'due',
    'important', 'action required', 'respond', 'confirm',
    'critical', 'emergency', 'time-sensitive'
])
```

### Authentication Issues

```powershell
# Re-authenticate Gmail
Remove-Item "G:\My Drive\03_Areas\Keys\Gmail\token.json"
python run_process_new_v2.py
```

---

## Version History

| Version | Date | Changes |
|---------|------|--------|
| 3.0.0 | 2026-04-09 | AI Thread Analysis with Content Quality |
| 1.0.0 | 2026-02-22 | Initial release with Gmail, Todoist integration |

---

**End of Master Guide**
