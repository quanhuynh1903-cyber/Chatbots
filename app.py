import streamlit as st
import pandas as pd
import joblib
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="ESL AI Chatbot", layout="wide")

# --- LOAD DỮ LIỆU & MODEL ---
@st.cache_resource
def load_assets():
    model = joblib.load('esl_model.pkl')
    df = pd.read_csv('10000_esl_dataset.csv')
    return model, df

model, df = load_assets()

# --- GIAO DIỆN CHÍNH ---
st.title("🎙️ Improving ESL Speaking Skills using AI")
st.markdown("---")

# Sidebar cho cấu hình
with st.sidebar:
    st.header("Settings")
    mode = st.selectbox("Choose Mode", ["Role-play", "Topic Discussion", "Debate"])
    speed = st.slider("Voice Speed", 0.5, 2.0, 1.0)
    st.info("Model hiện tại hỗ trợ: Airport, Directions, Job Interview, v.v.")

# --- XỬ LÝ GHI ÂM (STT) ---
st.subheader("Start Speaking:")
audio = mic_recorder(start_prompt="Click to Speak 🎤", stop_prompt="Stop Recording 🛑", key='recorder')

if audio:
    # Ở đây bạn sẽ gửi audio.bytes đến Whisper API của OpenAI
    # Giả sử chúng ta có text sau khi chuyển đổi:
    user_text = "I want to practice airport custom" # Demo text
    st.success(f"You said: {user_text}")

    # Dự đoán Intent bằng model .pkl của bạn
    prediction = model.predict([user_text])[0]
    st.write(f"Detected Intent: **{prediction}**")

    # Lấy phản hồi từ dataset hoặc LLM
    response = df[df['Intent'] == prediction]['Bot_Response'].values[0]
    st.chat_message("assistant").write(response)

    # --- TEXT TO SPEECH (TTS) ---
    tts = gTTS(text=response, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    st.audio(audio_fp, format='audio/mp3')

# --- HỆ THỐNG ĐÁNH GIÁ (ANALYTICS) ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Fluency", "85%", "+2%")
col2.metric("Grammar Accuracy", "90%", "+5%")
col3.metric("Daily Streak", "5 Days", "🔥")
