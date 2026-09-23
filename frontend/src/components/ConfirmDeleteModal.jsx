import React, { useState } from 'react'
import { AlertTriangle, X } from 'lucide-react'

/**
 * A confirmation modal for genuinely irreversible actions. The confirm button stays disabled
 * until the user types the exact confirmText (e.g. the asset's ID) — a lighter "Are you sure?"
 * dialog is too easy to click through on a destructive, cascading delete.
 */
export default function ConfirmDeleteModal({ title, warning, confirmText, onConfirm, onClose }) {
  const [typed, setTyped] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')

  const handleConfirm = async () => {
    setDeleting(true)
    setError('')
    try {
      await onConfirm()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete')
      setDeleting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="font-bold text-red-700 flex items-center gap-2">
            <AlertTriangle size={18} /> {title}
          </h2>
          <button onClick={onClose}><X size={20} className="text-slate-400" /></button>
        </div>

        <div className="p-5 space-y-4">
          <p className="text-sm text-slate-700">{warning}</p>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Type <span className="font-mono font-bold text-red-700">{confirmText}</span> to confirm
            </label>
            <input
              autoFocus value={typed} onChange={(e) => setTyped(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 mt-1 font-mono"
            />
          </div>

          {error && <div className="text-sm text-red-600">{String(error)}</div>}

          <div className="flex gap-3">
            <button onClick={onClose} className="flex-1 border rounded-lg py-2 font-semibold text-slate-600">
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={typed !== confirmText || deleting}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white rounded-lg py-2 font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {deleting ? 'Deleting...' : 'Delete Permanently'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
