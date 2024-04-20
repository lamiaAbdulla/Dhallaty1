import csv
import io
import os
import openai
import streamlit as st
import time
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
import boto3



def configure():
    load_dotenv()


openai.api_key = os.getenv("api_secret")
#for aws
SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
KEY_ID = os.getenv("KEY_ID")
configure()

responses_df = pd.read_csv("secure_responses.csv", encoding='utf-8') if "secure_responses.csv" in os.listdir() else pd.DataFrame()

st.set_page_config(page_title="Dhallaty", page_icon=":mag_right:", layout="wide")

#-------------------------------start images code block--------------------------------------------

#credentials for s3 aws
REGION_NAME = 'us-east-1'
BUCKET_NAME = 'dhallaty-imagess'


s3 = boto3.client( #S3 client
    's3',
    aws_access_key_id=KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)

#upload images to S3 bucket
def upload_to_s3(file, bucket_name, key):
    s3.upload_fileobj(file, bucket_name, key)
    return st.success("File uploaded successfully!")


def image_url(key):
    public_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{key}"
    return public_url


def uploaded_image():
    uploaded_file = st.file_uploader("أرفقي صورة للغرض إن وجد (سواءً صورة من الإنترنت أو من صورك)")
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        key = uploaded_file.name  
        upload_to_s3(uploaded_file, BUCKET_NAME, key)

        
        processed_image = image_url(key)
        imageUrl = processed_image
        return imageUrl


def join_and_submit(text_input, imageurl = None):
  data = {}

  data["text"] = text_input
  if image_url is not None:
    data["image"] = imageurl 

  return data
#----------------------------------------------end images code block-------------------------------------------------------

#---------------------------------------start of openai.chat.completions.create--------------------------------------------
st.title("مساعدك لضالتك")
st.write(":violet[نرجو كتابة الوصف مع مراعاة (اللون / المكان /العلامة التجارية) ]")

user_input = st.text_area("اوصف ضالتك هنا")
imageUrl = uploaded_image()



if st.button("ارسلي الوصف"):

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Please analyze the following description of a lost item and ONLY ANSWER with this exact format. type, brand, color, place. stick with the format,FOUR sections only (NO MATTER WHAT). you can answer with a sorry message if you did not understand the input. NOTE: here is some words that you might face with their definitions (1- حلق = Earrings 2- شنطة = bag 3- سلسال = necklace 4- سواره = bracelet 5- ريال = money):\n{user_input}"},
 ])

    analysis = response.choices[0].message.content

    joined_data = join_and_submit(user_input, imageUrl)
    if len(analysis.split(",")) >= 4:
     imageUrl = joined_data.get("image", None)
     new_row = pd.DataFrame({"description": [user_input], "analysis": [analysis],"image": [imageUrl]})
     responses_df = pd.concat([responses_df, new_row], ignore_index=True)


     responses_df.to_csv("secure_responses.csv", index=False)

     st.success("تم إرسال وصفك للقسم الأمني.")
    else:
       st.error("حدث فشل في إرسال الطلب، الرجاء التأكد من ارسال وصف واضح ") 


#  -----------------------------------------end of openai.chat.completions.create --------------------------------------------------

    
def edit_df1():
  items_with_description = {"items": {}}

  for row in responses_df.itertuples():
    try:

      description = row.description
      image = row.image
      analysis = str(row.analysis)  #ensure that it is a string
      analysis_list = analysis.lower().split(",")

      if len(analysis_list) >= 4:
        #Create a unique key based on a counter 
        item_key = f"item{len(items_with_description['items']) + 1}"
        items_with_description["items"][item_key] = {
          "analysis": analysis_list[:4],
          "description": description,
          "image": image
        }
    except (KeyError, AttributeError) as e:

      print(f"Error processing row: {row.Index} - {e}")

  return items_with_description
 
  
lost_items = edit_df1() 
st.session_state["lost_items"] = lost_items
