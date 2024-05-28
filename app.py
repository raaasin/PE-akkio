import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure GenerativeAI
genai.configure(api_key=GOOGLE_API_KEY)

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
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            chat = model.start_chat(history=[])
            prompt_eng=(
                f"You are graphbot. If the user asks to plot a graph, you only reply with the Python code of Matplotlib to plot the graph and save it as graph.png. "
                f"The data is in data.csv and its attributes are: {metadata_str}. If the user does not ask for a graph, you only reply with the answer to the query. "
                f"The user asks: {user_query}"
            )
            response = chat.send_message(prompt_eng, stream=True,generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0.2))

            # Initialize placeholder for displaying generated content
            generated_content = st.empty()
            all_text = ""
            # Display generated content dynamically
            for chunk in response:
                # Update the content dynamically
                all_text += chunk.text
                generated_content.text(all_text)
            
            # Display the code block
            code = response.text.replace("```python", "").replace("```", "")
            generated_content.code(code, language="python")

            # If response in its entirety is a code, execute it
            if '```python' in response.text:
                try:
                    exec(code)
                    st.image("graph.png")
                    
                except Exception as e:
                    prompt_eng="there has occured an error while executing the code, please take a look at the error and strictly only reply with the full python code do not apologize or anything just give the code "+str(e)
                    response = chat.send_message(prompt_eng, stream=True,generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    temperature=0.2))
                    all_text = ""
                    # Display generated content dynamically
                    for chunk in response:
                        # Update the content dynamically
                        all_text += chunk.text
                        generated_content.text(all_text)
                    # Display the code block
                    code = response.text.replace("```python", "").replace("```", "")
                    generated_content.code(code, language="python")
                    try:
                        exec(code)
                        st.image("graph.png")
                    except Exception as e:
                        prompt_eng="Again another error occured, please take a look at the error and strictly only reply with the full python code do not apologize or anything just give the code "+str(e)
                        response = chat.send_message(prompt_eng, stream=True,generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        temperature=0.3))
                        all_text = ""
                        # Display generated content dynamically
                        for chunk in response:
                            # Update the content dynamically
                            all_text += chunk.text
                            generated_content.text(all_text)
                        # Display the code block
                        code = response.text.replace("```python", "").replace("```", "")
                        generated_content.code(code, language="python")
                        try:
                            exec(code)
                            st.image("graph.png")
                        except Exception as e:
                            prompt_eng="Again another error occured, please take a look at the error and strictly only reply with the full python code do not apologize or anything just give the code "+str(e)
                            response = chat.send_message(prompt_eng, stream=True,generation_config=genai.types.GenerationConfig(
                            candidate_count=1,
                            temperature=1))
                            all_text = ""
                            # Display generated content dynamically
                            for chunk in response:
                                # Update the content dynamically
                                all_text += chunk.text
                                generated_content.text(all_text)
                            # Display the code block
                            code = response.text.replace("```python", "").replace("```", "")
                            generated_content.code(code, language="python")
                            try:
                                exec(code)
                                st.image("graph.png")
                            except:
                                generated_content.text("Hey After the 4th try, It seems I'm unable to generate the chart for this query. Please try later again.")
            else:
                st.write(response.text)

    else:
        st.sidebar.info("Please upload a CSV file first.")

if __name__ == "__main__":
    main()
    