'use client';
import Map from './map'

export default function Home(){
    return(
        <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-50">
            <h1 className="text-4xl font-bold mb-10 text-blue-900">NORA</h1>
            <Map />
        </main>
    );
}

