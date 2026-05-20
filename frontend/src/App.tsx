import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './i18n'
import AppShell from './components/layout/AppShell'
import LoginPage from './pages/auth/LoginPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import SampleListPage from './pages/samples/SampleListPage'
import TestQueuePage from './pages/tests/TestQueuePage'
import QCDashboardPage from './pages/qc/QCDashboardPage'
import ControlChartPage from './pages/qc/ControlChartPage'
import EquipmentListPage from './pages/equipment/EquipmentListPage'
import ReportListPage from './pages/reports/ReportListPage'
import InstrumentConsolePage from './pages/instruments/InstrumentConsolePage'
import SettingsPage from './pages/settings/SettingsPage'
import { useUIStore } from './stores/uiStore'
import { useEffect } from 'react'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30000, retry: 1 } },
})

function ThemeApplier() {
  const { theme } = useUIStore()
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])
  return null
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeApplier />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AppShell />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/samples" element={<SampleListPage />} />
            <Route path="/tests" element={<TestQueuePage />} />
            <Route path="/qc" element={<QCDashboardPage />} />
            <Route path="/qc/charts/:chart_id" element={<ControlChartPage />} />
            <Route path="/equipment" element={<EquipmentListPage />} />
            <Route path="/reports/coa" element={<ReportListPage />} />
            <Route path="/instruments" element={<InstrumentConsolePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
