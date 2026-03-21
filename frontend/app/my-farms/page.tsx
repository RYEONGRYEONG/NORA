'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function MyFarmsPage() {
  const [farms, setFarms] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [currentFarmId, setCurrentFarmId] = useState<number | null>(null)
  const router = useRouter()
  const URL = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    const savedUser = localStorage.getItem('user') 
    const savedFarm = localStorage.getItem('selectedFarm')

    if (savedFarm) {
      setCurrentFarmId(JSON.parse(savedFarm).id)
    }
    
    if (!savedUser) {
      alert("Please sign in to view your farms.")
      return
    }

    const userEmail = JSON.parse(savedUser).email 

    const fetchFarms = async () => {
      try {
        const res = await fetch(`${URL}/api/farms?email=${userEmail}`)
        if (res.ok) {
          const data = await res.json()
          setFarms(data)
        } else {
          console.error("Failed to fetch from server")
        }
      } catch (error) {
        console.error("Connection error:", error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchFarms()
  }, [URL, router])

  const handleSelectFarm = async (farm: any) => {
    localStorage.setItem('selectedFarm', JSON.stringify(farm))
    setCurrentFarmId(farm.id)

    try {
      const res = await fetch(`${URL}/api/farms/select/${farm.id}`, { 
      method: 'POST' 
    })

    if (res.ok){
      console.log("Forecast synced for farm:", farm.id)
    }
    } catch (error) {
      console.error("Sync error:", error)
    }
  }

  const handleDeleteFarm = async (farmId: number) => {
    if (!confirm("Are you sure you want to delete this farm?")) return;

    try {
      const res = await fetch(`${URL}/api/farms/${farmId}`, { method: 'DELETE' })
      if (res.ok) {
        setFarms(farms.filter(f => f.id !== farmId))
        
        if (currentFarmId === farmId) {
          localStorage.removeItem('selectedFarm')
          setCurrentFarmId(null)
        }
        alert("Farm deleted successfully.")
      } else {
        alert("Failed to delete farm.")
      }
    } catch (error) {
      console.error("Delete error:", error)
    }
  }

  const sortedFarms = [...farms].sort((a, b) => {
    if (a.id === currentFarmId) return -1;
    if (b.id === currentFarmId) return 1;
    return 0;
  })

  return (
    <div className="min-h-screen bg-slate-50 p-10 animate-in fade-in duration-500">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-black text-slate-800 mb-2">My Farms</h1>
        <p className="text-slate-500 mb-10">Select a farm to analyse risks for fertiliser application</p>
        
        {loading ? (
          <div className="flex justify-center py-20">
            <p className="text-slate-400 font-bold animate-pulse">Loading your farms...</p>
          </div>
        ) : farms.length === 0 ? (
          <div className="bg-white p-10 rounded-3xl text-center shadow-sm border border-slate-100">
            <p className="text-slate-500 mb-4">No farms found. Please register a farm first!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedFarms.map((farm) => (
              <div 
                key={farm.id} 
                className={`bg-white p-8 rounded-3xl shadow-sm border flex flex-col justify-between transition-all ${
                  currentFarmId === farm.id ? 'border-[#0782c5] ring-2 ring-[#0782c5]/20' : 'border-slate-100 hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-2xl font-black text-slate-800 break-words pr-2">
                      {farm.farm_name}
                    </h3>
                    
                    {currentFarmId === farm.id && (
                      <span className="text-[10px] font-black uppercase tracking-wider bg-[#0782c5]/10 text-[#0782c5] px-2 py-1 rounded-full">
                        Current
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-slate-500 mb-6 flex items-center gap-1">
                    📍 {farm.location_name}
                  </p>

                  <p className="text-xs text-slate-400 font-mono mb-6 flex items-center gap-1">
                    Lat: {Number(farm.latitude).toFixed(4)} / Lng: {Number(farm.longitude).toFixed(4)}
                  </p>

                  <div className="inline-block px-3 py-1 bg-slate-100 text-slate-600 text-xs rounded-full font-bold">
                    {farm.soil_condition} Soil
                  </div>
                </div>
                
                <div className="flex gap-3 mt-8 pt-6 border-t border-slate-100">
                  <button 
                    onClick={() => handleSelectFarm(farm)}
                    className="flex-1 py-3 bg-[#0782c5] text-white rounded-xl font-bold hover:bg-[#0671ab] active:scale-[0.98] transition-all text-sm">
                    Select
                  </button>
                  <button 
                    onClick={() => handleDeleteFarm(farm.id)}
                    className="flex-1 py-3 bg-red-50 text-red-600 rounded-xl font-bold hover:bg-red-100 active:scale-[0.98] transition-all text-sm">
                    Delete
                  </button>
                </div>
                
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}