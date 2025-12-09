# 🏢 구리시 아파트 추천 AI 챗봇
# Guri Apartment Recommendation AI Chatbot

구리시 내 학교·병원·카페 등 특정 시설을 기준으로 반경 내 아파트를 추천하고, 사용자의 후속 질문까지 이해하는 대화형 AI 챗봇 프로젝트입니다.

RAG + SQLite + Vector DB + GPT 모델을 결합해 정확하고 자연스러운 부동산 상담 경험을 제공합니다.

## 📌 주요 기능

### ✅ 1. 시설 기반 아파트 추천
- "구리고 반경 500m 아파트 추천해줘"
- "수택초 근처 아파트 찾아줘"
- SQLite 기반 실거리(Haversine) 계산으로 정확한 반경 필터링

### ✅ 2. 두 시설 사이 아파트 추천 (Between Mode)
- "인창고와 구리고 사이 아파트 추천해줘"
- 두 지점의 중간 지점 + 최적 반경 계산

### ✅ 3. 후속 질문 이해 (Context Memory)
- "그중 가장 가까운 곳은?"
- "몇 개나 있어?"
- "가장 멀리 있는 곳은?"
- 최근 검색 결과 기반 자연스러운 후속 질문 처리

### ✅ 4. GPT 기반 자연스러운 요약 응답
- 시설 주소 포함
- 2~3 문장 자연스러운 상담사 스타일
- 대화 히스토리를 반영한 문맥 응답

### ✅ 5. RAG (Retrieval Augmented Generation)
- SQLite + Chroma VectorDB 하이브리드 검색
- 키워드 검색 + 의미 기반 검색 결합

### ✅ 6. React 기반 챗봇 UI
- 상단 입력창 고정
- 하단 스크롤 대화창
- 말풍선 UI + 자동 스크롤
- 반응형 UI

## 🗂 프로젝트 구조
```
Final_Project/
│
├── backend/
│   ├── main.py                      # FastAPI 서버, 챗봇 API
│   ├── llm_parser.py                # 시설명/거리 파싱
│   ├── chat_memory.py               # 대화 메모리
│   ├── rag/
│   │   ├── rag_service.py           # RAG + 벡터/DB 검색 로직
│   │   ├── vector_db/               # Chroma 벡터 DB
│   └── data/
│       └── apartments_facilities.db # SQLite DB
│
├── frontend/
│   ├── src/
│   │   ├── pages/Recommend.jsx      # 챗봇 UI
│   │   ├── api/guriApi.js           # API 연동
│   │   └── components/
│   └── package.json
│
└── requirements.txt                 # Python 의존성
```

## 🚀 실행 방법

### 🔹 1) 백엔드 실행 (FastAPI)
```bash
cd backend
uvicorn main:app --reload
```

**접속:**
- http://localhost:8000
- Swagger 문서: http://localhost:8000/docs

### 🔹 2) 프론트엔드 실행 (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

**접속:**
- http://localhost:5173

## 🧠 기술 스택

### Backend
- Python 3.11
- FastAPI
- SQLite
- ChromaDB
- SentenceTransformers (Ko-sRoBERTa)
- OpenAI GPT (gpt-4o-mini)

### Frontend
- React (Vite)
- TailwindCSS
- React Hooks 기반 대화 UI

### ML / NLP
- Embedding 기반 의미 검색
- Haversine 거리 기반 반경 추천
- RAG 하이브리드 검색 구조

## 🔥 주요 특징 정리

| 기능 | 설명 |
|------|------|
| 시설명 파싱 | 자연어에서 학교/병원/카페 등 추출 |
| 거리 파싱 | "500m", "1km" 등 거리 인식 |
| Between 모드 | 지점 2개 사이 아파트 검색 |
| 후속 질문 | "몇 개야?", "가까운 곳은?" |
| GPT 요약 | 전문 상담사 스타일의 자연스러운 응답 |
| UI 최적화 | 말풍선, 자동 스크롤, 반응형 |

## 📄 저작권 (Copyright)

본 프로젝트의 코드는 개인 학습 및 포트폴리오 목적으로 작성되었습니다.  
저작권은 개발자 **Taesik Won**에게 있으며, 무단 복제·배포·상업적 이용을 금지합니다.
```
Copyright (c) 2025 Taesik Won  
All rights reserved.
```