#!/usr/bin/env python3
"""
Authenticate All Services
Interactive script to set up all OAuth tokens for holistic daily planning
"""

import os
import sys
from pathlib import Path

def check_token_status():
    """Check which tokens are missing or expired"""
    gmail_token = Path(r'G:\My Drive\03_Areas\Keys\Gmail\token.json')

    status = {
        'gmail': gmail_token.exists()
    }

    return status

def main():
    print("\n" + "="*60)
    print("AUTHENTICATION SETUP FOR HOLISTIC DAILY PLANNING")
    print("="*60)
    
    status = check_token_status()

    print("\nCurrent Authentication Status:")
    print(f"  {'✅' if status['gmail'] else '❌'} Gmail/Google Drive")

    missing = [k for k, v in status.items() if not v]

    if not missing:
        print("\n✅ All tokens are present!")
        print("\nNote: Tokens may still be expired. Run 'process new' to verify.")
        return

    if missing:
        print(f"\n⚠️  Missing: {', '.join(missing)}")
        print("\nTo set up Gmail and Google Drive:")
        print("1. Delete existing token if present:")
        print("   del \"G:\\My Drive\\03_Areas\\Keys\\Gmail\\token.json\"")
        print("\n2. Run the daily planner - it will trigger OAuth flow:")
        print("   python daily_planner.py")
        print("\n3. A browser will open for you to sign in with your Google account")
        print("4. Grant permissions for Gmail and Drive access")


    print("\n" + "="*60)
    print("After authentication, run 'process new' to generate your daily plan!")
    print("="*60)

if __name__ == '__main__':
    main()
