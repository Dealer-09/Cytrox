import React, { useEffect, useState } from 'react'
import { Users, Plus } from 'lucide-react'
import api from '../api/client'

interface Team {
  id: number
  name: string
  description: string
  member_count: number
  created_at: string
}

export default function Team() {
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [newTeamName, setNewTeamName] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTeams()
  }, [])

  const fetchTeams = async () => {
    try {
      const response = await api.get('/teams')
      setTeams(response.data.teams || [])
    } catch (err) {
      console.error('Failed to fetch teams:', err)
      setError('Failed to load teams')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTeamName.trim()) return

    setCreating(true)
    setError('')
    try {
      await api.post('/teams', { name: newTeamName })
      setNewTeamName('')
      await fetchTeams()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create team')
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return <div className="text-white p-8">Loading teams...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Team Management</h1>
      
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Create New Team</h2>
        <form onSubmit={handleCreateTeam} className="flex gap-2">
          <input
            type="text"
            placeholder="Team name"
            value={newTeamName}
            onChange={(e) => setNewTeamName(e.target.value)}
            disabled={creating}
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={creating || !newTeamName.trim()}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            <Plus className="w-5 h-5" />
            Create
          </button>
        </form>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>

      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Your Teams</h2>
        {teams.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {teams.map((team) => (
              <div key={team.id} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-blue-500 rounded-lg p-3">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white">{team.name}</h3>
                </div>
                <p className="text-gray-400 mb-4">{team.description || 'No description'}</p>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">{team.member_count} members</span>
                  <span className="text-sm text-gray-500">{new Date(team.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
            <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No teams yet. Create one to get started!</p>
          </div>
        )}
      </div>
    </div>
  )
}
