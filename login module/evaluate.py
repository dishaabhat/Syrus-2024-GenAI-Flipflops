import streamlit as st
from firebase_admin import auth

# access the session state from start_interview.py
from start_interview import st

def evaluate_app():
    # check if login
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    # if not login then go to login page
    if st.session_state.username == '':
        st.title('Welcome user to your :violet[Evaluation of Interview]')
        st.write('Evaluate your interview skills.')
        st.subheader('Please login to continue')
        st.subheader('You can login from the sidebar')
        return

    else:
        # goto start_interview.py
        st.title('Welcome ' + st.session_state["username"] + ' to your :violet[Evaluation of Interview]')
        # print the metrics from start_interview.py in sesssion state
        st.write('Your interview has been evaluated')
        st.write('You can see the interaction below:')
        st.write(st.session_state.interaction)

