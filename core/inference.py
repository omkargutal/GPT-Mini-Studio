# ==========================================
# GPT Mini Studio: Local Inference Engine
# ==========================================
# This module leverages Hugging Face Transformers to run a local
# conversational model. It specifically uses the 
# Qwen/Qwen2.5-0.5B-Instruct model, optimized for low memory usage.
#
# PIPELINE:
# 1. Hardware Detection (GPU, MPS for Apple, CPU)
# 2. Lazy-Loading: Model is loaded only when first required.
# 3. Chat Templating: Converts raw prompts into conversational formats.
# ==========================================

import os
import torch
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. Pydantic Data Models (API Schemas)
# ==========================================
class GenerateRequest(BaseModel):
    prompt: str = Field(..., max_length=10000)
    max_new_tokens: int = Field(default=1000, ge=1, le=1000)
    temperature: float = Field(default=0.7, ge=0.1, le=2.0)
    top_k: int = Field(default=50, ge=1, le=200)

class GenerateResponse(BaseModel):
    generated_text: str
    num_tokens: int

# ==========================================
# 2. Hardware Acceleration Setup
# ==========================================
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Loading inference on device: {device}")

# ==========================================
# 3. Model & Tokenizer Initialization
# ==========================================
# We use an INSTRUCTION TUNED model. Unlike base GPT-2, this model is trained 
# specifically to have conversations, answer questions, and follow format rules.
model_id = "Qwen/Qwen2.5-0.5B-Instruct"  
tokenizer = None
model = None

# ==========================================
# 4. Model Loading Function
# ==========================================
def load_model():
    """
    Loads the instruction-tuned model.
    """
    global model, tokenizer
    if model is None:
        print(f"Loading '{model_id}' conversational model weights...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            ).to(device)
            model.eval()
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

# ==========================================
# 5. Core Generation (Chat Format)
# ==========================================
def generate_text(request: GenerateRequest) -> GenerateResponse:
    if model is None:
        load_model()
        
    print(f"Generating for prompt: '{request.prompt[:50]}...'")
    
    # We format the prompt as a conversation so the model knows we are chatting
    # The 'system' prompt forces it to give short, direct answers.
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Provide clear, accurate, and detailed responses based on the user's request. Be polite and professional."},
        {"role": "user", "content": request.prompt}
    ]
    
    # Apply the chat format correctly for this specific model
    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # Convert string prompt into token tensors
    inputs = tokenizer([prompt_text], return_tensors="pt").to(device)
    
    # Generate the response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_k=request.top_k,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
    # Extract only the newly generated tokens (ignore the input prompt)
    generated_ids = outputs[0][inputs.input_ids.shape[1]:]
    decoded_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    return GenerateResponse(
        generated_text=decoded_text.strip(),
        num_tokens=len(generated_ids)
    )
