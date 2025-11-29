// frontend/src/pages/Recommend.jsx
import { useState } from "react";
import { parseConditions, recommendApts } from "../api/guriApi";

export default function Recommend() {
  const [text, setText] = useState("");
  const [conditions, setConditions] = useState(null);
  const [recommend, setRecommend] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRecommend = async () => {
    if (!text.trim()) return alert("조건을 입력해주세요!");

    setLoading(true);
    setRecommend(null);

    try {
      const parsed = await parseConditions(text);
      setConditions(parsed.parsed_conditions);

      const res = await recommendApts(parsed.parsed_conditions);
      setRecommend(res.recommendations);
    } catch (err) {
      console.error(err);
      alert("추천 중 오류가 발생했습니다.");
    }

    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-6">

      {/* 입력 카드 */}
      <div className="bg-white shadow-lg rounded-xl p-6 border border-gray-100">
        <h2 className="text-2xl font-bold mb-4 text-gray-800 flex items-center gap-2">
          🏡 AI 아파트 추천
        </h2>

        <div className="flex gap-4 mt-2">
          <input
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-gray-800
                       focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="예: 초등학교 500m 이내, 10억 이하, 신축 아파트 추천해줘"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <button
            onClick={handleRecommend}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white 
                       rounded-lg font-medium shadow-md transition"
          >
            추천하기
          </button>
        </div>

        {loading && (
          <div className="mt-4 text-blue-600 font-medium animate-pulse">
            ⏳ 추천 중입니다...
          </div>
        )}
      </div>

      {/* 조건 분석 카드 */}
      {conditions && (
        <div className="mt-8 p-6 bg-red-50 border border-blue-200 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-blue-900">
            🔍 조건 분석 결과
          </h3>
          <pre className="mt-3 bg-white p-4 border rounded-lg text-sm overflow-x-auto">
            {JSON.stringify(conditions, null, 2)}
          </pre>
        </div>
      )}

      {/* 추천 결과 */}
      {recommend && (
        <div className="mt-10 space-y-6">
          <h3 className="text-xl font-bold text-gray-800">🏠 추천 아파트 리스트</h3>

          {recommend.length === 0 && (
            <p className="text-gray-600">조건에 맞는 아파트가 없습니다.</p>
          )}

          {recommend.map((apt, idx) => (
            <div
              key={idx}
              className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition"
            >
              <h4 className="text-xl font-semibold text-gray-900">
                {apt.apartment}
              </h4>
              <p className="text-gray-600 mt-1">{apt.address}</p>

              <div className="mt-4">
                <h5 className="font-semibold text-gray-800 mb-2">
                  📍 주변 시설 거리 정보
                </h5>

                <pre className="bg-gray-50 p-4 border rounded-lg text-sm overflow-x-auto">
                  {JSON.stringify(apt.distance_detail, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
