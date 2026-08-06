# Environment Variables & Credentials Management - Master Guide

## Overview

**Purpose**: Complete guide for managing environment variables, credentials, API keys, and secrets across all projects and automation scripts.

**Last Updated**: February 22, 2026
**Version**: 1.1.0

**Security Level**: CRITICAL - Contains sensitive information handling procedures

## Quick Reference
**Use when:** Setting up API keys, finding where credentials are stored, configuring a new integration, script fails with auth error
**Don't use when:** Looking for HRSA/EHBS environment credentials — use pskills `09_environments/skill_keys_management.md`
**Trigger phrases:** "where are credentials", "set up API key", "find my token", "authentication setup", "environments.json"
**Time:** 5-10 minutes for initial setup; instant for lookup
**Lookup order:** KeePass (`keys pass.kdbx`) → `environments.json` → `.env`

---

## Table of Contents

1. [Security Principles](#security-principles)
2. [Credentials Storage Structure](#credentials-storage-structure)
3. [Environment Variables (.env)](#environment-variables-env)
4. [Python Integration](#python-integration)
5. [PowerShell Integration](#powershell-integration)
6. [Adding New Credentials](#adding-new-credentials)
7. [Current Credentials Inventory](#current-credentials-inventory)
8. [Best Practices](#best-practices)
9. [Security Checklist](#security-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Security Principles

### Core Rules (NEVER VIOLATE)

1. **NEVER** commit credentials to version control (Git, SVN, etc.)
2. **NEVER** hardcode credentials in scripts or code
3. **NEVER** share credentials in plain text (email, chat, etc.)
4. **NEVER** store credentials in cloud sync folders without encryption
5. **ALWAYS** use environment variables or secure credential stores
6. **ALWAYS** keep `.env` files in `.gitignore`
7. **ALWAYS** rotate credentials regularly (quarterly minimum)
8. **ALWAYS** use least-privilege access (minimum permissions needed)

### Security Layers

```
Layer 1: Physical Security
├── G Drive encrypted at rest
└── Local machine password protected

Layer 2: File Security
├── .env file permissions (read-only for user)
├── Keys folder not in version control
└── Backup encrypted separately

Layer 3: Application Security
├── Environment variables loaded at runtime
├── Credentials never logged or printed
└── Secure credential helpers only
```

---

## Credentials Storage Structure

### 🔐 PRIMARY CREDENTIAL SOURCES - CHECK THESE FIRST

**Before creating new credentials, ALWAYS check these locations:**

#### 1. KeePass Database (Passwords & Secrets)
- **Location:** `${PARA_ROOT}/03_Areas/Keys/keys pass.kdbx`
- **Contains:** Passwords, API keys, secrets, secure notes
- **Access:** KeePass application with master password
- **Use for:** All passwords, sensitive API keys, personal credentials

#### 2. Environments JSON (API Configurations)
- **Location:** `${PARA_ROOT}/03_Areas/Keys/Environments/environments.json`
- **Contains:** API endpoints, OAuth configs, service credentials
- **Access:** Direct file access (encrypted on Google Drive)
- **Use for:** Development environments, API integrations, automation
- **Current services:** Salesforce, GEMS, Azure DevOps, Todoist, Amplenote, Gmail

#### 3. Environment Variables (.env)
- **Location:** `${PARA_ROOT}/03_Areas/Keys/.env`
- **Contains:** Legacy environment variables
- **Use for:** Backward compatibility with older scripts

**Note on Path Variables:**

- **`${PARA_ROOT}`**: Your main PARA organizational folder (typically `G:\My Drive` on Windows)
  - Configured in `${SKILLS_ROOT}/skills_config.json`
  - Points to your PARA method structure:
    - `01_Operate/Projects/` - Active work with deadlines
    - `03_Areas/` - Ongoing responsibilities (credentials stored here)
    - `04_Resources/` - Reference materials
    - `05_Archive/` - Completed items
    - `06_Skills/` - AI assistant skills and workflows
  - Example: `${PARA_ROOT}\03_Areas\Keys\` resolves to `G:\My Drive\03_Areas\Keys\`

- **`${SKILLS_ROOT}`**: Location of your skills repository
  - Configured in `skills_config.json`
  - Contains all AI assistant skills organized by category

### Credential Lookup Workflow

```
Need a credential?
    ↓
1. Check KeePass database first (keys pass.kdbx)
    ↓
2. If not in KeePass, check environments.json
    ↓
3. If not in either, check .env file
    ↓
4. If not found anywhere, then create new credential
    ↓
5. Store in appropriate location:
   - Passwords/secrets → KeePass
   - API configs → environments.json
   - Legacy vars → .env
```

### Primary Location

**Path**: `${PARA_ROOT}/03_Areas/Keys/`

```
03_Areas/Keys/
├── keys pass.kdbx          # KeePass database (PRIMARY for passwords)
├── Environments/
│   └── environments.json   # API configurations (PRIMARY for APIs)
├── .env                    # Environment variables (LEGACY)
├── load_credentials.py     # Python credential loader
├── load_credentials.ps1    # PowerShell credential loader
├── README.md              # Usage documentation
└── .gitignore             # Ensures .env is never committed
```

### Backup Location

**Path**: `${PARA_ROOT}/05_Archive/Credentials_Backup/`

- Monthly encrypted backups
- Stored separately from active credentials
- Encrypted with strong password

---

## Environment Variables (.env)

### File Format

**Location**: `${PARA_ROOT}/03_Areas/Keys/.env`

```bash
# ===================================
# HEALTH INSURANCE - CIGNA
# ===================================
CIGNA_USERNAME=your_username_here
CIGNA_PASSWORD=your_password_here
CIGNA_CLAIMS_URL=https://my.cigna.com/claims

# ===================================
# AZURE DEVOPS
# ===================================
ADO_ORG_URL=https://ehbads.hrsa.gov/ads/EHBs/EHBs/
ADO_PROJECT=EHBs
ADO_PAT=your_personal_access_token_here
ADO_USERNAME=your_ado_username

# ===================================
# GOOGLE SERVICES
# ===================================
GOOGLE_CREDENTIALS_PATH=${PARA_ROOT}\credentials.json
GOOGLE_TOKEN_PATH=${PARA_ROOT}\token.json
GMAIL_API_SCOPES=https://www.googleapis.com/auth/gmail.modify

# ===================================
# TORRENT SERVICES
# ===================================
TORRENT_DOWNLOAD_PATH=C:\Users\sol90\Downloads
TORRENT_TRACKER_URL=your_tracker_url
TORRENT_USERNAME=your_username
TORRENT_PASSKEY=your_passkey

# ===================================
# API KEYS
# ===================================
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ===================================
# DATABASE CREDENTIALS
# ===================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password

# ===================================
# CLOUD STORAGE
# ===================================
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

# ===================================
# OTHER SERVICES
# ===================================
SERVICE_NAME_API_KEY=your_key_here
SERVICE_NAME_SECRET=your_secret_here
```

### Naming Conventions

**Pattern**: `SERVICE_CREDENTIAL_TYPE`

Examples:
- `CIGNA_USERNAME` (service_credential_type)
- `ADO_PAT` (service_credential_type)
- `GMAIL_API_SCOPES` (service_credential_type)

**Rules**:
- Use UPPERCASE for all variable names
- Use underscores to separate words
- Start with service/platform name
- End with credential type (USERNAME, PASSWORD, API_KEY, etc.)
- Group related credentials with comments

---

## Python Integration

### Setup

**File**: `${PARA_ROOT}\03_Areas\Keys\load_credentials.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Path to .env file
ENV_PATH = Path(__file__).parent / '.env'

def load_env():
    """Load environment variables from .env file"""
    if not ENV_PATH.exists():
        raise FileNotFoundError(f".env file not found at {ENV_PATH}")
    load_dotenv(ENV_PATH)
    print(f"✓ Loaded credentials from {ENV_PATH}")

def get_credential(key, required=True):
    """Get a credential from environment variables"""
    value = os.getenv(key)
    if required and not value:
        raise ValueError(f"Required credential '{key}' not found in .env")
    return value

def get_cigna_credentials():
    """Get all Cigna health insurance credentials"""
    return {
        'username': get_credential('CIGNA_USERNAME'),
        'password': get_credential('CIGNA_PASSWORD'),
        'claims_url': get_credential('CIGNA_CLAIMS_URL')
    }

def get_ado_credentials():
    """Get all Azure DevOps credentials"""
    return {
        'org_url': get_credential('ADO_ORG_URL'),
        'project': get_credential('ADO_PROJECT'),
        'pat': get_credential('ADO_PAT'),
        'username': get_credential('ADO_USERNAME')
    }

def get_google_credentials():
    """Get Google API credentials paths"""
    return {
        'credentials_path': get_credential('GOOGLE_CREDENTIALS_PATH'),
        'token_path': get_credential('GOOGLE_TOKEN_PATH'),
        'scopes': get_credential('GMAIL_API_SCOPES')
    }

def get_torrent_credentials():
    """Get torrent service credentials"""
    return {
        'download_path': get_credential('TORRENT_DOWNLOAD_PATH'),
        'tracker_url': get_credential('TORRENT_TRACKER_URL'),
        'username': get_credential('TORRENT_USERNAME'),
        'passkey': get_credential('TORRENT_PASSKEY')
    }

def get_database_credentials():
    """Get database connection credentials"""
    return {
        'host': get_credential('DB_HOST'),
        'port': int(get_credential('DB_PORT')),
        'database': get_credential('DB_NAME'),
        'username': get_credential('DB_USERNAME'),
        'password': get_credential('DB_PASSWORD')
    }

def get_aws_credentials():
    """Get AWS credentials"""
    return {
        'access_key_id': get_credential('AWS_ACCESS_KEY_ID'),
        'secret_access_key': get_credential('AWS_SECRET_ACCESS_KEY'),
        'region': get_credential('AWS_REGION')
    }
```

### Usage in Scripts

```python
from pathlib import Path
import sys

# Add keys folder to path
keys_path = Path(r"${PARA_ROOT}\03_Areas\Keys")
sys.path.insert(0, str(keys_path))

from load_credentials import load_env, get_credential, get_cigna_credentials

# Load all credentials
load_env()

# Method 1: Get individual credentials
cigna_user = get_credential('CIGNA_USERNAME')
cigna_pass = get_credential('CIGNA_PASSWORD')

# Method 2: Get all service credentials at once
cigna = get_cigna_credentials()
print(f"Logging in as: {cigna['username']}")

# Method 3: Get optional credential (won't raise error if missing)
optional_key = get_credential('OPTIONAL_KEY', required=False)
```

---

## PowerShell Integration

### Setup

**File**: `${PARA_ROOT}\03_Areas\Keys\load_credentials.ps1`

```powershell
# Load environment variables from .env file
function Load-Env {
    param(
        [string]$EnvPath = "$PSScriptRoot\.env"
    )
    
    if (-not (Test-Path $EnvPath)) {
        throw ".env file not found at $EnvPath"
    }
    
    Get-Content $EnvPath | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    
    Write-Host "✓ Loaded credentials from $EnvPath" -ForegroundColor Green
}

# Get a credential from environment variables
function Get-Credential-Value {
    param(
        [string]$Key,
        [bool]$Required = $true
    )
    
    $value = [Environment]::GetEnvironmentVariable($Key, "Process")
    
    if ($Required -and [string]::IsNullOrEmpty($value)) {
        throw "Required credential '$Key' not found in environment"
    }
    
    return $value
}

# Get Cigna credentials
function Get-CignaCredentials {
    return @{
        Username = Get-Credential-Value -Key "CIGNA_USERNAME"
        Password = Get-Credential-Value -Key "CIGNA_PASSWORD"
        ClaimsUrl = Get-Credential-Value -Key "CIGNA_CLAIMS_URL"
    }
}

# Get Azure DevOps credentials
function Get-AdoCredentials {
    return @{
        OrgUrl = Get-Credential-Value -Key "ADO_ORG_URL"
        Project = Get-Credential-Value -Key "ADO_PROJECT"
        Pat = Get-Credential-Value -Key "ADO_PAT"
        Username = Get-Credential-Value -Key "ADO_USERNAME"
    }
}

# Get Google credentials
function Get-GoogleCredentials {
    return @{
        CredentialsPath = Get-Credential-Value -Key "GOOGLE_CREDENTIALS_PATH"
        TokenPath = Get-Credential-Value -Key "GOOGLE_TOKEN_PATH"
        Scopes = Get-Credential-Value -Key "GMAIL_API_SCOPES"
    }
}
```

### Usage in Scripts

```powershell
# Import credential loader
. "${PARA_ROOT}\03_Areas\Keys\load_credentials.ps1"

# Load all credentials
Load-Env

# Method 1: Get individual credentials
$cignaUser = Get-Credential-Value -Key "CIGNA_USERNAME"
$cignaPass = Get-Credential-Value -Key "CIGNA_PASSWORD"

# Method 2: Get all service credentials at once
$cigna = Get-CignaCredentials
Write-Host "Logging in as: $($cigna.Username)"

# Method 3: Get optional credential
$optionalKey = Get-Credential-Value -Key "OPTIONAL_KEY" -Required $false
```

---

## Adding New Credentials

### Step-by-Step Process

#### 1. Add to .env File

Edit `${PARA_ROOT}\03_Areas\Keys\.env`:

```bash
# ===================================
# NEW SERVICE NAME
# ===================================
NEWSERVICE_USERNAME=your_username
NEWSERVICE_PASSWORD=your_password
NEWSERVICE_API_KEY=your_api_key
NEWSERVICE_BASE_URL=https://api.newservice.com
```

#### 2. Add Python Helper Function

Edit `${PARA_ROOT}\03_Areas\Keys\load_credentials.py`:

```python
def get_newservice_credentials():
    """Get New Service credentials"""
    return {
        'username': get_credential('NEWSERVICE_USERNAME'),
        'password': get_credential('NEWSERVICE_PASSWORD'),
        'api_key': get_credential('NEWSERVICE_API_KEY'),
        'base_url': get_credential('NEWSERVICE_BASE_URL')
    }
```

#### 3. Add PowerShell Helper Function

Edit `${PARA_ROOT}\03_Areas\Keys\load_credentials.ps1`:

```powershell
function Get-NewServiceCredentials {
    return @{
        Username = Get-Credential-Value -Key "NEWSERVICE_USERNAME"
        Password = Get-Credential-Value -Key "NEWSERVICE_PASSWORD"
        ApiKey = Get-Credential-Value -Key "NEWSERVICE_API_KEY"
        BaseUrl = Get-Credential-Value -Key "NEWSERVICE_BASE_URL"
    }
}
```

#### 4. Update Documentation

Add to [Current Credentials Inventory](#current-credentials-inventory) section below.

#### 5. Test

```python
# Python test
from load_credentials import load_env, get_newservice_credentials
load_env()
creds = get_newservice_credentials()
print(creds)
```

```powershell
# PowerShell test
. "${PARA_ROOT}\03_Areas\Keys\load_credentials.ps1"
Load-Env
$creds = Get-NewServiceCredentials
$creds
```

---

## Current Credentials Inventory

### Health Insurance

#### Cigna
- **Variables**: `CIGNA_USERNAME`, `CIGNA_PASSWORD`, `CIGNA_CLAIMS_URL`
- **Purpose**: Access health insurance claims and benefits
- **Helper**: `get_cigna_credentials()` (Python), `Get-CignaCredentials` (PowerShell)
- **Last Updated**: January 2026

### Work & Productivity

#### Microsoft 365 / Microsoft Graph API
- **API**: Microsoft Graph API v1.0
- **Auth Type**: OAuth 2.0 Delegated Permissions (user context)
- **Client ID**: `1e1de7bf-6be5-4795-ad73-bf753ccb5ba5`
- **Tenant ID**: `31996441-7546-4120-826b-df0c3e239671`
- **Token Location**: `${PARA_ROOT}\03_Areas\Keys\Microsoft365\token.json`
- **Purpose**: Work email (Outlook), calendar (disabled)
- **Scopes**: Mail.Read, Calendars.Read, Files.Read.All, Sites.Read.All, User.Read
- **Setup**: Run `python setup_microsoft_oauth.py` for user consent flow
- **Setup Guide**: See `${PARA_ROOT}\01_Projects\Development\OAUTH_SETUP_GUIDE.md`
- **Endpoints**:
  - Mail: `https://graph.microsoft.com/v1.0/me/messages`
  - Calendar: `https://graph.microsoft.com/v1.0/me/events`
  - Drive: `https://graph.microsoft.com/v1.0/me/drive/recent`
- **Token Expiry**: 1 hour (requires re-authentication)
- **Last Updated**: February 22, 2026

#### Azure DevOps
- **Variables**: `ADO_ORG_URL`, `ADO_PROJECT`, `ADO_PAT`, `ADO_USERNAME`
- **Purpose**: Automate work item creation and management
- **Helper**: `get_ado_credentials()` (Python), `Get-AdoCredentials` (PowerShell)
- **Last Updated**: January 2026
- **PAT Expiration**: Check quarterly

### Google Services

#### Gmail API
- **Variables**: `GOOGLE_CREDENTIALS_PATH`, `GOOGLE_TOKEN_PATH`, `GMAIL_API_SCOPES`
- **Purpose**: Email automation and organization
- **Helper**: `get_google_credentials()` (Python), `Get-GoogleCredentials` (PowerShell)
- **OAuth Type**: Desktop app OAuth 2.0
- **Last Updated**: January 2026

### Downloads & Media

#### Torrent Services
- **Variables**: `TORRENT_DOWNLOAD_PATH`, `TORRENT_TRACKER_URL`, `TORRENT_USERNAME`, `TORRENT_PASSKEY`
- **Purpose**: Automated torrent downloads
- **Helper**: `get_torrent_credentials()` (Python)
- **Last Updated**: January 2026

### AI Services

#### OpenAI
- **Variables**: `OPENAI_API_KEY`
- **Purpose**: GPT API access
- **Last Updated**: TBD

#### Anthropic
- **Variables**: `ANTHROPIC_API_KEY`
- **Purpose**: Claude API access
- **Last Updated**: TBD

### Cloud Services

#### AWS
- **Variables**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- **Purpose**: Cloud storage and services
- **Helper**: `get_aws_credentials()` (Python)
- **Last Updated**: TBD

### Database

#### PostgreSQL (Example)
- **Variables**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`
- **Purpose**: Database connections
- **Helper**: `get_database_credentials()` (Python)
- **Last Updated**: TBD

---

## Best Practices

### 1. Credential Rotation Schedule

| Credential Type | Rotation Frequency | Next Review |
|----------------|-------------------|-------------|
| Passwords | Every 90 days | April 2026 |
| API Keys | Every 180 days | July 2026 |
| Personal Access Tokens | Every 90 days | April 2026 |
| OAuth Tokens | Auto-refresh | N/A |

### 2. Access Control

- **Principle of Least Privilege**: Only grant minimum necessary permissions
- **Regular Audits**: Review credential usage quarterly
- **Immediate Revocation**: Disable compromised credentials immediately
- **Separate Credentials**: Never reuse passwords across services

### 3. Storage Security

- **Encryption**: Use encrypted storage for backups
- **Permissions**: Restrict file permissions to owner only
- **Backups**: Monthly encrypted backups to separate location
- **Version Control**: NEVER commit .env to Git

### 4. Usage Security

- **No Logging**: Never log credentials in application logs
- **No Printing**: Never print credentials to console
- **No Sharing**: Never share credentials via email/chat
- **Secure Transmission**: Only transmit over HTTPS/TLS

### 5. Development vs Production

```python
# Use different credentials for dev/prod
ENV = os.getenv('ENVIRONMENT', 'development')

if ENV == 'production':
    creds = get_production_credentials()
else:
    creds = get_development_credentials()
```

---

## Security Checklist

### Daily
- [ ] No credentials in code commits
- [ ] No credentials in console output
- [ ] Scripts use credential helpers

### Weekly
- [ ] Review credential access logs
- [ ] Check for unauthorized access attempts
- [ ] Verify .env file permissions

### Monthly
- [ ] Backup .env file (encrypted)
- [ ] Review credential inventory
- [ ] Update documentation

### Quarterly
- [ ] Rotate passwords and PATs
- [ ] Audit credential usage
- [ ] Review and update helper functions
- [ ] Test credential recovery process

### Yearly
- [ ] Comprehensive security audit
- [ ] Update all credentials
- [ ] Review and update security policies
- [ ] Test disaster recovery

---

## Troubleshooting

### Issue: "Credential not found" Error

**Cause**: Environment variable not loaded or misspelled

**Solution**:
```python
# Verify .env file exists
import os
print(os.path.exists("${PARA_ROOT}\\03_Areas\\Keys\\.env"))

# Check if variable is loaded
print(os.getenv('CIGNA_USERNAME'))  # Should not be None

# Reload environment
load_env()
```

### Issue: ".env file not found"

**Cause**: Incorrect path or file doesn't exist

**Solution**:
```python
from pathlib import Path

env_path = Path(r"${PARA_ROOT}\03_Areas\Keys\.env")
print(f"Exists: {env_path.exists()}")
print(f"Path: {env_path.absolute()}")
```

### Issue: "Permission denied" when reading .env

**Cause**: File permissions too restrictive

**Solution**:
```powershell
# Check permissions
Get-Acl "${PARA_ROOT}\03_Areas\Keys\.env" | Format-List

# Fix permissions (Windows)
icacls "${PARA_ROOT}\03_Areas\Keys\.env" /grant:r "$env:USERNAME:(R)"
```

### Issue: Credentials work locally but not in automation

**Cause**: Environment not loaded in automation context

**Solution**:
```python
# Always load at start of script
from load_credentials import load_env
load_env()  # Must be called before using credentials
```

### Issue: OAuth token expired

**Cause**: Google token needs refresh

**Solution**:
```python
# Delete token.json to force re-authentication
import os
token_path = "${PARA_ROOT}\\token.json"
if os.path.exists(token_path):
    os.remove(token_path)
# Run script again - will prompt for re-auth
```

---

## Emergency Procedures

### Credential Compromise

1. **Immediate Actions**:
   - Revoke compromised credential immediately
   - Generate new credential
   - Update .env file
   - Test all affected scripts

2. **Investigation**:
   - Review access logs
   - Identify scope of compromise
   - Document incident

3. **Prevention**:
   - Rotate all related credentials
   - Review security practices
   - Update documentation

### Lost .env File

1. **Recovery**:
   - Restore from encrypted backup
   - Verify all credentials still valid
   - Test credential helpers

2. **If No Backup**:
   - Manually recreate .env file
   - Reset all credentials
   - Update all services
   - Test thoroughly

---

## Related Guides

- [MASTER_GUIDE_AZURE_DEVOPS_AUTOMATION.md](MASTER_GUIDE_AZURE_DEVOPS_AUTOMATION.md) - ADO automation using credentials
- [MASTER_GUIDE_GMAIL_AUTOMATION.md](MASTER_GUIDE_GMAIL_AUTOMATION.md) - Gmail OAuth setup
- [MASTER_GUIDE_FILE_ORGANIZATION.md](MASTER_GUIDE_FILE_ORGANIZATION.md) - File organization system

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-25 | Initial creation - comprehensive credential management guide |

---

## Quick Reference

### Load Credentials (Python)
```python
from load_credentials import load_env, get_cigna_credentials
load_env()
creds = get_cigna_credentials()
```

### Load Credentials (PowerShell)
```powershell
. "${PARA_ROOT}\03_Areas\Keys\load_credentials.ps1"
Load-Env
$creds = Get-CignaCredentials
```

### Add New Credential
1. Add to `.env` file
2. Add helper function to `load_credentials.py` and `load_credentials.ps1`
3. Update this guide's inventory
4. Test in both Python and PowerShell

### Security Rules
- ✓ Use environment variables
- ✓ Load from .env file
- ✓ Use credential helpers
- ✗ Never hardcode
- ✗ Never commit to Git
- ✗ Never log or print
