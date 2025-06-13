# app.py
import os
import streamlit as st
from gemini_core import call_gemini  # We reuse our existing connector!
from file_reader import get_project_context


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


# --- The Main Application Logic ---

# Sidebar for project directory selection and controls
with st.sidebar:
    st.header("Controls")
    project_directory = st.text_input("Enter Project Directory (e.g., . for current)", ".")
    
    project_context = ""
    if project_directory:
        try:
            # Get absolute path for get_project_context
            abs_project_directory = os.path.abspath(project_directory)
            st.write(f"Analyzing directory: `{abs_project_directory}`")
            project_context = get_project_context(abs_project_directory)
            if project_context:
                st.success(f"Loaded project context from `{project_directory}`")
                with st.expander("View Project Context"):
                    st.code(project_context, language='python') # Display as generic code
            else:
                st.warning("No relevant files found in the specified directory.")
        except Exception as e:
            st.error(f"Error reading project directory: {e}")

# Initialize chat history in Streamlit's session state
# This makes the history persist between reruns (i.e., when you send a message)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input from the chat box
if prompt := st.chat_input("What change would you like to make?", key="chat_input_main"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Check if project context has been loaded
    if not project_context:
        st.warning("Please specify a project directory to provide context for your request.")
    else:
        # Construct the full prompt for the LLM
        final_prompt = f"""
        You are an expert pair-programming assistant.
        The user has provided the following project context:

        --- START OF PROJECT CONTEXT ---
        {project_context}
        --- END OF PROJECT CONTEXT ---

        The user's request is: "{prompt}"

        Based on the project context and the user request, generate the required code.
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
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})