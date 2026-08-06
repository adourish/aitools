# G Drive Complete Filing Guide

## Quick Reference
**Use when:** Downloads folder is cluttered, new files need routing, unsure where something belongs in G Drive
**Don't use when:** File already has an obvious home or you're organizing work deliverables (use pskills routing instead)
**Trigger phrases:** "file my downloads", "where does this go", "organize my files", "file organization", "clean up downloads"
**Time:** 10-30 minutes depending on volume
**Command:** Ask AI to review Downloads folder and suggest PARA locations

## Table of Contents
1. [Overview](#overview)
2. [Input Locations - Where New Files Enter the System](#input-locations---where-new-files-enter-the-system)
3. [PARA System Structure](#para-system-structure)
4. [01_Operate - Daily Operations](#01_operate---daily-operations)
5. [02_Projects - Active Projects](#02_projects---active-projects)
6. [03_Areas - Ongoing Responsibilities](#03_areas---ongoing-responsibilities)
7. [04_Resources - Reference Materials](#04_resources---reference-materials)
8. [05_Archive - Completed Items](#05_archive---completed-items)
9. [Media Filing Rules](#media-filing-rules)
10. [Naming Conventions](#naming-conventions)
11. [Processing Workflows](#processing-workflows)
12. [File Lineage Tracking System](#file-lineage-tracking-system)
13. [Automation Scripts](#automation-scripts)
14. [Best Practices](#best-practices)
15. [Troubleshooting](#troubleshooting)
16. [FAQ](#faq)
17. [Quick Reference](#quick-reference)
18. [Maintenance Schedule](#maintenance-schedule)

---

## Overview

**G Drive Location**: `G:\My Drive\`

**Purpose**: Comprehensive personal knowledge management system using the PARA method (Projects, Areas, Resources, Archive) with an additional Operate layer for daily operations.

**Key Principles**:
- Everything has a designated place in the PARA hierarchy
- Active work lives in Operate and Projects
- Ongoing responsibilities in Areas
- Reference materials in Resources
- Completed items move to Archive
- Consistent naming conventions across all categories
- Regular review and maintenance

---

## PARA System Structure

```
G:\My Drive\
├── 01_Operate/          # Daily operations and immediate tasks
├── 02_Projects/         # Active projects with defined end dates
├── 03_Areas/            # Ongoing responsibilities without end dates
├── 04_Resources/        # Reference materials and knowledge base
├── 05_Archive/          # Completed projects and inactive items
└── [Root scripts and documentation]
```

---

## 01_Operate - Daily Operations

### Purpose
Temporary workspace for immediate tasks, daily processing, and active work-in-progress items.

### Structure
```
01_Operate/
├── Inbox/              # Unprocessed items awaiting filing
├── Today/              # Current day's active work
├── This_Week/          # Weekly priorities
├── Processing/         # Items being actively worked on
└── Quick_Reference/    # Frequently accessed shortcuts
```

### Filing Rules

#### What Goes in Operate
- **Inbox**: All new downloads, emails to process, unorganized files
- **Today**: Tasks and files needed for current day
- **This_Week**: Weekly goals and associated materials
- **Processing**: Files actively being edited or reviewed
- **Quick_Reference**: Links, notes, templates used daily

#### What Does NOT Go in Operate
- Completed work (→ move to Projects or Archive)
- Reference materials (→ move to Resources)
- Long-term storage (→ move to Areas or Archive)

#### Processing Workflow
1. **Daily**: Review Inbox, move items to appropriate PARA locations
2. **Weekly**: Clear out This_Week, archive completed items
3. **Monthly**: Ensure Operate contains only active work

#### Example Files
```
01_Operate/
├── Inbox/
│   ├── Downloaded_Article_2026-01-11.pdf
│   └── Email_Attachment_Meeting_Notes.docx
├── Today/
│   ├── Budget_Review_Draft.xlsx
│   └── Client_Presentation_v2.pptx
└── Processing/
    └── Video_Edit_Project_WIP/
```

---

## 02_Projects - Active Projects

### Purpose
Projects are endeavors with a specific goal and end date. Once complete, they move to Archive.

### Structure
```
02_Projects/
├── [Project_Name]/
│   ├── 00_Project_Brief.md
│   ├── Planning/
│   ├── Assets/
│   ├── Deliverables/
│   └── Notes/
```

### Filing Rules

#### What Qualifies as a Project
- Has a clear, specific goal
- Has a defined completion date
- Requires multiple steps or sessions
- Will be "done" at some point

#### Project Naming Convention
Format: `YYYY-MM_Project_Name_Brief_Description`

Examples:
- `2026-01_Website_Redesign`
- `2026-02_Tax_Preparation_2025`
- `2026-03_Home_Office_Setup`

#### Project Folder Structure
Each project should contain:
- **00_Project_Brief.md**: Goals, timeline, success criteria
- **Planning/**: Plans, schedules, task lists
- **Assets/**: Source files, images, documents
- **Deliverables/**: Final outputs
- **Notes/**: Meeting notes, research, ideas

#### Project Lifecycle
1. **Creation**: Create folder in 02_Projects with proper naming
2. **Active Work**: Keep all related files within project folder
3. **Completion**: Move entire folder to 05_Archive
4. **Review**: Quarterly review to archive stalled projects

#### Example Projects
```
02_Projects/
├── 2026-01_Kitchen_Renovation/
│   ├── 00_Project_Brief.md
│   ├── Planning/
│   │   ├── Budget.xlsx
│   │   └── Timeline.md
│   ├── Assets/
│   │   ├── Design_Mockups/
│   │   └── Contractor_Quotes/
│   └── Deliverables/
│       └── Final_Design.pdf
├── 2026-02_Learn_Python/
│   ├── 00_Project_Brief.md
│   ├── Code_Examples/
│   ├── Exercises/
│   └── Notes/
```

---

## 03_Areas - Ongoing Responsibilities

### Purpose
Areas are ongoing responsibilities without end dates. They require regular attention and maintenance.

### Structure
```
03_Areas/
├── [Area_Name]/
│   ├── Active/
│   ├── Reference/
│   ├── Templates/
│   └── Archive/
```

### Filing Rules

#### What Qualifies as an Area
- Ongoing responsibility (no end date)
- Requires regular maintenance
- Has standards to uphold
- Part of your life or work role

#### Common Areas
- **Health & Fitness**: Medical records, workout plans, nutrition
- **Finances**: Budgets, investments, bills
- **Home Maintenance**: Manuals, warranties, repair records
- **Professional Development**: Certifications, training, skills
- **Relationships**: Important contacts, gift ideas, event planning

#### Area Naming Convention
Format: `Area_Name` (simple, descriptive)

Examples:
- `Health_Fitness`
- `Finance_Personal`
- `Home_Maintenance`
- `Career_Development`

#### Area Folder Structure
- **Active/**: Current documents and work
- **Reference/**: Important reference materials
- **Templates/**: Reusable templates and forms
- **Archive/**: Old but potentially useful materials

#### Maintenance Schedule
- **Weekly**: Review active items
- **Monthly**: Update reference materials
- **Quarterly**: Archive outdated items
- **Yearly**: Comprehensive review and cleanup

#### Example Areas
```
03_Areas/
├── Health_Fitness/
│   ├── Active/
│   │   ├── Current_Workout_Plan.pdf
│   │   └── Meal_Prep_Schedule.xlsx
│   ├── Reference/
│   │   ├── Medical_Records/
│   │   └── Lab_Results/
│   └── Templates/
│       └── Weekly_Meal_Template.xlsx
├── Finance_Personal/
│   ├── Active/
│   │   ├── 2026_Budget.xlsx
│   │   └── Monthly_Expenses_Tracker.xlsx
│   ├── Reference/
│   │   ├── Tax_Documents/
│   │   └── Investment_Statements/
│   └── Archive/
│       └── 2025_Financial_Records/
```

---

## 04_Resources - Reference Materials

### Purpose
Resources are reference materials, knowledge bases, and assets you may need in the future but aren't actively working on.

### Structure
```
04_Resources/
├── Media/              # Videos, photos, magazines, music
├── Documents/          # PDFs, articles, ebooks
├── Learning/           # Courses, tutorials, educational content
├── Templates/          # Reusable templates and forms
├── Tools/              # Software, scripts, utilities
└── Knowledge_Base/     # Notes, wikis, reference guides
```

### Filing Rules

#### What Goes in Resources
- Reference materials for potential future use
- Learning resources and courses
- Media collections (organized)
- Templates and reusable assets
- Knowledge bases and documentation
- Tools and utilities

#### Resource Categories

##### Media Resources
Location: `04_Resources/Media/`

Structure:
```
Media/
├── Video/
│   ├── Spicy/          # Adult content
│   ├── Movies/         # Films
│   ├── TV_Shows/       # Television series
│   └── Educational/    # Tutorials, courses
├── Pictures/
│   ├── Spicy/          # Adult content
│   ├── Photography/    # Personal photos
│   └── Stock_Images/   # Stock photography
├── Magazines/
│   ├── Spicy/
│   │   └── Collections/
│   │       ├── [Magazine_Name]/
│   └── General/
├── Music/
│   ├── By_Artist/
│   ├── By_Genre/
│   └── Playlists/
└── Audio/
    ├── Podcasts/
    ├── Audiobooks/
    └── Sound_Effects/
```

**Media Filing Rules**: See [Media Filing Rules](#media-filing-rules) section below.

##### Document Resources
Location: `04_Resources/Documents/`

Structure:
```
Documents/
├── Articles/           # Saved articles and blog posts
├── Ebooks/            # Digital books
├── Research_Papers/   # Academic and research materials
├── Manuals/           # User manuals and guides
└── Reference/         # General reference documents
```

**Document Naming**: `YYYY-MM-DD_Title_Author.pdf`

##### Learning Resources
Location: `04_Resources/Learning/`

Structure:
```
Learning/
├── Courses/
│   ├── [Course_Name]/
│   │   ├── Videos/
│   │   ├── Materials/
│   │   └── Notes/
├── Tutorials/
├── Certifications/
└── Practice_Projects/
```

##### Tools and Scripts
Location: `04_Resources/Tools/`

Structure:
```
Tools/
├── Scripts/
│   ├── PowerShell/
│   ├── Python/
│   └── Batch/
├── Software/
│   ├── Installers/
│   └── Portable_Apps/
└── Utilities/
```

#### Resource Maintenance
- **Monthly**: Review new additions, ensure proper filing
- **Quarterly**: Remove duplicates, update organization
- **Yearly**: Archive unused resources, update structure

---

## 05_Archive - Completed Items

### Purpose
Archive stores completed projects, inactive areas, and historical materials that may be needed for reference.

### Structure
```
05_Archive/
├── Projects/
│   └── YYYY/
│       └── [Completed_Project_Name]/
├── Areas/
│   └── [Former_Area_Name]/
└── Resources/
    └── [Outdated_Resources]/
```

### Filing Rules

#### What Goes in Archive
- Completed projects
- Inactive or discontinued areas
- Outdated resources still worth keeping
- Historical records and documentation

#### Archive Naming Convention
Maintain original naming but organize by year:
- Projects: `05_Archive/Projects/2026/2026-01_Website_Redesign/`
- Areas: `05_Archive/Areas/Old_Job_Career_Development/`

#### Archive Maintenance
- **Quarterly**: Move completed projects to Archive
- **Yearly**: Review Archive, delete truly unnecessary items
- **Every 2 Years**: Compress old archives to save space

#### Archive Access
- Keep Archive organized for easy retrieval
- Maintain index of archived projects
- Use search-friendly naming conventions

---

## Media Filing Rules

### Overview
Media files (videos, photos, magazines, music) require special handling due to volume and specific organizational needs.

**For complete media filing instructions, see:**
`G:\My Drive\04_Resources\Media\HOW_TO_FILE_MEDIA.md`

This separate guide covers:
- Video organization (movies, TV shows, documentaries, tutorials)
- Picture management (photos, screenshots, wallpapers)
- Audio filing (music, podcasts, audiobooks)
- Magazine and document organization
- Privacy considerations and folder structure

**Note:** The media filing guide is kept separate to maintain privacy of certain folder structures.

### Media Filing Details

All detailed media filing rules (videos, photos, magazines, music) have been moved to a separate guide for privacy and organization:

**See:** `G:\My Drive\04_Resources\Media\HOW_TO_FILE_MEDIA.md`

**Quick summary:**
- Videos: Organized by type (movies, TV shows, documentaries, tutorials)
- Photos: Organized by category with date-based structure
- Magazines: Organized by publication in collections
- Music: Organized by artist/album
- Audio: Podcasts, audiobooks organized by show/author

**Processing workflow:**
1. Download/receive media file
2. Identify media type
3. Follow specific rules in media filing guide
4. Move to appropriate location in `04_Resources/Media/`
5. Archive source files to `Downloads/Archives/Processed/`

---

## Input Locations - Where New Files Enter the System

### Overview
New files can enter the system through various locations. Understanding these locations helps in organizing and processing files efficiently.

### Complete Input Location Reference

**Quick Reference Table**:

| Source | Primary Location | Alternative Location | Processing |
|--------|-----------------|---------------------|------------|
| Web downloads | `C:\Users\sol90\Downloads` | N/A | Daily |
| Torrent downloads | `C:\Users\sol90\Downloads` | Custom torrent folder | Daily |
| Email attachments | `C:\Users\sol90\Downloads` | `G:\My Drive\01_Operate\Inbox\` | Daily |
| Mobile uploads | `G:\My Drive\01_Operate\Inbox\` | `G:\My Drive\` (root) | Daily |
| Google Drive web | `G:\My Drive\01_Operate\Inbox\` | Any folder | Daily |
| Screenshots | `C:\Users\sol90\Pictures\Screenshots\` | `G:\My Drive\01_Operate\Inbox\` | Daily |
| USB/External | Copy to Downloads | Copy to Inbox | As needed |
| Cloud sync | Service folder | Move to Downloads/Inbox | As needed |
| Bulk media | `G:\My Drive\01_Operate\Media_Staging\` | Inbox | Weekly |
| Bulk documents | `G:\My Drive\01_Operate\Documents_Staging\` | Inbox | Weekly |

### Input Location Decision Tree

**New file arrives → Where did it come from?**

1. **Downloaded from web/torrent** → `C:\Users\sol90\Downloads`
2. **Email attachment** → `Downloads` or `01_Operate/Inbox/`
3. **Created by me** → Save directly to appropriate PARA location
4. **Shared from others** → `01_Operate/Inbox/` for review
5. **Mobile upload** → `01_Operate/Inbox/`
6. **Bulk media import** → `01_Operate/Media_Staging/`
7. **Bulk documents** → `01_Operate/Documents_Staging/`
8. **Screenshot** → `01_Operate/Inbox/` or Screenshots folder
9. **External drive** → Copy to Downloads or Inbox
10. **Uncertain** → `01_Operate/Inbox/`

### Downloads Folder Subdirectories

**Location**: `C:\Users\sol90\Downloads`

The Downloads folder contains several subdirectories for organizing different types of files:

```
Downloads/
├── Archives/          # Multi-part archives and extracted content
├── Executables/       # Downloaded installers and programs
├── Scripts/           # Downloaded scripts and code files
├── Temp/              # Temporary extraction and processing
└── [Root files]       # New downloads appear here
```

**Subdirectory Rules**:
- **Archives/**: Store multi-part archives and processed source files
  - `Archives/Incomplete/` - Multi-part archives waiting for all parts
  - `Archives/Processed/` - Source archives after extraction (videos, photos, magazines)
- **Executables/**: Downloaded software installers (process to Tools or archive after install)
- **Scripts/**: Downloaded scripts (process to `04_Resources/Tools/Scripts/`)
- **Temp/**: Temporary extraction folder (clean weekly)
- **Root**: Process daily - move files to appropriate PARA locations

**Important**: These subdirectories should also be checked during daily processing, especially Archives for incomplete multi-part downloads.

#### Archive Retention Policy

**CRITICAL RULE**: **NEVER DELETE** source files from Downloads. Always move to archive.

**Archive Structure**:
```
Downloads/Archives/
├── Incomplete/        # Multi-part archives missing pieces
├── Processed/         # Successfully processed source files
│   ├── Videos/        # Source archives for extracted videos
│   ├── Photos/        # Source archives for extracted photos
│   └── Magazines/     # Source files for processed magazines
└── MISSING_PARTS_REMINDER.txt
```

**Processing Rules**:
1. After extracting videos → Move archive to `Archives/Processed/Videos/`
2. After extracting photos → Move archive to `Archives/Processed/Photos/`
3. After processing magazines → Move source to `Archives/Processed/Magazines/`
4. Incomplete multi-part archives → Move to `Archives/Incomplete/`
5. **NEVER** delete source files - always archive for potential re-processing

**Retention**:
- Keep all processed archives indefinitely (storage is cheap, re-downloading is hard)
- Periodically review `Archives/Incomplete/` for missing parts
- Archive folders can be moved to external backup if Downloads space needed

### Processing Priority Order

1. **Downloads folder root** (highest priority - fills up quickly, limited space)
2. **Downloads subdirectories** (check for incomplete archives, temp files)
3. **Operate/Inbox** (second priority - temporary holding)
4. **Screenshots folder** (third priority - accumulates quickly)
5. **Staging folders** (fourth priority - bulk processing)
6. **G Drive root** (weekly check for orphaned files)
7. **External/cloud sync** (as needed when connected to other cloud services)

---

## Naming Conventions

### General Principles
- Use underscores instead of spaces
- Use descriptive names
- Include dates when relevant (YYYY-MM-DD format)
- Avoid special characters: `& , - ( ) ' "`
- Keep names concise but clear

### File Naming Patterns

#### Documents
`YYYY-MM-DD_Document_Title_Author.ext`
- Example: `2026-01-11_Filing_Guide_Complete.md`

#### Projects
`YYYY-MM_Project_Name_Brief_Description`
- Example: `2026-01_Website_Redesign`

#### Media Files
- Videos: `Descriptive_Name_Quality.ext`
- Photos: `Model_Name_Set_Theme/` or `Code/`
- Magazines: `Magazine_Title_Issue_Date.pdf`

#### Scripts and Tools
`action_description.ext`
- Example: `standardize_filenames.ps1`

### Character Replacement Rules

| Original | Replace With | Example |
|----------|--------------|---------|
| Space ` ` | Underscore `_` | `Big Tits` → `Big_Tits` |
| Dash `-` (in names) | Underscore `_` | `Shay Laren - Set` → `Shay_Laren_Set` |
| Comma `,` | Remove or `_` | `A, B, C` → `A_B_C` |
| Ampersand `&` | Remove or `_` | `A & B` → `A_B` |
| Parentheses `()` | Remove | `Name (Info)` → `Name_Info` |
| Double underscore `__` | Single `_` | `A__B` → `A_B` |
| Periods `.` (except extension) | Underscore `_` | `Name.Set` → `Name_Set` |

---

## Processing Workflows

### Daily Processing Checklist (Non-Negotiable)
1. **Check Downloads folder root** - `C:\Users\sol90\Downloads` (main files)
2. **Check Downloads/Archives** - `C:\Users\sol90\Downloads\Archives` (incomplete multi-part archives)
3. **Check Downloads/Temp** - `C:\Users\sol90\Downloads\Temp` (clean up extractions)
4. **Check Operate/Inbox** - `G:\My Drive\01_Operate\Inbox\`
5. **Check Screenshots folder** - `C:\Users\sol90\Pictures\Screenshots\`
6. **Check G Drive root** - `G:\My Drive\` (for orphaned uploads)
7. **Check custom torrent folder** - If configured differently
8. **Check Media_Staging** - `G:\My Drive\01_Operate\Media_Staging\` (if exists)
9. **Check Documents_Staging** - `G:\My Drive\01_Operate\Documents_Staging\` (if exists)

#### Processing Priority Order
1. **Downloads folder root** (highest priority - fills up quickly, limited space)
2. **Downloads subdirectories** (Archives, Temp, Scripts, Executables)
3. **Operate/Inbox** (second priority - temporary holding)
4. **Screenshots folder** (third priority - accumulates quickly)
5. **Staging folders** (fourth priority - bulk processing)
6. **G Drive root** (weekly check for orphaned files)
7. **External/cloud sync** (as needed when connected to other cloud services)

### Weekly Review Workflow

#### Sunday Planning
1. Review `01_Operate/Inbox/` - file all items
2. Review `01_Operate/This_Week/` - archive completed items
3. Review `02_Projects/` - update project status
4. Plan upcoming week in `01_Operate/This_Week/`

#### Weekly Maintenance
1. Clear out `01_Operate/` of completed work
2. Archive finished projects to `05_Archive/`
3. Update area documentation in `03_Areas/`
4. Review and organize new resources in `04_Resources/`
5. **Clean Downloads subdirectories**:
   - Empty `Downloads/Temp/` folder
   - Review `Downloads/Archives/` for incomplete multi-part archives
   - Move scripts from `Downloads/Scripts/` to `04_Resources/Tools/Scripts/`
   - Process or delete installers in `Downloads/Executables/`

### Monthly Maintenance Workflow

#### First of Month
1. **Operate Cleanup**: Ensure only active work remains
2. **Project Review**: Archive completed projects
3. **Area Maintenance**: Update active documents, archive old materials
4. **Resource Organization**: Review new additions, remove duplicates

#### Media Maintenance
1. Run filename standardization scripts
2. Check for duplicate files
3. Verify folder organization
4. Update media catalogs

### Quarterly Review Workflow

#### Every 3 Months
1. **PARA Audit**: Review entire structure for misplaced items
2. **Archive Sweep**: Move stalled projects to Archive
3. **Resource Pruning**: Remove outdated or unused resources
4. **Template Updates**: Update templates and forms
5. **Script Maintenance**: Update automation scripts

---

## File Lineage Tracking System

### Overview
The lineage tracking system maintains a complete history of all file operations (renames, moves, modifications) with the ability to roll back changes. Each file's history is stored in JSON format for easy querying and restoration.

### Lineage Storage Structure

**Location**: `G:\My Drive\.lineage\`

```
.lineage/
├── by_category/
│   ├── media_video/
│   ├── media_pictures/
│   ├── media_magazines/
│   ├── documents/
│   └── projects/
├── by_date/
│   └── YYYY/
│       └── MM/
│           └── DD/
│               └── operations_YYYY-MM-DD.json
├── index.json
└── rollback_history.json
```

### Lineage File Format

Each file operation creates or updates a lineage record:

**Filename**: `[original_filename_hash].lineage.json`

**Structure**:
```json
{
  "file_id": "unique_hash_identifier",
  "current_location": "G:\\My Drive\\04_Resources\\Media\\Magazines\\Spicy\\Collections\\Hustler\\Hustler_Taboo_2025_11.pdf",
  "current_name": "Hustler_Taboo_2025_11.pdf",
  "original_name": "1018-Hustlr's_Tb_2025-11-12__.pdf",
  "original_location": "C:\\Users\\sol90\\Downloads\\1018-Hustlr's_Tb_2025-11-12__.pdf",
  "category": "media_magazines",
  "created_date": "2026-01-11T10:00:00Z",
  "last_modified": "2026-01-11T15:30:00Z",
  "operations": [
    {
      "operation_id": "op_20260111_100000_001",
      "timestamp": "2026-01-11T10:00:00Z",
      "type": "download",
      "details": {
        "source": "web_download",
        "location": "C:\\Users\\sol90\\Downloads\\1018-Hustlr's_Tb_2025-11-12__.pdf"
      }
    },
    {
      "operation_id": "op_20260111_143000_002",
      "timestamp": "2026-01-11T14:30:00Z",
      "type": "move",
      "details": {
        "from": "C:\\Users\\sol90\\Downloads\\1018-Hustlr's_Tb_2025-11-12__.pdf",
        "to": "G:\\My Drive\\04_Resources\\Media\\Magazines\\Spicy\\Collections\\Hustler\\1018-Hustlr's_Tb_2025-11-12__.pdf",
        "script": "process_downloads.ps1",
        "user": "automated"
      }
    },
    {
      "operation_id": "op_20260111_153000_003",
      "timestamp": "2026-01-11T15:30:00Z",
      "type": "rename",
      "details": {
        "old_name": "1018-Hustlr's_Tb_2025-11-12__.pdf",
        "new_name": "Hustler_Taboo_2025_11.pdf",
        "script": "standardize_filenames.ps1",
        "rules_applied": [
          "remove_numeric_prefix",
          "expand_abbreviations",
          "standardize_date_format",
          "clean_underscores"
        ],
        "reversible": true
      }
    }
  ],
  "metadata": {
    "file_size": 30928384,
    "file_hash_md5": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "file_type": "application/pdf",
    "tags": ["magazine", "hustler", "adult", "2025"],
    "collection": "Hustler"
  },
  "rollback_available": true,
  "rollback_points": [
    {
      "point_id": "rb_20260111_143000",
      "timestamp": "2026-01-11T14:30:00Z",
      "description": "Before standardization",
      "restore_to": {
        "name": "1018-Hustlr's_Tb_2025-11-12__.pdf",
        "location": "G:\\My Drive\\04_Resources\\Media\\Magazines\\Spicy\\Collections\\Hustler\\"
      }
    }
  ]
}
```

### Lineage Tracking Rules

#### When to Create Lineage Records
- **Always**: File downloads, moves, renames, deletions
- **Optional**: File edits, metadata changes
- **Never**: Temporary files, cache files

#### Lineage Categories
- `media_video` - Video files
- `media_pictures` - Photo files and folders
- `media_magazines` - Magazine PDFs
- `documents` - General documents
- `projects` - Project files
- `areas` - Area files
- `resources` - Resource files

#### Automatic Lineage Tracking
All automation scripts should:
1. Check if lineage exists for file
2. Create lineage if new file
3. Append operation to existing lineage
4. Update current location/name
5. Create rollback point before destructive operations

### Rollback System

#### Rollback Capabilities

**Full Rollback**: Restore file to any previous state
```powershell
Restore-FileLineage -FileId "unique_hash" -RollbackPoint "rb_20260111_143000"
```

**Batch Rollback**: Undo all operations from a specific script run
```powershell
Restore-BatchLineage -OperationId "op_20260111_153000_*" -Script "standardize_filenames.ps1"
```

**Time-based Rollback**: Restore all files to state at specific time
```powershell
Restore-TimelineLineage -Timestamp "2026-01-11T14:00:00Z"
```

#### Rollback Safety Rules
1. **Verify**: Check current file state matches lineage before rollback
2. **Backup**: Create backup before rollback operation
3. **Log**: Record all rollback operations in `rollback_history.json`
4. **Validate**: Verify file integrity after rollback
5. **Notify**: Alert user of any issues during rollback

### Lineage Maintenance

#### Daily
- Append new operations to lineage files
- Update index with new files

#### Weekly
- Consolidate daily operation logs
- Verify lineage integrity
- Clean up orphaned lineage records

#### Monthly
- Archive old lineage records (>6 months)
- Compress lineage data
- Generate lineage reports

#### Yearly
- Full lineage audit
- Remove lineage for deleted files
- Optimize lineage storage

### Lineage Query Examples

**Find all renames for a file**:
```powershell
Get-FileLineage -FileName "Hustler_Taboo_2025_11.pdf" | Where-Object { $_.operations.type -eq "rename" }
```

**Find all files moved on specific date**:
```powershell
Get-LineageByDate -Date "2026-01-11" | Where-Object { $_.operations.type -eq "move" }
```

**Find all operations by script**:
```powershell
Get-LineageByScript -ScriptName "standardize_filenames.ps1"
```

**Find files in specific category**:
```powershell
Get-LineageByCategory -Category "media_magazines"
```

### Lineage Integration with Scripts

All file operation scripts should include lineage tracking:

```powershell
# Example: Rename with lineage tracking
function Rename-WithLineage {
    param(
        [string]$FilePath,
        [string]$NewName,
        [string]$ScriptName
    )
    
    # Get or create lineage
    $lineage = Get-FileLineage -FilePath $FilePath
    if (-not $lineage) {
        $lineage = New-FileLineage -FilePath $FilePath
    }
    
    # Create rollback point
    $rollbackPoint = New-RollbackPoint -Lineage $lineage
    
    # Perform rename
    $oldName = Split-Path $FilePath -Leaf
    Rename-Item -Path $FilePath -NewName $NewName
    
    # Update lineage
    Add-LineageOperation -Lineage $lineage -Type "rename" -Details @{
        old_name = $oldName
        new_name = $NewName
        script = $ScriptName
        rollback_point = $rollbackPoint
    }
    
    # Save lineage
    Save-FileLineage -Lineage $lineage
}
```

### Lineage Backup

**Location**: `G:\My Drive\.lineage_backup\`

**Schedule**:
- **Daily**: Incremental backup of changed lineage files
- **Weekly**: Full backup of all lineage data
- **Monthly**: Compressed archive of lineage backups

**Retention**:
- Daily backups: 30 days
- Weekly backups: 6 months
- Monthly backups: 2 years

---

## Automation Scripts

### Location
Scripts stored in: `G:\My Drive\` (root) and `04_Resources/Tools/Scripts/`

### Lineage Tracking Scripts

#### lineage_manager.ps1
**Location**: `G:\My Drive\.lineage\scripts\lineage_manager.ps1`

**Functions**:
- `New-FileLineage`: Create new lineage record
- `Get-FileLineage`: Retrieve lineage for file
- `Add-LineageOperation`: Append operation to lineage
- `Save-FileLineage`: Save lineage to disk
- `New-RollbackPoint`: Create rollback checkpoint
- `Restore-FileLineage`: Rollback file to previous state
- `Get-LineageByCategory`: Query lineage by category
- `Get-LineageByDate`: Query lineage by date
- `Export-LineageReport`: Generate lineage report

**Usage**:
```powershell
# Import lineage manager
. "G:\My Drive\.lineage\scripts\lineage_manager.ps1"

# Create lineage for new file
$lineage = New-FileLineage -FilePath "C:\Users\sol90\Downloads\file.pdf" -Category "media_magazines"

# Add operation
Add-LineageOperation -Lineage $lineage -Type "download" -Details @{ source = "web" }

# Save lineage
Save-FileLineage -Lineage $lineage
```

### Key Scripts

#### Media Processing
- **standardize_filenames.ps1**: Standardize magazine filenames
  - Location: `G:\My Drive\04_Resources\Media\Magazines\Spicy\`
  - Purpose: Clean and standardize PDF filenames
  - Usage: Run monthly or after adding new magazines

#### Download Processing
- **process_downloads.ps1**: Process new downloads
  - Extracts archives
  - Moves videos to Video Spicy
  - Moves PDFs to Magazine collections
  - Moves photo folders to Pictures Spicy
  - Cleans up Downloads folder

#### Organization
- **cleanup_and_organize_media.ps1**: Organize media files
- **deep-organize.ps1**: Deep organization of files
- **rename_to_convention.ps1**: Rename files to convention

### Script Usage Guidelines
1. Review script before running
2. Test on small batch first
3. Check logs after execution
4. Verify results before cleanup
5. Document any issues

---

## Quick Reference

### Filing Decision Tree

**New Item Arrives** →
1. Is it for immediate use? → `01_Operate/Inbox/`
2. Is it part of an active project? → `02_Projects/[Project_Name]/`
3. Is it an ongoing responsibility? → `03_Areas/[Area_Name]/`
4. Is it reference material? → `04_Resources/[Category]/`
5. Is it completed/historical? → `05_Archive/`

### Common Filing Locations

| Content Type | Destination |
|--------------|-------------|
| Videos (Adult) | `04_Resources/Media/Video/Spicy/` |
| Photos (Adult) | `04_Resources/Media/Pictures/Spicy/` |
| Magazines (Adult) | `04_Resources/Media/Magazines/Spicy/Collections/[Magazine]/` |
| Active Project Files | `02_Projects/[Project_Name]/` |
| Reference Documents | `04_Resources/Documents/[Category]/` |
| Templates | `04_Resources/Templates/` or `03_Areas/[Area]/Templates/` |
| Scripts | `04_Resources/Tools/Scripts/` |
| Completed Projects | `05_Archive/Projects/YYYY/[Project]/` |

### Archive Password
**Default**: `koth` (for all adult content archives)

### Critical Safety Rules
1. **NEVER** delete archives without verifying extraction
2. **ALWAYS** check extracted folder has content before deleting archive
3. **VERIFY** videos are in Spicy drive before deleting source
4. **PRESERVE** incomplete downloads (*.crdownload)
5. **BACKUP** before bulk deletions

---

## Maintenance Schedule

### Daily
- [ ] Process Downloads folder
- [ ] File items from Operate/Inbox
- [ ] Update Today folder

### Weekly
- [ ] Clear Operate/This_Week
- [ ] Review active projects
- [ ] Archive completed items
- [ ] Plan upcoming week

### Monthly
- [ ] Clean Operate folder
- [ ] Archive finished projects
- [ ] Update area documentation
- [ ] Organize new resources
- [ ] Run media standardization scripts

### Quarterly
- [ ] Full PARA audit
- [ ] Archive stalled projects
- [ ] Prune unused resources
- [ ] Update templates
- [ ] Review and update scripts

### Yearly
- [ ] Comprehensive system review
- [ ] Archive old materials
- [ ] Update filing guide
- [ ] Optimize folder structure
- [ ] Backup entire system

---

---

## Best Practices

### General Filing Best Practices

#### 1. File Immediately, Don't Pile
- Process new items within 24 hours
- Use `01_Operate/Inbox/` as temporary holding only
- Don't let items accumulate in Downloads
- Make filing decisions quickly and confidently

#### 2. Use Descriptive Names
- Future-you should understand the filename
- Include context: dates, sources, topics
- Avoid generic names like "Document1.pdf"
- Be specific but concise

#### 3. Maintain Consistent Structure
- Follow established folder hierarchies
- Don't create ad-hoc subfolders
- Use templates for recurring structures
- Document any structural changes

#### 4. Regular Reviews Prevent Chaos
- Daily: Process inbox
- Weekly: Review active work
- Monthly: Archive completed items
- Quarterly: Full system audit

#### 5. When in Doubt, Use Operate/Inbox
- Better to file temporarily than incorrectly
- Review inbox regularly to make proper decisions
- Don't stress over perfect categorization
- You can always move files later (with lineage tracking)

### PARA-Specific Best Practices

#### Projects
- **Start with a brief**: Always create `00_Project_Brief.md`
- **Set clear goals**: Define what "done" looks like
- **Review weekly**: Update status and next actions
- **Archive promptly**: Move completed projects within 1 week
- **Learn from past**: Review archived projects before starting similar ones

#### Areas
- **Define standards**: What does "good" look like for this area?
- **Create templates**: Standardize recurring documents
- **Schedule reviews**: Set calendar reminders for maintenance
- **Archive old materials**: Keep Active folder current
- **Document processes**: Write down your workflows

#### Resources
- **Tag for discovery**: Use descriptive folder names
- **Remove duplicates**: Run deduplication monthly
- **Verify quality**: Delete low-quality resources
- **Organize by use**: Most-used items should be easiest to find
- **Index large collections**: Create README files for navigation

#### Archive
- **Compress old files**: Save space on large archives
- **Maintain searchability**: Keep good naming conventions
- **Don't over-archive**: Delete truly unnecessary items
- **Document lessons**: Add project retrospectives before archiving
- **Review yearly**: Purge truly obsolete materials

### Media-Specific Best Practices

#### Video Management
- **Verify before deleting**: Always check video plays before deleting source
- **Keep quality indicators**: Preserve resolution info in filenames
- **Flat structure works**: Don't over-organize with subfolders
- **Log everything**: Use `_unpack_log.txt` for tracking
- **Backup critical content**: Not everything needs to be backed up, but favorites should be

#### Photo Management
- **Preserve folder structure**: Photo sets belong together
- **Keep original names**: When descriptive, maintain original folder names
- **Verify extraction**: Check folder has images before deleting archive
- **Remove empty folders**: Clean up after moving content
- **Consider storage**: Large photo collections need space planning

#### Magazine Management
- **Collection-based organization**: Group by magazine title, not date
- **Standardize filenames**: Run standardization script monthly
- **Track lineage**: Enable rollback for mass renames
- **Identify unknowns**: Use OCR for poorly named files
- **Remove duplicates**: Check for duplicate issues by hash

### Automation Best Practices

#### Script Usage
- **Test first**: Run on small batch before full execution
- **Review logs**: Check output after every script run
- **Enable lineage**: Track all automated operations
- **Backup before bulk**: Create restore point for large operations
- **Document changes**: Note what scripts do in comments

#### Safety Protocols
- **Never auto-delete**: Always verify before deletion
- **Preserve originals**: Keep source files until verified
- **Use rollback points**: Create checkpoints before destructive operations
- **Log everything**: Maintain operation logs
- **Test rollback**: Verify rollback works before relying on it

### Workflow Optimization

#### Speed Up Common Tasks
- **Keyboard shortcuts**: Learn file manager shortcuts
- **Quick access folders**: Pin frequently used locations
- **Batch processing**: Group similar tasks together
- **Template usage**: Create templates for recurring structures
- **Script automation**: Automate repetitive tasks

#### Reduce Decision Fatigue
- **Follow the guide**: Trust your documented processes
- **Use decision trees**: Refer to filing decision tree
- **Set defaults**: Establish default locations for common types
- **Time-box decisions**: Don't spend >1 minute deciding where to file
- **Review and refine**: Improve processes based on experience

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Downloads Folder Always Full

**Symptoms**:
- Downloads folder has 50+ items
- Can't find recent downloads
- Mix of old and new files

**Solutions**:
1. **Immediate**: Run full processing workflow
   ```powershell
   # Process all content
   & "G:\My Drive\process_downloads.ps1"
   ```
2. **Short-term**: Set daily reminder to process downloads
3. **Long-term**: Enable automated processing script on schedule

**Prevention**:
- Process downloads daily
- Don't use Downloads as storage
- Set up automated cleanup script

---

#### Issue: Can't Find Files After Filing

**Symptoms**:
- Know you filed something but can't locate it
- Searching multiple folders
- Unsure which PARA category was used

**Solutions**:
1. **Check lineage system**:
   ```powershell
   # Search by filename
   Get-FileLineage -FileName "document.pdf"
   ```
2. **Use Windows Search**: Search across entire G Drive
3. **Check common locations**: Operate/Inbox, Recent files
4. **Review filing log**: Check operation logs by date

**Prevention**:
- Use consistent naming conventions
- Enable lineage tracking for all operations
- Create index files for large collections
- Use descriptive folder names

---

#### Issue: Duplicate Files Everywhere

**Symptoms**:
- Same file in multiple locations
- Multiple versions with slight name differences
- Wasting storage space

**Solutions**:
1. **Find duplicates by hash**:
   ```powershell
   # Find duplicate files
   Get-ChildItem -Recurse | Get-FileHash | Group-Object Hash | Where-Object { $_.Count -gt 1 }
   ```
2. **Use lineage to identify original**: Check which file was created first
3. **Delete duplicates**: Keep one copy, delete others
4. **Update references**: If files are linked elsewhere, update links

**Prevention**:
- Run monthly duplicate check
- Use lineage tracking to prevent duplicate moves
- Establish single source of truth for each file
- Don't copy, move files instead

---

#### Issue: Archive Extraction Fails

**Symptoms**:
- 7-Zip reports errors
- Partial extraction
- Corrupted files

**Solutions**:
1. **Verify password**: Ensure using correct password (`koth`)
2. **Check archive integrity**:
   ```powershell
   & "C:\Program Files\7-Zip\7z.exe" t "archive.rar" -pkoth
   ```
3. **Download again**: If corrupted, re-download
4. **Try different tool**: Use WinRAR or other extraction tool
5. **Check for multi-part**: Ensure all parts present

**Prevention**:
- Verify downloads complete (check .crdownload files)
- Test archives before deleting source
- Keep archive until extraction verified
- Log extraction errors for pattern detection

---

#### Issue: Lineage Tracking Not Working

**Symptoms**:
- No lineage files created
- Rollback fails
- Missing operation history

**Solutions**:
1. **Initialize lineage system**:
   ```powershell
   . "G:\My Drive\.lineage\scripts\lineage_manager.ps1"
   Initialize-LineageSystem
   ```
2. **Check permissions**: Ensure write access to `.lineage` folder
3. **Verify script integration**: Ensure scripts call lineage functions
4. **Manually create lineage**: For existing files, create retroactive lineage

**Prevention**:
- Test lineage system after setup
- Include lineage calls in all file operation scripts
- Monitor lineage folder for new files
- Run lineage integrity check weekly

---

#### Issue: Projects Never Get Archived

**Symptoms**:
- 02_Projects folder has 20+ projects
- Many projects are actually complete
- Can't find active projects among old ones

**Solutions**:
1. **Review all projects**: Go through each, mark status
2. **Archive completed**: Move done projects to Archive immediately
3. **Archive stalled**: Move inactive projects (>3 months no activity)
4. **Update remaining**: Ensure active projects have recent activity

**Prevention**:
- Set project completion criteria upfront
- Review projects weekly
- Archive within 1 week of completion
- Quarterly audit to catch stalled projects

---

#### Issue: Operate Folder Becomes Storage

**Symptoms**:
- Operate has files from weeks/months ago
- Inbox has 100+ items
- Can't find today's work

**Solutions**:
1. **Emergency cleanup**: Batch move old items to appropriate locations
2. **Sort by date**: Process oldest items first
3. **Quick decisions**: Use decision tree, don't overthink
4. **Set deadline**: Process all items within 2 hours

**Prevention**:
- Daily inbox processing (non-negotiable)
- Weekly Operate cleanup
- Monthly audit to catch buildup
- Set file count limits (e.g., max 20 items in Inbox)

---

#### Issue: Naming Conventions Inconsistent

**Symptoms**:
- Files named different ways
- Hard to sort or search
- Unclear what files contain

**Solutions**:
1. **Batch rename**: Use standardization scripts
2. **Create naming templates**: Document patterns for each type
3. **Rename as you go**: Fix names when you encounter them
4. **Use lineage**: Track renames for rollback if needed

**Prevention**:
- Follow naming conventions strictly
- Use templates for new files
- Run standardization scripts monthly
- Review naming guide before filing

---

## FAQ

### General Questions

**Q: What's the difference between Projects and Areas?**

A: Projects have a defined end goal and completion date. Areas are ongoing responsibilities without end dates. Example: "Learn Python" is a project (you'll eventually finish the course). "Professional Development" is an area (ongoing career growth).

---

**Q: Where do I put files I'm actively working on?**

A: Use `01_Operate/Processing/` for work-in-progress. If it's part of a project, you can also work directly in the project folder. Move to final location when complete.

---

**Q: Can I create subfolders in PARA categories?**

A: Yes! The PARA structure is the top level. Within each category, create whatever subfolders make sense. Just maintain consistency and document your structure.

---

**Q: How do I handle files that fit multiple categories?**

A: Choose the primary purpose:
- If actively working on it → Operate or Projects
- If ongoing responsibility → Areas
- If reference material → Resources
- If completed → Archive

Create shortcuts/links if needed in other locations.

---

**Q: Should I backup my G Drive?**

A: Yes! Google Drive has built-in redundancy, but consider:
- Local backup of critical files
- Export important data periodically
- Backup lineage system separately
- Test restore procedures

---

### Media Questions

**Q: Why flat structure for videos?**

A: Flat structure (no subfolders) makes it easier to:
- Browse all content quickly
- Avoid deep folder hierarchies
- Use search/filter instead of navigation
- Prevent duplicate categorization issues

---

**Q: What if I don't know the magazine name?**

A: Use OCR to identify:
1. Run OCR on first page
2. Extract magazine title from text
3. Create collection folder
4. Move PDF to collection

If still unknown, use `Other_Magazines` temporarily.

---

**Q: Can I delete archives immediately after extraction?**

A: NO! Always verify first:
1. Check extracted folder has content
2. Verify files open correctly
3. Confirm file count matches expected
4. Only then delete archive

---

**Q: What's the password for archives?**

A: Default password is `koth` for all adult content archives. If extraction fails, verify:
- Correct password spelling
- Archive isn't corrupted
- All parts present (for multi-part)

---

**Q: How do I handle multi-part archives?**

A: Extract only the `.part1` file:
```powershell
& "C:\Program Files\7-Zip\7z.exe" x "archive.part1.rar" -o"Destination" -pkoth -y
```
7-Zip automatically uses all parts. Keep all parts until extraction verified.

---

### Lineage Questions

**Q: What is file lineage tracking?**

A: A system that records every operation on a file (download, move, rename, delete) with the ability to rollback changes. Think of it as "undo" for file operations.

---

**Q: Do I need lineage for every file?**

A: Enable for:
- Media files (videos, photos, magazines)
- Important documents
- Project files
- Anything you might rename or reorganize

Skip for:
- Temporary files
- Cache files
- Truly disposable content

---

**Q: How do I rollback a file rename?**

A:
```powershell
# Find the file's lineage
$lineage = Get-FileLineage -FileName "current_name.pdf"

# View rollback points
$lineage.rollback_points

# Restore to specific point
Restore-FileLineage -FileId $lineage.file_id -RollbackPointId "rb_20260111_143000"
```

---

**Q: Can I undo an entire script run?**

A: Yes! Batch rollback:
```powershell
Restore-BatchLineage -Script "standardize_filenames.ps1" -Timestamp "2026-01-11T14:00:00Z"
```
This reverts all operations from that script run.

---

**Q: Where is lineage data stored?**

A: `G:\My Drive\.lineage\` folder:
- `by_category/` - Lineage files organized by type
- `index.json` - Fast lookup index
- `rollback_history.json` - Log of all rollbacks

---

### Workflow Questions

**Q: How often should I process Downloads?**

A: Daily minimum. Ideally:
- After each download session
- End of workday
- Before shutting down computer

Goal: Downloads folder should be empty or near-empty.

---

**Q: What's the fastest way to file something?**

A: Use the decision tree:
1. Is it for today? → `01_Operate/Today/`
2. Is it a project? → `02_Projects/[Project]/`
3. Is it ongoing? → `03_Areas/[Area]/`
4. Is it reference? → `04_Resources/[Category]/`
5. Is it done? → `05_Archive/`

Don't overthink it. You can always move it later.

---

**Q: How do I handle email attachments?**

A:
1. Download to Downloads folder
2. Process like any other file
3. File to appropriate PARA location
4. Delete from Downloads
5. Optional: Keep email for context

---

**Q: Should I organize by date or by topic?**

A: **By topic** (PARA category), then by date within categories if needed. PARA is topic-based organization. Dates are useful for:
- Project naming (YYYY-MM prefix)
- Archive organization (by year)
- Document naming (YYYY-MM-DD prefix)

---

**Q: How do I prevent the system from becoming messy again?**

A: Discipline and routine:
- **Daily**: Process inbox (15 min)
- **Weekly**: Review and cleanup (30 min)
- **Monthly**: Archive and organize (1 hour)
- **Quarterly**: Full audit (2-3 hours)

Consistency beats perfection. Better to file imperfectly daily than perfectly monthly.

---

**Last Updated**: January 11, 2026
**Version**: 3.1
**Maintained By**: Personal Knowledge Management System
- Test restore procedures

---

### Media Questions

**Q: Why flat structure for videos?**

A: Flat structure (no subfolders) makes it easier to:
- Browse all content quickly
- Avoid deep folder hierarchies
- Use search/filter instead of navigation
- Prevent duplicate categorization issues

---

**Q: What if I don't know the magazine name?**

A: Use OCR to identify:
1. Run OCR on first page
2. Extract magazine title from text
3. Create collection folder
4. Move PDF to collection

If still unknown, use `Other_Magazines` temporarily.

---

**Q: Can I delete archives immediately after extraction?**

A: NO! Always verify first:
1. Check extracted folder has content
2. Verify files open correctly
3. Confirm file count matches expected
4. Only then delete archive

---

**Q: What's the password for archives?**

A: Default password is `koth` for all adult content archives. If extraction fails, verify:
- Correct password spelling
- Archive isn't corrupted
- All parts present (for multi-part)

---

**Q: How do I handle multi-part archives?**

A: Extract only the `.part1` file:
```powershell
& "C:\Program Files\7-Zip\7z.exe" x "archive.part1.rar" -o"Destination" -pkoth -y
```
7-Zip automatically uses all parts. Keep all parts until extraction verified.

---

### Lineage Questions

**Q: What is file lineage tracking?**

A: A system that records every operation on a file (download, move, rename, delete) with the ability to rollback changes. Think of it as "undo" for file operations.

---

**Q: Do I need lineage for every file?**

A: Enable for:
- Media files (videos, photos, magazines)
- Important documents
- Project files
- Anything you might rename or reorganize

Skip for:
- Temporary files
- Cache files
- Truly disposable content

---

**Q: How do I rollback a file rename?**

A:
```powershell
# Find the file's lineage
$lineage = Get-FileLineage -FileName "current_name.pdf"

# View rollback points
$lineage.rollback_points

# Restore to specific point
Restore-FileLineage -FileId $lineage.file_id -RollbackPointId "rb_20260111_143000"
```

---

**Q: Can I undo an entire script run?**

A: Yes! Batch rollback:
```powershell
Restore-BatchLineage -Script "standardize_filenames.ps1" -Timestamp "2026-01-11T14:00:00Z"
```
This reverts all operations from that script run.

---

**Q: Where is lineage data stored?**

A: `G:\My Drive\.lineage\` folder:
- `by_category/` - Lineage files organized by type
- `index.json` - Fast lookup index
- `rollback_history.json` - Log of all rollbacks

---

### Workflow Questions

**Q: How often should I process Downloads?**

A: Daily minimum. Ideally:
- After each download session
- End of workday
- Before shutting down computer

Goal: Downloads folder should be empty or near-empty.

---

**Q: What's the fastest way to file something?**

A: Use the decision tree:
1. Is it for today? → `01_Operate/Today/`
2. Is it a project? → `02_Projects/[Project]/`
3. Is it ongoing? → `03_Areas/[Area]/`
4. Is it reference? → `04_Resources/[Category]/`
5. Is it done? → `05_Archive/`

Don't overthink it. You can always move it later.

---

**Q: How do I handle email attachments?**

A:
1. Download to Downloads folder
2. Process like any other file
3. File to appropriate PARA location
4. Delete from Downloads
5. Optional: Keep email for context

---

**Q: Should I organize by date or by topic?**

A: **By topic** (PARA category), then by date within categories if needed. PARA is topic-based organization. Dates are useful for:
- Project naming (YYYY-MM prefix)
- Archive organization (by year)
- Document naming (YYYY-MM-DD prefix)

---

**Q: How do I prevent the system from becoming messy again?**

A: Discipline and routine:
- **Daily**: Process inbox (15 min)
- **Weekly**: Review and cleanup (30 min)
- **Monthly**: Archive and organize (1 hour)
- **Quarterly**: Full audit (2-3 hours)

Consistency beats perfection. Better to file imperfectly daily than perfectly monthly.

---

**Last Updated**: January 11, 2026
**Version**: 3.1
**Maintained By**: Personal Knowledge Management System
