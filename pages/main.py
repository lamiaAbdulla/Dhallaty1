import csv
import io
import os
import openai
import streamlit as st
import time
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

def configure():
    load_dotenv()


openai.api_key = os.getenv("api_secret")

configure()

responses_df = pd.read_csv("secure_responses.csv", encoding='utf-8') if "secure_responses.csv" in os.listdir() else pd.DataFrame()

st.set_page_config(page_title="Dhallaty", page_icon=":mag_right:", layout="wide")


# User input page
st.title("مساعدك لضالتك")


def join_and_submit(text_input, uploaded_file):

  data = {}
  data["text"] = text_input
  if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    image = Image.open(io.BytesIO(bytes_data))  # Convert bytes to image
    data["image"] = bytes_data  # Store image data with key "image"
  return data

user_input = st.text_area("اوصف ضالتك هنا")
uploaded_file = st.file_uploader("ارفقي صورة للغرض إن وجد")

#التيمب ليست هنا بس حطيتها عشان بعد كل  ريكويست يطلع شكل تحليل جي بي تي له في نفس الصفحة
temp_list = []
if 'temp_list' not in st.session_state:
      st.session_state['temp_list'] = temp_list

if st.button("ارسلي الوصف"):
    joined_data = join_and_submit(user_input, uploaded_file)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Please analyze the following description of a lost item and ONLY ANSWER with this exact format. type, brand, color, place. stick with the format,FOUR sections only.you can answer with a sorry message if you did not understand the input. NOTE: here is some words that you might face with their definitions (1- حلق = Earrings 2- شنطة = bag 3- سلسال = necklace 4- سواره = bracelet):\n{user_input}"},
 ])

    analysis = response.choices[0].message.content

    if len(analysis.split(",")) >= 4:
     new_row = pd.DataFrame({"description": [user_input], "analysis": [analysis],"Photo": joined_data.get("image", None)})
     responses_df = pd.concat([responses_df, new_row], ignore_index=True)

    #Save to CSV
     responses_df.to_csv("secure_responses.csv", index=False)

     st.success("تم إرسال وصفك للقسم الأمني.")
    else:
       st.error("حدث فشل في إرسال الطلب، الرجاء التأكد من ارسال وصف واضح ") 

    #هنا يعرض التيمب ليست (فقط للتأكد انها مضبوطه))
    #test_list = analysis.split(",")
    #st.write(test_list)

#  -----------------------------------------end of openai.chat.completions.create --------------------------------------------------

    
def edit_df1():
  items_with_description = {"items": {}}

  for row in responses_df.itertuples():
    try:

      description = row.description
      Photo = row.Photo
      analysis = str(row.analysis)  #ensure that it is a string
      analysis_list = analysis.split(",")

      if len(analysis_list) >= 4:
        #Create a unique key based on a counter 
        item_key = f"item{len(items_with_description['items']) + 1}"
        items_with_description["items"][item_key] = {
          "analysis": analysis_list[:4],
          "description": description,
          "Photo": Photo
        }
    except (KeyError, AttributeError) as e:

      print(f"Error processing row: {row.Index} - {e}")

  return items_with_description
 
  
lost_items = edit_df1() 
st.session_state["lost_items"] = lost_items
#st.write(lost_items.items()) # عشان اتأكد من القيم فقط