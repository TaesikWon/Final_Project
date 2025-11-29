// frontend/src/api/guriApi.js

import api from "./api";

/* 1) /predict — KoBERT + GPT + Claude 분석 */
export const predictSentence = async (query) => {
  const res = await api.post("/predict", { query });
  return res.data;
};

/* 2) /parse — 자연어 → JSON 조건 변환 */
export const parseConditions = async (text) => {
  const res = await api.post("/parse", { text });
  return res.data;
};

/* 3) /recommend — 조건 기반 아파트 추천 */
export const recommendApts = async (conditions) => {
  const res = await api.post("/recommend", { conditions });
  return res.data;
};

/* 4) /shared — 두 아파트 반경 공유 검색 */
export const sharedRadius = async (apt1, apt2, category, radius) => {
  const res = await api.post("/shared", {
    apt1,
    apt2,
    category,
    radius,
  });
  return res.data;
};

/* 5) /rag/search — RAG 규칙 검색 */
export const ragSearch = async (query) => {
  const res = await api.get(`/rag/search?q=${encodeURIComponent(query)}`);
  return res.data;
};
