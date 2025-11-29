import React, { useState } from "react";
import { ragSearch } from "../api/guriApi";

const RagTest = () => {
  const [query, setQuery] = useState("");
  const [res, setRes] = useState([]);

  const runSearch = async () => {
    const r = await ragSearch(query);
    setRes(r);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>RAG 검색 테스트 (/rag/search)</h2>

      <input
        placeholder="예: 병원 기준"
        onChange={(e) => setQuery(e.target.value)}
        style={{ width: "300px", padding: 8 }}
      />
      <button onClick={runSearch}>검색</button>

      <pre style={{ background: "#eee", padding: 15 }}>
        {JSON.stringify(res, null, 2)}
      </pre>
    </div>
  );
};

export default RagTest;
