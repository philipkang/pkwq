import streamlit as st
import urllib.request
import urllib.error
import os
from openai import OpenAI

# Set page config at the very beginning
st.set_page_config(layout="wide")

# Hide Streamlit's branding and header
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Add custom CSS
custom_css = """
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    h1 {
        margin-top: -1rem;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# Function to fetch content from URL
def fetch_content(url, jina_api_key):
    full_url = f"https://r.jina.ai/{url}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Authorization': f'Bearer {jina_api_key}'
    }
    req = urllib.request.Request(full_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

# Function to ask question using OpenAI
def ask_question(client, content, question):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Here's some content:\n\n{content[:8000]}\n\nBased on this content, please answer the following question and be concise: {question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=700
    )

    return response.choices[0].message.content

# Streamlit app
def main():          
    # Initialize session state
    if 'content' not in st.session_state:
        st.session_state.content = None
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'reset' not in st.session_state:
        st.session_state.reset = False

    # Check if reset is triggered
    if st.session_state.reset:
        st.session_state.content = None
        st.session_state.question_count = 0
        st.session_state.reset = False

    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Web Content Q&A</h1>", unsafe_allow_html=True)

    # Get API keys from environment variables or Streamlit secrets
    jina_api_key = os.environ.get('JINA_API_KEY') or st.secrets["JINA_API_KEY"]
    openai_api_key = os.environ.get('OPENAI_API_KEY') or st.secrets["OPENAI_API_KEY"]

    if not jina_api_key or not openai_api_key:
        st.error("API keys are missing. Please set JINA_API_KEY and OPENAI_API_KEY.")
        return

    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # URL input
    url = st.text_input("Enter the URL:")

    if url and not st.session_state.content:
        try:
            # Fetch content
            with st.spinner("Fetching content..."):
                st.session_state.content = fetch_content(url, jina_api_key)
            st.success("Content fetched successfully!")
        except urllib.error.HTTPError as e:
            st.error(f'HTTP Error {e.code}: {e.reason}. URL: {url}')
        except urllib.error.URLError as e:
            st.error(f'URL Error: {str(e)}. URL: {url}')
        except Exception as e:
            st.error(f'Unexpected error: {str(e)}. URL: {url}')

    if st.session_state.content:
        # Question input
        question = st.text_input("Enter your question:")

        if st.button("Ask") and st.session_state.question_count < 3:
            if question:
                st.session_state.question_count += 1
                with st.spinner("Generating answer..."):
                    answer = ask_question(client, st.session_state.content, question)
                st.subheader(f"Answer (Question {st.session_state.question_count}/3):")
                st.write(answer)
            else:
                st.warning("Please enter a question.")
        
        # Display remaining questions
        remaining = 3 - st.session_state.question_count
        st.write(f"Remaining questions: {remaining}")

        if st.session_state.question_count >= 3:
            st.warning("You have reached the maximum number of questions (3). Please reset to start over.")

    # Reset button
    if st.button("Reset"):
        st.session_state.reset = True
        st.rerun()

if __name__ == "__main__":
    main()
