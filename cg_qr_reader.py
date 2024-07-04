import streamlit as st
from pyzbar import pyzbar
import cv2
import numpy as np

# Title customization with center alignment and underline
st.markdown("<h1 style='text-align: center; text-decoration: underline;'>QR Code Scanner</h1>", 
            unsafe_allow_html=True)

# Function to detect barcodes and QR codes using pyzbar
def detect_codes(inputImage):
    detectedBarcodes = pyzbar.decode(inputImage)
    if detectedBarcodes:
        for barcode in detectedBarcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(inputImage, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            text = f"{barcodeData} ({barcodeType})"
            cv2.putText(inputImage, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            return inputImage, barcodeData
    return inputImage, ""

# Ask user for input method (webcam or upload)
input_method = st.radio("Select input method:", ("Use Webcam", "Upload an Image"))

if input_method == "Use Webcam":
    # Initialize camera
    camera = cv2.VideoCapture(0)

    # Placeholder for displaying live video feed
    video_placeholder = st.empty()

    # Main loop
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        # Detect QR codes
        frame, data = detect_codes(frame)
        if data:
            st.success(f"Decoded Data: {data}")
            break  # Stop capturing frames once QR code is detected
        else:
            # Display the live video feed
            video_placeholder.image(frame, caption='Live Feed', use_column_width=True)

    # Release camera
    camera.release()

elif input_method == "Upload an Image":
    # File uploader for direct image upload
    uploaded_file = st.file_uploader("Upload a QR code or barcode image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        inputImage = cv2.imdecode(file_bytes, 1)
        _, data = detect_codes(inputImage)
        if data:
            st.success(f"Decoded Data (Uploaded Image): {data}")
        else:
            st.error("No QR Code or Barcode detected in the uploaded image")
