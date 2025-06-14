import streamlit as st
import os
from dotenv import load_dotenv
from crew.blog_crew import create_blog_crew, create_email_crew
from tools.trend_analyzer import get_trending_topics
import time

# Load environment variables
load_dotenv()

# Initialize session state for blog content and topic
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = None
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'current_content' not in st.session_state:
    st.session_state.current_content = ""

# Page config
st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide"
)

# Sidebar
st.sidebar.title("Settings")
email_list = st.sidebar.text_area("Email List (one per line)", height=150)
custom_subject = st.sidebar.text_input("Custom Subject Line (optional)")

# Main content
st.title("✍️ AI Blog Generator")
st.markdown("Generate, edit, and distribute blog posts with AI agents")

# Topic input with trending suggestions
col1, col2 = st.columns([2, 1])
with col1:
    topic = st.text_input("Enter your blog topic", 
                         value=st.session_state.topic,
                         placeholder="e.g., Future of AI in Education")
with col2:
    if st.button("Get Trending Topics"):
        trends = get_trending_topics()
        st.session_state.trends = trends

if 'trends' in st.session_state:
    st.subheader("🔥 Trending Topics")
    for trend in st.session_state.trends:
        if st.button(trend, key=trend):
            st.session_state.topic = trend
            st.rerun()

# Progress tracking
progress_placeholder = st.empty()
content_placeholder = st.empty()
status_placeholder = st.empty()

# Generate button - ONLY handles blog generation
if st.button("🚀 Generate Blog Post", type="primary"):
    if not topic:
        st.error("Please enter a topic first!")
    else:
        # Initialize progress
        progress = st.progress(0)
        progress_placeholder.progress(0, "Starting research...")
        content_placeholder.markdown("")
        status_placeholder.info("🔄 Initializing AI agents...")
        
        try:
            # Create blog crew WITHOUT email task
            blog_crew = create_blog_crew(topic=topic)
            
            # Update status for research phase
            status_placeholder.info("🔍 Researching topic and gathering information...")
            progress_placeholder.progress(33, "Researching...")
            
            # Execute the crew (research + writing only)
            result = blog_crew.kickoff()
            
            # Update progress
            progress_placeholder.progress(100, "Complete!")
            status_placeholder.success("✨ Blog post generated successfully!")
            
            # Store the result
            st.session_state.blog_content = result
            content_placeholder.markdown(st.session_state.blog_content)
            
        except Exception as e:
            status_placeholder.error(f"❌ Error: {str(e)}")
            progress_placeholder.empty()

# Display generated content
if st.session_state.blog_content:
    st.markdown("---")
    st.subheader("📝 Generated Blog Post")
    st.markdown(st.session_state.blog_content)

# Email sending section - SEPARATE from blog generation
if st.session_state.blog_content:
    st.markdown("---")
    st.subheader("📧 Email Distribution")
    
    # Show email settings
    email_count = len([e.strip() for e in email_list.split('\n') if e.strip() and '@' in e.strip()]) if email_list else 0
    st.info(f"📧 Recipients: {email_count} email(s)")
    if custom_subject:
        st.info(f"📝 Subject: {custom_subject}")
    
    # Send button - ONLY handles email sending
    if st.button("📤 Send Blog Post", type="primary"):
        if not email_list:
            st.error("Please add at least one email address in the sidebar!")
        else:
            with st.spinner("Sending email..."):
                try:
                    # Clean email list
                    clean_emails = [e.strip() for e in email_list.split('\n') if e.strip() and '@' in e.strip()]
                    
                    # Create email crew with the generated blog content
                    email_crew = create_email_crew(
                        blog_content=st.session_state.blog_content,
                        email_list=clean_emails,
                        custom_subject=custom_subject,
                        topic=topic
                    )
                    
                    # Send email
                    email_result = email_crew.kickoff()
                    
                    st.success(f"📧 Email sent successfully to {len(clean_emails)} recipients!")
                    st.info(f"Recipients: {', '.join(clean_emails)}")
                    
                except Exception as e:
                    st.error(f"Failed to send email: {str(e)}")
                    st.exception(e)  # Show full error for debugging