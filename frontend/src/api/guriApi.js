// frontend/src/api/guriApi.js

import api from "./api";

export const pingServer = () => api.get("/ping");

export const parseConditions = async (text) => {
  const res = await api.post("/parse", { text });
  return res.data;
};

export const predictKLUE = async (text) => {
  const res = await api.post("/predict/klue", { text });
  return res.data;
};

// ✅ 수정: question 키로 전송
export const recommendAsk = async (query) => {
  const res = await api.post("/recommend/ask", { 
    question: query 
  });
  return res.data;
};