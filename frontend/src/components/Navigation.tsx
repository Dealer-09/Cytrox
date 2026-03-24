import React from 'react'
import { ShieldAlert, Menu, X } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useState } from 'react'

export default function Navigation() {
  const { logout } = useAuthStore()
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()

  const links = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/scan', label: 'New Scan' },
    { path: '/scan-history', label: 'History' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/team', label: 'Team' },
  ]

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/dashboard" className="flex items-center gap-2">
            <ShieldAlert className="w-8 h-8 text-blue-400" />
            <span className="text-xl font-bold text-white">RepoShield</span>
          </Link>

          {/* Desktop menu */}
          <div className="hidden md:flex items-center gap-8">
            {links.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-2 rounded transition ${
                  location.pathname === link.path
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition"
            >
              Logout
            </button>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-gray-300 hover:text-white"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            {links.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-slate-700 rounded"
                onClick={() => setIsOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={() => {
                logout()
                setIsOpen(false)
              }}
              className="w-full text-left px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
