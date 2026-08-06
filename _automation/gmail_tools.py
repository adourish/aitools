#!/usr/bin/env python3
"""
Gmail tools for MCP Server
"""

import base64
import logging
import re
from typing import List, Dict, Any
from googleapiclient.discovery import build
from html.parser import HTMLParser

logger = logging.getLogger(__name__)

class HTMLTextExtractor(HTMLParser):
    """Extract text from HTML"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip = True
    
    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip = False
    
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)
    
    def get_text(self):
        return ' '.join(self.text).strip()

class GmailTools:
    """Gmail operations for MCP server"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        
        # Reference email patterns (important info to save)
        self.reference_patterns = [
            'account number', 'account #', 'account:', 'acct #',
            'confirmation number', 'confirmation code', 'confirmation #',
            'reference number', 'reference #', 'ref #',
            'policy number', 'policy #', 'claim number', 'case number',
            'username:', 'password:', 'login:', 'credentials',
            'activation code', 'verification code', 'access code',
            'membership number', 'member #', 'customer id', 'customer number',
            'order number', 'order #', 'invoice #', 'invoice number',
            'hoa', 'homeowners association', 'property account'
        ]
        
        # High-priority whitelisted domains (NEVER filter these)
        self.whitelist_domains = [
            'fcps.edu',
            'fairfaxcounty.gov',
            'townsq.io',
            'virginiadmv',
            'irs.gov',
            'dmv.virginia.gov',
            'aggressor.com',
            'padi.com',
        ]
        
        # Skip patterns for unimportant emails
        self.skip_senders = [
            'tiktok.com',
            'marketing@', 'promo@', 'newsletter@',
            'redditmail.com', 'email.monarch.com', 'rescueme.org',
            'membershipto', 'bankofamerica.com',
            'ealerts.', 'USPSInformeddelivery', 'schwab.com',
            'creditkarma.com', 'omadahealth.com',
            'congressman', 'senator', 'representative', 'house.gov',
            'senate.gov', 'whitehouse.gov', 'campaign@', 'political',
            'amazon.com', 'shipment-tracking@', 'ship-confirm@',
            'auto-confirm@', 'order-update@', 'delivery@',
            'fedex.com', 'ups.com', 'usps.com', 'dhl.com',
            'tracking@', 'shipping@', 'shippo.com',
            # Promotional/marketing emails
            'newsletters@audible.com', 'audible.com',
            'email.bestbuy.com', 'bestbuy.com',
            'emails.ugg.com', 'ugg.com',
            'email@mail.salesforce.com',
            # Travel/cruise promotions
            'royalcaribbean', 'carnival.com', 'norwegiancruise',
            'princess.com', 'hollandamerica.com',
            # Financial newsletters/promotions
            'motley.fool.com', 'fool@', 'morningstar.com',
            'seekingalpha.com', 'investopedia.com',
            'thestreet.com', 'marketwatch.com', 'barrons.com',
            # Tax/financial services promotions
            'turbotax@', 'turbotax.intuit.com', 'intuit.com',
            # Entertainment/streaming services
            'hbo.com', 'hbomax.com', 'max.com', 'warnermedia.com',
            # Healthcare/appointment services
            'zocdoc.com', 'mail5.zocdoc.com',
            # Billing notifications
            'verizon', 'vzw.com', 'verizonwireless.com',
            # School/PTA promotional emails
            'notify@membershiptoolkit.com', 'afterschool activities',
            # Investment newsletters
            'fool.com', 'motleyfool.com', 'tom gardner'
        ]
        
        # High-priority keywords (ALWAYS include if present)
        self.priority_keywords = [
            'school closed', 'school closing', 'schools closed',
            'school delay', 'two-hour delay', 'early dismissal',
            'appointment reminder', 'appointment confirmed',
            'scheduled for', 'appointment on',
            'field trip', 'permission slip',
            'registration due', 'renewal due', 'expires',
            'property maintenance', 'on site', 'service scheduled',
            'today at', 'this afternoon', 'this evening',
            'same day', 'deadline today',
            'certification', 'scuba', 'padi', 'dive trip',
        ]
        
        self.skip_keywords = [
            'shipped', 'delivered', 'delivery', 'tracking',
            'package', 'shipment', 'order confirmation',
            'your order', 'has shipped', 'out for delivery',
            'hanger', 'hangers', 'item has been delivered',
            # Promotional/sales keywords
            'deal ends', 'wish list', 'sale', 'discount',
            'trade up', 'own apple for less',
            'view as a web page', 'membership now',
            'newness for your littles', 'latest and greatest',
            # Savings/deals
            'instant savings', 'save up to', 'up to $', 'off before',
            'vacay alert', 'vacation alert', 'cruise deal',
            'limited time offer', 'act now', 'ends tonight',
            'last chance', 'final hours', 'flash sale',
            'mega savings', 'huge savings', 'score up to',
            # Marketing language
            'click here to', 'shop now', 'buy now', 'order now',
            'free shipping', 'free delivery', 'no purchase necessary',
            'terms and conditions apply', 'see details',
            # OneDrive and signup notifications
            'onedrive', 'cloud storage', 'sign up', 'signup', 'sign-up',
            'account creation', 'welcome to', 'verify your account',
            'activate your account', 'complete your profile'
        ]
        
        self.reference_emails = []
        self._service = None
    
    async def _get_service(self):
        """Get Gmail service, creating if needed"""
        if not self._service:
            creds = await self.auth_manager.get_gmail_credentials()
            self._service = build('gmail', 'v1', credentials=creds)
        return self._service
    
    def is_whitelisted_sender(self, sender: str) -> bool:
        """Check if sender is whitelisted (high priority)"""
        sender_lower = sender.lower()
        return any(domain in sender_lower for domain in self.whitelist_domains)
    
    def is_important_sender(self, sender: str) -> bool:
        """Check if email is from important sender"""
        sender_lower = sender.lower()
        
        # Whitelisted senders are always important
        if self.is_whitelisted_sender(sender):
            return True
        
        # Check skip patterns
        for skip_pattern in self.skip_senders:
            if skip_pattern in sender_lower:
                return False
        return True
    
    def has_priority_content(self, subject: str, body: str) -> bool:
        """Check if email contains high-priority keywords"""
        text = (subject + ' ' + body).lower()
        return any(keyword in text for keyword in self.priority_keywords)
    
    def is_unimportant_email(self, subject: str, body: str, sender: str = '') -> bool:
        """Check if email is shipping/delivery notification or generic newsletter"""
        # Whitelisted senders are NEVER unimportant
        if self.is_whitelisted_sender(sender):
            return False
        
        # Priority content is NEVER unimportant
        if self.has_priority_content(subject, body):
            return False
        
        text = (subject + ' ' + body).lower()
        return any(keyword in text for keyword in self.skip_keywords)
    
    def is_reference_email(self, subject: str, body: str) -> bool:
        """Check if email contains reference information"""
        text = (subject + ' ' + body).lower()
        return any(pattern in text for pattern in self.reference_patterns)
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Gmail for messages"""
        service = await self._get_service()
        
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            detailed_messages = []
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                detailed_messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': from_email,
                    'date': date
                })
            
            logger.info(f"Found {len(detailed_messages)} messages for query: {query}")
            return detailed_messages
        
        except Exception as e:
            logger.error(f"Error searching Gmail: {e}")
            raise
    
    async def get_email(self, message_id: str) -> Dict[str, Any]:
        """Get full email content"""
        service = await self._get_service()
        
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            # Get body - try text/plain first, then HTML
            body = ''
            html_body = ''
            
            def extract_body_from_parts(parts):
                """Recursively extract body from message parts"""
                text = ''
                html = ''
                for part in parts:
                    mime_type = part.get('mimeType', '')
                    
                    if 'parts' in part:
                        sub_text, sub_html = extract_body_from_parts(part['parts'])
                        text += sub_text
                        html += sub_html
                    elif mime_type == 'text/plain' and 'data' in part.get('body', {}):
                        text += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    elif mime_type == 'text/html' and 'data' in part.get('body', {}):
                        html += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                
                return text, html
            
            if 'parts' in message['payload']:
                body, html_body = extract_body_from_parts(message['payload']['parts'])
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                mime_type = message['payload'].get('mimeType', '')
                decoded = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')
                if mime_type == 'text/html':
                    html_body = decoded
                else:
                    body = decoded
            
            # If no plain text, extract from HTML
            if not body and html_body:
                try:
                    parser = HTMLTextExtractor()
                    parser.feed(html_body)
                    body = parser.get_text()
                    # Clean up whitespace
                    body = re.sub(r'\s+', ' ', body).strip()
                except Exception as e:
                    logger.warning(f"Could not parse HTML for message {message_id}: {e}")
                    body = html_body[:500]
            
            return {
                'id': message_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'body': body
            }
        
        except Exception as e:
            logger.error(f"Error getting email {message_id}: {e}")
            raise
    
    async def get_urgent_emails(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get urgent emails from last N days and detect reference emails"""
        query = f'newer_than:{days}d -from:noreply -from:no-reply -from:donotreply'

        messages = await self.search(query, max_results=100)

        # Supplemental query: whitelisted domains bypass noreply filter
        whitelist_query = '(' + ' OR '.join(f'from:{d}' for d in self.whitelist_domains) + f') newer_than:{days}d'
        whitelist_messages = await self.search(whitelist_query, max_results=50)
        seen_ids = {m['id'] for m in messages}
        for m in whitelist_messages:
            if m['id'] not in seen_ids:
                messages.append(m)
                seen_ids.add(m['id'])
        
        urgent = []
        self.reference_emails = []
        
        for msg in messages:
            # Get full message for better filtering
            full_msg = await self.get_email(msg['id'])
            subject = full_msg.get('subject', '')
            body = full_msg.get('body', '')
            sender = full_msg.get('from', '')
            
            # Skip unimportant senders FIRST (before any other checks)
            if not self.is_important_sender(sender):
                continue
            
            # Skip unimportant emails (now considers sender and priority content)
            if self.is_unimportant_email(subject, body, sender):
                continue
            
            text = (subject + ' ' + body).lower()
            
            # Check if this is a reference email (save silently, don't treat as urgent)
            if self.is_reference_email(subject, body):
                self.reference_emails.append({
                    'subject': subject,
                    'from': sender.split('<')[0].strip() if '<' in sender else sender,
                    'body': body[:1000],
                    'date': full_msg.get('date', ''),
                    'id': full_msg.get('id', '')
                })
                # Reference-only emails (confirmations, account numbers) are NOT urgent
                # unless they also contain actionable content
                if not self.has_priority_content(subject, body) and not any(
                    word in (subject + ' ' + body).lower()
                    for word in ['urgent', 'asap', 'action required', 'respond', 'deadline']
                ):
                    continue

            # Whitelisted senders or priority content = always urgent
            if self.is_whitelisted_sender(sender) or self.has_priority_content(subject, body):
                urgent.append(full_msg)
                continue
            
            # Check urgency keywords for important senders
            is_urgent = any(word in text for word in [
                'urgent', 'asap', 'today', 'deadline', 'due',
                'important', 'action required', 'respond', 'confirm'
            ])
            
            if is_urgent:
                urgent.append(full_msg)
        
        logger.info(f"Found {len(urgent)} urgent emails, {len(self.reference_emails)} reference emails")
        return urgent
