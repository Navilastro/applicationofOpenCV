import streamlit as st
import cv2
import numpy as np
from PIL import Image
import uuid

# Sayfa yapılandırması
st.set_page_config(page_title="Görüntü Filtreleme Aracı", layout="wide", page_icon="🎨")
st.title("Kapsamlı Görsel Filtreleme Uygulaması 🎨")
st.write("Fotoğraflarınıza farklı sanatsal ve nostaljik dokunuşlar ekleyin.")

FILTER_OPTIONS = [
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

if 'filters' not in st.session_state:
    st.session_state.filters = [{"id": str(uuid.uuid4()), "type": "Orijinal"}]

def add_filter():
    st.session_state.filters.append({"id": str(uuid.uuid4()), "type": "Orijinal"})

def remove_filter(index):
    st.session_state.filters.pop(index)

def apply_filter(img, filter_type):
    is_gray = len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1)
    
    if filter_type == "Orijinal":
        return img
    elif filter_type == "Gri Tonlama (Siyah-Beyaz)":
        if is_gray: return img
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
    elif filter_type == "Karakalem Çizim":
        if is_gray:
            gray = img
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        inv_gray = cv2.bitwise_not(gray) # Negatifini al
        blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0) # Bulanıklaştır
        return cv2.divide(gray, 255 - blurred, scale=256) # Birleştir
        
    elif filter_type == "Sepya":
        if is_gray:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        kernel = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        sepia = cv2.transform(img, kernel)
        return np.clip(sepia, 0, 255).astype(np.uint8)
        
    elif filter_type == "Bulanıklaştırma":
        return cv2.GaussianBlur(img, (25, 25), 0)
        
    elif filter_type == "Kenar Bulma (Canny)":
        if is_gray:
            gray = img
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return cv2.Canny(gray, 100, 200)
        
    elif filter_type == "Kabartma (Emboss)":
        kernel = np.array([
            [-2, -1,  0],
            [-1,  1,  1],
            [ 0,  1,  2]
        ])
        return cv2.filter2D(img, -1, kernel)
        
    elif filter_type == "Piksalleştirme":
        height, width = img.shape[:2]
        temp = cv2.resize(img, (width // 15, height // 15), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)
        
    elif filter_type == "Negatif (Invert)":
        return cv2.bitwise_not(img)
        
    return img

# Görsel yükleme alanı
uploaded_file = st.file_uploader("Bir görsel yükleyin", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    # Görseli oku ve RGB formatına çevir
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    # Yan menü (Sidebar) filtre seçenekleri
    st.sidebar.header("Filtre Seçenekleri")
    
    # Dinamik filtre seçenekleri
    for i, f_dict in enumerate(st.session_state.filters):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            selected_filter = st.selectbox(
                f"{i+1}. Filtre:",
                FILTER_OPTIONS,
                index=FILTER_OPTIONS.index(f_dict["type"]),
                key=f_dict["id"]
            )
            st.session_state.filters[i]["type"] = selected_filter
            
        with col2:
            if i > 0: # İlk filtre silinemez
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("➖", key=f"remove_{f_dict['id']}"):
                    remove_filter(i)
                    st.rerun()

    if st.sidebar.button("➕ Filtre Ekle"):
        add_filter()
        st.rerun()

    processed_img = img_array.copy()

    # Seçilen tüm filtreleri sırasıyla uygula
    for f_dict in st.session_state.filters:
        processed_img = apply_filter(processed_img, f_dict["type"])

    # Görselleştirme Ekranı
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Orijinal")
        st.image(img_array, use_container_width=True)
        
    with col2:
        st.subheader("Filtrelenmiş Sonuç")
        st.image(processed_img, use_container_width=True)