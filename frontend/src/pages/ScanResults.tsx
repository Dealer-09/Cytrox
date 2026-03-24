import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'
import { AlertTriangle, CheckCircle, Loader } from 'lucide-react'

export default function ScanResults() {
  const { id } = useParams<{ id: string }>()
  const [scan, setScan] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchResults()
    const interval = setInterval(fetchResults, 2000)
    return () => clearInterval(interval)
  }, [id])

  const fetchResults = async () => {
    try {
      const response = await api.get(`/scan/${id}`)
      setScan(response.data)
      if (response.data.status === 'COMPLETED') {
        setLoading(false)
      }
    } catch (error) {
      console.error('Failed to fetch results:', error)
    }
  }

  if (!scan) {
    return <div className="text-white p-8">Loading...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-white">{scan.repository_url}</h1>
          {scan.status === 'RUNNING' && <Loader className="w-8 h-8 text-blue-400 animate-spin" />}
        </div>
        
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-slate-700 rounded p-4">
            <p className="text-gray-400 mb-2">Risk Level</p>
            <p className={`text-2xl font-bold ${
              scan.risk_level === 'CRITICAL' ? 'text-red-400' :
              scan.risk_level === 'HIGH' ? 'text-orange-400' :
              scan.risk_level === 'MEDIUM' ? 'text-yellow-400' :
              'text-green-400'
            }`}>
              {scan.risk_level}
            </p>
          </div>
          <div className="bg-slate-700 rounded p-4">
            <p className="text-gray-400 mb-2">Risk Score</p>
            <p className="text-2xl font-bold text-white">{scan.risk_score}</p>
          </div>
          <div className="bg-slate-700 rounded p-4">
            <p className="text-gray-400 mb-2">Status</p>
            <p className="text-2xl font-bold text-white">{scan.status}</p>
          </div>
        </div>
      </div>

      {scan.findings?.findings?.length > 0 && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-700">
            <h2 className="text-xl font-bold text-white">{scan.findings.findings.length} Findings</h2>
          </div>
          
          <div className="space-y-4 p-6">
            {scan.findings.findings.map((finding: any, idx: number) => (
              <div key={idx} className="bg-slate-700 rounded p-4 border-l-4 border-red-500">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-white font-semibold">{finding.type}</h3>
                  <span className={`px-2 py-1 rounded text-sm font-semibold ${
                    finding.severity === 'CRITICAL' ? 'bg-red-900 text-red-200' :
                    finding.severity === 'HIGH' ? 'bg-orange-900 text-orange-200' :
                    finding.severity === 'MEDIUM' ? 'bg-yellow-900 text-yellow-200' :
                    'bg-gray-700 text-gray-200'
                  }`}>
                    {finding.severity}
                  </span>
                </div>
                <p className="text-gray-300 mb-2">{finding.message}</p>
                <p className="text-gray-400 text-sm mb-3">{finding.file_path}:{finding.line_number}</p>
                <div className="bg-slate-800 rounded p-2 mb-3 overflow-x-auto">
                  <code className="text-gray-300 text-sm">{finding.code_snippet}</code>
                </div>
                <p className="text-gray-400 italic">{finding.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {scan.status === 'COMPLETED' && (!scan.findings?.findings || scan.findings.findings.length === 0) && (
        <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
          <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">No Issues Found!</h2>
          <p className="text-gray-400">This repository passed security analysis.</p>
        </div>
      )}
    </div>
  )
}
