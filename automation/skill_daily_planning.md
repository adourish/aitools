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
  │ AI         │  OpenRouter (claude-haiku-4-5) per thread:
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
  ┌─────┴──────────────────────────────────┐
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
- ✅ **Todoist tasks** - active tasks with priorities
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
- 📄 **Daily plan JSON** - Saved for Amplenote sync

### Key Features

✅ **Fully Autonomous Authentication** - Auto-refreshes tokens, triggers OAuth when needed, zero user prompts  
✅ **Gmail + Calendar Integration** - Scans 1 month of emails + 7 days of calendar events  
✅ **Smart Filtering** - Removes political emails, newsletters, sign-up emails, shipping notifications automatically  
✅ **Reference Email Detection** - Auto-saves emails with account numbers, confirmations, credentials  
✅ **Action-Priority Categorization** - DO NOW/DO SOON/MONITOR (not time-based)  
✅ **Calendar Event Integration** - Meetings and appointments included in daily plan  
✅ **Document Tracking** - Shows recent Google Drive files you're working on  
✅ **Holistic View** - Combines Gmail, Calendar, Todoist, and Drive  
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
- First run of the day → Creates new "📋 Daily Plan" note
- Subsequent runs same day → **Updates existing note** (doesn't create new one)
- Next day → Creates new note for new date

**Why:**
- Avoids clutter (no duplicate daily plans)
- Single source of truth for today's plan
- Can run "process new" multiple times to refresh without creating mess

**Example:**
- 9am: Run "process new" → Creates "📋 Daily Plan"
- 2pm: Run "process new" again → **Updates same note** with latest emails/tasks

**Workflow (100% Autonomous):**
1. **Auto-authenticate** → Gmail/Calendar/Drive OAuth (auto-refresh or trigger new flow)
2. **Scan Gmail** → 1 month of emails, filter out political/newsletter/sign-up/shipping
3. **Detect reference emails** → Auto-save account numbers, confirmations to Amplenote
4. **Scan Calendar** → Next 7 days of events
5. **Fetch Todoist** → All active tasks
6. **Scan Google Drive** → Last 7 days of document activity
7. **Categorize by Action-Priority** → DO NOW (urgent), DO SOON (important), MONITOR (awareness)
8. **Generate JSON plan** → Save to `output/` folder
9. **Sync to Amplenote** → Create daily note with Action-Priority sections
10. **Work from plan** → Clear priorities, full context, reference info linked

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│            HOLISTIC DAILY PLANNER SYSTEM                     │
│         (Personal + Work Combined View)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     1. Data Collection (run_process_new_v2.py)│
        └─────────────────────────────────────────┘
                              │
        ┌───────┼───────────┬───────────┐
        │         │           │           │
        ▼         ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Gmail  │ │Todoist │ │ Google │ │Calendar│
   │  API   │ │ API v1 │ │ Drive  │ │        │
   │Personal│ │ Tasks  │ │  Docs  │ │        │
   └────────┘ └────────┘ └────────┘ └────────┘
        │         │           │           │
        └───────┴───────────┴───────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     2. Smart Filtering & Prioritization  │
        │     - Skip spam/shipping notifications   │
        │     - Skip sign-up/registration emails   │
        │     - Detect urgency indicators          │
        │     - Extract due dates                  │
        │     - Remove duplicates                  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     3. AI Thread Analysis                │
        │     - claude-haiku-4-5 per thread        │
        │     - ACTION ITEMS, DEADLINE, PRIORITY   │
        │     - CONTEXT, FOLLOW_UP                 │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     4. Daily Output Generation           │
        │     - Todoist tasks (daily-plan label)   │
        │     - Amplenote rich-text note           │
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
   - Filters out spam, newsletters, sign-up emails, shipping notifications

2. **Intelligent Email Analysis** (15-20 seconds)
   - **Actionable vs Reference**: Classifies emails requiring action vs info-only
   - **Deadline extraction**: Parses "by Friday", "due tomorrow", "end of week"
   - **Urgency detection**: Identifies urgent, asap, deadline, today keywords
   - **Sender importance**: Prioritizes real people over automated systems
   - **Spam filtering**: Skips newsletters, marketing, sign-ups, social media, tracking
   - **Deduplication**: Removes duplicate items across sources

3. **Auto-Task/Note Creation** (10-15 seconds)
   - **Creates tasks in BOTH Todoist AND Amplenote** for actionable emails
   - **Todoist**: Permanent storage with due date, priority, labels
   - **Amplenote**: Daily Kanban view with checkbox, section, context
   - **Creates Amplenote notes** for important reference emails (non-actionable)
   - **Adds context**: Key details, sender

4. **Categorization** (5 seconds)
   - Sorts into High/Medium/Low priority
   - Filters expired deadlines and informational-only threads

5. **Board Creation** (45 seconds)
   - Creates/updates daily Amplenote note
   - Adds tasks with checkboxes
   - Includes due dates and priorities
   - Shows calendar events for today and tomorrow
   - Generates usage instructions

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
- ❌ **Sign-ups/Registration**: Sign-up links, enroll now, register now emails
- ❌ **Subscriptions**: Streaming services, app updates, software notifications

**Always Included (Actionable Patterns):**
- ✅ **Real People**: Emails from colleagues, clients, family (personal names)
- ✅ **Important Services**: DMV, IRS, school, healthcare, government
- ✅ **Action Required**: Contains "please review", "need you to", "can you"
- ✅ **Deadline Indicators**: "by [date]", "due [date]", "deadline"
- ✅ **Urgency Markers**: "urgent", "asap", "today", "tomorrow"
- ✅ **Meeting Requests**: Calendar invites, meeting confirmations
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

### Deduplication

Items are deduplicated across all sources using word-overlap analysis:
- **Gmail**: "Review Q1 budget by Friday"
- **Todoist**: "Review Q1 budget"
- **Result:** Single task in high-priority section (keeps most detailed version)

---

## Kanban Board Structure

### 🔥 DO NOW Section

**Criteria:**
- Due date is today or overdue
- OR marked as high priority with no due date
- OR contains urgency keywords (urgent, asap)
- Capped at 5 items (overflow goes to DO SOON)

### ⏰ DO SOON Section

**Criteria:**
- Medium priority items
- Deadline 7-30 days out
- Overflow from DO NOW

### 👁 MONITOR Section

**Criteria:**
- Low priority or informational threads
- No deadline or deadline > 30 days

### ⏳ Stale Tasks Section

**Criteria:**
- Todoist tasks more than 7 days overdue
- Shown separately for review/reschedule

---

## Running the Daily Planner

### Daily Usage

**Morning Routine:**
```powershell
cd "G:\My Drive\06_Skills\_automation"

# Install/update dependencies (first time only)
pip install -r requirements.txt

# Run daily planning
python run_process_new_v2.py
```

---

## Updating and Maintaining Your Board

### Throughout the Day

**In Amplenote:**
1. Open your daily plan note
2. Check off tasks as you complete them ✅
3. Add quick notes or updates to tasks as needed

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

### 2. Focus on DO NOW First

**Strategy:**
- Start with high priority items
- Work through DO NOW section before moving to DO SOON
- Don't worry about MONITOR until DO NOW is clear

**Goal:** Complete all DO NOW items before end of day.

### 3. Keep Todoist Updated

**Throughout Day:**
- Add new tasks as they come up
- Mark tasks complete in Todoist (not just Amplenote)
- Update due dates when priorities change

**Why:** Tomorrow's board will reflect these changes.

### 4. Weekly Backlog Review

**Every Friday or Sunday:**
- Review Stale Tasks section
- Delete tasks no longer relevant
- Promote important items by adding due dates

### 5. Don't Create Tasks for Everything

**Only create tasks for:**
- ✅ Items requiring action from you
- ✅ Important deadlines or commitments
- ✅ Things you might forget

**Don't create tasks for:**
- ❌ FYI emails (just read and archive)
- ❌ Automated notifications (bank alerts, tracking)
- ❌ Marketing emails (unsubscribe instead)
- ❌ Sign-up / registration emails

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
3. Re-authenticate Gmail (delete token.json and re-run)

### Todoist Tasks Not Appearing

**Symptom:** "Found 0 active tasks" but you have tasks in Todoist

**Causes:**
- Todoist API token incorrect
- All tasks are completed
- Network connection issue

**Solutions:**
1. Verify Todoist token in credential resolver
2. Check internet connection

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

```python
# In run_process_new_v2.py, change days parameter:
all_threads = await thread_tools.get_thread_emails(days=14)  # Look back 2 weeks
```

### Adding Custom Skip Filters

```python
# Add to skip_senders in gmail_tools.py:
self.skip_senders = [
    'your-custom-sender@example.com',
    # ... rest of list
]

# Add to skip_keywords in gmail_tools.py:
self.skip_keywords = [
    'your custom phrase',
    # ... rest of list
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
```

### Authentication Issues

```powershell
# Re-authenticate Gmail (delete token to trigger OAuth)
Remove-Item "G:\My Drive\03_Areas\Keys\Gmail\token.json"
python run_process_new_v2.py
```

---

## Integration with Other Systems

### Todoist

**Write:**
- Todoist tasks are created/updated by the daily planner (daily-plan label)
- Complete in Todoist → Removed from next day's plan

**Best Practice:** Use Todoist as your task inbox. Daily planner writes to it.

### Gmail

**One-way sync:**
- Urgent emails → Daily Plan
- Emails are not modified
- Archive manually after handling

### Amplenote

**One-way sync:**
- Daily Plan → Amplenote board
- Check off in Amplenote (doesn't sync back)
- New board created daily

---

## Version History

| Version | Date | Changes |
|---------|------|--------|
| 3.0.0 | 2026-04-09 | V3 AI thread analysis, claude-haiku-4-5, sign-up filtering |
| 2.0.0 | 2026-03-01 | V2 comprehensive thread analysis, Todoist integration |
| 1.0.0 | 2026-02-22 | Initial release with Gmail, Todoist integration |

---

## Related Guides

- [skill_email_processing.md](skill_email_processing.md) - Email processing and filtering
- [../system/skill_environments_credentials.md](../system/skill_environments_credentials.md) - Credentials management

---

**End of Master Guide**

For questions or issues, refer to the troubleshooting section or related guides.
