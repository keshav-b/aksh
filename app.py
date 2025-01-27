import streamlit as st
from audio_recorder_streamlit import audio_recorder
from questions import *
import time


if 'show_main' not in st.session_state:
    st.session_state.show_main = False


st.session_state.user_email = None

if 'login_code' not in st.session_state:
    st.session_state.login_code = None

if 'show_email' not in st.session_state:
    st.session_state.show_email = True

if 'signed_in' not in st.session_state:
    st.session_state.signed_in = False

if 'feedback_generated' not in st.session_state:
    st.session_state.feedback_generated = False

if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None

if 'session_rubric' not in st.session_state:
    st.session_state.session_rubric = None


if st.session_state.feedback_generated==False:
    if st.session_state.show_email == True:
        st.header("Start your PM interview journey")
        st.session_state.user_email = st.text_input('Enter your email', placeholder="youare@awesome.com")
        
        login_button = st.button("Request Code")
        if login_button:
            if save():
                login()
                st.session_state.show_email = False
                st.rerun()
            else:
                st.warning('Only 1 try per day', icon="⚠️")
                st.session_state.show_email = True
                # st.session_state.signed_in =True

    if st.session_state.show_email == False and st.session_state.signed_in == False:
        st.header("Start your PM interview journey")
        st.session_state.login_code = st.text_input('Enter the code you received on your email')
        sign_in = st.button("Sign In")

        if sign_in:
            if st.session_state.login_code == st.session_state.session_otp:
                with st.spinner('Your login was successful!'):
                    time.sleep(2)
                st.session_state.show_main = True
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error('Wrong login code', icon="🚨")
                with st.spinner(''):
                    time.sleep(2)
                    st.session_state.show_email = True
                    st.session_state.signed_in = False
                    st.rerun()


    if st.session_state.show_main == True:
        show_columns = st.button("↩️", key="Show_columns_button")


        if 'show_columns' not in st.session_state:
            st.session_state.show_columns = True


        if  "generate_clicked" not in st.session_state:
            st.session_state.generate_clicked = False

        if "audio_recorded" not in st.session_state:
            st.session_state.audio_recorded = False

        if show_columns:
            st.session_state.show_columns = not st.session_state.show_columns
            st.session_state.generate_clicked = False

        if st.session_state.show_columns:
            col1, col2 = st.columns(2)

            with col1:
                # category = st.selectbox("Select category", ["🎲 Random", "🤝🏽 Behavior", "🤔 Guesstimation", "🎨 Product Design", "🚀 Product Strategy"])
                category = st.selectbox("Select category", ["🤝🏽 Behavior"])
                st.session_state.category = category
                if st.button("Generate question"):
                    st.session_state.show_columns = False
                    st.session_state.generate_clicked = True
                    st.rerun()
            with col2:
                pass

                
        if  st.session_state.generate_clicked:
            st.divider()
            question, st.session_state.session_rubric = choose_question()
            st.header(question)
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                pass
            with col2:
                st.session_state.audio_bytes = audio_recorder(text="", icon_size="7x", pause_threshold=10, sample_rate=41_000)
            with col3:
                pass
            st.caption("Whenever you are ready, click on the mic to record your answer. You're awesome you don't need luck!")
            st.caption("Once you are done, click on the mic again and I'll save the recording!")

        


        # st.divider()
        # if st.session_state.generate_clicked:
            # with st.spinner('Generating Feedback'):
        if st.session_state.audio_bytes:
            with open("recording.wav", "wb") as f:
                f.write(st.session_state.audio_bytes)
                # st.audio(st.session_state.audio_bytes, format="audio/wav")


            # st.success('Feedback being generated.....', icon="⏳")
            
            
            st.session_state.feedback_generated = True
            st.rerun()


if st.session_state.feedback_generated == True:
    speech2text()
    check_answer()
    
    


