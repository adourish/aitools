# Where Things Go: Complete Routing Rules

**Last Updated:** February 22, 2026

## Quick Reference
**Use when:** Deciding where a task, note, event, or file belongs; setting up a new workflow; onboarding to the system
**Don't use when:** You already know where something goes
**Trigger phrases:** "where does this go", "where should I put", "routing rules", "which system", "Todoist or Amplenote"
**Time:** Instant reference
**Rule:** Tasks → Todoist | Notes/daily view → Amplenote | Events → Google Calendar | Files → PARA on G Drive

---

## 📍 The Golden Rule

**Todoist = Tasks (Permanent Storage)**  
**Amplenote = Notes + Daily View (Temporary/Reference)**  
**Google Calendar = Events (Time-specific)**

---

## 📋 Tasks → Todoist + Amplenote

**Tasks are created in BOTH systems:**
- **Todoist** = Permanent storage (single source of truth)
- **Amplenote** = Daily Kanban view (refreshed daily)

### What Goes to Todoist:
- ✅ Tasks extracted from emails (Gmail + Outlook)
- ✅ Action items from meetings
- ✅ Things you need to do
- ✅ Items with deadlines
- ✅ Recurring tasks
- ✅ Project tasks
- ✅ **Auto-extracted actionable items** from email intelligence

### What Goes to Amplenote:
- ✅ **Same tasks as Todoist** (for daily Kanban board)
- ✅ Reference notes (confirmations, credentials, important info)
- ✅ Daily planning view (Today/Tomorrow/Week/Backlog)
- ✅ **Holistic daily plan** - Personal + Work combined
- ✅ **Document status** - Recent Google Drive + SharePoint files
- ✅ **Email summary** - Gmail + Outlook actionable items

### How Tasks Are Added:
- **Automatically via email intelligence**: Creates in BOTH Todoist AND Amplenote
- **Manually in Todoist**: Add here, appears in next day's Kanban board
- **Manually in Amplenote**: Only for today's view, won't persist

### Email → Task Routing Logic:

**Automatically Creates Task in BOTH Todoist AND Amplenote When Email Contains:**

**Personal Email (Gmail):**
1. **Deadline indicators**: "by [date]", "due [date]", "deadline", "before [date]"
2. **Action verbs**: "please review", "need you to", "can you", "submit", "complete", "send"
3. **Urgency markers**: "urgent", "asap", "today", "tomorrow", "this week"
4. **Request patterns**: "could you", "would you", "I need", "we need"
5. **From important senders**: Colleagues, managers, clients (not automated systems)

**Work Email (Outlook/Microsoft 365 via Microsoft Graph API):**
1. **Same criteria as Gmail** plus:
2. **Meeting requests** with action items in description
3. **Approval requests** from workflows
4. **Document review requests** with SharePoint links
5. **Team notifications** requiring response
6. **Calendar invites** with preparation tasks

**API:** Microsoft Graph API v1.0 (delegated permissions)
**Endpoint:** `https://graph.microsoft.com/v1.0/me/messages`
**Auth:** OAuth 2.0 with user consent (delegated, not application)

**Task Properties (Created in BOTH Systems):**

**Todoist (Permanent):**
- **Title**: Extracted action item (e.g., "Review Q1 budget")
- **Due Date**: Parsed from email content
- **Priority**: P1 = urgent, P2 = this week, P3 = later
- **Project**: Detected from email subject/content
- **Labels**: #email, #work, #personal
- **Description**: Link to original email + key context

**Amplenote (Daily View):**
- **Title**: Same as Todoist
- **Checkbox**: Unchecked task item
- **Section**: Today/Tomorrow/Week/Backlog (based on due date)
- **Context**: Email sender + deadline
- **Link**: To original email

### Why Todoist:
- Single source of truth for all tasks
- Syncs across all devices
- Supports priorities, due dates, projects
- Integrates with daily planner

---

## 📄 Documents → Google Drive + SharePoint

**Document tracking shows recent activity:**

### What Gets Tracked:
- ✅ **Google Drive**: Recently modified files (last 7 days)
  - API: Google Drive API v3
  - Endpoint: `/drive/v3/files`
  - Auth: OAuth 2.0 with Drive scope
- ✅ **File types**: Docs, Sheets, Slides, PDFs
- ✅ **Shared files**: Documents shared with you requiring review

### Document Info Displayed:
- **File name** and type
- **Last modified** date/time
- **Owner/Shared by**
- **Location** (folder/site)
- **Status**: Unread, needs review, in progress

### Routing:
- **Daily plan note** → Shows "📄 Documents in Progress" section
- **Action required** → Creates task if document has deadline
- **Reference only** → Listed for context

**Example:**
```
📄 Documents in Progress:
- Q1 Budget Report.xlsx (SharePoint) - Modified 2 hours ago by Manager
- Project Proposal.docx (Google Drive) - Shared with you yesterday
- Client Presentation.pptx (SharePoint) - Due for review by Friday
```

---

## 📝 Amplenote → Notes + Daily View

**Amplenote is for reference notes and temporary daily planning view**

### What Goes to Amplenote:

**1. Daily Kanban Board (Temporary)**
- Created fresh each morning
- Pulls from Todoist + urgent emails
- Shows: Today, Tomorrow, This Week, Backlog
- Can be deleted after the day
- **This is a VIEW, not storage**

**2. Reference Notes (Permanent)**
- Passwords and access codes
- Receipts and confirmations
- Important documentation
- Meeting notes with context
- Research and reference materials
- Master guides synced from Google Drive
- **Auto-extracted important info** from emails (non-actionable but important)

### Email → Note Routing Logic:

**Automatically Creates Amplenote Note When Email Contains:**
1. **Confirmation numbers**: Order confirmations, booking references
2. **Access credentials**: Passwords, login info, account details
3. **Important reference**: Policies, procedures, guidelines
4. **Meeting summaries**: Notes, decisions, action items for others
5. **Important announcements**: Company updates, policy changes
6. **No immediate action required** but needs to be saved

**Note Properties Set Automatically:**
- **Title**: Email subject + sender
- **Tags**: #email, #reference, #confirmation, #important
- **Content**: Full email body + attachments info
- **Metadata**: Date received, sender, original email link

### What Does NOT Go to Amplenote:
- ❌ Tasks (use Todoist)
- ❌ Permanent task lists
- ❌ Project task tracking

### Why Amplenote:
- Great for rich notes with formatting
- Good for daily planning view
- Excellent for reference documentation
- Not designed for task management

---

## 📅 Google Calendar → Events

**Time-specific events only**

### What Goes to Calendar:
- ✅ Meetings with specific times
- ✅ Appointments
- ✅ Deadlines with specific dates
- ✅ Events with attendees
- ✅ Recurring events

### What Does NOT Go to Calendar:
- ❌ General tasks (use Todoist)
- ❌ Things without specific times

---

## � Files → PARA System (G Drive)

**All files go to PARA locations based on purpose**

### File Routing by Type:

**Downloads → Operate/Inbox** (temporary staging)
- All new downloads start here
- Process daily to move to permanent locations

**Active Work → Operate or Projects**
- Today's work → Operate/Today
- This week's work → Operate/This_Week
- Project files → Projects/[ProjectName]

**Reference Materials → Resources**
- Documentation → Resources/Documentation
- Media → Resources/Media
- Templates → Resources/Templates

**Ongoing Responsibilities → Areas**
- Keys/Credentials → Areas/Keys
- Personal → Areas/Personal
- Work → Areas/Work

**Completed Items → Archive**
- Finished projects → Archive/Projects
- Old files → Archive/[Category]

### Quick Decision Tree:
```
New file downloaded?
    ↓
Operate/Inbox (staging)
    ↓
Is it for active project? → Projects/[ProjectName]
Is it reference material? → Resources/[Category]
Is it ongoing responsibility? → Areas/[Category]
Is it completed work? → Archive/[Category]
Is it today's work? → Operate/Today
```

**For detailed filing rules, see:** [07_MASTER_GUIDE_FILE_ORGANIZATION.md](07_MASTER_GUIDE_FILE_ORGANIZATION.md)

---

## �� Complete Workflows

### Daily Planning Workflow

```
Morning:
1. Run: python daily_planner.py && node sync_plan_to_amplenote.js
2. Result: Kanban board in Amplenote (pulls from Todoist)
3. Work from Kanban board throughout day
4. Add new tasks to Todoist (not Amplenote)
```

**Flow:**
```
Todoist (tasks) + Urgent Emails
         ↓
   Daily Planner
         ↓
Amplenote Kanban Board (temporary view)
```

### Weekly Email Processing Workflow

```
Weekly:
1. Run: python email_processor.py --days 7
2. Run: node sync_email_to_services.js
3. Result:
   - Tasks → Todoist
   - Events → Listed for Google Calendar
   - Important emails → Amplenote notes
```

**Flow:**
```
Gmail Inbox
     ↓
Email Processor
     ├─→ Tasks → Todoist
     ├─→ Events → Google Calendar (manual)
     └─→ Notes → Amplenote
```

---

## ❌ Common Mistakes to Avoid

### Mistake 1: Creating Tasks in Amplenote
**Wrong:** Creating task lists in Amplenote  
**Right:** Create tasks in Todoist, view them in Amplenote Kanban board

### Mistake 2: Treating Kanban Board as Permanent
**Wrong:** Keeping old Kanban boards forever  
**Right:** Delete yesterday's board, create fresh one each day

### Mistake 3: Adding Tasks to Calendar
**Wrong:** Creating calendar events for general tasks  
**Right:** Only time-specific events in Calendar, tasks in Todoist

### Mistake 4: Duplicating Tasks
**Wrong:** Task in both Todoist and Amplenote  
**Right:** Task in Todoist, viewed in Amplenote Kanban board

---

## 🎯 Quick Decision Tree

**I have something to do:**
- Has specific time? → Google Calendar
- General task? → Todoist
- Reference info? → Amplenote note

**I'm processing emails:**
- Action required? → Extract task to Todoist
- Meeting invite? → Add to Google Calendar
- Important info to save? → Create Amplenote note
- Unimportant? → Archive/delete

**I'm planning my day:**
- Run daily planner → Creates Kanban board in Amplenote
- Work from Kanban board
- Add new tasks to Todoist (not Amplenote)

---

## 📊 Current State (What Needs Cleanup)

### In Amplenote Now:
1. ✅ **Daily Plan - Sunday, February 22, 2026** - KEEP (today's Kanban board)
2. ❌ **Email Processing - Week of 2/15/2026** - Should have created tasks in Todoist instead
3. ✅ **Master Guides** - KEEP (reference documentation)
4. ✅ **Other notes** - KEEP (reference materials)

### Action Needed:
1. Delete "Email Processing - Week of 2/15/2026" note (tasks should be in Todoist)
2. Going forward: Email processing creates tasks in Todoist, not Amplenote
3. Only create Amplenote notes for reference information

---

## 🔧 Scripts and Their Routing

### daily_planner.py
**Reads from:**
- Todoist (tasks)
- Gmail (urgent emails)

**Writes to:**
- JSON file (intermediate)

### sync_plan_to_amplenote.js
**Reads from:**
- JSON file from daily_planner.py

**Writes to:**
- Amplenote (Kanban board note only)

### email_processor.py
**Reads from:**
- Gmail

**Writes to:**
- JSON file (intermediate)

### sync_email_to_services.js
**Reads from:**
- JSON file from email_processor.py

**Writes to:**
- Todoist (tasks)
- Amplenote (reference notes only)
- Console (events for manual calendar entry)

---

## ✅ Correct Usage Examples

### Example 1: Morning Routine
```
1. Run daily planner
2. Open Amplenote Kanban board
3. See tasks from Todoist organized by priority
4. Work through Today section
5. Add new task? → Add to Todoist
6. Tomorrow: Fresh Kanban board pulls updated Todoist tasks
```

### Example 2: Email Processing
```
1. Run email processor weekly
2. Script extracts:
   - "Review Q1 budget" → Creates in Todoist
   - "Meeting Tuesday 2pm" → Lists for Calendar
   - "Password reset confirmation" → Creates Amplenote note
3. Check Todoist to see new tasks
4. Add calendar events manually
5. Reference notes saved in Amplenote
```

### Example 3: Adding a Task
```
Wrong: Create task in Amplenote
Right: 
  1. Open Todoist
  2. Add task with due date
  3. Tomorrow's Kanban board will show it
```

---

## 🆘 Troubleshooting

**Q: I don't see my Todoist tasks in Amplenote**  
A: Run daily planner to create fresh Kanban board

**Q: Tasks in Amplenote aren't syncing to Todoist**  
A: They won't - Amplenote is read-only view. Add tasks to Todoist directly.

**Q: Should I keep old Kanban boards?**  
A: No, delete them. Create fresh one each day.

**Q: Where do I add new tasks?**  
A: Always add to Todoist. They'll appear in tomorrow's Kanban board.

**Q: Email processing created tasks in Amplenote**  
A: That's a bug in the script. Tasks should go to Todoist. Delete the Amplenote note with tasks.

---

## 📞 Summary

**Remember:**
- 📋 Todoist = All tasks (permanent)
- 📝 Amplenote = Notes + daily view (temporary/reference)
- 📅 Calendar = Time-specific events

**Daily workflow:**
1. Morning: Generate Kanban board (pulls from Todoist)
2. Work from Kanban board
3. Add new tasks to Todoist
4. Tomorrow: Fresh board with updated tasks

**Weekly workflow:**
1. Process emails
2. Tasks → Todoist
3. Notes → Amplenote
4. Events → Calendar

---

**End of Routing Rules**

Refer to this document whenever you're unsure where something should go.
