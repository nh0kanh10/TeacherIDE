# AI LEARNING COACH - Tài Liệu Hệ Thống Hoàn Chỉnh

## 📖 TỔNG QUAN

### Mục đích
Hệ thống học lập trình ASP.NET Core trong 12 tháng với sự hỗ trợ của AI Coach trực tiếp.

### Kiến trúc tổng thể
```
┌─────────────────────────────────────────┐
│         USER (Học viên)                 │
└───────────────┬─────────────────────────┘
                │
                │ Chat trực tiếp
                ▼
┌─────────────────────────────────────────┐
│    AI AGENT (Antigravity/Claude)        │
│    - Giáo viên chính                    │
│    - Giải thích concepts                │
│    - Review code                        │
│    - Đặt câu hỏi Socratic               │
└───────────┬─────────────────────────────┘
            │
            │ Gọi sau mỗi session
            ▼
┌─────────────────────────────────────────┐
│    teaching_helper.py                   │
│    - Lưu kiến thức → Obsidian           │
│    - Update profile → JSON              │
│    - Track progress → SQLite            │
│    - Log interactions → SQLite          │
└───────────┬─────────────────────────────┘
            │
            │ Ghi dữ liệu
            ▼
┌─────────────────────────────────────────┐
│         DATA STORAGE                    │
│  ┌─────────────────────────────────┐   │
│  │ SQLite Database (progress.db)   │   │
│  │  - topics                       │   │
│  │  - progress                     │   │
│  │  - knowledge_extracts           │   │
│  │  - interaction_log              │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ Obsidian Vault                  │   │
│  │  - 05_Extracted_Knowledge/*.md  │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ user_profile.json               │   │
│  │  - basic_info, goals            │   │
│  │  - learning_style               │   │
│  │  - strengths, weaknesses        │   │
│  └─────────────────────────────────┘   │
└───────────┬─────────────────────────────┘
            │
            │ Đọc & Hiển thị
            ▼
┌─────────────────────────────────────────┐
│    Dashboard UI (app.py - Streamlit)    │
│    - Xem kiến thức đã lưu               │
│    - Xem tiến độ học                    │
│    - Xem profile                        │
│    - READ-ONLY (không chat)             │
└─────────────────────────────────────────┘
```

---

## 📂 CẤU TRÚC THỨ MỤC

```
c:/Users/ADMIN/Desktop/Học/
├── .ai_coach/                    # Dữ liệu hệ thống (Hidden)
│   ├── progress.db              # SQLite database
│   ├── user_profile.json        # Hồ sơ học viên
│   ├── config.json              # Cấu hình
│   ├── chroma_db/               # Vector DB (optional)
│   └── .env                     # API keys (legacy)
│
├── .agent/                      # Hướng dẫn cho AI Agent
│   ├── AI_COACH_RULES.md       # ⭐ QUY TẮC BẮT BUỘC
│   └── workflows/
│       ├── resume_learning.md  # Resume project
│       └── teaching_mode.md    # Teaching instructions
│
├── 00_Meta/                     # Tài liệu dự án
│   ├── PROJECT_STATUS.md       # Trạng thái dự án
│   ├── ROADMAP_12_THANG.md     # Lộ trình học
│   ├── task.md                 # Task checklist
│   └── Templates/              # Templates cho notes
│
├── 01-04_*/                     # Nội dung học theo giai đoạn
│   └── (Các thư mục con theo topic)
│
├── 05_Extracted_Knowledge/      # Kiến thức tự động lưu
│   └── *.md                    # Markdown files
│
├── Scripts/                     # Python scripts
│   ├── teaching_helper.py      # ⭐ Backend helper
│   ├── app.py                  # Dashboard UI
│   ├── ai_coach.py             # Legacy standalone
│   ├── extract_knowledge.py    # Utility
│   ├── setup.py                # Initial setup
│   ├── requirements.txt        # Dependencies
│   └── .streamlit/
│       └── config.toml         # Streamlit config
│
└── START_LEARNING.bat           # Launch dashboard
```

---

## 🔧 CÁC THÀNH PHẦN CHÍNH

### 1. AI Agent (Antigravity/Claude)
**Vai trò:** Giáo viên trực tiếp

**Nhiệm vụ:**
- Dạy ASP.NET Core theo `00_Meta/ROADMAP_12_THANG.md`
- Trả lời câu hỏi, giải thích concepts
- Review code, đưa ra feedback
- Sử dụng Socratic questioning

**Quy trình sau mỗi session:**
```bash
# 1. Lưu kiến thức (nếu có)
python Scripts/teaching_helper.py save_knowledge "Title" "Topic" "content.md"

# 2. Update profile (nếu phát hiện info mới)
python Scripts/teaching_helper.py update_profile "updates.json"

# 3. Log interaction
python Scripts/teaching_helper.py log_chat "User question" "AI answer" "Topic"

# 4. Update progress (nếu hoàn thành topic)
python Scripts/teaching_helper.py update_progress "C# Basics" 50
```

---

### 2. teaching_helper.py
**Mô tả:** Backend script để persist learning data

**Functions:**
- `save_knowledge_block(title, content, topic)` → Lưu vào Obsidian + SQLite
- `update_profile(updates_dict)` → Cập nhật user_profile.json
- `log_interaction(user_msg, ai_msg, topic)` → Ghi log vào DB
- `update_progress(topic_name, percent)` → Cập nhật tiến độ

**CLI Usage:**
```bash
python teaching_helper.py save_knowledge "OOP in C#" "C# Basics" "content.md"
python teaching_helper.py update_profile "updates.json"
python teaching_helper.py log_chat "What is LINQ?" "LINQ là..." "C# Advanced"
python teaching_helper.py update_progress "ASP.NET MVC" 75
```

---

### 3. Dashboard UI (app.py)
**Mô tả:** Streamlit read-only dashboard

**Pages:**
1. **📚 Knowledge Vault:** Xem kiến thức đã lưu (từ SQLite)
2. **📊 Progress:** Charts tiến độ học (từ SQLite)
3. **👤 Profile:** Xem hồ sơ học viên (từ JSON)

**⚠️ Không có Chat!** User chat trực tiếp với AI Agent trong IDE.

**Launch:**
```bash
# Windows
START_LEARNING.bat

# Hoặc trực tiếp
streamlit run Scripts/app.py
```

---

### 4. SQLite Database Schema
**File:** `.ai_coach/progress.db`

**Tables:**
```sql
-- Topics học
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    roadmap_month INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tiến độ học
CREATE TABLE progress (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER,
    status TEXT DEFAULT 'not_started',
    progress_percent INTEGER DEFAULT 0,
    last_studied TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Kiến thức đã extract
CREATE TABLE knowledge_extracts (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER,
    title TEXT,
    content TEXT,
    topic TEXT,
    obsidian_path TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Log tương tác
CREATE TABLE interaction_log (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_message TEXT,
    ai_response TEXT,
    topic TEXT,
    session_id TEXT
);

-- Goals (Multi-goal support)
CREATE TABLE goals (
    id TEXT PRIMARY KEY,
    type TEXT,
    name TEXT,
    duration_months INTEGER,
    status TEXT DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
```

---

### 5. User Profile Structure
**File:** `.ai_coach/user_profile.json`

```json
{
  "user_profile": {
    "basic_info": {
      "name": "",
      "timezone": "Asia/Ho_Chi_Minh",
      "created_at": "2025-12-25T...",
      "last_active": "2025-12-25T..."
    },
    "learning_style": {
      "primary_style": "visual/active/reading/project-based",
      "explanation_preference": "detailed",
      "difficulty_preference": "steady",
      "feedback_style": "balanced/encouraging/direct"
    },
    "personality_traits": {
      "motivation_level": "high/medium/low",
      "persistence": "high/medium/low",
      "learning_pace": "fast/moderate/slow",
      "attention_to_detail": "high/medium/low"
    },
    "goals": {
      "primary_goal": "ASP.NET Core Backend Developer in 12 months",
      "short_term": [],
      "long_term": [],
      "motivation": ""
    },
    "strengths": [
      {"area": "...", "evidence": "..."}
    ],
    "weaknesses": [
      {"area": "...", "evidence": "..."}
    ],
    "learning_patterns": {
      "most_productive_time": "morning/afternoon/evening/night",
      "avg_session_duration": 60,
      "preferred_break_frequency": "flexible"
    }
  }
}
```

---

## 🚀 QUY TRÌNH HỌC CHUẨN

### Bước 1: Setup (Chỉ làm 1 lần)
```bash
cd Scripts
python setup.py  # Tạo database, folders, config
```

### Bước 2: Học với AI Agent
**User:** Chat trong IDE với AI Agent (Antigravity/Claude)
- Hỏi questions
- Nhận giải thích
- Review code
- Làm bài tập

**AI Agent:** Sau session, tự động gọi `teaching_helper.py` để lưu data

### Bước 3: Xem lại kiến thức
```bash
START_LEARNING.bat  # Mở dashboard
```
→ Browse knowledge vault, check progress

---

## 📋 WORKFLOW CHO AI AGENT

### Đọc trước khi dạy:
1. `.agent/AI_COACH_RULES.md` - Quy tắc bắt buộc
2. `00_Meta/ROADMAP_12_THANG.md` - Lộ trình
3. `.ai_coach/user_profile.json` - Profile học viên

### Trong khi dạy:
- 100% Tiếng Việt
- Socratic questioning
- Code examples
- Liên kết với roadmap

### Sau khi dạy:
- Lưu knowledge blocks
- Update profile
- Log interaction
- Track progress

---

## 🔒 BẢO MẬT & DEPENDENCIES

### Environment Variables
File: `.ai_coach/.env` (Legacy, không cần nếu dùng IDE AI)
```
GEMINI_API_KEY=...  # Chỉ cần nếu dùng standalone app
```

### Python Dependencies
```
streamlit>=1.32.0
plotly>=5.19.0
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r Scripts/requirements.txt
```

---

## 🎯 ROADMAP 12 THÁNG (Tóm tắt)

**Tháng 1-2:** C# Fundamentals (Basics, OOP, Collections)  
**Tháng 3-4:** ASP.NET Core Basics (MVC, Web API)  
**Tháng 5-6:** Entity Framework, Database  
**Tháng 7-8:** Authentication, Middleware, Architecture  
**Tháng 9-10:** Advanced Topics (Caching, Performance)  
**Tháng 11-12:** Real Projects, Portfolio

Chi tiết: `00_Meta/ROADMAP_12_THANG.md`

---

## 🐛 TROUBLESHOOTING

### Dashboard không khởi động?
```bash
# Check Streamlit
streamlit --version

# Run trực tiếp
cd Scripts
streamlit run app.py
```

### Database lỗi?
```bash
# Recreate
cd Scripts
python setup.py
```

### Profile trống?
→ AI Agent sẽ tự động điền khi chat

---

## 📞 LIÊN HỆ & HỖ TRỢ

**Khi cần resume project:**
```
Đọc: .agent/workflows/resume_learning.md
```

**Khi AI Agent mới tiếp quản:**
```
Đọc: .agent/AI_COACH_RULES.md
```

**Khi muốn dùng standalone app:**
```
python Scripts/ai_coach.py
# (Cần Gemini API key trong .env)
```

---

## 🎓 KẾT LUẬN

Hệ thống này tối ưu hóa việc học bằng cách:
✅ Dùng AI Agent trong IDE làm giáo viên (không tốn API ngoài)  
✅ Tự động lưu mọi kiến thức quan trọng  
✅ Track tiến độ chi tiết  
✅ Cá nhân hóa learning experience  
✅ UI đơn giản để review lại  

**Chúc bạn học tốt! 🚀**
