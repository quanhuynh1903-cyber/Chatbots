import streamlit as st
import pandas as pd
import joblib
import time
import io
import base64
from gtts import gTTS
from fuzzywuzzy import fuzz
import speech_recognition as sr

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI Speaking Partner", page_icon="💬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }
    .user-msg {
        background-color: #0084ff; color: white; padding: 15px;
        border-radius: 18px 18px 2px 18px; margin: 10px 0;
        float: right; clear: both; max-width: 75%;
    }
    .ai-msg {
        background-color: white; color: #1c1e21; padding: 15px;
        border-radius: 18px 18px 18px 2px; margin: 10px 0;
        float: left; clear: both; max-width: 75%;
        border: 1px solid #ddd;
    }
    .feedback-panel {
        background: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 6px solid #4f46e5; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỖ TRỢ ---
def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# --- 3. QUẢN LÝ SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "ai", "content": "Hi! I'm your AI Speaking Partner. Ready to practice?"}]
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None

# --- 4. GIAO DIỆN CHÍNH ---
st.title("💬 Real-time Speaking Conversation")

col_chat, col_feedback = st.columns([2, 1])

with col_chat:
    st.subheader("Chat")
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            div_class = "ai-msg" if msg["role"] == "ai" else "user-msg"
            st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    st.write("---")
    voice_input = st.audio_input("Bấm micro để nói")

    if voice_input:
        with st.spinner("AI đang lắng nghe..."):
            r = sr.Recognizer()
            try:
                with sr.AudioFile(voice_input) as source:
                    audio_data = r.record(source)
                    user_text = r.recognize_google(audio_data, language="en-US")
                    
                    # Cập nhật hội thoại
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    
                    # Logic phản hồi (Demo)
                    ai_reply = "That's interesting! Can you tell me more?"
                    if "hello" in user_text.lower(): ai_reply = "Hello there! How are you today?"
                    
                    st.session_state.messages.append({"role": "ai", "content": ai_reply})
                    
                    # Phân tích Feedback
                    score = min(100, len(user_text) * 5 + 40)
                    st.session_state.last_feedback = {
                        "text": user_text,
                        "score": score,
                        "suggestion": "Good flow. Try adding more details to your answer."
                    }
                    st.rerun()
            except:
                st.error("Xin lỗi, tôi không nghe rõ. Thử lại nhé!")

# --- 5. PHẦN FEEDBACK (ĐÃ FIX LỖI SYNTAX) ---
with col_feedback:
    st.subheader("Practice Feedback")
    
    # FIX: Tách việc gán và kiểm tra điều kiện
    fb = st.session_state.last_feedback 
    
    if fb is not None:
        st.markdown(f"""
        <div class="feedback-panel">
            <p style="color: #666; font-size: 0.8em; margin-bottom: 5px;">PHÂN TÍCH CÂU VỪA NÓI</p>
            <h2 style="margin: 0; color: #4f46e5;">{fb['score']}%</h2>
            <p style="font-weight: bold; margin-top: 10px;">Câu của bạn:</p>
            <p style="font-style: italic; color: #444;">"{fb['text']}"</p>
            <hr>
            <p><b>Lời khuyên:</b><br>{fb['suggestion']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Phát giọng nói cho câu trả lời mới nhất của AI
        last_ai_msg = st.session_state.messages[-1]["content"]
        st.markdown(speak(last_ai_msg), unsafe_allow_html=True)
    else:
        st.info("Hãy nói gì đó để bắt đầu cuộc đối thoại!")

with st.sidebar:
    if st.button("Reset Conversation"):
        st.session_state.clear()
        st.rerun()
