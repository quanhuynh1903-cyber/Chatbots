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

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# CSS Tùy chỉnh (Giao diện hiện đại)
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border-left: 5px solid #6366f1; }
    .feedback-card { 
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); 
        color: white; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .feedback-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .feedback-table td { padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.2); }
    .status-badge { background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.9em; }
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

# --- 3. KHỞI TẠO TRẠNG THÁI ---
if "step" not in st.session_state: st.session_state.step = 0
if "last_processed_id" not in st.session_state: st.session_state.last_processed_id = ""

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8649/8649603.png", width=120)
st.sidebar.title("ESL AI Tutor")

# Lời chào cố định
st.markdown('<div class="main-card">🌐 <b>AI Tutor:</b> Hello! I am your AI partner. How can I help you practice English today?</div>', unsafe_allow_html=True)

# --- KHỐI HIỂN THỊ KẾT QUẢ (PRACTICE FEEDBACK) ---
if st.session_state.step == 1:
    user_txt = st.session_state.user_text
    bot_txt = st.session_state.bot_reply
    
    current_msg_id = f"{hash(bot_txt)}_{st.session_state.get('response_time', 0)}"

    if st.session_state.last_processed_id != current_msg_id:
        # Logic phân tích điểm số dựa trên câu trả lời
        score = fuzz.ratio(user_txt.lower(), bot_txt.lower())
        
        if score >= 85:
            status, analysis, guidance = "Excellent", "Natural response with high accuracy.", "Try using more advanced vocabulary next time."
        elif score >= 60:
            status, analysis, guidance = "Good Effort", "Clear meaning, but minor structure issues.", "Pay attention to word order and prepositions."
        else:
            status, analysis, guidance = "Keep Practicing", "Significant differences detected.", "Listen to the AI and repeat the sentence out loud."

        # Render Giao diện Feedback dạng bảng
        st.markdown(f"""
        <div class="feedback-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">⚡ Practice Feedback</h3>
                <span class="status-badge">{status}</span>
            </div>
            <table class="feedback-table">
                <tr>
                    <td><b>Accuracy Score</b></td>
                    <td style="text-align: right;"><b>{score}%</b></td>
                </tr>
                <tr>
                    <td><b>Error Analysis</b></td>
                    <td style="text-align: right; font-size: 0.9em;">{analysis}</td>
                </tr>
                <tr>
                    <td style="border:none;"><b>Guidance</b></td>
                    <td style="text-align: right; border:none; font-size: 0.9em; font-style: italic;">{guidance}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Hiển thị phản hồi của AI
        st.markdown(f'<div class="main-card" style="margin-top:20px;">🤖 <b>AI Tutor:</b> {bot_txt}</div>', unsafe_allow_html=True)

        # Phát âm thanh tự động
        audio_fp = text_to_speech(bot_txt)
        audio_base64 = base64.b64encode(audio_fp.read()).decode()
        st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

        st.session_state.last_processed_id = current_msg_id
    else:
        st.info("Task completed. Ready for your next sentence!")

# --- 5. ĐIỀU KHIỂN NHẬP LIỆU ---
st.write("---")
tab1, tab2 = st.tabs(["⌨️ Text Input", "🎙️ Voice Practice"])

with tab2:
    audio_val = st.audio_input("Press the mic to speak")
    if audio_val:
        with st.spinner("Analyzing your voice..."):
            import speech_recognition as sr
            r = sr.Recognizer()
            try:
                with sr.AudioFile(audio_val) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language="en-US")
                    
                    st.session_state.user_text = text
                    st.session_state.bot_reply = "Your pronunciation is clear! Let's continue."
                    st.session_state.step = 1
                    st.session_state.response_time = time.time()
                    st.rerun()
            except:
                st.error("Sorry, I couldn't hear you clearly. Please try again!")

with tab1:
    txt_input = st.chat_input("Type your answer here...")
    if txt_input:
        st.session_state.user_text = txt_input
        st.session_state.bot_reply = "I understand. Let's keep practicing!"
        st.session_state.step = 1
        st.session_state.response_time = time.time()
        st.rerun()
