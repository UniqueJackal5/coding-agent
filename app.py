# app.py
import streamlit as st
import os
from gemini_core import call_gemini  # We reuse our existing connector!

# --- Page Configuration ---
# This should be the first Streamlit command in your script.
st.set_page_config(
    page_title="Gemini Coding Agent",
    page_icon="🤖",
    layout="wide"
)

# --- App Title and Description ---
st.title("🤖 Gemini Coding Agent")
st.write("An interactive chat agent to help you write and modify code. Just upload a file and start chatting!")


# --- Helper function to read file content ---
def read_file_content(uploaded_file):
    """Reads the content of an uploaded file."""
    if uploaded_file is not None:
        try:
            return uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None
    return None


# --- The Main Application Logic ---

# Sidebar for file upload and controls
with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Upload a code file", type=['py', 'txt', 'js', 'html', 'css', 'md'])
    
    # Read the file content when a file is uploaded
    file_content = read_file_content(uploaded_file)
    
    if uploaded_file:
        st.success(f"Loaded `{uploaded_file.name}`")
        # Display file content in an expandable box
        with st.expander("View File Content"):
            st.code(file_content, language='python') # You can change the language

# Initialize chat history in Streamlit's session state
# This makes the history persist between reruns (i.e., when you send a message)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input from the chat box
if prompt := st.chat_input("What change would you like to make?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Check if a file has been uploaded
    if not file_content:
        st.warning("Please upload a code file first to provide context for your request.")
    else:
        # Construct the full prompt for the LLM
        # We'll include the last few messages for conversation context if you want,
        # but for a simple file-based agent, just the file content is often enough.
        final_prompt = f"""
        You are an expert pair-programming assistant.
        The user has provided the following code file content:

        --- START OF FILE CONTENT ---
        {file_content}
        --- END OF FILE CONTENT ---

        The user's request is: "{prompt}"

        Based on the file content and the user request, generate the required code.
        Provide only the raw code block unless the user asks for an explanation.
        """

        # Display "thinking" message while waiting for the response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = call_gemini(final_prompt)
                    st.code(response, language='python') # Use st.code for beautiful formatting
                except ValueError as e:
                    st.error(f"Configuration Error: {e}. Please ensure your `GEMINI_API_KEY` is correctly set.")
                    response = None
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    response = None

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})