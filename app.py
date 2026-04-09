import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. CẤU HÌNH TRANG WEB (Wide Layout để có không gian thiết kế) ---
st.set_page_config(page_title="ESL AI Tutor PRO", page_icon="🤖", layout="wide")

# --- 2. TẢI DỮ LIỆU & MODEL (Giả lập để web chạy được giao diện) ---
# Trong thực tế, bạn sẽ nối file pkl và csv của bạn vào đây.
@st.cache_resource
def load_mock_data():
    # Giả lập dataset
    df_mock = pd.DataFrame({
        'Intent': ['greeting', 'pronunciation'],
        'User_Input': ['Hello', 'How to pronounce beach'],
        'Bot_Response': ['Hi there! Ready to speak?', 'Focus on the long E sound. Say beach.']
    })
    return df_mock

try:
    df = load_mock_data()
    # nlp_model = joblib.load('esl_model.pkl') # Bỏ comment khi nối backend thật
    # whisper_model = whisper.load_model("tiny") # Bỏ comment khi nối backend thật
except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
    st.stop()

# --- 3. CSS TÙY CHỈNH NÂNG CAO (Trái tim của thiết kế UI) ---
st.markdown("""
<style>
    /* Reset nền ứng dụng sang màu sáng xám hiện đại */
    .stApp {
        background-color: #f0f4f8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Ẩn các thành phần mặc định của Streamlit cho giống App thật */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style cho Sidebar (Bên trái) */
    [data-testid="stSidebar"] {
        background-color: #e5eaf0;
        padding-top: 2rem;
    }
    
    /* Style cho các Khối nội dung (Cards) - Bo góc và Đổ bóng */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 20px;
    }
    
    .card-title {
        font-size: 16px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 10px;
    }

    /* Style cho Khung Chat */
    .ai-chat-bubble {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-top: 10px;
        margin-bottom: 25px;
    }
    
    /* Style cho Instant Practice Feedback (Bảng màu Gradient & Neon) */
    .feedback-card {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.3);
        width: 80%;
        margin: 0 auto; /* Căn giữa */
        position: relative;
    }
    
    /* Sóng âm Neon Neon giả lập */
    .neon-wave {
        position: absolute;
        bottom: 10px;
        right: 20px;
        width: 100px;
        height: 30px;
        background: repeating-linear-gradient(90deg, #00f2fe, #00f2fe 2px, transparent 2px, transparent 10px);
        opacity: 0.7;
        filter: drop-shadow(0 0 5px #00f2fe);
    }

    /* Đánh dấu màu từ vựng */
    .word-bad {
        color: #fb923c; /* Màu cam neon nhạt */
        font-weight: bold;
        text-decoration: underline;
    }
    .word-good {
        color: #4ade80; /* Màu xanh neon nhạt */
        font-weight: bold;
    }

    /* Style cho Nút Micro */
    div.stAudioInput button {
        background: linear-gradient(135deg, #60a5fa, #a78bfa) !important;
        border: none !important;
        color: white !important;
        border-radius: 50px !important;
        box-shadow: 0 4px 15px rgba(167, 139, 250, 0.4) !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR LAYOUT (Tiến trình & Khen thưởng) ---
with st.sidebar:
    # 🤖 Robot 3D Thân thiện (Sử dụng Image link public thay vì icon phẳng)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/8649/8649603.png" alt="3D Robot Avatar" style="width: 130px; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);">
            <h3 style="color: #1e293b; margin-top: 10px;">ESL AI Tutor</h3>
            <p style="color: #64748b; font-size: 14px;">Your personal speaking guide</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")

    # 📈 Your Speaking Progress (Biểu đồ & Trình độ)
    st.markdown('<div class="glass-card"><div class="card-title">📉 Your Speaking Progress</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12px; color: gray; margin-bottom: 5px;">Weekly practice time (min)</p>', unsafe_allow_html=True)
    
    # Biểu đồ mô phỏng thời gian học
    chart_data = pd.DataFrame(np.array([2, 5, 4, 10, 15, 8, 12]), columns=['Minutes'])
    st.line_chart(chart_data, height=120)
    
    # Thang đánh giá trình độ
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
            <div style="background-color: #0284c7; color: white; padding: 5px 10px; border-radius: 8px; font-weight: bold;">A2</div>
            <div>
                <div style="font-weight: bold; font-size: 14px; color: #1e293b;">Intermediate A2</div>
                <div style="color: #f59e0b; font-size: 12px;">⭐⭐⭐⭐⭐</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🏅 Gamification (Khen thưởng)
    st.markdown("""
        <div class="glass-card">
            <div class="card-title">🏅 Khen thưởng Học tập</div>
            <p style="font-size: 14px; color: #334155; margin-bottom: 8px;">🔥 <strong>5-Day Streak</strong> (Chuỗi 5 ngày)</p>
            <p style="font-size: 14px; color: #334155; margin-bottom: 8px;">🥈 <strong>Pronunciation Ace</strong> (Bậc thầy phát âm)</p>
            <p style="font-size: 14px; color: #334155;">🥇 <strong>Grammar Master</strong> (Bậc thầy ngữ pháp)</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("🔄 Bắt đầu bài tập mới", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

# --- 5. MAIN AREA LAYOUT (Khu vực chính) ---
st.title("🗣️ Thực hành Luyện nói Tiếng Anh")

# Khởi tạo trạng thái mô phỏng (Để web chạy được giao diện)
if "step" not in st.session_state:
    st.session_state.step = 0

# Câu hỏi của Bot AI (Mô phỏng)
with st.chat_message("assistant", avatar="🤖"):
    st.write("Hello! I am your AI English tutor. Let's practice! **Can you describe your favorite movie?**")

st.write("---")

# Mô phỏng quá trình người dùng thu âm và AI phản hồi
if st.session_state.step == 1:
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write("bạn đã trả lời (Thông qua Whisper):")
        
        # ⚡ Instant Practice Feedback (Bảng màu Gradient & Neon)
        st.markdown(f"""
        <div class="feedback-card">
            <h4 style="color: white; margin-bottom: 15px;">⚡ Instant Practice Feedback</h4>
            
            <p style="color: #e2e8f0; font-size: 14px;"><strong>Câu nói của bạn:</strong></p>
            <p style="font-size: 18px; color: white;">
                My <span class="word-good">favorite</span> movie <span class="word-good">is</span> The Matrix, it <span class="word-good">has</span> very <span class="word-bad">good</span> <span class="word-bad">actress</span>.
            </p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; font-size: 14px; color: #e2e8f0;">
                <div>🎯 <strong>Pronunciation Score:</strong> 85%</div>
                <div>📝 <strong>Grammar check:</strong> <span style="color: #4ade80;">Correct</span></div>
                <div>🗣️ <strong>Fluency:</strong> ⭐⭐⭐⭐</div>
                <div>🔍 <strong>Gợi ý sửa lỗi:</strong> 'actress' -> 'action'</div>
            </div>
            
            <div class="neon-wave"></div>
        </div>
        """, unsafe_allow_html=True)
        
    # Câu phản hồi tiếp theo của AI
    with st.chat_message("assistant", avatar="🤖"):
        st.write("Great! You have good fluency. Just be careful with the word **'action'**, you pronounced it a bit like 'actress'. Let's try saying it again!")

st.write("<br><br>", unsafe_allow_html=True)

# --- 6. KHU VỰC THU ÂM (Sóng âm Neon giả lập) ---
st.markdown("<h3 style='text-align: center; color: #2E86C1;'>🎙️ Nhấn vào Micro để nói</h3>", unsafe_allow_html=True)
st.caption("<p style='text-align:center;'>AI Whisper sẽ phân tích giọng nói của bạn ngay lập tức!</p>", unsafe_allow_html=True)

# Khung chứa Audio Input ở giữa màn hình
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Nút thu âm gốc của Streamlit (bắt buộc phải dùng)
    user_audio = st.audio_input("Thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("🎧 AI đang lắng nghe và phân tích..."):
            time.sleep(2) # Giả lập thời gian AI xử lý
            st.session_state.step = 1
            st.rerun()
