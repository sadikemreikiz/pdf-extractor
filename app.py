import streamlit as st
import pdfplumber
import pandas as pd

st.title("PDF Extractor App")
st.write("PDF'den isim ve adresleri otomatik çıkar!")

uploaded_file = st.file_uploader("PDF dosyası yükle", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Metni satırlara böl
    lines = [line.strip() for line in text.split('\n') if line.strip() != ""]
    
    data = []
    # 3 satırda bir kaydı al
    for i in range(0, len(lines)-2, 3):
        isim = lines[i]
        adres = lines[i+1]
        sehir = lines[i+2]
        data.append({"İsim": isim, "Adres": adres, "Şehir": sehir})

    df = pd.DataFrame(data)
    st.write("Çıkarılan Bilgiler:")
    st.dataframe(df)

    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV olarak indir",
            data=csv,
            file_name='pdf_adresler.csv',
            mime='text/csv',
        )
else:
    st.info("Başlamak için PDF dosyası yükleyin.")
