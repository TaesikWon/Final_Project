import { useState } from "react";
import QueryInput from "../components/QueryInput";
import ResultBox from "../components/ResultBox";

export default function Recommend() {
  const [result, setResult] = useState(null);

  const sendQuery = async (text) => {
    const resp = await fetch("http://localhost:8000/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const json = await resp.json();
    setResult(json);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>자연어로 조건을 입력하세요</h2>
      <QueryInput onSubmit={sendQuery} />
      {result && <ResultBox result={result} />}
    </div>
  );
}
