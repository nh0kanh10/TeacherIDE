"""
AI Learning Coach - Read-Only Dashboard
Hiển thị kiến thức đã lưu, tiến độ học, và profile
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sqlite3
from pathlib import Path

# Paths - Use absolute for reliability
BASE_DIR = Path("c:/Users/ADMIN/Desktop/Học")
SYSTEM_DIR = BASE_DIR / ".ai_coach"
DB_PATH = SYSTEM_DIR / "progress.db"
PROFILE_PATH = SYSTEM_DIR / "user_profile.json"

# Page config
st.set_page_config(
    page_title="AI Learning Coach - Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load profile
@st.cache_data
def load_profile():
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f).get('user_profile', {})
    return {}

profile = load_profile()

# Sidebar
with st.sidebar:
    st.title("📚 AI Learning Coach")
    st.caption("Read-Only Dashboard")
    
    if profile and profile.get('basic_info', {}).get('name'):
        name = profile['basic_info']['name']
        st.success(f"Xin chào {name}! 👋")
    else:
        st.info("Profile chưa được tạo")
    
    st.divider()
    page = st.radio("Navigation", ["📚 Knowledge Vault", "📊 Progress", "👤 Profile"])
    
    st.divider()
    st.caption("💡 **Cách học:**")
    st.caption("Chat với AI Agent trong IDE để học")
    st.caption("Dashboard này CHỈ để xem lại")

# Main content
if page == " 📚 Knowledge Vault":
    st.header("📚 Knowledge Vault - Kiến thức đã lưu")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all knowledge
        cursor.execute("""
            SELECT title, content, topic, extracted_at 
            FROM knowledge_extracts 
            ORDER BY extracted_at DESC
        """)
        
        knowledge = cursor.fetchall()
        conn.close()
        
        if knowledge:
            # Filter by topic
            all_topics = list(set([k[2] for k in knowledge if k[2]]))
            selected_topic = st.selectbox("Lọc theo Topic:", ["Tất cả"] + all_topics)
            
            # Display
            filtered = knowledge if selected_topic == "Tất cả" else [k for k in knowledge if k[2] == selected_topic]
            
            st.info(f"Tìm thấy {len(filtered)} knowledge blocks")
            
            for title, content, topic, extracted_at in filtered:
                with st.expander(f"📌 {title} ({topic})"):
                    st.caption(f"Lưu lúc: {extracted_at}")
                    st.markdown(content)
        else:
            st.warning("Chưa có kiến thức nào được lưu.")
            st.info("💡 Chat với AI Agent để bắt đầu học, kiến thức sẽ tự động được lưu!")
            
    except Exception as e:
        st.error(f"Lỗi kết nối database: {e}")

elif page == "📊 Progress":
    st.header("📊 Tiến độ học tập")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Overall stats
        query = """
            SELECT 
                COUNT(DISTINCT t.id) as total_topics,
                COUNT(CASE WHEN p.progress_percent > 0 THEN 1 END) as started,
                COUNT(CASE WHEN p.progress_percent >= 100 THEN 1 END) as completed,
                AVG(CASE WHEN p.progress_percent > 0 THEN p.progress_percent END) as avg_progress
            FROM topics t
            LEFT JOIN progress p ON t.id = p.topic_id
        """
        stats = pd.read_sql_query(query, conn)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Topics tổng", int(stats['total_topics'].iloc[0]) if not stats.empty else 0)
        with col2:
            st.metric("🚀 Đã bắt đầu", int(stats['started'].iloc[0]) if not stats.empty else 0)
        with col3:
            st.metric("✅ Hoàn thành", int(stats['completed'].iloc[0]) if not stats.empty else 0)
        with col4:
            avg = stats['avg_progress'].iloc[0] if not stats.empty else 0
            st.metric("📈 Tiến độ TB", f"{avg:.1f}%" if avg else "0%")
        
        st.divider()
        
        # Progress by topic
        query2 = """
            SELECT 
                t.name as topic_name,
                t.category,
                COALESCE(p.progress_percent, 0) as progress,
                p.last_studied
            FROM topics t
            LEFT JOIN progress p ON t.id = p.topic_id
            ORDER BY p.last_studied DESC NULLS LAST
            LIMIT 20
        """
        df = pd.read_sql_query(query2, conn)
        conn.close()
        
        if not df.empty:
            st.subheader("Topics gần đây")
            
            # Bar chart
            fig = px.bar(
                df, 
                x='topic_name', 
                y='progress',
                color='category',
                title="Tiến độ theo Topic",
                labels={'progress': 'Tiến độ (%)', 'topic_name': 'Topic'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(
                df[['topic_name', 'category', 'progress', 'last_studied']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Chưa có dữ liệu tiến độ. Hãy bắt đầu học với AI Agent!")
            
    except Exception as e:
        st.error(f"Lỗi: {e}")

elif page == "👤 Profile":
    st.header("👤 Hồ sơ học viên")
    
    if profile:
        # Basic Info
        st.subheader("Thông tin cơ bản")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Tên:** {profile.get('basic_info', {}).get('name', 'Chưa cập nhật')}")
            st.info(f"**Timezone:** {profile.get('basic_info', {}).get('timezone', 'N/A')}")
        with col2:
            created = profile.get('basic_info', {}).get('created_at', 'N/A')
            st.info(f"**Tạo lúc:** {created[:10] if created != 'N/A' else 'N/A'}")
        
        # Learning Style
        st.subheader("Phong cách học")
        ls = profile.get('learning_style', {})
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🎨 **Primary Style:** {ls.get('primary_style', 'N/A')}")
            st.write(f"📖 **Explanation:** {ls.get('explanation_preference', 'N/A')}")
        with col2:
            st.write(f"💬 **Feedback Style:** {ls.get('feedback_style', 'N/A')}")
            st.write(f"⚡ **Difficulty:** {ls.get('difficulty_preference', 'N/A')}")
        
        # Goals
        st.subheader("🎯 Mục tiêu")
        goals = profile.get('goals', {})
        st.success(f"**Primary:** {goals.get('primary_goal', 'N/A')}")
        if goals.get('motivation'):
            st.write(f"**Động lực:** {goals['motivation']}")
        
        # Strengths & Weaknesses
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💪 Điểm mạnh")
            strengths = profile.get('strengths', [])
            if strengths:
                for s in strengths:
                    st.success(f"• {s.get('area', 'N/A')}")
            else:
                st.info("AI sẽ tự động phát hiện khi chat")
        
        with col2:
            st.subheader("⚠️ Cần cải thiện")
            weaknesses = profile.get('weaknesses', [])
            if weaknesses:
                for w in weaknesses:
                    st.warning(f"• {w.get('area', 'N/A')}")
            else:
                st.info("AI sẽ tự động phát hiện khi chat")
        
        # Learning Patterns
        st.subheader("📊 Thói quen học")
        lp = profile.get('learning_patterns', {})
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"⏰ **Thời gian tốt nhất:** {lp.get('most_productive_time', 'N/A')}")
        with col2:
            st.write(f"⏱️ **Avg session:** {lp.get('avg_session_duration', 'N/A')} phút")
    else:
        st.warning("Profile chưa được khởi tạo!")
        st.info("💡 Chat với AI Agent, profile sẽ tự động được tạo và cập nhật")

# Footer
st.divider()
st.caption("🤖 Được xây dựng bởi AI Agent | Dữ liệu tự động sync từ teaching sessions")
