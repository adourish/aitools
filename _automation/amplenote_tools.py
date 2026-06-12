#!/usr/bin/env python3
"""
Amplenote tools for MCP Server
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class AmplenoteTools:
    """Amplenote operations for MCP server"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.base_url = "https://api.amplenote.com/v4"
        self.openrouter_key = None
        self._openrouter_key_loaded = False
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token"""
        token = await self.auth_manager.get_amplenote_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    async def _ensure_openrouter_key(self) -> bool:
        """Ensure OpenRouter API key is loaded from auth_manager"""
        if not self._openrouter_key_loaded:
            self.openrouter_key = await self.auth_manager.get_openrouter_key()
            self._openrouter_key_loaded = True
        return self.openrouter_key is not None
    
    async def create_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new note in Amplenote"""
        headers = await self._get_headers()
        
        try:
            note_data = {'name': title, 'text': content}
            
            if tags:
                # Amplenote expects tags as array of objects with 'text' field
                note_data['tags'] = [{'text': tag} for tag in tags]
            
            logger.info(f"Sending to Amplenote - Title: {title}, Body length: {len(content)}")
            logger.debug(f"Note data structure: {note_data}")
            
            response = requests.post(
                f"{self.base_url}/notes",
                headers=headers,
                json=note_data
            )
            
            logger.info(f"Amplenote response status: {response.status_code}")
            logger.debug(f"Amplenote response: {response.text}")
            
            if response.status_code == 401:
                logger.warning("Amplenote token expired, attempting automatic refresh...")
                
                # Try to refresh the token automatically
                try:
                    new_token = await self.auth_manager.refresh_amplenote_token()
                    logger.info("Token refreshed successfully, retrying request...")
                    
                    # Retry the request with new token
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.post(
                        f"{self.base_url}/notes",
                        headers=headers,
                        json=note_data
                    )
                    
                    if response.status_code >= 400:
                        logger.error(f"Amplenote API error after refresh: {response.status_code} - {response.text}")
                        raise Exception(f"Amplenote API error: {response.status_code}")
                    
                    # Success after refresh
                    note = response.json()
                    logger.info(f"Created Amplenote note after token refresh: {title}")
                    return note
                    
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh Amplenote token: {refresh_error}")
                    print("\n" + "=" * 70)
                    print("⚠️  AMPLENOTE TOKEN REFRESH FAILED")
                    print("=" * 70)
                    print("\nAutomatic token refresh failed.")
                    print("\nTo manually refresh the token, run:")
                    print('  cd "G:\\My Drive\\06_Master_Guides\\Scripts"')
                    print("  node refresh_amplenote_token.js")
                    print("\nThen run process new again.")
                    print("=" * 70 + "\n")
                    raise Exception("Amplenote token refresh failed - manual intervention required")
            elif response.status_code >= 400:
                logger.error(f"Amplenote API error: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            note = response.json()
            logger.info(f"Created Amplenote note: {title}")
            return note
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Already handled above, just re-raise
                raise
            logger.error(f"Error creating Amplenote note: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating Amplenote note: {e}")
            raise
    
    async def get_notes(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notes from Amplenote"""
        headers = await self._get_headers()
        
        try:
            url = f"{self.base_url}/notes"
            if tag:
                url += f"?tag={tag}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                logger.warning("Amplenote token expired, attempting automatic refresh...")
                
                try:
                    new_token = await self.auth_manager.refresh_amplenote_token()
                    logger.info("Token refreshed successfully, retrying request...")
                    
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code >= 400:
                        logger.error(f"Amplenote API error after refresh: {response.status_code} - {response.text}")
                        raise Exception(f"Amplenote API error: {response.status_code}")
                
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh Amplenote token: {refresh_error}")
                    raise Exception("Amplenote token refresh failed - manual intervention required")
            
            response.raise_for_status()
            
            response_data = response.json()
            # API returns dict with 'notes' key containing array of note objects
            if isinstance(response_data, dict) and 'notes' in response_data:
                notes = response_data['notes']
            elif isinstance(response_data, list):
                notes = response_data
            else:
                logger.warning(f"Unexpected API response format: {type(response_data)}")
                notes = []
            
            logger.info(f"Retrieved {len(notes)} notes from Amplenote")
            return notes
        
        except Exception as e:
            logger.error(f"Error getting Amplenote notes: {e}")
            raise
    
    async def find_daily_note(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find today's daily note by title pattern"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        headers = await self._get_headers()
        
        try:
            response = requests.get(f"{self.base_url}/notes", headers=headers)
            response.raise_for_status()
            notes_data = response.json()
            
            # Handle different response formats
            if isinstance(notes_data, dict) and 'notes' in notes_data:
                notes = notes_data['notes']
            elif isinstance(notes_data, list):
                notes = notes_data
            else:
                logger.warning(f"Unexpected notes response format: {type(notes_data)}")
                return None
            
            # Look for daily note with date in title
            for note in notes:
                if isinstance(note, str):
                    continue
                note_title = note.get('name', '') if isinstance(note, dict) else ''
                if date in note_title or datetime.now().strftime("%B %d, %Y") in note_title:
                    logger.info(f"Found daily note: {note_title}")
                    return note
            
            logger.info(f"No daily note found for {date}")
            return None
        
        except Exception as e:
            logger.error(f"Error finding daily note: {e}")
            return None
    
    async def get_note_content(self, note_uuid: str) -> str:
        """Get the full content of a note"""
        headers = await self._get_headers()
        
        try:
            response = requests.get(f"{self.base_url}/notes/{note_uuid}", headers=headers)
            response.raise_for_status()
            note = response.json()
            return note.get('body', '')
        
        except Exception as e:
            logger.error(f"Error getting note content: {e}")
            raise
    
    async def replace_note_content(self, note_uuid: str, content: str) -> bool:
        """Replace all content in a note using PUT request"""
        headers = await self._get_headers()
        
        try:
            # Use PUT to completely replace note text
            response = requests.put(
                f"{self.base_url}/notes/{note_uuid}",
                headers=headers,
                json={'text': content}
            )
            response.raise_for_status()
            logger.info(f"Replaced content in note: {note_uuid}")
            return True
        
        except Exception as e:
            logger.error(f"Error replacing note content: {e}")
            logger.error(f"Response: {response.text if 'response' in locals() else 'No response'}")
            return False
    
    async def update_note(self, note_uuid: str, content: str) -> Dict[str, Any]:
        """Update an existing note's content"""
        headers = await self._get_headers()
        
        try:
            response = requests.put(
                f"{self.base_url}/notes/{note_uuid}",
                headers=headers,
                json={'text': content}
            )
            
            if response.status_code >= 400:
                logger.error(f"Amplenote API error updating note: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            logger.info(f"Updated note: {note_uuid}")
            return response.json() if response.text else {"success": True}
        
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            raise
    
    async def delete_note(self, note_uuid: str) -> bool:
        """Delete a note"""
        headers = await self._get_headers()
        
        try:
            response = requests.delete(
                f"{self.base_url}/notes/{note_uuid}",
                headers=headers
            )
            
            if response.status_code >= 400:
                logger.error(f"Amplenote API error deleting note: {response.status_code} - {response.text}")
                return False
            
            response.raise_for_status()
            logger.info(f"Deleted note: {note_uuid}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return False
    
    async def insert_content(self, note_uuid: str, text: str) -> bool:
        """Insert content into note using actions endpoint"""
        headers = await self._get_headers()
        
        try:
            action_data = {
                'type': 'INSERT_NODES',
                'nodes': [
                    {
                        'type': 'paragraph',
                        'content': [
                            {
                                'type': 'text',
                                'text': text
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/notes/{note_uuid}/actions",
                headers=headers,
                json=action_data
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            logger.error(f"Error inserting content: {e}")
            return False
    
    async def insert_task(self, note_uuid: str, text: str, important: bool = False) -> bool:
        """Insert a task/checkbox into note"""
        headers = await self._get_headers()
        
        try:
            attrs = {}
            if important:
                attrs['flags'] = 'I'
            
            action_data = {
                'type': 'INSERT_NODES',
                'nodes': [
                    {
                        'type': 'check_list_item',
                        'attrs': attrs,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': text
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/notes/{note_uuid}/actions",
                headers=headers,
                json=action_data
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            logger.error(f"Error inserting task: {e}")
            return False
    
    async def _generate_daily_summary(self, plan: Dict[str, Any]) -> str:
        """Use AI to generate executive summary of the day"""
        try:
            # Collect all content for analysis
            emails = [item for item in plan['do_now'] if item.get('source') == 'Email']
            tasks = [item for item in plan['do_now'] if item.get('source') == 'Todoist']
            events = [item for item in plan['do_now'] if item.get('source') == 'Calendar']
            upcoming = plan['do_soon'][:5]  # Next 5 items
            
            # Build comprehensive context
            context = "Today's Overview:\n\n"
            
            if emails:
                context += "EMAILS:\n"
                for email in emails[:5]:
                    context += f"- {email.get('title', '')}\n"
                    context += f"  From: {email.get('from', '')}\n"
                    if email.get('thread_context'):
                        context += f"  Context: {email.get('thread_context', '')[:150]}\n"
                    elif email.get('preview'):
                        context += f"  Preview: {email.get('preview', '')[:150]}\n"
                context += "\n"
            
            if events:
                context += "EVENTS:\n"
                for event in events:
                    time_str = f" at {event.get('time', '')}" if event.get('time') else ""
                    context += f"- {event.get('title', '')}{time_str}\n"
                context += "\n"
            
            if tasks:
                context += "TASKS:\n"
                for task in tasks:
                    context += f"- {task.get('title', '')}\n"
                context += "\n"
            
            if upcoming:
                context += "UPCOMING:\n"
                for item in upcoming:
                    due = f" (Due: {item.get('due', '')})" if item.get('due') else ""
                    context += f"- {item.get('title', '')}{due}\n"
            
            # Generate AI summary
            if not await self._ensure_openrouter_key():
                return "• No AI summary available (OpenRouter key not configured)"
            
            import requests
            prompt = f"""Analyze this day's schedule and create a bulleted executive summary.

{context}

Create 3-5 bullet points covering:
- Key actions needed (especially responses to emails or follow-ups)
- Important deadlines or time-sensitive items
- Notable updates or responses received
- Any conflicts or scheduling considerations

Format as bullet points starting with • or -. Be specific about WHO responded and WHAT they said if relevant."""

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://adourish.github.io",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-sonnet-4-6",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    summary = result['choices'][0]['message']['content'].strip()
                    return summary
            
            return "Focus on urgent emails and scheduled events today."
            
        except Exception as e:
            logger.warning(f"Failed to generate daily summary: {e}")
            return "Review your tasks and emails to prioritize your day."
    
    async def update_daily_note_with_plan(self, plan: Dict[str, Any]) -> bool:
        """Create/update single daily plan note using INSERT_NODES for proper rendering"""
        try:
            static_title = "\U0001f4cb Daily Plan"

            # Find existing note to replace
            all_notes = await self.get_notes(tag='daily-plan')
            logger.info(f"Found {len(all_notes)} notes with 'daily-plan' tag")

            existing_note_uuid = None
            logger.info(f"Searching all {len(all_notes)} notes for static daily plan: {static_title}")
            for note_item in all_notes:
                try:
                    if isinstance(note_item, dict) and note_item.get('name', '') == static_title:
                        existing_note_uuid = note_item.get('uuid')
                        logger.info(f"✓ Found existing daily plan note: {static_title} (UUID: {existing_note_uuid})")
                        break
                except Exception as e:
                    logger.warning(f"Error checking note: {e}")
                    continue

            # Delete old note if it exists
            if existing_note_uuid:
                logger.info(f"Deleting existing daily plan note: {existing_note_uuid}")
                await self.delete_note(existing_note_uuid)

            # Create empty note first
            logger.info(f"Creating new daily plan note")
            note = await self.create_note(
                title=static_title,
                content="",
                tags=['daily-plan', 'process-new']
            )
            note_uuid = note['uuid']

            # Build structured nodes and insert them
            nodes = self._build_daily_plan_nodes(plan)
            await self._insert_nodes_batched(note_uuid, nodes)

            logger.info(f"Daily plan note created successfully: https://www.amplenote.com/notes/{note_uuid}")
            return True

        except Exception as e:
            logger.error(f"Error creating daily plan note: {e}")
            return False

    async def _insert_nodes_batched(self, note_uuid: str, nodes: list, batch_size: int = 15):
        """Insert nodes in batches to avoid API limits"""
        headers = await self._get_headers()
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            action_data = {
                'type': 'INSERT_NODES',
                'nodes': batch
            }
            try:
                response = requests.post(
                    f"{self.base_url}/notes/{note_uuid}/actions",
                    headers=headers,
                    json=action_data,
                    timeout=30
                )
                if response.status_code >= 400:
                    logger.warning(f"INSERT_NODES batch {i // batch_size + 1} returned {response.status_code}: {response.text[:200]}")
            except Exception as e:
                logger.warning(f"INSERT_NODES batch {i // batch_size + 1} failed: {e}")

    def _make_heading(self, text: str, level: int = 2) -> dict:
        """Create a heading node"""
        return {
            'type': 'heading',
            'attrs': {'level': level},
            'content': [{'type': 'text', 'text': text}]
        }

    def _make_paragraph(self, text: str) -> dict:
        """Create a paragraph node"""
        return {
            'type': 'paragraph',
            'content': [{'type': 'text', 'text': text}]
        }

    def _make_bullet(self, text: str) -> dict:
        """Create a bullet list item node"""
        return {
            'type': 'bullet_list_item',
            'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': text}]}]
        }

    def _make_task(self, text: str, important: bool = False) -> dict:
        """Create a check list item (task) node"""
        attrs = {}
        if important:
            attrs['flags'] = 'I'
        return {
            'type': 'check_list_item',
            'attrs': attrs,
            'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': text}]}]
        }

    def _build_daily_plan_nodes(self, plan: Dict[str, Any]) -> list:
        """Build structured Amplenote nodes for the daily plan"""
        nodes = []
        now = datetime.now()

        # ── Header ──
        nodes.append(self._make_paragraph(f"\U0001f4c5 {now.strftime('%A, %B %d, %Y')}"))

        # ── Today's Schedule ──
        today_events = plan.get('today_events', [])
        if today_events:
            nodes.append(self._make_heading("Today", 2))
            nodes.extend(self._events_to_nodes(today_events))

        # ── Tomorrow's Schedule ──
        tomorrow_events = plan.get('tomorrow_events', [])
        if tomorrow_events:
            try:
                from datetime import timedelta
                tmrw_date = (now + timedelta(days=1)).strftime('%A %b %d')
            except Exception:
                tmrw_date = "Tomorrow"
            nodes.append(self._make_heading(f"Tomorrow — {tmrw_date}", 2))
            nodes.extend(self._events_to_nodes(tomorrow_events))

        # ── Action Items ──
        if plan['do_now']:
            nodes.append(self._make_heading("Action Items", 2))
            for item in plan['do_now'][:5]:
                source = item.get('source', '')
                if source == 'Email Thread':
                    action_items = item.get('action_items', [])
                    action = action_items[0] if action_items else item.get('title', 'Review thread')
                    if len(action) > 120:
                        action = action[:117] + "..."
                    nodes.append(self._make_task(action, important=True))
                    context = item.get('context', '')
                    if context and context.lower() != 'fyi only':
                        nodes.append(self._make_paragraph(f"  ↳ {context}"))
                else:
                    nodes.append(self._make_task(item['title']))

        # ── Do Soon ──
        if plan['do_soon']:
            nodes.append(self._make_heading("Do Soon", 2))
            for item in plan['do_soon'][:5]:
                title = item['title'][:80]
                due_str = self._format_due_date(item.get('due'))
                nodes.append(self._make_task(f"{title}{due_str}"))

        # ── Stale Tasks ──
        if plan.get('stale'):
            nodes.append(self._make_heading("Stale — Review or Close", 2))
            for task in plan['stale']:
                days = task.get('days_overdue', '?')
                due = task.get('due', '')
                title = task['title']
                # Extract just the action part before " - " description
                if ' - ' in title:
                    title = title.split(' - ')[0]
                if len(title) > 80:
                    title = title[:77] + "..."
                nodes.append(self._make_bullet(f"{title} — due {due} ({days}d overdue)"))

        # ── Rest of Week ──
        week_events = plan.get('week_events', [])
        if week_events:
            nodes.append(self._make_heading("Rest of Week", 2))
            for event in week_events[:8]:
                date_str = event.get('date', '')
                time_str = event.get('time', '')
                summary = event.get('summary', '')
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    day_label = dt.strftime('%a %b %d')
                except ValueError:
                    day_label = date_str
                if time_str and time_str != 'All day':
                    nodes.append(self._make_bullet(f"{day_label} — {summary} at {time_str}"))
                else:
                    nodes.append(self._make_bullet(f"{day_label} — {summary}"))

        # ── Follow-ups ──
        if plan.get('follow_ups'):
            nodes.append(self._make_heading("Follow-ups", 2))
            for item in plan['follow_ups']:
                text = item.get('follow_up', item.get('title', ''))
                if text:
                    nodes.append(self._make_bullet(text))

        # ── Footer ──
        stats = plan.get('stats', {})
        action_count = len(plan.get('do_now', []))
        stale_count = len(plan.get('stale', []))
        total_events = len(today_events) + len(tomorrow_events) + len(week_events)
        nodes.append(self._make_paragraph("—"))
        nodes.append(self._make_paragraph(
            f"{action_count} actions · {total_events} events · {stale_count} stale · Generated {now.strftime('%I:%M %p')}"
        ))

        return nodes

    def _events_to_nodes(self, events: list) -> list:
        """Convert calendar events to sorted bullet nodes"""
        nodes = []
        timed = [(e, e.get('time', '')) for e in events if e.get('time') and e['time'] != 'All day']
        allday = [e for e in events if not e.get('time') or e['time'] == 'All day']
        timed.sort(key=lambda x: x[1])
        for event, time in timed:
            nodes.append(self._make_bullet(f"{time} — {event.get('summary', '')}"))
        for event in allday:
            nodes.append(self._make_bullet(f"All day — {event.get('summary', '')}"))
        return nodes

    def _format_due_date(self, due_str: Optional[str]) -> str:
        """Format a YYYY-MM-DD date string as readable short date"""
        if not due_str:
            return ""
        try:
            dt = datetime.strptime(due_str, '%Y-%m-%d')
            return f" (due {dt.strftime('%b %d')})"
        except ValueError:
            return f" ({due_str})"
    
    def _format_plan_for_amplenote(self, plan: Dict[str, Any]) -> str:
        """Format the plan data as markdown for Amplenote"""
        lines = []
        lines.append("## Process New Results")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}*\n")
        
        # DO NOW section
        lines.append("### \U0001f3af DO NOW")
        if plan['do_now']:
            for item in plan['do_now']:
                if item['source'] == 'Email':
                    lines.append(f"- [ ] **{item['title']}**")
                    lines.append(f"  - From: {item.get('from', 'Unknown')}")
                    if item.get('preview'):
                        lines.append(f"  - {item['preview'][:150]}...")
                else:
                    time_str = f" at {item['time']}" if item.get('time') else ""
                    lines.append(f"- [ ] **[{item['source']}]** {item['title']}{time_str}")
        else:
            lines.append("- *No urgent items*")
        
        # DO SOON section
        lines.append("\n### ⏰ DO SOON")
        if plan['do_soon']:
            for item in plan['do_soon']:
                due_str = f" (due: {item.get('due', 'N/A')})" if item.get('due') else ""
                time_str = f" at {item['time']}" if item.get('time') else ""
                lines.append(f"- [ ] **[{item['source']}]** {item['title']}{time_str}{due_str}")
        else:
            lines.append("- *No upcoming items*")
        
        # MONITOR section
        lines.append("\n### \U0001f4cb MONITOR")
        if plan['monitor']:
            for item in plan['monitor']:
                lines.append(f"- [ ] {item['title']}")
        else:
            lines.append("- *No items to monitor*")
        
        return "\n".join(lines)
