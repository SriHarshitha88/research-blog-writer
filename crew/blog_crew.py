from crewai import Crew, Task
from typing import List, Optional
from agents.researcher_agent import researcher
from agents.writer_agent import writer
from agents.email_agent import emailer

def create_blog_crew(topic: str) -> Crew:
    """
    Create a crew of AI agents to handle ONLY the blog creation process.
    Email sending is handled separately.
    
    Args:
        topic: The main topic for the blog post
    
    Returns:
        A configured Crew instance for blog generation only
    """
    
    # Research task
    research_task = Task(
        description=f"""
        Research the topic: {topic}
        - Find relevant SEO keywords
        - Identify target audience pain points
        - Gather trending subtopics
        - Collect supporting statistics and data
        Output should be a structured research brief in JSON format.
        """,
        expected_output="JSON research brief with keywords, pain points, and data",
        agent=researcher
    )

    # Writing task
    writing_task = Task(
        description="""
        Write a 1000-word blog post based on the research.
        - Use Medium-style writing
        - Include SEO-optimized headings
        - Add relevant statistics and examples
        - Format in markdown
        - Include meta description and tags
        - Ensure high-quality, polished content
        Save the final version as 'final_blog.md'
        """,
        expected_output="Markdown formatted blog post with meta content",
        agent=writer,
        context=[research_task],
        output_file="final_blog.md"
    )

    # Create and return the crew with ONLY research and writing
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True
    )

    return crew

def create_email_crew(
    blog_content: str,
    email_list: List[str],
    custom_subject: Optional[str] = None,
    topic: str = ""
) -> Crew:
    """
    Create a crew specifically for sending emails with the generated blog content.
    
    Args:
        blog_content: The already generated blog post content
        email_list: List of email addresses to send the blog to
        custom_subject: Optional custom subject line for the email
        topic: The blog topic (for default subject line)
    
    Returns:
        A configured Crew instance for email sending only
    """
    
    # Clean and validate email list
    valid_emails = []
    for email in email_list:
        email = email.strip()
        if email and '@' in email:
            valid_emails.append(email)
    
    print(f"Debug - Valid emails for email crew: {valid_emails}")
    
    if not valid_emails:
        raise ValueError("No valid email addresses provided")
    
    # Email task - focused ONLY on sending
    email_task = Task(
        description=f"""
        Send the provided blog post via email using the Gmail Sender tool.
        
        CRITICAL INSTRUCTIONS:
        - Email Recipients: {valid_emails}
        - Subject Line: {custom_subject if custom_subject else 'New Blog Post: ' + topic}
        - Blog Content: Use the provided blog content exactly as given
        - Send to EXACTLY these email addresses: {', '.join(valid_emails)}
        - DO NOT use any placeholder emails
        
        Use the Gmail Sender tool with these exact parameters:
        - blog_text: {blog_content}
        - recipients: {valid_emails}
        - subject: {custom_subject if custom_subject else 'New Blog Post: ' + topic}
        
        Verify that the email is sent to all recipients in this list: {valid_emails}
        """,
        expected_output=f"Email sent confirmation to all {len(valid_emails)} recipients: {', '.join(valid_emails)}",
        agent=emailer
    )

    # Create and return the email crew
    crew = Crew(
        agents=[emailer],
        tasks=[email_task],
        verbose=True
    )

    return crew