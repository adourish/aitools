#!/usr/bin/env python3
"""
Gmail Thread Tools - Group and analyze email threads
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class GmailThreadTools:
    """Tools for grouping and analyzing email threads"""
    
    def __init__(self, gmail_tools):
        self.gmail = gmail_tools
    
    def normalize_subject(self, subject: str) -> str:
        """Normalize subject line by removing RE:, FW:, etc."""
        normalized = subject
        
        # Remove common prefixes
        prefixes = ['RE:', 'Re:', 'RE: [External]', 'Re: [External]', 'FW:', 'Fwd:', 'Fw:']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def group_emails_by_thread(self, emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group emails into threads based on normalized subject
        
        Returns:
            Dict mapping normalized subject to list of emails in that thread
        """
        threads = defaultdict(list)
        
        for email in emails:
            subject = email.get('subject', 'No Subject')
            normalized = self.normalize_subject(subject)
            threads[normalized].append(email)
        
        # Sort each thread by date (oldest first)
        for thread_subject in threads:
            threads[thread_subject].sort(key=lambda e: e.get('date', ''))
        
        logger.info(f"Grouped {len(emails)} emails into {len(threads)} threads")
        
        return dict(threads)
    
    async def get_thread_emails(self, days: int = 14) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get emails from last N days and group them into threads
        
        Args:
            days: Number of days to look back (default 14 for 2 weeks)
            
        Returns:
            Dict mapping thread subject to list of emails in chronological order
        """
        logger.info(f"Fetching emails from last {days} days for thread analysis...")
        
        # Get all emails from the period
        emails = await self.gmail.get_urgent_emails(days=days)
        
        # Group into threads
        threads = self.group_emails_by_thread(emails)
        
        # Log thread statistics
        thread_sizes = [len(emails) for emails in threads.values()]
        if thread_sizes:
            logger.info(f"Thread statistics:")
            logger.info(f"  - Total threads: {len(threads)}")
            logger.info(f"  - Avg emails per thread: {sum(thread_sizes) / len(thread_sizes):.1f}")
            logger.info(f"  - Largest thread: {max(thread_sizes)} emails")
            logger.info(f"  - Single email threads: {sum(1 for s in thread_sizes if s == 1)}")
            logger.info(f"  - Multi-email threads: {sum(1 for s in thread_sizes if s > 1)}")
        
        return threads
    
    def get_priority_threads(self, threads: Dict[str, List[Dict[str, Any]]], max_threads: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter to most important threads based on:
        - Whitelisted senders
        - Priority keywords
        - Recent activity
        - Thread length (more emails = more important conversation)
        
        Args:
            threads: All email threads
            max_threads: Maximum number of threads to return
            
        Returns:
            Dict of priority threads
        """
        # Subjects/senders to skip entirely before scoring
        SKIP_SUBJECT_PATTERNS = [
            'onedrive', 'one drive',
            'sign up', 'signup', 'sign-up',
            'unsubscribe', 'newsletter',
        ]

        scored_threads = []
        now = datetime.now()

        for subject, emails in threads.items():
            # Skip noise threads before scoring
            subject_lower = subject.lower()
            body_lower = (emails[-1].get('body', '') or '')[:300].lower()
            if any(p in subject_lower or p in body_lower for p in SKIP_SUBJECT_PATTERNS):
                logger.info(f"Skipped noise thread: {subject[:60]}")
                continue

            score = 0
            latest_email = emails[-1]
            sender = latest_email.get('from', '')

            # Whitelisted sender = high priority
            if self.gmail.is_whitelisted_sender(sender):
                score += 100

            # Check for priority content in any email
            for email in emails:
                if self.gmail.has_priority_content(
                    email.get('subject', ''),
                    email.get('body', '')
                ):
                    score += 50
                    break

            # Multi-email threads are more important (active conversation), cap at 30
            if len(emails) > 1:
                score += min(len(emails) * 10, 30)

            # Recency decay: subtract 2 points per day old (based on latest email)
            latest_date_str = latest_email.get('date', '')
            if latest_date_str:
                try:
                    # Handle various date formats
                    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %z'):
                        try:
                            latest_dt = datetime.strptime(latest_date_str.strip(), fmt)
                            if latest_dt.tzinfo:
                                latest_dt = latest_dt.replace(tzinfo=None)
                            days_old = (now - latest_dt).days
                            score -= days_old * 2
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass  # Can't parse date, skip decay

            # Check for action keywords
            text = (latest_email.get('subject', '') + ' ' + latest_email.get('body', '')).lower()
            if any(word in text for word in ['urgent', 'asap', 'today', 'deadline', 'action required',
                                              'past due', 'overdue', 'expires', 'expiring']):
                score += 30

            scored_threads.append((score, subject, emails))
        
        # Sort by score descending
        scored_threads.sort(reverse=True, key=lambda x: x[0])
        
        # Return top threads
        priority_threads = {}
        for score, subject, emails in scored_threads[:max_threads]:
            priority_threads[subject] = emails
            logger.info(f"Priority thread (score={score}): {subject} ({len(emails)} emails)")

        return priority_threads

    def _extract_sender_domain(self, from_string: str) -> str:
        """Extract sender domain from a From header string like 'Name <email@domain.com>'"""
        match = re.search(r'<([^>]+)>', from_string)
        email = match.group(1) if match else from_string
        if '@' in email:
            return email.split('@')[1].lower().strip()
        return from_string.lower().strip()

    def _extract_sender_label(self, from_string: str) -> str:
        """Extract a readable sender name from a From header string"""
        # Try to get display name first
        match = re.match(r'^"?([^"<]+)"?\s*<', from_string)
        if match:
            return match.group(1).strip()
        # Fall back to domain
        return self._extract_sender_domain(from_string)

    def _subject_similarity(self, a: str, b: str) -> float:
        """Calculate word-overlap similarity between two subjects (0.0 to 1.0)."""
        stop_words = {'the', 'a', 'an', 'to', 'for', 'and', 'or', 'is', 'in', 'on', 'at',
                      'of', 'your', 'this', 'that', 're', 'fwd', 'fw'}
        words_a = set(a.lower().split()) - stop_words
        words_b = set(b.lower().split()) - stop_words
        if not words_a or not words_b:
            return 0.0
        overlap = words_a & words_b
        smaller = min(len(words_a), len(words_b))
        return len(overlap) / smaller if smaller > 0 else 0.0

    def cluster_threads_by_sender(self, priority_threads: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Cluster related threads from the same sender into super-threads.

        Only merges threads from the same sender domain when their subjects
        have >= 40% word overlap (i.e. they're actually about the same topic).
        Unrelated threads from the same sender stay separate.

        Args:
            priority_threads: Dict of subject -> emails from get_priority_threads()

        Returns:
            Dict of (possibly combined) subject -> combined email list
        """
        SIMILARITY_THRESHOLD = 0.4

        # Group threads by sender domain
        sender_groups = defaultdict(list)
        for subject, emails in priority_threads.items():
            latest_from = emails[-1].get('from', '')
            domain = self._extract_sender_domain(latest_from)
            sender_groups[domain].append((subject, emails))

        clustered = {}

        for domain, thread_list in sender_groups.items():
            if len(thread_list) == 1:
                subject, emails = thread_list[0]
                clustered[subject] = emails
                continue

            # Build similarity clusters — only merge threads with overlapping subjects
            used = set()
            for i, (subj_a, emails_a) in enumerate(thread_list):
                if i in used:
                    continue
                group_subjects = [subj_a]
                group_emails = list(emails_a)
                used.add(i)

                for j, (subj_b, emails_b) in enumerate(thread_list):
                    if j in used:
                        continue
                    # Check if any subject in the group is similar to subj_b
                    if any(self._subject_similarity(s, subj_b) >= SIMILARITY_THRESHOLD for s in group_subjects):
                        group_subjects.append(subj_b)
                        group_emails.extend(emails_b)
                        used.add(j)

                if len(group_subjects) == 1:
                    # No merge — pass through unchanged
                    clustered[subj_a] = emails_a
                else:
                    # Merge similar threads
                    group_emails.sort(key=lambda e: e.get('date', ''))
                    sender_label = self._extract_sender_label(group_emails[-1].get('from', domain))
                    # Limit combined subject length
                    short_subjects = [s[:50] for s in group_subjects]
                    combined_subject = f"[{sender_label}] {' / '.join(short_subjects)}"
                    if len(combined_subject) > 200:
                        combined_subject = combined_subject[:197] + "..."
                    clustered[combined_subject] = group_emails
                    logger.info(f"Clustered {len(group_subjects)} similar threads from {domain}: {combined_subject[:80]}")

        if len(clustered) < len(priority_threads):
            logger.info(f"Clustering reduced {len(priority_threads)} threads to {len(clustered)} groups")

        return clustered
