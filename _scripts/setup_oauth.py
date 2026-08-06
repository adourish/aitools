#!/usr/bin/env python3
"""
OAuth Setup Script for Daily Planning
Sets up user authentication for Google Drive (Gmail + Drive)
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Paths
GMAIL_CREDS_PATH = r'G:\My Drive\03_Areas\Keys\Gmail\credentials.json'
GMAIL_TOKEN_PATH = r'G:\My Drive\03_Areas\Keys\Gmail\token.json'

# Scopes
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def setup_google_oauth():
    """Set up Google OAuth with Gmail and Drive scopes"""
    print("\n" + "="*60)
    print("GOOGLE OAUTH SETUP (Gmail + Drive)")
    print("="*60)
    
    if not os.path.exists(GMAIL_CREDS_PATH):
        print(f"❌ Credentials file not found: {GMAIL_CREDS_PATH}")
        print("   Download from Google Cloud Console")
        return False
    
    try:
        # Delete old token to force re-authentication with new scopes
        if os.path.exists(GMAIL_TOKEN_PATH):
            print("🗑️  Removing old token to re-authenticate with Drive scope...")
            os.remove(GMAIL_TOKEN_PATH)
        
        print("🔐 Starting OAuth flow...")
        print("   Browser will open for authentication")
        print("   Grant access to Gmail and Drive\n")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            GMAIL_CREDS_PATH,
            GOOGLE_SCOPES
        )
        
        creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(GMAIL_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        
        print("✅ Google OAuth successful!")
        print(f"   Token saved to: {GMAIL_TOKEN_PATH}")
        print(f"   Scopes: Gmail + Drive")
        return True
        
    except Exception as e:
        print(f"❌ Google OAuth failed: {e}")
        return False

def setup_microsoft_oauth():
    """Microsoft OAuth setup has been disabled"""
    print("\n" + "="*60)
    print("MICROSOFT 365 OAUTH SETUP - DISABLED")
    print("="*60)
    print("Microsoft 365 (Outlook + SharePoint) integration has been removed.")
    print("The system now uses Gmail and Google Drive exclusively.")
    return False
        print("   Grant access to Mail, Calendar, Files, and Sites\n")
        
        # Interactive authentication
        result = app.acquire_token_interactive(
            scopes=MICROSOFT_SCOPES,
            prompt="select_account"
        )
        
        if "access_token" in result:
            # Save token
            os.makedirs(os.path.dirname(MS_TOKEN_PATH), exist_ok=True)
            
            token_data = {
                'access_token': result['access_token'],
                'refresh_token': result.get('refresh_token'),
                'expires_in': result.get('expires_in'),
                'token_type': result.get('token_type'),
                'scope': result.get('scope'),
                'acquired_at': datetime.now().isoformat()
            }
            
            with open(MS_TOKEN_PATH, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print("✅ Microsoft 365 OAuth successful!")
            print(f"   Token saved to: {MS_TOKEN_PATH}")
            print(f"   Scopes: Mail, Calendar, Files, Sites")
            return True
        else:
            print(f"❌ Microsoft 365 OAuth failed: {result.get('error_description')}")
            return False
            
    except Exception as e:
        print(f"❌ Microsoft 365 OAuth failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("HOLISTIC DAILY PLANNING - OAUTH SETUP")
    print("="*60)
    print("\nThis script will set up OAuth authentication for:")
    print("  1. Google (Gmail + Drive)")
    print("\nYou'll need to:")
    print("  - Sign in to your Google account")
    print("  - Grant permissions for Gmail and Drive")
    print("\n" + "="*60)
    
    input("\nPress Enter to continue...")
    
    # Setup Google OAuth
    google_success = setup_google_oauth()
    
    # Setup Microsoft OAuth
    ms_success = setup_microsoft_oauth()
    
    # Summary
    print("\n" + "="*60)
    print("OAUTH SETUP SUMMARY")
    print("="*60)
    print(f"Google (Gmail + Drive):     {'✅ Success' if google_success else '❌ Failed'}")
    print("="*60)

    if google_success:
        print("\n✅ OAuth setup complete!")
        print("   You can now run 'process new'")
        print("\n   Run: python run_process_new_v2.py")
    else:
        print("\n❌ OAuth setup failed")
        print("   Check error messages above and try again")

if __name__ == '__main__':
    main()
