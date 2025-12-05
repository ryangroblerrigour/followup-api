from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load local environment variables from .env (development only)
load_dotenv()

# Configure OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Fail fast at startup if key is missing – easier to debug than runtime errors
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
