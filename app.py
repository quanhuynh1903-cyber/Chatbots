import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# --- 1. CẤU HÌNH TRANG WEB (Wide Layout) ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# --- 2. CSS TÙY CHỈNH (Thiết kế UI/UX) ---
st.markdown("""
<style>
    /* Nền ứng dụng */
    .stApp {
        background-color: #f4f7f6;
    }
    /* Thẻ Feedback Tức thì */
    .feedback-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        margin-top: 15px;
        border-left: 5px solid #4facfe;
    }
    /* Đánh dấu màu từ vựng */
    .word-good {
        background-color: #d4edda;
        color: #155724;
        padding: 2px 6px;
        border-radius: 5px;
        font-weight: bold;
    }
    .word-bad {
        background-color: #ffeeba;
        color: #856404;
        padding: 2px 6px;
        border-radius: 5px;
        font-weight: bold;
    }
    /* Chữ Neon */
    .neon-text {
        background: -webkit-linear-gradient(#00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        text-align: center;
    }
    /* Thẻ Gamification Sidebar */
    .sidebar-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. THANH SIDEBAR (Tiến trình & Khen thưởng) ---
with st.sidebar:
    # Avatar Robot (Sử dụng Emoji hoặc Icon lớn)
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #2E86C1;'>ESL AI Tutor</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Trợ lý luyện nói AI siêu nhạy</p>", unsafe_allow_html=True)
    st.write("---")

    # Thẻ Lộ trình học tập (Progress)
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.subheader("📈 Your Speaking Progress")
    st.write("Thời gian luyện tập tuần này (phút)")
    
    # Biểu đồ mô phỏng thời gian học
    chart_data = pd.DataFrame(np.array([10, 15, 12, 20, 25, 30, 40]), columns=['Minutes'])
    st.line_chart(chart_data, height=150)
    
    st.metric(label="Trình độ hiện tại", value="A2 Intermediate", delta="Tăng 1 bậc")
    st.markdown('</div>', unsafe_allow_html=True)

    # Thẻ Thành tích (Gamification)
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.subheader("🏆 Thành tích của bạn")
    st.markdown("🔥 **5-Day Streak** (Chuỗi 5 ngày)")
    st.markdown("🎖️ **Pronunciation Ace** (Phát âm chuẩn)")
    st.markdown("⭐ **Grammar Master** (Bậc thầy ngữ pháp)")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Bắt đầu bài tập mới", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

# --- 4. KHU VỰC CHÍNH (Luyện nói & Phản hồi) ---
st.title("🎙️ Thực hành Giao tiếp Tiếng Anh")

# Tạo một biến trạng thái để mô phỏng kịch bản (Vì chưa có AI nối vào)
if "step" not in st.session_state:
    st.session_state.step = 0

# Câu hỏi của AI
with st.chat_message("assistant", avatar="🤖"):
    st.write("Hello! I am your AI English tutor. **Can you recommend a good restaurant?**")

# Nếu người dùng đã thu âm (chuyển sang bước 1)
if st.session_state.step == 1:
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write("Bạn đã trả lời (Thông qua Whisper):")
        
        # Thẻ Instant Practice Feedback
        st.markdown(f"""
        <div class="feedback-card">
            <h4 style="color: #2E86C1;">⚡ Instant Practice Feedback</h4>
            <hr style="margin: 10px 0;">
            <p><strong>Câu nói của bạn:</strong></p>
            <p style="font-size: 18px;">
                I <span class="word-bad">tink</span> you should <span class="word-good">try</span> the seafood restaurant near the <span class="word-good">beach</span>.
            </p>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <div>
                    <p>🎯 <strong>Pronunciation Score:</strong> 88%</p>
                    <p>📝 <strong>Grammar Check:</strong> <span style="color: green;">Correct</span></p>
                </div>
                <div>
                    <p>🗣️ <strong>Fluency:</strong> ⭐⭐⭐⭐</p>
                    <p>🔍 <strong>Gợi ý sửa lỗi:</strong> 'tink' -> 'think'</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Lời khen của AI sau khi feedback
    with st.chat_message("assistant", avatar="🤖"):
        st.write("Good job! Your fluency is great. Just be careful with the 'th' sound in the word **'think'**. Let's try another question!")

st.write("---")

# --- 5. KHU VỰC THU ÂM (Mô phỏng sóng âm) ---
st.markdown("<h3 class='neon-text'>🎙️ Nhấn vào Micro để nói</h3>", unsafe_allow_html=True)
st.caption("<p style='text-align:center;'>AI Whisper sẽ phân tích giọng nói của bạn ngay lập tức!</p>", unsafe_allow_html=True)

# Khung chứa Audio Input ở giữa màn hình
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    user_audio = st.audio_input("Thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("🎧 Đang phân tích phát âm..."):
            time.sleep(2) # Giả lập thời gian AI xử lý
            st.session_state.step = 1
            st.rerun()
