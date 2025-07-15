import streamlit as st
import openai

st.title("AI PDF/Görsel Extractor")
st.write("Her tür PDF veya görselde *isim* ve *adres*leri otomatik bulur, tablo halinde çıkarır.")

uploaded_file = st.file_uploader("Belge yükle (PDF/JPG/PNG):", type=["pdf", "jpg", "jpeg", "png"])
api_key = st.text_input("OpenAI API Key’in:", type="password")

if uploaded_file and api_key:
    with st.spinner("AI analiz ediyor, lütfen bekle..."):
        file_bytes = uploaded_file.read()
        # OpenAI Vision modeline hem dosyayı hem promptu gönderiyoruz:
        response = openai.chat.completions.create(
            model="gpt-4o",  # veya "gpt-4-vision-preview" (her ikisi de olur)
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kullanıcıdan gelen belgeyi oku ve varsa içindeki tüm kişi **isim** ve **adres** bilgilerini ayıkla. "
                        "Sadece isim ve adresleri tablo halinde, Türkçe başlıklarla yaz (örn: İsim, Adres, Şehir). "
                        "Başka hiçbir şey yazma."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Lütfen bu dosyadan isim ve adresleri çıkar:"},
                        {
                            "type": "file",
                            "file": {
                                "name": uploaded_file.name,
                                "mime_type": uploaded_file.type,
                                "data": file_bytes,
                            },
                        },
                    ],
                }
            ],
            max_tokens=1200,
            api_key=api_key,
        )
        st.markdown(response.choices[0].message.content)
else:
    st.info("Belgeyi yükle ve OpenAI API anahtarını gir.")

st.markdown("""
---
:bulb: **Kullanım:**  
1. PDF veya görsel dosyanı yükle  
2. OpenAI API Key’ini gir  
3. AI otomatik olarak tablo halinde isim ve adresleri çıkarır.
""")
