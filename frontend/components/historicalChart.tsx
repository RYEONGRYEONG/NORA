'use client'
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { format, parseISO } from 'date-fns';

export default function HistoricalChart({ trend, average }: { trend: any[], average: any }) {
  const formattedData = (trend || []).map(item => ({
    ...item,
    displayDate: format(parseISO(item.date), 'dd/MM'),
    avgSmd: average?.smd || 0
  }));

  if (!trend || trend.length === 0) {
    return <div className="h-[400px] flex items-center justify-center bg-white rounded-[2rem]">No historical data available or no farm selected.</div>;
  }

  return (
    <div className="h-[400px] w-full bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm">
      <h3 className="text-xl font-bold text-slate-800 mb-6">14-Day Moisture & Rain Trend</h3>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={formattedData} margin={{ top: 10, right: 10, bottom: 20, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis 
            dataKey="displayDate" 
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            dy={10}
          />
          {/* left y axis: SMD */}
          <YAxis 
            yAxisId="left" 
            tick={{ fill: '#059669', fontSize: 12 }} 
            axisLine={false} 
            tickLine={false}
        />
        <Line 
            yAxisId="left" 
            type="monotone" 
            dataKey="avgSmd" 
            name="Average SMD (Historical)" 
            stroke="#94a3b8"  
            strokeDasharray="5 5" 
            dot={false} 
            strokeWidth={2} 
        />
          {/* right y axis: rain */}
          <YAxis 
            yAxisId="right" 
            orientation="right" 
            tick={{ fill: '#3b82f6', fontSize: 12 }} 
            axisLine={false} 
            tickLine={false}
          />
          <Tooltip 
            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }}/>
          
          {/* right: rain */}
          <Bar yAxisId="right" dataKey="rain" name="Rainfall (mm)" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={20} />
          {/* left: SMD */}
          <Line yAxisId="left" type="monotone" dataKey="smd" name="Soil Moisture Deficit (mm)" stroke="#059669" strokeWidth={4} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 8 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}