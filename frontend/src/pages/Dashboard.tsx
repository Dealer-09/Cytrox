import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../api/client'
import { Activity, TrendingUp, AlertCircle } from 'lucide-react'

interface DashboardData {
  total_scans: number
  average_risk_score: number
  risk_distribution: Record<string, number>
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const response = await api.get('/analytics/dashboard')
      setData(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-white p-8">Loading...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome, {user?.username}!</h1>
        <p className="text-gray-400">Let's keep your repositories secure</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Total Scans</h3>
            <Activity className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-3xl font-bold text-white">{data?.total_scans || 0}</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Average Risk Score</h3>
            <TrendingUp className="w-5 h-5 text-yellow-400" />
          </div>
          <p className="text-3xl font-bold text-white">{Math.round(data?.average_risk_score || 0)}</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Subscription</h3>
            <AlertCircle className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-3xl font-bold text-white">{user?.subscription_tier}</p>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/scan')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition"
          >
            Start New Scan
          </button>
          <button
            onClick={() => navigate('/scan-history')}
            className="bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 px-4 rounded-lg transition"
          >
            View Scan History
          </button>
        </div>
      </div>

      {data?.risk_distribution && Object.keys(data.risk_distribution).length > 0 && (
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-bold text-white mb-4">Risk Distribution</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(data.risk_distribution).map(([level, count]: [string, any]) => (
              <div key={level} className="bg-slate-700 rounded p-4 text-center">
                <p className="text-gray-400 mb-2">{level}</p>
                <p className="text-2xl font-bold text-white">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  }
}

// Remove the incomplete button tag that was cut off
            onClick={() => navigate('/analytics')}
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-4 rounded-lg transition"
          >
            View Analytics
          </button>
        </div>
      </div>
    </div>
  )
}
