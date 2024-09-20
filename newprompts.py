
import os
import base64
import requests
import json
from PIL import Image
import io
import csv

import time
start_time = time.time()


input_folder = r"./Input"       # where labels are kept
output_folder = r"./Output"     # where response will be saved in json format as text file 

# GPT-4o API configuration
api_url = "https://api.openai.com/v1/chat/completions"

# Function to resize image maintaining aspect ratio with a maximum width of 1000 pixels
def resize_image(image_path, max_width=1000):
    with Image.open(image_path) as img:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        resized_img = img.resize((max_width, new_height), Image.LANCZOS)
        img_byte_arr = io.BytesIO()
        resized_img.save(img_byte_arr, format=img.format)
        return img_byte_arr.getvalue()

# Function to encode the image to base64
def encode_image(image_path):
    resized_image_bytes = resize_image(image_path)  # Resize the image
    return base64.b64encode(resized_image_bytes).decode('utf-8')

# Function to call the GPT-4o API for each image and get the response
def get_response_for_image(image_path):
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-2024-08-06",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": '''
                        Extract the following information from the given text and format it as JSON. 
                        Do not introduce any nested keys. 
                        Ensure that all fields are returned as lists, even if they contain only a single item.
                        
                        Analyze this medical device label image thoroughly and extract ALL information present. 
                        Include, but don’t limit yourself to:

                        1.	Product name, brand and full description.
                        2.	Manufacturer details (name, address, contact information).
                        3.	All numerical identifiers (REF/catalog numbers, LOT numbers, UDI (Unique Device Identifier) barcode number).
                        4.	Dates (manufacturing, expiration) - note associated symbols (e.g., hourglass, factory).
                        5.	Contents, quantity, measurements or volume.
                        6.	Regulatory marks and numbers (e.g., CE mark and number, EC REP).
                        7.	ALL symbols and icons - make separate json keys for each symbol and icon if present and assign Yes in json value, including:
                            o Single use symbol (crossed out 2).
                            o 'Do not use if package damaged' symbol.
                            o Rx only symbol.
                            o Sterile packaging symbol.
                            o Temperature limit symbols
                            o Any other regulatory or warning symbols (e.g. MD for medical device)
                        8.	Sterilization method and information (e.g. STERILE R, STERILE EO)
                        9.	Storage and operating conditions (temperature, humidity, pressure limits).
                        10.	Power/battery specifications.
                        11.	Material composition.
                        12.	Text in different languages.
                        13.	QR codes or other machine-readable elements (note presence, don’t decode).
                        14.	Disposal instructions.
                        15.	Clinical or technical specifications.
                    
                        • Include every piece of information visible, even if its purpose isn’t clear.
                        • If unsure about any element, describe it and note your uncertainty.
                        • Pay special attention to extracting:
                            o Barcode numbers.
                            o Manufacturing date (look for factory symbol).
                            o Expiry date (look for hourglass symbol).
                        
                        Aim to be as comprehensive as possible in your analysis, capturing both standard and unique attributes of this specific medical device label.
                        Remember to only report information that is actually present on the label. Do not mention or list any information that is not visible in the image.
                
                        Provide only the JSON output without any additional text before or after it. Do not mention the keys which are not present.
                        
                        '''
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.3
    }
    response = requests.post(api_url, headers=headers, json=payload)
    
    # Check if the response was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(f"Response content: {response.text}")
        return None
    
    # Attempt to parse the JSON response
    try:
        response_json = response.json()
        return response_json
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response")
        return None
    

# Main processing function
def process_images(input_folder, output_folder):
    # Iterate through each image file in the folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".png"):  # Assuming the images are .png files
            image_path = os.path.join(input_folder, file_name)
            
            # Call the API and get the response
            response = get_response_for_image(image_path)
            
            if response and 'choices' in response:
                extracted_text = response['choices'][0]['message']['content']
                
                # Remove the code block markers
                if extracted_text.startswith("```json") and extracted_text.endswith("```"):
                    extracted_text = extracted_text[7:-3].strip()
                
                # Parse the JSON text
                try:
                    json_data = json.loads(extracted_text)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON for image: {image_path}")
                    continue

                csv_file_name = file_name.replace(".png", ".csv")
                output_file_path = os.path.join(output_folder, csv_file_name)

                # Write to CSV
                with open(output_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(['Metadata', 'Response'])

                    for key, value in json_data.items():
                        if isinstance(value, list):
                            value = ', '.join(map(str, value))
                        writer.writerow([key, value])

                print(f"Processed and saved: {output_file_path}")
            else:
                print(f"Failed to process image: {image_path}")

process_images(input_folder, output_folder)

print("Processing completed!")


end_time = time.time()
time_taken_seconds = end_time - start_time
time_taken_minutes = time_taken_seconds // 60
time_taken_seconds %= 60

print(f"\nTime taken: {int(time_taken_minutes)} minutes {int(time_taken_seconds)} seconds")

