import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to save CSV file
def save_csv_file(df):
    df.to_csv("data.csv", index=False)

# Function to gather metadata about the CSV file
def get_csv_metadata(df):
    metadata = {
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.to_dict(),
        "null_values": df.isnull().sum().to_dict(),
        "example_data": df.head().to_dict()
    }
    return metadata

# Define Streamlit app
def main():
    # Title
    st.title("DIGIOTAI GRAPH GENERATOR")

    # File uploader for CSV file
    st.sidebar.title("Upload CSV File")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Save the uploaded CSV file locally
        df = pd.read_csv(uploaded_file)
        save_csv_file(df)
        st.sidebar.success("CSV file uploaded successfully!")

        # Get metadata about the CSV file
        csv_metadata = get_csv_metadata(df)
        metadata_str = ", ".join(csv_metadata["columns"])

        # User input for query
        st.subheader("Enter your query:")
        user_query = st.text_input("")

        if user_query:
            # Generate content using user input
            prompt_eng = (
                f"You are graphbot. If the user asks to plot a graph, you only reply with the Python code of Matplotlib to plot the graph and save it as graph.png. "
                f"The data is in data.csv and its attributes are: {metadata_str}. If the user does not ask for a graph, you only reply with the answer to the query. "
                f"The user asks: {user_query}"
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt_eng}
                ]
            )

            # Initialize placeholder for displaying generated content
            generated_content = st.empty()
            all_text = ""

            # Display generated content dynamically
            for choice in response.choices:
                print(f"Debug - choice structure: {choice}")  # Debugging line
                message = choice.message
                print(f"Debug - message structure: {message}")  # Debugging line
                chunk_message = message.content if message else ''
                all_text += chunk_message
                generated_content.text(all_text)

            # Extract the code block
            code_start = all_text.find("```python") + 9
            code_end = all_text.find("```", code_start)
            code = all_text[code_start:code_end]

            # Display the code block
            generated_content.code(code, language="python")

            # If response in its entirety is a code, execute it
            if 'import matplotlib' in code:
                try:
                    exec(code)
                    st.image("graph.png")
                except Exception as e:
                    prompt_eng = f"There has occurred an error while executing the code, please take a look at the error and strictly only reply with the full python code do not apologize or anything just give the code {str(e)}"
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt_eng}
                        ]
                    )
                    all_text = ""
                    for choice in response.choices:
                        print(f"Debug - choice structure: {choice}")  # Debugging line
                        message = choice.message
                        print(f"Debug - message structure: {message}")  # Debugging line
                        chunk_message = message.content if message else ''
                        all_text += chunk_message
                        generated_content.text(all_text)

                    # Extract the code block
                    code_start = all_text.find("```python") + 9
                    code_end = all_text.find("```", code_start)
                    code = all_text[code_start:code_end]

                    # Display the code block
                    generated_content.code(code, language="python")
                    try:
                        exec(code)
                        st.image("graph.png")
                    except Exception as e:
                        st.error("Failed to generate the chart. Please try later.")

    else:
        st.sidebar.info("Please upload a CSV file first.")

if __name__ == "__main__":
    main()
