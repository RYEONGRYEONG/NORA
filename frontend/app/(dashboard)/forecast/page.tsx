'use client'
import { useState, useEffect } from 'react';
import DailyWeather from '@/components/dailyWeather';
import HourlyWeather from '@/components/hourlyWeather';

export default function ForecastPage() {
  const [forecastData, setForecastData] = useState<{ daily: any[], hourly: any[] } | null>(null);
  const [loading, setLoading] = useState(true);

  const [targetDate, setTargetDate] = useState('');
  const [hourlyData, setHourlyData] = useState<any[]>([]);
  const [loadingHourly, setLoadingHourly] = useState(false);
  
  const URL = process.env.NEXT_PUBLIC_API_URL 
  const maxDate = new Date();
  maxDate.setDate(new Date().getDate() + 7);
  const maxDateStr = maxDate.toISOString().split('T')[0];

  useEffect(() => {
    const fetchForecast = async () => {
      const savedFarm = localStorage.getItem('selectedFarm');
      if (!savedFarm) {
        alert("Please select a farm first.");
        setLoading(false);
        return;
      }
      const farmId = JSON.parse(savedFarm).id;

      try {
        const response = await fetch(`${URL}/api/forecast?farm_id=${farmId}`);
        const result = await response.json();

        if (response.ok) {
          setForecastData(result);
        } else {
          console.error("Failed to fetch:", result);
        }
      } catch (error) {
        console.error("Connection error:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, [URL]);

  const handleAnalyse = async () => {
    if(!targetDate) return alert("Please select a target date.");
    const savedFarm = localStorage.getItem('selectedFarm');
    if (!savedFarm) return alert("Please select a farm first.");

    const farmId = JSON.parse(savedFarm).id;
    setLoadingHourly(true);

    try{
      const response = await fetch(`${URL}/api/hourly?farm_id=${farmId}&target_date=${targetDate}`);
      const result = await response.json();

      if (response.ok) {
        setHourlyData(result.hourly || []);
      } else{
        alert(result.message || "Failed to anlyse");
      } 
    } catch (error){
      alert("Connection error.");
    } finally {
      setLoadingHourly(false)
    }
  };

return (
    <div className="space-y-8 animate-in fade-in duration-500 p-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-slate-800">Weather Forecast & Risk Analyser</h1>
        <p className="text-sm text-slate-500 mt-1 italic font-bold">10-day summary and professional risk assessment</p>
      </div>
      
      {loading ? (
        <div className="mt-12 flex flex-col justify-center items-center h-64 bg-white rounded-3xl border border-slate-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#0782c5]"></div>
          <p className="ml-4 mt-4 text-slate-500 font-bold">Loading NORA data...</p>
        </div>
      ) : forecastData ? (
        <div className="mt-10 space-y-12">
          
          <DailyWeather data={forecastData.daily} />

          <div className="flex justify-between items-center bg-white p-10 rounded-[2.5rem] shadow-sm border-2 border-slate-100">
            <div className="flex flex-col gap-3">
              <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Risk Analyser</h2>
              <p className="text-xl font-bold text-slate-700">
                Evaluate <span className="text-rose-500 underline decoration-4 underline-offset-8">weather hazards</span> to find the safest day to spread.
              </p>
            </div>
            
            <div className="flex gap-4 items-center">
              <input 
                type="date" 
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                max={maxDateStr}
                className="p-4 border-4 border-slate-200 rounded-2xl text-xl font-black text-slate-800 focus:border-[#0782c5] outline-none transition-all"
              />
              <button 
                onClick={handleAnalyse}
                disabled={loadingHourly}
                className="bg-[#0782c5] text-white px-10 py-5 rounded-2xl text-2xl font-black hover:scale-105 active:scale-95 transition-all shadow-xl disabled:opacity-50 uppercase tracking-widest"
              >
                {loadingHourly ? "Analysing..." : "Analyse"}
              </button>
            </div>
          </div>

          {hourlyData.length > 0 ? (
            <HourlyWeather data={hourlyData} />
          ) : (
            <div className="p-10 text-center bg-slate-50 rounded-[2rem] border border-dashed border-slate-300">
              <p className="text-slate-400 font-bold italic text-lg">Select a date and click Analyse to see the safety strip.</p>
            </div>
          )}

        </div>
      ) : (
        <div className="p-6 bg-red-50 text-red-600 rounded-2xl">
          <p>Error loading weather data. Please try again.</p>
        </div>
      )}
    </div>
  );
}