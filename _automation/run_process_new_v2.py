#!/usr/bin/env python3
"""
Comprehensive Process New Workflow - V2
Analyzes email threads over 2 weeks with full context and creates single consolidated daily plan
"""

import asyncio
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from auth_manager import AuthManager
from gmail_tools import GmailTools
from gmail_thread_tools import GmailThreadTools
from comprehensive_analyzer import ComprehensiveAnalyzer
from todoist_tools import TodoistTools
from calendar_tools import CalendarTools
from amplenote_tools import AmplenoteTools

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_new_comprehensive():
    """Execute comprehensive process new workflow with 2-week thread analysis."""
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE PROCESS NEW WORKFLOW - V2")
    logger.info("Analyzing email threads over 30 days with full context")
    logger.info("=" * 80)

    # Initialize tools
    auth_manager = AuthManager()
    gmail = GmailTools(auth_manager)
    thread_tools = GmailThreadTools(gmail)
    analyzer = ComprehensiveAnalyzer(auth_manager)
    todoist = TodoistTools(auth_manager)
    calendar = CalendarTools(auth_manager)
    amplenote = AmplenoteTools(auth_manager)
    
    # Step 1: Fetch email threads from last 2 weeks
    logger.info("\n📧 STEP 1: Fetching email threads (30 day lookback)...")
    all_threads = await thread_tools.get_thread_emails(days=30)
    logger.info(f"   Found {len(all_threads)} total threads")
    
    # Step 2: Filter to priority threads
    logger.info("\n🎯 STEP 2: Identifying priority threads...")
    priority_threads = thread_tools.get_priority_threads(all_threads, max_threads=15)
    logger.info(f"   Selected {len(priority_threads)} priority threads for analysis")

    # Step 2.5: Cluster related threads by sender
    logger.info("\n🔗 STEP 2.5: Clustering related threads by sender...")
    clustered_threads = thread_tools.cluster_threads_by_sender(priority_threads)
    logger.info(f"   Clustered {len(priority_threads)} threads into {len(clustered_threads)} groups")

    # Step 3: Analyze each priority thread comprehensively
    logger.info("\n🔍 STEP 3: Analyzing threads comprehensively...")
    thread_analyses = []

    for i, (subject, emails) in enumerate(clustered_threads.items(), 1):
        is_cluster = subject.startswith('[')  # Clustered subjects start with [SenderName]
        logger.info(f"\n   Analyzing thread {i}/{len(clustered_threads)}: {subject}")
        logger.info(f"      - {len(emails)} emails in {'cluster' if is_cluster else 'thread'}")
        logger.info(f"      - Latest from: {emails[-1].get('from', 'Unknown')}")

        analysis = await analyzer.analyze_email_thread(emails, subject, is_cluster=is_cluster)
        thread_analyses.append(analysis)
        
        # Log key findings
        logger.info(f"      ✓ Priority: {analysis['priority'].upper()}")
        logger.info(f"      ✓ Action items: {len(analysis['action_items'])}")
        logger.info(f"      ✓ Follow-up needed: {'YES' if analysis['follow_up_needed'] else 'NO'}")
        if analysis['action_items']:
            logger.info(f"      ✓ First action: {analysis['action_items'][0][:80]}")
    
    # Step 4: Get tasks and calendar
    logger.info("\n✅ STEP 4: Fetching Todoist tasks...")
    tasks = await todoist.get_tasks()
    today = datetime.now().strftime("%Y-%m-%d")
    today_dt = datetime.now().date()

    # Classify tasks: today, upcoming, stale (>7 days overdue), no-date
    STALE_THRESHOLD_DAYS = 7
    today_tasks = []
    upcoming_tasks = []
    stale_tasks = []
    no_date_tasks = []

    for t in tasks:
        due_info = t.get('due')
        if not due_info or not due_info.get('date'):
            no_date_tasks.append(t)
            continue
        due_date_str = due_info['date']
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            no_date_tasks.append(t)
            continue

        days_overdue = (today_dt - due_date).days

        if days_overdue > STALE_THRESHOLD_DAYS:
            stale_tasks.append(t)
        elif due_date_str == today:
            today_tasks.append(t)
        else:
            upcoming_tasks.append(t)

    logger.info(f"   Found {len(today_tasks)} tasks due today")
    logger.info(f"   Found {len(upcoming_tasks)} upcoming tasks")
    if stale_tasks:
        logger.info(f"   Found {len(stale_tasks)} STALE tasks (>{STALE_THRESHOLD_DAYS} days overdue):")
        for st in stale_tasks:
            logger.info(f"      ⚠️  {st['content']} (due {st['due']['date']})")
    if no_date_tasks:
        logger.info(f"   Found {len(no_date_tasks)} tasks with no due date")
    
    logger.info("\n📅 STEP 5: Fetching calendar events...")
    try:
        events = await calendar.get_events(days_ahead=7)  # Get full week
        tomorrow = (today_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        today_events = [e for e in events if e.get('date') == today]
        tomorrow_events = [e for e in events if e.get('date') == tomorrow]
        logger.info(f"   Found {len(today_events)} events today, {len(tomorrow_events)} tomorrow")
        logger.info(f"   Found {len(events)} events in next 7 days")
    except Exception as e:
        logger.warning(f"   Calendar unavailable (insufficient scopes or auth): {e}")
        events = []
        today_events = []
    
    # Step 5: Create comprehensive summary
    logger.info("\n📝 STEP 6: Creating comprehensive daily summary...")
    comprehensive_summary = await analyzer.create_comprehensive_daily_summary(
        thread_analyses,
        today_tasks,
        today_events
    )
    
    logger.info(f"\n{'=' * 80}")
    logger.info("COMPREHENSIVE DAILY SUMMARY")
    logger.info(f"{'=' * 80}")
    logger.info(f"\n{comprehensive_summary}\n")
    
    # Step 6: Create detailed breakdown for Amplenote
    logger.info("\n📋 STEP 7: Preparing detailed breakdown...")
    
    detailed_breakdown = {
        "summary": comprehensive_summary,
        "generated_at": datetime.now().isoformat(),
        "threads_analyzed": len(thread_analyses),
        "high_priority": [],
        "medium_priority": [],
        "low_priority": [],
        "follow_ups_needed": [],
        "tasks_today": today_tasks,
        "upcoming_tasks": upcoming_tasks,
        "stale_tasks": stale_tasks,
        "no_date_tasks": no_date_tasks,
        "events_today": today_events
    }
    
    # Categorize analyses
    for analysis in thread_analyses:
        item = {
            "subject": analysis['thread_subject'],
            "summary": analysis['summary'],
            "outcome": analysis['outcome'],
            "action_items": analysis['action_items'],
            "deadline": analysis.get('deadline'),
            "follow_up": analysis['follow_up_reason'] if analysis['follow_up_needed'] else None,
            "context": analysis['context'],
            "latest_from": analysis['latest_sender'],
            "email_count": analysis['email_count']
        }
        
        if analysis['priority'] == 'high':
            detailed_breakdown['high_priority'].append(item)
        elif analysis['priority'] == 'medium':
            detailed_breakdown['medium_priority'].append(item)
        else:
            detailed_breakdown['low_priority'].append(item)
        
        if analysis['follow_up_needed']:
            detailed_breakdown['follow_ups_needed'].append(item)
    
    # Log breakdown
    logger.info(f"   🔴 High priority (DO NOW): {len(detailed_breakdown['high_priority'])} threads")
    logger.info(f"   ⚠️  Medium priority (DO SOON): {len(detailed_breakdown['medium_priority'])} threads")
    logger.info(f"   ℹ️  Low priority (monitor): {len(detailed_breakdown['low_priority'])} threads")
    logger.info(f"   📧 Follow-ups needed: {len(detailed_breakdown['follow_ups_needed'])} threads")
    if stale_tasks:
        logger.info(f"   ⏳ Stale tasks (>{STALE_THRESHOLD_DAYS}d overdue): {len(stale_tasks)} — review or reschedule")
    
    # Step 7: Save comprehensive output
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(detailed_breakdown, f, indent=2)
    
    logger.info(f"\n💾 Full analysis saved to: {output_file}")
    
    # Step 7.5: Deduplicate action items across analyses
    logger.info("\n🧹 STEP 7.5: Deduplicating action items...")
    thread_analyses = analyzer.deduplicate_action_items(thread_analyses)

    # Step 7.55: Filter out informational-only and expired threads
    logger.info("\n🧹 STEP 7.55: Filtering out informational-only and expired threads...")
    actionable_analyses = []
    informational_count = 0
    expired_count = 0
    for analysis in thread_analyses:
        actions = analysis.get('action_items', [])

        # Check if deadline has passed — demote to low/informational
        deadline = analysis.get('deadline')
        if deadline and deadline < today:
            days_past = (today_dt - datetime.strptime(deadline, "%Y-%m-%d").date()).days
            analysis['priority'] = 'low'
            analysis['action_items'] = [f"None - deadline passed ({deadline}, {days_past}d ago)"]
            expired_count += 1
            logger.info(f"   Expired (deadline {deadline}): {analysis['thread_subject'][:60]}")

        # Also expire follow-ups that reference past dates
        if analysis.get('follow_up_needed'):
            follow_text = (analysis.get('follow_up_reason') or '').lower()
            import re as _re
            date_match = _re.search(r'(\d{4}-\d{2}-\d{2})', follow_text)
            if not date_match:
                # Try "march 16, 2026" style
                date_match = _re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s*\d{4}', follow_text)
            if date_match:
                try:
                    raw = date_match.group(0).replace(',', '')
                    for fmt in ('%Y-%m-%d', '%B %d %Y'):
                        try:
                            fu_date = datetime.strptime(raw, fmt).date()
                            if fu_date < today_dt:
                                analysis['follow_up_needed'] = False
                                analysis['follow_up_reason'] = ''
                                logger.info(f"   Expired follow-up (date {fu_date}): {analysis['thread_subject'][:50]}")
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

        # Check if all actions are "None" variants or empty
        is_informational = (
            not actions
            or all(
                (a.lower().startswith('none') and 'waiting on' not in a.lower()) or
                'informational' in a.lower() or
                'already handled' in a.lower() or
                'deadline passed' in a.lower()
                for a in analysis.get('action_items', [])
            )
        )
        if is_informational and not analysis.get('follow_up_needed'):
            informational_count += 1
            logger.info(f"   Filtered (informational): {analysis['thread_subject'][:60]}")
        else:
            actionable_analyses.append(analysis)
    logger.info(f"   Kept {len(actionable_analyses)} actionable, filtered {informational_count} informational, {expired_count} expired")
    thread_analyses = actionable_analyses

    # Rebuild detailed_breakdown with deduped + filtered analyses
    detailed_breakdown['high_priority'] = []
    detailed_breakdown['medium_priority'] = []
    detailed_breakdown['low_priority'] = []
    detailed_breakdown['follow_ups_needed'] = []
    for analysis in thread_analyses:
        item = {
            "subject": analysis['thread_subject'],
            "summary": analysis['summary'],
            "outcome": analysis['outcome'],
            "action_items": analysis['action_items'],
            "deadline": analysis.get('deadline'),
            "follow_up": analysis['follow_up_reason'] if analysis['follow_up_needed'] else None,
            "context": analysis['context'],
            "latest_from": analysis['latest_sender'],
            "email_count": analysis['email_count']
        }
        if analysis['priority'] == 'high':
            detailed_breakdown['high_priority'].append(item)
        elif analysis['priority'] == 'medium':
            detailed_breakdown['medium_priority'].append(item)
        else:
            detailed_breakdown['low_priority'].append(item)
        if analysis['follow_up_needed']:
            detailed_breakdown['follow_ups_needed'].append(item)

    # Step 7.56: Cap DO NOW at 5 — overflow high priority items to medium
    MAX_DO_NOW = 5
    if len(detailed_breakdown['high_priority']) > MAX_DO_NOW:
        overflow = detailed_breakdown['high_priority'][MAX_DO_NOW:]
        detailed_breakdown['high_priority'] = detailed_breakdown['high_priority'][:MAX_DO_NOW]
        detailed_breakdown['medium_priority'] = overflow + detailed_breakdown['medium_priority']
        logger.info(f"   Capped DO NOW at {MAX_DO_NOW}, moved {len(overflow)} items to DO SOON")

    # Step 7.6: Cross-reference calendar events with email analyses
    logger.info("\n📅 STEP 7.6: Cross-referencing calendar with email threads...")
    matched_event_indices = set()
    stop_words = {'the', 'a', 'an', 'to', 'for', 'and', 'or', 'is', 'in', 'on', 'at', 'of', 'your', 'this', 'that'}
    all_events_list = today_events + [e for e in events if e.get('date') != today]

    for ei, event in enumerate(all_events_list):
        event_summary = event.get('summary', '')
        event_words = set(event_summary.lower().split()) - stop_words
        if len(event_words) < 2:
            continue
        for analysis in thread_analyses:
            subject_words = set(analysis.get('thread_subject', '').lower().split()) - stop_words
            action_text = ' '.join(analysis.get('action_items', []))
            action_words = set(action_text.lower().split()) - stop_words
            combined_words = subject_words | action_words
            overlap = event_words & combined_words
            if len(overlap) >= 2:
                matched_event_indices.add(ei)
                logger.info(f"   Calendar event '{event_summary}' matched to email thread '{analysis['thread_subject'][:50]}' — skipping calendar task")
                break

    # Step 8: Create individual Todoist tasks for each action
    logger.info("\n📋 STEP 8: Flushing old tasks and creating new ones...")

    try:
        # Comprehensively flush ALL old daily plan tasks (all formats and labels)
        flushed_count = await todoist.flush_old_daily_plan_tasks()
        
        created_count = 0
        seen_actions = set()  # Track normalized actions to prevent duplicates

        def normalize_for_dedup(text):
            import string
            return ' '.join(text.lower().translate(str.maketrans('', '', string.punctuation)).split())

        def build_task(item, priority_level):
            """Build a Todoist task from an analysis item. Returns (title, description, due_date) or None."""
            action_items = item.get('action_items', [])
            follow_up = item.get('follow_up', '') or ''

            if not action_items:
                if follow_up and not follow_up.lower().startswith('none'):
                    action = follow_up
                    for prefix in ('Yes - ', 'yes - ', 'YES - '):
                        if action.startswith(prefix):
                            action = action[len(prefix):]
                            break
                else:
                    return None
            else:
                action = action_items[0]

            # Skip non-actionable items
            action_lower = action.lower()
            if action_lower.startswith('none'):
                if 'waiting on' in action_lower:
                    who = action_lower.split('waiting on', 1)[-1].strip().rstrip('.')
                    subject_short = item.get('subject', '')[:60]
                    action = f"Follow up with {who} re: {subject_short}" if who else f"Follow up re: {subject_short}"
                    action_lower = action.lower()
                else:
                    logger.info(f"   ⏭️  Skipped non-actionable: {action[:60]}")
                    return None
            if any(phrase in action_lower for phrase in ('informational', 'already handled', 'no action', 'fyi only', 'deadline passed')):
                logger.info(f"   ⏭️  Skipped non-actionable: {action[:60]}")
                return None

            norm_action = normalize_for_dedup(action)
            if norm_action in seen_actions:
                logger.info(f"   ⏭️  Skipped duplicate action: {action[:60]}")
                return None
            seen_actions.add(norm_action)

            sender = item.get('latest_from', 'Unknown').split('<')[0].strip()
            context = item.get('context', '')

            # Title: just the action, clean and short
            task_title = action
            if len(task_title) > 120:
                task_title = task_title[:117] + "..."

            # Description: context + sender, concise
            desc_lines = []
            if context and context.lower() != 'fyi only':
                desc_lines.append(context)
            desc_lines.append(f"From: {sender}")
            # Additional actions below the first
            if len(action_items) > 1:
                desc_lines.append("")
                for i, a in enumerate(action_items[1:], 2):
                    desc_lines.append(f"{i}. {a}")

            due_date = item.get('deadline') or 'today'

            return task_title, "\n".join(desc_lines), due_date

        # Create tasks for high priority items
        for item in detailed_breakdown['high_priority']:
            result = build_task(item, 'high')
            if not result:
                continue
            task_title, description, due_date = result
            await todoist.create_task(
                content=task_title,
                description=description,
                priority=4,  # High priority (red)
                due_string=due_date,
                labels=['daily-plan']
            )
            created_count += 1
            logger.info(f"   ✅ Created (due {due_date}): {task_title[:80]}")

        # Create tasks for medium priority items
        for item in detailed_breakdown['medium_priority'][:3]:  # Top 3 medium
            result = build_task(item, 'medium')
            if not result:
                continue
            task_title, description, due_date = result
            await todoist.create_task(
                content=task_title,
                description=description,
                priority=3,  # Medium priority (orange)
                due_string=due_date,
                labels=['daily-plan']
            )
            created_count += 1
            logger.info(f"   ✅ Created (due {due_date}): {task_title[:80]}")

        # Create follow-up reminders for "waiting on" threads (any priority)
        logger.info("\n   Creating follow-up reminders for waiting-on threads...")
        for item in detailed_breakdown['low_priority']:
            actions = item.get('action_items', [])
            has_waiting = any('waiting on' in a.lower() for a in actions)
            if not has_waiting:
                continue
            result = build_task(item, 'low')
            if not result:
                continue
            task_title, description, due_date = result
            await todoist.create_task(
                content=task_title,
                description=description,
                priority=2,  # Low priority (blue)
                due_string=due_date,
                labels=['daily-plan', 'follow-up']
            )
            created_count += 1
            logger.info(f"   ✅ Created follow-up (due {due_date}): {task_title[:80]}")

        # Create tasks for follow_up_needed threads that had no action_items
        logger.info("\n   Creating tasks for follow-up-needed threads...")
        seen_follow_up_subjects = set()
        for item in detailed_breakdown['follow_ups_needed']:
            if item.get('action_items'):
                continue  # Already handled above
            subject_key = item.get('subject', '')[:80]
            if subject_key in seen_follow_up_subjects:
                continue
            seen_follow_up_subjects.add(subject_key)
            result = build_task(item, 'low')
            if not result:
                continue
            task_title, description, due_date = result
            await todoist.create_task(
                content=task_title,
                description=description,
                priority=2,
                due_string=due_date,
                labels=['daily-plan', 'follow-up']
            )
            created_count += 1
            logger.info(f"   ✅ Created follow-up task (due {due_date}): {task_title[:80]}")

        # Create tasks for NON-ROUTINE calendar events
        # Recurring events (regular taekwondo, cleaners, etc.) are skipped
        # unless they contain attention keywords (cancelled, doctor, etc.)
        logger.info("\n   Creating tasks for non-routine calendar events...")

        attention_keywords = [
            'cancelled', 'canceled', 'rescheduled', 'moved',
            'dr', 'doctor', 'dentist', 'appointment',
            'pickup', 'drop off', 'dropoff',
            'deadline', 'due', 'expires',
            'interview', 'presentation', 'demo',
            'flight', 'travel', 'hotel', 'checkout',
        ]

        for ei, event in enumerate(all_events_list):
            if ei in matched_event_indices:
                continue
            summary = event.get('summary', '')
            date = event.get('date', '')
            time = event.get('time', '')
            is_recurring = event.get('is_recurring', False)
            summary_lower = summary.lower()

            needs_attention = any(kw in summary_lower for kw in attention_keywords)

            if is_recurring and not needs_attention:
                logger.info(f"   Skipped recurring event: {summary[:60]}")
                continue

            task_content = summary
            if time and time != 'All day':
                task_content = f"{summary} at {time}"

            description = f"Calendar event on {date}"
            if time:
                description += f" at {time}"

            priority = 3
            if any(kw in summary_lower for kw in ['cancelled', 'canceled', 'dr', 'doctor', 'dentist', 'pickup', 'deadline', 'interview']):
                priority = 4

            await todoist.create_task(
                content=task_content,
                description=description,
                priority=priority,
                due_string=date,
                labels=['daily-plan', 'calendar']
            )
            created_count += 1
            logger.info(f"   ✅ Created calendar task: {task_content[:60]}")
        
        logger.info(f"\n   ✅ Created {created_count} total tasks")
        
    except Exception as e:
        logger.error(f"   ❌ Error creating Todoist tasks: {e}")
    
    # Step 9: Update Amplenote with detailed analysis
    logger.info("\n📝 STEP 9: Updating Amplenote daily note...")
    try:
        # Create formatted plan for Amplenote
        amplenote_plan = {
            "do_now": [],
            "do_soon": [],
            "monitor": [],
            "stale": [],
            "reference": [],
            "documents": {},
            "reference_emails": gmail.reference_emails,
            "today_events": today_events,
            "tomorrow_events": tomorrow_events,
            "week_events": [e for e in events if e.get('date') != today and e.get('date') != tomorrow],
            "stats": {
                "threads_analyzed": len(thread_analyses),
                "high_priority": len(detailed_breakdown['high_priority']),
                "medium_priority": len(detailed_breakdown['medium_priority']),
                "follow_ups": len(detailed_breakdown['follow_ups_needed']),
                "stale_tasks": len(stale_tasks)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Add high priority items to do_now
        for item in detailed_breakdown['high_priority']:
            amplenote_plan["do_now"].append({
                "title": item['subject'],
                "source": "Email Thread",
                "summary": item['summary'],
                "outcome": item['outcome'],
                "action_items": item['action_items'],
                "context": item['context'],
                "from": item['latest_from'],
                "email_count": item['email_count'],
                "priority": "high"
            })
        
        # Add medium priority to do_soon
        for item in detailed_breakdown['medium_priority']:
            amplenote_plan["do_soon"].append({
                "title": item['subject'],
                "source": "Email Thread",
                "summary": item['summary'],
                "action_items": item['action_items'],
                "priority": "medium"
            })

        # Add stale tasks to separate section (not DO NOW)
        for task in stale_tasks:
            days_overdue = (today_dt - datetime.strptime(task['due']['date'], "%Y-%m-%d").date()).days
            amplenote_plan["stale"].append({
                "title": task['content'],
                "source": "Todoist",
                "due": task['due']['date'],
                "days_overdue": days_overdue,
                "priority": "stale"
            })
        if stale_tasks:
            logger.info(f"   Added {len(stale_tasks)} stale tasks to separate section")

        # Add follow-up items (threads with follow_up_needed but no action_items)
        amplenote_plan["follow_ups"] = []
        for item in detailed_breakdown['follow_ups_needed']:
            if not item.get('action_items'):
                follow_up_text = item.get('follow_up', '')
                for prefix in ('Yes - ', 'yes - ', 'YES - '):
                    if follow_up_text.startswith(prefix):
                        follow_up_text = follow_up_text[len(prefix):]
                        break
                amplenote_plan["follow_ups"].append({
                    "title": item['subject'][:60],
                    "follow_up": follow_up_text,
                    "from": item.get('latest_from', '')
                })
        if amplenote_plan["follow_ups"]:
            logger.info(f"   Added {len(amplenote_plan['follow_ups'])} follow-up items to Amplenote")

        amplenote_success = await amplenote.update_daily_note_with_plan(amplenote_plan)
        if amplenote_success:
            logger.info("   ✅ Amplenote daily note updated successfully")
        else:
            logger.warning("   ⚠️  Could not update Amplenote daily note")
            
    except Exception as e:
        logger.error(f"   ❌ Error updating Amplenote: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("COMPREHENSIVE ANALYSIS COMPLETE")
    logger.info("=" * 80)
    
    return detailed_breakdown

async def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='MCP Daily Planning System - Comprehensive email and calendar analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default environment path
  python run_process_new_v2.py
  
  # Use custom environment path
  python run_process_new_v2.py
        """
    )
    
    args = parser.parse_args()

    try:
        result = await process_new_comprehensive()
        return result
    except Exception as e:
        logger.error(f"Error running comprehensive process: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
