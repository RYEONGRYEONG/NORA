'use client'
import React from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export default function HourlyWeather({ data }: { data: any[] }) {
  if (!data || data.length === 0) return null;

  const chartWidth = Math.max(800, data.length * 40);

  return (
    <div className="w-full bg-white p-6 rounded-3xl shadow-sm border border-slate-100 overflow-x-auto custom-scrollbar">
      <h2 className="text-xl font-black text-slate-800 mb-6">Hourly Weather Timeline</h2>
      
      <div style={{ width: `${chartWidth}px`, height: '400px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12, fill: '#64748b' }} 
              interval="preserveStartEnd" 
              minTickGap={30}
              tickFormatter={(str) => format(new Date(str), 'MMM dd HH:mm')} 
            />
            
            <YAxis yAxisId="left" orientation="left" stroke="#3b82f6" label={{ value: 'Rain (mm)', angle: -90, position: 'insideLeft', fill: '#3b82f6' }} />
            <YAxis yAxisId="right" orientation="right" stroke="#ef4444" label={{ value: 'Temp (°C)', angle: 90, position: 'insideRight', fill: '#ef4444' }} />
            
            <Tooltip 
              labelFormatter={(label) => format(new Date(label), 'MMM dd, yyyy HH:mm')}
              contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} 
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />

            <Bar yAxisId="left" dataKey="rain" fill="#3b82f6" barSize={8} name="Rainfall (mm)" radius={[2, 2, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="temp" stroke="#ef4444" strokeWidth={3} name="Temperature (°C)" dot={false} connectNulls={true} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}