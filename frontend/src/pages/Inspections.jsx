import React, { useEffect, useState } from 'react'
import { ShieldAlert } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import InspectionCorrectionModal from '../components/InspectionCorrectionModal'

const RESULT_COLORS = {
  pass: 'bg-green-100 text-green-800',
  pass_with_observation: 'bg-yellow-100 text-yellow-800',
  requires_maintenance: 'bg-orange-100 text-orange-800',
  failed: 'bg-red-100 text-red-800',
}

export default function Inspections() {
  const { user } = useAuth()
  const [inspections, setInspections] = useState([])
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [correcting, setCorrecting] = useState(null)

  const load = () => {
    setLoading(true)
    const params = {}
    if (statusFilter) params.status = statusFilter
    api.get('/inspections', { params }).then((res) => setInspections(res.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [statusFilter])

  const review = async (id, approve) => {
    await api.post(`/inspections/${id}/review`, { approve })
    load()
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-fire-800">Inspections</h1>
            <p className="text-slate-500 text-sm">
              {user?.role === 'inspector' ? 'Your submitted inspections' : 'All submitted inspections'}
            </p>
          </div>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="border rounded-lg px-3 py-2 text-sm">
            <option value="">All</option>
            <option value="submitted">Pending Review</option>
            <option value="approved">Approved</option>
            <option value="returned">Returned</option>
          </select>
        </div>

        <div className="bg-white rounded-xl shadow divide-y">
          {loading && <div className="p-6 text-center text-slate-400">Loading...</div>}
          {!loading && inspections.length === 0 && <div className="p-6 text-center text-slate-400">No inspections found.</div>}
          {inspections.map((i) => (
            <div key={i.id} className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-800">Inspection #{i.id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${RESULT_COLORS[i.overall_result]}`}>
                    {i.overall_result.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  {new Date(i.inspected_at).toLocaleString()} · Status: {i.status}
                </div>
                {i.general_remarks && <div className="text-sm text-slate-600 mt-1">{i.general_remarks}</div>}
              </div>
              <div className="flex gap-2">
                {(user?.role === 'admin' || user?.role === 'supervisor') && i.status === 'submitted' && (
                  <>
                    <button onClick={() => review(i.id, true)} className="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg font-semibold">Approve</button>
                    <button onClick={() => review(i.id, false)} className="text-xs border border-red-300 text-red-600 px-3 py-1.5 rounded-lg font-semibold">Return</button>
                  </>
                )}
                {user?.role === 'admin' && (
                  <button
                    onClick={() => setCorrecting(i)}
                    title="Admin-only correction of this inspection's content"
                    className="flex items-center gap-1 text-xs border border-gold-400 text-gold-700 px-3 py-1.5 rounded-lg font-semibold hover:bg-gold-50"
                  >
                    <ShieldAlert size={13} /> Correct
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {correcting && (
        <InspectionCorrectionModal
          inspection={correcting}
          onClose={() => setCorrecting(null)}
          onSaved={() => { setCorrecting(null); load() }}
        />
      )}
    </Layout>
  )
}
