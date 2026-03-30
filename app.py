# ==========================================
# GPT Mini Studio: Core Application Logic
# ===============================
# This is the main backend application for the GPT Mini Studio.
# It uses FastAPI for the web server, SQLAlchemy for database 
# management (SQLite), and integrates with Hugging Face 
# transformers for local inference.
#
# ARCHITECTURE OVERVIEW:
# 1. Auth: Google, GitHub, and LinkedIn OAuth + Local Email/Pass Login.
# 2. Credits: User-specific token usage and 8-hour refresh system.
# 3. History: CRUD operations for chat sessions and messages.
# 4. Generation: Integration with the local inference engine.
# ==========================================

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import json
from sqlalchemy.orm import Session
import bcrypt
from pydantic import BaseModel
from typing import Optional
import os
import datetime

from core.database import get_db, engine
from core import models
from core.inference import GenerateRequest, generate_text, load_model

# Initialize tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GPT Mini Deployment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables and add Session Middleware
load_dotenv()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-super-secret-key"))

## ! Initial Deployment OAuth Secret Key not passed

# OAuth Setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}
)

oauth.register(
    name='linkedin',
    client_id=os.getenv("LINKEDIN_CLIENT_ID"),
    client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={
        'scope': 'openid email profile',
        'token_endpoint_auth_method': 'client_secret_post',
    }
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- OAuth Routes ---
@app.get("/api/auth/login/{provider}")
async def oauth_login(provider: str, request: Request):
    if not os.getenv(f"{provider.upper()}_CLIENT_ID"):
        return HTMLResponse(f"<h3>{provider.capitalize()} OAuth not configured. Please add Client ID and Secret to .env</h3>")
    
    # Use BASE_URL from .env if available, otherwise reconstruct from request
    base_url = os.getenv("BASE_URL")
    if not base_url:
        scheme = request.url.scheme
        host = request.url.hostname
        port = request.url.port
        base_url = f"{scheme}://{host}"
        if port:
            base_url += f":{port}"
            
    redirect_uri = f"{base_url}/api/auth/callback/{provider}"
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

@app.get("/api/auth/callback/{provider}")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        return HTMLResponse(f"<h3>Authentication failed: {str(e)}</h3>")

    user_info = {}
    if provider == 'google':
        user_info = token.get('userinfo')
    elif provider == 'github':
        resp = await client.get('user', token=token)
        user_info = resp.json()
        if not user_info.get('email'):
            email_resp = await client.get('user/emails', token=token)
            emails = email_resp.json()
            user_info['email'] = next(e['email'] for e in emails if e['primary'])
    elif provider == 'linkedin':
        # OpenID Connect flow for LinkedIn returns userinfo in token
        user_info = token.get('userinfo')

    email = user_info.get('email')
    if not email:
        return HTMLResponse("<h3>Could not retrieve email from provider.</h3>")

    # Sync user with DB
    db_user = db.query(models.User).filter(models.User.email == email).first()
    #Example: SELECT * FROM users WHERE email='user@gmail.com' LIMIT 1;
    if not db_user:
        new_user = models.User(
            first_name=user_info.get('given_name') or user_info.get('name', 'User').split(' ')[0],
            last_name=user_info.get('family_name') or (user_info.get('name', ' ').split(' ')[1] if ' ' in user_info.get('name', '') else ''),
            email=email,
            credits=50,
            is_admin=(email == "gutalomkar01@gmail.com")
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db_user = new_user

    # Prepare user data for frontend
    frontend_user = {
        "user_id": db_user.id, # 1
        "email": db_user.email, # hifi@gmail.com
        "first_name": db_user.first_name, # hif
        "last_name": db_user.last_name, # ii
        "credits": db_user.credits, # 50
        "is_admin": db_user.is_admin # False
    }

    # Inject into localStorage and redirect
    # This is how your UI knows: who is logged in.
    content = f"""
    <script>
        localStorage.setItem('gpt_user', JSON.stringify({json.dumps(frontend_user)}));
        window.location.href = '/';
    </script>
    """
    return HTMLResponse(content)

# --- Feedback & Help ---
class FeedbackRequest(BaseModel):
    user_email: str
    message: str
    include_screenshot: bool

@app.post("/api/feedback")
async def receive_feedback(request: FeedbackRequest):
    # In a real environment, you would use an SMTP library here to send an email.
    # For now, we log the feedback to the console and a local file.
    feedback_log = f"[{datetime.datetime.now()}] FROM: {request.user_email} | MSG: {request.message} | SCREENSHOT: {request.include_screenshot}\n"
    print(f"FEEDBACK RECEIVED: {feedback_log}")
    
    os.makedirs("logs", exist_ok=True)
    with open("logs/feedback.log", "a") as f:
        f.write(feedback_log)
        
    # LOGIC: Sharing feedback to omkargutal10@gmail.com
    # Note: To actually SEND an email, you'd need SMTP credentials (like Gmail App Passwords).
    # Since I cannot configure your private email credentials, I am logging it here.
    return {"message": "Feedback received successfully"}

@app.on_event("startup")
async def startup_event():
    print("Initializing application and loading model...")
    load_model()

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

# --- Schemas ---
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    mobile: Optional[int] = None

class UserLogin(BaseModel):
    email: str
    password: str

class GenerateRequestWithAuth(GenerateRequest):
    user_id: Optional[int] = None
    session_id: Optional[int] = None


'''
## Generation Flow Using This Schema

Frontend sends request
        │
        ▼
GenerateRequestWithAuth
        │
        ├── prompt
        ├── user_id
        └── session_id
        │
        ▼
Backend validates data
        │
        ▼
Call inference engine
        │
        ▼
Save chat history (if logged in)

'''
# Manual Authentication Logic
# --- Auth Endpoints ---
@app.post("/api/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        mobile=user.mobile,
        hashed_password=hashed_password,
        credits=50,
        is_admin=(user.email == "gutalomkar01@gmail.com")
    )
    if new_user.is_admin:
        new_user.credits = 999999
        
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/api/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # Check 8-hour credit refresh (28800 seconds)
    now = datetime.datetime.utcnow()
    if not db_user.is_admin and (now - db_user.last_credit_refresh).total_seconds() > 28800: # 8 hours
        db_user.credits = 50
        db_user.last_credit_refresh = now
        db.commit()
        
    return {
        "user_id": db_user.id,
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "credits": db_user.credits,
        "is_admin": db_user.is_admin
    }

# --- History Endpoints ---
@app.get("/api/users/{user_id}/sessions")
def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    # Check 8-hour credit refresh here too
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user and not db_user.is_admin:
        now = datetime.datetime.utcnow()
        if (now - db_user.last_credit_refresh).total_seconds() > 28800: # 8 hours
            db_user.credits = 50
            db_user.last_credit_refresh = now
            db.commit()

    # Order by pinned first (desc), then by date (desc)
    sessions = db.query(models.ChatSession)\
        .filter(models.ChatSession.user_id == user_id)\
        .order_by(models.ChatSession.is_pinned.desc(), models.ChatSession.created_at.desc())\
        .all()
    return sessions

'''
Sorting Logic: 
| Priority     | Order |
| ------------ | ----- |
| Pinned chats | first |
| Newest chats | next  |
'''

# Rename Chat Session
@app.patch("/api/sessions/{session_id}/rename")
def rename_session(session_id: int, request: dict, db: Session = Depends(get_db)):
    new_title = request.get("title")
    if not new_title:
        raise HTTPException(status_code=400, detail="Title is required")
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = new_title
    db.commit()
    return {"message": "Success"}

# Pin / Unpin Chat
@app.post("/api/sessions/{session_id}/pin")
def toggle_pin(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_pinned = not session.is_pinned
    db.commit()
    return {"is_pinned": session.is_pinned}

# Delete Chat Session
@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Deleted"}

# Get Chat Session Messages 
@app.get("/api/sessions/{session_id}/messages")
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.asc()).all()
    return messages

# Search History (Search with Keyword)
@app.get("/api/users/{user_id}/search")
def search_history(user_id: int, q: str, db: Session = Depends(get_db)):
    # Search in session titles and message contents for this user
    query = f"%{q}%"
    results = db.query(models.ChatSession).join(models.Message).filter(
        models.ChatSession.user_id == user_id,
        (models.ChatSession.title.ilike(query)) | (models.Message.content.ilike(query))
    ).distinct().all()
    return results

# --- Generation API ---
@app.post("/api/generate")
async def generate(request: GenerateRequestWithAuth, db: Session = Depends(get_db)):
    # Verify credits if logged in
    db_user = None
    if request.user_id:
        db_user = db.query(models.User).filter(models.User.id == request.user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        if db_user.credits <= 0 and not db_user.is_admin:
            raise HTTPException(status_code=403, detail="Not enough credits! Credits reset every 8 hours.")
    else:
        # Note: Guests handled primarily via UI local storage, but API is allowed to serve
        pass

    try:
        # Standard fast-load generation
        response_obj = generate_text(request)
        
        # Pydantic v1 / v2 compat: convert safely to dict so we can inject new keys
        response = getattr(response_obj, "model_dump", response_obj.dict)()
        tokens_used = response.get("num_tokens", 0)
        
        # Deduct credits & Save logic
        if db_user:
            if not db_user.is_admin:
                db_user.credits -= 1
            
            sess_id = request.session_id
            if not sess_id:
                # Create a new session with snippet title
                snippet = request.prompt[:20] + "..." if len(request.prompt) > 20 else request.prompt
                new_session = models.ChatSession(user_id=db_user.id, title=snippet)
                db.add(new_session)
                db.commit()
                db.refresh(new_session)
                sess_id = new_session.id
                
            # Log user prompt
            db.add(models.Message(session_id=sess_id, sender="user", content=request.prompt, tokens_used=0))
            # Log model reply
            db.add(models.Message(session_id=sess_id, sender="model", content=response["generated_text"], tokens_used=tokens_used))
            db.commit()
            
            response["session_id"] = sess_id
            response["credits_remaining"] = db_user.credits
            
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ==========================================
# 7. Local Development Server Launcher
# ==========================================
# If this file is run directly (`python app.py`), it starts the uvicorn web server engine.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
