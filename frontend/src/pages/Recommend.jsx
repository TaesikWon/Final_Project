// frontend/src/pages/Recommend.jsx

import { useState, useEffect, useRef } from "react";
import { recommendAsk } from "../api/guriApi";

export default function Recommend() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const askServer = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    try {
      const data = await recommendAsk(query);

      if (!data.ok) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.error }
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.summary }
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "서버 오류가 발생했습니다." }
      ]);
    } finally {
      setQuery("");
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-gray-100">

      {/* -------------------- 상단 고정 영역 -------------------- */}
      <div className="max-w-5xl mx-auto w-full p-6 flex-shrink-0">
        <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
          🏢 구리시 AI 아파트 추천 - 챗봇
        </h1>

        <div className="bg-white border rounded-xl p-6 shadow">
          <input
            className="w-full border rounded px-4 py-3 mb-4"
            placeholder="예: 구리고등학교 반경 500m 내 아파트 추천해줘"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && askServer()}
          />

          <button
            onClick={askServer}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition"
          >
            {loading ? "⏳ 검색 중..." : "보내기"}
          </button>
        </div>
      </div>

      {/* -------------------- 대화 영역 전체 -------------------- */}
      <div className="max-w-5xl mx-auto w-full flex-1 px-6 pb-6 overflow-hidden">
        <div className="bg-white border rounded-xl shadow-sm h-full flex flex-col">

          {/* 제목 */}
          <div className="px-4 py-3 border-b bg-gray-50 rounded-t-xl">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              💬 대화
            </h2>
          </div>

          {/* 메시지 스크롤 영역 */}
          <div
            ref={chatRef}
            className="flex-1 p-6 overflow-y-auto space-y-4"
          >
            {messages.length === 0 && (
              <p className="text-gray-400 text-center py-20">
                아직 대화가 없습니다. 질문을 입력해보세요!
              </p>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`
                  p-4 rounded-xl shadow 
                  w-fit max-w-[75%] whitespace-pre-line break-words
                  ${
                    msg.role === "user"
                      ? "bg-blue-100 ml-auto text-right"
                      : "bg-gray-100 mr-auto text-left"
                  }
                `}
              >
                {msg.content}
              </div>
            ))}
          </div>

        </div>
      </div>

    </div>
  );
}
