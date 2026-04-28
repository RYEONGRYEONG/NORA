'use client'
import React from 'react';

const UserResources = () => {
  return (
    <div className="max-w-6xl mx-auto p-10 font-sans">
      <h1 className="text-4xl font-bold text-slate-800 mb-4">User Resources</h1>
      <p className="text-xl text-slate-500 mb-10">
        Everything you need to get started with NORA and understand our data-driven approach.
      </p>

      <section className="mb-16">
        <h2 className="text-2xl font-bold text-[#0782c5] mb-6 flex items-center gap-2">
            ▶ Video Tutorial
        </h2>

        <div className="relative pb-[56.25%] h-0 overflow-hidden rounded-xl shadow-lg">
          <iframe 
            src="https://www.youtube.com/embed/klLSdP6KPtw" 
            className="absolute top-0 left-0 w-full h-full border-0"
            allowFullScreen
            title="NORA Project Demo"
          ></iframe>
        </div>
        <p className="mt-6 text-lg text-slate-600 leading-relaxed">
          Please Watch this screencast above to see NORA in action and learn how to navigate the system effectively.
        </p>
      </section>
      
      <section className="bg-slate-50 p-8 rounded-2xl border border-slate-100 shadow-sm">
        <h2 className="text-2xl font-bold mb-6">Step-by-Step Guide</h2>
        <div className="space-y-8">
          <div>
            <h3 className="text-lg font-bold text-[#0782c5] mb-2">1. Account Setup</h3>
            <p className="text-slate-600">Sign up for a new account or log in to access your personalised dashboard.</p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-[#0782c5] mb-2">2. Register Your Farm</h3>
            <p className="text-slate-600">
              Navigate to the <strong>My Farms</strong> page. Use the interactive map to drop a pin on your exact location and select your soil drainage type. NORA will then <strong>dynamically fetch</strong> precise weather data for your specific coordinates.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-[#0782c5] mb-2">3. Explore Historical Context</h3>
            <p className="text-slate-600">
              Visit the <strong>Historical</strong> page to review recent weather trends. Compare your current Soil Moisture Deficit (SMD) against the <strong>5-year historical average</strong>. This helps you understand why the current conditions might be an anomaly compared to past habits.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-[#0782c5] mb-2">4. Analyse Daily Risks</h3>
            <p className="text-slate-600">
              On the <strong>Risk Analyser</strong> page, select your target date. The system <strong>instantly calculates</strong> a risk score by combining soil and weather data. You will also receive a <strong>custom AI advisory</strong>, providing context-aware guidelines for your specific farm.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-[#0782c5] mb-2">5. Find the ‘Best Window’</h3>
            <p className="text-slate-600">
              Finally, check the <strong>Forecast</strong> page for the safest hourly ‘Best Window’. Check wind speed and rainfall hour-by-hour to avoid fertiliser drift or runoff. Click on any time slot for a detailed data breakdown.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default UserResources;