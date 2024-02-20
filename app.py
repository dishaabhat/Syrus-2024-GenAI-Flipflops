import streamlit as st
import PyPDF2
import os
import google.generativeai as genai
import numpy as np
import math
from dotenv import load_dotenv
load_dotenv()
# no wide mode
st.set_page_config(page_title="Streamlit App", page_icon=":shark:", layout="centered", initial_sidebar_state="auto")

st.title("Mock Interview")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
text_model= genai.GenerativeModel("gemini-pro")

st.write("Welcome to the mock interview app. This app will help you prepare for your next interview. You can practice your responses to common interview questions and receive feedback on your responses.")

def getallinfo(data):
    text = f"{data} is not properly formatted for this model. Please try again and format the whole in a single paragraph covering all the information."
    response = text_model.generate_content(text)
    response.resolve()
    return response.text

def file_processing(uploaded_file):
    # upload pdf of resume
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


uploaded_file = st.file_uploader("Upload your resume in simple Document Format", type=["pdf"])
roles_applied = []
if uploaded_file is not None:
    st.write("File uploaded successfully!")
    data = file_processing(uploaded_file)
    st.write(data)
    st.write(getallinfo(data))
    updated_data = getallinfo(data)
    st.write(updated_data)
