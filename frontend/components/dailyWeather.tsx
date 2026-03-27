'use client'
import React from 'react';
import { format } from 'date-fns';

export default function DailyWeather({ data }: { data: any[] }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="w-full bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-8">
      <h2 className="text-xl font-black text-slate-800 mb-5">8-Day Summary</h2>
      
      <div className="flex space-x-4 overflow-x-auto pb-4 custom-scrollbar">
        {data.map((day, index) => {
          const dateObj = new Date(day.date);
          let icon = '☀️'; // default

          if (day.rain > 10.0){
            icon = '⛈️';
          }
          else if (day.rain >= 7.0){
            icon = '🌧️⚠️';
          }
          else if (day.rain >= 3.0){
            icon = '🌧️';
          }
          else if (day.rain >= 1.0){
            icon = '🌦️';
          }
          else if (day.rain > 0){
            icon = '💧';
          }

          return (
            <div key={index} className="flex-none w-36 bg-slate-50 p-5 rounded-2xl border border-slate-100 text-center">
              <p className="text-xs font-bold text-[#0782c5] uppercase">{format(dateObj, 'EEE')}</p>
              <p className="text-xl font-black text-slate-900 mt-1">{format(dateObj, 'MMM dd')}</p>
              
              <div className="text-4xl my-4">{icon}</div>
              
              <div className="flex justify-center space-x-2 text-sm">
                <span className="font-bold text-slate-800">{day.max.toFixed(1)}°</span>
                <span className="text-slate-400">{day.min.toFixed(1)}°</span>
              </div>
              <p className="text-xs text-[#0782c5] font-semibold mt-2">{day.rain > 0 ? `${day.rain}mm` : 'No rain'}</p> 
            </div>
          );
        })}
      </div>
    </div>
  );
}