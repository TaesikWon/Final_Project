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
from kobert_transformers import get_tokenizer, get_kobert_model

from backend.llm_parser import LLMParser
from backend.recommender import Recommender
from backend.utils.rag_service import RAGService

load_dotenv()

app = FastAPI(
    title="Guri Apartment Recommendation API",
    description="구리시 아파트 추천 AI 서버",
    version="1.0.0"
)

# -------------------------
# 서비스 객체 생성
# -------------------------
parser = LLMParser()
recommender = Recommender()
rag = RAGService()

# -------------------------
# 서버 시작 시 아파트 데이터 로딩
# -------------------------
APART_PATH = "backend/data/guri_apartments_final.csv"

if os.path.exists(APART_PATH):
    df_apts = pd.read_csv(APART_PATH)
    apts = df_apts.to_dict(orient="records")
    recommender.set_apartments(apts)
    print(f"🏢 아파트 {len(apts)}개 로딩 완료")
else:
    print("❌ 아파트 CSV 파일 없음:", APART_PATH)


# -------------------------
# 요청 모델
# -------------------------
class Query(BaseModel):
    text: str

class RecommendRequest(BaseModel):
    conditions: dict

class SharedRequest(BaseModel):
    apt1: str
    apt2: str
    category: str = "school"
    radius: int = 800


# -------------------------
# KoBERT 모델 로드 (수정됨)
# -------------------------
kobert_path = "./backend/models/kobert_facility_classifier.pt"
kobert_tokenizer = get_tokenizer()
kobert_labels = ["school", "subway", "park", "hospital", "safety"]

# 전역 변수
kobert_bert_model = None
kobert_classifier = None

if os.path.exists(kobert_path):
    try:
        print("📦 KoBERT 모델 로딩 중...")
        checkpoint = torch.load(kobert_path, map_location="cpu", weights_only=False)
        
        # 모델 재구성
        kobert_bert_model = get_kobert_model()
        num_labels = len(checkpoint["label_encoder"])
        kobert_classifier = nn.Linear(768, num_labels)
        
        # 가중치 로드
        kobert_bert_model.load_state_dict(checkpoint["kobert"])
        kobert_classifier.load_state_dict(checkpoint["classifier"])
        
        kobert_bert_model.eval()
        kobert_classifier.eval()
        
        # 라벨 업데이트
        kobert_labels = checkpoint["label_encoder"].tolist()
        
        print(f"✅ KoBERT 모델 로드 완료 ({len(kobert_labels)}개 카테고리)")
    except Exception as e:
        print(f"⚠️ KoBERT 로드 실패: {e}")
        kobert_bert_model = None
        kobert_classifier = None
else:
    print("ℹ️ KoBERT 모델 파일 없음 - 기본 기능으로 실행")


def run_kobert(text):
    """KoBERT 추론"""
    if kobert_bert_model is None or kobert_classifier is None:
        return "모델 없음"
    
    try:
        inputs = kobert_tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=64
        )
        
        with torch.no_grad():
            outputs = kobert_bert_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"]
            )[1]  # pooler_output
            logits = kobert_classifier(outputs)
        
        pred = torch.argmax(logits, dim=1).item()
        return kobert_labels[pred]
    except Exception as e:
        return f"추론 오류: {str(e)}"


# -------------------------
# GPT-4.1
# -------------------------
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_gpt4(text):
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4-turbo",  # gpt-4.1은 존재하지 않음, gpt-4-turbo 사용
            messages=[{"role": "user", "content": text}]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"GPT 오류: {str(e)}"


# -------------------------
# Claude
# -------------------------
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_claude(text):
    try:
        resp = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",  # 올바른 모델명
            max_tokens=200,
            messages=[{"role": "user", "content": text}]
        )
        return resp.content[0].text
    except Exception as e:
        return f"Claude 오류: {str(e)}"


# -------------------------
# /predict – 3개 모델 동시 호출
# -------------------------
class PredictRequest(BaseModel):
    query: str

@app.post("/predict")
def predict(req: PredictRequest):
    text = req.query

    return {
        "kobert": run_kobert(text),
        "gpt4_1": run_gpt4(f"이 문장을 분석해줘: {text}"),
        "claude": run_claude(f"한 문장으로 설명해줘: {text}")
    }


# -------------------------
# 기존 라우터
# -------------------------
parse_router = APIRouter(prefix="/parse", tags=["Parser"])
recommend_router = APIRouter(prefix="/recommend", tags=["Recommendation"])
shared_router = APIRouter(prefix="/shared", tags=["Shared"])
rag_router = APIRouter(prefix="/rag", tags=["RAG"])


@parse_router.post("/")
def parse_text(req: Query):
    return {
        "input_text": req.text,
        "parsed_conditions": parser.parse_to_conditions(req.text)
    }


@recommend_router.post("/")
def recommend_api(req: RecommendRequest):
    return {
        "input_conditions": req.conditions,
        "recommendations": recommender.recommend(req.conditions)
    }


@shared_router.post("/")
def shared_api(req: SharedRequest):
    return recommender.shared_radius(
        aptA_name=req.apt1,
        aptB_name=req.apt2,
        category=req.category,
        radius=req.radius
    )


@rag_router.get("/search")
def rag_query(q: str):
    return rag.search(q)


# 라우터 등록
app.include_router(parse_router)
app.include_router(recommend_router)
app.include_router(shared_router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {"message": "Guri AI Recommendation API is running"}