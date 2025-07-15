import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import pandas as pd

st.title("PDF/Görsel OCR Extractor")
st.write("PDF veya resimden isim/adres/şehir bilgisini otomatik çıkar!")

uploaded_file = st.file_uploader("PDF veya Görsel yükle", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    all_text = ""
    # PDF ise her sayfayı görsele çevir, OCR uygula
    if uploaded_file.type == "application/pdf":
        images = convert_from_bytes(uploaded_file.read())
        for img in images:
            text = pytesseract.image_to_string(img, lang='deu+eng')  # Almanca/İngilizce desteği için
            all_text += text + "\n"
    else:
        # Görsel dosya ise doğrudan OCR uygula
        img = Image.open(uploaded_file)
        all_text = pytesseract.image_to_string(img, lang='deu+eng')

    # Satırlara böl, gereksiz boşlukları temizle
    lines = [line.strip() for line in all_text.split('\n') if line.strip() != ""]

    data = []
    # 3 satırda bir isim, adres, şehir olarak işle
    for i in range(0, len(lines)-2, 3):
        grup = lines[i:i+3]
        if len(grup) == 3:
            isim, adres, sehir = grup
            data.append({"İsim": isim, "Adres": adres, "Şehir": sehir})

    df = pd.DataFrame(data)
    st.write("Çıkarılan Bilgiler:")
    st.dataframe(df)
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV olarak indir",
            data=csv,
            file_name='ocr_adresler.csv',
            mime='text/csv',
        )
else:
    st.info("Başlamak için PDF veya resim yükleyin.")
