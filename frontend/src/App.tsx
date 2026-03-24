import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Navigation from './components/Navigation'
import Dashboard from './pages/Dashboard'
import Scan from './pages/Scan'
import ScanHistory from './pages/ScanHistory'
import ScanResults from './pages/ScanResults'
import Auth from './pages/Auth'
import Analytics from './pages/Analytics'
import Team from './pages/Team'
import './App.css'

export default function App() {
  const { isAuthenticated, checkAuth } = useAuthStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 mb-4 bg-blue-600 rounded-full animate-pulse"></div>
          <p className="text-white">Loading RepoShield...</p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      {isAuthenticated ? (
        <div className="min-h-screen bg-slate-900">
          <Navigation />
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/scan" element={<Scan />} />
            <Route path="/scan-history" element={<ScanHistory />} />
            <Route path="/scan/:id" element={<ScanResults />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/team" element={<Team />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      ) : (
        <Routes>
          <Route path="/auth" element={<Auth />} />
          <Route path="*" element={<Navigate to="/auth" />} />
        </Routes>
      )}
    </BrowserRouter>
  )
}