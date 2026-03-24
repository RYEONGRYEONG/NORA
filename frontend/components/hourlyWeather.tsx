'use client'
import React, { useState } from 'react';
import { format } from 'date-fns';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

export default function HourlyDecisionCard({ data }: { data: any[] }) {
  const [selectedHour, setSelectedHour] = useState<any>(null);

  if (!data || data.length === 0) return null;

  const getRisk = (rain: number, wind: number, gust: number) => {
    // (wind (m/s))
    // light rain -> avoid
    if (rain >= 1.0 || wind >= 2.8 || gust >= 4.2) return { status: 'Avoid', color: 'bg-red-500', icon: '🔴', label: 'High Risk' };
    if (rain > 0 || wind >= 2.0 || gust >= 2.8) return { status: 'Caution', color: 'bg-amber-400', icon: '🟡', label: 'Caution' };
    return { status: 'Good', color: 'bg-emerald-500', icon: '🟢', label: 'Optimal' };
  };

  // calculate optimal working window
  const goodHours = data.filter(d => getRisk(d.rain, d.wind, d.gust).status === 'Good');
  const bestWindow = goodHours.length > 0 
    ? `${format(new Date(goodHours[0].time), 'HH:mm')} – ${format(new Date(goodHours[Math.min(3, goodHours.length-1)].time), 'HH:mm')}`
    : "No ideal window today";

  const firstAvoidHour = data.find(d => getRisk(d.rain, d.wind, d.gust).status === 'Avoid');
  const warningMessage = firstAvoidHour ? `Avoid after ${format(new Date(firstAvoidHour.time), 'HH:mm')} (Risk increases)`
  : "Conditions remain stable for the next few hours.";

  return (
    <div className="w-full bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-8 font-sans">
      <div className="mb-8 p-5 bg-slate-50 rounded-2xl border-l-8 border-emerald-500">
        <h2 className="text-sm font-black text-slate-500 uppercase tracking-widest">Recommended working window</h2>
        <div className="mt-2">
          <p className="text-2xl font-black text-slate-900">Best window: <span className="text-emerald-600">{bestWindow}</span></p>
          <p className="text-sm text-rose-500 mt-1 font-bold italic underline decoration-rose-300">{warningMessage}</p>
        </div>
      </div>

      {/* Strip */}
      <div className="mb-8">
        <h3 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-tighter text-center">Hourly Safety Strip (Click to see details)</h3>
        <div className="flex overflow-x-auto pb-4 custom-scrollbar space-x-1">
          {data.map((hour, idx) => {
            const risk = getRisk(hour.rain, hour.wind, hour.gust);
            return (
              <button 
                key={idx} 
                onClick={() => setSelectedHour(hour)}
                className={`flex-none w-10 flex flex-col items-center group transition-all`}
              >
                <span className="text-[10px] font-bold text-slate-400 mb-2">{format(new Date(hour.time), 'HH')}</span>
                <div className={`w-full h-12 ${risk.color} rounded-md shadow-inner group-hover:brightness-110 flex items-center justify-center text-[10px] opacity-40`}>
                  {risk.icon}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* details */}
      {selectedHour && (
        <div className="mt-4 p-6 bg-slate-50 rounded-3xl border border-slate-100 animate-in fade-in slide-in-from-top-4 duration-300">
          <div className="flex justify-between items-center mb-6">
            <h4 className="font-black text-slate-800 underline decoration-emerald-500 decoration-4 underline-offset-4">
              Details for {format(new Date(selectedHour.time), 'HH:mm')}
            </h4>
            <button onClick={() => setSelectedHour(null)} className="text-xs font-bold text-slate-400 hover:text-slate-600">Close ✕</button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* rain chart */}
            <div className="h-32">
              <p className="text-[10px] font-black text-blue-500 uppercase mb-2">Rainfall (mm/h)</p>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[selectedHour]}>
                  <Bar dataKey="rain" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                  <YAxis hide domain={[0, 5]} />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-center font-bold text-slate-700 mt-2">{selectedHour.rain} mm</p>
            </div>
            
            {/* wind chart */}
            <div className="h-32">
              <p className="text-[10px] font-black text-rose-500 uppercase mb-2">Wind Speed (m/s)</p>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[selectedHour]}>
                  <Bar dataKey="wind" fill="#f43f5e" radius={[4, 4, 0, 0]} barSize={40} />
                  <YAxis hide domain={[0, 15]} />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-center font-bold text-slate-700 mt-2">{selectedHour.wind} m/s</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}