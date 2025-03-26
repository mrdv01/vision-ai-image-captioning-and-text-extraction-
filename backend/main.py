from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import torch
import pytesseract
import cv2
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration
import os

# set the path for Tesseract ocr
if os.name == "nt":  # check if the operating system is Window
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# create a FastAPI application
app = FastAPI()

# enable cors to allow frontend applications to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains to access the API
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers
)

# Load the BLIP model for generating image captions
# Check if GPU (CUDA) is available; otherwise, use the CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# Root endpoint to check if the API is running
@app.get("/")
def read_root():
    return {"message": "Image Captioning & OCR API is running!"}

# Endpoint to generate a caption for an uploaded image
@app.post("/caption/")
async def generate_caption(file: UploadFile = File(...)):
    try:
        # read the uploaded image file
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")  # Convert to RGB format

        # process the image using the BLIP model
        inputs = processor(image, return_tensors="pt").to(device)
        outputs = model.generate(**inputs)

        # decode and return the generated caption
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        return {"caption": caption}
    except Exception as e:
        return {"error": f"Caption generation failed: {str(e)}"}

# function to preprocess an image for better OCR accuracy
def preprocess_image(image: Image.Image):
    """
    Convert the image to grayscale, apply noise reduction, and improve text visibility.
    """
    # Convert PIL image to OpenCV format (numpy array)
    open_cv_image = np.array(image)
    
    # Convert the image to grayscale (black & white)
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)

    # Resize the image if it's too small (for better OCR accuracy)
    height, width = gray.shape
    if width < 800:  # If width is less than 800 pixels
        scale_factor = 2  # Increase size by 2x
        gray = cv2.resize(gray, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to improve text clarity
    processed_image = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Convert the processed image back to PIL format and return
    return Image.fromarray(processed_image)

# Endpoint to extract text from an uploaded image using OCR
@app.post("/extract-text-auto/")
async def extract_text_auto(file: UploadFile = File(...)):
    try:
        # Read the uploaded image file
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")  # Convert to RGB format

        # Preprocess the image to improve text extraction accuracy
        processed_image = preprocess_image(image)

        # Use Tesseract OCR to extract text (supports both Hindi and English)
        extracted_text = pytesseract.image_to_string(processed_image, lang="hin+eng")

        # Return the extracted text (removing extra spaces)
        return {"text": extracted_text.strip()}
    except Exception as e:
        return {"error": f"Text extraction failed: {str(e)}"}
