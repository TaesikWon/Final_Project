// frontend/src/components/PredictTest.jsx
import React, { useState } from "react";
import { predictSentence } from "../api/guriApi";

const PredictTest = () => {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const handlePredict = async () => {
    const res = await predictSentence(text);
    setResult(res);
  };

  return (
    <div>
      <h2>문장 분석 테스트</h2>
      <input
        value={text}
        placeholder="입력하세요"
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={handlePredict}>분석</button>

      {result && (
        <pre style={{ background: "#eee", padding: 10 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default PredictTest;
