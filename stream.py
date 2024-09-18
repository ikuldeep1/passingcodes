import streamlit as st
import base64
from openai import AzureOpenAI
from PIL import Image
import io

# Azure OpenAI Client setup
api_key = "your_api_key_here"
endpoint = "your_endpoint_here"
client = AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version="2024-05-15-preview")

def analyze_image(image_data):
    # Define system prompt and input prompt
    system_prompt = """
    Analyze the image and identify the presence of any of the following labels based on their visual cues:
    1. Brand Name - Look for the company name and product name with trademark TM symbol and return it.
    2. Catalog Number - Search for the text 'REF' written inside a box. Extract the catalog number and return.
    Return the label names along with any associated numbers or limits when applicable. Do not output anything else.
    """
    
    # Image encoding
    encoded_image = base64.b64encode(image_data).decode('ascii')
    input_prompt = [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded_image}"}]

    # Get GPT-4 response
    chat_completion = client.chat.completions.create(
        model="gpt-4-2024-05-15",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(input_prompt)},
        ],
        max_tokens=300
    )
    message_content = chat_completion.choices[0].message.content
    return message_content

# Streamlit UI
st.title("Image Label Analyzer")

# Upload an image file
uploaded_image = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Display image on the right
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # When the "Analyze Image" button is clicked
    if st.button("Analyze Image"):
        # Convert image to bytes for processing
        image_bytes = uploaded_image.read()

        # Call the analyze_image function to get labels
        analysis_result = analyze_image(image_bytes)
        
        # Display results in table format on the left
        st.subheader("Analysis Results")
        st.write(analysis_result)
