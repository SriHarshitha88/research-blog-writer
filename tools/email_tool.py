from crewai.tools import BaseTool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from typing import List
import markdown
import re

class EmailTool(BaseTool):
    name: str = "Gmail Sender"
    description: str = "Sends formatted blog posts via Gmail"

    def _run(self, blog_text: str, recipients: List[str], subject: str) -> str:
        """
        Send the blog post via Gmail.
        
        Args:
            blog_text: The markdown formatted blog post
            recipients: List of email addresses
            subject: Email subject line
        
        Returns:
            Confirmation message
        """
        try:
            # Extract metadata and content
            metadata, content = self._parse_blog_content(blog_text)
            
            # Convert markdown to HTML
            html_content = markdown.markdown(content)
            
            # Create email body with proper formatting
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                        {metadata.get('title', 'Blog Post')}
                    </h1>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <p style="margin: 0;"><strong>Meta Description:</strong> {metadata.get('meta_description', '')}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Tags:</strong> {metadata.get('tags', '')}</p>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        {html_content}
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Get Gmail service
            service = self._get_gmail_service()
            
            # Create email message
            message = {
                'raw': self._create_message(
                    to=recipients,
                    subject=subject or metadata.get('title', 'New Blog Post'),
                    html_content=email_body
                )
            }
            
            # Send email
            sent_message = service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return f"Email sent successfully! Message ID: {sent_message['id']}"
            
        except Exception as e:
            return f"Error sending email: {str(e)}"

    def _parse_blog_content(self, blog_text: str) -> tuple:
        """Parse blog content to extract metadata and main content."""
        # Initialize metadata
        metadata = {
            'title': '',
            'meta_description': '',
            'tags': ''
        }
        
        # Extract metadata using regex
        title_match = re.search(r'title:\s*(.*?)(?:\n|$)', blog_text)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        meta_desc_match = re.search(r'meta_description:\s*(.*?)(?:\n|$)', blog_text)
        if meta_desc_match:
            metadata['meta_description'] = meta_desc_match.group(1).strip()
        
        tags_match = re.search(r'tags:\s*(.*?)(?:\n|$)', blog_text)
        if tags_match:
            metadata['tags'] = tags_match.group(1).strip()
        
        # Remove metadata section from content
        content = re.sub(r'---\s*\n.*?---\s*\n', '', blog_text, flags=re.DOTALL)
        
        return metadata, content.strip()

    def _get_gmail_service(self):
        """Get Gmail API service."""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        
        # Load credentials from token.pickle
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)

    def _create_message(self, to: List[str], subject: str, html_content: str) -> str:
        """Create email message in base64url format."""
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart('alternative')
        message['to'] = ', '.join(to)
        message['subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes())
        return raw.decode()

email_tool = EmailTool()