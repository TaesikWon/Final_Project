// frontend/src/pages/PredictTest.jsx

import { useState } from "react";
import { predictSentence } from "../api/guriApi";

export default function PredictTest() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runPredict = async () => {
    if (!text.trim()) {
      alert("문장을 입력하세요");
      return;
    }

    setLoading(true);
    try {
      const res = await predictSentence(text);
      setResult(res);
    } catch (err) {
      console.error(err);
      alert("예측 실패: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">
        🧪 문장 분석 테스트 (/predict)
      </h2>

      <div className="bg-white border rounded-xl p-6 shadow">
        <input
          className="w-full border rounded px-4 py-3 mb-4"
          placeholder="예: 지하철 가까운 아파트 찾아줘"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && runPredict()}
        />

        <button
          onClick={runPredict}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded
                     disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? "분석 중..." : "실행"}
        </button>
      </div>

      {result && (
        <div className="bg-gray-100 p-6 mt-6 rounded-xl shadow">
          <h3 className="text-lg font-semibold mb-3">📊 분석 결과</h3>
          <pre className="text-sm overflow-auto bg-white p-4 rounded border">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}