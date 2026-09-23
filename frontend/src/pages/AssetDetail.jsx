import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ScanLine, ClipboardCheck, Wrench, Printer, Pencil, Trash2, ArrowLeft } from 'lucide-react'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { assetTypeLabel, assetTypeEmoji } from '../components/assetMeta'
import api, { assetUrl } from '../api/client'
import { useAuth } from '../context/AuthContext'
import MaintenanceFormModal from '../components/MaintenanceFormModal'
import AssetFormModal from '../components/AssetFormModal'
import ConfirmDeleteModal from '../components/ConfirmDeleteModal'

export default function AssetDetail() {
  const { assetCode } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [tab, setTab] = useState('inspections')
  const [showMaintenance, setShowMaintenance] = useState(false)
  const [showEdit, setShowEdit] = useState(false)
  const [showDelete, setShowDelete] = useState(false)

  const load = () => {
    api.get(`/assets/${assetCode}/history`).then((res) => setData(res.data))
  }

  useEffect(() => { load() }, [assetCode])

  if (!data) {
    return <Layout><div className="p-8 text-slate-500">Loading...</div></Layout>
  }

  const { asset, inspections, maintenance, defects, photos } = data

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-5xl mx-auto">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-slate-500 mb-4">
          <ArrowLeft size={16} /> Back
        </button>

        <div className="bg-white rounded-xl shadow p-5 mb-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div>
              <div className="text-2xl font-bold text-fire-800">{asset.asset_id}</div>
              <div className="text-slate-500">{assetTypeEmoji(asset.asset_type)} {assetTypeLabel(asset.asset_type)}</div>
            </div>
            <StatusBadge status={asset.status} />
          </div>

          <div className="mt-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-700 mb-1">Location</div>
            {asset.location_path || 'Not assigned'}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
            <DateField label="Last Inspection" value={asset.last_inspection_date} />
            <DateField label="Next Inspection" value={asset.next_inspection_date} />
            <DateField label="Last Service" value={asset.last_service_date} />
            <DateField label="Next Service" value={asset.next_service_date} />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm border-t pt-4">
            <InfoField label="Manufacturer" value={asset.manufacturer} />
            <InfoField label="Model" value={asset.model} />
            <InfoField label="Serial Number" value={asset.serial_number} />
            <InfoField label="Installed" value={asset.installation_date} />
          </div>

          {asset.extinguisher_detail && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm border-t pt-4">
              <InfoField label="Extinguisher Type" value={asset.extinguisher_detail.extinguisher_type} />
              <InfoField label="Capacity" value={asset.extinguisher_detail.capacity} />
              <InfoField label="Medium" value={asset.extinguisher_detail.extinguishing_medium} />
            </div>
          )}
          {asset.mcp_detail && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm border-t pt-4">
              <InfoField label="Connected Panel" value={asset.mcp_detail.connected_panel} />
              <InfoField label="Zone/Address" value={asset.mcp_detail.zone_address} />
            </div>
          )}

          {asset.remarks && (
            <div className="mt-4 text-sm border-t pt-4">
              <div className="font-semibold text-slate-700 mb-1">Remarks</div>
              {asset.remarks}
            </div>
          )}

          <div className="flex flex-wrap gap-2 mt-5">
            <ActionButton icon={ClipboardCheck} label="Start Inspection" onClick={() => navigate(`/inspections/new/${asset.asset_id}`)} primary />
            {user?.role === 'admin' && (
              <ActionButton icon={Pencil} label="Edit" onClick={() => setShowEdit(true)} />
            )}
            {(user?.role === 'admin' || user?.role === 'supervisor') && (
              <ActionButton icon={Wrench} label="Log Maintenance" onClick={() => setShowMaintenance(true)} />
            )}
            {asset.qr_code_path && (
              <a href={assetUrl(asset.qr_code_path)} target="_blank" rel="noreferrer">
                <ActionButton icon={Printer} label="Print QR" />
              </a>
            )}
            {asset.barcode_path && (
              <a href={assetUrl(asset.barcode_path)} target="_blank" rel="noreferrer">
                <ActionButton icon={Printer} label="Print Barcode" />
              </a>
            )}
            {user?.role === 'admin' && (
              <button
                onClick={() => setShowDelete(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border border-red-200 text-red-600 hover:bg-red-50 ml-auto"
              >
                <Trash2 size={16} /> Delete
              </button>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow">
          <div className="flex border-b overflow-x-auto">
            {['inspections', 'maintenance', 'defects', 'photos'].map((t) => (
              <button
                key={t} onClick={() => setTab(t)}
                className={`px-4 py-3 text-sm font-semibold whitespace-nowrap ${tab === t ? 'text-fire-700 border-b-2 border-fire-700' : 'text-slate-400'}`}
              >
                {t[0].toUpperCase() + t.slice(1)} ({t === 'inspections' ? inspections.length : t === 'maintenance' ? maintenance.length : t === 'defects' ? defects.length : photos.length})
              </button>
            ))}
          </div>

          <div className="p-4">
            {tab === 'inspections' && (
              inspections.length === 0 ? <Empty text="No inspections recorded yet." /> :
              inspections.map((i) => (
                <TimelineItem key={i.id}
                  date={i.inspected_at}
                  title={`Result: ${i.overall_result.replace(/_/g, ' ').toUpperCase()}`}
                  subtitle={`Status: ${i.status} ${i.reviewed_by_id ? '· Reviewed' : ''}`}
                  body={i.general_remarks}
                />
              ))
            )}
            {tab === 'maintenance' && (
              maintenance.length === 0 ? <Empty text="No maintenance/refill records yet." /> :
              maintenance.map((m) => (
                <TimelineItem key={m.id}
                  date={m.service_date}
                  title={`${m.service_type.toUpperCase()} — ${m.service_provider || 'Unspecified provider'}`}
                  subtitle={m.technician ? `Technician: ${m.technician}` : ''}
                  body={m.work_performed}
                />
              ))
            )}
            {tab === 'defects' && (
              defects.length === 0 ? <Empty text="No defects logged." /> :
              defects.map((d) => (
                <DefectTimelineItem key={d.id} defect={d} canEdit={user?.role === 'admin'} onUpdated={load} />
              ))
            )}
            {tab === 'photos' && (
              photos.length === 0 ? <Empty text="No photos uploaded." /> :
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {photos.map((p) => (
                  <a key={p.id} href={assetUrl(p.file_path)} target="_blank" rel="noreferrer">
                    <img src={assetUrl(p.file_path)} alt={p.context} className="rounded-lg w-full h-28 object-cover border" />
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {showMaintenance && (
        <MaintenanceFormModal
          assetId={asset.id}
          onClose={() => setShowMaintenance(false)}
          onCreated={() => { setShowMaintenance(false); load() }}
        />
      )}

      {showEdit && (
        <AssetFormModal
          existingAsset={asset}
          onClose={() => setShowEdit(false)}
          onCreated={() => { setShowEdit(false); load() }}
        />
      )}

      {showDelete && (
        <ConfirmDeleteModal
          title={`Delete ${asset.asset_id}`}
          confirmText={asset.asset_id}
          warning={
            `This permanently deletes ${asset.asset_id} and cannot be undone. This also deletes its ` +
            `entire history: ${inspections.length} inspection(s), ${maintenance.length} maintenance ` +
            `record(s), ${defects.length} defect(s), and ${photos.length} photo(s). Only delete an asset ` +
            `that was set up by mistake or is being permanently decommissioned — for equipment that's ` +
            `temporarily out of service, leave the record in place instead.`
          }
          onClose={() => setShowDelete(false)}
          onConfirm={async () => {
            await api.delete(`/assets/${asset.asset_id}`)
            navigate('/assets')
          }}
        />
      )}
    </Layout>
  )
}

function DateField({ label, value }) {
  return (
    <div>
      <div className="text-xs text-slate-400">{label}</div>
      <div className="font-medium text-slate-700">{value ? new Date(value).toLocaleDateString() : '—'}</div>
    </div>
  )
}

function InfoField({ label, value }) {
  return (
    <div>
      <div className="text-xs text-slate-400">{label}</div>
      <div className="font-medium text-slate-700">{value || '—'}</div>
    </div>
  )
}

function ActionButton({ icon: Icon, label, onClick, primary }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold ${
        primary ? 'bg-fire-700 hover:bg-fire-800 text-white' : 'border text-slate-600 hover:bg-slate-50'
      }`}
    >
      <Icon size={16} /> {label}
    </button>
  )
}

const DEFECT_STATUS_OPTIONS = ['open', 'assigned', 'in_progress', 'resolved', 'verified']

function DefectTimelineItem({ defect, canEdit, onUpdated }) {
  const [status, setStatus] = useState(defect.status)
  const [saving, setSaving] = useState(false)

  const save = async (newStatus) => {
    setStatus(newStatus)
    setSaving(true)
    try {
      await api.put(`/defects/${defect.id}`, { status: newStatus })
      onUpdated()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="border-l-2 border-fire-200 pl-4 pb-5 relative">
      <div className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-fire-600" />
      <div className="text-xs text-slate-400">{new Date(defect.created_at).toLocaleString()}</div>
      <div className="flex items-center gap-2 flex-wrap">
        <span className="font-semibold text-slate-800">{defect.severity.toUpperCase()}</span>
        {canEdit ? (
          <select
            value={status} disabled={saving} onChange={(e) => save(e.target.value)}
            className="text-xs border rounded-full px-2 py-0.5 font-semibold text-fire-800 bg-fire-50"
          >
            {DEFECT_STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
          </select>
        ) : (
          <span className="text-xs text-slate-500">{status.replace(/_/g, ' ')}</span>
        )}
      </div>
      {defect.assigned_to && <div className="text-xs text-slate-500">Assigned to: {defect.assigned_to}</div>}
      <div className="text-sm text-slate-600 mt-1">{defect.description}</div>
      {!canEdit && (
        <div className="text-xs text-slate-400 mt-1">Only an Admin can update defect status.</div>
      )}
    </div>
  )
}

function TimelineItem({ date, title, subtitle, body }) {
  return (
    <div className="border-l-2 border-fire-200 pl-4 pb-5 relative">
      <div className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-fire-600" />
      <div className="text-xs text-slate-400">{date ? new Date(date).toLocaleString() : ''}</div>
      <div className="font-semibold text-slate-800">{title}</div>
      {subtitle && <div className="text-xs text-slate-500">{subtitle}</div>}
      {body && <div className="text-sm text-slate-600 mt-1">{body}</div>}
    </div>
  )
}

function Empty({ text }) {
  return <div className="text-center text-slate-400 py-8 text-sm">{text}</div>
}
