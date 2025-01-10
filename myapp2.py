
#from langchain.llms import OpenAI
import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image
import google.generativeai as genai
# import PyMuPDF
import fitz  # PyMuPDF
import base64
from io import BytesIO
from dotenv import load_dotenv

# genai.configure(api_key='AIzaSyAku0AUb-InsJlac_4HXxgAoDbyIQ9J0dM')
# os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key='AIzaSyBefMFEStxc82vEXk0rC4o1p-V2KeArLnU')

## Function to load 

def get_gemini_response(input,image,prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input,image[0],prompt])
    return response.text
    

def input_image_setup(uploaded_file):
    #  file uploaded
    if uploaded_file is not None:
        # Read the file into bytes as image
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def convert_pdf_to_images(pdf_contents):
    pdf_document = fitz.open("pdf", pdf_contents)
    images = []

    for page_number in range(pdf_document.page_count):
        pdf_page = pdf_document.load_page(page_number)
        image = pdf_page.get_pixmap()
        img = Image.frombytes("RGB", [image.width, image.height], image.samples)
        images.append(img)

    return images

def concatenate_images_vertically(images):
    if len(images) == 1:
        return images[0]

    width, height = images[0].size

    concat_image = Image.new("RGB", (width, sum(img.height for img in images)))

    offset = 0
    for img in images:
        concat_image.paste(img, (0, offset))
        offset += img.height

    return concat_image
def convert_image_to_image_parts(image):
    # Convert the image to bytes
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    bytes_data = img_bytes.getvalue()

    # Encode bytes as base64
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    # Create image parts
    image_parts = [
        {
            "mime_type": "image/png",  # Adjust the MIME type if needed
            "data": base64_data
        }
    ]

    return image_parts
##streamlit app
# Sidebar
st.set_page_config(page_title="Gemini Image Demo")
st.sidebar.title("Powered by Moreyeahs INC")
st.sidebar.write("Extract information From Image")
st.sidebar.write("Juned.khan@moreyeahs.in") 
st.sidebar.write("https://www.moreyeahs.com")
st.header("Report Summary")
input=st.text_input("What you want to extract: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["pdf","jpg", "jpeg", "png"])
image="" 
# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
#     st.image(image, caption="Uploaded Image.", use_column_width=True)
if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            pdf_contents = uploaded_file.read()
            images = convert_pdf_to_images(pdf_contents)
            image = concatenate_images_vertically(images)
            image_parts_c = convert_image_to_image_parts(image)


            # converted images from pdf
            # for i, img in enumerate(images):
            #     st.image(img, caption=f"Page {i + 1}", use_column_width=True)

            st.success("PDF file uploaded and converted to Vertical Single images successfully!")
            st.image(image, caption="Vertical image", use_column_width=True)
            # st.write(uploaded_file.type)
            # st.write(type(image))
            
        elif uploaded_file.type.startswith("image"):
            # uploaded image as image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            st.success("Image file uploaded successfully!")
            image_parts_c = input_image_setup(uploaded_file)
            # st.write(uploaded_file.type)
        else:
            st.error("Unsupported file format. Please upload a PDF or an image.")

submit=st.button("Start Processing")

input_prompt = """
               You are an expert in understanding images and can extract all the infromation from it.
               You will receive input images &
               you will have to answer questions based on the input image
               """

## If ask button is clicked

if submit:
    # image_data = input_image_setup(uploaded_file)
    # image_data = input_image_setup(image)
    response=get_gemini_response(input_prompt,image_parts_c,input)
    st.subheader("The Response is")
    st.write(response)
    print(type(response))
