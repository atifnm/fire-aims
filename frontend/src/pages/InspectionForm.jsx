import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Camera, CheckCircle2, XCircle, MinusCircle } from 'lucide-react'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { assetTypeLabel, assetTypeEmoji } from '../components/assetMeta'
import api from '../api/client'
import { queueInspection } from '../api/offlineQueue'

const RESULT_OPTIONS = [
  { value: 'pass', label: 'PASS' },
  { value: 'pass_with_observation', label: 'PASS WITH OBSERVATION' },
  { value: 'requires_maintenance', label: 'REQUIRES MAINTENANCE' },
  { value: 'failed', label: 'FAILED / REMOVE FROM SERVICE' },
]

export default function InspectionForm() {
  const { assetCode } = useParams()
  const navigate = useNavigate()
  const [asset, setAsset] = useState(null)
  const [checklist, setChecklist] = useState(null)
  const [itemResults, setItemResults] = useState({})
  const [overallResult, setOverallResult] = useState('pass')
  const [generalRemarks, setGeneralRemarks] = useState('')
  const [defectDescription, setDefectDescription] = useState('')
  const [correctiveAction, setCorrectiveAction] = useState('')
  const [defectSeverity, setDefectSeverity] = useState('medium')
  const [photoFile, setPhotoFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)
  const [offline, setOffline] = useState(false)

  useEffect(() => {
    api.get(`/assets/scan/${assetCode}`).then(async (res) => {
      setAsset(res.data)
      const cl = await api.get('/checklists', { params: { asset_type: res.data.asset_type } })
      if (cl.data.length > 0) {
        setChecklist(cl.data[0])
        const initial = {}
        cl.data[0].items.forEach((it) => { initial[it.id] = { result: 'pass', remarks: '' } })
        setItemResults(initial)
      }
    })
  }, [assetCode])

  const setItemResult = (id, field, value) => {
    setItemResults((prev) => ({ ...prev, [id]: { ...prev[id], [field]: value } }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    const items = checklist
      ? checklist.items.map((it) => ({
          section: it.section, label: it.label,
          result: itemResults[it.id]?.result || 'pass',
          remarks: itemResults[it.id]?.remarks || null,
        }))
      : []

    const payload = {
      asset_id: asset.id,
      checklist_template_id: checklist?.id || null,
      overall_result: overallResult,
      general_remarks: generalRemarks || null,
      defect_description: ['requires_maintenance', 'failed'].includes(overallResult) ? (defectDescription || null) : null,
      corrective_action: ['requires_maintenance', 'failed'].includes(overallResult) ? (correctiveAction || null) : null,
      defect_severity: ['requires_maintenance', 'failed'].includes(overallResult) ? defectSeverity : null,
      items,
    }

    try {
      if (!navigator.onLine) throw new Error('offline')
      const res = await api.post('/inspections', payload)
      if (photoFile) {
        const form = new FormData()
        form.append('asset_id', asset.id)
        form.append('context', ['requires_maintenance', 'failed'].includes(overallResult) ? 'defect' : 'general')
        form.append('inspection_id', res.data.id)
        form.append('file', photoFile)
        await api.post('/photos', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      }
      setDone(true)
      setTimeout(() => navigate(`/assets/${asset.asset_id}`), 1200)
    } catch (err) {
      if (!navigator.onLine || err.message === 'offline') {
        queueInspection(payload)
        setOffline(true)
        setDone(true)
        setTimeout(() => navigate(`/assets/${asset.asset_id}`), 1500)
      } else {
        setError(err.response?.data?.detail || 'Failed to submit inspection')
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (!asset) {
    return <Layout><div className="p-8 text-slate-500">Loading equipment...</div></Layout>
  }

  if (done) {
    return (
      <Layout>
        <div className="p-8 max-w-md mx-auto text-center">
          <CheckCircle2 className="mx-auto text-green-600 mb-3" size={48} />
          <h2 className="text-xl font-bold text-slate-800">
            {offline ? 'Saved offline — will sync automatically' : 'Inspection submitted'}
          </h2>
          <p className="text-slate-500 text-sm mt-1">Redirecting to {asset.asset_id}...</p>
        </div>
      </Layout>
    )
  }

  const groupedItems = {}
  if (checklist) {
    checklist.items.forEach((it) => {
      const section = it.section || 'General'
      if (!groupedItems[section]) groupedItems[section] = []
      groupedItems[section].push(it)
    })
  }

  const needsDefect = ['requires_maintenance', 'failed'].includes(overallResult)

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto pb-24">
        <div className="bg-white rounded-xl shadow p-4 mb-4 flex items-center justify-between">
          <div>
            <div className="font-bold text-fire-800">{asset.asset_id}</div>
            <div className="text-sm text-slate-500">{assetTypeEmoji(asset.asset_type)} {assetTypeLabel(asset.asset_type)} · {asset.location_path}</div>
          </div>
          <StatusBadge status={asset.status} />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {checklist ? (
            Object.entries(groupedItems).map(([section, items]) => (
              <div key={section} className="bg-white rounded-xl shadow p-4">
                <h3 className="font-semibold text-slate-700 mb-3">{section}</h3>
                <div className="space-y-3">
                  {items.map((it) => (
                    <div key={it.id} className="border-b last:border-b-0 pb-3 last:pb-0">
                      <div className="text-sm text-slate-700 mb-2">{it.label}</div>
                      <div className="flex gap-2">
                        <ResultChip icon={CheckCircle2} label="Pass" active={itemResults[it.id]?.result === 'pass'} color="green" onClick={() => setItemResult(it.id, 'result', 'pass')} />
                        <ResultChip icon={XCircle} label="Fail" active={itemResults[it.id]?.result === 'fail'} color="red" onClick={() => setItemResult(it.id, 'result', 'fail')} />
                        <ResultChip icon={MinusCircle} label="N/A" active={itemResults[it.id]?.result === 'not_applicable'} color="gray" onClick={() => setItemResult(it.id, 'result', 'not_applicable')} />
                      </div>
                      {itemResults[it.id]?.result === 'fail' && (
                        <input
                          placeholder="Remarks (optional)"
                          value={itemResults[it.id]?.remarks || ''}
                          onChange={(e) => setItemResult(it.id, 'remarks', e.target.value)}
                          className="w-full mt-2 border rounded-lg px-3 py-1.5 text-sm"
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="bg-yellow-50 text-yellow-800 rounded-xl p-4 text-sm">
              No checklist template configured for this equipment type. You can still submit an overall result and remarks below.
            </div>
          )}

          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-semibold text-slate-700 mb-3">Overall Result</h3>
            <div className="grid grid-cols-1 gap-2">
              {RESULT_OPTIONS.map((opt) => (
                <label key={opt.value} className={`flex items-center gap-2 border rounded-lg px-3 py-2 cursor-pointer text-sm ${overallResult === opt.value ? 'border-fire-600 bg-fire-50 font-semibold text-fire-800' : 'border-slate-200'}`}>
                  <input type="radio" name="overallResult" value={opt.value} checked={overallResult === opt.value} onChange={() => setOverallResult(opt.value)} />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-4">
            <label className="text-sm font-medium text-slate-700">General Remarks</label>
            <textarea value={generalRemarks} onChange={(e) => setGeneralRemarks(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>

          {needsDefect && (
            <div className="bg-red-50 rounded-xl shadow p-4 space-y-3">
              <h3 className="font-semibold text-red-800">Defect / Corrective Action</h3>
              <div>
                <label className="text-sm font-medium text-slate-700">Defect Description</label>
                <textarea value={defectDescription} onChange={(e) => setDefectDescription(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} required />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Corrective Action</label>
                <textarea value={correctiveAction} onChange={(e) => setCorrectiveAction(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Risk Priority</label>
                <select value={defectSeverity} onChange={(e) => setDefectSeverity(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>
          )}

          <div className="bg-white rounded-xl shadow p-4">
            <label className="text-sm font-medium text-slate-700 flex items-center gap-2 mb-2">
              <Camera size={16} /> Photo Evidence (optional)
            </label>
            <input type="file" accept="image/*" capture="environment" onChange={(e) => setPhotoFile(e.target.files[0])} className="text-sm" />
          </div>

          {error && <div className="text-sm text-red-600">{String(error)}</div>}

          <button type="submit" disabled={submitting} className="w-full bg-fire-700 hover:bg-fire-800 text-white font-semibold py-3 rounded-lg disabled:opacity-60">
            {submitting ? 'Submitting...' : 'Submit Inspection'}
          </button>
        </form>
      </div>
    </Layout>
  )
}

function ResultChip({ icon: Icon, label, active, color, onClick }) {
  const colorMap = {
    green: active ? 'bg-green-600 text-white border-green-600' : 'text-green-700 border-green-300',
    red: active ? 'bg-red-600 text-white border-red-600' : 'text-red-700 border-red-300',
    gray: active ? 'bg-slate-600 text-white border-slate-600' : 'text-slate-600 border-slate-300',
  }
  return (
    <button type="button" onClick={onClick} className={`flex items-center gap-1 border rounded-full px-3 py-1.5 text-xs font-semibold ${colorMap[color]}`}>
      <Icon size={14} /> {label}
    </button>
  )
}
