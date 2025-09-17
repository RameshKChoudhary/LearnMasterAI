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

def extract_key_sentences(text, num_sentences=2):
    """Extract key sentences for summary using simple scoring"""
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return sentences
    
    # Score sentences based on word frequency
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalnum() and word not in stop_words]
    word_freq = Counter(words)
    
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_words = word_tokenize(sentence.lower())
        score = 0
        word_count = 0
        for word in sentence_words:
            if word in word_freq:
                score += word_freq[word]
                word_count += 1
        if word_count > 0:
            sentence_scores[i] = score / word_count
    
    # Get top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_sentences.sort(key=lambda x: x[0])  # Sort by original order
    
    return [sentences[i] for i, _ in top_sentences]

def generate_summary(text):
    """Generate a simple extractive summary"""
    key_sentences = extract_key_sentences(text, 2)
    return " ".join(key_sentences)

def extract_key_terms(text):
    """Extract important terms from the text"""
    words = word_tokenize(text)
    tagged = pos_tag(words)
    
    # Extract nouns, proper nouns, and adjectives
    key_terms = []
    for word, tag in tagged:
        if tag in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ'] and len(word) > 3:
            key_terms.append(word)
    
    return list(set(key_terms))[:10]  # Return unique terms

def generate_mcq(text, key_terms):
    """Generate multiple choice questions"""
    questions = []
    sentences = sent_tokenize(text)
    
    # Generate questions based on key terms
    for i, term in enumerate(key_terms[:2]):
        # Find sentence containing the term
        for sentence in sentences:
            if term.lower() in sentence.lower():
                # Create a simple question
                question = f"What is mentioned about {term} in the text?"
                # Create dummy options
                options = [
                    f"A) {term} is the main focus",
                    f"B) {term} is briefly mentioned",
                    f"C) {term} is explained in detail",
                    f"D) {term} is compared to something else"
                ]
                questions.append(f"{i+1}. {question}\n   " + "\n   ".join(options))
                break
    
    return questions

def generate_short_answer(text):
    """Generate short answer questions"""
    sentences = sent_tokenize(text)
    questions = []
    
    # Generate questions based on sentence patterns
    question_starters = [
        "What is the main point discussed about",
        "How does the text describe",
        "Why is",
        "What role does"
    ]
    
    words = word_tokenize(text)
    tagged = pos_tag(words)
    nouns = [word for word, tag in tagged if tag in ['NN', 'NNS', 'NNP', 'NNPS'] and len(word) > 3]
    
    for i, starter in enumerate(question_starters[:2]):
        if i < len(nouns):
            questions.append(f"{len(questions)+1}. {starter} {nouns[i]}?")
    
    return questions

def generate_true_false(text):
    """Generate true/false questions"""
    sentences = sent_tokenize(text)
    if sentences:
        # Take a key sentence and modify it slightly
        sentence = sentences[0]
        # Simple modification - this is a basic implementation
        question = f"True or False: {sentence}"
        return [question]
    return ["True or False: The text discusses important concepts."]

def generate_vocabulary_questions(text, key_terms):
    """Generate vocabulary and grammar questions"""
    questions = []
    
    # Vocabulary question
    if key_terms:
        term = random.choice(key_terms[:5])
        questions.append(f"Define the term '{term}' as used in the context of this text.")
    
    # Grammar question - find complex sentences
    sentences = sent_tokenize(text)
    for sentence in sentences:
        if len(sentence.split(',')) > 2:  # Sentence with multiple clauses
            questions.append(f"Identify the main clause in this sentence: '{sentence}'")
            break
    
    if len(questions) < 2:
        questions.append("What is the tone of this text? (formal, informal, academic, etc.)")
    
    return questions

@app.post("/generate")
async def generate_summary_and_questions(data: ParagraphInput):
    text = data.paragraph.strip()
    
    if not text:
        return {"summary": "", "questions": []}
    
    try:
        # Generate summary
        summary = generate_summary(text)
        
        # Extract key terms
        key_terms = extract_key_terms(text)
        
        # Generate different types of questions
        questions = []
        
        # Multiple choice questions
        mcq_questions = generate_mcq(text, key_terms)
        questions.extend(mcq_questions)
        
        # Short answer questions
        short_questions = generate_short_answer(text)
        questions.extend(short_questions)
        
        # True/false question
        tf_questions = generate_true_false(text)
        questions.extend(tf_questions)
        
        # Vocabulary questions
        vocab_questions = generate_vocabulary_questions(text, key_terms)
        questions.extend(vocab_questions)
        
        return {
            "summary": summary,
            "questions": questions
        }
    
    except Exception as e:
        # Enhanced fallback that still uses the actual text content
        print(f"NLTK processing failed: {e}")
        
        # Simple text processing fallback
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = re.findall(r'\b[A-Za-z]{4,}\b', text)
        
        # Simple summary
        if len(sentences) >= 2:
            summary = sentences[0] + '. ' + sentences[1] + '.'
        else:
            summary = text
            
        # Simple keyword extraction
        word_freq = {}
        for word in words:
            word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
        
        key_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        key_terms = [word.title() for word, freq in key_words]
        
        # Generate contextual questions using simple methods
        questions = []
        
        # MCQ based on content
        if key_terms:
            q1 = f"1. What role does {key_terms[0]} play in this text?"
            q1 += "\n   A) It is the main subject\n   B) It provides supporting details\n   C) It introduces the topic\n   D) It concludes the discussion"
            questions.append(q1)
            
            if len(key_terms) > 1:
                q2 = f"2. How is {key_terms[1]} presented in the passage?"
                q2 += "\n   A) As a key concept\n   B) As an example\n   C) As a contrast\n   D) As additional information"
                questions.append(q2)
        
        # Short answer questions
        if key_terms:
            questions.append(f"3. Explain the significance of {key_terms[0]} according to this text.")
        questions.append("4. What is the main message or purpose of this passage?")
        
        # True/false from actual content
        if len(sentences) > 1:
            questions.append(f"5. True or False: {sentences[1]}")
        else:
            questions.append(f"5. True or False: {sentences[0]}")
            
        # Vocabulary questions
        if key_terms:
            questions.append(f"6. Define '{key_terms[0]}' as it is used in this context.")
        questions.append("7. What is the overall tone and style of this writing?")
        
        return {
            "summary": summary,
            "questions": questions
        }

@app.get("/")
async def root():
    return {"message": "ParaMaster AI Backend - Local Processing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)