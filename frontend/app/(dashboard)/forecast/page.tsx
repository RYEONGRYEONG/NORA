'use client'
import { useState, useEffect } from 'react';
import DailyWeather from '@/components/dailyWeather';
import HourlyWeather from '@/components/hourlyWeather';

export default function ForecastPage() {
  const [forecastData, setForecastData] = useState<{ daily: any[], hourly: any[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const URL = process.env.NEXT_PUBLIC_API_URL 

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
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 p-8">
      <div>
        <h1 className="text-3xl font-black text-slate-800">Weather Forecast</h1>
        <p className="text-sm text-slate-500 mt-1">10-day summary and detailed hourly timeline</p>
      </div>
      
      {loading ? (
        <div className="mt-12 flex flex-col justify-center items-center h-64 bg-white rounded-3xl border border-slate-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#0782c5]"></div>
          <p className="ml-4 mt-4 text-slate-500 font-bold">Loading forecast data...</p>
        </div>
      ) : forecastData ? (
        <div className="mt-10">
          <DailyWeather data={forecastData.daily} />
          <HourlyWeather data={forecastData.hourly} />
        </div>
      ) : (
        <div className="p-6 bg-red-50 text-red-600 rounded-2xl">
          <p>Error loading weather data. Please try again.</p>
        </div>
      )}
    </div>
  );
}