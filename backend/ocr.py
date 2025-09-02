import os
KEY = os.environ['GEMINI_API']
from pydantic import BaseModel
from crewai_tools import tool
from google import genai
from google.genai import types
from pydantic import BaseModel

client = genai.Client(api_key=KEY)

with open("DELETE.png", "rb") as f:
    image_bytes = f.read()


@tool
def extract_text_from_chat(image_bytes):
    '''Extract text from an image using Gemini API.
     Args:
         image_bytes (bytes): The image data in bytes.
     Returns:
         str: The extracted text from the image along with Datetime sender and receiver.
     '''
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Extract all the text with positions",
        ],
    )

    print(response.text)
    return response.text

def extract_text_from_bills(image_bytes):
    '''Extract text from a bill image using Gemini API.
     Args:
         image_bytes (bytes): The image data in bytes.
     Returns:
         str: The extracted text from the bill along with the total amount and date.
     '''
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Extract the text with positions",
        ],
    )

    print(response.text)
 #https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/000/578/632/datas/original.png