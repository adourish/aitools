# MASTER GUIDE: Daily Planning & Kanban System

**Fully Autonomous Holistic Daily Planning: Gmail + Calendar + Todoist → Prioritized Daily Plan**

**Last Updated:** May 24, 2026
**Version:** 3.1.0 - AI Thread Analysis with Content Quality (Todoist-only output)

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
  │            │  6. Skip sign-up/registration calendar events
  └─────┬──────┘
        │
  ▼
Todoist Tasks
• Clean title (action only)
• Concise description (context + sender)
• AI-extracted due date
• daily-plan label
• Calendar events included (non-routine, non-signup)
• JSON output saved to output/ directory
```

### Key Files

| File | Purpose |
|------|--------|
| `_automation/run_process_new_v2.py` | Main orchestrator — all steps |
| `_automation/gmail_tools.py` | Gmail fetch, sender filtering, priority keywords |
| `_automation/gmail_thread_tools.py` | Thread grouping, priority scoring, clustering |
| `_automation/comprehensive_analyzer.py` | AI prompt (claude-sonnet-4-5), response parsing, deduplication |
| `_automation/todoist_tools.py` | Task CRUD with Todoist REST API |
| `_automation/calendar_tools.py` | Google Calendar event fetch |
| `_automation/auth_manager.py` | Credential resolution for all services |
| `_automation/credential_resolver.py` | Cascade credential lookup (env files → KeePass) |

### Content Quality Rules (V3)

**AI Prompt (claude-sonnet-4-5 via OpenRouter):**
- Provides today's date — past-deadline actions are rejected ("None - deadline passed")
- CONTEXT must be specific: "Mount Vernon trip May 12. $65 if chaperoning." not "This is an educational opportunity"
- Priority levels: High (7 days), Medium (7-30 days), Low (informational/expired)

**Post-processing:**
- Threads with `deadline < today` are auto-expired and filtered out
- Follow-ups referencing past dates are silently removed
- Stale Todoist tasks (>7 days overdue) shown in separate section
- Sign-up / registration calendar events are always skipped

**Todoist tasks:**
- Title = action only (no summary appended)
- Description = context + sender (2-3 lines, no emoji field dumps)
- Due date = AI-extracted deadline, not hardcoded "today"
- Results go to Todoist only (DakBoard-compatible)

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Daily Planning Workflow](#daily-planning-workflow)
4. [Smart Prioritization Logic](#smart-prioritization-logic)
5. [Running the Daily Planner](#running-the-daily-planner)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This system creates a **smart daily action plan** that aggregates your important tasks from multiple sources into a single, prioritized Todoist task list.

### What It Does

**Inputs:**
- 📧 **Gmail emails** (past 1 month) - personal email, intelligent filtering
- 📅 **Google Calendar events** (next 7 days) - upcoming meetings and appointments
- 📋 **Todoist tasks** - active tasks with priorities

**Intelligent Processing:**
- 🧠 **AI-powered email analysis** (claude-sonnet-4-5) - Detects actionable items vs spam/newsletters
- 🎯 **Deadline extraction** - Parses due dates from natural language
- ✅ **Auto-creates tasks in Todoist** - For emails requiring action
- 🔍 **Smart filtering** - Removes sign-ups, recurring events, and promotions

**Output:**
- 🎯 **Todoist tasks** with sections:
  - 🎯 **DO NOW** (priority 4/red) - Urgent & important (due today/tomorrow, high priority)
  - ⏰ **DO SOON** (priority 3/orange) - Important (due this week, medium priority)
  - 📌 **FOLLOW-UP** (priority 2/blue) - Waiting-on threads, follow-up reminders
  - 📅 **CALENDAR** label - Non-routine calendar events
- 💾 **JSON output** - Full analysis saved to `_automation/output/`

### Authentication Status

**✅ FULLY WORKING (Autonomous):**
- Gmail (1 month of emails) - OAuth auto-handled
- Google Calendar (7 days of events) - OAuth auto-handled
- Todoist (all active tasks) - API token via credential resolver

**OAuth Credentials Location:**
- Gmail/Calendar: `G:\My Drive\03_Areas\Keys\Gmail\credentials.json`
- Gmail Token: `G:\My Drive\03_Areas\Keys\Gmail\token.json` (auto-refreshed)
- OpenRouter: resolved via `api-personal-openrouter-keys.json` in Keys/Environments/
- Todoist: resolved via `api-personal-todoist-keys.json` in Keys/Environments/

---

## Daily Planning Workflow

### Morning Routine

```powershell
# Navigate to automation folder
cd "G:\My Drive\06_Skills\_automation"

# Run daily planning
python run_process_new_v2.py
```

**What Happens (9 steps):**

1. **Email Thread Fetch** - Gmail last 30 days
2. **Priority Filtering** - Top 15 threads by score
3. **Thread Clustering** - Group related sender threads
4. **AI Analysis** - claude-sonnet-4-5 analyzes each thread for ACTION ITEMS, DEADLINE, PRIORITY, CONTEXT
5. **Calendar Fetch** - Next 7 days of events
6. **Daily Summary** - Top 3 actions for quick review
7. **Post-Processing** - Deduplicate, expire past deadlines, filter informational
8. **Todoist Task Creation** - Clean slate (delete old daily-plan tasks), then create new
   - High priority email actions → priority 4 (red)
   - Medium priority → priority 3 (orange)
   - Waiting-on threads → priority 2 (blue) with follow-up label
   - Non-routine calendar events → calendar label (sign-ups always skipped)
9. **JSON Output** - Full analysis saved to `_automation/output/`

---

## Smart Prioritization Logic

### Automatically Skipped

**Email Senders (skip_senders):**
- Shipping/tracking: Amazon, FedEx, UPS, USPS
- Marketing: tiktok.com, bankofamerica.com, bestbuy.com
- Newsletters: Motley Fool, Seeking Alpha, Audible
- Political: house.gov, senate.gov, whitehouse.gov, campaign@

**Email Keywords (skip_keywords):**
- Shipping: shipped, delivered, tracking, package
- Promotions: deal ends, sale, discount, flash sale, shop now

**Calendar Events (always skipped):**
- Sign-up / registration events: `sign up`, `signup`, `sign-up`, `registration`, `tryout`, `try out`
- Recurring events that don't need attention (no doctor/cancelled/interview/etc.)

### Always Included

**Whitelisted Domains:**
- fcps.edu, fairfaxcounty.gov, townsq.io, virginiadmv, irs.gov, aggressor.com, padi.com

**Priority Keywords:**
- school closed, field trip, permission slip, appointment reminder
- registration due, expires, today at, deadline today, certification

### Calendar Attention Keywords

Calendar events with these keywords bypass the recurring-event filter:
```
cancelled, canceled, rescheduled, moved,
dr, doctor, dentist, appointment,
pickup, drop off, deadline, due, expires,
interview, presentation, demo, flight, travel, hotel, checkout
```

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
3. Delete token to re-auth: `Remove-Item "G:\My Drive\03_Areas\Keys\Gmail\token.json"`

### OpenRouter API Error

**Symptom:** `OpenRouter API error: 401` or `403`

**Cause:** OpenRouter API key expired or invalid

**Solution:**
1. Check `api-personal-openrouter-keys.json` in Keys/Environments/
2. Verify the `credentials.apiKey` field is valid
3. The key is used via CredentialResolver — check `~/.credentials/config.json` paths

### Todoist Tasks Not Creating

**Symptom:** "Error creating Todoist tasks"

**Causes:**
- Todoist API token incorrect or expired
- Network issue

**Solutions:**
1. Verify `api-personal-todoist-keys.json` in Keys/Environments/
2. Check `credentials.apiToken` field

### Credential Resolver Fails

**Symptom:** `FileNotFoundError: Resolver config not found`

**Cause:** `~/.credentials/config.json` not present on this machine

**Solution:**
1. Run `python _scripts/migrate_personal_credentials.py` to set up resolver
2. Or check `system/skill_environments_credentials.md` for full setup guide

---

## Best Practices

1. **Run every morning** — fresh slate of daily-plan tasks created each run
2. **Trust the filtering** — sign-ups, promotions, and recurring events are skipped automatically
3. **Review JSON output** — `_automation/output/comprehensive_analysis_*.json` has full detail
4. **DO NOW cap = 5** — overflow goes to DO SOON automatically
5. **Credentials stay local** — keys are in Google Drive (local sync) and KeePass, never in repo

---

## Related Guides

- `system/skill_environments_credentials.md` - Credential management and key file locations
- `system/skill_process_new.md` - Original process new overview
- `integrations/skill_todoist_api.md` - Todoist API reference
- `_automation/README.md` - Automation folder overview

---

**End of Master Guide**
