'use client';
import { useState } from 'react';

interface SignModal {
  mode: 'login' | 'register';
  onClose: () => void;
  onLoginSuccess: (userData: any) => void;
}

export default function Sign({ mode, onClose, onLoginSuccess }: SignModal) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [job, setJob] = useState('');

  const URL = process.env.NEXT_PUBLIC_API_URL;

  console.log("API URL:", URL)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const endpoint = mode === 'login' ? '/login' : '/register';
    
    const payload = mode === 'login' 
      ? { email, password } 
      : { email, password, job };

    try {
      const response = await fetch(`${URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        if (mode == 'login'){
          localStorage.setItem('user', JSON.stringify(result.user));
          onLoginSuccess(result.user);
        }

        alert(result.message); 
        onClose();  
      } else {
        alert(result.message || "Something went wrong");
      }
    } catch (error) {
      console.error("Connection error:", error);
      alert("Failed to reach to the backend");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-in fade-in duration-200">
      <div className="bg-white p-8 rounded-2xl w-full max-w-md shadow-2xl relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors">✕</button>
        
        <h2 className="text-2xl font-bold mb-6 text-slate-800">
          {mode === 'login' ? 'Sign In to NORA' : 'Create Your Account'}
        </h2>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input 
            type="email" placeholder="Email Address" required
            className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            value={email} onChange={(e) => setEmail(e.target.value)}
          />
          <input 
            type="password" placeholder="Password" required
            className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            value={password} onChange={(e) => setPassword(e.target.value)}
          />
          
          {mode === 'register' && (
            <input 
              type="text" placeholder="Job (e.g. Farmer, Researcher)" required
              className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              value={job} onChange={(e) => setJob(e.target.value)}
            />
          )}

          <button 
            type="submit" 
            className="w-full py-3 bg-[#0782c5] text-white rounded-xl font-bold hover:bg-[#0671ab] active:scale-[0.98] transition-all mt-2"
          >
            {mode === 'login' ? 'Sign In' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  );
}