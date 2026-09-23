import React, { useState } from 'react'
import { X } from 'lucide-react'
import api from '../api/client'

export default function MaintenanceFormModal({ assetId, onClose, onCreated }) {
  const [form, setForm] = useState({
    service_date: new Date().toISOString().slice(0, 10),
    service_type: 'refilled',
    work_performed: '',
    agent_used: '',
    quantity: '',
    service_provider: '',
    technician: '',
    cost: '',
    next_service_date: '',
    remarks: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.post('/maintenance', {
        asset_id: assetId,
        ...form,
        cost: form.cost ? Number(form.cost) : null,
        next_service_date: form.next_service_date || null,
      })
      onCreated()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save maintenance record')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="font-bold text-fire-800">Log Maintenance / Refill</h2>
          <button onClick={onClose}><X size={20} className="text-slate-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-5 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Service Date</label>
              <input type="date" required value={form.service_date} onChange={(e) => setForm({ ...form, service_date: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Type</label>
              <select value={form.service_type} onChange={(e) => setForm({ ...form, service_type: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1">
                <option value="refilled">Refilled</option>
                <option value="serviced">Serviced</option>
                <option value="repaired">Repaired</option>
                <option value="replaced">Replaced</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Work Performed</label>
            <textarea value={form.work_performed} onChange={(e) => setForm({ ...form, work_performed: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Agent/Media Used</label>
              <input value={form.agent_used} onChange={(e) => setForm({ ...form, agent_used: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Quantity</label>
              <input value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Service Provider</label>
              <input value={form.service_provider} onChange={(e) => setForm({ ...form, service_provider: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Technician</label>
              <input value={form.technician} onChange={(e) => setForm({ ...form, technician: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Cost</label>
              <input type="number" step="0.01" value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Next Service Date</label>
              <input type="date" value={form.next_service_date} onChange={(e) => setForm({ ...form, next_service_date: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Remarks</label>
            <textarea value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>
          {error && <div className="text-sm text-red-600">{String(error)}</div>}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border rounded-lg py-2 font-semibold text-slate-600">Cancel</button>
            <button type="submit" disabled={saving} className="flex-1 bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-2 font-semibold disabled:opacity-60">
              {saving ? 'Saving...' : 'Save Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
