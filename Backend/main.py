from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
import random
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import string
from mangum import Mangum   # ✅ Added for Vercel serverless support

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ParagraphInput(BaseModel):
    paragraph: str

# ---------------- YOUR FUNCTIONS (no change) ---------------- #
# extract_key_sentences, generate_summary, extract_key_terms, etc...
# (keep all your functions as-is here)
# ------------------------------------------------------------- #

@app.post("/generate")
async def generate_summary_and_questions(data: ParagraphInput):
    # ... your existing logic unchanged ...
    text = data.paragraph.strip()
    if not text:
        return {"summary": "", "questions": []}
    try:
        summary = generate_summary(text)
        key_terms = extract_key_terms(text)
        questions = []
        questions.extend(generate_mcq(text, key_terms))
        questions.extend(generate_short_answer(text))
        questions.extend(generate_true_false(text))
        questions.extend(generate_vocabulary_questions(text, key_terms))
        return {"summary": summary, "questions": questions}
    except Exception as e:
        print(f"NLTK processing failed: {e}")
        # fallback logic here...
        return {"summary": text, "questions": ["Processing failed."]}

@app.get("/")
async def root():
    return {"message": "ParaMaster AI Backend - Local Processing"}

# ✅ Handler for Vercel
handler = Mangum(app)

# ✅ Local development (only runs when you do python main.py)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
