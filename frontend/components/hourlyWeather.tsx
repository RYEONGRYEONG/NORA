'use client'
import React, { useState } from 'react';
import { format, parseISO } from 'date-fns';

export default function HourlyWeatherPage({data}: {data: any[]}) {
  const [selectedHour, setSelectedHour] = useState<any>(null);

  if (!data || data.length === 0) return null;

  const getRisk = (rain: number, wind: number) => {
    // (wind (m/s))
    // light rain -> avoid
    if (rain >= 1.0 || wind >= 5) return { status: 'Avoid', color: 'bg-red-400', icon: '🔴', label: 'High Risk' };
    if (rain > 0 || wind >= 2.8) return { status: 'Caution', color: 'bg-amber-300', icon: '🟡', label: 'Caution' };
    return { status: 'Good', color: 'bg-emerald-400', icon: '🟢', label: 'Optimal' };
  };

  // calculate optimal working window
  const goodHours = data.filter((h: any) => getRisk(h.rain, h.wind).status === 'Good');
  const bestWindow = goodHours.length > 0 
    ? `${format(parseISO(goodHours[0].time), 'HH:mm')} – ${format(parseISO(goodHours[Math.min(3, goodHours.length-1)].time), 'HH:mm')}`
    : "No ideal window on this day";

  const firstAvoid = data.find((h: any) => getRisk(h.rain, h.wind).status === 'Avoid');
  
return (
    <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-50 animate-in slide-in-from-bottom-4 duration-500 mt-8 font-sans">
      <div className="mb-10 p-7 bg-slate-50/50 rounded-[2rem] border-l-[12px] border-emerald-400">
        <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2 italic">Recommended Working Window</h2>
        <p className="text-3xl font-black text-slate-900">Best window: <span className="text-emerald-500">{bestWindow}</span></p>
        {firstAvoid && (
          <p className="text-sm text-rose-500 mt-2 font-bold italic underline decoration-rose-200 decoration-2 underline-offset-4">
            ⚠️ Risk increases at {format(parseISO(firstAvoid.time), 'HH:mm')}
          </p>
        )}
      </div>

      <div className="relative">
         <h3 className="text-xs font-black text-slate-300 mb-5 uppercase tracking-tighter text-center italic font-sans">Hourly Safety Strip (Click for details)</h3>
         <div className="flex overflow-x-auto pb-6 space-x-1.5 custom-scrollbar">
            {data.map((hour: any, idx: number) => {
              const risk = getRisk(hour.rain, hour.wind);
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
  );
}