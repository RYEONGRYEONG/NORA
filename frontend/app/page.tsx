'use client';
import Map from './map'

export default function Home(){
    return(
        <main className="flex min-h-screen flex-col bg-slate-50">
            <section className="flex-1 flex items-center justify-center p-6 md:p-12">
                <div className="w-full max-w-6xl h-full flex items-center justify-center">
                    <Map />
                </div>
            </section>
            
        </main>
    );
}