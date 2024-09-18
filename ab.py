import base64
import streamlit as st
from openai import AzureOpenAI
from utils import encode_image

# Azure OpenAI Client setup
client = AzureOpenAI(api_key=st.secrets["AZURE_OPENAI_API_KEY"],
                     azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
                     api_version="2023-09-15-preview")

# Set page configuration
st.set_page_config(page_icon="🖼️", page_title="GPT-4V Demo", initial_sidebar_state="collapsed")

# App title
st.title("GPT-4V Demo 🖼️")

# System message input
system_message = st.text_area("**Prompt**", "Your task is to identify what is in the image. Be succinct.")

# File uploader for image upload
input_pic = st.file_uploader("**Upload a Photo**", type=["jpg", "jpeg", "png"])

# Sidebar for advanced settings
with st.sidebar:
    st.subheader("Advanced Settings ⚙️")
    resolution = st.selectbox('**Quality of Image to be processed by GPT-4V**', ('Low', 'High'))
    temperature = st.slider('**Temperature**', min_value=0.0, max_value=2.0, step=0.1, value=0.0)
    seed = st.number_input("**Seed**", min_value=0, max_value=999, step=1)
    max_tokens = st.slider('**Max Tokens**', 1, 500, 250)

# Submit button
if st.button("Run"):
    if input_pic is None:
        st.warning('Please upload an image before clicking Run.', icon='⚠️')
    else:
        # Convert image to base64 format
        image_bytes = input_pic.read()  # Read the file as bytes
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")  # Encode to base64

        # Prepare the prompt for GPT-4V
        input_prompt = [{"type": "image_url", "image_url": {
            "url": f"data:image/jpeg;base64,{image_base64}",
            "detail": resolution}}]
        
        # Show loading spinner
        with st.spinner('Processing the image...'):
            chat_completion = client.chat.completions.create(
                model="gpt-4v",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": input_prompt}
                ],
                max_tokens=max_tokens,
                seed=seed,
                temperature=temperature
            )

        # Extract the GPT-4V response and display
        message_content = chat_completion.choices[0].message.content
        st.info(message_content)
