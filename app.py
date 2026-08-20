import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Görüntü Filtreleme Aracı", layout="wide", page_icon="🎨")
st.title("Kapsamlı Görsel Filtreleme Uygulaması 🎨")
st.write("Fotoğraflarınıza farklı sanatsal ve nostaljik dokunuşlar ekleyin.")

uploaded_file = st.file_uploader("Bir görsel yükleyin", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    st.sidebar.header("Filtre Seçenekleri")

    filter_type = st.sidebar.selectbox(
        "Uygulamak istediğiniz filtreyi seçin:",
        [
            "Orijinal",
            "Gri Tonlama (Siyah-Beyaz)",
            "Karakalem Çizim",
            "Sepya",
            "Bulanıklaştırma",
            "Kenar Bulma (Canny)",
            "Kabartma (Emboss)",
            "Piksalleştirme",
            "Negatif (Invert)"
        ]
    )

    processed_img = img_array.copy()

    if filter_type == "Gri Tonlama (Siyah-Beyaz)":
        processed_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
    elif filter_type == "Karakalem Çizim":
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        inv_gray = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        processed_img = cv2.divide(gray, 255 - blurred, scale=256)
        
    elif filter_type == "Sepya":
        kernel = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        sepia = cv2.transform(img_array, kernel)
        processed_img = np.clip(sepia, 0, 255).astype(np.uint8)
        
    elif filter_type == "Bulanıklaştırma":
        processed_img = cv2.GaussianBlur(img_array, (25, 25), 0)
        
    elif filter_type == "Kenar Bulma (Canny)":
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        processed_img = cv2.Canny(gray, 100, 200)
        
    elif filter_type == "Kabartma (Emboss)":
        kernel = np.array([
            [-2, -1,  0],
            [-1,  1,  1],
            [ 0,  1,  2]
        ])
        processed_img = cv2.filter2D(img_array, -1, kernel)
        
    elif filter_type == "Piksalleştirme":
        height, width = img_array.shape[:2]
        temp = cv2.resize(img_array, (width // 15, height // 15), interpolation=cv2.INTER_LINEAR)

        processed_img = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)
        
    elif filter_type == "Negatif (Invert)":
        processed_img = cv2.bitwise_not(img_array)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Orijinal")
        st.image(img_array, use_container_width=True)
        
    with col2:
        st.subheader(filter_type)
        st.image(processed_img, use_container_width=True)