'use client'
import { useState, useEffect } from 'react'
import Sign from './sign'

export default function Navbar() {
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
  };

  return (
    <header className="w-full py-6 px-10 bg-white border-b border-slate-200 flex justify-between items-center shadow-sm">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-thin text-[#0782c5] tracking-tighter">NORA</h1>
      </div>

      <div className="flex gap-4">
        {user ? (
          <div className="flex gap-4 items-center">
            <span className="text-slate-600 font-medium">
              Welcome, <span className="text-[#0782c5]">{user.email}</span>!
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-400 hover:text-red-500 transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={() => setModalMode('login')}
              className="text-slate-600 font-medium hover:text-[#0782c5] transition-colors"
            >
              Sign In
            </button>
            <button
              onClick={() => setModalMode('register')}
              className="bg-[#0782c5] text-white px-5 py-2 rounded-lg hover:bg-[#0671ab] transition-all shadow-md active:scale-95"
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
          onLoginSuccess={(userData) => setUser(userData)}
        />
      )}
    </header>
  );
}