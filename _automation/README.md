# Daily Planning Automation Scripts

**Autonomous daily planning system that aggregates emails, calendar, and tasks into a prioritized action plan.**

---

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Credentials configured** in `environments.json` (see [Credentials Setup](#credentials-setup))
3. **Gmail OAuth** credentials (see [Gmail Setup](#gmail-setup))

### Run Daily Planning

```powershell
# Navigate to automation folder
cd "G:\My Drive\06_Skills\_automation"

# Install dependencies (first time only)
pip install -r requirements.txt

# Run daily planning
python run_process_new_v2.py
```

**Output:**
- Creates/updates daily plan in Amplenote
- Auto-creates tasks in Todoist for actionable emails
- Saves reference emails as Amplenote notes
- Generates JSON plan file in `daily_plans/` folder

**Time:** ~30-45 seconds total

---

## What This Does

### Inputs
- 📧 **Gmail emails** (past 1 month) - Intelligent filtering
- 📅 **Google Calendar events** (next 7 days) - Meetings and appointments
- ✅ **Todoist tasks** - Active tasks with priorities

### Processing
- 🧠 **AI-powered email analysis** - Detects actionable items vs spam
- 🎯 **Deadline extraction** - Parses due dates from natural language
- ✅ **Auto-creates tasks** in Todoist AND Amplenote
- 📝 **Auto-creates notes** in Amplenote for reference info

### Output
- 🎯 **DO NOW** - Urgent & important (due today/tomorrow)
- ⏰ **DO SOON** - Important (due this week)

---

## File Structure

```
_automation/
├── README.md                      # This file
├── run_process_new_v2.py         # Main entry point - run this
├── comprehensive_analyzer.py      # Email analysis and categorization
├── gmail_tools.py                # Gmail API integration
├── gmail_thread_tools.py         # Gmail thread processing
├── todoist_tools.py              # Todoist API integration
├── amplenote_tools.py            # Amplenote API integration
├── calendar_tools.py             # Google Calendar integration
├── auth_manager.py               # OAuth authentication handler
├── requirements.txt              # Python dependencies
├── config.json                   # Configuration settings
└── daily_plans/                  # Generated daily plans (JSON)
```

---

## Credentials Setup

### Required Credentials

All credentials are stored in:
```
G:\My Drive\03_Areas\Keys\Environments\environments.json
```

**Required entries:**
```json
{
  "todoist": {
    "api_token": "your_todoist_api_token"
  },
  "amplenote": {
    "api_token": "your_amplenote_api_token"
  }
}
```

### Get Todoist API Token
1. Go to https://todoist.com/app/settings/integrations
2. Scroll to "API token"
3. Copy token to `environments.json`

### Get Amplenote API Token
1. Go to https://www.amplenote.com/settings
2. Navigate to "API" section
3. Generate new token
4. Copy token to `environments.json`

---

## Gmail Setup

### OAuth Credentials

**Location:** `G:\My Drive\03_Areas\Keys\Gmail\credentials.json`

**First-time setup:**
1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable Gmail API, Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to Keys/Gmail folder

**Token file:** `G:\My Drive\03_Areas\Keys\Gmail\token.json`
- Auto-generated on first run
- Auto-refreshed when expired
- No manual intervention needed

**OAuth Scopes:**
```python
[
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
]
```

---

## Configuration

### config.json

```json
{
  "amplenote": {
    "daily_plan_tag": "daily-plan",
    "reference_tag": "reference"
  },
  "email_filters": {
    "days_to_scan": 30,
    "skip_domains": [
      "noreply",
      "notifications",
      "marketing"
    ]
  },
  "calendar": {
    "days_ahead": 7
  }
}
```

---

## Usage Examples

### Daily Morning Routine

```powershell
# Full workflow
cd "G:\My Drive\06_Skills\_automation"
python run_process_new_v2.py
```

### Check What Was Created

```powershell
# View latest daily plan JSON
cd "G:\My Drive\06_Skills\_automation\daily_plans"
dir | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

### Troubleshooting

```powershell
# Re-authenticate Gmail (if token expired)
# Just run the script - it will trigger OAuth flow automatically
python run_process_new_v2.py

# Check Todoist connection
python -c "import json; print(json.load(open('G:/My Drive/03_Areas/Keys/Environments/environments.json'))['todoist'])"

# Check Amplenote connection
python -c "import json; print(json.load(open('G:/My Drive/03_Areas/Keys/Environments/environments.json'))['amplenote'])"
```

---

## How It Works

### 1. Authentication (Autonomous)
- Checks for existing Gmail token
- Auto-refreshes if expired
- Triggers OAuth flow if needed (opens browser)
- Loads Todoist/Amplenote tokens from environments.json

### 2. Data Collection (30-45 seconds)
- Scans Gmail (1 month, ~100-500 emails)
- Fetches Calendar events (7 days ahead)
- Retrieves Todoist tasks (all active)

### 3. Smart Filtering
**Automatically skips:**
- Political emails
- Newsletters and marketing
- Shipping notifications
- Social media alerts
- Sign-up and registration solicitations
- Automated systems (noreply@)

**Automatically includes:**
- Emails from real people
- Work domain emails
- Important services (DMV, IRS, school, healthcare)
- Action-required emails

### 4. Email Analysis
- **Actionable detection:** "please review", "need you to", "can you"
- **Deadline extraction:** "by Friday", "due tomorrow", "end of week"
- **Urgency detection:** "urgent", "asap", "deadline", "today"
- **Reference detection:** Account numbers, confirmations, credentials

### 5. Task/Note Creation
- **Actionable emails** → Creates tasks in Todoist AND Amplenote
- **Reference emails** → Creates notes in Amplenote only
- **Deduplication** → Removes duplicates across sources

### 6. Categorization
- **DO NOW:** Due today/tomorrow OR high priority
- **DO SOON:** Due this week OR medium priority

### 7. Output Generation
- Creates/updates daily plan note in Amplenote
- Saves JSON plan to `daily_plans/` folder
- One plan per day (updates existing, doesn't duplicate)

---

## Best Practices

### Run Every Morning
- **When:** First thing, before checking email
- **Time:** 5-10 minutes (2 min to run, 3-8 min to review)
- **Benefit:** Clear priorities for the day

### Focus on DO NOW First
- Complete urgent items before moving to DO SOON
- Don't worry about lower-priority items until DO NOW is clear

### Keep Todoist Updated
- Add new tasks as they come up
- Mark complete in Todoist (not just Amplenote)
- Update due dates when priorities change

### Weekly Backlog Review
- Every Friday or Sunday
- Delete tasks no longer relevant
- Promote important items by adding due dates
- Break down large tasks

---

## Troubleshooting

### Gmail Authentication Failed
**Error:** "Token expired" or "Authentication required"

**Solution:**
```powershell
# Delete old token
Remove-Item "G:\My Drive\03_Areas\Keys\Gmail\token.json"

# Run script again - will trigger OAuth
python run_process_new_v2.py
```

### Todoist Tasks Not Appearing
**Check:**
1. Verify API token in `environments.json`
2. Ensure tasks are not completed
3. Check task filters (not in archived projects)

### Amplenote Note Not Created
**Check:**
1. Verify API token in `environments.json`
2. Check Amplenote account has space
3. Verify network connection

### No Emails Found
**Check:**
1. Gmail OAuth scopes include `gmail.readonly`
2. Email filters not too aggressive
3. Date range in `config.json` (default: 30 days)

---

## Advanced Configuration

### Customize Email Filters

Edit `config.json`:
```json
{
  "email_filters": {
    "days_to_scan": 30,
    "skip_domains": [
      "noreply",
      "notifications",
      "marketing",
      "your-custom-domain.com"
    ],
    "always_include_domains": [
      "yourcompany.com",
      "important-client.com"
    ]
  }
}
```

### Adjust Categorization Logic

Edit `comprehensive_analyzer.py`:
```python
# Change urgency thresholds
URGENT_KEYWORDS = ['urgent', 'asap', 'critical', 'immediate']

# Change deadline detection
DEADLINE_PATTERNS = [
    r'due (?:by |on )?(\w+)',
    r'deadline[:\s]+(\w+)',
    # Add custom patterns
]
```

---

## Related Skills

- **[skill_daily_planning.md](../automation/skill_daily_planning.md)** - Complete daily planning guide
- **[skill_email_processing.md](../automation/skill_email_processing.md)** - Email processing workflows
- **[skill_environments_credentials.md](../system/skill_environments_credentials.md)** - Credentials management

---

## Changelog

- **2026-10-05:** Fix token path to 03_Areas; upgrade AI to gpt-4o; add signup filtering; remove unimplemented drive step
- **2026-03-01:** Moved scripts from mcptools to skills repo _automation folder
- **2026-03-01:** Created comprehensive README with setup and usage instructions
- **2026-02-28:** Added comprehensive email analyzer with AI-powered categorization
- **2026-02-22:** Implemented autonomous OAuth authentication
- **2026-02-22:** Added reference email detection and auto-note creation

---

**Location:** `G:\My Drive\06_Skills\_automation\README.md`  
**Category:** Automation  
**Difficulty:** Intermediate  
**Dependencies:** Python 3.8+, Gmail API, Todoist API, Amplenote API
