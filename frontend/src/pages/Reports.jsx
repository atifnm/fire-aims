import React, { useRef, useState } from 'react'
import { FileBarChart, Download, Upload, FileSpreadsheet, CheckCircle2, XCircle } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

async function download(url, filename) {
  const res = await api.get(url, { responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = blobUrl
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
}

const REPORTS = [
  { key: 'equipment', label: 'Equipment Report', desc: 'All assets with location, dates and current status.' },
  { key: 'defects', label: 'Defect Report', desc: 'All logged defects with severity, status and corrective action.' },
  { key: 'maintenance', label: 'Maintenance Report', desc: 'Full refill/service history across all equipment.' },
]

export default function Reports() {
  const { user } = useAuth()
  const fileInputRef = useRef(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [importResult, setImportResult] = useState(null)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0] || null)
    setImportResult(null)
    setError('')
  }

  const handleImport = async () => {
    if (!selectedFile) return
    setUploading(true)
    setError('')
    setImportResult(null)
    try {
      const form = new FormData()
      form.append('file', selectedFile)
      const res = await api.post('/assets/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      setImportResult(res.data)
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setError(err.response?.data?.detail || 'Import failed — check the file format and try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1 flex items-center gap-2"><FileBarChart /> Reports</h1>
        <p className="text-slate-500 text-sm mb-6">Download professional reports as CSV, Excel or PDF.</p>

        <div className="space-y-3">
          {REPORTS.map((r) => (
            <div key={r.key} className="bg-white rounded-xl shadow p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <div className="font-semibold text-slate-800">{r.label}</div>
                <div className="text-sm text-slate-500">{r.desc}</div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => download(`/reports/${r.key}/csv`, `${r.key}_report.csv`)} className="flex items-center gap-1 border rounded-lg px-3 py-1.5 text-sm font-semibold text-slate-600">
                  <Download size={14} /> CSV
                </button>
                <button onClick={() => download(`/reports/${r.key}/excel`, `${r.key}_report.xlsx`)} className="flex items-center gap-1 border rounded-lg px-3 py-1.5 text-sm font-semibold text-slate-600">
                  <Download size={14} /> Excel
                </button>
              </div>
            </div>
          ))}

          <div className="bg-white rounded-xl shadow p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div>
              <div className="font-semibold text-slate-800">Monthly Inspection Summary</div>
              <div className="text-sm text-slate-500">Total, inspected, pending, overdue, passed, failed, defective and under-maintenance counts.</div>
            </div>
            <button onClick={() => download('/reports/monthly-summary/pdf', 'monthly_summary_report.pdf')} className="flex items-center gap-1 bg-fire-700 hover:bg-fire-800 text-white rounded-lg px-3 py-1.5 text-sm font-semibold">
              <Download size={14} /> PDF
            </button>
          </div>
        </div>

        {user?.role === 'admin' && (
          <>
            <h2 className="text-lg font-bold text-fire-800 mt-8 mb-1 flex items-center gap-2">
              <Upload size={18} /> Import Equipment
            </h2>
            <p className="text-slate-500 text-sm mb-3">
              Bulk-create fire safety equipment from a CSV or Excel file — useful for setting up a new
              building's inventory in one go instead of adding items one at a time. Buildings, floors and
              rooms named in the file are matched by name or created automatically. This only creates new
              assets; it doesn't update existing ones.
            </p>

            <div className="bg-white rounded-xl shadow p-4 space-y-4">
              <button
                onClick={() => download('/assets/import/template', 'asset_import_template.csv')}
                className="flex items-center gap-2 border rounded-lg px-3 py-1.5 text-sm font-semibold text-slate-600"
              >
                <FileSpreadsheet size={14} /> Download CSV Template
              </button>

              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <input
                  ref={fileInputRef} type="file" accept=".csv,.xlsx,.xls" onChange={handleFileChange}
                  className="text-sm"
                />
                <button
                  onClick={handleImport} disabled={!selectedFile || uploading}
                  className="bg-fire-700 hover:bg-fire-800 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-40 whitespace-nowrap"
                >
                  {uploading ? 'Importing...' : 'Upload & Import'}
                </button>
              </div>

              {error && <div className="text-sm text-red-600">{String(error)}</div>}

              {importResult && (
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">
                    {importResult.created} created, {importResult.failed} failed (of {importResult.total} rows)
                  </div>
                  <div className="max-h-64 overflow-y-auto border rounded-lg divide-y">
                    {importResult.results.map((r) => (
                      <div key={r.row} className="flex items-start gap-2 px-3 py-2 text-sm">
                        {r.status === 'created' ? (
                          <CheckCircle2 size={16} className="text-green-600 shrink-0 mt-0.5" />
                        ) : (
                          <XCircle size={16} className="text-red-600 shrink-0 mt-0.5" />
                        )}
                        <div>
                          <span className="text-slate-500">Row {r.row}:</span>{' '}
                          {r.status === 'created' ? (
                            <span className="text-slate-800">created <strong>{r.asset_id}</strong></span>
                          ) : (
                            <span className="text-red-700">{r.error}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}
