import streamlit as st
import PyPDF2
import os
import google.generativeai as genai
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel
import numpy as np
import math
from dotenv import load_dotenv
import matplotlib.pyplot as plt  # Added for visualization

load_dotenv()
# no wide mode
st.set_page_config(page_title="Streamlit App", page_icon=":shark:", layout="centered", initial_sidebar_state="auto")

st.session_state()
st.title("Mock Interview")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
text_model = genai.GenerativeModel("gemini-pro")

st.write(
    "Welcome to the mock interview app. This app will help you prepare for your next interview. You can practice your responses to common interview questions and receive feedback on your responses.")


def getallinfo(data):
    # text = f"{data} is not properly formatted for this model. Please try again with a different format."
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


# Load the pre-trained BERT model
model = TFBertModel.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


# Function to preprocess text and get embeddings
def get_embedding(text):
    encoded_text = tokenizer(text, return_tensors="tf")
    output = model(encoded_text)
    embedding = output.last_hidden_state[:, 0, :]
    return embedding


# Function to generate feedback (replace with your logic)
def generate_feedback(question, answer):
    # Ensure correct variable name (case-sensitive)
    question_embedding = get_embedding(question)
    answer_embedding = get_embedding(answer)

    # Enable NumPy-like behavior for transpose
    tf.experimental.numpy.experimental_enable_numpy_behavior()

    # Calculate similarity score (cosine similarity)
    similarity_score = np.dot(question_embedding, answer_embedding.T) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(answer_embedding))

    # Generate basic feedback based on similarity score
    corrected_string = f"Feedback: {np.array2string(similarity_score, precision=2)}"
    # print(corrected_string)
    return corrected_string


# # Example usage
# question = "What is your experience with designing and implementing cloud infrastructure?"
# answer = "In my previous role I led the design and implementation of cloud-based solutions using AWS. I have experience with services such as EC2 S3 RDS and Lambda and have designed scalable and cost-effective architectures to meet business requirements."
# feedback = generate_feedback(question, answer)
# # print(feedback)

def generate_questions(roles, data):
    questions = []
    text = f"this is a resume overview of the candidate. The candidate details are in {data}. The candidate has applied for the role of {roles}. Generate questions for the candidate based on the role applied and on the Resume of the candidate. Not always necceassary to ask only technical questions related to the role. Ask some personal questions too. Ask no additional questions. Max 5 questions. but not less than 3 questions. Dont categorize the questions."
    response = text_model.generate_content(text)
    response.resolve()
    # split the response into questions
    questions = response.text.split("?\n")
    return questions


def generate_overall_feedback(data, percent, answer, questions):
    # st.write(percent)
    # avg = math.ceil(sum(percent)/len(percent))
    # test = f"This is the resume overview of the candidate {data}. Based on the answers provided, the candidate has scored {percent}% in the interview. Dont disclose the percent but rate the interview experience out of 10. The candidate has answered the following questions: {questions}. The candidate has answered the questions as follows: {answer}. Give overall feedback to the candidate based on the answers provided. and the Areas to improve for the candidate. Always talk with candidate while taking their name. Dont give any big answer it should be small 2 paragraphs. 1st para about score and how candidate did the interview. 2nd para about the areas to improve. See to that the user is not faking anything and the questions asked on resume matches the answers given by the candidate. If the user is faking then give a feedback that the user is faking and ask the user to be honest."
    test = f"Here is the overview of the candidate {data}. In the interview the questions asked were {questions}. The candidate has answered the questions as follows: {answer}. Based on the answers provided, the candidate has scored {percent}. tell the average percent and rate the interview out of 10. Give the feedback to the candidate about the interview and areas of improvements. While talking to candidate always take their name. Dont give any big answer it should be small 2 paragraphs. 1st para about score and how candidate did the interview. 2nd para about the areas to improve. See to that the user is not faking anything and the questions asked on resume matches the answers given by the candidate. If the user is faking then give a feedback that the user is faking and ask the user to be honest."
    # st.write(test)
    response = text_model.generate_content(test)
    response.resolve()
    return response.text


def create_answer_box(answers, ansno):
    answers.append(st.text_area(f"Answer the question {ansno}:", key=ansno))
    return answers

def visualize_accuracy(interactions):
    text = f"here is the interaction of the whole interview of the candidate. generate me some factors for which i can plot"

    plt.figure(figsize=(8, 6))
    plt.pie(scores, labels=[f"Question {i+1}" for i in range(len(scores))], autopct='%1.1f%%', startangle=140)
    plt.title("Accuracy Scores")
    st.pyplot()


uploaded_file = st.file_uploader("Upload your resume in simple Document Format", type=["pdf"])
roles_applied = []
if uploaded_file is not None:
    st.write("File uploaded successfully!")
    data = file_processing(uploaded_file)
    # st.write(data)
    # st.write(getallinfo(data))
    updated_data = getallinfo(data)
    # st.write(updated_data)
    roles = st.multiselect("Select your job role:",
                           ["Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
                            "Business Analyst"])
    if roles:
        roles_applied.append(roles)
        st.write(f"Selected roles: {roles}")
        questions = generate_questions(roles, updated_data)
        # for each question in the questions, ask the user to answer the question
        feedback = []
        answers = []
        interactions = {}
        for i in range(len(questions)):
            st.write(questions[i])
            answers = create_answer_box(answers, i + 1)
            interactions[questions[i]] = answers[i]
            st.session_state()
        if st.button("Submit"):
            if len(answers) != len(questions):
                print(interactions)
                st.error("Please answer all the questions.")
                st.stop()

            for i in range(len(questions)):
                feedback.append(generate_feedback(questions[i], answers[i]))
            if feedback:
                st.write(generate_overall_feedback(updated_data, feedback, answers, questions))
                st.stop()
                st.success('Thank you.')

    else:
        st.write("Please select at least one role.")
