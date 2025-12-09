// frontend/src/pages/RecommendTest.jsx

import { useState } from "react";
import { parseConditions, recommendApts } from "../api/guriApi";

export default function RecommendTest() {
  const [text, setText] = useState("");
  const [conditions, setConditions] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    setLoading(true);
    setResult(null);
    setConditions(null);

    try {
      // 1) 파싱
      const parsed = await parseConditions(text);
      setConditions(parsed.parsed_conditions);

      // 2) 추천 API 실행
      const res = await recommendApts(parsed.parsed_conditions);
      setResult(res);
    } catch (err) {
      console.error(err);
      alert("테스트 중 오류 발생: " + err.message);
    }

    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-6">

      <h1 className="text-2xl font-bold mb-6">🔍 RAG + 추천 테스트</h1>

      {/* 입력 */}
      <div className="bg-white border rounded-xl p-6 shadow">
        <input
          className="w-full border rounded px-4 py-3 mb-4"
          placeholder="예: 인창고등학교 근처 아파트"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          onClick={handleTest}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded"
        >
          추천 실행
        </button>
      </div>

      {/* 파싱된 조건 */}
      {conditions && (
        <div className="bg-gray-100 p-4 mt-6 rounded shadow">
          <h2 className="text-lg font-semibold">📌 파싱된 조건</h2>
          <pre className="text-sm">{JSON.stringify(conditions, null, 2)}</pre>
        </div>
      )}

      {/* 추천 리스트 */}
      {result && (
        <div className="mt-8 bg-white border rounded-xl p-6 shadow">
          <h2 className="text-lg font-semibold mb-4">🏘 추천된 아파트 목록</h2>

          {result.length === 0 && (
            <p className="text-gray-600">추천 결과가 없습니다.</p>
          )}

          <ul className="space-y-3">
            {result.map((apt, idx) => (
              <li
                key={idx}
                className="p-4 border rounded-lg bg-gray-50 hover:bg-gray-100 transition"
              >
                <p className="font-bold">{apt.apartment || "이름 없음"}</p>
                <p className="text-sm text-gray-600">
                  거리: {apt.distance_school || "?"} m
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {loading && (
        <p className="mt-4 text-center text-gray-500">⏳ 로딩 중...</p>
      )}
    </div>
  );
}
