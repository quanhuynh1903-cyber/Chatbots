import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="ESL AI Tutor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- THÊM CSS TÙY CHỈNH CHO GIAO DIỆN HIỆN ĐẠI ---
st.markdown("""
    <style>
        /* Tiêu đề chính với hiệu ứng Gradient */
        .main-title {
            text-align: center;
            background: -webkit-linear-gradient(45deg, #00C9FF 0%, #92FE9D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Nunito', 'Segoe UI', sans-serif;
            font-weight: 900;
            font-size: 3.2rem;
            margin-bottom: -10px;
        }
        /* Phụ đề */
        .sub-title {
            text-align: center;
            color: #6c757d;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 30px;
            letter-spacing: 0.5px;
        }
        /* Tinh chỉnh khoảng cách Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. THANH SIDEBAR (Menu bên trái) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=150, use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #2E86C1;'>ESL AI Tutor</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🌟 Về Ứng Dụng")
    st.info("Trợ lý ảo giúp bạn tự tin giao tiếp Tiếng Anh mỗi ngày. Chọn gõ phím hoặc thu âm để bắt đầu luyện tập ngay!")
    
    st.markdown("### 💡 Mẹo Học Tập")
    st.success("""
    - **Nghe kỹ:** Lắng nghe phát âm của AI.
    - **Lặp lại:** Cố gắng bắt chước ngữ điệu.
    - **Đừng sợ sai:** AI luôn ở đây để giúp bạn!
    """)
    
    st.divider()
    
    # Nút làm mới giao diện 
    if st.button("🔄 Bắt đầu cuộc hội thoại mới", use_container_width=True, type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello there! I'm your AI English tutor. How would you like to practice today?"}]
        st.toast('Đã làm mới cuộc trò chuyện!', icon='✨')
        st.rerun()

# --- 3. GIAO DIỆN CHÍNH (Header) ---
st.markdown("<h1 class='main-title'>ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Trợ lý Luyện Nghe & Nói Tiếng Anh Thông Minh 🇬🇧</div>", unsafe_allow_html=True)

# --- 4. TẢI DỮ LIỆU & MODEL (Giữ nguyên logic của bạn) ---
@st.cache_resource
def load_data_and_model():
    # Sử dụng try-except tại đây hoặc mock data nếu đang test giao diện
    df = pd.read_csv('10000_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error("⚠️ Lỗi tải dữ liệu. Vui lòng kiểm tra lại file .pkl và .csv!")
    st.stop()

# Hàm tạo giọng nói AI
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 5. HIỂN THỊ LỊCH SỬ KHUNG CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello there! I'm your AI English tutor. How would you like to practice today?"}]

# Vùng chứa khung chat với border bo góc đẹp mắt
chat_container = st.container(height=400, border=True)
with chat_container:
    for message in st.session_state.messages:
        # Thay đổi icon avatar 
        avatar_icon = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

st.write("") # Tạo khoảng trắng đệm

# --- 6. KHU VỰC NHẬP LIỆU (CHIA TABS GỌN GÀNG) ---
tab1, tab2 = st.tabs(["⌨️ Luyện Viết", "🎙️ Luyện Nói"])

user_message = None

# TAB 1: GIAO DIỆN GÕ VĂN BẢN
with tab1:
    with st.form("text_form", clear_on_submit=True, border=False):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_text = st.text_input(
                "Nhập tin nhắn...", 
                placeholder="Ví dụ: How do I improve my vocabulary?", 
                label_visibility="collapsed"
            )
        with col_btn:
            submit_text = st.form_submit_button("Gửi 🚀", use_container_width=True)
            
        if submit_text and user_text.strip() != "":
            user_message = user_text

# TAB 2: GIAO DIỆN THU ÂM TRỰC TIẾP
with tab2:
    st.caption("✨ Nhấn vào biểu tượng micro bên dưới, nói một câu Tiếng Anh, hệ thống sẽ tự động chuyển thành văn bản và phản hồi.")
    user_audio = st.audio_input("Nhấn để thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("🎧 Đang phân tích giọng nói..."):
            r = sr.Recognizer()
            with sr.AudioFile(user_audio) as source:
                audio_data = r.record(source)
                try:
                    # Nhận diện giọng nói Tiếng Anh
                    recognized_text = r.recognize_google(audio_data, language="en-US")
                    user_message = recognized_text
                    st.success(f"Bạn đã nói: *'{recognized_text}'*")
                except sr.UnknownValueError:
                    st.error("⚠️ Xin lỗi, hệ thống nghe không rõ. Bạn hãy nói to và rõ chữ hơn nhé!")
                except sr.RequestError:
                    st.error("⚠️ Lỗi kết nối máy chủ giọng nói.")

# --- 7. XỬ LÝ LÝ LOGIC AI TRẢ LỜI ---
if user_message:
    # 7.1 Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Hiển thị tạm thời tin nhắn người dùng
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_message)

    # 7.2 AI Xử lý và Phản hồi
    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 Đang suy nghĩ..."):
                try:
                    # Phân tích ý định và tìm câu trả lời
                    predicted_intent = model.predict([user_message])[0]
                    possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                    bot_reply = random.choice(possible_responses)
                except Exception as e:
                    bot_reply = "I'm sorry, I couldn't understand that perfectly. Could you try rephrasing?"
            
            # In câu trả lời ra màn hình
            st.markdown(bot_reply)
            
            # Đọc câu trả lời bằng giọng nói
            audio_bytes = text_to_speech(bot_reply)
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    # Lưu câu trả lời vào bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
