#!/usr/bin/env python3
"""
Comprehensive Email Thread Analyzer
Analyzes email threads over 2 weeks to understand context, outcomes, and action items
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
import requests

logger = logging.getLogger(__name__)

class ComprehensiveAnalyzer:
    """Analyzes email threads, tasks, and calendar to provide comprehensive context"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.openrouter_key = None
        self._openrouter_key_loaded = False
    
    async def _ensure_openrouter_key(self) -> bool:
        """Ensure OpenRouter API key is loaded from auth_manager"""
        if not self._openrouter_key_loaded:
            self.openrouter_key = await self.auth_manager.get_openrouter_key()
            self._openrouter_key_loaded = True
        return self.openrouter_key is not None
    
    async def analyze_email_thread(self, emails: List[Dict[str, Any]], thread_subject: str, is_cluster: bool = False) -> Dict[str, Any]:
        """
        Analyze a complete email thread to understand context, outcomes, and action items
        
        Args:
            emails: List of emails in the thread (chronologically ordered)
            thread_subject: The subject line of the thread
            
        Returns:
            Dict with analysis including:
            - summary: What this conversation is about
            - outcome: What has been resolved or decided
            - action_items: What needs to be done
            - follow_up_needed: Whether follow-up is required
            - priority: Urgency level
            - context: Full context for understanding
        """
        if not await self._ensure_openrouter_key():
            return self._fallback_analysis(emails, thread_subject)
        
        # Build comprehensive thread context
        thread_text = self._build_thread_context(emails)
        
        # Create analysis prompt
        cluster_instruction = ""
        if is_cluster:
            cluster_instruction = """
IMPORTANT: These emails are from the SAME sender about RELATED topics (possibly the same appointment, transaction, or request).
Consolidate into ONE set of non-redundant action items.
Do NOT create duplicate or overlapping actions — if multiple emails reference the same form, payment, or task, produce a SINGLE action for it.

"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""Analyze this email thread. Today is {today_str}.
{cluster_instruction}
THREAD SUBJECT: {thread_subject}

THREAD CONTENT:
{thread_text}

RULES:
- If the DEADLINE has already passed (before {today_str}), set ACTION ITEMS to "None - deadline passed [date]" and PRIORITY to "low". Do NOT suggest actions for expired events.
- If there is NO specific action I must personally take, set ACTION ITEMS to "None - informational only" and PRIORITY to "low".
- Newsletters, FYI updates, confirmations, status reports = "None - informational only"
- Someone else handling it = "None - waiting on [person]"
- I already replied/acted = "None - already handled"
- "Review", "consider", "be aware of", "stay informed" are NOT action items

ACTION ITEMS must be specific and concrete:
  GOOD: "Pay $55 field trip fee by May 5 via MySchoolBucks"
  BAD: "Review the situation" / "Stay informed" / "Monitor updates"

DEADLINE: Extract the exact date as YYYY-MM-DD. If no date mentioned, write "None".

CONTEXT: Write ONE short, specific sentence with key details (who, how much, what date). Not generic filler.
  GOOD: "Mount Vernon field trip May 12. $65 if chaperoning."
  GOOD: "No school Apr 21 — need childcare plan."
  BAD: "This is an educational opportunity for students."
  BAD: "This matters as it involves the school schedule."

Respond in EXACTLY this format:
SUMMARY: [1 sentence — what happened]
OUTCOME: [1 sentence — what's resolved, or "Pending - [what's needed]"]
ACTION ITEMS: [specific actions with dollar amounts/dates, or "None - reason"]
DEADLINE: [YYYY-MM-DD, or "None"]
FOLLOW_UP: [Yes/No - if yes, what specifically to check and by when]
PRIORITY: [High/Medium/Low - reason]
CONTEXT: [1 specific sentence with key details]

Priority levels:
- High = explicit deadline within 7 days OR someone blocked on me OR money/registration at risk
- Medium = action needed but deadline is 7-30 days out
- Low = informational, already handled, deadline passed, or no action needed"""
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://adourish.github.io",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-sonnet-4-5",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 700 if is_cluster else 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    analysis_text = result['choices'][0]['message']['content'].strip()
                    return self._parse_analysis(analysis_text, emails, thread_subject)
                else:
                    logger.warning(f"OpenRouter response missing choices: {result}")
                    return self._fallback_analysis(emails, thread_subject)
            else:
                logger.warning(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._fallback_analysis(emails, thread_subject)
                
        except Exception as e:
            logger.warning(f"Thread analysis failed: {e}")
            return self._fallback_analysis(emails, thread_subject)
    
    def _build_thread_context(self, emails: List[Dict[str, Any]]) -> str:
        """Build chronological thread context from emails"""
        thread_lines = []
        
        for i, email in enumerate(emails, 1):
            sender = email.get('from', 'Unknown')
            date = email.get('date', 'Unknown date')
            body = email.get('body', email.get('preview', ''))[:800]  # First 800 chars
            
            thread_lines.append(f"--- Email {i} ---")
            thread_lines.append(f"From: {sender}")
            thread_lines.append(f"Date: {date}")
            thread_lines.append(f"Content: {body}")
            thread_lines.append("")
        
        return "\n".join(thread_lines)
    
    def _parse_analysis(self, analysis_text: str, emails: List[Dict[str, Any]], thread_subject: str) -> Dict[str, Any]:
        """Parse the AI analysis response into structured data"""
        lines = analysis_text.split('\n')
        analysis = {
            'summary': '',
            'outcome': '',
            'action_items': [],
            'deadline': None,
            'follow_up_needed': False,
            'follow_up_reason': '',
            'priority': 'medium',
            'priority_reason': '',
            'context': '',
            'thread_subject': thread_subject,
            'email_count': len(emails),
            'latest_sender': emails[-1].get('from', 'Unknown') if emails else 'Unknown',
            'latest_date': emails[-1].get('date', 'Unknown') if emails else 'Unknown'
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                analysis['summary'] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('OUTCOME:'):
                current_section = 'outcome'
                analysis['outcome'] = line.replace('OUTCOME:', '').strip()
            elif line.startswith('ACTION ITEMS:'):
                current_section = 'action_items'
                action_text = line.replace('ACTION ITEMS:', '').strip()
                if action_text and action_text.lower() != 'none':
                    analysis['action_items'].append(action_text)
            elif line.startswith('DEADLINE:'):
                current_section = 'deadline'
                deadline_text = line.replace('DEADLINE:', '').strip()
                # Extract YYYY-MM-DD date if present
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', deadline_text)
                if date_match:
                    analysis['deadline'] = date_match.group(1)
            elif line.startswith('FOLLOW_UP:') or line.startswith('FOLLOW-UP:'):
                current_section = 'follow_up'
                follow_text = line.replace('FOLLOW_UP:', '').replace('FOLLOW-UP:', '').strip()
                analysis['follow_up_needed'] = follow_text.lower().startswith('yes')
                analysis['follow_up_reason'] = follow_text
            elif line.startswith('PRIORITY:'):
                current_section = 'priority'
                priority_text = line.replace('PRIORITY:', '').strip()
                if 'high' in priority_text.lower():
                    analysis['priority'] = 'high'
                elif 'low' in priority_text.lower():
                    analysis['priority'] = 'low'
                else:
                    analysis['priority'] = 'medium'
                analysis['priority_reason'] = priority_text
            elif line.startswith('CONTEXT:'):
                current_section = 'context'
                analysis['context'] = line.replace('CONTEXT:', '').strip()
            elif current_section == 'action_items' and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                item = line.lstrip('-•* ').strip()
                if item and item.lower() != 'none':
                    analysis['action_items'].append(item)
            elif current_section and line and not line.startswith(('SUMMARY', 'OUTCOME', 'ACTION', 'FOLLOW', 'PRIORITY', 'CONTEXT', 'DEADLINE')):
                if current_section == 'summary':
                    analysis['summary'] += ' ' + line
                elif current_section == 'outcome':
                    analysis['outcome'] += ' ' + line
                elif current_section == 'context':
                    analysis['context'] += ' ' + line

        return analysis
    
    def _fallback_analysis(self, emails: List[Dict[str, Any]], thread_subject: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        latest_email = emails[-1] if emails else {}
        
        return {
            'summary': f"Email thread: {thread_subject}",
            'outcome': "Unknown - AI analysis unavailable",
            'action_items': ["Review email thread and determine action needed"],
            'follow_up_needed': True,
            'follow_up_reason': "Manual review required",
            'priority': 'medium',
            'priority_reason': 'Default priority - manual review needed',
            'context': f"{len(emails)} emails in thread",
            'thread_subject': thread_subject,
            'email_count': len(emails),
            'latest_sender': latest_email.get('from', 'Unknown'),
            'latest_date': latest_email.get('date', 'Unknown')
        }
    
    def _normalize_action(self, action: str) -> str:
        """Normalize an action string for comparison"""
        import string
        text = action.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return ' '.join(text.split())

    def _actions_overlap(self, a: str, b: str) -> bool:
        """Check if two normalized action strings are semantically similar"""
        # Substring check
        if a in b or b in a:
            return True
        # Word overlap check
        words_a = set(a.split())
        words_b = set(b.split())
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'to', 'for', 'and', 'or', 'is', 'in', 'on', 'at', 'of', 'your', 'this', 'that', 'it', 'from', 'with', 'by'}
        words_a -= stop_words
        words_b -= stop_words
        if not words_a or not words_b:
            return False
        overlap = words_a & words_b
        smaller = min(len(words_a), len(words_b))
        return len(overlap) / smaller >= 0.6 if smaller > 0 else False

    def deduplicate_action_items(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate action items across different thread analyses.
        When duplicates are found, keep the one from the higher-priority analysis.

        Args:
            analyses: List of analysis dicts with 'action_items' and 'priority'

        Returns:
            Cleaned list of analyses with duplicate actions removed
        """
        priority_order = {'high': 0, 'medium': 1, 'low': 2}

        # Build a global list of (normalized_action, priority, analysis_idx, action_idx)
        all_actions = []
        for ai, analysis in enumerate(analyses):
            for ji, action in enumerate(analysis.get('action_items', [])):
                norm = self._normalize_action(action)
                pri = priority_order.get(analysis.get('priority', 'low'), 2)
                all_actions.append((norm, pri, ai, ji))

        # Find duplicates: for each pair across different analyses
        to_remove = set()  # (analysis_idx, action_idx) to remove
        for i in range(len(all_actions)):
            for j in range(i + 1, len(all_actions)):
                norm_i, pri_i, ai_i, ji_i = all_actions[i]
                norm_j, pri_j, ai_j, ji_j = all_actions[j]
                if ai_i == ai_j:
                    continue  # Same analysis — skip
                if self._actions_overlap(norm_i, norm_j):
                    # Remove the lower-priority one (higher number = lower priority)
                    if pri_i >= pri_j:
                        to_remove.add((ai_i, ji_i))
                    else:
                        to_remove.add((ai_j, ji_j))

        if to_remove:
            logger.info(f"Dedup: removing {len(to_remove)} duplicate action items across analyses")

        # Rebuild analyses with duplicates removed
        result = []
        for ai, analysis in enumerate(analyses):
            cleaned_actions = [
                action for ji, action in enumerate(analysis.get('action_items', []))
                if (ai, ji) not in to_remove
            ]
            cleaned = dict(analysis)
            cleaned['action_items'] = cleaned_actions
            result.append(cleaned)

        return result

    async def create_comprehensive_daily_summary(
        self,
        email_analyses: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> str:
        """
        Create clean summary with top 3 actions for DakBoard title
        
        Returns:
            Clean string with top 3 action items only
        """
        actions = []
        
        # Collect all actions with priority
        all_items = []
        
        # High priority first
        for analysis in email_analyses:
            if analysis.get('action_items') and analysis['priority'] == 'high':
                for action in analysis['action_items'][:1]:  # First action only
                    all_items.append((action, 'high'))
        
        # Medium priority next
        for analysis in email_analyses:
            if analysis.get('action_items') and analysis['priority'] == 'medium':
                for action in analysis['action_items'][:1]:
                    all_items.append((action, 'medium'))
        
        # Take top 3 actions
        for action, priority in all_items[:3]:
            # Shorten if too long
            if len(action) > 70:
                action = action[:67] + "..."
            actions.append(f"• {action}")
        
        # If no actions, show count
        if not actions:
            if email_analyses:
                return f"{len(email_analyses)} threads to review"
            else:
                return "No urgent actions"
        
        return " | ".join(actions)
