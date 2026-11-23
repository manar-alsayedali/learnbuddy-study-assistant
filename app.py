import streamlit as st
import pyrebase
import re
from time import monotonic
from openai import OpenAI
from streamlit.errors import StreamlitSecretNotFoundError

st.set_page_config(page_title="LearnBuddy", layout="centered")

try:
    firebase_config = dict(st.secrets["firebase"])
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except (KeyError, StreamlitSecretNotFoundError):
    st.error("Kurulum eksik. README'deki .streamlit/secrets.toml adımlarını izleyin.")
    st.stop()

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

st.title("Welcome to LearnBuddy")
st.markdown("Kişiye özel ders planı ve kaynak önerisi için yapay zeka asistanınız!")
st.markdown("---")

# Oturum durumu
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------------
#  Giriş ve Kayıt Olma
# -------------------------------
if not st.session_state.logged_in:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            st.session_state.page = "login"
    with col2:
        if st.button("Hesap Oluştur"):
            st.session_state.page = "signup"

    if st.session_state.page == "login":
        st.subheader("Giriş Sayfası")
        email = st.text_input("Email adresi", key="login_email")
        password = st.text_input("Şifre", type="password", key="login_password")
        if st.button("Giriş", key="login_submit"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.firebase_user = user
                st.session_state.refresh_at = monotonic() + int(user["expiresIn"]) - 60
                st.session_state.logged_in = True
            except Exception:
                st.error("Email veya şifre hatalı!!!")
            else:
                st.rerun()

    elif st.session_state.page == "signup":
        st.subheader("Hesap Oluşturma Sayfası")
        email = st.text_input("Email adresi", key="signup_email")
        password = st.text_input("Şifre", type="password", key="signup_password")
        if st.button("Hesap Oluştur", key="signup_submit"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Hesap oluşturuldu! Şimdi giriş yapabilirsin.")
            except Exception:
                st.error("Bu email zaten kayıtlı veya şifre zayıf!")

# ------------------------
#     Ana Sayfa
# ------------------------
else:
    user = st.session_state.firebase_user
    if monotonic() >= st.session_state.refresh_at:
        try:
            refreshed = auth.refresh(user["refreshToken"])
            user.update(refreshed)
            st.session_state.refresh_at = monotonic() + 3500
        except Exception:
            st.session_state.logged_in = False
            st.session_state.pop("firebase_user", None)
            st.rerun()

    user_id = user["localId"]
    id_token = user["idToken"]
    st.subheader("Ders Planı Oluşturucu")
    st.markdown("Aşağıdan bir ders seçin ve hedefinizi belirleyin...")

    dersler = [
        "Algoritma ve Analiz", "Veri Yapıları", "Veritabanı",
        "Calculus 1", "Calculus 2", "Yapay Zeka",
        "Bilgisayar Ağları", "İşletim Sistemleri",
        "Sistem Programlama", "Veri İletişim"
    ]

    hedefler = [
        "Konuyu anlamak (genel kavrama)",
        "Test sınavına hazırlanmak",
        "Klasik sınav için çalışmak",
        "İleri düzey bilgi geliştirmek"
    ]

    seviyeler = [
        "Yeni başlıyorum (hiç bilmiyorum)",
        "Orta seviyedeyim (bazı şeyleri biliyorum)",
        "Konuya oldukça hakimim (geliştirmek istiyorum)"
    ]

    ders = st.selectbox("Çalışmak istediğiniz dersi seçin:", dersler)
    hedef = st.radio("Hedefinizi seçin:", hedefler)
    seviye = st.radio("Bu dersteki seviyenizi belirtin:", seviyeler)

    if st.button("Yapay Zeka ile Plan Oluştur"):
        with st.spinner("Plan oluşturuluyor..."):
            try:
                prompt = f"""
Sen bir yapay zeka eğitim asistanısın. Öğrenci sana aşağıdaki bilgilerle geldi:

Ders: {ders}
Hedef: {hedef}
Seviye: {seviye}

Lütfen öğrencinin seviyesine uygun, 5 adımlık kısa bir çalışma planı hazırla.
Her adım 2-3 cümle olsun.
Her seviye için ona faydalı ve uygun kaynaklar öner (youtube kanallari dahil - linkler - kanalın ismi - website).
Her seviye için ona hedeflerine göre uygun sorular hazırla (5-10 soru).
"""

                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model=st.secrets.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                content = response.choices[0].message.content

                match = re.search(r"⁠  (?:[a-zA-Z]*)?\s*([\s\S]*?)  ⁠", content, re.DOTALL)
                plan_text = match.group(1).strip() if match else content.strip()

                db.child("users").child(user_id).child(ders).set({
                    "plan": plan_text,
                    "progress": 0
                }, token=id_token)

                st.success("Plan başarıyla kaydedildi!")

            except Exception:
                st.error("Plan oluşturulamadı veya kaydedilemedi. API ve Firebase ayarlarını kontrol edin.")

        st.markdown("---")
    st.subheader("Planlarım")

    show_plans = st.checkbox("Planlarımı Göster", key="show_plans")

    if show_plans:
        user_plans = db.child("users").child(user_id).get(token=id_token)

        if user_plans.each():
            plan_names = [material.key() for material in user_plans.each()]
            selected_plan = st.selectbox("Bir plan seçin:", plan_names)

            selected_data = db.child("users").child(user_id).child(selected_plan).get(token=id_token).val()
            plan_text = selected_data.get("plan", "")
            progress = selected_data.get("progress", 0)

            st.markdown(f"### {selected_plan}")
            st.progress(min(progress / 5, 1.0))  # Gelişimi gösteren bir çubuk
            st.markdown(plan_text)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Bir Seviye İlerle", key=f"progress_{selected_plan}"):
                    db.child("users").child(user_id).child(selected_plan).update({
                        "progress": progress + 1
                    }, token=id_token)
                    st.rerun()
            with col2:
                if st.button("Planı Sil", key=f"delete_{selected_plan}"):
                    db.child("users").child(user_id).child(selected_plan).remove(token=id_token)
                    st.rerun()
        else:
            st.info("Henüz kayıtlı bir plan yok.")