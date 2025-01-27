import random
import streamlit as st
from openai import OpenAI
import smtplib
import pandas as pd
from datetime import datetime, timedelta 

from email.message import EmailMessage
import gspread
from google.oauth2.service_account import Credentials
import assemblyai as aai
import os

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = st.secrets['gspread_credentials']

creds = Credentials.from_service_account_info(credentials,scopes=scopes)
client = gspread.authorize(creds)



sheet = client.open_by_key(st.secrets.sheet_id)
worksheet_list = sheet.worksheets()




client = OpenAI(api_key=st.secrets["api_key"])

if 'session_otp' not in st.session_state:
    st.session_state.session_otp = ""

if 'session_question' not in st.session_state:
    st.session_state.session_question = ""

if 'session_answer' not in st.session_state:
    st.session_state.session_answer = ""

if 'session_feedback' not in st.session_state:
    st.session_state.session_feedback = ""

if 'connection' not in st.session_state:
    st.session_state.connection = None



def login():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0,9))
        st.session_state.session_otp = otp

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    from_mail = 'balachandarkeshav@gmail.com'
    server.login(from_mail, st.secrets.gmail_code)
    msg = EmailMessage()
    msg['Subject'] = "Verify you account | AI PM Interviewer"
    msg['From'] = from_mail
    msg['To'] = st.session_state.user_email

    msg.set_content(f"Your login code is: {otp}")
    server.send_message(msg)



def save():    
    cell = sheet.sheet1.find(st.session_state.user_email)

    print(cell)
    
    if cell:
        print("----cell is present----")
        all = sheet.sheet1.get_all_records()
        for record in all:
            if record['user'] == st.session_state.user_email:
                timestamp_value = record['timestamp']
                break

        timestamp_dt = datetime.strptime(timestamp_value, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        
        if current_time - timestamp_dt < timedelta(hours=24):
            print("----less than 24h----")
            return False
        else:
            print("----present but more than 24h----")
            current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # sheet.sheet1.append_row([st.session_state.user_email, current_time_str])
            dataframe = pd.DataFrame(all)
            
            # Get the row where the "user" column matches st.session_state.user_email
            user_row = dataframe[dataframe['user'] == st.session_state.user_email]
            row_index = user_row.index[0] + 2
            sheet.sheet1.update_acell(f'B{row_index}', current_time_str)
            return True
    else:
        print("----not present----")
        current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.sheet1.append_row([st.session_state.user_email, current_time_str])
        return True


def choose_question():
    rand = random.randint(2,21)
    row = worksheet_list[1].row_values(rand)
    st.session_state.session_question = row[1]
    rubric = row[2]
    return st.session_state.session_question, rubric




def speech2text():
    aai.settings.api_key = st.secrets.assembly_api_key
    FILE_URL = "recording.wav"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(FILE_URL)

    
    st.session_state.session_answer = transcript.text

    st.warning('Only 1 try per day, Retry after 24h', icon="⚠️")
    st.header(st.session_state.session_question)
    with st.expander("Your Answer"):
        st.write(st.session_state.session_answer)

    if st.session_state.audio_bytes:
                with open("recording.wav", "wb") as f:
                    f.write(st.session_state.audio_bytes)
                st.audio(st.session_state.audio_bytes, format="audio/wav")
                st.caption("Yes, I know, listening to your own voice is about as fun as stepping on a LEGO, but trust me, it’s worth it for interview prep. Embrace the cringe and do it!")

    st.divider()
    st.empty()
    st.empty()
    st.empty()
    st.empty()
    st.empty()


def check_answer():
    # content = "f"+st.secrets.content
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": st.secrets.system_prompt},
        {
            "role": "user",
            "content": f"Question: {st.session_state.session_question} \n Candidate's answer: {st.session_state.session_answer} \n Rubric: {st.session_state.session_rubric}"
        }
    ]
    )
    st.session_state.session_feedback = completion.choices[0].message.content   
    st.subheader("Feedback")
    st.text(st.session_state.session_feedback)
    st.divider()


def send_answer():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    from_mail = 'balachandarkeshav@gmail.com'
    server.login(from_mail, st.secrets.gmail_code)
    msg = EmailMessage()
    msg['Subject'] = "Your feedback"
    msg['From'] = from_mail
    msg['To'] = st.session_state.user_email

    msg.set_content(f"Nice job on the question, here's your feedback. \n Question: {st.session_state.session_question} \n Your answer: {st.session_state.session_answer} \n Feedback: {st.session_state.session_feedback}")
    server.send_message(msg)
