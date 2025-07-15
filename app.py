import streamlit as st
import pdfplumber
from transformers import pipeline

@st.cache_resource
def get_ner():
    # Multilingual NER: Almanca, İngilizce, Türkçe vs.
    return pipeline("ner", model="Davlan/xlm-roberta-base-ner-hrl", aggregation_strategy="simple")

ner = get_ner()

st.title("Çok Dilli PDF'den İsim ve Adres Eşleştirici")
st.write("Herhangi bir PDF dosyasından **isim ve adres** çiftlerini otomatik çıkarır. (Türkçe, Almanca, İngilizce destekli)")

uploaded_file = st.file_uploader("PDF dosyasını yükle", type="pdf")
if uploaded_file:
    lines = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                page_lines = [line.strip() for line in page_text.split("\n") if line.strip()]
                lines.extend(page_lines)

    st.info("PDF içeriği satır satır okundu. AI ile analiz ediliyor...")

    pairs = []
    i = 0
    while i < len(lines):
        # 1. satır isim, 2. satır adres (3. satır varsa şehir veya posta kodu olabilir, birleştir)
        chunk = lines[i:i+3]
        # NER ile isim ve adres ayrıştır
        ner_results = ner("\n".join(chunk))
        isim = ""
        adres = ""
        for ent in ner_results:
            if ent["entity_group"] == "PER" and not isim:
                isim = ent["word"]
            elif ent["entity_group"] == "LOC":
                if adres:
                    adres += ", " + ent["word"]
                else:
                    adres = ent["word"]
        # Eğer isim ve adres varsa kaydet
        if isim and adres:
            pairs.append((isim, adres))
        i += 3  # 3 satır ilerle (gerekiyorsa ayarla: istersen i += 2 de yapabilirsin)

    import pandas as pd
    if pairs:
        df = pd.DataFrame(pairs, columns=["İsim/Name", "Adres/Address"])
        st.subheader("Çıkarılan ve Eşleştirilen Bilgiler:")
        st.dataframe(df)
        st.download_button(
            label="CSV olarak indir",
            data=df.to_csv(index=False),
            file_name="isim_adres_cifti.csv",
            mime="text/csv"
        )
    else:
        st.warning("Herhangi bir isim/adres çifti bulunamadı.")

    # Debug: Alt alta ne yakaladı görmek için
    st.write("---")
    st.write("Ham Satırlar (kontrol):")
    for satir in lines:
        st.text(satir)

