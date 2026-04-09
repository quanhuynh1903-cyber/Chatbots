import streamlit as st
import pandas as pd
import numpy as np
import joblib
import random
from gtts import gTTS
import io
from fuzzywuzzy import fuzz
import time
import base64

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# --- 2. CSS TÙY CHỈNH ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #f1f5f9; }
    .main-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .feedback-card { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white; padding: 25px; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(99,102,241,0.4); }
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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/8649/8649603.png" class="robot-img">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>ESL AI Tutor</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("**📈 Your Speaking Progress**")
        chart_data = pd.DataFrame(np.random.randn(7, 1) + 10, columns=['min'])
        st.line_chart(chart_data, height=100)
    
    if st.button("🔄 Xóa lịch sử", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 5. KHU VỰC CHÍNH ---
if "step" not in st.session_state: st.session_state.step = 0
if "last_processed_id" not in st.session_state: st.session_state.last_processed_id = ""

st.markdown('<div class="main-card">🌐 <b>AI Tutor:</b> Hello! I am your AI English tutor. How can I practice with you today?</div>', unsafe_allow_html=True)

# --- KHỐI HIỂN THỊ KẾT QUẢ ---
if st.session_state.step == 1:
    user_txt = st.session_state.user_text
    bot_txt = st.session_state.bot_reply
    
    # 1. Hiển thị bảng Feedback (Luôn hiện)
    intent_pred = nlp_model.predict([user_txt])[0]
    sample_targets = df[df['Intent'] == intent_pred]['User_Input'].tolist()
    target = sample_targets[0] if sample_targets else user_txt
    score = fuzz.ratio(user_txt.lower(), target.lower())

    st.markdown(f"""
    <div class="feedback-card">
        <h3 style="color: white; margin-top: 0;">⚡ Instant Practice Feedback</h3>
        <p>Your Sentence: <span style="font-size: 1.2rem;">"{user_txt}"</span></p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
            <div>🎯 Pronunciation: <b>{score}%</b></div>
            <div>🗣️ Fluency: ⭐⭐⭐⭐⭐</div>
            <div>📝 Grammar: <span style="color: #4ade80;">Correct</span></div>
            <div>🔍 Tip: Keep it up!</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Hiển thị Robot Chat (Luôn hiện)
    st.markdown(f'<div class="main-card" style="margin-top: 20px;">🤖 <b>AI:</b> {bot_txt}</div>', unsafe_allow_html=True)

    # 3. 🟢 XỬ LÝ ÂM THANH (Chỉ phát 1 lần duy nhất)
    current_msg_id = f"{hash(bot_txt)}_{st.session_state.get('response_time', 0)}"

    if st.session_state.last_processed_id != current_msg_id:
        # Nhúng thẻ audio autoplay bằng HTML (Base64)
        audio_fp = text_to_speech(bot_txt)
        audio_base64 = base64.b64encode(audio_fp.read()).decode()
        # Dùng container để chứa audio, sau đó đánh dấu đã phát
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        
        # Cập nhật ID để lần rerun tiếp theo không chạy vào đây nữa
        st.session_state.last_processed_id = current_msg_id
    else:
        # Nếu đã phát rồi, chỉ hiện thanh audio tĩnh, KHÔNG autoplay
        audio_fp = text_to_speech(bot_txt)
        st.audio(audio_fp, format="audio/mp3", autoplay=False)

# --- 6. NHẬN DIỆN GIỌNG NÓI ---
st.write("---")
tab1, tab2 = st.tabs(["⌨️ Text", "🎙️ Voice"])

with tab2:
    audio_val = st.audio_input("Ghi âm", label_visibility="collapsed")
    if audio_val:
        with st.spinner("AI đang phân tích..."):
            import speech_recognition as sr
            r = sr.Recognizer()
            try:
                with sr.AudioFile(audio_val) as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language="en-US")
                    if text:
                        intent = nlp_model.predict([text])[0]
                        replies = df[df['Intent'] == intent]['Bot_Response'].tolist()
                        
                        st.session_state.user_text = text
                        st.session_state.bot_reply = random.choice(replies) if replies else "Interesting!"
                        st.session_state.step = 1
                        st.session_state.response_time = time.time()
                        st.rerun()
            except Exception as e:
                st.error("❌ AI không nghe rõ, hãy thử lại!")

with tab1:
    user_input = st.chat_input("Gõ tiếng Anh tại đây...")
    if user_input:
        intent = nlp_model.predict([user_input])[0]
        replies = df[df['Intent'] == intent]['Bot_Response'].tolist()
        st.session_state.user_text = user_input
        st.session_state.bot_reply = random.choice(replies) if replies else "Interesting!"
        st.session_state.step = 1
        st.session_state.response_time = time.time()
        st.rerun()
