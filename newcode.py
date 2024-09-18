import requests
import json
import os

# Set your API key and endpoint
api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Alternatively, replace with your API key
endpoint = "https://<your-resource-name>.openai.azure.com"  # Replace with your Azure OpenAI endpoint
deployment_id = "<your-deployment-id>"  # Replace with the vision model deployment ID

# Vision API URL
url = f"{endpoint}/openai/deployments/{deployment_id}/images/generate"

# Read the image file
image_path = "path_to_your_image.jpg"
with open(image_path, "rb") as image_file:
    image_data = image_file.read()

# Set the headers
headers = {
    "Content-Type": "application/octet-stream",
    "api-key": api_key,
}

# Request payload (you may need to customize this depending on the API requirements)
payload = {
    "parameters": {
        "prompt": "Describe this image in detail"
    }
}

# Make the request
response = requests.post(url, headers=headers, data=image_data, params=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON
    result = json.loads(response.text)
    print("Result:", json.dumps(result, indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
