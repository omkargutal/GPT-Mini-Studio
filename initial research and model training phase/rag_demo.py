import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import warnings
import time

warnings.filterwarnings('ignore')

# -----------------------------------------------------------------------------
# 1. SETUP: We use a small embedding model for searching text, and a better LLM for generation
# -----------------------------------------------------------------------------

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# We use SentenceTransformers to convert our knowledge documents into vectors
print("Loading embedding model (for search/retrieval)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# We use a powerful lightweight pre-trained model from the market (Qwen 0.5B Instruct)
# This model is much smarter than base GPT-2 and follows instructions well.
model_id = "Qwen/Qwen2.5-0.5B-Instruct"
print(f"\nLoading LLM ({model_id})...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
llm = AutoModelForCausalLM.from_pretrained(
    model_id, 
    torch_dtype=torch.float16 if device != "cpu" else torch.float32,
).to(device)

# -----------------------------------------------------------------------------
# 2. OUR KNOWLEDGE BASE (RAG Documents)
# -----------------------------------------------------------------------------
# Think of this as your company data, PDFs, or website pages.
documents = [
    "Excela mini GPT is a language model built to demonstrate from-scratch AI architecture.",
    "Omkar's GPT mini deployment runs smoothly with FastAPI and a modern UI.",
    "RAG (Retrieval-Augmented Generation) prevents hallucinations by forcing the LLM to read relevant search results before answering.",
    "The capital of France is Paris, but the capital of Excela is innovation.",
    "To train a RAG model, you don't actually 'train' the LLM. Instead, you convert your data into vectors, search them at runtime, and paste the results into the model's prompt."
]

print("\nEncoding documents into vector space...")
# Encode the documents into embeddings
doc_embeddings = embedding_model.encode(documents, convert_to_tensor=True)

# -----------------------------------------------------------------------------
# 3. RAG RETRIEVAL AND GENERATION FUNCTION
# -----------------------------------------------------------------------------

def ask_rag(question: str):
    print(f"\n=====================================")
    print(f"QUESTION: {question}")
    
    # --- Step A: Retrieval ---
    # Convert the user's question into a vector
    question_embedding = embedding_model.encode(question, convert_to_tensor=True)
    
    # Calculate Cosine Similarity between the question and all documents
    cos_scores = torch.nn.functional.cosine_similarity(question_embedding, doc_embeddings)
    
    # Get the top 2 most relevant documents
    top_results = torch.topk(cos_scores, k=2)
    
    print("\n[Retrieved Context]")
    retrieved_context = ""
    for score, idx in zip(top_results.values, top_results.indices):
        doc = documents[idx]
        print(f" - (Score {score:.2f}): {doc}")
        retrieved_context += f"- {doc}\n"
    
    # --- Step B: Generation ---
    # We construct a prompt that includes BOTH the system instructions and the retrieved context
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Answer the user's question using ONLY the provided context. If the answer is not in the context, say 'I don't know based on the provided context.'"},
        {"role": "user", "content": f"Context:\n{retrieved_context}\n\nQuestion: {question}"}
    ]
    
    # Format the prompt using the model's chat template
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    inputs = tokenizer([prompt], return_tensors="pt").to(device)
    
    print("\n[Generating Answer...]")
    t0 = time.time()
    
    # Generate the response using our pre-trained model
    outputs = llm.generate(
        inputs.input_ids,
        max_new_tokens=100,
        temperature=0.3,
        do_sample=True,
    )
    
    # Extract only the newly generated tokens
    generated_ids = outputs[0][inputs.input_ids.shape[1]:]
    answer = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    t1 = time.time()
    
    print(f"\nANSWER:\n{answer}")
    print(f"[Generation took {t1-t0:.2f}s]")


# -----------------------------------------------------------------------------
# 4. TEST IT OUT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ask_rag("What is Excela mini GPT and what is its capital?")
    ask_rag("How do you train a model with RAG?")
