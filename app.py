import streamlit as st
import openai
import tempfile
import os

from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract

# Başlık
st.title("PDF Extractor App (AI Destekli)")
st.write("PDF dosyasındaki **isim** ve **adres** bilgilerini otomatik çıkartır!")

# OpenAI API Key kullanıcıdan alınır
api_key = st.text_input("OpenAI API Key’inizi girin:", type="password")
if not api_key:
    st.warning("Devam etmek için lütfen bir OpenAI API Key girin.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# PDF Yükleme
uploaded_file = st.file_uploader("PDF dosyasını yükle", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    try:
        # 1. Önce klasik PDF metin okuma
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except:
        pass
    # 2. Eğer metin azsa (görsel taranmış olabilir) → OCR yap
    if len(text) < 50:
        try:
            images = convert_from_bytes(file.getvalue())
            for img in images:
                text += pytesseract.image_to_string(img, lang='deu+eng')
        except Exception as e:
            st.error(f"OCR sırasında hata: {e}")
    return text

def gpt_extract_names_addresses(text):
    prompt = f"""
    Aşağıda bir Almanca maaş bordrosu, fatura veya resmi belge metni var. 
    Lütfen metindeki ad-soyad ve adres bilgilerini (adres: sokak adı ve numarası, posta kodu ve şehir) tespit et. 
    Sadece tablo formatında İsim | Adres | Şehir başlıklarıyla döndür.

    Belge metni:
    \"\"\"
    {text}
    \"\"\"
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen belgelerden adres ve isim tespit eden bir asistansın."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=500,
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        return f"AI hatası: {e}"

if uploaded_file:
    with st.spinner("PDF'den metin okunuyor..."):
        text = extract_text_from_pdf(uploaded_file)
    if not text or len(text.strip()) < 10:
        st.error("PDF'den metin çıkartılamadı!")
    else:
        st.success("PDF metni başarıyla okundu. AI ile analiz ediliyor...")
        result = gpt_extract_names_addresses(text)
        st.markdown("#### Çıkarılan Bilgiler:")
        st.markdown(result)
