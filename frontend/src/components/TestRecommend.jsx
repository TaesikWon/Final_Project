// frontend/src/components/TestRecommend.jsx
import { useState } from "react";
import { recommendApts } from "../api/guriApi";

const TestRecommend = () => {
  const [result, setResult] = useState(null);

  const testRecommend = async () => {
    const conditions = {
      school_distance: 500,
      subway_distance: 800,
    };

    const res = await recommendApts(conditions);
    setResult(res);
  };

  return (
    <div>
      <h2>추천 API 테스트</h2>
      <button onClick={testRecommend}>테스트 실행</button>

      {result && (
        <pre style={{ background: "#eee" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default TestRecommend;
