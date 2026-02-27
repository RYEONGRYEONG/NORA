'use client';
import Map from './map'

export default function Home(){
    return(
        <main className="flex min-h-screen flex-col bg-slate-50">
<header className="w-full py-6 px-10 bg-white border-b border-slate-200 flex justify-between items-center shadow-sm">
                <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-black text-[#0782c5] tracking-[-0.1em] scale-y-110">NORA</h1>
                </div>
                <p className="text-sm text-slate-400 font-medium italic hidden md:block">
                    Dashboard
                </p>
            </header>

            <section className="flex-1 flex items-center justify-center p-6 md:p-12">
                <div className="w-full max-w-6xl h-full flex items-center justify-center">
                    <Map />
                </div>
            </section>
            
        </main>
    );
}