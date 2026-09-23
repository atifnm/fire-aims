import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import Layout from '../components/Layout'
import api from '../api/client'
import { assetTypeLabel, assetTypeEmoji } from '../components/assetMeta'

const STATUS_COLORS = {
  compliant: '#16a34a', due_soon: '#eab308', due_today: '#f97316',
  overdue: '#dc2626', defective: '#dc2626', under_maintenance: '#2563eb', out_of_service: '#6b7280',
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.get('/dashboard/summary'), api.get('/dashboard/analytics')])
      .then(([s, a]) => { setSummary(s.data); setAnalytics(a.data) })
      .finally(() => setLoading(false))
  }, [])

  if (loading || !summary) {
    return <Layout><div className="p-8 text-slate-500">Loading dashboard...</div></Layout>
  }

  const statusData = Object.entries(summary.by_status)
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: k, value: v }))

  const typeData = Object.entries(summary.by_type).map(([k, v]) => ({ name: assetTypeLabel(k), count: v }))

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1">Dashboard</h1>
        <p className="text-slate-500 text-sm mb-6">Fleet-wide fire safety equipment overview</p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <SummaryCard label="Total Assets" value={summary.total_assets} accent="fire" />
          <SummaryCard label="Compliance" value={`${summary.compliance_percentage}%`} accent="green" />
          <SummaryCard label="Overdue" value={summary.overdue} accent="red" />
          <SummaryCard label="Defective" value={summary.defective} accent="red" />
          <SummaryCard label="Due Within 30 Days" value={summary.due_within_30_days} accent="yellow" />
          <SummaryCard label="Open Defects" value={summary.open_defects} accent="orange" />
          <SummaryCard label="Critical Defects" value={summary.critical_defects} accent="red" />
          <SummaryCard label="Buildings" value={summary.total_buildings} accent="fire" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          {Object.entries(summary.by_type).map(([type, count]) => (
            <div key={type} className="bg-white rounded-xl shadow p-4 flex items-center gap-3">
              <div className="text-2xl">{assetTypeEmoji(type)}</div>
              <div>
                <div className="text-xl font-bold text-fire-800">{count}</div>
                <div className="text-xs text-slate-500">{assetTypeLabel(type)}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Equipment by Status</h2>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" outerRadius={90} label>
                  {statusData.map((entry, i) => (
                    <Cell key={i} fill={STATUS_COLORS[entry.name] || '#94a3b8'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Equipment by Type</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={60} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#0f3d24" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Equipment by Building</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={analytics?.equipment_by_building || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="building" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#c9a227" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Inspections per Month</h2>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={analytics?.inspections_per_month || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#0f3d24" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {analytics && (
          <div className="grid grid-cols-3 gap-3 mt-4">
            <SummaryCard label="Failed Inspections (all-time)" value={analytics.failed_inspections} accent="red" small />
            <SummaryCard label="Maintenance Activities" value={analytics.maintenance_activities} accent="fire" small />
            <SummaryCard label="Overdue Now" value={analytics.overdue_count} accent="red" small />
          </div>
        )}
      </div>
    </Layout>
  )
}

function SummaryCard({ label, value, accent, small }) {
  const accentMap = {
    fire: 'text-fire-700', green: 'text-green-600', red: 'text-red-600',
    yellow: 'text-yellow-600', orange: 'text-orange-600',
  }
  return (
    <div className="bg-white rounded-xl shadow p-4">
      <div className={`font-bold ${small ? 'text-xl' : 'text-2xl'} ${accentMap[accent] || 'text-slate-800'}`}>{value}</div>
      <div className="text-xs text-slate-500 mt-1">{label}</div>
    </div>
  )
}
