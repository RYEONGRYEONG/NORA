'use client'
import { useState } from 'react'

export default function RiskAnalyserPage() {
  const [targetDate, setTargetDate] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const URL = process.env.NEXT_PUBLIC_API_URL;
  const today = new Date();
  const maxDate = new Date();
  maxDate.setDate(today.getDate() + 7);
  const maxDateString = maxDate.toISOString().split('T')[0];

  const handleAnalyse = async (dateToUse?: string) => {
    const checkDate = dateToUse || targetDate
    if (!checkDate) return alert("Please select a target date.")

    const savedFarm = localStorage.getItem('selectedFarm');
    if (!savedFarm) {
      alert("Please select a farm from the 'My Farms' menu first.");
      return;
    }
    const farmId = JSON.parse(savedFarm).id;

    setLoading(true)
    try {
        const response = await fetch(`${URL}/api/analysis?farm_id=${farmId}&target_date=${checkDate}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();

        if (response.ok) {
        setResult(data);
        if (dateToUse) setTargetDate(dateToUse); 
      } else {
        alert(data.detail || data.message || "Failed to analyse risk.");
      }
    } catch (error) {
      console.error("Connection error:", error);
      alert("Failed to reach the backend server.");
    } finally {
      setLoading(false);
    }
  };

  const riskColour = (risk: string) => {
    if (risk === 'High') return 'bg-red-500 text-white shadow-red-500/30'
    if (risk === 'Medium') return 'bg-yellow-400 text-slate-900 shadow-yellow-400/30'
    if (risk === 'Low') return 'bg-green-500 text-white shadow-green-500/30'
    return 'bg-slate-100'
  }

  const badgeColour = (risk: string) => {
    if (risk === 'High') return 'bg-red-100 text-red-700 font-bold'
    if (risk === 'Medium') return 'bg-yellow-100 text-yellow-800 font-bold'
    if (risk === 'Low') return 'bg-green-100 text-green-700 font-bold'
    return 'bg-slate-100'
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Target Date */}
      <div className="flex justify-between items-end bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div>
          <h1 className="text-3xl font-black text-slate-800">Risk Analyser</h1>
          <p className="text-sm text-slate-500 mt-1">When are you planning to spread fertiliser? Select a date to check the conditions!</p>
        </div>
        <div className="flex gap-3">
          <input 
            type="date" 
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            max={maxDateString}
            className="p-3 border border-slate-200 rounded-xl font-bold text-slate-700 outline-none focus:ring-2 focus:ring-[#0782c5]"
          />
          <button 
            onClick={() => handleAnalyse()}
            disabled={loading}
            className="bg-[#0782c5] text-white px-8 py-3 rounded-xl font-bold hover:bg-[#0671ab] transition-all disabled:opacity-50"
          >
            {loading ? "Analysing..." : "Analyse"}
          </button>
        </div>
      </div>

      {/* alternative date recommendation */}
      {result && result.recommended_date && result.recommended_date !== targetDate && (
        <div className="bg-blue-50 border-2 border-blue-400 p-6 rounded-2xl flex justify-between items-center shadow-md animate-pulse">
          <div>
            <h3 className="text-blue-800 font-bold text-lg">Alternative Found</h3>
            {/* detail messages */}
            <p className="text-blue-600 font-medium">{result.message}</p>
          </div>
          <button 
            onClick={() => handleAnalyse(result.recommended_date)}
            className="bg-blue-600 text-white px-6 py-2 rounded-xl font-bold shadow-lg hover:bg-blue-700 transition-colors"
          >
            Change Date
          </button>
        </div>
      )}

      {/* main */}
      {result && (
        <div className={`p-10 rounded-[32px] shadow-2xl transition-colors duration-500 ${riskColour(result.final_risk)}`}>
          <p className="text-sm font-bold uppercase tracking-widest opacity-80 mb-2">Final Assessment</p>
          <h2 className="text-6xl font-black mb-4">{result.final_risk}</h2>
          
          {result.recommended_date === targetDate && (
            <p className="text-xl font-medium mb-8 opacity-90">{result.message}</p>
          )}
          {result.recommended_date !== targetDate && (
            <p className="text-xl font-medium mb-8 opacity-90">Please see the alternative suggestion above.</p>
          )}
          
          <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/20">
            <div>
              <p className="text-xs font-bold opacity-70 uppercase mb-1">Rainfall Trigger</p>
              <p className="text-2xl font-bold">{result.rain_risk}</p>
              
              {result.reason && <p className="text-sm mt-1 opacity-90">{result.reason}</p>}
          
              <div className="mt-3 text-sm opacity-90 bg-black/10 px-3 py-2 rounded-lg inline-block">
                <p>Past (2d): <span className="font-black">{result.past_rain_sum} mm</span></p>
                <p>Forecast (2d): <span className="font-black">{result.forecast_rain_sum} mm</span></p>
              </div>
            </div>
            <div>
              <p className="text-xs font-bold opacity-70 uppercase mb-1">Soil Moisture (SMD)</p>
              <p className="text-2xl font-bold">{result.smd_value} mm</p>
              <p className="text-sm mt-1 opacity-80">{result.smd_risk} Saturation</p>
            </div>
          </div>
        </div>
      )}

      {/* total report */}
      {result && result.full_demo_report && result.full_demo_report.length > 0 && (
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-xl font-black text-slate-800">8-Day Detailed Demo Report</h3>
              <p className="text-sm text-slate-500 mt-1">Underlying logic and sliding window analysis for optimal date selection.</p>
            </div>
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{result.full_demo_report.length} Days Analysed</span>
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
                <tr>
                  <th className="px-5 py-4 font-bold">Date</th>
                  <th className="px-5 py-4 font-bold">Final Risk</th>
                  <th className="px-5 py-4 font-bold">Score</th>
                  <th className="px-5 py-4 font-bold">Past Rain</th>
                  <th className="px-5 py-4 font-bold">Forecast Rain</th>
                  <th className="px-5 py-4 font-bold w-1/3">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {result.full_demo_report.map((day: any) => {
                  const isTarget = day.date === targetDate;
                  const isRecommended = day.date === result.recommended_date && result.recommended_date !== targetDate;
                  
                  return (
                    <tr key={day.date} className={`${isTarget ? "bg-slate-50" : "hover:bg-slate-50/50"} transition-colors`}>
                      <td className="px-5 py-4">
                        <span className={`font-mono ${isTarget ? "font-black text-slate-900" : "text-slate-600"}`}>{day.date}</span>
                        {isTarget && <span className="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-600">TARGET</span>}
                        {isRecommended && <span className="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-600">RECOMMENDED</span>}
                      </td>
                      <td className="px-5 py-4">
                        <span className={`px-2.5 py-1 rounded-md text-xs ${badgeColour(day.final_risk)}`}>
                          {day.final_risk}
                        </span>
                      </td>
                      <td className="px-5 py-4 font-mono text-slate-600">{day.score}</td>
                      <td className="px-5 py-4 font-mono text-slate-600">{day.past_rain_sum} mm</td>
                      <td className="px-5 py-4 font-mono text-slate-600">{day.forecast_rain_sum} mm</td>
                      <td className="px-5 py-4 text-xs text-slate-500 line-clamp-2" title={day.reason}>
                        {day.reason}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  )
}