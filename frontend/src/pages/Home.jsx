// frontend/src/pages/Home.jsx

export default function Home() {
  return (
    <div className="">

      {/* ------------------------------ */}
      {/*           HERO 영역            */}
      {/* ------------------------------ */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-400 text-white py-24 px-6 text-center shadow-lg">
        <h1 className="text-5xl font-extrabold mb-6 drop-shadow-md">
          구리시 AI 아파트 추천 서비스
        </h1>
        <p className="text-lg opacity-90 max-w-2xl mx-auto leading-relaxed">
          구리시 시설·거리·환경 데이터를 기반으로  
          당신의 조건에 가장 잘 맞는 아파트를 AI가 찾아드립니다.
        </p>

        <a
          href="/recommend"
          className="inline-block mt-10 px-10 py-4 bg-white text-blue-600 
                     font-bold rounded-2xl text-lg shadow-lg hover:shadow-xl
                     hover:bg-blue-50 transition"
        >
          🔍 AI로 아파트 추천받기
        </a>
      </section>


      {/* ------------------------------ */}
      {/*         FEATURES (3카드)       */}
      {/* ------------------------------ */}
      <section className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 py-16 px-6">

        {/* Feature 1 */}
        <div className="bg-white p-8 rounded-2xl shadow hover:shadow-md transition border">
          <h3 className="text-xl font-semibold mb-3">📌 자연어 분석</h3>
          <p className="text-gray-600 text-sm leading-relaxed">
            “학교 반경 500m 이내 아파트를 추천해줘”  
            같은 문장을 AI가 자동으로 조건으로 변환합니다.
          </p>
        </div>

        {/* Feature 2 */}
        <div className="bg-white p-8 rounded-2xl shadow hover:shadow-md transition border">
          <h3 className="text-xl font-semibold mb-3">🏠 맞춤형 추천</h3>
          <p className="text-gray-600 text-sm leading-relaxed">
            교육·의료·편의시설 등을 종합 분석해  
            최적의 아파트를 추천합니다.
          </p>
        </div>

        {/* Feature 3 */}
        <div className="bg-white p-8 rounded-2xl shadow hover:shadow-md transition border">
          <h3 className="text-xl font-semibold mb-3">🔍 RAG 기반 분석</h3>
          <p className="text-gray-600 text-sm leading-relaxed">
            구리시 데이터 800+개 시설 정보를  
            벡터DB 기반으로 검색합니다.
          </p>
        </div>

      </section>


      {/* ------------------------------ */}
      {/*    BOTTOM INFO / FOOTER        */}
      {/* ------------------------------ */}
      <footer className="text-center text-gray-400 text-sm py-10">
        © 2025 Guri AI Housing Recommender · Made with FastAPI / React / Tailwind
      </footer>
    </div>
  );
}
