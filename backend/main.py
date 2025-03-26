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

# Set the Tesseract path (only required for Windows)
if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load BLIP model for image captioning
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

@app.get("/")
def read_root():
    return {"message": "Image Captioning & OCR API is running!"}

@app.post("/caption/")
async def generate_caption(file: UploadFile = File(...)):
    try:
        # Read the image file
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        # Process image using BLIP model
        inputs = processor(image, return_tensors="pt").to(device)
        outputs = model.generate(**inputs)

        # Decode caption
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        return {"caption": caption}
    except Exception as e:
        return {"error": f"Caption generation failed: {str(e)}"}

def preprocess_image(image: Image.Image):
    """Enhance image for better OCR accuracy"""
    # Convert image to OpenCV format (numpy array)
    open_cv_image = np.array(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)

    # Resize the image if it’s too small
    height, width = gray.shape
    if width < 800:  # Resize if the width is too small
        scale_factor = 2  # Increase size
        gray = cv2.resize(gray, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding for better text detection
    processed_image = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Convert back to PIL Image
    return Image.fromarray(processed_image)

@app.post("/extract-text-auto/")
async def extract_text_auto(file: UploadFile = File(...)):
    try:
        # Read the image file
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        # Preprocess the image
        processed_image = preprocess_image(image)

        # Extract text using OCR (Hindi + English)
        extracted_text = pytesseract.image_to_string(processed_image, lang="hin+eng")

        return {"text": extracted_text.strip()}
    except Exception as e:
        return {"error": f"Text extraction failed: {str(e)}"}
