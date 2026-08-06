# 09_MASTER_GUIDE: Process New

**One-Command Daily Planning: Autonomous Gmail + Calendar + Todoist + Drive Integration**

**Version:** 2.1.0 - Fully Autonomous  
**Last Updated:** May 4, 2026  
**Guide Number:** 09

---

## ⚠️ IMPORTANT FOR AI AGENTS

**USE THIS COMMAND (MCP Server):**
```powershell
cd "G:\My Drive\06_Master_Guides\MCP_Server"
python run_process_new.py
```

**DO NOT use `Scripts/daily_planner.py` unless you want to see a wrapper message.**

The MCP Server has all the latest features including:
- Smart email filtering (no promotional emails)
- Google Drive document scanning
- File system scanning (Inbox, Downloads)
- Automatic Todoist task creation (DakBoard compatible)
- Automatic Amplenote note creation (full content)

---

## What is "Process New"?

**One command to generate your complete daily action plan.**

Scans **all new content** - Emails, Tasks & Calendar, Files & Downloads, and Documents - then creates a prioritized Action-Priority plan showing exactly what to work on NOW vs SOON vs MONITOR.

---

## 📊 Data Sources Scanned

**Emails:**
- ✅ Gmail (last 1 month) - Urgent emails and reference info

**Tasks & Calendar:**
- ✅ Todoist (all active tasks)
- ✅ Google Calendar (next 7 days - **Alex Hartnett events auto-filtered**)

**Files & Downloads:**
- ✅ Inbox folder (`G:\My Drive\01_Operate\Inbox`) - Files needing filing
- ✅ Downloads folder - Recent files (last 7 days)

**Documents:**
- ✅ Google Drive (last 7 days)

---

## Quick Start (30 seconds)

**RECOMMENDED - Use MCP Server (Latest Features):**
```powershell
cd "G:\My Drive\06_Master_Guides\MCP_Server"
python run_process_new.py
```

**OR - Use Scripts Wrapper (Backward Compatible):**
```powershell
cd "G:\My Drive\06_Master_Guides\Scripts"
python daily_planner.py
```

**Both methods call the same MCP server code.**

**That's it.** Everything else is automatic:
- ✅ Auto-authenticates Gmail/Calendar/Drive (refreshes tokens or triggers OAuth)
- ✅ Scans all data sources
- ✅ Filters out spam/newsletters/political emails
- ✅ Detects reference emails (account numbers, confirmations)
- ✅ Categorizes by Action-Priority (DO NOW/SOON/MONITOR)
- ✅ Generates daily plan JSON
- ✅ Shows summary in terminal

**No prompts. No questions. No configuration needed.**

---

## What You'll Get

### 1. Terminal Output

```
✅ Gmail & Calendar authenticated
✅ Google Drive authenticated

╔════════════════════════════════════════════════════════════╗
║              Daily Planner - Generating Plan               ║
╚════════════════════════════════════════════════════════════╝

📧 Checking Gmail (last 1 month)...
   Found 3 urgent items from Gmail
   Found 3 reference emails with important info
📋 Fetching Todoist tasks...
   Found 2 active tasks
📅 Checking Google Calendar (next 7 days)...
   Found 10 upcoming events
📄 Checking Google Drive documents (last 7 days)...
   Found 0 recent Google Drive files

✨ Total unique items: 14

💾 Plan saved to: daily_plan_20260222.json

============================================================
DAILY PLAN SUMMARY (Action-Priority Model)
============================================================
🎯 DO NOW (7 items):
   • RE: [External] Max Dourish—Feb 19 (due 2026-02-22)
   • Max Dourish—Feb 19 (due 2026-02-22)
   • godzilla task 2 (due 2025-11-13)
   • 📅 Cleaners (due 2026-02-23)
   • 📅 Taekwondo (due 2026-02-23)

⏰ DO SOON (6 items):
   • Do taxes 💵 (due 2026-03-01)
   • 📅 Cancelled TKD February 25 Wednesday (due 2026-02-25)
   • 📅 Book Club (due 2026-02-25)

👀 MONITOR: 1 items

📌 REFERENCE: 3 important emails saved
   • Your Available Balance (from Bank of America)
   • Successful payment at Keep2Share

============================================================
Next: Run sync_plan_to_amplenote.js to create Action Plan
============================================================
```

### 2. DakBoard-Compatible Todoist Tasks

**Automatically created in your Todoist (6 individual tasks):**

```
🎯 TODAY: RE: [External] Max Dourish—Feb 19
🎯 TODAY: godzilla task 2
🎯 TODAY: 📅 Cleaners at 08:30 AM
🎯 TODAY: 📅 Taekwondo at 06:30 PM
⏰ SOON: 3 items this week
```

**Features:**
- ✅ **Individual tasks** - Each DO NOW item is a separate task (DakBoard shows full title)
- ✅ **Event times included** - "at 08:30 AM" visible on DakBoard
- ✅ **High priority (red)** - DO NOW tasks are priority 4
- ✅ **Medium priority (yellow)** - DO SOON summary is priority 2
- ✅ **Kill and fill** - Deletes ALL old daily plan tasks before creating new ones
- ✅ **No duplicates** - Clean slate every run
- ✅ **DakBoard optimized** - All details in task title, not description
- ✅ **Sign-up events skipped** - Registration and sign-up calendar events are not converted to tasks

**How it works:**
- **Every run:** Deletes ALL old `🎯 TODAY:` and `⏰ SOON:` tasks
- **Then creates:** DO NOW tasks + DO SOON summary
- **No accumulation** - Only current day's tasks exist
- **DakBoard displays:** Full task titles with times and details

### 3. Action-Priority Categories

**🎯 DO NOW** - Work on these today
- Emails due today/tomorrow
- Overdue tasks
- High priority items
- Calendar events today/tomorrow

**⏰ DO SOON** - Schedule time this week
- Tasks due this week
- Important emails
- Upcoming calendar events

**👀 MONITOR** - Keep aware, no action yet
- Items you're waiting on
- Background tasks
- Low priority items

**📌 REFERENCE** - Important info saved
- Account numbers
- Confirmation codes
- Passwords/credentials
- Important receipts

**📊 CONTEXT** - Background awareness
- Recent Google Drive documents
- Email activity summary

---

## Data Sources

### ✅ Working (Autonomous)

**Gmail** (1 month)
- Scans last 30 days
- Filters out: political emails, newsletters, shipping notifications
- Detects: urgent emails, reference info (account numbers, confirmations)

**Google Calendar** (7 days)
- Next 7 days of events
- Prioritizes events today/tomorrow as DO NOW
- Later events go to DO SOON
- Sign-up and registration events are automatically skipped

**Todoist**
- All active tasks
- Respects priorities and due dates

**Google Drive** (7 days)
- Recently modified documents
- Shows what you're working on

---

## Smart Filtering

### Automatically Skipped

**Political Emails:**
- Congressman, Senator, Representative
- house.gov, senate.gov, whitehouse.gov
- Campaign emails

**Newsletters & Updates:**
- "Sharing important updates"
- "Weekly update", "Monthly update"
- Generic announcements
- "Unsubscribe" links

**Shipping Notifications:**
- Amazon, FedEx, UPS, USPS
- Tracking numbers
- Delivery confirmations

**Marketing:**
- noreply@, no-reply@, donotreply@
- marketing@, promo@, newsletter@

**Personal Exclusions:**
- Excluded User emails (sender contains 'hartnett' or 'alexandra')
- Excluded User calendar events (organizer email: excluded-user@example.com)
- **Automatic filtering** - Any event organized by excluded-user@example.com is excluded
- Works for ALL future events from Alex's calendar

**Calendar Event Exclusions:**
- Sign-up and registration events (signup, sign up, sign-up, registration)
- Recurring routine events without special attention keywords

### Always Included

**Real People:**
- Colleagues, family, friends
- Personal email addresses

**Actionable Emails:**
- Contains deadlines
- Action required
- Urgent/ASAP markers
- Meeting requests

**Reference Info:**
- Account numbers
- Confirmation codes
- Credentials
- Important receipts

---

## Reference Email Detection

**Automatically detects and saves emails containing:**

- Account number, Account #, Acct #
- Confirmation number, Confirmation code
- Reference number, Ref #
- Policy number, Claim number
- Username, Password, Login credentials
- Activation code, Verification code
- Membership number, Customer ID
- Order number, Invoice number
- HOA, Homeowners association

**These are saved as separate Amplenote notes with links to original emails.**

---

## Authentication (100% Automatic)

### How It Works

1. **Check for existing token** - `G:\My Drive\03_Areas\Keys\Gmail\token.json`
2. **If token valid** - Use it
3. **If token expired** - Auto-refresh using refresh token
4. **If no token** - Auto-trigger OAuth flow (browser opens, you sign in once)
5. **Save new token** - For next time

**You never have to think about authentication. It just works.**

### OAuth Credentials

**Location:** `G:\My Drive\03_Areas\Keys\Gmail\credentials.json`

**Scopes:**
```python
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]
```

**Single token for all Google services** - Gmail, Calendar, Drive

---

## Troubleshooting

### "Gmail token expired"

**Don't worry.** Just run `python daily_planner.py` again. It will:
1. Detect expired token
2. Auto-trigger OAuth flow
3. Browser opens
4. Sign in with Google
5. Grant permissions
6. Token saved
7. Process continues automatically

**You only have to sign in once when token expires (every few weeks).**

### "Google Drive API not enabled"

Already enabled. If you see this error, it means the API was just enabled and needs a few minutes to propagate. Wait 5 minutes and try again.

### "No urgent emails found"

This is normal if:
- You don't have urgent emails in the last month
- All emails are from filtered senders (newsletters, etc.)
- Your inbox is clean

**Not an error - just means you're caught up!**

---

## What Gets Created

### 1. DakBoard Todoist Tasks

**Tasks in your Todoist inbox:**
- Individual DO NOW tasks with full details in title
- DO SOON summary task
- All details visible on DakBoard (not hidden in description)

**Kill and fill approach:**
- Every run: Deletes ALL old daily plan tasks
- Then creates: Fresh tasks with current priorities
- No duplicates or accumulated garbage

### 2. JSON File

**File:** `daily_plan_YYYYMMDD.json`

**Location:** `G:\My Drive\06_Master_Guides\Scripts\`

**Contains:**
```json
{
  "generated": "2026-05-04T13:09:21.364936",
  "do_now": [...],
  "do_soon": [...],
  "monitor": [...],
  "documents": {...},
  "reference_emails": [...],
  "email_summary": {...},
  "stats": {...}
}
```

**Used by:** `sync_plan_to_amplenote.js` to create Amplenote board

---

## Next Steps

### Option 1: Use DakBoard (Recommended)

**Your "process new" workflow now creates:**
1. ✅ Daily plan JSON file (`daily_plan_YYYYMMDD.json`) with email body previews
2. ✅ **Individual Todoist tasks** for DakBoard (top 5 DO NOW + DO SOON summary)
3. ✅ Amplenote note with full plan and email previews (when you run sync script)

### Option 2: Use Terminal Output

The terminal shows your complete daily plan. You can work from that.

### Option 3: Sync to Amplenote (Optional)

```powershell
node sync_plan_to_amplenote.js
```

Creates a formatted daily plan note in Amplenote with:
- Checkboxes for each task
- Sections for DO NOW/SOON/MONITOR
- **Email body previews** - See what action is needed without clicking
- Links to reference emails
- Document context
- Clear "How to Use This Plan" instructions at top
- Event times included (08:30 AM, 06:30 PM, etc.)

---

## Advanced: Customization

### Change Email Lookback Period

Edit `daily_planner.py` line ~590:
```python
gmail_items = self.get_gmail_emails(days=30)  # Change 30 to desired days
```

### Change Calendar Lookahead Period

Edit `daily_planner.py` line ~603:
```python
calendar_items = self.get_calendar_events(days=7)  # Change 7 to desired days
```

### Add Custom Filters

Edit `daily_planner.py` lines ~44-73:
```python
self.skip_senders = [
    'tiktok.com',
    'your-custom-sender@example.com',  # Add here
    # ... rest of list
]

self.skip_keywords = [
    'shipped',
    'your-custom-keyword',  # Add here
    # ... rest of list
]
```

---

## Summary

**Process new = One command for complete daily planning**

```powershell
python daily_planner.py
```

- ✅ Fully autonomous (no prompts, no questions)
- ✅ Auto-authenticates all services
- ✅ Scans Gmail, Calendar, Todoist, Drive
- ✅ Smart filtering (removes spam/newsletters/political/sign-ups)
- ✅ Reference email detection (account numbers, confirmations)
- ✅ Action-Priority categorization (DO NOW/SOON/MONITOR)
- ✅ Clear terminal output showing priorities
- ✅ JSON file for Amplenote sync (optional)

**Just run it every morning. That's it.**

---

## For Another Agent

**If you're an AI agent trying to run "process new" for the user:**

**IMPORTANT: Use MCP Server (not Scripts folder):**

1. Navigate to MCP Server: `cd "G:\My Drive\06_Master_Guides\MCP_Server"`
2. Run: `python run_process_new.py`
3. Wait for completion (30-60 seconds)
4. Read terminal output - that's the daily plan

**The MCP server automatically:**
- Creates Todoist tasks (DakBoard compatible)
- Creates Amplenote note with full content
- Scans Google Drive documents
- Scans file system (Inbox, Downloads)
- Filters promotional emails and sign-up events
- Uses Claude Sonnet for intelligent email analysis

**Don't ask the user for anything. Everything is automatic.**

**Alternative (backward compatible):**
- You can also run `python daily_planner.py` from Scripts folder
- It's a wrapper that calls the MCP server

**If you see authentication errors:**
- Just run the command again
- OAuth flow will trigger automatically
- User signs in once
- System continues

**The system is designed to be fully autonomous. Trust it.**
