
import csv
import io
import struct
import streamlit as st
import openai
import pandas as pd
import os
from collections import defaultdict
from main import edit_df1
#import streamlit.elements.data_frame_editor as data_frame
from PIL import Image

secuirty_responses_file = "secure_secuirty_responses.csv"
secuirty_responses_df = pd.read_csv(secuirty_responses_file) if os.path.exists(secuirty_responses_file) else pd.DataFrame()
#st.session_state["secuirty_responses_df"] = secuirty_responses_df

def edit_df2():
  items_with_description = {"items": {}}

  for row in secuirty_responses_df.itertuples():
    try:
      description = row.description

      analysis = str(row.analysis)  
      analysis_list = analysis.split(",")

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
  """
  Calculates Jaccard similarity between a query document and documents,
  returning sorted documents with descriptions based on analysis key values.
  """
  # Set of unique elements for efficiency
  query_set = set(query_doc)

  descriptions = [item["description"] for item in documents["items"].values()]
  analysis_sets = [set(item["analysis"]) for item in documents["items"].values()]
  Photo = [item["Photo"] for item in documents["items"].values()]
 
  similarities = [
      len(query_set.intersection(analysis_set)) / float(len(query_set.union(analysis_set)))
      if len(query_set.union(analysis_set)) > 0 else 0
      for analysis_set in analysis_sets
  ]

  #Sort documents by similarity in descending order (highest first)
  sorted_indices = sorted(range(len(similarities)), key=similarities.__getitem__, reverse=True)


  sorted_docs = [ # to store documents
      {
          "analysis": list(documents["items"][list(documents["items"].keys())[i]]["analysis"]),
          "description": descriptions[i],
          "similarity": similarities[i],
          "Photo": Photo[i]
      }
      for i in sorted_indices
  ]

  return sorted_docs



#user input page
st.title("ماذا وجدتِ")
secuirty_input = st.text_area("اوصفي الذي وجدتيه هنا")


if st.button("ارسلي الوصف"):

    secuirty_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Please analyze the following description of a lost item and ONLY ANSWER with this exact format. type, brand, color, place. stick with the format,FOUR sections only.you can answer with a sorry message if you did not understand the input. NOTE: here is some words that you might face with their definitions (1- حلق = Earings 2- شنطة = bag 3- سلسال = necklace 4- سواره = bracelet):\n{secuirty_input}"},
 ])

    found_analysis = secuirty_response.choices[0].message.content

    secuirty_new_row = pd.DataFrame({"description": [secuirty_input], "analysis": [found_analysis]})
    secuirty_responses_df = pd.read_csv(secuirty_responses_file) if os.path.exists(secuirty_responses_file) else pd.DataFrame()
    secuirty_responses_df = pd.concat([secuirty_responses_df, secuirty_new_row], ignore_index=True)


    try:
        secuirty_responses_df.to_csv(secuirty_responses_file, index=False)
        st.success("تم حفظ الوصف و سننبهك عند وجود تطابق.")
    except PermissionError:
        st.error("Permission error: Failed to save the description. Please check file permissions.")

    #secuirty_temp_list = found_analysis.split(",") 
    #st.write(secuirty_temp_list) #فقط للتأكد

#  -----------------------------------------end of openai.chat.completions.create --------------------------------------------------


st.title("التطابقات")
selected_item = st.selectbox("اختاري طلب لإظهار التطابقات", [f"{item["description"]}"  for item in found_items["items"].values()])


selected_item_info = None
for item_key, item in found_items["items"].items():
  if item["description"] == selected_item:
    selected_item_info = item
    break

if selected_item_info:
    similarity_score = jaccard_similarity_ranked(selected_item_info["analysis"], lost_items)
    df = pd.DataFrame(similarity_score)  
    #df = df.drop("similarity", axis=1)
    st.session_state.original_df = df.copy()

    edited_df = st.data_editor(df, num_rows="dynamic")

    df = edited_df.copy()

    if len(edited_df) > len(st.session_state.original_df): # an if statement so the user can't add a row
        st.warning("Row additions are not allowed. Reverting to original data.")
        edited_df = st.session_state.original_df.copy()


#if st.session_state.get('data_editor_df_component', None) is not None: # ماضبط معانا
#    df = st.session_state.data_editor_df_component.copy()
    

#if st.sidebar.checkbox("عرض  جميع المفقودات"):
#    show_security_page = True

#if show_security_page:
#    st.write("جميع المفقودات")
#    try:
#        responses_df = pd.read_csv("secure_responses.csv") 
#        st.dataframe(responses_df[["analysis", "description"]])  
#    except FileNotFoundError:
#        st.error("Error: CSV file 'secure_responses.csv' not found.")
#else:
#    st.write("محتوى الصفحة الرئيسية")   
