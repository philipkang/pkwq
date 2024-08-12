import streamlit as st
import urllib.request
import urllib.error
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
    if 'url' not in st.session_state:
        st.session_state.url = ""
    if 'question' not in st.session_state:
        st.session_state.question = ""
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    if 'jina_api_key' not in st.session_state:
        st.session_state.jina_api_key = ""

    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Web Content Q&A</h1>", unsafe_allow_html=True)

    # Jina API key input (automatically masked)
    if not st.session_state.jina_api_key:
        jina_api_key = st.text_input("Enter your Jina API key:", type="password", key="jina_key_input")
        if st.button("Set Jina API Key"):
            if jina_api_key:
                st.session_state.jina_api_key = jina_api_key
                st.success("Jina API key is set.")
            else:
                st.warning("Please enter a Jina API key.")
    else:
        st.success("Jina API key is set.")

    # OpenAI API key input (automatically masked)
    if not st.session_state.openai_api_key:
        openai_api_key = st.text_input("Enter your OpenAI API key:", type="password", key="openai_key_input")
        if st.button("Set OpenAI API Key"):
            if openai_api_key:
                st.session_state.openai_api_key = openai_api_key
                st.success("OpenAI API key is set.")
            else:
                st.warning("Please enter an OpenAI API key.")
    else:
        st.success("OpenAI API key is set.")

    # Initialize OpenAI client if API key is provided
    client = None
    if st.session_state.openai_api_key:
        client = OpenAI(api_key=st.session_state.openai_api_key)

    # URL input
    url = st.text_input("Enter the URL:", value=st.session_state.url, key="url_input")

    if url and url != st.session_state.url:
        st.session_state.url = url
        st.session_state.content = None
        st.session_state.question_count = 0

    if url and not st.session_state.content:
        if not st.session_state.jina_api_key:
            st.warning("Please enter your Jina API key.")
        else:
            try:
                # Fetch content
                with st.spinner("Fetching content..."):
                    st.session_state.content = fetch_content(url, st.session_state.jina_api_key)
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
            if not st.session_state.openai_api_key:
                st.warning("Please enter your OpenAI API key.")
            elif not question:
                st.warning("Please enter a question.")
            elif client:
                st.session_state.question_count += 1
                with st.spinner("Generating answer..."):
                    answer = ask_question(client, st.session_state.content, question)
                st.subheader(f"Answer to Question {st.session_state.question_count}:")
                st.write(answer)

    # Reset button
    if st.button("Reset"):
        st.session_state.content = None
        st.session_state.question_count = 0
        st.session_state.url = ""
        st.session_state.question = ""
        st.rerun()

if __name__ == "__main__":
    main()
