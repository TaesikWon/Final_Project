// frontend/src/App.jsx

import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Recommend from "./pages/Recommend";

function App() {
  return (
    <div className="min-h-screen bg-gray-100">

      <BrowserRouter>

        <div className="max-w-4xl mx-auto p-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/recommend" element={<Recommend />} />
          </Routes>
        </div>

      </BrowserRouter>

    </div>
  );
}

export default App;
