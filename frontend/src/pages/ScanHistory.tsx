import React, { useEffect, useState } from 'react'
import api from '../api/client'
import { AlertTriangle, CheckCircle } from 'lucide-react'

interface ScanResult {
  id: number
  repository_url: string
  risk_level: string
  risk_score: number
  created_at: string
  status: string
}

export default function ScanHistory() {
  const [scans, setScans] = useState<ScanResult[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await api.get('/scan/history')
      setScans(response.data.scans)
    } catch (error) {
      console.error('Failed to fetch history:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'text-red-400 bg-red-900/30'
      case 'HIGH':
        return 'text-orange-400 bg-orange-900/30'
      case 'MEDIUM':
        return 'text-yellow-400 bg-yellow-900/30'
      case 'LOW':
        return 'text-blue-400 bg-blue-900/30'
      default:
        return 'text-green-400 bg-green-900/30'
    }
  }

  if (loading) {
    return <div className="text-white p-8">Loading...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Scan History</h1>

      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="px-6 py-4 text-left text-gray-300">Repository</th>
              <th className="px-6 py-4 text-left text-gray-300">Risk Level</th>
              <th className="px-6 py-4 text-left text-gray-300">Score</th>
              <th className="px-6 py-4 text-left text-gray-300">Status</th>
              <th className="px-6 py-4 text-left text-gray-300">Date</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr key={scan.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                <td className="px-6 py-4 text-gray-300 truncate">{scan.repository_url}</td>
                <td className={`px-6 py-4 font-semibold ${getRiskColor(scan.risk_level)}`}>
                  {scan.risk_level}
                </td>
                <td className="px-6 py-4 text-gray-300">{scan.risk_score}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded text-sm ${
                    scan.status === 'COMPLETED' ? 'bg-green-900/30 text-green-300' : 'bg-blue-900/30 text-blue-300'
                  }`}>
                    {scan.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-400">{new Date(scan.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
