'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import { Search, MapPin, Navigation } from 'lucide-react';

const MapComponent = dynamic(() => import('./mapComponent'), { 
    ssr: false,
    loading: () => <div className="w-full h-full bg-slate-100 animate-pulse flex items-center justify-center text-slate-400">Loading Map...</div>
});

const OAK_PARK: [number, number] = [52.841, -6.926];

export default function Map() {
    const router = useRouter();
    const [position, setPosition] = useState<[number, number]>(OAK_PARK);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSearch, setIsSearch] = useState(false);

    // Eircode 
    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSearch(true);
        if (!searchQuery) return;

        setIsLoading(true);
        try {
            // Nominatim API
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${searchQuery}, Carlow, Ireland`);
            const data = await res.json();

            if (data && data.length > 0) {
                const { lat, lon } = data[0];
                setPosition([parseFloat(lat), parseFloat(lon)]);
            } else {
                alert("Location not found. Please check the address or Eircode.");
            }
        } catch (err) {
            console.error("Search error:", err);
            alert("An error occurred while searching.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSetPosition = (pos: [number, number]) => {
        setIsSearch(false);
        setPosition(pos);
    }

    return (
        <div className="flex flex-col lg:flex-row items-stretch justify-center gap-8 bg-white p-8 rounded-3xl shadow-2xl border border-slate-100 w-full max-w-6xl mx-auto">
            
            {/* left: map */}
            <div className="w-full lg:w-2/3 flex flex-col gap-4">
                <div className="flex flex-col gap-1">
                    <h2 className="text-2xl font-black text-slate-800 tracking-tight">Locate Your Farm</h2>
                    <p className="text-sm text-slate-500">Search by address or Eircode to pin your location in Carlow.</p>
                </div>

                {/* search bar */}
                <form onSubmit={handleSearch} className="relative flex gap-2">
                    <div className="relative flex-1">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                        <input 
                            type="text" 
                            placeholder="e.g. R93 E2R7 or College St, Carlow"
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none transition-all shadow-sm"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <button 
                        type="submit" 
                        disabled={isLoading}
                        className="bg-[#0782c5] text-white px-6 rounded-xl font-bold hover:bg-[#0671ab] transition-all disabled:opacity-50"
                    >
                        {isLoading ? 'Searching...' : 'Search'}
                    </button>
                </form>

                {/* actual map section */}
                <div className="relative w-full aspect-video lg:aspect-square rounded-2xl border border-slate-200 shadow-inner overflow-hidden z-0">
                    <MapComponent position={position} setPosition={setPosition} isSearch={isSearch}
                    />
                </div>
            </div>

            {/* right: info confirm */}
            <div className="flex-1 flex flex-col justify-between py-2 gap-6">
                <div className="space-y-6">
                    <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 shadow-sm">
                        <p className="text-blue-600 font-bold mb-4 text-xs tracking-widest uppercase">Target Region</p>
                        <h3 className="text-3xl font-black text-gray-900 flex items-center gap-3">
                            <Navigation className="text-blue-500" fill="currentColor" size={24} />
                            Carlow
                        </h3>
                        <div className="mt-4 pt-4 border-t border-blue-100 space-y-2">
                            <p className="text-xs text-slate-500 flex justify-between">
                                <span>Latitude:</span> <span className="font-mono font-bold text-slate-700">{position[0].toFixed(5)}</span>
                            </p>
                            <p className="text-xs text-slate-500 flex justify-between">
                                <span>Longitude:</span> <span className="font-mono font-bold text-slate-700">{position[1].toFixed(5)}</span>
                            </p>
                        </div>
                    </div>

                    <div className="p-5 border border-dashed border-amber-200 rounded-2xl bg-amber-50">
                        <p className="text-xs text-amber-700 font-medium leading-relaxed">
                            ⚠️ <b>Note:</b> NORA is currently optimised for the Carlow region. Weather forecast data will be fetched for your precise coordinates.
                        </p>
                    </div>
                </div>
                
                <button
                    onClick={() => router.push(`/analysis/Carlow?lat=${position[0]}&lng=${position[1]}`)}
                    className="w-full py-5 rounded-2xl text-xl font-bold bg-[#0782c5] hover:bg-[#0671ab] text-white shadow-xl transition-all active:scale-[0.98] flex items-center justify-center gap-2"
                >
                    <MapPin size={20} />
                    Confirm your location
                </button>
            </div>
        </div>
    );
}