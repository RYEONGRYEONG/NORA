'use client'
import React, { useState } from 'react';
import { format, parseISO } from 'date-fns';

export default function HourlyWeatherPage({ data }: { data: any[] }) {
  const [targetDate, setTargetDate] = useState('');
  const [hourlyData, setHourlyData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedHour, setSelectedHour] = useState<any>(null);

  const URL = process.env.NEXT_PUBLIC_API_URL;
  const maxDate = new Date();
  maxDate.setDate(new Date().getDate() + 7);
  const maxDateStr = maxDate.toISOString().split('T')[0];

  const getRisk = (rain: number, wind: number, gust: number) => {
    // (wind (m/s))
    // light rain -> avoid
    if (rain >= 1.0 || wind >= 2.8 || gust >= 4.2) return { status: 'Avoid', color: 'bg-red-400', icon: '🔴', label: 'High Risk' };
    if (rain > 0 || wind >= 2.0 || gust >= 2.8) return { status: 'Caution', color: 'bg-amber-300', icon: '🟡', label: 'Caution' };
    return { status: 'Good', color: 'bg-emerald-400', icon: '🟢', label: 'Optimal' };
  };

  const handleAnalyse = async () => {
    if (!targetDate) return alert("Please select a target date.");
    const savedFarm = localStorage.getItem('selectedFarm');
    if (!savedFarm) return alert("Please select a farm first.");

    const farmId = JSON.parse(savedFarm).id;
    setLoading(true)

    try {
      const response = await fetch(`${URL}/api/hourly?farm_id=${farmId}&target_date=${targetDate}`);
      const data = await response.json();

      if (response.ok) {
        setHourlyData(data.hourly || []);
        setSelectedHour(null);
      } else{
        alert (data.message || "Failed to analyse.");
      }
    }
    
    catch (error){
      alert("Connection error.");
    } finally {
      setLoading(false);
    }
  };

  // calculate optimal working window
  const goodHours = hourlyData.filter((h: any) => getRisk(h.rain, h.wind, h.gust).status === 'Good');
  const bestWindow = goodHours.length > 0 
    ? `${format(parseISO(goodHours[0].time), 'HH:mm')} – ${format(parseISO(goodHours[Math.min(3, goodHours.length-1)].time), 'HH:mm')}`
    : "No ideal window on this day";

  const firstAvoid = hourlyData.find((h: any) => getRisk(h.rain, h.wind, h.gust).status === 'Avoid');
  
return (
    <div className="space-y-8 animate-in fade-in duration-500 font-sans">
      {/* [1] Date Selection */}
      <div className="flex justify-between items-end bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
        <div>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight">Select a date to check your safe spreading window.</h1>
        </div>
        <div className="flex gap-3">
          <input 
            type="date" 
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            max={maxDateStr}
            className="p-3 border border-slate-200 rounded-2xl font-bold text-slate-700 outline-none focus:ring-2 focus:ring-[#0782c5]"
          />
          <button 
            onClick={handleAnalyse}
            disabled={loading}
            className="bg-[#0782c5] text-white px-8 py-3 rounded-2xl font-black hover:bg-[#0671ab] transition-all disabled:opacity-50"
          >
            {loading ? "Analysing..." : "Analyse"}
          </button>
        </div>
      </div>

      {/* result section */}
      {hourlyData.length > 0 && (
        <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-50 animate-in slide-in-from-bottom-4 duration-500">
          <div className="mb-10 p-7 bg-slate-50/50 rounded-[2rem] border-l-[12px] border-emerald-400">
            <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2 italic">Recommended Working Window</h2>
            <p className="text-3xl font-black text-slate-900">Best window: <span className="text-emerald-500">{bestWindow}</span></p>
            {firstAvoid && (
              <p className="text-sm text-rose-500 mt-2 font-bold italic underline decoration-rose-200 decoration-2 underline-offset-4">
                Avoid after {format(parseISO(firstAvoid.time), 'HH:mm')} (Risk increases)
              </p>
            )}
          </div>

          <div className="relative">
             <h3 className="text-xs font-black text-slate-300 mb-5 uppercase tracking-tighter text-center italic font-sans">Hourly Safety Strip (Click for details)</h3>
             <div className="flex overflow-x-auto pb-6 space-x-1.5 custom-scrollbar">
                {hourlyData.map((hour: any, idx: number) => {
                  const risk = getRisk(hour.rain, hour.wind, hour.gust);
                  return (
                    <button 
                      key={idx} 
                      onClick={() => setSelectedHour(hour)}
                      className="flex-none w-12 flex flex-col items-center group"
                    >
                      <span className="text-[10px] font-black text-slate-400 mb-3">{format(parseISO(hour.time), 'HH')}</span>
                      <div className={`w-full h-14 ${risk.color} rounded-xl shadow-inner transition-transform group-hover:scale-105 flex items-center justify-center opacity-80`}>
                        <span className="text-xs">{risk.icon}</span>
                      </div>
                    </button>
                  );
                })}
             </div>
          </div>

          {selectedHour && (
            <div className="mt-8 p-8 bg-slate-50 rounded-[2rem] border border-slate-100 animate-in zoom-in-95 duration-200">
              <div className="flex justify-between items-center mb-6">
                <h4 className="font-black text-slate-800 italic underline decoration-emerald-400 decoration-4 underline-offset-4">Insights for {format(parseISO(selectedHour.time), 'HH:mm')}</h4>
                <button onClick={() => setSelectedHour(null)} className="text-xs font-black text-slate-300 hover:text-slate-500 uppercase">Close ✕</button>
              </div>
              <div className="grid grid-cols-2 gap-10 text-center font-sans">
                <div>
                  <p className="text-[10px] font-black text-blue-400 uppercase mb-2 italic">Rainfall</p>
                  <p className="text-2xl font-black text-slate-700">{selectedHour.rain} <span className="text-xs text-slate-400">mm/h</span></p>
                </div>
                <div>
                  <p className="text-[10px] font-black text-rose-400 uppercase mb-2 italic">Wind Speed</p>
                  <p className="text-2xl font-black text-slate-700">{selectedHour.wind} <span className="text-xs text-slate-400">m/s</span></p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}