import React, { useEffect, useState } from 'react'
import { Bell, RefreshCw } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'

const TYPE_ICON = {
  due_soon: '🟡', due_today: '🟠', overdue: '🔴', defect: '⚠️', assignment: '📋', approval: '✅', system: 'ℹ️',
}

export default function Notifications() {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = () => {
    setLoading(true)
    api.get('/notifications').then((res) => setNotes(res.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const refresh = async () => {
    setRefreshing(true)
    await api.post('/notifications/refresh')
    load()
    setRefreshing(false)
  }

  const markRead = async (id) => {
    await api.post(`/notifications/${id}/read`)
    load()
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-fire-800 flex items-center gap-2"><Bell /> Notifications</h1>
            <p className="text-slate-500 text-sm">Due-soon, overdue, and defect alerts</p>
          </div>
          <button onClick={refresh} disabled={refreshing} className="flex items-center gap-2 border rounded-lg px-3 py-2 text-sm font-semibold text-slate-600">
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>

        <div className="bg-white rounded-xl shadow divide-y">
          {loading && <div className="p-6 text-center text-slate-400">Loading...</div>}
          {!loading && notes.length === 0 && <div className="p-6 text-center text-slate-400">No notifications.</div>}
          {notes.map((n) => (
            <div key={n.id} onClick={() => markRead(n.id)} className={`p-4 flex items-start gap-3 cursor-pointer ${n.is_read ? 'opacity-60' : 'bg-fire-50/40'}`}>
              <div className="text-xl">{TYPE_ICON[n.type] || '🔔'}</div>
              <div className="flex-1">
                <div className="text-sm text-slate-800">{n.message}</div>
                <div className="text-xs text-slate-400 mt-1">{new Date(n.created_at).toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}
