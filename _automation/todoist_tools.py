#!/usr/bin/env python3
"""
Todoist tools for MCP Server
"""

import logging
from typing import List, Dict, Any, Optional
import requests
import os
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class TodoistTools:
    """Todoist operations for MCP server"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.base_url = "https://api.todoist.com/api/v1"
        # OpenRouter API key will be loaded from auth_manager when needed
        self.openrouter_key = None
        self._openrouter_key_loaded = False
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token"""
        token = await self.auth_manager.get_todoist_token()
        return {'Authorization': f'Bearer {token}'}
    
    async def _ensure_openrouter_key(self) -> bool:
        """Ensure OpenRouter API key is loaded from auth_manager"""
        if not self._openrouter_key_loaded:
            self.openrouter_key = await self.auth_manager.get_openrouter_key()
            self._openrouter_key_loaded = True
        return self.openrouter_key is not None
    
    async def _generate_thread_context(self, subject: str, sender: str, preview: str) -> str:
        """Generate a summary of what's happening in an email thread"""
        if not await self._ensure_openrouter_key():
            return ""
            
        try:
            prompt = f"""Analyze this email thread and provide a brief summary (2-3 sentences) of what's happening in the conversation.

Subject: {subject}
From: {sender}
Email Content: {preview[:800]}

Explain:
1. What is this conversation about?
2. What has happened so far in the thread?
3. What needs to happen next?

Keep it concise and actionable. Focus on the key points.

Summary:"""

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://adourish.github.io",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"OpenRouter thread context response: {result}")
                
                if 'choices' in result and len(result['choices']) > 0:
                    summary = result['choices'][0]['message']['content'].strip()
                    logger.info(f"AI generated thread context: '{summary}'")
                    return summary
                else:
                    logger.warning(f"OpenRouter response missing choices: {result}")
                    return ""
            else:
                logger.warning(f"OpenRouter API error: {response.status_code} - {response.text}")
                return ""
            
        except Exception as e:
            logger.warning(f"Thread context generation failed: {e}")
            return ""
    
    async def _generate_task_summary(self, subject: str, sender: str, preview: str) -> str:
        """Use AI to generate actionable task from email content"""
        if not await self._ensure_openrouter_key():
            # Fallback to cleaned subject
            clean_subject = subject
            for prefix in ['RE: [External] Re: ', 'Re: ', 'RE: ', 'FW: ', 'Fwd: ', 'Fw: ']:
                if clean_subject.startswith(prefix):
                    clean_subject = clean_subject[len(prefix):]
                    break
            return clean_subject
            
        try:
            # Detect if this is part of an email chain
            is_reply = any(subject.startswith(prefix) for prefix in ['RE:', 'Re:', 'RE: [External]', 'FW:', 'Fwd:'])
            
            if is_reply:
                # For email chains, analyze the thread context
                prompt = f"""Analyze this email thread and create a clear, actionable task (max 60 characters).

Subject: {subject}
From: {sender}
Email Content: {preview[:800]}

This is part of an email conversation. Based on the content:
1. What is the main topic/issue being discussed?
2. What action do I need to take next?

Create a task that captures both the context and the required action.
Examples:
- "Respond to teacher: Max needs extra help"
- "Follow up on refund - they're reviewing case"
- "Confirm virtual meeting with Lisa Prescott"
- "Reply to property manager about tree work"

Task:"""
            else:
                # For single emails, simpler prompt
                prompt = f"""Analyze this email and create a single, clear, actionable task (max 60 characters).

Subject: {subject}
From: {sender}
Preview: {preview[:500]}

Create a task that clearly states what action needs to be taken. Be specific and concise.
Examples:
- "Respond to teacher about Max's progress"
- "Review and approve summer camp registration"
- "Call Aggressor Adventures about refund"
- "Confirm meeting time with Lisa Prescott"

Task:"""

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://adourish.github.io",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"OpenRouter API response: {result}")
                
                # Extract task from response
                if 'choices' in result and len(result['choices']) > 0:
                    task = result['choices'][0]['message']['content'].strip()
                    logger.info(f"AI generated task: '{task}'")
                    # Remove quotes if AI added them
                    task = task.strip('"').strip("'")
                    return task
                else:
                    logger.warning(f"OpenRouter response missing choices: {result}")
                    raise Exception("No choices in API response")
            else:
                logger.warning(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"API returned {response.status_code}")
            
        except Exception as e:
            logger.warning(f"AI task generation failed: {e}, using subject instead")
            # Fallback to cleaned subject
            clean_subject = subject
            for prefix in ['RE: [External] Re: ', 'Re: ', 'RE: ', 'FW: ', 'Fwd: ', 'Fw: ']:
                if clean_subject.startswith(prefix):
                    clean_subject = clean_subject[len(prefix):]
                    break
            return clean_subject
    
    async def get_tasks(self, filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks from Todoist"""
        headers = await self._get_headers()
        
        try:
            url = f"{self.base_url}/tasks"
            if filter:
                url += f"?filter={filter}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            tasks = response.json()
            tasks = tasks.get('results', []) if isinstance(tasks, dict) else tasks
            
            # Filter out auto-created daily plan tasks
            filtered_tasks = []
            for task in tasks:
                content = task.get('content', '')
                if not (content.startswith('🎯 TODAY:') or content.startswith('⏰ SOON:') or content.startswith('📋 Daily Plan -')):
                    filtered_tasks.append(task)
            
            logger.info(f"Retrieved {len(filtered_tasks)} tasks from Todoist")
            return filtered_tasks
        
        except Exception as e:
            logger.error(f"Error getting Todoist tasks: {e}")
            raise
    
    async def create_task(
        self,
        content: str,
        description: Optional[str] = None,
        priority: int = 1,
        due_string: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new task in Todoist"""
        headers = await self._get_headers()
        
        try:
            task_data = {'content': content}
            
            if description:
                task_data['description'] = description
            if priority:
                task_data['priority'] = priority
            if due_string:
                task_data['due_string'] = due_string
            if labels:
                task_data['labels'] = labels
            
            response = requests.post(
                f"{self.base_url}/tasks",
                headers=headers,
                json=task_data
            )
            response.raise_for_status()
            
            task = response.json()
            logger.info(f"Created task: {content}")
            return task
        
        except Exception as e:
            logger.error(f"Error creating Todoist task: {e}")
            raise
    
    async def update_task(
        self,
        task_id: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update an existing task"""
        headers = await self._get_headers()
        
        try:
            update_data = {}
            if content:
                update_data['content'] = content
            if description:
                update_data['description'] = description
            if priority:
                update_data['priority'] = priority
            
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers,
                json=update_data
            )
            response.raise_for_status()
            
            logger.info(f"Updated task: {task_id}")
            return response.json() if response.text else {"success": True}
        
        except Exception as e:
            logger.error(f"Error updating Todoist task: {e}")
            raise
    
    async def complete_task(self, task_id: str) -> bool:
        """Mark a task as complete"""
        headers = await self._get_headers()
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/close",
                headers=headers
            )
            response.raise_for_status()
            
            logger.info(f"Completed task: {task_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error completing Todoist task: {e}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        headers = await self._get_headers()

        try:
            response = requests.delete(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers
            )
            response.raise_for_status()

            logger.info(f"Deleted task: {task_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting Todoist task: {e}")
            raise

    async def flush_old_daily_plan_tasks(self) -> int:
        """Comprehensively delete all old daily plan tasks (all formats)"""
        headers = await self._get_headers()
        deleted_count = 0

        try:
            all_tasks = await self.get_tasks()

            # Patterns to identify daily plan tasks
            daily_plan_patterns = [
                'daily-plan',  # Label
                '📋',  # Emoji prefix
                '🎯 TODAY:',
                '⏰ SOON:',
                '🎯 ',
                '🔴',  # Priority colors used in old format
                '⚠️',
                'ℹ️',
            ]

            descriptions_containing = [
                'Daily Planner',
                'Source: Email',
                'From:',  # Email attribution in description
                'Calendar event',
            ]

            for task in all_tasks:
                content = task.get('content', '')
                labels = task.get('labels', [])
                description = task.get('description', '')

                # Check if task should be deleted
                should_delete = False

                # Check labels
                if 'daily-plan' in labels:
                    should_delete = True

                # Check content patterns
                if not should_delete:
                    for pattern in daily_plan_patterns:
                        if pattern in content:
                            should_delete = True
                            break

                # Check description patterns
                if not should_delete:
                    for pattern in descriptions_containing:
                        if pattern in description:
                            should_delete = True
                            break

                # Delete if matched
                if should_delete:
                    try:
                        await self.delete_task(task['id'])
                        deleted_count += 1
                        logger.info(f"Flushed old task: {content[:60]}")
                    except Exception as e:
                        logger.warning(f"Failed to delete task {task['id']}: {e}")

            logger.info(f"✓ Flushed {deleted_count} old daily plan tasks")
            return deleted_count

        except Exception as e:
            logger.error(f"Error flushing old daily plan tasks: {e}")
            raise

    async def create_daily_plan_tasks(self, do_now_items: List[Dict[str, Any]], do_soon_items: List[Dict[str, Any]]) -> bool:
        """Create individual Todoist tasks for DakBoard (kill and fill approach)"""
        from datetime import datetime
        
        try:
            headers = await self._get_headers()
            
            # Get all existing tasks
            response = requests.get(f"{self.base_url}/tasks", headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch tasks: {response.status_code}")
                return False
            
            tasks = response.json()
            tasks = tasks.get('results', []) if isinstance(tasks, dict) else tasks
            
            # Delete ALL old daily plan tasks (kill and fill)
            deleted_count = 0
            for task in tasks:
                content = task.get('content', '')
                if content.startswith('📋 Daily Plan -') or content.startswith('🎯 TODAY:') or content.startswith('⏰ SOON:'):
                    await self.delete_task(task['id'])
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old daily plan tasks")
            
            # Deduplicate and filter DO NOW items
            seen_subjects = set()
            filtered_do_now = []
            
            for item in do_now_items:
                title = item['title']
                source = item.get('source', '')
                
                # Skip file organization items
                if 'file' in title.lower() and 'inbox' in title.lower():
                    continue
                
                # Deduplicate email threads (RE:, Re:, FW:, Fwd:)
                clean_title = title
                for prefix in ['RE: [External] Re: ', 'Re: ', 'RE: ', 'FW: ', 'Fwd: ', 'Fw: ']:
                    if clean_title.startswith(prefix):
                        clean_title = clean_title[len(prefix):]
                
                # Skip if we've seen this subject already
                if clean_title.lower() in seen_subjects:
                    continue
                
                seen_subjects.add(clean_title.lower())
                filtered_do_now.append(item)
            
            # Create tasks for top 5 filtered DO NOW items (DakBoard visible)
            created_count = 0
            for item in filtered_do_now[:5]:
                title = item['title']
                due = item.get('due', 'today')
                time_info = f" at {item['time']}" if item.get('time') else ''
                source = item.get('source', 'Unknown')
                
                # Use existing AI summary if available, otherwise use title
                if source == 'Email' and item.get('ai_summary'):
                    # Build detailed task title for DakBoard visibility
                    action_task = item['ai_summary']
                    sender_name = item.get('from', '').split('<')[0].strip() if item.get('from') else 'Unknown'
                    
                    # Add thread context snippet if available (first sentence)
                    context_snippet = ""
                    if item.get('thread_context'):
                        thread_context = item['thread_context']
                        # Get first sentence or first 100 chars
                        first_sentence = thread_context.split('.')[0][:100]
                        if first_sentence:
                            context_snippet = f" - {first_sentence}"
                    
                    # Create detailed title: Action | From | Context
                    task_title = f"🎯 {action_task} (from {sender_name}){context_snippet}{time_info}"
                    # Limit to 250 chars for readability
                    if len(task_title) > 250:
                        task_title = task_title[:247] + "..."
                else:
                    # For non-email items, use clean title
                    clean_title = title
                    for prefix in ['RE: [External] Re: ', 'Re: ', 'RE: ', 'FW: ', 'Fwd: ', 'Fw: ']:
                        if clean_title.startswith(prefix):
                            clean_title = clean_title[len(prefix):]
                            break
                    task_title = f"🎯 TODAY: {clean_title}{time_info}"
                    thread_context = item.get('thread_context', '')
                
                # Build detailed description with context
                description_parts = [f"**Source:** {source}"]
                
                # Add sender info for emails
                if item.get('from'):
                    description_parts.append(f"**From:** {item['from']}")
                
                # Add thread context if this is an email chain
                if thread_context:
                    description_parts.append(f"\n**Thread Summary:**\n{thread_context}")
                
                # Add original subject if we generated a summary
                if source == 'Email' and item.get('preview'):
                    description_parts.append(f"\n**Subject:** {title}")
                
                # Add email preview/body snippet
                if item.get('preview'):
                    preview = item['preview'][:300]  # First 300 chars
                    description_parts.append(f"\n**Preview:**\n{preview}")
                
                # Add date info if available
                if item.get('date'):
                    description_parts.append(f"\n**Received:** {item['date']}")
                
                # Add email ID for reference
                if item.get('email_id'):
                    description_parts.append(f"\n**Email ID:** {item['email_id']}")
                
                description_parts.append(f"\n*Generated: {datetime.now().strftime('%I:%M %p')}*")
                
                await self.create_task(
                    content=task_title,
                    due_string=due if due != 'today' else 'today',
                    priority=4,  # High priority (red)
                    description="\n".join(description_parts)
                )
                created_count += 1
            
            # Create individual tasks for DO SOON items (more actionable)
            if do_soon_items:
                for item in do_soon_items[:3]:  # Top 3 upcoming items
                    title = item['title']
                    due_date = item.get('due', '')
                    source = item.get('source', 'Unknown')
                    
                    # Format due date for display
                    due_display = ''
                    if due_date:
                        try:
                            from datetime import datetime as dt
                            due_dt = dt.strptime(due_date, '%Y-%m-%d')
                            due_display = f" ({due_dt.strftime('%b %d')})"
                        except:
                            pass
                    
                    task_title = f"⏰ SOON: {title[:70]}{due_display}"
                    
                    try:
                        await self.create_task(
                            content=task_title,
                            due_string=due_date if due_date else 'next week',
                            priority=2,  # Medium priority (yellow)
                            description=f"Source: {source}\nFrom: Daily Planner\nGenerated: {datetime.now().strftime('%I:%M %p')}"
                        )
                        created_count += 1
                    except Exception as e:
                        logger.warning(f"Could not create DO SOON task for {title}: {e}")
            
            logger.info(f"Created {created_count} Todoist tasks for DakBoard")
            return True
        
        except Exception as e:
            logger.error(f"Error creating daily plan tasks: {e}")
            return False
