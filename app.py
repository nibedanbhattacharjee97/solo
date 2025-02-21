import streamlit as st
import folium
from streamlit_folium import folium_static
import geocoder
from datetime import datetime
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorFactory
from io import BytesIO
import base64
import tempfile
from PIL import Image, ImageDraw, ImageFont

st.title("📍 GPS Map Camera & Audio Recorder 🎙️")

# Get GPS Location
def get_location():
    g = geocoder.ip('me')  # Fetch location based on IP (browser-based GPS not supported in Streamlit)
    return g.latlng, g.postal, g.city

location, pincode, city = get_location()
current_time = datetime.now().strftime('%d %b, %Y %I:%M %p, %A')

if location:
    st.success(f"🌍 Location: {location}, 📌 Pincode: {pincode}, 🏙️ City: {city}")
    
    # Show map
    m = folium.Map(location=location, zoom_start=15)
    folium.Marker(location, popup="Your Location").add_to(m)
    folium_static(m)
else:
    st.error("❌ Failed to get location. Ensure GPS is enabled.")

# 📸 Capture Image
image_file = st.camera_input("📷 Take a Picture")
if image_file:
    img = Image.open(image_file)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()  # Fallback font if Arial is missing

    # Text for watermark
    text = f"{city}\nPincode: {pincode}\nLat: {location[0]}, Long: {location[1]}\n{current_time}"
    
    # Calculate text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Position text in the middle bottom of the image
    img_width, img_height = img.size
    text_x = (img_width - text_width) // 2
    text_y = img_height - text_height - 30  # 30 pixels above the bottom edge

    # Draw semi-transparent background for better visibility
    bg_box = [(text_x - 10, text_y - 10), (text_x + text_width + 10, text_y + text_height + 10)]
    draw.rectangle(bg_box, fill=(0, 0, 0, 150))  # Black semi-transparent box
    
    # Draw text on image
    draw.text((text_x, text_y), text, fill="white", font=font)
    
    # Save image
    img_path = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    img.save(img_path)
    
    st.image(img, caption="📷 Captured Image with Location Stamp", use_container_width=True)
    st.success(f"✅ Image saved as {img_path}")
    
    # Provide download link
    with open(img_path, "rb") as f:
        img_bytes = f.read()
        b64 = base64.b64encode(img_bytes).decode()
        href = f'<a href="data:file/jpg;base64,{b64}" download="{img_path}">📥 Download Image</a>'
        st.markdown(href, unsafe_allow_html=True)

# 🎤 Audio Recording
def record_audio():
    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    webrtc_streamer(key="audio", audio_processor_factory=AudioProcessorFactory)
    return temp_audio_path

if st.button("🎙️ Start Recording"):
    audio_path = record_audio()
    st.success(f"🎵 Audio recorded and saved at: {audio_path}")
    
    # Provide download link
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        href = f'<a href="data:file/wav;base64,{b64}" download="recorded_audio.wav">📥 Download Audio</a>'
        st.markdown(href, unsafe_allow_html=True)

st.info("ℹ️ After downloading, manually move the files to your gallery.")
