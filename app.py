import streamlit as st
import urllib.request
import urllib.error
import os
import requests
import json

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

# Azure OpenAI API endpoint
api_url = "https://copilot-sales.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-06-01"

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

# Function to ask question using Azure OpenAI
def ask_question(azure_api_key, content, question):
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_api_key,
    }

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Here's some content:\n\n{content[:8000]}\n\nBased on this content, please answer the following question and be concise: {question}"}
    ]

    payload = {
        "messages": messages,
        "max_tokens": 700,
        "temperature": 0
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("choices", [])[0].get("message", {}).get("content", "")
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

# Streamlit app
def main():          
    # Initialize session state
    if 'content' not in st.session_state:
        st.session_state.content = None
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'url' not in st.session_state:
        st.session_state.url = ""
    if 'question' not in st.session_state:
        st.session_state.question = ""

    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Web Content Q&A</h1>", unsafe_allow_html=True)

    # Get API keys from environment variables or Streamlit secrets
    jina_api_key = os.environ.get('JINA_API_KEY') or st.secrets["JINA_API_KEY"]
    azure_api_key = os.environ.get('AZURE_API_KEY') or st.secrets["AZURE_API_KEY"]

    if not jina_api_key or not azure_api_key:
        st.error("API keys are missing. Please set JINA_API_KEY and AZURE_API_KEY.")
        return

    # URL input
    url = st.text_input("Enter the URL:", value=st.session_state.url, key="url_input")

    if url and url != st.session_state.url:
        st.session_state.url = url
        st.session_state.content = None
        st.session_state.question_count = 0

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
        # Display question count
        if st.session_state.question_count > 0:
            st.info(f"{st.session_state.question_count} question{'s' if st.session_state.question_count > 1 else ''} have been asked for this URL.")

        # Question input
        question = st.text_input("Enter your question:", value="", key="question_input")

        if st.button("Ask"):
            if question:
                st.session_state.question_count += 1
                with st.spinner("Generating answer..."):
                    answer = ask_question(azure_api_key, st.session_state.content, question)
                st.subheader(f"Answer to Question {st.session_state.question_count}:")
                st.write(answer)
            else:
                st.warning("Please enter a question.")

    # Reset button
    if st.button("Reset"):
        st.session_state.content = None
        st.session_state.question_count = 0
        st.session_state.url = ""
        st.session_state.question = ""
        st.rerun()

if __name__ == "__main__":
    main()
