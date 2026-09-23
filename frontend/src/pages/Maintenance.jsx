import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function Maintenance() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/maintenance').then((res) => setRecords(res.data)).finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1">Maintenance Records</h1>
        <p className="text-slate-500 text-sm mb-6">Complete refill/service history — records are never overwritten.</p>

        {loading && <div className="bg-white rounded-xl shadow px-4 py-6 text-center text-slate-400">Loading...</div>}
        {!loading && records.length === 0 && (
          <div className="bg-white rounded-xl shadow px-4 py-6 text-center text-slate-400">No maintenance records yet.</div>
        )}

        {/* Mobile: stacked cards */}
        {!loading && records.length > 0 && (
          <div className="md:hidden space-y-2">
            {records.map((r) => (
              <div key={r.id} className="bg-white rounded-xl shadow p-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-800 capitalize">{r.service_type}</span>
                  <span className="text-sm text-slate-500">{r.service_date}</span>
                </div>
                <div className="text-sm text-slate-600 mt-1">{r.service_provider || 'No provider recorded'}</div>
                <div className="flex items-center justify-between text-xs text-slate-400 mt-2">
                  <span>{r.technician ? `Technician: ${r.technician}` : ''}</span>
                  <span>{r.cost ? `$${r.cost}` : ''}</span>
                </div>
                {r.next_service_date && (
                  <div className="text-xs text-slate-400 mt-1">Next service: {r.next_service_date}</div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Desktop/tablet: full table */}
        {!loading && records.length > 0 && (
          <div className="hidden md:block bg-white rounded-xl shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
                <tr>
                  <th className="text-left px-4 py-3">Date</th>
                  <th className="text-left px-4 py-3">Type</th>
                  <th className="text-left px-4 py-3">Provider</th>
                  <th className="text-left px-4 py-3">Technician</th>
                  <th className="text-left px-4 py-3">Next Service</th>
                  <th className="text-left px-4 py-3">Cost</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id} className="border-t">
                    <td className="px-4 py-3">{r.service_date}</td>
                    <td className="px-4 py-3 capitalize">{r.service_type}</td>
                    <td className="px-4 py-3">{r.service_provider || '—'}</td>
                    <td className="px-4 py-3">{r.technician || '—'}</td>
                    <td className="px-4 py-3">{r.next_service_date || '—'}</td>
                    <td className="px-4 py-3">{r.cost ? `$${r.cost}` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  )
}
