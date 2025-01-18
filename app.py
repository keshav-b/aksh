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

    audio_bytes = None

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
            category = st.selectbox("Select category", ["🎲 Random", "🤝🏽 Behavior", "🤔 Guesstimation", "🎨 Product Design", "🚀 Product Strategy"])
            st.session_state.category = category
            if st.button("Generate question"):
                st.session_state.show_columns = False
                st.session_state.generate_clicked = True
                st.rerun()
        with col2:
            pass

            
    if  st.session_state.generate_clicked:
        st.divider()
        question, rubric = choose_question(st.session_state.category)
        st.header(question)
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            pass
        with col2:
            audio_bytes = audio_recorder(text="", icon_size="7x", pause_threshold=10)
        with col3:
            pass
        st.caption("Whenever you are ready, click on the mic to record your answer. You're awesome you don't need luck!")

    if audio_bytes:
        with open("recording.wav", "wb") as f:
            f.write(audio_bytes)
        st.audio(audio_bytes, format="audio/wav")
        st.session_state.audio_recorded = True

    st.divider()
    # st.session_state.audio_recorded = True # just for quick testing
    # answer = """
    #             At Walmart, during my PM internship, I was tasked with improving adoption for a feature in our logistics platform. A key enterprise customer, responsible for a significant portion of our revenue, had reported dissatisfaction with the feature, claiming it didn’t address their specific use case. This escalated to leadership, putting pressure on me to resolve it.
    #             My goal was to understand their pain points, ensure they felt heard, and determine whether the issue was a product gap or a miscommunication. I also needed to balance their needs with our roadmap priorities.
    #             Customer Empathy: I organized a call with the customer to listen directly to their concerns. Rather than jumping to conclusions, I asked probing questions to understand the nuances of their workflows and why our solution wasn’t fitting their needs.

    #             Internal Collaboration: Post-call, I facilitated a meeting with the engineering and design teams to analyze the feasibility of their requests. I mapped their concerns to our product capabilities and identified a misalignment in how they were using the feature compared to how it was designed.

    #             Solution Design: I worked with the customer to co-create a temporary workaround while advocating for a longer-term fix in our backlog. I provided them with tailored documentation and a clear timeline for the planned updates.

    #             Proactive Communication: I kept the customer updated weekly on our progress, ensuring transparency. Simultaneously, I conducted an impact analysis and shared it with leadership to secure buy-in for prioritizing the fix.


    #             The customer was satisfied with the transparency and the temporary solution, allowing them to meet their immediate business goals. Once the fix was deployed, their adoption of the feature increased by 30%, and their NPS improved significantly. The episode also revealed a broader gap in how we communicated feature use cases to customers, leading us to improve onboarding materials for all users.


    #         """
    if st.session_state.generate_clicked and st.session_state.audio_recorded:
        answer = speech2text()
        
        with st.expander("Your Answer"):
            st.write(answer)

        feedback = check_answer(question, answer, rubric)
        st.divider()
        st.subheader("Feedback")
        st.text(feedback)






