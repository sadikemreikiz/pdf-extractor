import streamlit as st
import pdfplumber
from transformers import pipeline

@st.cache_resource
def get_ner():
    return pipeline("ner", model="savasy/bert-base-turkish-ner-cased", aggregation_strategy="simple")

ner = get_ner()

st.title("Türkçe PDF'den İsim ve Adres Çıkarıcı")
st.write("Herhangi bir PDF dosyasından **isim, adres ve kurum** gibi bilgileri otomatik çıkarır.")

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
    isimler, kurumlar, adresler = set(), set(), set()
    for r in results:
        if r["entity_group"] == "PER":
            isimler.add(r["word"])
        elif r["entity_group"] == "ORG":
            kurumlar.add(r["word"])
        elif r["entity_group"] == "LOC":
            adresler.add(r["word"])

    st.subheader("Çıkarılan Bilgiler:")
    st.write("**İsimler:**", ", ".join(isimler) if isimler else "Bulunamadı.")
    st.write("**Kurumlar:**", ", ".join(kurumlar) if kurumlar else "Bulunamadı.")
    st.write("**Adresler:**", ", ".join(adresler) if adresler else "Bulunamadı.")

    import pandas as pd
    df = pd.DataFrame({
        "İsim": list(isimler),
        "Kurum": list(kurumlar),
        "Adres": list(adresler)
    })
    st.download_button(
        label="CSV olarak indir",
        data=df.to_csv(index=False),
        file_name="cikarilan_bilgiler.csv",
        mime="text/csv"
    )
