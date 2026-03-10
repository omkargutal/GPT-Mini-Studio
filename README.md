# 🤖 GPT Mini Studio

**GPT Mini Studio** is a professional-grade, local AI assistant platform. It brings the full ChatGPT-like experience—complete with authentication, persistent chat history, and credit usage limits—directly to your local hardware. No cloud, no subscription, total privacy.

---

## 🚀 Key Features

- **� Local AI Inference:** Powered by `Qwen2.5-0.5B-Instruct` via Hugging Face Transformers.
- **⚡ Hardware Acceleration:** Automatic detection and switching between **Apple MPS**, **NVIDIA CUDA**, and CPU fallback.
- **� Secure Authentication:** Integrated OAuth for **Google, GitHub, and LinkedIn**, plus traditional Email/Password login.
- **💬 Persistent Chat History:** Full CRUD operations for chat sessions, message history, pinning, and searching.
- **💳 SaaS-Style Credit System:** Simulated monetization with a 50-credit limit that refreshes every 8 hours.
- **🎨 Modern UI/UX:** Responsive glassmorphism design with a collapsible sidebar, dark mode support, and interactive menus.
- **🐞 Feedback System:** Integrated bug reporting and feedback logging for continuous improvement.

---

## 🏗️ Architecture

The project is built with a decoupled architecture for scalability and maintainability:

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JS | Modern, responsive UI with glassmorphism aesthetics. |
| **Backend** | FastAPI, Uvicorn | High-performance asynchronous API handling logic and routing. |
| **Database** | SQLite, SQLAlchemy ORM | Persistent storage for users, sessions, and messages. |
| **AI Engine** | Transformers, Torch | Local model management and inference execution. |
| **Auth** | Authlib, Bcrypt | Secure token-based session management and OAuth integration. |

---

## 📂 Project Structure

```text
├── app.py              # Main FastAPI application & API routing
├── inference.py        # Local AI model loading and generation logic
├── models.py           # SQLAlchemy database models
├── database.py         # Database connection & session setup
├── static/             # Frontend assets (HTML, CSS, JS)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── research/           # Initial research and model training labs
```

---

## 🛠️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/omkargutal/GPT-Mini-Studio.git
cd "GPT Mini Studio"
```

### 2. Set Up Environment Variables
Copy the `.env.example` file and fill in your OAuth credentials:
```bash
cp .env.example .env
```

### 3. Install Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the Application
Start the development server:
```bash
python app.py
```

### 5. For Video Explaination Visit
**Youtube [Build With OmkarG](https://youtu.be/c5DzxEoBpco?si=RBtVCedcBQYasTcC)**
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
Distributed under the MIT License. See `LICENSE` for more information.

**Built with ❤️ by [Omkar Gutal](https://github.com/omkargutal)**