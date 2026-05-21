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
                    "model": "openai/gpt-4o",
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
            clean_subject = subject
            for prefix in ['RE: [External] Re: ', 'Re: ', 'RE: ', 'FW: ', 'Fwd: ', 'Fw: ']:
                if clean_subject.startswith(prefix):
                    clean_subject = clean_subject[len(prefix):]
                    break
            return clean_subject
            
        try:
            is_reply = any(subject.startswith(prefix) for prefix in ['RE:', 'Re:', 'RE: [External]', 'FW:', 'Fwd:'])
            
            if is_reply:
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
                    "model": "openai/gpt-4o",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"OpenRouter API response: {result}")
                
                if 'choices' in result and len(result['choices']) > 0:
                    task = result['choices'][0]['message']['content'].strip()
                    logger.info(f"AI generated task: '{task}'")
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
