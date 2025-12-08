import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { auth, googleProvider } from './firebase';
import { signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';
import axios from 'axios';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Spending from './pages/Spending';


import Goals from './pages/Goals';
import Bills from './pages/Bills';
import Admin from './pages/Admin';
import Onboarding from './pages/Onboarding';
import Recommendations from './pages/Recommendations';
import Transactions from './pages/Transactions';
import Analytics from './pages/Analytics';
import Analysis from './pages/Analysis';
import Profile from './pages/Profile';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(true);
  const [onboardingComplete, setOnboardingComplete] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        syncUser(currentUser);
      } else {
        setLoading(false);
      }
    });
    return () => unsubscribe();
  }, []);

  const syncUser = async (currentUser) => {
    try {
      const token = await currentUser.getIdToken();
      const response = await axios.post(`${API_BASE}/sync-user`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOnboardingComplete(response.data.onboarding_completed);
    } catch (error) {
      console.error("Error syncing user:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (error) {
      console.error("Google Login Error:", error);
    }
  };

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    try {
      if (isSignUp) {
        await createUserWithEmailAndPassword(auth, email, password);
      } else {
        await signInWithEmailAndPassword(auth, email, password);
      }
    } catch (error) {
      console.error("Auth Error:", error);
      alert(error.message);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setOnboardingComplete(null);
  };

  if (loading) return <div className="flex justify-center items-center h-screen">Loading...</div>;

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-6 text-blue-600">FinPersonalize</h1>

          <div className="space-y-4">
            <button
              onClick={handleGoogleLogin}
              className="w-full bg-red-500 text-white py-2 rounded hover:bg-red-600 transition"
            >
              Sign in with Google
            </button>

            <div className="relative flex py-2 items-center">
              <div className="flex-grow border-t border-gray-300"></div>
              <span className="flex-shrink mx-4 text-gray-400">Or</span>
              <div className="flex-grow border-t border-gray-300"></div>
            </div>

            <form onSubmit={handleEmailAuth} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 block w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 block w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
              >
                {isSignUp ? 'Sign Up' : 'Sign In'}
              </button>
            </form>

            <div className="text-center text-sm">
              <button
                onClick={() => setIsSignUp(!isSignUp)}
                className="text-blue-600 hover:underline"
              >
                {isSignUp ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Force Onboarding if not complete */}
        {onboardingComplete === false && (
          <Route path="*" element={<Navigate to="/onboarding" replace />} />
        )}

        <Route path="/" element={<Layout user={user} onLogout={handleLogout} />}>
          <Route index element={<Dashboard user={user} />} />
          <Route path="spending" element={<Spending user={user} />} />
          <Route path="goals" element={<Goals user={user} />} />
          <Route path="bills" element={<Bills user={user} />} />
          <Route path="admin" element={<Admin />} />
          <Route path="transactions" element={<Transactions user={user} />} />
          <Route path="analytics" element={<Analytics user={user} />} />
          <Route path="recommendations" element={<Recommendations user={user} />} />
          <Route path="analysis" element={<Analysis user={user} />} />
          <Route path="profile" element={<Profile user={user} />} />
        </Route>
        <Route path="/onboarding" element={<Onboarding user={user} onComplete={() => setOnboardingComplete(true)} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
