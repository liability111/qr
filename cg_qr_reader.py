import streamlit as st
from pyzbar import pyzbar
import cv2
import numpy as np
import qrcode
from io import BytesIO
from PIL import Image

# Title customization with center alignment and underline
st.markdown("<h1 style='text-align: center; text-decoration: underline;'>QR Code App</h1>", 
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

# Function to generate QR code with custom colors and logo
def generate_custom_qr_code(text, fill_color, back_color, logo_path=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction to accommodate the logo
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    if logo_path:
        logo = Image.open(logo_path)
        logo = logo.resize((50, 50))  # Resize logo as needed
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos)

    return img

# Ask user for the desired action
action = st.radio("Select action:", ("Generate QR Code", "Read QR Code"))

if action == "Generate QR Code":
    text_data = st.text_input("Enter text for QR code generation:")
    fill_color = st.color_picker("Pick a fill color", "#000000")
    back_color = st.color_picker("Pick a background color", "#FFFFFF")
    logo_file = st.file_uploader("Upload a logo (optional)", type=["png", "jpg", "jpeg"])

    if text_data:
        logo_path = None
        if logo_file:
            logo_path = logo_file

        qr_image = generate_custom_qr_code(text_data, fill_color, back_color, logo_path)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)
        st.image(buffer, caption="Generated QR Code for Text", use_column_width=True)
        st.download_button(
            label="Download QR Code",
            data=buffer,
            file_name="custom_qrcode.png",
            mime="image/png"
        )

elif action == "Read QR Code":
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
