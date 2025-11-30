// frontend/src/pages/Recommend.jsx

import { useState } from "react";
import { parseConditions, recommendApts } from "../api/guriApi";
import MapView from "../components/MapView";

export default function Recommend() {
  const [query, setQuery] = useState("");
  const [conditions, setConditions] = useState(null);
  const [apartments, setApartments] = useState([]);
  const [selectedApt, setSelectedApt] = useState(null);

  const runRecommend = async () => {
    if (!query.trim()) return alert("조건을 입력하세요.");

    try {
      const parsed = await parseConditions(query);
      setConditions(parsed.parsed_conditions);

      const result = await recommendApts(parsed.parsed_conditions);
      setApartments(result);
    } catch (err) {
      console.error(err);
      alert("추천 과정에서 오류가 발생했습니다.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">🏢 구리시 아파트 추천</h1>

      {/* 입력 영역 */}
      <div className="bg-white border rounded-xl p-6 shadow">
        <input
          className="w-full border rounded px-4 py-3 mb-4"
          placeholder="예: 인창고등학교 근처 5억 이하 아파트 추천해줘"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={runRecommend}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded"
        >
          추천 실행
        </button>
      </div>

      {/* 지도 */}
      <h2 className="text-xl font-semibold mt-10">🗺 지도</h2>
      <MapView apartments={apartments} selectedApt={selectedApt} />

      {/* 추천 리스트 */}
      <div className="mt-8 grid grid-cols-1 gap-4">
        {apartments.map((apt) => (
          <div
            key={apt.apartment}
            onClick={() => setSelectedApt(apt.apartment)}
            className="bg-white border rounded-xl p-4 shadow cursor-pointer hover:shadow-md transition"
          >
            <h3 className="font-bold">{apt.apartment}</h3>
            <p className="text-sm text-gray-600">
              학교 거리: {apt.distance_school}m
            </p>
            <p className="text-sm text-gray-600">
              가격: {apt.price || "정보 없음"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
