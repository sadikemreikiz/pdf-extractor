import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("PDF Extractor App")
st.write("PDF dosyasından isim ve adresleri çıkar!")

uploaded_file = st.file_uploader("PDF dosyası yükle", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Basit örnek: 'İsim:' ve 'Adres:' geçen satırları bulur.
    isimler = re.findall(r'İsim[:\s]+(.+)', text)
    adresler = re.findall(r'Adres[:\s]+(.+)', text)

    # Sonuçları eşleştir
    data = []
    for isim, adres in zip(isimler, adresler):
        data.append({"İsim": isim, "Adres": adres})

    df = pd.DataFrame(data)

    st.write("Çıkarılan Bilgiler:")
    st.dataframe(df)

    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV olarak indir",
            data=csv,
            file_name='pdf_cikarim.csv',
            mime='text/csv',
        )
else:
    st.info("Başlamak için PDF dosyası yükleyin.")
