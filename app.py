import streamlit as st
import urllib.request
import urllib.error
import os
from openai import OpenAI

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
        {"role": "user", "content": f"Here's some content:\n\n{content[:7000]}\n\nBased on this content, please answer the following question and be concise: {question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=700
    )

    return response.choices[0].message.content

# Streamlit app
def main():
    st.title("Web/PDF URL Content Q&A")

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

    if url:
        try:
            # Fetch content
            with st.spinner("Fetching content..."):
                content = fetch_content(url, jina_api_key)
            st.success("Content fetched successfully!")

            # Question input
            question = st.text_input("Enter your question:")

            if st.button("Ask"):
                if question:
                    with st.spinner("Generating answer..."):
                        answer = ask_question(client, content, question)
                    st.subheader("Answer:")
                    st.write(answer)
                else:
                    st.warning("Please enter a question.")
        
        except urllib.error.HTTPError as e:
            st.error(f'HTTP Error {e.code}: {e.reason}. URL: {url}')
        except urllib.error.URLError as e:
            st.error(f'URL Error: {str(e)}. URL: {url}')
        except Exception as e:
            st.error(f'Unexpected error: {str(e)}. URL: {url}')

if __name__ == "__main__":
    main()
