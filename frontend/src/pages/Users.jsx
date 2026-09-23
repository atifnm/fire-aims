import React, { useEffect, useState } from 'react'
import { Plus, Pencil } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'
import UserFormModal from '../components/UserFormModal'

export default function Users() {
  const [users, setUsers] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingUser, setEditingUser] = useState(null)

  const load = () => api.get('/users').then((res) => setUsers(res.data))
  useEffect(() => { load() }, [])

  const toggleActive = async (u) => {
    await api.put(`/users/${u.id}`, { is_active: !u.is_active })
    load()
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-fire-800">Users</h1>
            <p className="text-slate-500 text-sm">Manage admin, supervisor and inspector accounts</p>
          </div>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-fire-700 hover:bg-fire-800 text-white px-4 py-2 rounded-lg text-sm font-semibold">
            <Plus size={16} /> Add User
          </button>
        </div>

        {/* Mobile: stacked cards */}
        <div className="md:hidden space-y-2">
          {users.map((u) => (
            <div key={u.id} className="bg-white rounded-xl shadow p-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-semibold text-slate-800">{u.full_name}</div>
                  <div className="text-xs text-slate-500">{u.employee_code} · <span className="capitalize">{u.role}</span></div>
                </div>
                {u.is_active ? (
                  <span className="text-xs text-green-600 font-semibold shrink-0">Active</span>
                ) : (
                  <span className="text-xs text-slate-400 font-semibold shrink-0">Disabled</span>
                )}
              </div>
              <div className="text-sm text-slate-500 mt-2 truncate">{u.email}</div>
              <div className="flex items-center gap-4 mt-3">
                <button onClick={() => setEditingUser(u)} className="flex items-center gap-1 text-xs text-fire-700 font-semibold">
                  <Pencil size={14} /> Edit
                </button>
                <button onClick={() => toggleActive(u)} className="text-xs text-slate-500 font-semibold">
                  {u.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Desktop/tablet: full table */}
        <div className="hidden md:block bg-white rounded-xl shadow overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
              <tr>
                <th className="text-left px-4 py-3">Employee Code</th>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Email</th>
                <th className="text-left px-4 py-3">Role</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="px-4 py-3">{u.employee_code}</td>
                  <td className="px-4 py-3">{u.full_name}</td>
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3 capitalize">{u.role}</td>
                  <td className="px-4 py-3">{u.is_active ? <span className="text-green-600">Active</span> : <span className="text-slate-400">Disabled</span>}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <button onClick={() => setEditingUser(u)} title={`Edit ${u.full_name}`} className="text-slate-400 hover:text-fire-700">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => toggleActive(u)} className="text-xs text-fire-700 font-semibold whitespace-nowrap">
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showForm && (
        <UserFormModal onClose={() => setShowForm(false)} onSaved={() => { setShowForm(false); load() }} />
      )}
      {editingUser && (
        <UserFormModal
          existingUser={editingUser}
          onClose={() => setEditingUser(null)}
          onSaved={() => { setEditingUser(null); load() }}
        />
      )}
    </Layout>
  )
}
