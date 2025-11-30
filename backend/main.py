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

# =========================================
# FastAPI 생성
# =========================================
app = FastAPI(
    title="Guri Apartment Recommendation API",
    description="구리시 아파트 추천 AI 서버",
    version="1.0.0"
)

# =========================================
# CORS 설정 (⚠ 반드시 app 생성 이후에 위치해야 정상 동작)
# =========================================
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# KoBERT
# =========================================
from kobert_transformers import get_tokenizer, get_kobert_model

# HuggingFace
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Custom
from backend.llm_parser import LLMParser
from backend.recommender import Recommender
from backend.rag.rag_service import RAGService
from backend.llm_explainer import explain_recommendation

# =========================================
# 환경 변수
# =========================================
load_dotenv()

# =========================================
# 서비스 객체
# =========================================
parser = LLMParser()
recommender = Recommender()
rag = RAGService()

# =========================================
# 아파트 데이터
# =========================================
APART_PATH = "backend/data/apartment_guri.csv"

if os.path.exists(APART_PATH):
    df_apts = pd.read_csv(APART_PATH)
    recommender.set_apartments(df_apts.to_dict(orient="records"))
    print(f"🏢 아파트 {len(df_apts)}개 로딩 완료")
else:
    print("❌ 아파트 CSV 파일 없음:", APART_PATH)

# =========================================
# Request Models
# =========================================
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

# =========================================
# 공통 라벨
# =========================================
LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]
NUM_LABELS = len(LABELS)

# =========================================
# KoBERT 로드
# =========================================
kobert_path = "./backend/models/kobert_facility_classifier.pt"

kobert_tokenizer = get_tokenizer()
kobert_bert_model = None
kobert_classifier = None

if os.path.exists(kobert_path):
    try:
        print("📦 KoBERT 모델 로딩 중...")
        checkpoint = torch.load(kobert_path, map_location="cpu")

        kobert_bert_model = get_kobert_model()
        kobert_classifier = nn.Linear(768, NUM_LABELS)

        kobert_bert_model.load_state_dict(checkpoint["kobert"])
        kobert_classifier.load_state_dict(checkpoint["classifier"])

        kobert_bert_model.eval()
        kobert_classifier.eval()

        print("✅ KoBERT 로딩 완료")
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


# =========================================
# KLUE
# =========================================
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


# =========================================
# ELECTRA
# =========================================
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


# =========================================
# GPT / Claude
# =========================================
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# =========================================
# Router 등록
# =========================================
parse_router = APIRouter(prefix="/parse", tags=["Parser"])
recommend_router = APIRouter(prefix="/recommend", tags=["Recommendation"])
shared_router = APIRouter(prefix="/shared", tags=["Shared"])
rag_router = APIRouter(prefix="/rag", tags=["RAG"])


@parse_router.post("/")
def parse_text(req: Query):
    return parser.parse_to_conditions(req.text)


@recommend_router.post("/")
def recommend(req: RecommendRequest):
    return recommender.recommend(req.conditions)


@rag_router.get("/search")
def rag_search(q: str):
    return rag.search(q)


@shared_router.post("/")
def shared_info(req: SharedRequest):
    return recommender.compare_shared(req.apt1, req.apt2, req.category, req.radius)


# 👍 모델 비교
@app.post("/predict_models")
def predict_models(req: PredictRequest):
    t = req.text
    return {
        "input": t,
        "KoBERT": run_kobert(t),
        "KLUE": run_klue(t),
        "ELECTRA": run_electra(t)
    }


# 라우터 등록
app.include_router(parse_router)
app.include_router(recommend_router)
app.include_router(shared_router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {"message": "Guri AI Recommendation API is running"}
