import { useState } from "react";

export default function QueryInput({ onSubmit }) {
  const [text, setText] = useState("");

  const handleClick = () => {
    if (!text.trim()) return;
    onSubmit(text);
  };

  return (
    <div>
      <input
        placeholder="예: 지하철 가까우면서 학군 좋은 곳"
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{ width: "100%", padding: 10, marginBottom: 10 }}
      />
      <button onClick={handleClick}>검색</button>
    </div>
  );
}
