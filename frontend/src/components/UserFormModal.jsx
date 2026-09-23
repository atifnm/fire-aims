import React, { useState } from 'react'
import { X } from 'lucide-react'
import api from '../api/client'

export default function UserFormModal({ onClose, onSaved, existingUser }) {
  const isEdit = Boolean(existingUser)
  const [form, setForm] = useState({
    employee_code: existingUser?.employee_code || '',
    full_name: existingUser?.full_name || '',
    email: existingUser?.email || '',
    phone: existingUser?.phone || '',
    role: existingUser?.role || 'inspector',
    is_active: existingUser?.is_active ?? true,
    password: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (isEdit) {
        // employee_code and email aren't editable once an account exists; password is only
        // sent if the admin actually typed a new one.
        const payload = {
          full_name: form.full_name, phone: form.phone, role: form.role, is_active: form.is_active,
        }
        if (form.password) payload.password = form.password
        await api.put(`/users/${existingUser.id}`, payload)
      } else {
        await api.post('/users', {
          employee_code: form.employee_code, full_name: form.full_name, email: form.email,
          phone: form.phone, role: form.role, password: form.password,
        })
      }
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${isEdit ? 'save' : 'create'} user`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="font-bold text-fire-800">{isEdit ? `Edit ${existingUser.full_name}` : 'Add User'}</h2>
          <button onClick={onClose}><X size={20} className="text-slate-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-5 space-y-3">
          <div>
            <input
              required disabled={isEdit} placeholder="Employee code (e.g. INS-020)"
              value={form.employee_code} onChange={(e) => setForm({ ...form, employee_code: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 disabled:bg-slate-100 disabled:text-slate-500"
            />
            {isEdit && <p className="text-xs text-slate-400 mt-1">Employee code can't be changed after account creation.</p>}
          </div>
          <input required placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <div>
            <input
              required disabled={isEdit} type="email" placeholder="Email"
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 disabled:bg-slate-100 disabled:text-slate-500"
            />
            {isEdit && <p className="text-xs text-slate-400 mt-1">Email (used to log in) can't be changed here.</p>}
          </div>
          <input placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="w-full border rounded-lg px-3 py-2">
            <option value="inspector">Inspector</option>
            <option value="supervisor">Supervisor</option>
            <option value="admin">Admin</option>
          </select>

          {isEdit ? (
            <>
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
                Account active
              </label>
              <input
                type="password" placeholder="New password (leave blank to keep current)"
                value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full border rounded-lg px-3 py-2"
              />
            </>
          ) : (
            <input required type="password" placeholder="Temporary password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          )}

          {error && <div className="text-sm text-red-600">{String(error)}</div>}
          <button type="submit" disabled={saving} className="w-full bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-2 font-semibold disabled:opacity-60">
            {saving ? 'Saving...' : isEdit ? 'Save Changes' : 'Create User'}
          </button>
        </form>
      </div>
    </div>
  )
}
