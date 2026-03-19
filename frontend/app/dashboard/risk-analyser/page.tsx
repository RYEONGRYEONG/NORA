'use client'
import { useState } from 'react'

export default function RiskAnalyserPage() {
  const [targetDate, setTargetDate] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const URL = process.env.NEXT_PUBLIC_API_URL;

  const handleAnalyse = async (dateToUse?: string) => {
    const checkDate = dateToUse || targetDate
    if (!checkDate) return alert("Please select a target date.")

    // const savedFarm = localStorage.getItem('selectedFarm');
    //if (!savedFarm) {
      //alert("Please select a farm from the 'My Farms' menu first.");
      //return;
    //}
    //const farmId = JSON.parse(savedFarm).id;

    // test
    const farmId = 13;
    const target_date = "2026-03-22";

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

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
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

      {result && result.recommended_date && result.recommended_date !== targetDate && (
        <div className="bg-blue-50 border-2 border-blue-400 p-6 rounded-2xl flex justify-between items-center shadow-md animate-pulse">
          <div>
            <h3 className="text-blue-800 font-bold text-lg">Safer Alternative Found</h3>
            <p className="text-blue-600">The weather and soil conditions are optimal on <span className="font-black underline">{result.recommended_date}</span>.</p>
          </div>
          <button 
            onClick={() => handleAnalyse(result.recommended_date)}
            className="bg-blue-600 text-white px-6 py-2 rounded-xl font-bold shadow-lg hover:bg-blue-700 transition-colors"
          >
            Change Date
          </button>
        </div>
      )}

      {result && (
        <div className={`p-10 rounded-[32px] shadow-2xl transition-colors duration-500 ${riskColour(result.final_risk)}`}>
          <p className="text-sm font-bold uppercase tracking-widest opacity-80 mb-2">Final Assessment</p>
          <h2 className="text-6xl font-black mb-4">{result.final_risk}</h2>
          <p className="text-xl font-medium mb-8 opacity-90">{result.message}</p>
          
          <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/20">
            <div>
              <p className="text-xs font-bold opacity-70 uppercase mb-1">Rainfall Trigger</p>
              <p className="text-2xl font-bold">{result.rain_risk}</p>
              {result.rain_details?.reason && <p className="text-sm mt-1 opacity-80">{result.rain_details.reason}</p>}
            </div>
            <div>
              <p className="text-xs font-bold opacity-70 uppercase mb-1">Soil Moisture (SMD)</p>
              <p className="text-2xl font-bold">{result.smd_value} mm</p>
              <p className="text-sm mt-1 opacity-80">{result.smd_risk} Saturation</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}