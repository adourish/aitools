#!/usr/bin/env python3
"""
Google Calendar tools for MCP Server
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class CalendarTools:
    """Google Calendar operations for MCP server"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self._service = None
    
    async def _get_service(self):
        """Get Calendar service, creating if needed"""
        if not self._service:
            creds = await self.auth_manager.get_gmail_credentials()
            self._service = build('calendar', 'v3', credentials=creds)
        return self._service
    
    async def get_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get calendar events for next N days"""
        service = await self._get_service()
        
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            # Filter calendar events
            filtered_events = []
            for event in events:
                summary = event.get('summary', '').lower()
                attendees = event.get('attendees', [])

                # Skip personal reminders (birthdays, anniversaries with no attendees)
                if any(word in summary for word in ['birthday', 'anniversary', 'bday']):
                    if not attendees or len(attendees) <= 1:
                        continue

                # Skip sign-up related events
                if any(word in summary for word in ['signup', 'sign up', 'sign-up', 'registration']):
                    continue

                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                organizer = event.get('organizer', {}).get('email', 'Unknown')
                is_recurring = 'recurringEventId' in event

                # Parse time
                if 'T' in start:
                    event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = event_time.strftime('%I:%M %p')
                else:
                    event_time = datetime.fromisoformat(start + 'T00:00:00+00:00')
                    time_str = 'All day'

                filtered_events.append({
                    'id': event['id'],
                    'summary': summary,
                    'date': event_time.strftime('%Y-%m-%d'),
                    'time': time_str,
                    'organizer': organizer,
                    'is_recurring': is_recurring
                })
            
            logger.info(f"Retrieved {len(filtered_events)} calendar events (Alex's events filtered)")
            return filtered_events
        
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            raise
