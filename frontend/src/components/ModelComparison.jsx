import React from 'react';
import './ModelComparison.css';

const ModelComparison = ({ results, loading }) => {
  if (loading) {
    return <div className="loading">🔄 AI 모델들이 분석 중입니다...</div>;
  }

  if (!results) {
    return null;
  }

  return (
    <div className="model-comparison">
      <h2>🤖 AI 모델 비교 결과</h2>
      
      <div className="comparison-grid">
        {/* KoBERT */}
        <div className="model-card kobert">
          <div className="model-header">
            <h3>🤖 KoBERT</h3>
            <span className="badge local">로컬 모델</span>
          </div>
          <div className="model-body">
            <p className="result">{results.kobert}</p>
            <div className="model-info">
              <small>✓ 빠른 응답</small>
              <small>✓ 카테고리 분류 특화</small>
            </div>
          </div>
        </div>

        {/* GPT-4 */}
        <div className="model-card gpt">
          <div className="model-header">
            <h3>🧠 GPT-4 Turbo</h3>
            <span className="badge cloud">클라우드</span>
          </div>
          <div className="model-body">
            <p className="result">{results.gpt4_1}</p>
            <div className="model-info">
              <small>✓ 상세한 분석</small>
              <small>✓ 범용 AI</small>
            </div>
          </div>
        </div>

        {/* Claude */}
        <div className="model-card claude">
          <div className="model-header">
            <h3>💬 Claude 3.5 Sonnet</h3>
            <span className="badge cloud">클라우드</span>
          </div>
          <div className="model-body">
            <p className="result">{results.claude}</p>
            <div className="model-info">
              <small>✓ 자연스러운 설명</small>
              <small>✓ 맥락 이해</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelComparison;