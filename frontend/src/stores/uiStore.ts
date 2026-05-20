import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
  language: 'es' | 'en'
  toggleTheme: () => void
  setSidebarCollapsed: (v: boolean) => void
  setLanguage: (lang: 'es' | 'en') => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarCollapsed: false,
      language: 'es',
      toggleTheme: () => set((s) => ({ theme: s.theme === 'light' ? 'dark' : 'light' })),
      setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
      setLanguage: (lang) => {
        localStorage.setItem('lims-language', lang)
        set({ language: lang })
      },
    }),
    { name: 'lims-ui' }
  )
)
