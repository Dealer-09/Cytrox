import React, { useEffect, useState } from 'react'
import api from '../api/client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Analytics() {
  const [trends, setTrends] = useState<any[]>([])
  const [topFindings, setTopFindings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const [trendsRes, findingsRes] = await Promise.all([
        api.get('/analytics/trends?days=30'),
        api.get('/analytics/top-findings')
      ])
      setTrends(trendsRes.data.trends)
      setTopFindings(findingsRes.data.top_findings)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-white p-8">Loading...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Analytics</h1>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Scanning Trends (Last 30 Days)</h2>
        {trends.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
              <Legend />
              <Line type="monotone" dataKey="scan_count" stroke="#3b82f6" name="Scans" />
              <Line type="monotone" dataKey="average_risk_score" stroke="#f59e0b" name="Avg Risk Score" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-400">No trend data available</p>
        )}
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">Top Findings</h2>
        {topFindings.length > 0 ? (
          <div className="space-y-3">
            {topFindings.map((finding, idx) => (
              <div key={idx} className="flex justify-between items-center bg-slate-700 p-3 rounded">
                <span className="text-gray-300">{finding.type}</span>
                <span className="bg-blue-600 text-white px-3 py-1 rounded">{finding.count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No findings data available</p>
        )}
      </div>
    </div>
  )
}
