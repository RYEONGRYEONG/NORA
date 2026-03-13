'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import Sign from './sign'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

export default function Navbar() {
  const router = useRouter();
  const [modalMode, setModalMode] = useState<'login' | 'register' | null>(null);
  const [user, setUser] = useState<{ email: string, job: string } | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    alert("Logged out");
    router.push('/');
  };

  const handleAccess = (e: React.MouseEvent, path: string) => {
    if (!user) {
      e.preventDefault();
      alert("This feature is for members only.\n Please login first.")
    }
  };

  return (
    <header className="w-full h-16 px-10 bg-white border-b border-slate-200 flex justify-between items-center shadow-sm sticky top-0 z-50">
      <div className="flex items-center gap-10">
        <h1 className="flex items-center gap-2 cursor-pointer" onClick={() => router.push('/')}>
          <Image
            src="/logo.png"
            alt="NORA"
            width={120}
            height={40}
            className="object-contain"
            />
        </h1>

        <nav className="hidden md:flex items-center gap-8 text-sm font-bold text-slate-500">
          <Link href="/historical" className="hover:text-[#0782c5] transition-colors">
          Historical
          </Link>

          <Link 
            href="/forecast" 
            onClick={(e) => handleAccess(e, '/forecast')}
            className="hover:text-[#0782c5] transition-colors flex items-center gap-1"
          >
            Forecast
          </Link>

          <Link 
            href="/risk-analyser" 
            onClick={(e) => handleAccess(e, '/risk-analyser')}
            className="hover:text-[#0782c5] transition-colors flex items-center gap-1"
          >
            Risk Analyser
          </Link>

          <Link 
            href="/my-farms" 
            onClick={(e) => handleAccess(e, '/my-farms')}
            className="hover:text-[#0782c5] transition-colors flex items-center gap-1"
          >
            My Farms
          </Link>
        </nav>
      </div>
      
      <div className="flex gap-4">
        {user ? (
          <div className="flex gap-4 items-center">
            <span className="text-slate-500 text-xs">
              Welcome <span className="text-[#0782c5] font-bold">{user.email}</span>
            </span>
            <button
              onClick={handleLogout}
              className="text-xs text-slate-400 hover:text-red-500 transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={() => setModalMode('login')}
              className="text-slate-600 font-medium hover:text-[#0782c5] transition-colors text-sm"
            >
              Sign In
            </button>
            <button
              onClick={() => setModalMode('register')}
              className="bg-[#0782c5] text-white px-5 py-2 rounded-lg hover:bg-[#0671ab] transition-all shadow-md active:scale-95 text-sm font-bold"
            >
              Register
            </button>
          </>
        )}
      </div>

      {modalMode && (
        <Sign
          mode={modalMode}
          onClose={() => setModalMode(null)}
          onLoginSuccess={(userData) => { 
            setUser(userData); 
            setModalMode(null);}}
        />
      )}
    </header>
  );
}