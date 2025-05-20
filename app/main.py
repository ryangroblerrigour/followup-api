from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import openai

# Load local environment variables from .env (development only)
load_dotenv()

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")

class FollowUpRequest(BaseModel):
    original_question: str
    user_answer: str

class FollowUpResponse(BaseModel):
    follow_up_question: str

app = FastAPI(
    title="Follow-Up Question API",
    description="Generates probing follow-up questions based on user answers",
    version="0.1.0"
)

PROMPT_TEMPLATE = (
    "You are a research assistant. Given:\n"
    "Original question: \"{orig}\"\n"
    "User’s answer: \"{ans}\"\n\n"
    "Generate one clear, polite, open-ended follow-up question that asks why they answered that way."
)

@app.post("/followup", response_model=FollowUpResponse)
async def generate_followup(req: FollowUpRequest):
    prompt = PROMPT_TEMPLATE.format(orig=req.original_question, ans=req.user_answer)
    try:
        resp = openai.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=60
)

        question = resp.choices[0].message.content.strip()
        if not question.endswith("?"):
            question += "?"
        return FollowUpResponse(follow_up_question=question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
