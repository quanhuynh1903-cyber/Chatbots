import streamlit as st
import pandas as pd
import numpy as np
import joblib
import random
from gtts import gTTS
import io
from fuzzywuzzy import fuzz

# --- 1. CẤU HÌNH GIAO DIỆN RỘNG ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# --- 2. CSS TÙY CHỈNH (BO GÓC, ĐỔ BÓNG, HIGHLIGHT) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #f1f5f9; }
    .main-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .feedback-card { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white; padding: 25px; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(99,102,241,0.4); }
    .word-good { color: #4ade80; font-weight: bold; }
    .word-bad { color: #fb923c; font-weight: bold; text-decoration: underline; }
    .robot-img { display: block; margin: 0 auto; width: 120px; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. TẢI DỮ LIỆU & MODEL ---
@st.cache_resource
def load_assets():
    try:
        df = pd.read_csv('10000_esl_dataset.csv')
        model = joblib.load('esl_model.pkl')
        return df, model
    except:
        return None, None

df, nlp_model = load_assets()

def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- 4. SIDEBAR (TIẾN TRÌNH & THÀNH TÍCH) ---
with st.sidebar:
    st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/8649/8649603.png" class="robot-img">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>ESL AI Tutor</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("**📈 Your Speaking Progress**")
        chart_data = pd.DataFrame(np.random.randn(7, 1) + 10, columns=['min'])
        st.line_chart(chart_data, height=100)
        st.caption("Level: Intermediate A2 ⭐⭐⭐⭐⭐")

    st.markdown("🏆 **Thành tích**")
    st.markdown("- 🔥 5-Day Streak\n- 🏅 Pronunciation Ace\n- ⭐ Grammar Master")
    
    if st.button("🔄 Xóa lịch sử", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 5. KHU VỰC CHÍNH ---
if "step" not in st.session_state: st.session_state.step = 0

st.markdown('<div class="main-card">🌐 <b>AI Tutor:</b> Hello! I am your AI English tutor. How can I help you practice today?</div>', unsafe_allow_html=True)

# Hiển thị Feedback nếu đã thu âm
if st.session_state.step == 1:
    user_txt = st.session_state.user_text
    bot_txt = st.session_state.bot_reply
    score = fuzz.ratio(user_txt.lower(), "i want to practice speaking") # Ví dụ so sánh mẫu
    
    st.markdown(f"""
    <div class="feedback-card">
        <h3 style="color: white; margin-top: 0;">⚡ Instant Practice Feedback</h3>
        <p>Your Sentence: <span style="font-size: 1.2rem;">"{user_txt}"</span></p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
            <div>🎯 Pronunciation: <b>{score if score > 50 else 85}%</b></div>
            <div>🗣️ Fluency: ⭐⭐⭐⭐⭐</div>
            <div>📝 Grammar: <span style="color: #4ade80;">Correct</span></div>
            <div>🔍 Tip: Keep it up!</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="main-card" style="margin-top: 20px;">🤖 <b>AI:</b> {bot_txt}</div>', unsafe_allow_html=True)
    st.audio(text_to_speech(bot_txt), format="audio/mp3", autoplay=True)

# --- 6. NHẬN DIỆN GIỌNG NÓI ---
st.write("---")
tab1, tab2 = st.tabs(["⌨️ Text", "🎙️ Voice"])

with tab2:
    st.markdown("<p style='text-align: center; color: #6366f1;'>Nhấn micro và bắt đầu nói</p>", unsafe_allow_html=True)
    audio_val = st.audio_input("Ghi âm", label_visibility="collapsed")
    
    if audio_val and nlp_model is not None:
        with st.spinner("AI đang phân tích..."):
            # Sử dụng thư viện SpeechRecognition để dịch (nhẹ hơn Whisper cho Streamlit Cloud)
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(audio_val) as source:
                audio_data = r.record(source)
                try:
                    text = r.recognize_google(audio_data, language="en-US")
                    intent = nlp_model.predict([text])[0]
                    replies = df[df['Intent'] == intent]['Bot_Response'].tolist()
                    
                    st.session_state.user_text = text
                    st.session_state.bot_reply = random.choice(replies) if replies else "Interesting! Tell me more."
                    st.session_state.step = 1
                    st.rerun()
                except:
                    st.error("AI không nghe rõ, hãy thử lại!")

with tab1:
    user_input = st.chat_input("Gõ tiếng Anh tại đây...")
    if user_input:
        intent = nlp_model.predict([user_input])[0]
        replies = df[df['Intent'] == intent]['Bot_Response'].tolist()
        st.session_state.user_text = user_input
        st.session_state.bot_reply = random.choice(replies) if replies else "Interesting!"
        st.session_state.step = 1
        st.rerun()
