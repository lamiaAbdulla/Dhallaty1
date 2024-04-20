import streamlit as st
import boto3
import os
import pandas as pd

st.set_page_config(page_title="Dhallaty", page_icon=":mag_right:", layout="wide")

st.image("https://dhallaty-imagess.s3.amazonaws.com/dhallaty+logo.png", width = 400)


credentials = {"444@pnu.edu.sa": "1", "username2": "password2"}

username = st.text_input("Username:")
password = st.text_input("Password:", type="password")  


if st.button("Login"):
  if username in credentials and credentials[username] == password:
    st.success("Login successful!")
    
    st.write("Welcome,", username)
    st.page_link("pages/User.py", label="Home", icon="🏠")
  else:
    st.error("Invalid username or password.")

