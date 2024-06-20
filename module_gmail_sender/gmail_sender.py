from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import re

class GmailSender:
    # Constants defining default values and configurations
    MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_FROM_ADDRESS = 'admin@cloudelivery.com.au'
    DEFAULT_TO_ADDRESS = 'jeffreycaizhenyuan@gmail.com'
    DEFAULT_SENDER_ID = 'me'
    ADMIN_EMAIL = 'admin@cloudelivery.com.au'
    SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, service_account_file=None):
        """
        Initializes the GmailSender with optional service account file path.
        
        Args:
            service_account_file (str, optional): Path to service account file. Defaults to None.
        """
        # Use provided service account file or default to the one in the module directory
        if service_account_file is None:
            self.service_account_file = os.path.join(self.MODULE_DIR, 'gcp-svc-acc-key.json')
        else:
            self.service_account_file = service_account_file
        
        self.default_from_email = self.DEFAULT_FROM_ADDRESS
        self.default_to_email = self.DEFAULT_TO_ADDRESS
        self.default_send_id = self.DEFAULT_SENDER_ID

    def send(self, subject, message_text_html, sender=None, sender_id=DEFAULT_SENDER_ID, to=None, attachment_paths=None):
        """
        Sends an email using Gmail service.
        
        Args:
            subject (str): Subject of the email.
            message_text_html (str): HTML content of the email.
            sender (str, optional): Email sender address. Defaults to None.
            sender_id (str, optional): Sender ID for Gmail API. Defaults to DEFAULT_SENDER_ID.
            to (str, optional): Recipient email address. Defaults to None.
            
        Returns:
            dict: Gmail API response after sending the email.
        """
        service = self.get_gmail_service()
        message = self.create_message(subject, message_text_html, sender, to, attachment_paths)
        return self.send_message(service, message, sender_id)

    def create_message(self, subject, message_text_html, sender=None, to=None, attachment_paths=None):
        """
        Creates an email message suitable for the Gmail API, including attachments.
        
        Args:
            subject (str): Subject of the email.
            message_text_html (str): HTML content of the email.
            sender (str, optional): Email sender address. Defaults to None.
            to (str, optional): Recipient email address. Defaults to None.
            attachment_paths (list, optional): List of file paths for attachments. Defaults to None.
            
        Returns:
            dict: Message formatted for Gmail API.
        """
        message = MIMEMultipart()
        message['to'] = to or self.default_to_email
        message['from'] = sender or self.default_from_email
        message['subject'] = subject

        # Attach the main message body
        msg = MIMEText(message_text_html, 'html')
        message.attach(msg)

        # Attach any files specified
        if attachment_paths:
            for file_path in attachment_paths:
                part = MIMEBase('application', 'octet-stream')
                with open(file_path, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(file_path)}"',
                )
                message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw_message}
        return body

    def send_message(self, service, message, user_id=DEFAULT_SENDER_ID):
        """
        Sends the email message using the Gmail API service instance.
        
        Args:
            service (obj): Gmail API service instance.
            message (dict): Email message formatted for Gmail API.
            user_id (str, optional): Sender ID for Gmail API. Defaults to DEFAULT_SENDER_ID.
            
        Returns:
            dict: Gmail API response after sending the email.
        """
        try:
            message = (service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
        except Exception as e:
            print('An error occurred: %s' % e)
            return None

    def get_gmail_service(self):
        """
        Returns an instance of the Gmail API service.
        
        Args:
            subject (str): Subject of the email, used for creating the service instance.
            
        Returns:
            obj: Gmail API service instance.
        """
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.SCOPES,
            subject=self.ADMIN_EMAIL)
        service = build('gmail', 'v1', credentials=credentials)
        return service

    def list_messages(self, user_id, regex, max_results=50):
        """List the user's Gmail messages matching a regex."""
        service = self.get_gmail_service()
        try:
            response = service.users().messages().list(userId=user_id, maxResults=max_results, labelIds=['INBOX']).execute()
            all_messages = response.get('messages', [])

            matching_messages = []
            for msg in all_messages:
                msg_detail = service.users().messages().get(userId=user_id, id=msg['id'], format='metadata', metadataHeaders=['Subject']).execute()
                headers = msg_detail.get('payload', {}).get('headers', [])
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')

                if re.search(regex, subject):
                    matching_messages.append(msg)

            return matching_messages

        except Exception as e:
            print(f'An error occurred while listing messages: {e}')
            return None

    def get_message(self, user_id, message_id):
        """Get a specific Gmail message."""
        service = self.get_gmail_service()
        try:
            message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
            
            # Decode the subject and sender from the headers
            headers = message.get('payload', {}).get('headers', [])
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            sender = next(header['value'] for header in headers if header['name'] == 'From')
    
            # Function to recursively walk through the message parts
            def get_mime_parts(parts, mime_type):
                mime_parts = []
                for part in parts:
                    if part['mimeType'] == mime_type:
                        mime_parts.append(part['body']['data'])
                    elif 'parts' in part:
                        mime_parts.extend(get_mime_parts(part['parts'], mime_type))
                return mime_parts
    
            # Adjust for messages without 'parts'
            if 'parts' in message['payload']:
                encoded_body_parts = get_mime_parts(message['payload']['parts'], 'text/html')
            else:
                encoded_body = message['payload']['body'].get('data')
                encoded_body_parts = [encoded_body] if encoded_body else []
    
            # Decode and print the HTML content
            if encoded_body:
                html_content = base64.urlsafe_b64decode(encoded_body).decode('utf-8')
                # print(f'From: {sender}')
                # print(f'Subject: {subject}')
                # print(f'HTML Content: {html_content}\n')
                return html_content
            else:
                print('No HTML content found.')
    
        except Exception as e:
            print(f'An error occurred in get_message(): {e}')
            return None
    
