
import csv
import io
import struct
import streamlit as st
import openai
import pandas as pd
import os
from collections import defaultdict
from PIL import Image

st.set_page_config(page_title="Dhallaty", page_icon=":mag_right:", layout="wide")

security_responses_file = "secure_security_responses.csv"
security_responses_df = pd.read_csv(security_responses_file) if os.path.exists(security_responses_file) else pd.DataFrame()


def edit_df2():
  items_with_description = {"items": {}}

  for row in security_responses_df.itertuples():
    try:
      description = row.description

      analysis = str(row.analysis)  
      analysis_list = analysis.lower().split(",")

      if len(analysis_list) >= 4:
        item_key = f"item{len(items_with_description['items']) + 1}"
        items_with_description["items"][item_key] = {
          "analysis": analysis_list[:4],
          "description": description
        }
    except (KeyError, AttributeError) as e:
      print(f"Error processing row: {row.Index} - {e}")

  return items_with_description


found_items = edit_df2()
st.session_state["found_items"] = found_items
lost_items = st.session_state["lost_items"]



def jaccard_similarity_ranked(query_doc, documents):

  query_set = set(query_doc)

  descriptions = [item["description"] for item in documents["items"].values()]
  analysis_sets = [set(item["analysis"]) for item in documents["items"].values()]
  image = [item.get("image", None) for item in documents["items"].values()]

 
  similarities = [
      len(query_set.intersection(analysis_set)) / float(len(query_set.union(analysis_set)))
      if len(query_set.union(analysis_set)) > 0 else 0
      for analysis_set in analysis_sets
  ]

  sorted_indices = sorted(range(len(similarities)), key=similarities.__getitem__, reverse=True)


  sorted_docs = [ # to store documents
      {
          "analysis": list(documents["items"][list(documents["items"].keys())[i]]["analysis"]),
          "description": descriptions[i],
          "similarity": similarities[i]*100,
          "image": image[i]
      }
      for i in sorted_indices
  ]

  return sorted_docs



#security input page
st.title("ماذا وجدتِ")
security_input = st.text_area("اوصفي الذي وجدتيه هنا")


if st.button("ارسلي الوصف"):

    security_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Please analyze the following description of a lost item and ONLY ANSWER with this exact format. type, brand, color, place. stick with the format,FOUR sections only (NO MATTER WHAT). you can answer with a sorry message if you did not understand the input. NOTE: here is some words that you might face with their definitions (1- حلق = Earrings 2- شنطة = bag 3- سلسال = necklace 4- سواره = bracelet 5- ريال = money):\n{security_input}"},
 ])

    found_analysis = security_response.choices[0].message.content
  
    if len(found_analysis.split(",")) >= 4:
        secuirty_new_row = pd.DataFrame({"description": [security_input], "analysis": [found_analysis]})
        secuirty_responses_df = pd.read_csv(security_responses_file) if os.path.exists(security_responses_file) else pd.DataFrame()
        secuirty_responses_df = pd.concat([secuirty_responses_df, secuirty_new_row], ignore_index=True)


        try:
            secuirty_responses_df.to_csv(security_responses_file, index=False)
            st.success("تم حفظ الوصف و يمكنك تفقد خانة التطابقات لرؤية قائمة المفقودات")

        except PermissionError:
            st.error("حدث فشل في إرسال الطلب، الرجاء التأكد من ارسال وصف واضح ")

    else:
        st.error("حدث فشل في إرسال الطلب، الرجاء التأكد من ارسال وصف واضح ") 


#  -----------------------------------------end of openai.chat.completions.create --------------------------------------------------


st.title("التطابقات")
selected_item = st.selectbox("اختاري طلب لإظهار التطابقات", [f'{item["description"]}'  for item in found_items["items"].values()])


selected_item_info = None
for item_key, item in found_items["items"].items():
  if item["description"] == selected_item:
    selected_item_info = item
    break

if selected_item_info:
    similarity_score = jaccard_similarity_ranked(selected_item_info["analysis"], lost_items)
    df = pd.DataFrame(similarity_score)  

    edited_df = st.data_editor(
        df,
        column_config={
            "image": st.column_config.ImageColumn(
                "Preview Image", width = "medium"
            )
        },
       hide_index=True
    )
