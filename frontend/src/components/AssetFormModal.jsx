import React, { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import api from '../api/client'

const ASSET_TYPES = [
  { value: 'extinguisher', label: '🧯 Fire Extinguisher' },
  { value: 'hose_cabinet', label: '🚒 Hose Cabinet' },
  { value: 'hose_reel', label: '🌀 Hose Reel' },
  { value: 'branch', label: '🔫 Branch/Nozzle' },
  { value: 'mcp', label: '📟 Manual Call Point' },
]

const detailFieldMap = {
  extinguisher: 'extinguisher_detail',
  hose_cabinet: 'hose_cabinet_detail',
  hose_reel: 'hose_reel_detail',
  branch: 'branch_detail',
  mcp: 'mcp_detail',
}

function detailFromExisting(existingAsset) {
  const d = existingAsset ? existingAsset[detailFieldMap[existingAsset.asset_type]] : null
  return {
    extinguisher_type: d?.extinguisher_type || 'ABC Dry Chemical',
    capacity: d?.capacity || '',
    extinguishing_medium: d?.extinguishing_medium || '',
    hose_length_m: d?.hose_length_m ?? '',
    hose_diameter_mm: d?.hose_diameter_mm ?? '',
    nozzle_type: d?.nozzle_type || '',
    condition: d?.condition || '',
    connected_panel: d?.connected_panel || '',
    zone_address: d?.zone_address || '',
    cabinet_material: d?.cabinet_material || '',
  }
}

// Asset dates come back from the API as full ISO datetimes; a <input type="date"> needs YYYY-MM-DD.
function toDateInputValue(value) {
  if (!value) return ''
  return String(value).slice(0, 10)
}

export default function AssetFormModal({ onClose, onCreated, existingAsset }) {
  const isEdit = Boolean(existingAsset)
  const [assetType, setAssetType] = useState(existingAsset?.asset_type || 'extinguisher')
  const [locations, setLocations] = useState([])
  const [form, setForm] = useState({
    location_id: existingAsset?.location_id || '',
    specific_location: existingAsset?.specific_location || '',
    manufacturer: existingAsset?.manufacturer || '',
    model: existingAsset?.model || '',
    serial_number: existingAsset?.serial_number || '',
    installation_date: toDateInputValue(existingAsset?.installation_date),
    assigned_department: existingAsset?.assigned_department || '',
    remarks: existingAsset?.remarks || '',
  })
  const [detail, setDetail] = useState(detailFromExisting(existingAsset))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/locations').then((res) => setLocations(res.data))
  }, [])

  const buildDetailPayload = () => {
    switch (assetType) {
      case 'extinguisher':
        return { extinguisher_type: detail.extinguisher_type, capacity: detail.capacity, extinguishing_medium: detail.extinguishing_medium }
      case 'hose_cabinet':
        return { cabinet_material: detail.cabinet_material }
      case 'hose_reel':
        return { hose_length_m: detail.hose_length_m ? Number(detail.hose_length_m) : null, hose_diameter_mm: detail.hose_diameter_mm ? Number(detail.hose_diameter_mm) : null }
      case 'branch':
        return { nozzle_type: detail.nozzle_type, condition: detail.condition }
      case 'mcp':
        return { connected_panel: detail.connected_panel, zone_address: detail.zone_address }
      default:
        return {}
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = {
        ...form,
        location_id: form.location_id ? Number(form.location_id) : null,
        installation_date: form.installation_date || null,
        [detailFieldMap[assetType]]: buildDetailPayload(),
      }
      if (isEdit) {
        await api.put(`/assets/${existingAsset.asset_id}`, payload)
      } else {
        await api.post('/assets', { asset_type: assetType, ...payload })
      }
      onCreated()
    } catch (err) {
      setError(err.response?.data?.detail?.[0]?.msg || err.response?.data?.detail || `Failed to ${isEdit ? 'save' : 'create'} asset`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="font-bold text-fire-800">
            {isEdit ? `Edit ${existingAsset.asset_id}` : 'Add Fire Safety Equipment'}
          </h2>
          <button onClick={onClose}><X size={20} className="text-slate-400" /></button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700">Equipment Type</label>
            <select
              value={assetType} disabled={isEdit}
              onChange={(e) => setAssetType(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 mt-1 disabled:bg-slate-100 disabled:text-slate-500"
            >
              {ASSET_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <p className="text-xs text-slate-400 mt-1">
              {isEdit
                ? "Equipment type can't be changed after creation — delete and re-add if it was set up wrong."
                : 'A unique Asset ID and QR/barcode will be generated automatically.'}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Location</label>
            <select value={form.location_id} onChange={(e) => setForm({ ...form, location_id: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1">
              <option value="">-- Select location --</option>
              {locations.map((l) => <option key={l.id} value={l.id}>{l.display_path}</option>)}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Specific Location (e.g. "Near Main Entrance")</label>
            <input value={form.specific_location} onChange={(e) => setForm({ ...form, specific_location: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Manufacturer</label>
              <input value={form.manufacturer} onChange={(e) => setForm({ ...form, manufacturer: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Model</label>
              <input value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Serial Number</label>
              <input value={form.serial_number} onChange={(e) => setForm({ ...form, serial_number: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Installation Date</label>
              <input type="date" value={form.installation_date} onChange={(e) => setForm({ ...form, installation_date: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
          </div>

          {assetType === 'extinguisher' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-fire-50 p-3 rounded-lg">
              <div>
                <label className="text-sm font-medium text-slate-700">Extinguisher Type</label>
                <select value={detail.extinguisher_type} onChange={(e) => setDetail({ ...detail, extinguisher_type: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1">
                  {['ABC Dry Chemical', 'CO2', 'Foam', 'Water', 'Wet Chemical', 'Clean Agent', 'Other'].map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Capacity</label>
                <input value={detail.capacity} onChange={(e) => setDetail({ ...detail, capacity: e.target.value })} placeholder="e.g. 9kg" className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
            </div>
          )}

          {assetType === 'hose_reel' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-fire-50 p-3 rounded-lg">
              <div>
                <label className="text-sm font-medium text-slate-700">Hose Length (m)</label>
                <input type="number" value={detail.hose_length_m} onChange={(e) => setDetail({ ...detail, hose_length_m: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Hose Diameter (mm)</label>
                <input type="number" value={detail.hose_diameter_mm} onChange={(e) => setDetail({ ...detail, hose_diameter_mm: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
            </div>
          )}

          {assetType === 'branch' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-fire-50 p-3 rounded-lg">
              <div>
                <label className="text-sm font-medium text-slate-700">Nozzle Type</label>
                <input value={detail.nozzle_type} onChange={(e) => setDetail({ ...detail, nozzle_type: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Condition</label>
                <input value={detail.condition} onChange={(e) => setDetail({ ...detail, condition: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
            </div>
          )}

          {assetType === 'mcp' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-fire-50 p-3 rounded-lg">
              <div>
                <label className="text-sm font-medium text-slate-700">Connected Panel</label>
                <input value={detail.connected_panel} onChange={(e) => setDetail({ ...detail, connected_panel: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Zone/Address</label>
                <input value={detail.zone_address} onChange={(e) => setDetail({ ...detail, zone_address: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
              </div>
            </div>
          )}

          {assetType === 'hose_cabinet' && (
            <div className="bg-fire-50 p-3 rounded-lg">
              <label className="text-sm font-medium text-slate-700">Cabinet Material</label>
              <input value={detail.cabinet_material} onChange={(e) => setDetail({ ...detail, cabinet_material: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" />
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-slate-700">Remarks</label>
            <textarea value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} className="w-full border rounded-lg px-3 py-2 mt-1" rows={2} />
          </div>

          {error && <div className="text-sm text-red-600">{String(error)}</div>}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border rounded-lg py-2 font-semibold text-slate-600">Cancel</button>
            <button type="submit" disabled={saving} className="flex-1 bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-2 font-semibold disabled:opacity-60">
              {saving ? 'Saving...' : isEdit ? 'Save Changes' : 'Create Asset'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
