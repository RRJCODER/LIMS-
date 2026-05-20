import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import { Sun, Moon, Globe, LogOut, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import i18n from '@/i18n'

export default function TopBar() {
  const { t } = useTranslation()
  const { user, logout } = useAuthStore()
  const { theme, toggleTheme, language, setLanguage } = useUIStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleLanguage = () => {
    const newLang = language === 'es' ? 'en' : 'es'
    setLanguage(newLang)
    i18n.changeLanguage(newLang)
  }

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
          ISO 17025 LIMS
        </span>
      </div>

      <div className="flex items-center gap-3">
        {/* Language toggle */}
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-400"
          title={t('settings.language')}
        >
          <Globe size={14} />
          <span className="uppercase font-medium">{language}</span>
        </button>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-400"
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        {/* User menu */}
        <div className="flex items-center gap-2 pl-3 border-l border-gray-200 dark:border-gray-700">
          <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
            <User size={16} className="text-primary-700 dark:text-primary-300" />
          </div>
          {user && (
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 leading-none">{user.full_name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500 capitalize mt-0.5">{user.role}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-500 hover:text-red-500"
            title={t('auth.logout')}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  )
}
