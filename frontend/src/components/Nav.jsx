import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Flame, ClipboardCheck, Wrench, MapPin, Bell,
  FileBarChart, Users, Settings, ScrollText, ScanLine, LogOut, Menu, X,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'supervisor', 'inspector'] },
  { to: '/assets', label: 'Assets', icon: Flame, roles: ['admin', 'supervisor', 'inspector'] },
  { to: '/scan', label: 'Scan', icon: ScanLine, roles: ['admin', 'supervisor', 'inspector'], mobilePrimary: true },
  { to: '/inspections', label: 'Inspections', icon: ClipboardCheck, roles: ['admin', 'supervisor', 'inspector'] },
  { to: '/maintenance', label: 'Maintenance', icon: Wrench, roles: ['admin', 'supervisor'] },
  { to: '/locations', label: 'Locations', icon: MapPin, roles: ['admin'] },
  { to: '/notifications', label: 'Notifications', icon: Bell, roles: ['admin', 'supervisor', 'inspector'] },
  { to: '/reports', label: 'Reports', icon: FileBarChart, roles: ['admin', 'supervisor'] },
  { to: '/users', label: 'Users', icon: Users, roles: ['admin'] },
  { to: '/settings', label: 'Settings', icon: Settings, roles: ['admin'] },
  { to: '/audit-logs', label: 'Audit Logs', icon: ScrollText, roles: ['admin', 'supervisor'] },
]

export function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const items = NAV_ITEMS.filter((i) => i.roles.includes(user?.role))

  return (
    <aside className="hidden md:flex md:flex-col w-60 bg-fire-800 text-slate-100 h-screen sticky top-0">
      <div className="px-5 py-5 border-b border-gold-700/40 flex items-center gap-3">
        <div className="bg-white rounded-lg p-1.5 shrink-0">
          <img src="/brand/logo.svg" alt="Organization logo" className="h-8 w-auto" />
        </div>
        <div>
          <div className="text-lg font-extrabold text-gold-400 tracking-wide leading-tight">FIRE-AIMS</div>
          <div className="text-[11px] text-fire-200 leading-tight">Fire Safety Equipment Mgmt</div>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto py-3">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm font-medium border-l-4 ${
                isActive
                  ? 'bg-fire-700 text-gold-300 border-gold-400'
                  : 'text-fire-100 border-transparent hover:bg-fire-700/60'
              }`
            }
          >
            <Icon size={18} /> {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-4 border-t border-gold-700/40">
        <div className="text-sm font-semibold">{user?.full_name}</div>
        <div className="text-xs text-fire-200 mb-2 capitalize">{user?.role} · {user?.employee_code}</div>
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="flex items-center gap-2 text-sm text-fire-100 hover:text-gold-300"
        >
          <LogOut size={16} /> Logout
        </button>
      </div>
    </aside>
  )
}

// Sticky top bar shown only on mobile, with a hamburger that opens the full nav list below.
// This exists because the bottom tab bar only has room for 5 shortcuts — everything else
// (Maintenance, Locations, Reports, Users, Settings, Audit Logs) would otherwise be
// completely unreachable on a phone.
export function MobileHeader() {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const items = NAV_ITEMS.filter((i) => i.roles.includes(user?.role))

  return (
    <>
      <header className="md:hidden sticky top-0 z-30 bg-fire-800 text-white flex items-center justify-between px-4 py-3 safe-top">
        <div className="flex items-center gap-2">
          <div className="bg-white rounded-md p-1">
            <img src="/brand/logo.svg" alt="Organization logo" className="h-5 w-auto" />
          </div>
          <span className="font-extrabold text-gold-400 tracking-wide">FIRE-AIMS</span>
        </div>
        <button onClick={() => setOpen(true)} aria-label="Open menu" className="p-1">
          <Menu size={24} />
        </button>
      </header>

      {open && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <div className="relative ml-auto w-72 max-w-[85%] bg-fire-800 text-white h-full flex flex-col safe-top safe-bottom">
            <div className="flex items-center justify-between px-5 py-4 border-b border-gold-700/40">
              <span className="font-extrabold text-gold-400">Menu</span>
              <button onClick={() => setOpen(false)} aria-label="Close menu"><X size={22} /></button>
            </div>
            <nav className="flex-1 overflow-y-auto py-3">
              {items.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-5 py-3 text-sm font-medium border-l-4 ${
                      isActive
                        ? 'bg-fire-700 text-gold-300 border-gold-400'
                        : 'text-fire-100 border-transparent'
                    }`
                  }
                >
                  <Icon size={18} /> {label}
                </NavLink>
              ))}
            </nav>
            <div className="px-5 py-4 border-t border-gold-700/40">
              <div className="text-sm font-semibold">{user?.full_name}</div>
              <div className="text-xs text-fire-200 mb-2 capitalize">{user?.role} · {user?.employee_code}</div>
              <button
                onClick={() => { setOpen(false); logout(); navigate('/login') }}
                className="flex items-center gap-2 text-sm text-fire-100"
              >
                <LogOut size={16} /> Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export function MobileBottomNav() {
  const mobileItems = [
    { to: '/dashboard', label: 'Home', icon: LayoutDashboard },
    { to: '/assets', label: 'Assets', icon: Flame },
    { to: '/scan', label: 'Scan', icon: ScanLine, primary: true },
    { to: '/inspections', label: 'Inspect', icon: ClipboardCheck },
    { to: '/notifications', label: 'Alerts', icon: Bell },
  ]
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-1 z-40 safe-bottom">
      {mobileItems.map(({ to, label, icon: Icon, primary }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `flex flex-col items-center py-1.5 px-2 text-[11px] ${
              primary
                ? 'text-white bg-fire-700 rounded-full -mt-4 h-14 w-14 justify-center shadow-lg border-2 border-gold-400'
                : isActive ? 'text-fire-700 font-semibold' : 'text-slate-500'
            }`
          }
        >
          <Icon size={primary ? 22 : 20} />
          {!primary && label}
        </NavLink>
      ))}
    </nav>
  )
}
