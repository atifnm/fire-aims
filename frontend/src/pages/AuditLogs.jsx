import React, { useEffect, useState } from 'react'
import { ScrollText } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function AuditLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/audit-logs').then((res) => setLogs(res.data)).finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1 flex items-center gap-2"><ScrollText /> Audit Logs</h1>
        <p className="text-slate-500 text-sm mb-6">Read-only record of every create/update/approval action in the system.</p>

        <div className="bg-white rounded-xl shadow divide-y">
          {loading && <div className="p-6 text-center text-slate-400">Loading...</div>}
          {!loading && logs.length === 0 && <div className="p-6 text-center text-slate-400">No audit entries yet.</div>}
          {logs.map((l) => (
            <div key={l.id} className="p-3 text-sm">
              <div className="text-slate-800">{l.action}</div>
              <div className="text-xs text-slate-400">{new Date(l.created_at).toLocaleString()} {l.entity_type ? `· ${l.entity_type} #${l.entity_id}` : ''}</div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}
