import { useState } from "react";
import { parseConditions, recommendApts } from "../api/guriApi";
import MapView from "../components/MapView";
import AptCard from "../components/AptCard";

export default function RecommendTest() {
  const [text, setText] = useState("");
  const [conditions, setConditions] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [selectedApt, setSelectedApt] = useState(null);

  const handleTest = async () => {
    setSelectedApt(null);
    setLoading(true);

    try {
      const parsed = await parseConditions(text);
      setConditions(parsed.parsed_conditions);

      const res = await recommendApts(parsed.parsed_conditions);
      setResult(res);
    } catch (err) {
      alert("테스트 중 오류 발생");
    }

    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-6">

      <h2 className="text-xl font-bold mb-4">🗺 지도 (추천 아파트 표시)</h2>
      <MapView 
        apartments={result || []}
        selectedApt={selectedApt}
      />

      {/* 입력 */}
      <div className="bg-white border rounded-xl p-6 mt-8 shadow">
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

      {/* 추천 리스트 */}
      {result && (
        <div className="grid grid-cols-1 gap-4 mt-8">
          {result.map((apt) => (
            <AptCard 
              key={apt.apartment}
              apt={apt}
              onClick={() => setSelectedApt(apt.apartment)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
