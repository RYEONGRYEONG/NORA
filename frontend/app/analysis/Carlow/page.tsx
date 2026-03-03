"use client";

import React, { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2' ;
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);


const analysis = () => {
  const [analysisData, setAnalysisData] = useState<any>(null);

  useEffect(() => {
    fetch('https://nora-k0g7.onrender.com/analysis/Carlow')
      .then(res => res.json())
      .then(data => setAnalysisData(data));
  }, []);

  if (!analysisData) return <div>Loading Analysis...</div>;

  const { metrics_json, risk_level, location } = analysisData;

  const febScenario = metrics_json.scenarios.find((s: any) => s.month === 2);
  const targetDate = "2026-03-02"
  const current = metrics_json.current_metrics

  const chartData = {
    labels: metrics_json.labels, // ["Day 0", "Day 1", "Day 2", "Day 3"]
    datasets: [
      {
        label: 'February 2025 Historical SMD Trend',
        data: febScenario ? febScenario.trend : [], 
        borderColor: '#3498db', 
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial, sans-serif', maxWidth: '1000px', margin: '0 auto'}}>
      <h2>{location} Soil Risk Analysis</h2>
      
      <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '2px solid #ddd' }}>
          <h3 style={{ marginTop: 0, color: '#2c3e50', borderBottom: '1px solid #eee' }}>Current Metrics ({targetDate})</h3>
          <ul style={{ listStyle: 'none', padding: '10px 0', fontSize: '1.2rem', lineHeight: '1.8' }}>
            <li><strong>Past Rainfall (3d):</strong> <span style={{ color: '#2980b9' }}>{current.past_3} mm</span></li>
            <li><strong>Forecast (4d):</strong> <span style={{ color: '#2980b9' }}>{current.fcst_4} mm</span></li>
            <li><strong>Status:</strong> Monitoring for saturation</li>
          </ul>
        </div>


      <div style={{ 
        padding: '10px', 
        backgroundColor: risk_level === 'High' ? '#e74c3c' : '#f39c12', 
        color: 'white',
        borderRadius: '5px',
        display: 'inline-block'
      }}>
        {risk_level} RISK DETECTED
      </div>

      <div style={{ marginTop: '20px', backgroundColor: '#f9f9f9', padding: '15px' }}>
        <h3>Scenario Summary: February Case</h3>
        {febScenario && (
          <ul>
            <li><strong>Past Rainfall (3d):</strong> {febScenario.hist_past_3.toFixed(1)} mm</li>
            <li><strong>Scenario Event (4d):</strong> {febScenario.hist_fcst_4.toFixed(1)} mm</li>
            <li><strong>Soil Condition:</strong> Poorly drained soil shows saturation.</li>
          </ul>
        )}
      </div>

      <div style={{ height: '400px', marginTop: '30px' }}>
        <Line data={chartData} options={{ maintainAspectRatio: false }} />
      </div>
    </div>
  );
};

export default analysis;