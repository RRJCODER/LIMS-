import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { Navigate } from 'react-router-dom'

export default function AppShell() {
  const { theme, sidebarCollapsed } = useUIStore()
  const { user } = useAuthStore()

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  if (!user) return <Navigate to="/login" replace />

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 font-sans">
      <Sidebar />
      <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-200 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
