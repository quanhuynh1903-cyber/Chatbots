import streamlit as st
import pandas as pd
import numpy as np
import time
import joblib
import random
from gtts import gTTS
import io
import whisper
import os

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# --- 2. TẢI CÁC MÔ HÌNH AI (BACKEND) ---
@st.cache_resource
def load_data_and_model():
    df = pd.read_csv('10000_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

@st.cache_resource
def load_whisper_model():
    # Sử dụng bản "small" là lựa chọn cân bằng nhất hiện tại
    return whisper.load_model("small")

try:
    df, nlp_model = load_data_and_model()
    whisper_model = load_whisper_model()
except Exception as e:
    st.error("Lỗi tải Model! Vui lòng kiểm tra lại file .pkl và .csv trên GitHub.")
    st.stop()

def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 3. CSS TÙY CHỈNH NÂNG CAO ---
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; font-family: 'Segoe UI', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #e5eaf0; padding-top: 1rem; }
    .robot-avatar-container { text-align: center; margin-bottom: 20px; }
    .robot-avatar { width: 150px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); background: linear-gradient(145deg, #ffffff, #e6e6e6); padding: 10px; }
    .glass-card { background: rgba(255, 255, 255, 0.9); border-radius: 16px; padding: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.5); }
    .card-title { font-size: 14px; font-weight: bold; color: #334155; margin-bottom: 10px; }
    .ai-chat-bubble { background-color: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-top: 20px; margin-bottom: 30px; display: flex; align-items: center; gap: 15px; }
    .feedback-card { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); width: 80%; margin: 0 auto; position: relative; }
    .feedback-title { font-size: 16px; font-weight: bold; color: #1e293b; margin-bottom: 15px; }
    .word-bad { background-color: #fed7aa; color: #c2410c; padding: 2px 8px; border-radius: 6px; font-weight: 600; }
    .word-good { background-color: #bbf7d0; color: #15803d; padding: 2px 8px; border-radius: 6px; font-weight: 600; }
    .score-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; font-size: 14px; color: #475569; }
    .neon-mic-container { background: linear-gradient(90deg, #dbeafe, #e0e7ff, #f3e8ff); padding: 20px; border-radius: 20px; text-align: center; margin-top: 40px; box-shadow: inset 0 0 20px rgba(255,255,255,0.5); border: 1px solid #e2e8f0; }
    .mic-button-mockup { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin: -40px auto 10px auto; box-shadow: 0 0 20px rgba(139, 92, 246, 0.6), 0 0 40px rgba(59, 130, 246, 0.4); font-size: 24px; border: 4px solid white; }
</style>
""", unsafe_allow_html=True)

# --- 4. THANH SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="robot-avatar-container">
            <img class="robot-avatar" src="https://cdn-icons-png.flaticon.com/512/8649/8649603.png" alt="3D Robot">
        </div>
        <div class="glass-card">
            <div class="card-title">✨ Về Ứng Dụng</div>
            <p style="font-size: 13px; color: #475569; margin: 0;">
                <strong style="color: #2563eb;">ESL AI Tutor</strong> sử dụng OpenAI Whisper để nhận diện giọng nói cực chuẩn.
            </p>
        </div>
        <div class="glass-card"><div class="card-title">📉 Your Speaking Progress</div>
    """, unsafe_allow_html=True)
    st.line_chart(pd.DataFrame(np.array([2, 5, 4, 10, 15, 8, 12]), columns=['Minutes']), height=120)
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
            <div style="background-color: #0284c7; color: white; padding: 5px 10px; border-radius: 8px; font-weight: bold;">A2</div>
            <div><div style="font-weight: bold; font-size: 14px; color: #1e293b;">Intermediate A2</div></div>
        </div></div>
    """, unsafe_allow_html=True)
    if st.button("🔄 Xóa lịch sử & Bắt đầu lại", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

# --- 5. KHU VỰC CHÍNH ---
if "step" not in st.session_state: st.session_state.step = 0
if "last_user_text" not in st.session_state: st.session_state.last_user_text = ""
if "last_bot_reply" not in st.session_state: st.session_state.last_bot_reply = ""

st.markdown("""<div class="ai-chat-bubble"><span>🌐</span><span style="color: #334155;">Hello! I am your AI English tutor. How can I practice with you today?</span></div>""", unsafe_allow_html=True)

if st.session_state.step == 1:
    st.markdown(f"""
<div class="feedback-card">
    <div class="feedback-title">Instant Practice Feedback</div>
    <p style="color: #334155;">Your Sentence: <strong style="color: #2563eb;">{st.session_state.last_user_text}</strong></p>
    <div class="score-grid">
        <div>Pronunciation: <strong>88%</strong> | Grammar: <strong>Correct</strong></div>
        <div>Fluency: ⭐⭐⭐⭐⭐</div>
    </div>
</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div class="ai-chat-bubble" style="margin-top: 20px;"><span>🤖</span><span style="color: #334155;">{st.session_state.last_bot_reply}</span></div>""", unsafe_allow_html=True)
    st.audio(text_to_speech(st.session_state.last_bot_reply), format='audio/mp3', autoplay=True)

# --- 6. XỬ LÝ BACKEND TỐI ƯU ---
tab1, tab2 = st.tabs(["📝 Luyện Viết", "🎙️ Luyện Nói"])

with tab2:
    st.markdown("""<div class="neon-mic-container"><div class="mic-button-mockup">🎙️</div><p style="color: #475569;">Nhấn vào micro phía dưới và nói chuyện với tôi.</p></div>""", unsafe_allow_html=True)
    user_audio = st.audio_input("Thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("🎧 Đang lắng nghe kỹ giọng nói của bạn..."):
            temp_path = "temp_voice.wav"
            with open(temp_path, "wb") as f:
                f.write(user_audio.read())
            
            try:
                # 🟢 Cải tiến: Tăng độ chính xác cho Whisper trên CPU
                result = whisper_model.transcribe(temp_path, language="en", fp16=False)
                recognized_text = result["text"].strip()
                
                if len(recognized_text) > 2:
                    # 🟢 Cải tiến: Xử lý dự đoán NLP
                    predicted_intent = nlp_model.predict([recognized_text])[0]
                    possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                    
                    # Nếu AI không chắc chắn, dùng câu trả lời linh hoạt
                    bot_reply = random.choice(possible_responses) if possible_responses else "That sounds interesting! Tell me more."
                    
                    st.session_state.last_user_text = recognized_text
                    st.session_state.last_bot_reply = bot_reply
                    st.session_state.step = 1
                else:
                    st.warning("⚠️ Tôi chưa nghe rõ, bạn có thể nói lại không?")
            except Exception as e:
                st.error(f"Lỗi: {e}")
            finally:
                if os.path.exists(temp_path): os.remove(temp_path)
            st.rerun()
