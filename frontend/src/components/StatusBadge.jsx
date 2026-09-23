import React from 'react'

const STATUS_CONFIG = {
  compliant: { label: 'Compliant', emoji: '🟢', className: 'bg-green-100 text-green-800' },
  due_soon: { label: 'Due Soon', emoji: '🟡', className: 'bg-yellow-100 text-yellow-800' },
  due_today: { label: 'Due Today', emoji: '🟠', className: 'bg-orange-100 text-orange-800' },
  overdue: { label: 'Overdue', emoji: '🔴', className: 'bg-red-100 text-red-800' },
  defective: { label: 'Defective', emoji: '⚠️', className: 'bg-red-100 text-red-800' },
  under_maintenance: { label: 'Under Maintenance', emoji: '🔧', className: 'bg-blue-100 text-blue-800' },
  out_of_service: { label: 'Out of Service', emoji: '❌', className: 'bg-gray-200 text-gray-800' },
}

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || { label: status, emoji: '•', className: 'bg-gray-100 text-gray-700' }
  return (
    <span className={`status-badge ${config.className}`}>
      <span>{config.emoji}</span> {config.label}
    </span>
  )
}
