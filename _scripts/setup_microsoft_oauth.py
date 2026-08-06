#!/usr/bin/env python3
"""
Microsoft 365 OAuth Setup
Sets up delegated permissions for Outlook email and Calendar
"""

import os
import json
from datetime import datetime
from msal import PublicClientApplication

# Paths
ENVIRONMENTS_PATH = r'G:\My Drive\03_Areas\Keys\Environments\environments.json'
MS_TOKEN_PATH = r'G:\My Drive\03_Areas\Keys\Microsoft365\token.json'

# Microsoft Graph Scopes
SCOPES = [
    'https://graph.microsoft.com/Mail.Read',
    'https://graph.microsoft.com/Calendars.Read',
    'https://graph.microsoft.com/User.Read'
]

def setup_microsoft_oauth():
    """Set up Microsoft OAuth with delegated permissions"""
    print("\n" + "="*60)
    print("MICROSOFT 365 OAUTH SETUP")
    print("="*60)
    print("\nThis will set up access to:")
    print("  - Outlook Email (work)")
    print("  - Calendar")
    print("\n" + "="*60)
    
    # Load config
    with open(ENVIRONMENTS_PATH, 'r') as f:
        config = json.load(f)
    
    ms_config = config['environments']['microsoft365']['oauth']
    client_id = ms_config['clientId']
    tenant_id = ms_config['tenantId']
    
    print(f"\nClient ID: {client_id}")
    print(f"Tenant ID: {tenant_id}")
    
    try:
        # Create public client application for delegated permissions
        app = PublicClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )
        
        print("\n🔐 Starting OAuth flow...")
        print("   Browser will open for authentication")
        print("   Sign in with your work account")
        print("   Grant access to Mail, Calendar, Files, and Sites\n")
        
        input("Press Enter to open browser and authenticate...")
        
        # Interactive authentication
        result = app.acquire_token_interactive(
            scopes=SCOPES,
            prompt="select_account"
        )
        
        if "access_token" in result:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(MS_TOKEN_PATH), exist_ok=True)
            
            # Save token
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
            
            print("\n" + "="*60)
            print("✅ MICROSOFT 365 OAUTH SUCCESSFUL!")
            print("="*60)
            print(f"Token saved to: {MS_TOKEN_PATH}")
            print(f"Scopes granted: {len(SCOPES)}")
            print("\nYou can now run:")
            print("  python daily_planner.py")
            print("\nTo see Outlook emails and SharePoint documents in your daily plan!")
            return True
        else:
            print("\n" + "="*60)
            print("❌ MICROSOFT 365 OAUTH FAILED")
            print("="*60)
            print(f"Error: {result.get('error')}")
            print(f"Description: {result.get('error_description')}")
            return False
            
    except Exception as e:
        print("\n" + "="*60)
        print("❌ MICROSOFT 365 OAUTH FAILED")
        print("="*60)
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = setup_microsoft_oauth()
    
    if not success:
        print("\n⚠️  OAuth setup failed. Please check:")
        print("  1. You have internet connection")
        print("  2. Your work account credentials are correct")
        print("  3. The Azure app is properly configured")
        print("\nTry running again: python setup_microsoft_oauth.py")
