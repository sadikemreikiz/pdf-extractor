import streamlit as st
import pdfplumber
from transformers import pipeline
import pandas as pd

@st.cache_resource
def get_ner():
    return pipeline("ner", model="savasy/bert-base-turkish-ner-cased", aggregation_strategy="simple")

ner = get_ner()

st.title("Türkçe PDF'den İsim ve Adres Eşleştirici")
st.write("Herhangi bir PDF dosyasından **isim** ve **adres** gibi bilgileri otomatik çıkarır ve eşleştirir.")

uploaded_file = st.file_uploader("PDF dosyasını yükle", type="pdf")
if uploaded_file:
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    st.info("PDF içeriği okundu. AI ile analiz ediliyor...")

    results = ner(text)
    isimler, adresler = [], []
    for r in results:
        if r["entity_group"] == "PER":
            isimler.append(r["word"])
        elif r["entity_group"] == "LOC":
            adresler.append(r["word"])

    st.subheader("Çıkarılan ve Eşleştirilen Bilgiler:")

    min_len = min(len(isimler), len(adresler))
    if min_len == 0:
        st.warning("Yeterli isim veya adres bulunamadı.")
    else:
        data = {
            "İsim": isimler[:min_len],
            "Adres": adresler[:min_len]
        }
        df = pd.DataFrame(data)
        st.dataframe(df)

        st.download_button(
            label="CSV olarak indir",
            data=df.to_csv(index=False),
            file_name="isim_adres.csv",
            mime="text/csv"
        )

    st.write("**İsimler:**", ", ".join(isimler) if isimler else "Bulunamadı.")
    st.write("**Adresler:**", ", ".join(adresler) if adresler else "Bulunamadı.")
