import './MetricsDashboard.css';

interface Metrics {
  total_queries: number;
  avg_spec_accuracy: number;
  avg_pricing_accuracy: number;
  avg_hallucination_check: number;
  avg_overall_score: number;
}

interface Props {
  metrics: Metrics | null;
}

const MetricsDashboard = ({ metrics }: Props) => {
  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'high';
    if (score >= 0.5) return 'medium';
    return 'low';
  };

  const getScoreEmoji = (score: number): string => {
    if (score >= 0.9) return '🌟';
    if (score >= 0.8) return '✅';
    if (score >= 0.5) return '⚠️';
    return '❌';
  };

  if (!metrics) {
    return (
      <div className="metrics-dashboard">
        <h2>📊 Quality Metrics</h2>
        <div className="loading-metrics">
          <div className="spinner"></div>
          <p>Loading metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="metrics-dashboard">
      <h2>📊 Quality Metrics</h2>

      <div className="metrics-summary">
        <div className="summary-card">
          <div className="summary-icon">💬</div>
          <div className="summary-content">
            <p className="summary-label">Total Queries</p>
            <p className="summary-value">{metrics.total_queries}</p>
          </div>
        </div>

        <div className="summary-card highlight">
          <div className="summary-icon">🎯</div>
          <div className="summary-content">
            <p className="summary-label">Overall Score</p>
            <p className="summary-value">
              {(metrics.avg_overall_score * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-icon">📊</span>
            <h3>Spec Accuracy</h3>
          </div>
          <div className="metric-score">
            <div className={`score-circle ${getScoreColor(metrics.avg_spec_accuracy)}`}>
              <span className="score-emoji">{getScoreEmoji(metrics.avg_spec_accuracy)}</span>
              <span className="score-value">
                {(metrics.avg_spec_accuracy * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <p className="metric-description">
            Accuracy of technical specifications
          </p>
          <div className="metric-bar">
            <div
              className={`metric-fill ${getScoreColor(metrics.avg_spec_accuracy)}`}
              style={{ width: `${metrics.avg_spec_accuracy * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-icon">💰</span>
            <h3>Pricing Accuracy</h3>
          </div>
          <div className="metric-score">
            <div className={`score-circle ${getScoreColor(metrics.avg_pricing_accuracy)}`}>
              <span className="score-emoji">{getScoreEmoji(metrics.avg_pricing_accuracy)}</span>
              <span className="score-value">
                {(metrics.avg_pricing_accuracy * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <p className="metric-description">
            Correct pricing and cost information
          </p>
          <div className="metric-bar">
            <div
              className={`metric-fill ${getScoreColor(metrics.avg_pricing_accuracy)}`}
              style={{ width: `${metrics.avg_pricing_accuracy * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-icon">✨</span>
            <h3>Hallucination Check</h3>
          </div>
          <div className="metric-score">
            <div className={`score-circle ${getScoreColor(metrics.avg_hallucination_check)}`}>
              <span className="score-emoji">{getScoreEmoji(metrics.avg_hallucination_check)}</span>
              <span className="score-value">
                {(metrics.avg_hallucination_check * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <p className="metric-description">
            Safety against false information
          </p>
          <div className="metric-bar">
            <div
              className={`metric-fill ${getScoreColor(metrics.avg_hallucination_check)}`}
              style={{ width: `${metrics.avg_hallucination_check * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="metrics-legend">
        <div className="legend-item">
          <span className="legend-dot high"></span>
          <span>Excellent (≥80%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot medium"></span>
          <span>Good (50-79%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot low"></span>
          <span>Needs Improvement (&lt;50%)</span>
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;
