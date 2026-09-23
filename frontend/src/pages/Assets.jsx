import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Plus, Pencil, ChevronRight } from 'lucide-react'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { assetTypeLabel, assetTypeEmoji } from '../components/assetMeta'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import AssetFormModal from '../components/AssetFormModal'

export default function Assets() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [editingAsset, setEditingAsset] = useState(null)

  const load = () => {
    setLoading(true)
    const params = {}
    if (search) params.search = search
    if (typeFilter) params.asset_type = typeFilter
    if (statusFilter) params.status = statusFilter
    api.get('/assets', { params }).then((res) => setAssets(res.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [typeFilter, statusFilter])
  useEffect(() => {
    const t = setTimeout(load, 350)
    return () => clearTimeout(t)
  }, [search])

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <div>
            <h1 className="text-2xl font-bold text-fire-800">Assets</h1>
            <p className="text-slate-500 text-sm">{assets.length} equipment record(s)</p>
          </div>
          {user?.role === 'admin' && (
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 bg-fire-700 hover:bg-fire-800 text-white px-4 py-2 rounded-lg text-sm font-semibold"
            >
              <Plus size={16} /> Add Asset
            </button>
          )}
        </div>

        <div className="bg-white rounded-xl shadow p-3 mb-4 flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-3 text-slate-400" />
            <input
              value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Search asset ID, serial number, manufacturer..."
              className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-fire-500"
            />
          </div>
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="border rounded-lg px-3 py-2 text-sm">
            <option value="">All Types</option>
            <option value="extinguisher">🧯 Fire Extinguisher</option>
            <option value="hose_cabinet">🚒 Hose Cabinet</option>
            <option value="hose_reel">🌀 Hose Reel</option>
            <option value="branch">🔫 Branch/Nozzle</option>
            <option value="mcp">📟 MCP</option>
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="border rounded-lg px-3 py-2 text-sm">
            <option value="">All Statuses</option>
            <option value="compliant">🟢 Compliant</option>
            <option value="due_soon">🟡 Due Soon</option>
            <option value="due_today">🟠 Due Today</option>
            <option value="overdue">🔴 Overdue</option>
            <option value="defective">⚠️ Defective</option>
            <option value="under_maintenance">🔧 Under Maintenance</option>
            <option value="out_of_service">❌ Out of Service</option>
          </select>
        </div>

        {loading && <div className="bg-white rounded-xl shadow px-4 py-6 text-center text-slate-400">Loading...</div>}
        {!loading && assets.length === 0 && (
          <div className="bg-white rounded-xl shadow px-4 py-6 text-center text-slate-400">No assets found.</div>
        )}

        {/* Mobile: stacked cards — every field visible with no sideways scrolling. */}
        {!loading && assets.length > 0 && (
          <div className="md:hidden space-y-2">
            {assets.map((a) => (
              <div
                key={a.id} onClick={() => navigate(`/assets/${a.asset_id}`)}
                className="bg-white rounded-xl shadow p-4 active:bg-fire-50"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-semibold text-fire-800">{a.asset_id}</div>
                    <div className="text-sm text-slate-600">{assetTypeEmoji(a.asset_type)} {assetTypeLabel(a.asset_type)}</div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <StatusBadge status={a.status} />
                    {user?.role === 'admin' && (
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditingAsset(a) }}
                        title={`Edit ${a.asset_id}`}
                        className="text-slate-400 hover:text-fire-700 p-1"
                      >
                        <Pencil size={16} />
                      </button>
                    )}
                    <ChevronRight size={16} className="text-slate-300" />
                  </div>
                </div>
                <div className="text-sm text-slate-500 mt-2">{a.location_path || 'No location assigned'}</div>
                <div className="text-xs text-slate-400 mt-1">
                  Next inspection: {a.next_inspection_date ? new Date(a.next_inspection_date).toLocaleDateString() : '—'}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Desktop/tablet: full table. */}
        {!loading && assets.length > 0 && (
          <div className="hidden md:block bg-white rounded-xl shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
                <tr>
                  <th className="text-left px-4 py-3">Asset ID</th>
                  <th className="text-left px-4 py-3">Type</th>
                  <th className="text-left px-4 py-3">Location</th>
                  <th className="text-left px-4 py-3">Next Inspection</th>
                  <th className="text-left px-4 py-3">Status</th>
                  {user?.role === 'admin' && <th className="text-left px-4 py-3 w-12"></th>}
                </tr>
              </thead>
              <tbody>
                {assets.map((a) => (
                  <tr
                    key={a.id} onClick={() => navigate(`/assets/${a.asset_id}`)}
                    className="border-t hover:bg-fire-50 cursor-pointer"
                  >
                    <td className="px-4 py-3 font-semibold text-fire-800">{a.asset_id}</td>
                    <td className="px-4 py-3">{assetTypeEmoji(a.asset_type)} {assetTypeLabel(a.asset_type)}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{a.location_path || '—'}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {a.next_inspection_date ? new Date(a.next_inspection_date).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                    {user?.role === 'admin' && (
                      <td className="px-4 py-3">
                        <button
                          onClick={(e) => { e.stopPropagation(); setEditingAsset(a) }}
                          title={`Edit ${a.asset_id}`}
                          className="text-slate-400 hover:text-fire-700"
                        >
                          <Pencil size={15} />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreate && (
        <AssetFormModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); load() }} />
      )}
      {editingAsset && (
        <AssetFormModal
          existingAsset={editingAsset}
          onClose={() => setEditingAsset(null)}
          onCreated={() => { setEditingAsset(null); load() }}
        />
      )}
    </Layout>
  )
}
