# app/email_utils.py

import smtplib
from email.message import EmailMessage
import os
import streamlit as st

def send_query_email(user_query: str, response):
    sender_email = st.secrets["EMAIL_SENDER"]
    receiver_email = st.secrets["EMAIL_RECEIVER"]
    app_password = st.secrets["EMAIL_APP_PASSWORD"]

    msg = EmailMessage()
    msg.set_content(f"User Text:\n{user_query}\n\nQuestions Generated: {response}")
    msg['Subject'] = '🧠 New Flashcard Query Logged'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        print('Trying to login to the mail server....')
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            print('Logged in!')
            server.send_message(msg)
        print("[✓] Email sent.")
    except Exception as e:
        print(f"[!] Failed to send email: {e}")

if __name__ == "__main__":
    send_query_email('Who was neitzsche', 'ssss')