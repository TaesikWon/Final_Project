// src/components/ResultBox.jsx
export default function ResultBox({ result }) {
  return (
    <div
      style={{
        width: "100%",
        minHeight: "200px",
        padding: "15px",
        borderRadius: "8px",
        border: "1px solid #ccc",
        background: "#f8f8f8",
        whiteSpace: "pre-wrap",
        overflowY: "auto",
      }}
    >
      {result ? JSON.stringify(result, null, 2) : "추천 결과가 여기에 표시됩니다."}
    </div>
  );
}
