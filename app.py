import streamlit as st
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os 
import pandas as pd
from dotenv import load_dotenv
import sys
from io import StringIO
import contextlib
import re

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Read the Titanic dataset
df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")

# Initialize the language model and create an agent
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)
agent = create_pandas_dataframe_agent(llm, df, verbose=True)

# Function to run the chatbot
def run_chat():
    chat_history = []
    while True:
        user_input = st.text_input("You:", key=f"user_input_{len(chat_history)}")
        if user_input:
            chat_history.append({"speaker": "You", "message": user_input})
            thought_process_output = st.empty()
            with st.spinner('Thinking...'):
                # Capture the output of print statements
                stdout_backup = sys.stdout
                sys.stdout = StringIO()
                try:
                    agent.invoke(user_input)
                finally:
                    thought_process = re.sub(r'\x1b\[[0-9;]*m', '', sys.stdout.getvalue())  # Remove ANSI escape codes
                    thought_process_output.text(thought_process)
                    # Reset the stdout to the original value
                    sys.stdout = stdout_backup

            response = agent.invoke(user_input)
            chat_history.append({"speaker": "Bot", "message": response})
            st.write("Bot:", response)
        else:
            break
    return chat_history

# Main Streamlit app
def main():
    st.title("Titanic Dataset Chatbot")
    st.sidebar.title("Chat History")
    st.sidebar.markdown("This is the chat history:")

    chat_history = run_chat()

    # Display chat history in sidebar
    for item in chat_history:
        st.sidebar.write(f"{item['speaker']}: {item['message']}")

if __name__ == "__main__":
    main()
