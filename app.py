import streamlit as st
import pandas as pd
import joblib
import time
import io
import base64
import random
from gtts import gTTS
from fuzzywuzzy import fuzz
import speech_recognition as sr

# --- 1. CẤU HÌNH GIAO DIỆN (UI/UX) ---
st.set_page_config(page_title="Voice-First AI Tutor", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #fcfcfd; }
    
    /* Card Phản hồi chính */
    .analysis-card {
        background: white;
        padding: 30px;
        border-radius: 24px;
        border: 1px solid #f1f1f3;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.04);
        margin-bottom: 25px;
    }
    
    /* Chỉ số Feedback */
    .stat-pill {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.85em;
        margin-right: 10px;
    }
    .score-high { background: #ecfdf5; color: #059669; }
    .score-mid { background: #fffbeb; color: #d97706; }
    .score-low { background: #fef2f2; color: #dc2626; }
    
    /* Bong bóng chat AI */
    .ai-voice-bubble {
        background: #4f46e5;
        color: white;
        padding: 20px;
        border-radius: 20px 20px 20px 5px;
        max-width: 80%;
        margin: 20px 0;
        font-size: 1.1em;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. XỬ LÝ TÀI NGUYÊN & DỮ LIỆU ---
@st.cache_resource
def load_system():
    try:
        data = pd.read_csv('10000_esl_dataset.csv')
        model = joblib.load('esl_model.pkl')
        return data, model
    except: return None, None

df, nlp_model = load_system()

def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# --- 3. QUẢN LÝ TRẠNG THÁI HÀNH VI ---
if "current_task" not in st.session_state:
    if df is not None:
        random_row = df.sample(1).iloc[0]
        st.session_state.current_task = {
            "target": str(random_row.iloc[1]), # Lấy câu mẫu từ data
            "bot_msg": "Listen and repeat this sentence: " + str(random_row.iloc[1])
        }
    else:
        st.session_state.current_task = {"target": "Hello world", "bot_msg": "Say hello to start!"}

# --- 4. GIAO DIỆN CHÍNH (SPEAKING FOCUS) ---
st.title("🗣️ Speaking Focus AI Tutor")
st.write("Hệ thống tập trung vào luyện phát âm và phản xạ nói.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 🤖 AI Instructor")
    st.markdown(f'<div class="ai-voice-bubble">{st.session_state.current_task["bot_msg"]}</div>', unsafe_allow_html=True)
    st.markdown(speak(st.session_state.current_task["bot_msg"]), unsafe_allow_html=True)
    
    # Input điều khiển
    st.write("---")
    audio_input = st.audio_input("Bấm để nói và nhận phản hồi")

with col_right:
    st.markdown("### 📊 Practice Feedback")
    
    if audio_input:
        with st.spinner("Đang phân tích giọng nói..."):
            r = sr.Recognizer()
            try:
                with sr.AudioFile(audio_input) as source:
                    audio_data = r.record(source)
                    user_text = r.recognize_google(audio_data, language="en-US")
                    
                    # Logic so sánh
                    target = st.session_state.current_task["target"]
                    score = fuzz.ratio(user_text.lower(), target.lower())
                    
                    # Hiển thị Dashboard Feedback
                    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                    
                    # Trạng thái điểm số
                    if score >= 85:
                        st.markdown('<span class="stat-pill score-high">EXCELLENT</span>', unsafe_allow_html=True)
                        feedback_txt = "Phát âm rất chính xác, trọng âm và nhịp điệu tự nhiên."
                    elif score >= 60:
                        st.markdown('<span class="stat-pill score-mid">GOOD JOB</span>', unsafe_allow_html=True)
                        feedback_txt = "Bạn đã truyền đạt được ý chính, cần chú ý rõ hơn các âm cuối (ending sounds)."
                    else:
                        st.markdown('<span class="stat-pill score-low">NEEDS WORK</span>', unsafe_allow_html=True)
                        feedback_txt = "Máy chưa nhận diện rõ, hãy thử nói chậm và rõ ràng từng từ một."

                    st.markdown(f"""
                        <div style="margin-top:20px;">
                            <h2 style="color:#4f46e5; margin:0;">{score}%</h2>
                            <p style="color:#64748b; font-size:0.9em; margin-bottom:20px;">Accuracy Score</p>
                            <p><b>Bạn đã nói:</b> <br><span style="color:#1e293b;">"{user_text}"</span></p>
                            <hr style="border:0; border-top:1px solid #f1f1f3; margin:15px 0;">
                            <p><b>Nhận xét:</b> {feedback_txt}</p>
                            <p style="color:#4f46e5; font-size:0.9em;"><b>💡 Gợi ý:</b> Hãy so sánh âm thanh bạn vừa nói với giọng của AI bên trái.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("Câu tiếp theo ➡️"):
                        st.session_state.clear()
                        st.rerun()
                        
            except Exception as e:
                st.error("Không thể nhận diện giọng nói. Hãy thử lại!")
    else:
        st.info("Hệ thống đang chờ giọng nói của bạn để bắt đầu phân tích.")

# --- 5. SIDEBAR PHỤ TRỢ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3241/3241517.png", width=80)
    st.header("Settings")
    st.slider("Target Accuracy", 0, 100, 75)
    st.write("Sử dụng dữ liệu: `10000_esl_dataset.csv`")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
