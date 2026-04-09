import streamlit as st
import whisper
import random
import time
import base64
from gtts import gTTS
import io

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="AI Language Partner", layout="wide")

# Tải model Whisper một lần duy nhất (Bản Tiny để không sập RAM)
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")

model = load_whisper()

# --- GIAO DIỆN CSS (HIỆN ĐẠI 2026) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .chat-container {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 25px;
        padding: 30px;
        backdrop-filter: blur(10px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.5);
    }
    .robot-box { text-align: center; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: TIẾN TRÌNH ---
with st.sidebar:
    st.markdown("<div class='robot-box'><img src='https://cdn-icons-png.flaticon.com/512/8649/8649603.png' width='150'></div>", unsafe_allow_html=True)
    st.title("My AI Tutor")
    st.progress(65, text="Trình độ: Intermediate A2")
    st.divider()
    if st.button("🔄 Làm mới buổi học"):
        st.session_state.clear()
        st.rerun()

# --- LOGIC XỬ LÝ CHÍNH ---
if "history" not in st.session_state:
    st.session_state.history = []

# Hiển thị hội thoại
chat_placeholder = st.container()

with chat_placeholder:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.write("🤖 **AI Tutor:** Hello! Let's start our English lesson. What would you like to talk about today?")
    
    # Khu vực hiển thị kết quả sau khi nói
    if "user_speech" in st.session_state:
        st.write(f"🧑 **You:** {st.session_state.user_speech}")
        st.info(f"🤖 **AI Response:** {st.session_state.bot_response}")
        
        # CHỐNG LẶP TIẾNG BẰNG CÁCH CHỈ PHÁT KHI CÓ AUDIO_KEY MỚI
        if st.session_state.get("played_key") != st.session_state.audio_key:
            tts = gTTS(text=st.session_state.bot_response, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format="audio/mp3", autoplay=True)
            st.session_state.played_key = st.session_state.audio_key
    st.markdown("</div>", unsafe_allow_html=True)

# --- NHẬN DIỆN GIỌNG NÓI ---
st.write("---")
audio_input = st.audio_input("Bấm để nói chuyện với AI")

if audio_input:
    with st.spinner("AI đang lắng nghe..."):
        # 1. Lưu file tạm
        with open("temp.wav", "wb") as f:
            f.write(audio_input.read())
        
        # 2. Dùng Whisper nhận diện (Cực chuẩn)
        result = model.transcribe("temp.wav")
        user_text = result["text"]
        
        # 3. Logic trả lời (Bạn có thể thay bằng nlp_model.predict cũ hoặc GPT API)
        # Giả lập trả lời
        responses = ["That's very interesting!", "Could you please explain more?", "Your pronunciation is getting better!"]
        bot_reply = random.choice(responses)
        
        # 4. Lưu vào session và tạo khóa âm thanh mới
        st.session_state.user_speech = user_text
        st.session_state.bot_response = bot_reply
        st.session_state.audio_key = str(time.time()) # Tạo key mới để phát nhạc
        st.rerun()
