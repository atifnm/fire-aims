import React, { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, X, Check } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function Locations() {
  const [buildings, setBuildings] = useState([])
  const [floors, setFloors] = useState([])
  const [locations, setLocations] = useState([])
  const [newBuilding, setNewBuilding] = useState({ name: '', code: '', address: '' })
  const [newFloor, setNewFloor] = useState({ building_id: '', name: '' })
  const [newLocation, setNewLocation] = useState({ floor_id: '', department: '', room: '', area: '', description: '' })

  // Which row (by id) is currently being edited, per section, and its draft values.
  const [editingBuilding, setEditingBuilding] = useState(null)
  const [editingFloor, setEditingFloor] = useState(null)
  const [editingLocation, setEditingLocation] = useState(null)

  const loadAll = () => {
    api.get('/buildings').then((res) => setBuildings(res.data))
    api.get('/floors').then((res) => setFloors(res.data))
    api.get('/locations').then((res) => setLocations(res.data))
  }

  useEffect(() => { loadAll() }, [])

  const addBuilding = async (e) => {
    e.preventDefault()
    await api.post('/buildings', newBuilding)
    setNewBuilding({ name: '', code: '', address: '' })
    loadAll()
  }

  const addFloor = async (e) => {
    e.preventDefault()
    await api.post('/floors', { ...newFloor, building_id: Number(newFloor.building_id) })
    setNewFloor({ building_id: '', name: '' })
    loadAll()
  }

  const addLocation = async (e) => {
    e.preventDefault()
    await api.post('/locations', { ...newLocation, floor_id: Number(newLocation.floor_id) })
    setNewLocation({ floor_id: '', department: '', room: '', area: '', description: '' })
    loadAll()
  }

  const saveBuilding = async (id) => {
    await api.put(`/buildings/${id}`, { name: editingBuilding.name, code: editingBuilding.code })
    setEditingBuilding(null)
    loadAll()
  }

  const saveFloor = async (id) => {
    await api.put(`/floors/${id}`, { name: editingFloor.name, building_id: Number(editingFloor.building_id) })
    setEditingFloor(null)
    loadAll()
  }

  const saveLocation = async (id) => {
    await api.put(`/locations/${id}`, {
      room: editingLocation.room, area: editingLocation.area, floor_id: Number(editingLocation.floor_id),
    })
    setEditingLocation(null)
    loadAll()
  }

  const removeBuilding = async (id) => {
    if (!confirm('Delete this building? This also removes its floors and rooms.')) return
    await api.delete(`/buildings/${id}`)
    loadAll()
  }
  const removeFloor = async (id) => {
    if (!confirm('Delete this floor? This also removes its rooms.')) return
    await api.delete(`/floors/${id}`)
    loadAll()
  }
  const removeLocation = async (id) => {
    if (!confirm('Delete this room/area?')) return
    await api.delete(`/locations/${id}`)
    loadAll()
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1">Locations</h1>
        <p className="text-slate-500 text-sm mb-6">
          Buildings → Floors → Rooms/Areas hierarchy. Only Admins can add, edit or remove locations.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* ---- Buildings ---- */}
          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Buildings ({buildings.length})</h2>
            <form onSubmit={addBuilding} className="space-y-2 mb-4">
              <input required placeholder="Building name" value={newBuilding.name} onChange={(e) => setNewBuilding({ ...newBuilding, name: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm" />
              <input placeholder="Code (optional)" value={newBuilding.code} onChange={(e) => setNewBuilding({ ...newBuilding, code: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm" />
              <button type="submit" className="w-full bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-1.5 text-sm font-semibold flex items-center justify-center gap-1"><Plus size={14} /> Add</button>
            </form>
            <ul className="text-sm space-y-1 text-slate-600">
              {buildings.map((b) => (
                <li key={b.id} className="flex items-center justify-between gap-1 group">
                  {editingBuilding?.id === b.id ? (
                    <div className="flex-1 space-y-1 py-0.5">
                      <input autoFocus value={editingBuilding.name} onChange={(e) => setEditingBuilding({ ...editingBuilding, name: e.target.value })} className="w-full border rounded px-2 py-1 text-sm" />
                      <div className="flex gap-3">
                        <button onClick={() => saveBuilding(b.id)} className="text-green-600"><Check size={16} /></button>
                        <button onClick={() => setEditingBuilding(null)} className="text-slate-400"><X size={16} /></button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <span className="truncate">🏢 {b.name}</span>
                      <span className="hidden group-hover:flex gap-2 shrink-0">
                        <button onClick={() => setEditingBuilding({ id: b.id, name: b.name, code: b.code })} className="text-slate-400 hover:text-fire-700"><Pencil size={14} /></button>
                        <button onClick={() => removeBuilding(b.id)} className="text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
                      </span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* ---- Floors ---- */}
          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Floors ({floors.length})</h2>
            <form onSubmit={addFloor} className="space-y-2 mb-4">
              <select required value={newFloor.building_id} onChange={(e) => setNewFloor({ ...newFloor, building_id: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm">
                <option value="">Select building</option>
                {buildings.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
              <input required placeholder="Floor name" value={newFloor.name} onChange={(e) => setNewFloor({ ...newFloor, name: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm" />
              <button type="submit" className="w-full bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-1.5 text-sm font-semibold flex items-center justify-center gap-1"><Plus size={14} /> Add</button>
            </form>
            <ul className="text-sm space-y-1 text-slate-600 max-h-48 overflow-y-auto">
              {floors.map((f) => (
                <li key={f.id} className="flex items-center justify-between gap-1 group">
                  {editingFloor?.id === f.id ? (
                    <div className="flex-1 space-y-1 py-0.5">
                      <input autoFocus value={editingFloor.name} onChange={(e) => setEditingFloor({ ...editingFloor, name: e.target.value })} className="w-full border rounded px-2 py-1 text-sm" />
                      <div className="flex gap-3">
                        <button onClick={() => saveFloor(f.id)} className="text-green-600"><Check size={16} /></button>
                        <button onClick={() => setEditingFloor(null)} className="text-slate-400"><X size={16} /></button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <span className="truncate">🏬 {f.name}</span>
                      <span className="hidden group-hover:flex gap-2 shrink-0">
                        <button onClick={() => setEditingFloor({ id: f.id, name: f.name, building_id: f.building_id })} className="text-slate-400 hover:text-fire-700"><Pencil size={14} /></button>
                        <button onClick={() => removeFloor(f.id)} className="text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
                      </span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* ---- Rooms/Areas ---- */}
          <div className="bg-white rounded-xl shadow p-4">
            <h2 className="font-semibold text-slate-700 mb-3">Rooms/Areas ({locations.length})</h2>
            <form onSubmit={addLocation} className="space-y-2 mb-4">
              <select required value={newLocation.floor_id} onChange={(e) => setNewLocation({ ...newLocation, floor_id: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm">
                <option value="">Select floor</option>
                {floors.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
              </select>
              <input placeholder="Room" value={newLocation.room} onChange={(e) => setNewLocation({ ...newLocation, room: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm" />
              <input placeholder="Area (e.g. Near Emergency Exit)" value={newLocation.area} onChange={(e) => setNewLocation({ ...newLocation, area: e.target.value })} className="w-full border rounded-lg px-3 py-1.5 text-sm" />
              <button type="submit" className="w-full bg-fire-700 hover:bg-fire-800 text-white rounded-lg py-1.5 text-sm font-semibold flex items-center justify-center gap-1"><Plus size={14} /> Add</button>
            </form>
            <ul className="text-sm space-y-1 text-slate-600 max-h-48 overflow-y-auto">
              {locations.map((l) => (
                <li key={l.id} className="flex items-center justify-between gap-1 group">
                  {editingLocation?.id === l.id ? (
                    <div className="flex-1 space-y-1">
                      <input autoFocus placeholder="Room" value={editingLocation.room || ''} onChange={(e) => setEditingLocation({ ...editingLocation, room: e.target.value })} className="w-full border rounded px-2 py-1 text-sm" />
                      <input placeholder="Area" value={editingLocation.area || ''} onChange={(e) => setEditingLocation({ ...editingLocation, area: e.target.value })} className="w-full border rounded px-2 py-1 text-sm" />
                      <div className="flex gap-2">
                        <button onClick={() => saveLocation(l.id)} className="text-green-600"><Check size={16} /></button>
                        <button onClick={() => setEditingLocation(null)} className="text-slate-400"><X size={16} /></button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <span className="truncate">📍 {l.display_path}</span>
                      <span className="hidden group-hover:flex gap-2 shrink-0">
                        <button onClick={() => setEditingLocation({ id: l.id, room: l.room, area: l.area, floor_id: l.floor_id })} className="text-slate-400 hover:text-fire-700"><Pencil size={14} /></button>
                        <button onClick={() => removeLocation(l.id)} className="text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
                      </span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </Layout>
  )
}
