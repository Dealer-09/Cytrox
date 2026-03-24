import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Github } from 'lucide-react'

export default function Auth() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Check if we're in the callback
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    
    if (code) {
      handleCallback(code)
    }
  }, [])

  const handleCallback = async (code: string) => {
    setLoading(true)
    try {
      await login(code)
      navigate('/dashboard')
    } catch (error) {
      console.error('Authentication failed')
      setLoading(false)
    }
  }

  const handleGitHubLogin = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
      const response = await fetch(`${apiUrl}/auth/github/login`)
      const data = await response.json()
      window.location.href = data.auth_url
    } catch (error) {
      console.error('Failed to initiate login')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">RepoShield-AI</h1>
          <p className="text-gray-400">Security analysis for your repositories</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-8 space-y-6">
          <p className="text-gray-300 text-center">
            Analyze your GitHub repositories for security vulnerabilities using AI-powered static analysis.
          </p>

          <button
            onClick={handleGitHubLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition"
          >
            <Github className="w-5 h-5" />
            {loading ? 'Authenticating...' : 'Login with GitHub'}
          </button>

          <div className="space-y-2 text-sm text-gray-400">
            <p>• Scan unlimited public repositories</p>
            <p>• Advanced security analysis</p>
            <p>• Real-time vulnerability detection</p>
          </div>
        </div>
      </div>
    </div>
  )
}
