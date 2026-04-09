import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Premium ESL Tutor", 
    page_icon="✨", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. CSS TÙY CHỈNH (GIAO DIỆN SANG TRỌNG) ---
st.markdown("""
    <style>
        /* Import Font chữ hiện đại, sang trọng */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif !important;
        }

        /* Nền trang web: Hiệu ứng Gradient thanh lịch */
        .stApp {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        }

        /* Tiêu đề chính */
        .premium-title {
            text-align: center;
            background: linear-gradient(to right, #bda376, #dfc28d, #bda376); /* Màu Vàng Gold sang trọng */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 3.5rem;
            margin-bottom: 0px;
            letter-spacing: -1px;
            padding-top: 20px;
        }

        /* Phụ đề */
        .premium-subtitle {
            text-align: center;
            color: #64748b;
            font-size: 1.1rem;
            font-weight: 400;
            margin-bottom: 40px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        /* Khu vực Chat (Glassmorphism) */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
            padding: 15px;
            margin-bottom: 15px;
        }

        /* Khu vực thu âm */
        .record-box {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 24px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            border: 1px solid rgba(226, 232, 240, 0.8);
            text-align: center;
            margin-top: 30px;
        }

        /* Tùy chỉnh Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.98) !important; /* Xanh đen sang trọng */
            color: #f8fafc;
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        
        /* Chỉnh lại viền của Audio Input */
        div[data-testid="stAudioInput"] {
            border-radius: 50px;
            overflow: hidden;
            border: 2px solid #dfc28d;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. THANH SIDEBAR ---
with st.sidebar:
    # Có thể đổi link ảnh này thành Logo của bạn
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083204.png", width=120)
    st.markdown("<h2 style='color: #dfc28d !important;'>ESL ELITE</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### ✨ Về Ứng Dụng")
    st.write("Trợ lý luyện giọng chuẩn bản xứ với công nghệ AI phân tích thời gian thực.")
    
    st.markdown("### 🎯 Mục Tiêu")
    st.write("✔ Luyện phản xạ nhanh \n\n✔ Chuẩn hóa phát âm \n\n✔ Mở rộng từ vựng")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("🔄 Bắt đầu phiên mới", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Welcome to your premium English session. How can I assist your learning today?"}]
        st.rerun()

# --- 4. GIAO DIỆN CHÍNH (HEADER) ---
st.markdown("<h1 class='premium-title'>ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='premium-subtitle'>Exclusive Speaking Partner</div>", unsafe_allow_html=True)

# --- 5. TẢI DỮ LIỆU & MODEL ---
@st.cache_resource
def load_data_and_model():
    df = pd.read_csv('cleaned_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error("⚠️ Không thể tải hệ thống. Vui lòng kiểm tra lại file dữ liệu.")
    st.stop()

def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 6. HIỂN THỊ LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to your premium English session. How can I assist your learning today?"}]

chat_container = st.container(height=400, border=False)
with chat_container:
    for message in st.session_state.messages:
        # Sử dụng icon sang trọng hơn
        avatar_icon = "👑" if message["role"] == "user" else "✨"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

# --- 7. KHU VỰC THU ÂM ---
st.markdown("<div class='record-box'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #334155; margin-bottom: 20px;'>🎙️ Chạm để giao tiếp với AI</h3>", unsafe_allow_html=True)

user_message = None
user_audio = st.audio_input("", label_visibility="collapsed")

if user_audio:
    with st.spinner("✨ Đang phân tích ngữ điệu..."):
        r = sr.Recognizer()
        with sr.AudioFile(user_audio) as source:
            audio_data = r.record(source)
            try:
                recognized_text = r.recognize_google(audio_data, language="en-US")
                user_message = recognized_text
                st.success(f"**Bạn:** {recognized_text}")
            except sr.UnknownValueError:
                st.warning("Xin lỗi, âm thanh chưa rõ ràng. Hãy thử lại trong môi trường yên tĩnh hơn.")
            except sr.RequestError:
                st.error("Lỗi kết nối máy chủ nhận diện giọng nói.")
st.markdown("</div>", unsafe_allow_html=True)

# --- 8. XỬ LÝ LOGIC AI TRẢ LỜI ---
if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    with chat_container:
        with st.chat_message("user", avatar="👑"):
            st.markdown(user_message)

    with chat_container:
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Đang phản hồi..."):
                try:
                    predicted_intent = model.predict([user_message])[0]
                    possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                    bot_reply = random.choice(possible_responses)
                except Exception as e:
                    bot_reply = "I beg your pardon, could you elaborate on that?"
            
            st.markdown(bot_reply)
            
            audio_bytes = text_to_speech(bot_reply)
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
