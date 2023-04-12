import streamlit as st
import os
import requests
from pydub import AudioSegment
import io
from time import sleep


# AssemblyAI API endpoint URLs
upload_url = "https://api.assemblyai.com/v2/upload"
transcript_url = "https://api.assemblyai.com/v2/transcript"

# AssemblyAI API key
API_KEY = st.secrets["api_key"]

# Streamlit app
st.title("Audio Transcription with Textin")

language = st.selectbox("Select language", ["Hindi", "English", "Spanish"])
language_map = {
    "Hindi": "hi",
    "English": "en",
    "Spanish": "es"
}

# Upload file widget
file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])


# Check if a file was uploaded
if file is not None:
    # Preview the audio file
    audio_bytes = file.read()
    st.audio(audio_bytes, format='audio/wav')

    headers = {
        "authorization": API_KEY,
        "content-type": "application/json"
    }

    bar = st.progress(0)
   
    upload_response = requests.post(
        upload_url,
        headers=headers,
        data=audio_bytes
    )
    audio_url = upload_response.json()["upload_url"]
    st.info('Audio file has been uploaded to Textin')
    bar.progress(30)

    # Create transcription request
    json = {
        "audio_url": audio_url,
        "content_safety" : True,        
        "language_code" : language_map[language],
       
    }

    # Submit transcription request to AssemblyAI
    response = requests.post(
        transcript_url,
        headers=headers,
        json=json
    )

    st.info('Transcribing uploaded file')
    bar.progress(40)

    # Extract transcript ID
    transcript_id = response.json()["id"]
    st.info('Extract transcript ID')
    bar.progress(50)

    # Retrieve transcription results
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {
        "authorization": API_KEY,
    }
    transcript_output_response = requests.get(endpoint, headers=headers)
    st.info('Retrieve transcription results')
    bar.progress(60)

    # Check if transcription is complete
    st.warning('Transcription is processing ...')
    while transcript_output_response.json()['status'] != 'completed':
        sleep(1)
        transcript_output_response = requests.get(endpoint, headers=headers)
    
    bar.progress(100)

    # Print transcribed text
    st.header('Output')
    
    with st.expander('Show Text'):
        st.success(transcript_output_response.json()["text"])


    

    # 9. Write JSON to app
    with st.expander('Show Full Results'):
        st.write(transcript_output_response.json())
    
    # 10. Write content_safety_labels
    with st.expander('Show content_safety_labels'):
        st.write(transcript_output_response.json()["content_safety_labels"])
    
    with st.expander('Summary of content_safety_labels'):
        st.write(transcript_output_response.json()["content_safety_labels"]["summary"])
        
 



