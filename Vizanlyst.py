import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO
from groq import Groq

# Set page title
st.set_page_config(page_title="Vizanlyst", layout="wide")

# Sidebar for API Key
st.sidebar.header("Vizanlyst - Automated Data Analysis")
st.sidebar.header("🔑 Enter Groq API Key")
groq_api_key = st.sidebar.text_input("API Key", type="password")
st.sidebar.markdown("[Get your Groq API Key](https://groq.com)")
st.sidebar.markdown("[☕ Buy Me a Coffee](https://buymeacoffee.com/shreyas.dasari)")

# File uploader
st.header("📊 Upload Your Dataset")
st.write("Upload your dataset, and our system will automatically clean, analyze, and visualize it. This tool helps data analysts and business professionals save hours of manual work by generating insights quickly. [View the GitHub Repository](https://github.com/your-repo-link)")
file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

def clean_data(df):
    """Automated data cleaning: handling missing values, outliers, and formatting."""
    df = df.drop_duplicates()
    df = df.dropna(thresh=len(df) * 0.5, axis=1)  # Remove columns with >50% missing
    df.fillna(df.median(numeric_only=True), inplace=True)  # Impute numerical columns
    df.fillna(df.mode().iloc[0], inplace=True)  # Impute categorical columns
    return df

if file:
    ext = os.path.splitext(file.name)[1]
    if ext == ".csv":
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    st.success("File uploaded successfully!")
    
    # Cleaning data
    df = clean_data(df)
    
    # Display basic statistics
    st.subheader("📌 Dataset Overview")
    st.write(df.head())
    
    # Send data to Groq for unique visualizations
    if groq_api_key:
        st.subheader("📈 AI-Generated Data Insights")
        client = Groq(api_key=groq_api_key)
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes datasets and provides visual insights."},
                    {"role": "user", "content": f"Analyze this dataset and generate key visualizations: {df.describe().to_string()}"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )
            insights = chat_completion.choices[0].message.content
            st.write(insights)
        
            # User can ask for custom visualizations
            st.subheader("🎨 Generate Custom Visualizations")
            user_query = st.text_input("Describe the visualization you want to generate")
            if user_query:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a data visualization assistant that creates charts based on user input."},
                        {"role": "user", "content": f"Using this dataset, generate a visualization for: {user_query}. The dataset details: {df}"}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    max_completion_tokens=1024,
                    top_p=1,
                    stop=None,
                    stream=False,
                )
                custom_viz = chat_completion.choices[0].message.content
                st.write(custom_viz)

            # Generate Python code dynamically using Groq API
            code_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a Python expert who writes data analysis scripts."},
                    {"role": "user", "content": f"Write a Python script that loads the following dataset, cleans it, and generates key visualizations. The dataset details: {df}"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=2048,
                top_p=1,
                stop=None,
                stream=False,
            )
            python_code = code_completion.choices[0].message.content
           
        except Exception as e:
            st.error(f"Error connecting to Groq API: {e}")
    else:
        st.warning("Please enter a valid Groq API Key.")
    
    
    
    st.subheader("📜 Download Auto-Generated Code")
    st.download_button("📥 Download Python Code", python_code, file_name="data_analysis.py", mime="text/x-python")