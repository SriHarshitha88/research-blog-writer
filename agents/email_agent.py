from crewai import Agent, Task
from tools.email_tool import email_tool

emailer = Agent(
    role="Email Distribution Specialist",
    goal="Distribute blog posts effectively via email with proper formatting to the exact recipients specified",
    backstory="""You are an expert in email marketing and content distribution.
    You know how to craft engaging email subject lines and format content for
    maximum impact. Your expertise ensures that blog posts reach their intended
    audience in a professional and engaging manner. You ALWAYS use the exact
    email addresses provided to you - never use placeholder or example emails.""",
    tools=[email_tool],
    verbose=True,
    allow_delegation=False
)

def create_email_task(blog_content: str, recipients: list, subject: str = None):
    """
    Create an email task with specific parameters.
    
    Args:
        blog_content: The blog post content to send
        recipients: List of email addresses
        subject: Email subject line
    """
    if not subject:
        subject = "Your AI-Generated Blog Post"
    
    # Create a detailed task description that includes the specific parameters
    task_description = f"""
    Send the following blog post via email to these specific recipients: {', '.join(recipients)}
    
    Email Subject: {subject}
    
    Blog Content:
    {blog_content}
    
    IMPORTANT: Use EXACTLY these email addresses: {recipients}
    Do NOT use any placeholder emails like recipient1@gmail.com or example@email.com
    """
    
    return Task(
        description=task_description,
        agent=emailer,
        expected_output="Confirmation that the email was sent successfully to all specified recipients"
    )