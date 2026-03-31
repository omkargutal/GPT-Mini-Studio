# 🤖 GPT Mini Studio

**GPT Mini Studio** is a professional-grade, local AI assistant platform. It brings the full ChatGPT-like experience—complete with authentication, persistent chat history, and credit usage limits—directly to your local hardware. No cloud, no subscription, total privacy.

---

## 📸 Project Preview

### ** Personalized GPT Mini Studio**

![Input Screen Preview](Output%20Preview/Collage%20%20Preview/Input%20Screen.jpg)
---
![Output Screen Preview](Output%20Preview/Collage%20%20Preview/Output%20Screen.jpg)

---

## 🚀 Key Features

- **📂 Local AI Inference:** Powered by `Qwen2.5-0.5B-Instruct` via Hugging Face Transformers.
- **⚡ Hardware Acceleration:** Automatic detection and switching between **Apple MPS**, **NVIDIA CUDA**, and CPU fallback.
- **🔐 Secure Authentication:** Integrated OAuth for **Google, GitHub, and LinkedIn**, plus traditional Email/Password login.
- **💬 Persistent Chat History:** Full CRUD operations for chat sessions, message history, pinning, and searching.
- **💳 SaaS-Style Credit System:** Simulated monetization with a 50-credit limit that refreshes every 8 hours.
- **🎨 Modern UI/UX:** Responsive glassmorphism design with a collapsible sidebar, dark mode support, and interactive menus.
- **🐞 Feedback System:** Integrated bug reporting and feedback logging for continuous improvement.

---

## 🏗️ Architecture

The project is built with a decoupled architecture for scalability and maintainability:

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JS | Modern, responsive UI with glassmorphism aesthetics. |
| **Backend** | FastAPI, Uvicorn | High-performance asynchronous API handling logic and routing. |
| **Database** | SQLite, SQLAlchemy ORM | Persistent storage for users, sessions, and messages. |
| **AI Engine** | Transformers, Torch | Local model management and inference execution. |
| **Auth** | Authlib, Bcrypt | Secure token-based session management and OAuth integration. |

---

## 📂 Project Structure

```text
GPT Mini Studio/
├── app.py                  # Main FastAPI application & API routing
├── core/                   # Backend core logic
│   ├── database.py         # Database connection & session setup
│   ├── inference.py        # Local AI model loading & generation
│   └── models.py           # SQLAlchemy database models
├── static/                 # Frontend assets
│   ├── index.html          # Main UI entry point
│   ├── css/                # Stylesheets (style.css)
│   └── js/                 # Client-side logic (script.js)
├── data/                   # Local databases (app.db)
├── logs/                   # Application logs (feedback.log)
├── scripts/                # Utility scripts (run.sh)
├── research/               # Initial research, notebooks & training labs
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
└── README.md               # Documentation
```

---

## 🛠️ Getting Started

Follow these steps to set up and run GPT Mini Studio on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/omkargutal/GPT-Mini-Studio.git
cd "GPT Mini Studio"
```

### 2. Set Up Environment Variables
Copy the `.env.example` file and fill in your OAuth credentials (get these from Google, GitHub, and LinkedIn developer consoles):
```bash
cp .env.example .env
```

### 3. Install Dependencies

#### 🍏 Mac / 🐧 Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 🪟 Windows
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Application

#### 🍏 Mac / 🐧 Linux
You can use the provided script:
```bash
bash scripts/run.sh
```
Or run directly:
```bash
python3 app.py
```

#### 🪟 Windows
```powershell
python app.py
```

The application will be available at: **http://localhost:8001**

---

## 📺 Video Explanation
Watch the full breakdown and demo on YouTube:
**[Build With OmkarG - GPT Mini Studio](https://youtu.be/c5DzxEoBpco)**

---

## 🔗 Connect with Me

<div align="center">

[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@buildwithomkarg)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/omkar-gutal-a25935249)
[![X](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/job_update_2k25)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/omkargutal)

</div>

---

## 📄 License
Distributed under the MIT License.

**Built with ❤️ by [Omkar Gutal](https://github.com/omkargutal)**