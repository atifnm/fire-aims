import React, { useState } from 'react'
import { X, ShieldAlert } from 'lucide-react'
import api from '../api/client'

const RESULT_OPTIONS = [
  { value: 'pass', label: 'PASS' },
  { value: 'pass_with_observation', label: 'PASS WITH OBSERVATION' },
  { value: 'requires_maintenance', label: 'REQUIRES MAINTENANCE' },
  { value: 'failed', label: 'FAILED / REMOVE FROM SERVICE' },
]

export default function InspectionCorrectionModal({ inspection, onClose, onSaved }) {
  const [overallResult, setOverallResult] = useState(inspection.overall_result)
  const [generalRemarks, setGeneralRemarks] = useState(inspection.general_remarks || '')
  const [defectDescription, setDefectDescription] = useState(inspection.defect_description || '')
  const [correctiveAction, setCorrectiveAction] = useState(inspection.corrective_action || '')
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.put(`/inspections/${inspection.id}`, {
        overall_result: overallResult,
        general_remarks: generalRemarks || null,
        defect_description: defectDescription || null,
        corrective_action: correctiveAction || null,
        correction_reason: reason,
      })
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save correction')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="font-bold text-fire-800 flex items-center gap-2">
            <ShieldAlert size={18} className="text-gold-600" /> Correct Inspection #{inspection.id}
          </h2>
          <button onClick={onClose}><X size={20} className="text-slate-400" /></button>
        </div>

        <div className="px-5 pt-4 text-xs text-amber-700 bg-amber-50 mx-5 mt-3 rounded-lg p-2">
          Admin-only correction. This change is written to the audit log along with your reason —
          it does not delete the original submission.
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700">Overall Result</label>
            <select value={overallResult} onChange={(e) => setOverallResult(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1">
              {RESULT_OPTIONS.map((opt) => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">General Remarks</label>
            <textarea value={generalRemarks} onChange={(e) => setGeneralRemarks(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Defect Description</label>
            <textarea value={defectDescription} onChange={(e) => setDefectDescription(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Corrective Action</label>
            <textarea value={correctiveAction} onChange={(e) => setCorrectiveAction(e.target.value)} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Reason for Correction (required, logged)</label>
            <input required value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Inspector reported wrong result by phone" className="w-full border rounded-lg px-3 py-2 mt-1" />
          </div>

          {error && <div className="text-sm text-red-600">{String(error)}</div>}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border rounded-lg py-2 font-semibold text-slate-600">Cancel</button>
            <button type="submit" disabled={saving} className="flex-1 bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-2 font-semibold disabled:opacity-60">
              {saving ? 'Saving...' : 'Save Correction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
