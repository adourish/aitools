# MASTER GUIDE: Daily Planning & Kanban System

**Fully Autonomous Holistic Daily Planning: Gmail + Calendar + Todoist → Prioritized Daily Plan**

**Last Updated:** July 13, 2026
**Version:** 3.1.0 - AI Thread Analysis with Content Quality (gpt-4o)

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
  │ AI         │  OpenRouter (gpt-4o) per thread:
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
|------|--------|
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
  - 📋 **MONITOR** - Awareness items (no immediate action needed)
  - 📌 **REFERENCE** - Important info saved (account numbers, confirmations)
- 📝 **Reference email notes** - Auto-created in Amplenote for important info
- 💾 **Daily plan JSON** - Saved for Amplenote sync

### Key Features

✅ **Fully Autonomous Authentication** - Auto-refreshes tokens, triggers OAuth when needed, zero user prompts  
✅ **Gmail + Calendar Integration** - Scans 1 month of emails + 7 days of calendar events  
✅ **Smart Filtering** - Removes political emails, newsletters, shipping notifications automatically  
✅ **Reference Email Detection** - Auto-saves emails with account numbers, confirmations, credentials  
✅ **Action-Priority Categorization** - DO NOW/DO SOON/MONITOR (not time-based)  
✅ **Calendar Event Integration** - Meetings and appointments included in daily plan  
✅ **Holistic View** - Combines personal Gmail, Calendar, and Todoist  
✅ **Intelligent Prioritization** - Analyzes urgency, deadlines, and importance  
✅ **Deduplication** - Removes duplicate items across sources  
✅ **Daily Refresh** - Generate new plan each day with updated priorities  
✅ **Zero Configuration** - Just run `python run_process_new_v2.py` - everything else is automatic

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
- Todoist (all active tasks) - API token via credential resolver

**OAuth Credentials Location:**
- Gmail/Calendar: `G:\My Drive\Areas\Keys\Gmail\credentials.json`
- Gmail Token: `G:\My Drive\Areas\Keys\Gmail\token.json` (auto-refreshed)

**OAuth Scopes:**
```python
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
]
```

### CRITICAL: Daily Plan Reuse

**One plan per day - updated, not duplicated**

**How it works:**
- First run of the day → Creates new "Daily Plan" note
- Subsequent runs same day → **Updates existing note** (doesn't create new one)
- Next day → Creates new note for new date

**Why:**
- Avoids clutter (no duplicate daily plans)
- Single source of truth for today's plan
- Can run "process new" multiple times to refresh without creating mess

**Example:**
- 9am: Run "process new" → Creates "📋 Daily Plan"
- 2pm: Run "process new" again → **Updates same note** with latest emails/tasks
- Next day: Run "process new" → Recreates note with fresh data

**Workflow (100% Autonomous):**
1. **Auto-authenticate** → Gmail/Calendar OAuth (auto-refresh or trigger new flow)
2. **Scan Gmail** → 1 month of emails, filter out political/newsletter/shipping
3. **Detect reference emails** → Auto-save account numbers, confirmations to Amplenote
4. **Scan Calendar** → Next 7 days of events
5. **Fetch Todoist** → All active tasks
6. **Categorize by Action-Priority** → DO NOW (urgent), DO SOON (important), MONITOR (awareness)
7. **Generate JSON plan** → Save to `daily_plan_YYYYMMDD.json`
8. **Sync to Amplenote** → Create daily note with Action-Priority sections
9. **Work from plan** → Clear priorities, full context, reference info linked

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            HOLISTIC DAILY PLANNER SYSTEM                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     1. Data Collection                   │
        └─────────────────────────────────────────┘
                              │
        ┌─────────┬───────────┼───────────┐
        │         │           │           │
        ▼         ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Gmail  │ │Todoist │ │ Google │ │Calendar│
   │  API   │ │ API v1 │ │ Drive  │ │  API   │
   │Personal│ │ Tasks  │ │  Keys  │ │        │
   └────────┘ └────────┘ └────────┘ └────────┘
        │         │           │           │
        └─────────┴───────────┴───────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     2. Smart Filtering & Prioritization  │
        │     - Skip spam/shipping notifications   │
        │     - Detect urgency indicators          │
        │     - Extract due dates                  │
        │     - Remove duplicates                  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     3. Time-Based Categorization         │
        │     - Today (due today or overdue)       │
        │     - Tomorrow (due tomorrow)            │
        │     - This Week (due within 7 days)      │
        │     - Backlog (no deadline or later)     │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     4. Holistic Kanban Board Generation  │
        │     - Create/Update daily Amplenote note │
        │     - Add tasks with checkboxes          │
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
   - Scans Gmail (last 30 days) for actionable items
   - Fetches active Todoist tasks
   - Filters out spam, newsletters, automated alerts

2. **Intelligent Email Analysis** (15-20 seconds)
   - **Actionable vs Reference**: Classifies emails requiring action vs info-only
   - **Deadline extraction**: Parses "by Friday", "due tomorrow", "end of week"
   - **Urgency detection**: Identifies urgent, asap, deadline, today keywords
   - **Sender importance**: Prioritizes real people over automated systems
   - **Spam filtering**: Skips newsletters, marketing, social media, tracking
   - **Deduplication**: Removes duplicate items across Gmail and Todoist

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
   - Adds "📧 Email Summary" section
   - Highlights newly created tasks from emails
   - Generates usage instructions

**Result:** A clean, prioritized Kanban board showing exactly what you need to focus on.

**Note:** If you run "process new" multiple times in one day, it will **update the existing daily plan** rather than creating a new one. This prevents clutter and keeps one single plan per day.

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
- ❌ **Subscriptions**: Streaming services, app updates, software notifications
- ❌ **Receipts (unless flagged)**: Purchase confirmations without action needed

**Always Included (Actionable Patterns):**
- ✅ **Real People**: Emails from colleagues, clients, family (personal names)
- ✅ **Important Services**: DMV, IRS, school, healthcare, government
- ✅ **Action Required**: Contains "please review", "need you to", "can you"
- ✅ **Deadline Indicators**: "by [date]", "due [date]", "deadline"
- ✅ **Urgency Markers**: "urgent", "asap", "today", "tomorrow"
- ✅ **Meeting Requests**: Calendar invites, meeting confirmations
- ✅ **School Sign-ups**: Activity registrations, field trip forms, permission slips
- ✅ **Todoist tasks** with priorities or due dates

### Actionable Item Detection

**Email is Actionable When It Contains:**

**1. Action Verbs + Request Patterns:**
```python
action_patterns = [
    'please review', 'need you to', 'can you', 'could you', 'would you',
    'please submit', 'please send', 'please complete', 'please confirm',
    'I need', 'we need', 'team needs', 'client needs',
    'waiting for', 'pending your', 'requires your',
    'action required', 'action needed', 'response needed'
]
```

**2. Deadline Indicators:**
```python
deadline_keywords = [
    'deadline', 'due date', 'due by', 'by [date]',
    'before [date]', 'no later than', 'must be completed',
    'submit by', 'send by', 'complete by'
]
```

**3. Urgency Markers (High Priority):**
```python
urgency_keywords = [
    'urgent', 'asap', 'immediately', 'right away',
    'today', 'this morning', 'this afternoon',
    'critical', 'time-sensitive', 'high priority',
    'important', 'emergency', 'expedite'
]
```

**4. Meeting/Event Patterns:**
```python
meeting_patterns = [
    'meeting', 'call', 'conference', 'zoom', 'teams',
    'scheduled for', 'calendar invite', 'appointment',
    'let\'s meet', 'can we meet', 'available for'
]
```

### Due Date Extraction (Natural Language Processing)

**Relative Dates:**
- "today" or "asap" → Due today
- "tomorrow" → Due tomorrow  
- "this week" or "end of week" → Due Friday
- "next week" → Due next Monday
- "end of month" → Last day of current month

**Specific Dates:**
- "by Friday" → This Friday or next Friday (context-aware)
- "by March 15" → March 15, 2026
- "before the 20th" → 20th of current/next month
- "no later than 3/15" → March 15, 2026

**Time Expressions:**
- "in 2 days" → 2 days from now
- "within 3 business days" → 3 weekdays from now
- "by end of day" → Today at 5 PM

---

## Kanban Board Structure

### 🔥 Today Section

**Criteria:**
- Due date is today or overdue
- OR marked as high priority with no due date
- OR contains urgency keywords (urgent, asap)

**Purpose:** Focus here first. These are your most critical items.

### 📅 Tomorrow Section

**Criteria:**
- Due date is tomorrow

**Purpose:** Plan ahead. Review these to prepare for tomorrow.

### 📆 This Week Section

**Criteria:**
- Due date is within the next 7 days
- After tomorrow but before next week

**Purpose:** Keep on radar. Don't forget about these.

### 📦 Backlog Section

**Criteria:**
- No due date
- OR due date is more than 7 days away
- AND not marked as high priority

**Purpose:** Important but not urgent. Review weekly.

---

## Running the Daily Planner

### Daily Usage

**Morning Routine:**
```powershell
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

### Authentication Issues

```powershell
# Re-authenticate Gmail (delete token to trigger OAuth)
Remove-Item "G:\My Drive\Areas\Keys\Gmail\token.json"
python run_process_new_v2.py
```

---

## Updating and Maintaining Your Board

### Throughout the Day

**In Amplenote:**
1. Open your daily plan note
2. Check off tasks as you complete them ✅
3. Completed tasks move to "Completed" section automatically
4. Add quick notes or updates to tasks as needed

**Adding New Tasks:**
- Add directly to Todoist (will appear in tomorrow's plan)
- Or add manually to today's Amplenote board

### End of Day Review (5 minutes)

**Review Completed Items:**
- ✅ What did you accomplish?
- 📊 How many items completed vs planned?

**Review Incomplete Items:**
- 🔄 Still relevant? Keep in Todoist
- ❌ No longer needed? Delete from Todoist
- 📅 Need new due date? Update in Todoist

### Next Morning

**Generate Fresh Board:**
```powershell
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

---

## Best Practices

### 1. Run Every Morning

**Why:** Priorities change daily. New urgent items appear. Tasks get completed.

**When:** First thing in the morning, before checking email.

**Time:** 5-10 minutes total (2 min to run scripts, 3-8 min to review board)

### 2. Focus on Today Section First

**Strategy:**
- Start with high priority items (⚡ icon)
- Work through Today section before moving to Tomorrow
- Don't worry about Backlog until Today is clear

**Goal:** Complete all Today items before end of day.

### 3. Keep Todoist Updated

**Throughout Day:**
- Add new tasks as they come up
- Mark tasks complete in Todoist (not just Amplenote)
- Update due dates when priorities change

**Why:** Tomorrow's board will reflect these changes.

### 4. Weekly Backlog Review

**Every Friday or Sunday:**
- Review Backlog section
- Delete tasks no longer relevant
- Promote important items by adding due dates
- Break down large tasks into smaller ones

**Goal:** Keep backlog under 20 items.

---

## Troubleshooting

### No Urgent Emails Found

**Symptom:** "Found 0 urgent items from emails"

**Causes:**
- No emails in past 30 days with urgency keywords
- All emails from filtered senders
- Gmail token expired

**Solutions:**
1. Check if you actually have urgent emails
2. Review skip_senders list in gmail_tools.py
3. Re-authenticate Gmail: delete token and re-run

### Todoist Tasks Not Appearing

**Symptom:** "Found 0 active tasks" but you have tasks in Todoist

**Causes:**
- Todoist API token incorrect
- All tasks are low priority with no due dates (filtered out)
- Network connection issue

**Solutions:**
1. Verify Todoist token via credential resolver
2. Add due dates or priorities to important tasks
3. Check internet connection

### Amplenote Sync Fails

**Symptom:** "API Error: 401 - invalid_token"

**Cause:** Amplenote token expired (tokens last 2 hours)

**Solution:**
```powershell
cd G:\My Drive\06_Master_Guides\Scripts
node refresh_amplenote_token.js
```

Then retry sync.

---

## Advanced Usage

### Customizing Urgency Keywords

Edit `gmail_tools.py`:

```python
is_urgent = any(word in text for word in [
    'urgent', 'asap', 'today', 'deadline', 'due',
    'important', 'action required', 'respond', 'confirm',
    # Add your custom keywords:
    'critical', 'emergency', 'time-sensitive'
])
```

### Adjusting Time Windows

**Change email lookback period:**
```python
# In run_process_new_v2.py, change days parameter:
all_threads = await thread_tools.get_thread_emails(days=30)  # Look back 30 days
```

### Adding Custom Filters

**Skip specific senders:**
```python
# Add to skip_senders list in gmail_tools.py:
self.skip_senders = [
    'tiktok.com',
    'your-custom-sender@example.com',  # Add here
    # ... rest of list
]
```

---

## Version History

| Version | Date | Changes |
|---------|------|--------|
| 3.1.0 | 2026-07-13 | Upgrade to gpt-4o; remove OneDrive/SharePoint (blocked); allow sign-up emails through |
| 3.0.0 | 2026-04-09 | AI Thread Analysis with Content Quality |
| 1.0.0 | 2026-02-22 | Initial release with Gmail, Todoist integration |

---

**End of Master Guide**

For questions or issues, refer to the troubleshooting section or check `run_process_new_v2.py`.
