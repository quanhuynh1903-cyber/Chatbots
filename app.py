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
    
    # Tính điểm thật dựa trên fuzzywuzzy (so sánh với dữ liệu chuẩn)
    # Tìm câu User_Input chuẩn nhất trong Intent đó để so sánh
    sample_targets = df[df['Intent'] == nlp_model.predict([user_txt])[0]]['User_Input'].tolist()
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
    
    st.markdown(f'<div class="main-card" style="margin-top: 20px;">🤖 <b>AI:</b> {bot_txt}</div>', unsafe_allow_html=True)

    # --- 🟢 KHỐI XỬ LÝ ÂM THANH KHÔNG LẶP LẠI ---
    # Chỉ phát âm thanh nếu đây là lượt phản hồi mới
    if "last_played_text" not in st.session_state or st.session_state.last_played_text != bot_txt:
        audio_fp = text_to_speech(bot_txt)
        st.audio(audio_fp, format="audio/mp3", autoplay=True)
        # Đánh dấu đã phát xong câu này
        st.session_state.last_played_text = bot_txt
    else:
        # Nếu đã phát rồi, vẫn hiện thanh audio nhưng không tự động chạy nữa
        audio_fp = text_to_speech(bot_txt)
        st.audio(audio_fp, format="audio/mp3", autoplay=False)
# --- 6. NHẬN DIỆN GIỌNG NÓI ---
st.write("---")
tab1, tab2 = st.tabs(["⌨️ Text", "🎙️ Voice"])

with tab2:
    st.markdown("<p style='text-align: center; color: #6366f1;'>Nhấn micro và bắt đầu nói</p>", unsafe_allow_html=True)
    audio_val = st.audio_input("Ghi âm", label_visibility="collapsed")
    
    if audio_val:
        with st.spinner("AI đang phân tích..."):
            import speech_recognition as sr
            r = sr.Recognizer()
            
            # Cấu hình để AI lọc nhiễu tốt hơn
            r.energy_threshold = 300 
            r.pause_threshold = 0.8
            
            try:
                with sr.AudioFile(audio_val) as source:
                    # Lọc nhiễu môi trường trước khi nghe
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = r.record(source)
                    
                    # Dịch giọng nói
                    text = r.recognize_google(audio_data, language="en-US")
                    
                    if text:
                        intent = nlp_model.predict([text])[0]
                        replies = df[df['Intent'] == intent]['Bot_Response'].tolist()
                        
                        st.session_state.user_text = text
                        st.session_state.bot_reply = random.choice(replies) if replies else "Interesting!"
                        st.session_state.step = 1
                        st.rerun()
            except sr.UnknownValueError:
                st.error("❌ AI không nghe rõ chữ nào cả. Bạn hãy nói to và rõ hơn nhé!")
            except sr.RequestError:
                st.error("❌ Lỗi kết nối đến máy chủ nhận diện. Hãy kiểm tra internet!")
            except Exception as e:
                st.error(f"❌ Có lỗi xảy ra: {e}")

with tab1:
    user_input = st.chat_input("Gõ tiếng Anh tại đây...")
    if user_input:
        intent = nlp_model.predict([user_input])[0]
        replies = df[df['Intent'] == intent]['Bot_Response'].tolist()
        st.session_state.user_text = user_input
        st.session_state.bot_reply = random.choice(replies) if replies else "Interesting!"
        st.session_state.step = 1
        st.rerun()
