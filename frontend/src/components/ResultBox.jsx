export default function ResultBox({ result }) {
  return (
    <pre
      style={{
        marginTop: 20,
        padding: 15,
        background: "#f5f5f5",
        borderRadius: 8,
      }}
    >
      {JSON.stringify(result, null, 2)}
    </pre>
  );
}
