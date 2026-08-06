#!/usr/bin/env python3
"""
Authenticate Services
Interactive script to set up OAuth tokens for daily planning
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
    print("AUTHENTICATION SETUP FOR DAILY PLANNING")
    print("="*60)

    status = check_token_status()

    print("\nCurrent Authentication Status:")
    print(f"  {'✅' if status['gmail'] else '❌'} Gmail/Google Drive")

    missing = [k for k, v in status.items() if not v]

    if not missing:
        print("\n✅ Authentication token is present!")
        print("\nNote: Token may still be expired. Run 'process new' to verify.")
        return

    print(f"\n⚠️  Missing: {', '.join(missing)}")
    print("\nWhat would you like to do?")
    print("  1. Set up Gmail/Google Drive OAuth")
    print("  2. Exit")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        print("\n" + "="*60)
        print("GMAIL/GOOGLE DRIVE SETUP")
        print("="*60)
        print("\nTo set up Gmail and Google Drive:")
        print("1. Delete existing token if present:")
        print("   del \"G:\\My Drive\\03_Areas\\Keys\\Gmail\\token.json\"")
        print("\n2. Run the process new script - it will trigger OAuth flow:")
        print("   python run_process_new_v2.py")
        print("\n3. A browser will open for you to sign in with your Google account")
        print("4. Grant permissions for Gmail and Drive access")

    if choice == "2":
        print("\nExiting...")
        return

    print("\n" + "="*60)
    print("After authentication, run 'process new' to generate your daily plan!")
    print("="*60)

if __name__ == '__main__':
    main()
