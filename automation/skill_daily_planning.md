# MASTER GUIDE: Daily Planning & Kanban System

**Fully Autonomous Holistic Daily Planning: Gmail + Calendar + Todoist → Prioritized Daily Plan**

**Last Updated:** May 13, 2026
**Version:** 3.1.0 - AI Thread Analysis with claude-sonnet-4-5

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
  │ AI         │  OpenRouter (claude-sonnet-4-5) per thread:
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
|------|----------|
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
  - 📋 **MONITOR** - Awareness items (no immediate action needed)
  - 📌 **REFERENCE** - Important info saved (account numbers, confirmations)
  - 📊 **CONTEXT** - Recent documents and email summary
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
- Google Drive (7 days of documents) - OAuth auto-handled
- Todoist (all active tasks) - API token via credential resolver

**OAuth Credentials Location:**
- Gmail/Calendar/Drive: `G:\My Drive\Areas\Keys\Gmail\credentials.json`
- Gmail Token: `G:\My Drive\Areas\Keys\Gmail\token.json` (auto-refreshed)
- OpenRouter Key: `G:\My Drive\Areas\Keys\api-personal-openrouter-keys.json`

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

**Why:**
- Avoids clutter (no duplicate daily plans)
- Single source of truth for today's plan
- Can run "process new" multiple times to refresh without creating mess

**Example:**
- 9am: Run "process new" → Creates "Daily Plan - Sunday, February 22, 2026"
- 2pm: Run "process new" again → **Updates same note** with latest emails/tasks
- Next day: Run "process new" → Creates "Daily Plan - Monday, February 23, 2026"

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
│         (Personal Combined View)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     1. Data Collection                   │
        └─────────────────────────────────────────┘
                              │
        ┌─────────┬───────────┼───────────┬─────────┐
        │         │           │           │         │
        ▼         ▼           ▼           ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Gmail  │ │Todoist │ │ Google │ │Calendar│ │ Drive  │
   │  API   │ │ API v1 │ │  Auth  │ │ Events │ │  Docs  │
   │Personal│ │ Tasks  │ │        │ │7 days  │ │7 days  │
   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
        │         │           │           │         │
        └─────────┴───────────┴───────────┴─────────┘
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
        │     - Create/Update daily Amplenote note │
        │     - Add tasks with action items        │
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
   - Includes due dates and priorities
   - Adds "📄 Documents in Progress" section
   - Shows Google Drive recent files
   - Adds "📧 Email Summary" section
   - Highlights newly created tasks from emails

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

**Sender Domain Patterns to Skip:**
```python
skip_domains = [
    'noreply', 'no-reply', 'donotreply', 'notifications',
    'marketing', 'newsletter', 'updates', 'alerts',
    'tiktok.com', 'facebook.com', 'instagram.com',
    'linkedin.com', 'twitter.com', 'x.com',
    'usps.com', 'fedex.com', 'ups.com',
    'creditkarma.com', 'mint.com', 'bankofamerica.com',
    'substack.com', 'medium.com', 'mailchimp.com'
]
```

**Always Included (Actionable Patterns):**
- ✅ **Real People**: Emails from colleagues, clients, family (personal names)
- ✅ **Important Services**: DMV, IRS, school, healthcare, government
- ✅ **Action Required**: Contains "please review", "need you to", "can you"
- ✅ **Deadline Indicators**: "by [date]", "due [date]", "deadline"
- ✅ **Urgency Markers**: "urgent", "asap", "today", "tomorrow"
- ✅ **Meeting Requests**: Calendar invites, meeting confirmations
- ✅ **Sign-ups/Registration**: "sign up", "register", "registration due"
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

### Missing Item Detection

**Flags Emails You May Have Overlooked:**

**Criteria for "Missing" Items:**
1. **From important sender** (colleague, manager, client)
2. **Contains action verb** ("please review", "need you to")
3. **Has deadline** ("by Friday", "due tomorrow")
4. **No corresponding Todoist task** exists
5. **Email is 1-2 days old** (not brand new, not too old)

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

**Purpose:** Focus here first. These are your most critical items.

**Example:**
```
🔥 Today (5 items)

⚡ Review Q1 budget - Email from manager@company.com
⚡ Submit expense report - Todoist
• Respond to client inquiry - Email from client@company.com
• Vehicle registration renewal - Email from DMV
• Conference scheduling - Todoist
```

### 📅 Tomorrow Section

**Criteria:**
- Due date is tomorrow

**Purpose:** Plan ahead. Review these to prepare for tomorrow.

**Example:**
```
📅 Tomorrow (3 items)

• Team meeting prep - Todoist
• Send project update - Email from project-lead@company.com
• Review contract - Todoist
```

### 📆 This Week Section

**Criteria:**
- Due date is within the next 7 days
- After tomorrow but before next week

**Purpose:** Keep on radar. Don't forget about these.

**Example:**
```
📆 This Week (4 items)

• Complete training module - Todoist
• Schedule dentist appointment - Email reminder
• Review performance goals - Todoist
• Submit timesheet - Email from HR
```

### 📦 Backlog Section

**Criteria:**
- No due date
- OR due date is more than 7 days away
- AND not marked as high priority

**Purpose:** Important but not urgent. Review weekly.

**Example:**
```
📦 Backlog (8 items)

• Research vacation destinations - Todoist
• Update resume - Todoist
• Organize photos - Todoist
... and 5 more items
```

---

## Running the Daily Planner

### First-Time Setup

**Prerequisites:**
- ✅ Gmail OAuth configured (credentials.json in Google Drive Keys folder)
- ✅ Todoist API token via credential resolver
- ✅ Amplenote OAuth token via credential resolver
- ✅ OpenRouter API key via credential resolver
- ✅ Python 3.7+ installed

**Verify Setup:**
```powershell
# Navigate to automation folder
cd "G:\My Drive\06_Skills\_automation"

# Install dependencies
pip install -r requirements.txt

# Run (will prompt for OAuth on first run)
python run_process_new_v2.py
```

### Daily Usage

**Morning Routine:**
```powershell
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

**Expected Output:**
```
================================================================================
COMPREHENSIVE PROCESS NEW WORKFLOW - V2
Analyzing email threads over 30 days with full context
================================================================================

📧 STEP 1: Fetching email threads (30 day lookback)...
   Found 49 total threads

🎯 STEP 2: Identifying priority threads...
   Selected 15 priority threads for analysis

🔗 STEP 2.5: Clustering related threads by sender...
   Clustered 15 threads into 13 groups

🔍 STEP 3: Analyzing threads comprehensively...
   Analyzing thread 1/13: Field trip permission due Friday
      - 2 emails in thread
      - Latest from: teacher@fcps.edu
      ✓ Priority: HIGH
      ✓ Action items: 1
      ✓ Follow-up needed: NO

✅ STEP 4: Fetching Todoist tasks...
   Found 5 tasks due today
   Found 8 upcoming tasks
   Found 2 STALE tasks (>7 days overdue)

📅 STEP 5: Fetching calendar events...
   Found 3 events today, 2 tomorrow

📝 STEP 6: Creating comprehensive daily summary...

📋 STEP 7: Preparing detailed breakdown...
   🔴 High priority (DO NOW): 4 threads
   ⚠️  Medium priority (DO SOON): 5 threads
   ℹ️  Low priority (monitor): 4 threads

📋 STEP 8: Creating individual Todoist tasks...
   ✅ Created (due 2026-05-15): Pay field trip fee via MySchoolBucks
   ✅ Created (due 2026-05-13): Respond to HOA about tree removal
   ...
   ✅ Created 7 total tasks

📝 STEP 9: Updating Amplenote daily note...
   ✅ Amplenote daily note updated successfully

================================================================================
COMPREHENSIVE ANALYSIS COMPLETE
================================================================================
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

**Plan for Tomorrow:**
- Check Tomorrow section
- Add any new tasks to Todoist
- Set priorities for next day

### Next Morning

**Generate Fresh Board:**
```powershell
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

**Benefits of Daily Refresh:**
- ✅ New urgent emails included
- ✅ Updated Todoist tasks
- ✅ Items automatically move between sections based on due dates
- ✅ Yesterday's completed items archived
- ✅ Clean slate with current priorities

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

### 5. Don't Create Tasks for Everything

**Only create tasks for:**
- ✅ Items requiring action from you
- ✅ Important deadlines or commitments
- ✅ Things you might forget

**Don't create tasks for:**
- ❌ FYI emails (just read and archive)
- ❌ Automated notifications (bank alerts, tracking)
- ❌ Marketing emails (unsubscribe instead)
- ❌ Things you'll remember anyway

**Remember:** The system already filters out unimportant emails. Trust the filtering.

### 6. Use Amplenote Features

**While working on tasks:**
- Add notes or context to task items
- Link related notes
- Use tags for categorization
- Set reminders for time-sensitive items

**Board is your workspace:**
- Not just a checklist
- Add details, thoughts, progress notes
- Reference information as needed

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
3. Re-authenticate: delete token and re-run
   ```powershell
   Remove-Item "G:\My Drive\Areas\Keys\Gmail\token.json"
   python run_process_new_v2.py
   ```

### Todoist Tasks Not Appearing

**Symptom:** "Found 0 active tasks" but you have tasks in Todoist

**Causes:**
- Todoist API token incorrect in credential resolver
- All tasks are low priority with no due dates (filtered out)
- Network connection issue

**Solutions:**
1. Verify Todoist token via credential_resolver
2. Add due dates or priorities to important tasks
3. Check internet connection

### Amplenote Sync Fails

**Symptom:** "API Error: 401 - invalid_token"

**Cause:** Amplenote token expired (tokens last 2 hours)

**Solution:**
```powershell
cd "G:\My Drive\06_Master_Guides\Scripts"
node refresh_amplenote_token.js
```

Then retry sync.

### Duplicate Tasks Appearing

**Symptom:** Same task appears multiple times

**Cause:** Title differs slightly between sources

**Solution:**
- Deduplication only works on exact title matches
- Manually delete duplicates in Amplenote
- Keep task titles consistent across sources

### Too Many Items in Today

**Symptom:** 20+ items in Today section

**Causes:**
- Too many high priority tasks in Todoist
- Many overdue items
- Urgency detection too aggressive

**Solutions:**
1. Review Todoist priorities - not everything is urgent
2. Clear out old overdue tasks
3. Adjust urgency keywords in gmail_tools.py if needed

---

## Advanced Usage

### Customizing Urgency Keywords

Edit `gmail_tools.py`:

```python
self.priority_keywords = [
    'school closed', 'school closing', 'schools closed',
    'field trip', 'permission slip',
    'registration due', 'renewal due', 'expires',
    'sign up', 'sign-up', 'signup', 'register',
    # Add your custom keywords:
    'your-custom-keyword'
]
```

### Adjusting Time Windows

**Change email lookback period:**
```python
# In run_process_new_v2.py, change days parameter:
all_threads = await thread_tools.get_thread_emails(days=14)  # Look back 14 days
```

### Adding Custom Sender Filters

**Skip specific senders:**
```python
# Add to skip_senders list in gmail_tools.py:
self.skip_senders = [
    'tiktok.com',
    'your-custom-sender@example.com',  # Add here
    # ... rest of list
]
```

**Always include specific domains:**
```python
# Add to whitelist_domains in gmail_tools.py:
self.whitelist_domains = [
    'fcps.edu',
    'your-important-domain.com',  # Add here
]
```

---

## Quick Reference Commands

### Daily Workflow

```powershell
# Full daily planning workflow
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

### Troubleshooting

```powershell
# Navigate to automation folder
cd "G:\My Drive\06_Skills\_automation"

# Install/update dependencies
pip install -r requirements.txt

# Re-authenticate Gmail
Remove-Item "G:\My Drive\Areas\Keys\Gmail\token.json"
python run_process_new_v2.py
```

---

## Example Daily Plan

### Sample Output in Amplenote

```markdown
# 📋 Daily Plan

📅 Wednesday, May 13, 2026

## Today
• 9:00 AM — Taekwondo class
• All day — No school (teacher workday)

## Action Items
☑️ Pay $55 field trip fee by May 15 via MySchoolBucks
  ↳ Mount Vernon field trip May 20. Payment due Friday.
☑️ Respond to HOA about tree removal request
  ↳ HOA requesting response by May 14. Tree overhangs shared fence.
☑️ Register for summer swim lessons before spots fill
  ↳ Registration opens today, limited spots.

## Do Soon
☑️ Review and sign updated HOA covenants (due May 20)
☑️ Schedule annual HVAC service (due May 30)

## Stale — Review or Close
• Update car registration — due 2026-04-30 (13d overdue)

## Rest of Week
• Thu May 14 — Dentist appointment at 2:00 PM
• Fri May 15 — Field trip fee deadline
• Sat May 16 — Taekwondo tournament

—
3 actions · 5 events · 1 stale · Generated 08:32 AM
```

---

## Integration with Other Systems

### Todoist

**Bi-directional sync:**
- Tasks from Todoist → Daily Plan
- Complete in Todoist → Removed from next day's plan
- Add to Todoist → Appears in next day's plan

**Best Practice:** Use Todoist as your task inbox. Daily planner pulls from it.

### Gmail

**One-way sync:**
- Urgent emails → Daily Plan
- Emails are not modified
- Archive manually after handling

**Best Practice:** Use email processing to create Todoist tasks, then daily planner pulls them.

### Amplenote

**One-way sync:**
- Daily Plan → Amplenote board
- Check off in Amplenote (doesn't sync back)
- New board created daily

**Best Practice:** Use Amplenote board for daily execution, Todoist for task management.

---

## Version History

| Version | Date | Changes |
|---------|------|----------|
| 3.1.0 | 2026-05-13 | Upgrade AI to claude-sonnet-4-5, remove OneDrive/Microsoft 365 integration, enable sign-up email capture |
| 3.0.0 | 2026-04-09 | AI Thread Analysis with Content Quality |
| 1.0.0 | 2026-02-22 | Initial release with Gmail, Todoist integration, smart filtering, Kanban board generation |

---

## Related Guides

- [MASTER_GUIDE_Email_Processing.md](MASTER_GUIDE_Email_Processing.md) - Email processing and filtering
- [MASTER_GUIDE_Amplenote_API_Integration.md](MASTER_GUIDE_Amplenote_API_Integration.md) - Amplenote API usage
- [MASTER_GUIDE_Environments_and_Credentials.md](MASTER_GUIDE_Environments_and_Credentials.md) - Credential management
- [MASTER_GUIDE_ROUTING_RULES.md](MASTER_GUIDE_ROUTING_RULES.md) - Routing rules

---

**End of Master Guide**

For questions or issues, refer to the troubleshooting section or related guides.
