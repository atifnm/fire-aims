import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function SettingsPage() {
  const [settings, setSettings] = useState([])
  const [saving, setSaving] = useState('')

  const load = () => api.get('/settings').then((res) => setSettings(res.data))
  useEffect(() => { load() }, [])

  const updateSetting = async (key, value) => {
    setSaving(key)
    await api.put(`/settings/${key}`, { value })
    setSaving('')
    load()
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1">Settings</h1>
        <p className="text-slate-500 text-sm mb-6">
          Inspection intervals and alert thresholds. These are configurable because requirements may differ by
          jurisdiction, equipment type, manufacturer instructions and department SOPs.
        </p>

        <div className="bg-white rounded-xl shadow divide-y">
          {settings.map((s) => (
            <SettingRow key={s.key} setting={s} onSave={updateSetting} saving={saving === s.key} />
          ))}
        </div>
      </div>
    </Layout>
  )
}

function SettingRow({ setting, onSave, saving }) {
  const [value, setValue] = useState(setting.value)
  return (
    <div className="p-4 flex items-center justify-between gap-4">
      <div>
        <div className="font-medium text-slate-800 text-sm">{setting.description || setting.key}</div>
        <div className="text-xs text-slate-400">{setting.key}</div>
      </div>
      <div className="flex items-center gap-2">
        <input value={value} onChange={(e) => setValue(e.target.value)} className="w-24 border rounded-lg px-2 py-1 text-sm text-right" />
        <button
          onClick={() => onSave(setting.key, value)}
          disabled={saving || value === setting.value}
          className="text-xs bg-fire-700 hover:bg-fire-800 disabled:opacity-40 text-white px-3 py-1.5 rounded-lg font-semibold"
        >
          {saving ? '...' : 'Save'}
        </button>
      </div>
    </div>
  )
}
