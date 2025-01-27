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
    



# secrets = {
#             "🤝🏽 Behavior" : 
#             {
#                     "questions": [["Describe a difficult interaction you had with a customer.", # Customer Obsession
#                                 "Give me an example of when you asked for customer feedback.",
#                                 "Tell me about a time when you had to balance the needs of the customer with the needs of the business.",
#                                 "Tell me about a time when you went above and beyond for a customer.",
#                                 "Tell me about a time when you had to deal with a very difficult customer."
#                                 ],
#                                 ["Tell me about a time when you solved a complex problem.", #Dive Deep
#                                  "Walk me through a bog problem or issue in your org that you helped solve.",
#                                  "Tell me time you worked on an analytical problem",
#                                  "Tell me about a time when you thought of diverse perspectives to solve a problem",
#                                  "Tell me about a time when you were able to make a decision without having much data metrics in hand."
#                                 ],
#                                 ["Tell me about a time when you had to get a buy-in.", #Deliver results
#                                  "Give me an example of a tough or critical piece of feedback you received.",
#                                  "Tell me about a time when you had communicate bad/ dissapointing news to your peers/ team.",
#                                  "Tell me about a time when you influenced a peer/ or your manager."
#                                  "Tell me about a time when you influenced a peer/ or your manager."
#                                 ],
#                                 ["Tell me about a time you made a bold and difficult decision.", #Ownership
#                                  "Describe a tough situation in which you had to step into a leadership role.",
#                                  "Tell me about a tough decision you made during a project. ",
#                                  "Tell me about a time when you took on something significantly outside your area of responsibility",
#                                  "Describe a time when you didn't think you were going to meet a commitment you promised"
#                                 ]
#                                 ],
#                     "rubric": ["The candidate did not do a good job if its the following: - Makes decisions or takes actions without adequately considering the customer impact - Fails to collect or respond to customer input appropriately - Fails to meet customer commitments - Loses and doesn't regain customers' trust - Develops a project approach based on industry trends rather than customer needs - Unable to identify primary customers \n \n The candidate did a good job if its the following:- Takes actions guided by customer input- Works backwards from the optimal customer experience- Tries to surprise and delight the customer- Applies time and energy to make the customer experience more efficient or enjoyable- Identifies new ways of gathering feedback from customer- Listens to feedback from customers and uses it to make improvements- Pushes back when necessary to ensure that decisions consider what is best for customer in the long-term- Earns customers trust by delivering promised services and products which meet or exceed expectation- Stops activities that no longer enhance the customer experience",
#                                "The candidate did not do a good job if its the following: - Does not understand the details of projects- Does not understand how different groups or Systems work together - Only holds surface-level understanding of metrics and data - Does not question assumptions - Unable to step in and get work done \n\nThe candidate did a good job if its the following: - Stays connected to the details of projects and programs - Understands how different groups or systems work together - Critically evaluates metrics and data - Asks good questions that provide clarity to situations - Steps in and gets work done - Investigates and get details in order to solve a problem - Gathers information to solve a problem, even if it's difficult or time-consuming",
#                                "The candidate did not do a good job if its the following: - Fails to treat others and their ideas with respect - Blames others for mistakes - Denies or covers up mistakes - Publicly criticizes or humiliates others \n\nThe candidate did a good job if its the following: - Builds positive working relationships by treating others and their ideas with respect - Seeks out and accepts feedback for self or team - Takes responsibility for shortfalls - Openly acknowledges mistakes - Provides feedback to others in a respectful manner - Represents data and information entirely transparently - Honors commitments and makes good on promises"
#                                "The candidate did not do a good job if its the following: - Makes decisions for short-term team success rather than long-term value- Describes setbacks or problems without talking about how to address them- Relies on others to remove roadblocks- Avoids tough decisions- Avoids addressing problems that are in others' work areas- Blames others for setbacks- Assigns work to others because the work is undesirable- Walks away if there are too many difficulties Creates solutions that negatively impact other teams \n \n The candidate did a good job if its the following: -Actively makes improvements outside of one's area of responsibility- Makes decisions that consider risks and future outcomes- Makes decisions that are scalable and contribute to long-term success- Takes the lead in solving problems- Takes accountability for dependencies and their work- Takes ownership for mistakes- Accepts responsibility- Inspires others to take ownership- Sees things through to completion"
#                                ]
#             }
#         }


def choose_question():
    
    rand = random.randint(2,21)
    

    row = worksheet_list[1].row_values(21)

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