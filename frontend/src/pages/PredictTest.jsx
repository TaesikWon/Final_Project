// frontend/src/pages/PredictTest.jsx

import React, { useState } from "react";
import { predictSentence } from "../api/guriApi";

const PredictTest = () => {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const runPredict = async () => {
    const res = await predictSentence(text);
    setResult(res);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>문장 분석 테스트 (/predict)</h2>

      <input
        style={{ width: "300px", padding: 8 }}
        placeholder="예: 지하철 가까운 아파트 찾아줘"
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={runPredict}>실행</button>

      {result && (
        <pre style={{ background: "#eee", padding: 15 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default PredictTest;
