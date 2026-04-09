import streamlit as st
import pandas as pd
import numpy as np
import joblib
import random
from gtts import gTTS
import io
import time
import base64
from fuzzywuzzy import fuzz

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# CSS Tùy chỉnh
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border-left: 5px solid #6366f1; }
    .feedback-card { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white; padding: 25px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. TẢI TÀI NGUYÊN ---
@st.cache_resource
def load_assets():
    try:
        df = pd.read_csv('10000_esl_dataset.csv')
        model = joblib.load('esl_model.pkl')
        return df, model
    except: return None, None

df, nlp_model = load_assets()

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- 3. KHỞI TẠO TRẠNG THÁI (SESSION STATE) ---
if "step" not in st.session_state: st.session_state.step = 0
if "last_processed_id" not in st.session_state: st.session_state.last_processed_id = ""

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8649/8649603.png", width=120)
st.sidebar.title("ESL AI Tutor")

# Lời chào cố định
st.markdown('<div class="main-card">🌐 <b>AI Tutor:</b> Hello! I am your AI partner. How can I help you practice English today?</div>', unsafe_allow_html=True)

# --- KHỐI HIỂN THỊ KẾT QUẢ DUY NHẤT ---
if st.session_state.step == 1:
    user_txt = st.session_state.user_text
    bot_txt = st.session_state.bot_reply
    
    # Tạo ID duy nhất dựa trên thời gian và nội dung
    current_msg_id = f"{hash(bot_txt)}_{st.session_state.get('response_time', 0)}"

    # CHỈ CHẠY NẾU ĐÂY LÀ LƯỢT MỚI (CHƯA XỬ LÝ)
    if st.session_state.last_processed_id != current_msg_id:
        
        # 1. Hiển thị Feedback
        score = fuzz.ratio(user_txt.lower(), "hello") # Demo score
        st.markdown(f"""
        <div class="feedback-card">
            <h3>⚡ Practice Feedback</h3>
            <p>You said: "<i>{user_txt}</i>"</p>
            <p>Score: <b>{score}%</b> | Fluency: ⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Hiển thị Chatbot Text (CHỈ HIỆN 1 LẦN)
        st.markdown(f'<div class="main-card" style="margin-top:20px;">🤖 <b>AI:</b> {bot_txt}</div>', unsafe_allow_html=True)

        # 3. Phát âm thanh (Autoplay)
        audio_fp = text_to_speech(bot_txt)
        audio_base64 = base64.b64encode(audio_fp.read()).decode()
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

        # 4. KHÓA CỔNG: Ghi nhớ ID này đã xong
        st.session_state.last_processed_id = current_msg_id
    else:
        # Nếu trang web load lại (Rerun), chúng ta KHÔNG làm gì cả hoặc chỉ hiện lại bảng điểm tĩnh
        st.info("Bài học đã hoàn thành. Hãy nói câu tiếp theo để tiếp tục!")

# --- 5. ĐIỀU KHIỂN NHẬP LIỆU ---
st.write("---")
tab1, tab2 = st.tabs(["⌨️ Text", "🎙️ Voice"])

with tab2:
    audio_val = st.audio_input("Bấm micro để nói")
    if audio_val:
        with st.spinner("Đang phân tích..."):
            import speech_recognition as sr
            r = sr.Recognizer()
            try:
                with sr.AudioFile(audio_val) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language="en-US")
                    
                    # Cập nhật Session State và reset cổng
                    st.session_state.user_text = text
                    st.session_state.bot_reply = "Your English is great! Let's try another sentence."
                    st.session_state.step = 1
                    st.session_state.response_time = time.time() # Mở cổng bằng thời gian mới
                    st.rerun()
            except:
                st.error("Không nghe rõ, thử lại nhé!")

with tab1:
    txt_input = st.chat_input("Nhập câu trả lời...")
    if txt_input:
        st.session_state.user_text = txt_input
        st.session_state.bot_reply = "I understand. Let's keep practicing!"
        st.session_state.step = 1
        st.session_state.response_time = time.time()
        st.rerun()
