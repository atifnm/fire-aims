import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail
      if (status === 401 || status === 403) {
        // The backend actually evaluated the credentials and rejected them.
        setError(detail || 'Incorrect email or password.')
      } else if (detail) {
        // Some other backend-originated error with a real message (e.g. validation).
        setError(detail)
      } else {
        // Either no response reached us at all, or we got one with no useful body — the
        // most common cause by far is the backend not running / not reachable at the
        // proxied URL (in dev, a down backend surfaces as an empty 500 from Vite's proxy
        // itself, not a network error, so this has to be the fallback for both cases).
        setError("Can't reach the server. Make sure the backend is running (uvicorn) and reachable at http://localhost:8000, then try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-fire-900 px-4">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-2xl p-8">
        <div className="flex flex-col items-center mb-6">
          <img src="/brand/logo.svg" alt="Organization logo" className="w-40 h-auto mb-4" />
          <h1 className="text-2xl font-extrabold text-fire-800 tracking-wide">FIRE-AIMS</h1>
          <p className="text-xs text-slate-500 text-center mt-1">
            Fire Inspection, Recording &amp; Equipment Asset Information Management System
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fire-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-fire-500"
            />
          </div>
          {error && <div className="text-sm text-red-600">{error}</div>}
          <button
            type="submit" disabled={loading}
            className="w-full bg-fire-700 hover:bg-fire-800 text-white font-semibold py-2.5 rounded-lg disabled:opacity-60"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
