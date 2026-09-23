import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute } from './components/Layout'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Assets from './pages/Assets'
import AssetDetail from './pages/AssetDetail'
import Scan from './pages/Scan'
import Inspections from './pages/Inspections'
import InspectionForm from './pages/InspectionForm'
import Maintenance from './pages/Maintenance'
import Locations from './pages/Locations'
import Notifications from './pages/Notifications'
import Reports from './pages/Reports'
import Users from './pages/Users'
import SettingsPage from './pages/Settings'
import AuditLogs from './pages/AuditLogs'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/assets" element={<ProtectedRoute><Assets /></ProtectedRoute>} />
      <Route path="/assets/:assetCode" element={<ProtectedRoute><AssetDetail /></ProtectedRoute>} />
      <Route path="/scan" element={<ProtectedRoute><Scan /></ProtectedRoute>} />
      <Route path="/inspections" element={<ProtectedRoute><Inspections /></ProtectedRoute>} />
      <Route path="/inspections/new/:assetCode" element={<ProtectedRoute><InspectionForm /></ProtectedRoute>} />
      <Route path="/maintenance" element={<ProtectedRoute roles={['admin', 'supervisor']}><Maintenance /></ProtectedRoute>} />
      <Route path="/locations" element={<ProtectedRoute roles={['admin']}><Locations /></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute roles={['admin', 'supervisor']}><Reports /></ProtectedRoute>} />
      <Route path="/users" element={<ProtectedRoute roles={['admin']}><Users /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute roles={['admin']}><SettingsPage /></ProtectedRoute>} />
      <Route path="/audit-logs" element={<ProtectedRoute roles={['admin', 'supervisor']}><AuditLogs /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
