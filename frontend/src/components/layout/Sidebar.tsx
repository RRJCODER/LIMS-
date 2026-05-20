import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useUIStore } from '@/stores/uiStore'
import { useQuery } from '@tanstack/react-query'
import { settingsApi } from '@/api/settings'
import {
  LayoutDashboard, FlaskConical, TestTube2, Activity, Wrench,
  FileText, BarChart3, Cpu, Users, Settings, ChevronLeft, ChevronRight
} from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, key: 'dashboard' },
  { to: '/samples', icon: FlaskConical, key: 'samples' },
  { to: '/tests', icon: TestTube2, key: 'tests' },
  { to: '/qc', icon: Activity, key: 'qc' },
  { to: '/equipment', icon: Wrench, key: 'equipment' },
  { to: '/documents', icon: FileText, key: 'documents' },
  { to: '/reports/coa', icon: BarChart3, key: 'reports' },
  { to: '/instruments', icon: Cpu, key: 'instruments' },
  { to: '/users', icon: Users, key: 'users' },
  { to: '/settings', icon: Settings, key: 'settings' },
]

export default function Sidebar() {
  const { t } = useTranslation()
  const { sidebarCollapsed, setSidebarCollapsed } = useUIStore()
  const { data: profile } = useQuery({ queryKey: ['lab-profile'], queryFn: settingsApi.labProfile })

  return (
    <aside className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-200 z-30 ${sidebarCollapsed ? 'w-16' : 'w-64'}`}>
      {/* Logo / Lab name */}
      <div className="flex items-center gap-3 px-4 py-4 border-b border-gray-200 dark:border-gray-700 min-h-[64px]">
        {profile?.logo_url ? (
          <img src={profile.logo_url} alt="Logo" className="h-8 w-8 object-contain flex-shrink-0" />
        ) : (
          <span className="text-2xl flex-shrink-0">🫒</span>
        )}
        {!sidebarCollapsed && (
          <span className="font-semibold text-sm text-primary-700 dark:text-primary-300 leading-tight line-clamp-2">
            {profile?.lab_name || 'Olive Oil LIMS'}
          </span>
        )}
      </div>

      {/* Nav items */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, key }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`
            }
          >
            <Icon size={18} className="flex-shrink-0" />
            {!sidebarCollapsed && <span>{t(`nav.${key}`)}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="flex items-center justify-center p-3 border-t border-gray-200 dark:border-gray-700 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
      >
        {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>
    </aside>
  )
}
