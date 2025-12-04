# backend/main.py

import os
import torch
import torch.nn as nn
import pandas as pd

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------
app = FastAPI(
    title="Guri Apartment Recommendation API",
    description="구리시 아파트 추천 AI 서버",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------
from kobert_transformers import get_tokenizer, get_kobert_model
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from backend.llm_parser import LLMParser
from backend.rag.rag_service import RAGService

# ---------------------------------------------------------
# Load env
# ---------------------------------------------------------
load_dotenv()

parser = LLMParser()
rag = RAGService()

# ---------------------------------------------------------
# Apartment Data Loading
# ---------------------------------------------------------
APART_PATH = "backend/data/apartment.csv"

if os.path.exists(APART_PATH):
    df_apts = pd.read_csv(APART_PATH)
    print(f"🏢 아파트 {len(df_apts)}개 로딩 완료")
else:
    print("❌ apartment.csv 없음:", APART_PATH)

# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class Query(BaseModel):
    text: str

class RecommendRequest(BaseModel):
    conditions: dict

class SharedRequest(BaseModel):
    apt1: str
    apt2: str
    category: str = "school"
    radius: int = 800

class PredictRequest(BaseModel):
    text: str

# ---------------------------------------------------------
# Labels
# ---------------------------------------------------------
LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]
NUM_LABELS = len(LABELS)

# ---------------------------------------------------------
# KoBERT Loading
# ---------------------------------------------------------
kobert_tokenizer = get_tokenizer()
kobert_model_path = "./backend/models/kobert_facility_classifier.pt"

kobert_bert_model = None
kobert_classifier = None

if os.path.exists(kobert_model_path):
    try:
        print("📦 KoBERT 모델 로딩...")
        checkpoint = torch.load(kobert_model_path, map_location="cpu")

        kobert_bert_model = get_kobert_model()
        kobert_classifier = nn.Linear(768, NUM_LABELS)

        kobert_bert_model.load_state_dict(checkpoint["kobert"])
        kobert_classifier.load_state_dict(checkpoint["classifier"])

        kobert_bert_model.eval()
        kobert_classifier.eval()
        print("✅ KoBERT 모델 로딩 완료")

    except Exception as e:
        print("⚠ KoBERT 로드 실패:", e)

else:
    print("ℹ KoBERT 모델 없음")

def run_kobert(text):
    if kobert_bert_model is None:
        return "KoBERT 모델 없음"

    try:
        inputs = kobert_tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            _, pooled = kobert_bert_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                return_dict=False
            )
            logits = kobert_classifier(pooled)

        pred = torch.argmax(logits, dim=1).item()
        return LABELS[pred]

    except Exception as e:
        return f"KoBERT 오류: {e}"

# ---------------------------------------------------------
# KLUE 모델 로딩
# ---------------------------------------------------------
try:
    print("📘 KLUE 로딩 중…")
    klue_tokenizer = AutoTokenizer.from_pretrained("klue/roberta-small")
    klue_model = AutoModelForSequenceClassification.from_pretrained(
        "klue/roberta-small",
        num_labels=NUM_LABELS
    )
    klue_model.load_state_dict(torch.load("./backend/models/klue_facility_classifier.pt"))
    klue_model.eval()
    print("✅ KLUE 로딩 완료")

except:
    klue_model = None
    print("⚠ KLUE 로드 실패")

def run_klue(text):
    if klue_model is None:
        return "KLUE 모델 없음"

    try:
        inputs = klue_tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            logits = klue_model(**inputs).logits

        pred = torch.argmax(logits, dim=1).item()
        return LABELS[pred]
    except Exception as e:
        return f"KLUE 오류: {e}"

# ---------------------------------------------------------
# ELECTRA 모델 로딩
# ---------------------------------------------------------
try:
    print("🟩 ELECTRA 로딩 중…")
    electra_tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-small-v3-discriminator")
    electra_model = AutoModelForSequenceClassification.from_pretrained(
        "monologg/koelectra-small-v3-discriminator",
        num_labels=NUM_LABELS
    )
    electra_model.load_state_dict(torch.load("./backend/models/electra_facility_classifier.pt"))
    electra_model.eval()
    print("✅ ELECTRA 로딩 완료")

except:
    electra_model = None
    print("⚠ ELECTRA 로드 실패")

def run_electra(text):
    if electra_model is None:
        return "ELECTRA 모델 없음"

    try:
        inputs = electra_tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            logits = electra_model(**inputs).logits

        pred = torch.argmax(logits, dim=1).item()
        return LABELS[pred]
    except Exception as e:
        return f"ELECTRA 오류: {e}"

# ---------------------------------------------------------
# GPT / CLAUDE API
# ---------------------------------------------------------
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
parse_router = APIRouter(prefix="/parse", tags=["Parser"])
predict_router = APIRouter(prefix="/predict", tags=["Prediction"])

app.include_router(parse_router)
app.include_router(predict_router)

@parse_router.post("/")
def parse_text(req: Query):
    return parser.parse(req.text)

@predict_router.post("/models")
def predict_models(req: PredictRequest):
    t = req.text
    return {
        "input": t,
        "KoBERT": run_kobert(t),
        "KLUE": run_klue(t),
        "ELECTRA": run_electra(t)
    }

@app.get("/")
def home():
    return {"message": "Guri AI Recommendation API is running"}

