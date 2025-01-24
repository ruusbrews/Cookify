import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from mimetypes import guess_type
from io import BytesIO
import base64

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-08-01-preview",
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
deployment_name='gpt-4o' #This will correspond to the custom name you chose for your deployment when you deployed a model. Use a gpt-35-turbo-instruct deployment. 

def local_image_to_data_url(image_path):
    """
    Get the url of a local image
    """
    mime_type, _ = guess_type(image_path)

    if mime_type is None:
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{base64_encoded_data}"

def gpt4o_imagefile(image_file, prompt):
    """
    Gpt-4o model
    """
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-08-01-preview",
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant to analyse images.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": local_image_to_data_url(image_file)},
                    },
                ],
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )

    return response

st.title("Cookify")
st.markdown(
    "<h2>don't think, <i>just cook.</i></h2>", 
    unsafe_allow_html=True
)
st.image("banner2.jpg")

preferences = ""
ingredients = ""
count = 0

uploaded_file = st.file_uploader("Upload a photo of your fridge or pantry here:")
if uploaded_file:
    image_file = uploaded_file.name
    #st.text("--Analysing the picture--")
    result = gpt4o_imagefile(
        image_file, "Extract all the different types of food or ingredients shown in the image and list them, separating each ingredient with '',''."
    )
    ingredients = (result.choices[0].message.content)

text_ingrediants =  st.text_input("If not uploading a photo, enter the ingredients you have here: ")
if text_ingrediants:
    ingredients += text_ingrediants

preferences = st.text_input("Please let us know of any other preferences you have. You can put multiple (e.g. healthy and prepared in under 30 minutes): ")


start_phrase = f'Make a recipe step-by-step using only these ingredients: {ingredients}. You do NOT have to use all of them - only use ones that are commonly used together. Reduce the use of any other main ingredients other than sauces, spices, etc. The priority is for the normal well-known dishes from different cultures. You could suggest any other ingrediants that I do not already have, but make it just a suggestion so that I could still cook with only what I already have. Other preferences include: {preferences}.'
if preferences:
    #st.text("--Generating your recipe--")

    response = client.chat.completions.create(
        model=deployment_name, 
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": start_phrase},
                    ],
                },
            ],
        max_tokens=2000)
    st.markdown(response.choices[0].message.content)
    count += 1

if count > 0:
    regenerate = st.button("Regenerate", type="primary")
    if regenerate:
        response = client.chat.completions.create(
            model=deployment_name, 
            messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": start_phrase},
                        ],
                    },
                ],
            max_tokens=2000)
        st.markdown(response.choices[0].message.content)
