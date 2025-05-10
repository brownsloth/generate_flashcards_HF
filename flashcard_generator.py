# app/flashcard_generator.py

import nltk
nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize
from transformers import pipeline
from email_utils import send_query_email

# Load pipelines once
#model = "mrm8488/t5-base-finetuned-question-generation-ap"
model = "iarfmoose/t5-base-question-generator"
qa_pipeline = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=model,
    device=-1
)

rewrite_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    tokenizer="google/flan-t5-small",
    device=-1
)

def chunk_text(text, max_len=400):
    print('started tokenizing')
    sentences = sent_tokenize(text)
    print('tokenized all text!')
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) <= max_len:
            current += " " + s
        else:
            chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())
    return chunks

def generate_flashcards(text, max_len=400):
    print('generate_flashcards started processing...')

    chunks = chunk_text(text, max_len=max_len)
    flashcards = []
    for chunk in chunks:
        try:
            q = qa_pipeline(f"generate question: {chunk}", max_length=64, do_sample=False)[0]["generated_text"]
            answer = chunk.strip()
            rewritten = rewrite_pipeline(f"Rewrite this into a meaningful, clear question a student might be asked at the end of a lesson:\n{q} so we can expect this as the answer: {answer}", max_length=64, do_sample=False)[0]["generated_text"]
            flashcards.append({
                "question": rewritten.strip(),
                "original_question": q.strip(),
                "answer": answer
            })
        except Exception as e:
            print(f"[!] Failed on chunk: {e}")
            flashcards.append({
                "question": "What information is in this text?",
                "original_question": "N/A",
                "answer": chunk.strip()
            })

    print('generate_flashcards finished processing...')
    print('will try to send mail...')
    send_query_email(text[:200], ",".join([f['question'] for f in flashcards]))
    print('sent mail...')
    return flashcards
