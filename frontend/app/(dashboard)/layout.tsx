'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [isMounted, setIsMounted] = useState(false)
  const [currentFarm, setCurrentFarm] = useState<any>(null);

  useEffect(() => {
    setIsMounted(true)
    const savedFarm = localStorage.getItem('selectedFarm');
    if (savedFarm) {
      setCurrentFarm(JSON.parse(savedFarm));
    }
  }, [pathname]);

  return (
    <div className="flex min-h-[calc(100vh-88px)] bg-slate-50">
      
      <aside className="w-80 bg-white border-r border-slate-200 shadow-sm p-8 flex flex-col shrink-0">
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Current Farm</h2>
        {!isMounted ? (
          <div className="h-44 bg-slate-100/50 rounded-2xl animate-pulse mb-8 border border-slate-100"></div>
        ) : currentFarm ? (
        
          <div className="bg-[#0782c5]/5 p-6 rounded-2xl border border-[#0782c5]/10 mb-8">
            <p className="text-2xl font-black text-slate-800 mb-1">{currentFarm.farm_name}</p>
            <p className="text-sm text-slate-500 flex items-center gap-1 mb-4">📍 {currentFarm.location_name}</p>
            <span className="inline-block px-3 py-1 bg-[#0782c5] text-white text-xs rounded-full font-bold">
              {currentFarm.soil_condition}
            </span>
          </div>
        ) : (
          <div className="bg-slate-100 p-6 rounded-2xl border border-slate-200 mb-8 text-center text-slate-500 text-sm flex flex-col justify-center h-44">
            <p className="font-bold text-slate-600 mb-1">No farm selected</p>
            <p>Please select a farm from My Farms.</p>
          </div>
        )}

        <nav className="flex flex-col gap-2">
          <Link href="/risk-analyser" 
            className={`p-4 rounded-2xl font-bold transition-all ${
              pathname === '/risk-analyser' ? 'bg-[#0782c5] text-white shadow-md' : 'text-slate-500 hover:bg-slate-100'
            }`}>
            Risk Analyser
          </Link>
          <Link href="/forecast" 
            className={`p-4 rounded-2xl font-bold transition-all ${
              pathname === '/forecast' ? 'bg-[#0782c5] text-white shadow-md' : 'text-slate-500 hover:bg-slate-100'
            }`}>
            Weather Forecast
          </Link>
          <Link href="/historical" 
            className={`p-4 rounded-2xl font-bold transition-all ${
              pathname === '/historical' ? 'bg-[#0782c5] text-white shadow-md' : 'text-slate-500 hover:bg-slate-100'
            }`}>
            Historical Data
          </Link>
        </nav>
      </aside>

      <main className="flex-1 p-10 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          {children}
        </div>
      </main>

    </div>
  )
}