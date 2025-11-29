// frontend/src/App.jsx

import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Home from "./pages/Home";
import Recommend from "./pages/Recommend";
import PredictTest from "./pages/PredictTest";
import RecommendTest from "./pages/RecommendTest";
import RagTest from "./pages/RagTest";

function App() {
  return (
    <div className="min-h-screen bg-gray-100">    {/* <-- 전체 배경색 & 레이아웃 컨트롤 */}

      <BrowserRouter>
        {/* 상단 네비게이션 */}
        <nav className="p-4 border-b bg-white shadow flex gap-5">
          <Link to="/" className="hover:text-blue-600">Home</Link>
          <Link to="/recommend" className="hover:text-blue-600">추천</Link>

          {/* 테스트 페이지들 */}
          <Link to="/predict-test" className="hover:text-blue-600">PredictTest</Link>
          <Link to="/recommend-test" className="hover:text-blue-600">RecommendTest</Link>
          <Link to="/rag-test" className="hover:text-blue-600">RagTest</Link>
        </nav>

        {/* 실제 페이지 */}
        <div className="max-w-4xl mx-auto p-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/recommend" element={<Recommend />} />
            <Route path="/predict-test" element={<PredictTest />} />
            <Route path="/recommend-test" element={<RecommendTest />} />
            <Route path="/rag-test" element={<RagTest />} />
          </Routes>
        </div>

      </BrowserRouter>

    </div>
  );
}

export default App;
