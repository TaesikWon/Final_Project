// src/components/QueryInput.jsx
import { useState } from "react";

export default function QueryInput({ onSubmit }) {
  const [text, setText] = useState("");

  const handleClick = () => {
    if (text.trim()) onSubmit(text);
  };

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="예) 초등학교 가까운 아파트 추천해줘"
        style={{
          width: "100%",
          height: "120px",
          padding: "10px",
          borderRadius: "8px",
          border: "1px solid #ccc",
          resize: "none",
        }}
      />

      <button
        onClick={handleClick}
        style={{
          width: "100%",
          marginTop: "10px",
          padding: "12px",
          borderRadius: "8px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        제출
      </button>
    </div>
  );
}
