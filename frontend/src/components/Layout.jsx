import React from 'react'
import { Navigate } from 'react-router-dom'
import { Sidebar, MobileHeader, MobileBottomNav } from './Nav'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ children, roles }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) {
    return (
      <Layout>
        <div className="p-8 text-center text-slate-500">
          You don't have permission to view this page.
        </div>
      </Layout>
    )
  }
  return children
}

export default function Layout({ children }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 min-w-0 flex flex-col">
        <MobileHeader />
        <main className="flex-1 pb-24 md:pb-0 w-full min-w-0">{children}</main>
      </div>
      <MobileBottomNav />
    </div>
  )
}
