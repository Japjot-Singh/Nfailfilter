import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
import os

def convert_timestamp(inp_str):
    # Your existing function code\
  time_obj = datetime.strptime(inp_str, "%H:%M:%S")
  new_time_obj = time_obj - timedelta(hours=5)
  new_time_str = new_time_obj.strftime("%H:%M:%S")
  if(len(new_time_str)!=11):
    new_time_str=new_time_str[1:]

  return new_time_str

def convert_timestamp_prev(inp_str):
  time_obj = datetime.strptime(inp_str, "%H:%M:%S")
  new_time_obj = (time_obj - timedelta(hours=5)) - timedelta(minutes=1)
  new_time_str_prev = new_time_obj.strftime("%H:%M:%S")
  if(len(new_time_str_prev)!=11):
    new_time_str_prev=new_time_str_prev[1:]

  return new_time_str_prev

def convert_timestamp_next(inp_str):
  time_obj = datetime.strptime(inp_str, "%H:%M:%S")
  new_time_obj = (time_obj - timedelta(hours=5)) + timedelta(minutes=1)
  new_time_str_next = new_time_obj.strftime("%H:%M:%S")
  if(len(new_time_str_next)!=11):
    new_time_str_next=new_time_str_next[1:]

  return new_time_str_next

# Define other functions (convert_timestamp_prev and convert_timestamp_next) similarly

# Your existing code for reading CSV and Excel files
df1 = pd.read_csv('Message_Flow_UE1 truncated.csv')
df2 = pd.read_excel('input-1.xlsx', sheet_name="7. VoNR CallStats")

def main():
    st.title("Call Failure Filter")

    # Display input files and allow the user to upload their own files
    st.header("Select Input Files")
    st.write("Currently using 'Message_Flow_UE1.csv' and 'input-1.xlsx'")
    uploaded_csv = st.file_uploader("Upload Input 1", type=["csv"])
    uploaded_excel = st.file_uploader("Upload Input 2", type=["xlsx"])

    if uploaded_csv is not None:
        df1 = pd.read_csv(uploaded_csv)
        st.success("CSV file successfully uploaded and loaded!")
    
    if uploaded_excel is not None:
        df2 = pd.read_excel(uploaded_excel, sheet_name="7. VoNR CallStats")
        st.success("Excel file successfully uploaded and loaded!")

    len_df1 = len(df1)
    st.write(f"Length of DataFrame 1: {len_df1}")

    # Your existing code for data processing
    
    # create a new DataFrame containing the matched rows
    df2 = df2[df2['Call Result'] == 'Setup Fail']
    df2= df2.reset_index(drop=True)
    
    """DataFrame of Rows with SIP INVITE"""
    matches = []
    cnt=0
    
    # iterate over the elements in df2
    for i in range(0,len(df2)):
        converted_timestamp=convert_timestamp(df2.at[i, 'Start Time'][11:-4])[:-3]
        converted_timestamp_prev=convert_timestamp_prev(df2.at[i, 'Start Time'][11:-4])[:-3]
        converted_timestamp_next=convert_timestamp_next(df2.at[i, 'Start Time'][11:-4])[:-3]

        if(i>=1):
            if(converted_timestamp==convert_timestamp(df2.at[i-1, 'Start Time'][11:-4])[:-3]):
                continue

            for j in range(cnt,len(df1)):
                stamp = df1.loc[j, 'Timestamp'][9:16][:-3]

                if(stamp == ((converted_timestamp) or (converted_timestamp_prev) or (converted_timestamp_next)) and df1.at[j, 'Message Name'] == 'SIP INVITE' and df1.at[j, 'Timestamp'][2]==(df2.at[i, 'Start Time'])[9]) :
                    matches.append(j)
                    cnt=j+1
                    break
                else:
                    continue

    df_selected = df1.iloc[matches]
    new_df = pd.DataFrame(columns=df1.columns)
    new_df = pd.concat([df_selected], ignore_index=True)
    print(len(new_df))
    new_df
    
    """DataFrame of Rows between Fail and NR5G Release"""

    release_list=[]
    for i in matches:
        while(True):
            release_list.append(i+1)
            i+=1
            if(df1.at[i, 'Additional Info']=='NR5G RRC Release' or df1.at[i, 'Message Name']=='VoNR Bearer Release'):
                break
    df_selected_release  = df1.iloc[release_list]
    new_df_release = pd.DataFrame(columns=df1.columns)
    new_df_release = pd.concat([df_selected_release], ignore_index=True)
    new_df_release

    # Display the Final DataFrame
    st.header("Final DataFrame")
    st.write(new_df_release)
    def get_binary_file_downloader_html(bin_file, file_label='File'):
         with open(bin_file, 'rb') as f:
             data = f.read()
         bin_str = base64.b64encode(data).decode()
         href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
         return href
    # Export the output Excel
    st.header("Export Output Excel")
    st.write("Click the button below to export the DataFrame to Excel.")
    #if st.button("Export to Excel"):
    file_name = 'Output.xlsx'
    new_df_release.to_excel(file_name, index=False)
    st.success('DataFrame is written to Excel File successfully.')
    #st.download_button("Download Output Excel", file_name)
    st.markdown(get_binary_file_downloader_html(file_name, 'Filtered Output Excel'), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
 
