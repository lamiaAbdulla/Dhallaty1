import streamlit as st

#logo_image = st.image(r'C:\Users\lamoa\Downloads\dhallaty logo.png', width=500)

# Placeholder for storing usernames and passwords (replace with a database or secure storage)
credentials = {"444@pnu.edu.sa": "1", "username2": "password2"}
 
# Login form elements
username = st.text_input("Username:")
password = st.text_input("Password:", type="password")  # Hide password input

# Login button and logic
if st.button("Login"):
  if username in credentials and credentials[username] == password:
    st.success("Login successful!")
    # Display user-specific content here (replace with your desired functionality)
    st.write("Welcome,", username)
    st.page_link("main.py", label="Home", icon="🏠")
  else:
    st.error("Invalid username or password.")
