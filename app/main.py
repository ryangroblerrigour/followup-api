from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load local environment variables from .env (development only)
load_dotenv()

# Configure OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Fail fast at startup if key is missing
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Default model – you can override with LLM_MODEL env var
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

class FollowUpRequest(BaseModel):
    original_question: str
    user_answer: str

class FollowUpResponse(BaseModel):
    follow_up_question: str

app = FastAPI(
    title="Follow-Up Question API",
    description="Generates probing follow-up questions based on user answers",
    version="0.2.0",
)

SYSTEM_PROMPT = (
    "You are a market research moderator working on a study about car brands.\n"
    "Your job is to ask ONE short, open-ended follow-up question that digs deeper into "
    "WHY the respondent answered the way they did.\n\n"
    "Rules:\n"
    "- Ask about their reasons for choosing or feeling that way about the car brand.\n"
    "- Focus on things like features, reliability, price, image, past experience, or how it fits their needs.\n"
    "- Only ONE question, 6–25 words, neutral and non-leading.\n"
    "- Do not ask multiple questions in one sentence.\n"
    "- Do not give advice or commentary—just the question."
)

PROMPT_TEMPLATE = (
    "Original survey question:\n\"{orig}\"\n\n"
    "Respondent's answer:\n\"{ans}\"\n\n"
    "Based on this answer, ask ONE follow-up question that digs deeper into the main reasons "
    "behind their choice or opinion about the car brand."
)

@app.get("/health")
async def health():
    return {"ok": True, "model": MODEL}

@app.post("/followup", response_model=FollowUpResponse)
async def generate_followup(req: FollowUpRequest):
    prompt = PROMPT_TEMPLATE.format(orig=req.original_question, ans=req.user_answer)

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_completion_tokens=80,
        )

        question = (resp.choices[0].message.content or "").strip().replace("\n", " ")

        # If it produced more than one question, keep only up to first '?'
        if "?" in question:
            question = question.split("?")[0].strip() + "?"

        if not question.endswith("?"):
            question = question.rstrip(".! ") + "?"

        if len(question.strip()) <= 1:  # just "?" or empty
            question = "What are the main reasons this car brand appeals to you?"

        return FollowUpResponse(follow_up_question=question)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
