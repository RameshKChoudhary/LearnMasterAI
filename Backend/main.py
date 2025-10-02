from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins (adjust in production for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input model
class ParagraphInput(BaseModel):
    paragraph: str

@app.post("/generate")
async def generate_summary_and_questions(data: ParagraphInput):
    # Create the prompt using input paragraph
    prompt = f"""
Summarise the following paragraph clearly and generate contextual questions:
- 2 multiple choice questions (with options)
- 2 short answer questions
- 1 true/false question
- 2 vocabulary or grammar-based questions

Paragraph:
\"\"\"
{data.paragraph}
\"\"\"

Output in this format:
Summary:
[summary]

Questions:
1. [question]
2. [question]
...
"""

    # Prepare API call to Mistral
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-small",  # change model as per your quota or requirement
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Raise error if not successful
    response.raise_for_status()

    # Extract content from response
    content = response.json()["choices"][0]["message"]["content"]

    # Parse summary and questions from content
    summary_part = ""
    questions_part = []
    if "Summary:" in content and "Questions:" in content:
        summary_part = content.split("Summary:")[1].split("Questions:")[0].strip()
        questions_raw = content.split("Questions:")[1].strip().split('\n')
        questions_part = [q.strip() for q in questions_raw if q.strip()]

    return {
        "summary": summary_part,
        "questions": questions_part
    }
