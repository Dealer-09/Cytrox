import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { PlayCircle, Loader } from 'lucide-react'

export default function Scan() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/scan/repository', {
        repository_url: url,
      })
      navigate(`/scan/${response.data.scan_id}`)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to start scan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-slate-800 rounded-lg p-8 border border-slate-700">
        <h1 className="text-3xl font-bold text-white mb-2">Scan Repository</h1>
        <p className="text-gray-400 mb-8">Enter a GitHub repository URL to analyze for security vulnerabilities</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-300 font-semibold mb-2">Repository URL</label>
            <input
              type="url"
              placeholder="https://github.com/owner/repo"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {error && (
            <div className="bg-red-900 border border-red-700 rounded-lg p-3 text-red-200">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !url}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <PlayCircle className="w-5 h-5" />
                Start Scan
              </>
            )}
          </button>
        </form>

        <div className="mt-8 p-4 bg-slate-700 rounded-lg">
          <h3 className="text-white font-semibold mb-2">Supported Formats:</h3>
          <ul className="text-gray-300 space-y-1">
            <li>• GitHub repos (public & private with Premium)</li>
            <li>• GitLab repos</li>
            <li>• Any Git repository URL</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
