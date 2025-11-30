// frontend/src/main.jsx

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// 🔥 네이버 지도 API 로드
function loadNaverMapScript() {
  const clientId = import.meta.env.VITE_NAVER_MAP_CLIENT_ID;

  if (!clientId) {
    console.warn("⚠ VITE_NAVER_MAP_CLIENT_ID가 없습니다. .env를 확인하세요.");
    return;
  }

  const script = document.createElement("script");
  script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=${clientId}`;
  script.async = true;
  script.onload = () => console.log("✅ 네이버 지도 API 로드 완료");
  script.onerror = () => console.error("❌ 네이버 지도 API 로드 실패");

  document.head.appendChild(script);
}

loadNaverMapScript();

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
