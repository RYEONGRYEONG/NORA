'use client'
import { useState, useEffect } from 'react';
import HistoricalChart from '@/components/historicalChart'

export default function HistoricalPage() {
  const [data, setData] = useState<{ trend: any[], average: any } | null>(null);
  const [loading, setLoading] = useState(true);
  const URL = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const fetchHistorical = async () => {
      const savedFarm = localStorage.getItem('selectedFarm');
      if (!savedFarm) {
        alert("Please select a farm first.");
        setLoading(false);
        return;
      }
      const farmId = JSON.parse(savedFarm).id;

      try {
        const response = await fetch(`${URL}/api/historical?farm_id=${farmId}`);
        const result = await response.json();
        if (response.ok) {
          setData(result);
        }
      } catch (error) {
        console.error("Connection error:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistorical();
  }, [URL]);

  if (loading) return <div className="p-8 text-center text-slate-500 font-bold">Loading historical context...</div>;
  if (!data || !data.trend || data.trend.length === 0) return <div className="p-8 text-center text-red-500">No historical data found.</div>;

  const currentSMD = data.trend[data.trend.length - 1].smd;
  const avgSMD = data.average.smd;
  
  const isWetterThanNormal = currentSMD < avgSMD; 
  
  // trend in 3days if recoving or getting wetter
  const recentTrend = data.trend.slice(-3);
  const isDrying = recentTrend[0].smd < recentTrend[2].smd;

  return (
    <div className="space-y-8 animate-in fade-in duration-500 p-8">
      <div>
        <h1 className="text-3xl font-black text-slate-800">Historical Context</h1>
        <p className="text-sm text-slate-500 mt-1 italic font-bold">Compare current conditions with past trends</p>
      </div>

      {/* current vs normal */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-8 bg-white rounded-[2rem] border-2 border-slate-100 shadow-sm flex flex-col justify-center">
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Current Status</p>
          <div className="flex items-end gap-3">
            <span className="text-5xl font-black text-slate-800">{currentSMD.toFixed(1)} <span className="text-2xl text-slate-400">mm</span></span>
          </div>
          <p className="text-emerald-600 font-bold mt-4 bg-emerald-50 w-fit px-4 py-2 rounded-lg">
            Soil Moisture Deficit (Yesterday)
          </p>
        </div>

        <div className="p-8 bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 flex flex-col justify-center">
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">5-Year Monthly Average</p>
          <div className="flex items-end gap-3">
            <span className="text-5xl font-black text-slate-400">{avgSMD.toFixed(1)} <span className="text-2xl text-slate-300">mm</span></span>
          </div>
          <p className="text-slate-500 font-bold mt-4 bg-white w-fit px-4 py-2 rounded-lg shadow-sm">
            Typical conditions for this month
          </p>
        </div>
      </div>

      {/* chart */}
      <HistoricalChart trend={data?.trend || []} average={data?.average || {smd: 0, trend: 0 }}/>

      {/* actionable Insight */}
      <div className={`p-8 rounded-[2rem] border-l-[12px] shadow-sm ${isWetterThanNormal ? 'bg-amber-50 border-amber-400' : 'bg-emerald-50 border-emerald-400'}`}>
        <h3 className="text-2xl font-black mb-2 text-slate-800">System Verdict</h3>
        <p className="text-lg text-slate-700 font-medium leading-relaxed">
          The field is currently <strong className={isWetterThanNormal ? "text-amber-600 underline" : "text-emerald-600 underline"}>
            {isWetterThanNormal ? "wetter than typical" : "drier than typical"}
          </strong> for this time of year. 
          Recent data shows the soil is <strong className="text-slate-900">{isDrying ? "in a recovery (drying) phase" : "still degrading (getting wetter)"}</strong>.
        </p>
        <div className="mt-4 inline-block bg-white px-6 py-3 rounded-xl font-bold text-slate-800 shadow-sm border border-slate-200">
          Action: {
            isWetterThanNormal && !isDrying ? "Delay spreading. Waiting for a dry window is highly recommended." :
            isWetterThanNormal && isDrying ? "Wait 1-2 more days for optimal absorption as the soil is recovering." :
            "Conditions are favorable compared to historical norms. Proceed with standard precautions."
          }
        </div>
      </div>

    </div>
  );
}