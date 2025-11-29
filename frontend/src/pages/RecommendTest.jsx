// frontend/src/pages/RecommendTest.jsx
import { useState } from "react";
import { parseConditions, recommendApts } from "../api/guriApi";

export default function RecommendTest() {
  const [text, setText] = useState("");
  const [conditions, setConditions] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    if (!text.trim()) return alert("문장을 입력해주세요.");

    setLoading(true);
    setResult(null);

    try {
      // 자연어 조건 파싱
      const parsed = await parseConditions(text);
      setConditions(parsed.parsed_conditions);

      // 추천 테스트
      const res = await recommendApts(parsed.parsed_conditions);
      setResult(res);
    } catch (err) {
      console.error(err);
      alert("테스트 중 오류 발생");
    }

    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-6">

      {/* 테스트 입력 카드 */}
      <div className="bg-white shadow rounded-xl border p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          🧪 Recommend Test 페이지
        </h2>

        <input
          className="w-full border border-gray-300 rounded-lg px-4 py-3 mb-4
                     focus:ring-2 focus:ring-blue-500 outline-none"
          placeholder="테스트할 문장을 입력하세요"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          onClick={handleTest}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow"
        >
          테스트 실행
        </button>

        {loading && (
          <p className="text-blue-600 font-medium mt-4 animate-pulse">
            ⏳ 테스트 실행 중...
          </p>
        )}
      </div>

      {/* 조건 출력 */}
      {conditions && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl mt-8 p-6">
          <h3 className="font-semibold text-blue-900">🔍 파싱된 조건(JSON)</h3>
          <pre className="mt-3 bg-white border p-4 rounded-lg text-sm overflow-x-auto">
            {JSON.stringify(conditions, null, 2)}
          </pre>
        </div>
      )}

      {/* 추천 API 결과 전체 출력 */}
      {result && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl mt-8 p-6">
          <h3 className="font-semibold text-gray-900">📦 API 원본 응답</h3>

          <pre className="mt-3 bg-white border p-4 rounded-lg text-sm overflow-x-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
