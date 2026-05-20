import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { FlaskConical, AlertTriangle, Wrench, Clock, TestTube2 } from 'lucide-react'

interface KPICardProps {
  title: string
  value: number | string
  icon: React.ComponentType<any>
  color: string
  alert?: boolean
}

function KPICard({ title, value, icon: Icon, color, alert }: KPICardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl p-5 border ${alert && Number(value) > 0 ? 'border-red-200 dark:border-red-800' : 'border-gray-200 dark:border-gray-700'} shadow-sm`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
          <p className={`text-3xl font-bold mt-1 ${alert && Number(value) > 0 ? 'text-red-600' : 'text-gray-900 dark:text-white'}`}>
            {value}
          </p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon size={22} className="text-white" />
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const { data: kpis, isLoading: kpiLoading } = useQuery({ queryKey: ['kpis'], queryFn: dashboardApi.kpis, refetchInterval: 30000 })
  const { data: throughput } = useQuery({ queryKey: ['throughput'], queryFn: () => dashboardApi.throughput(30) })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('dashboard.title')}</h1>

      {/* KPI Cards */}
      {kpiLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 bg-gray-100 dark:bg-gray-700 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <KPICard title={t('dashboard.pendingSamples')} value={kpis?.pending_samples ?? 0} icon={FlaskConical} color="bg-blue-500" />
          <KPICard title={t('dashboard.overdueSamples')} value={kpis?.overdue_samples ?? 0} icon={Clock} color="bg-red-500" alert />
          <KPICard title={t('dashboard.openViolations')} value={kpis?.open_qc_violations ?? 0} icon={AlertTriangle} color="bg-orange-500" alert />
          <KPICard title={t('dashboard.calibrationsDue')} value={kpis?.calibrations_due_30d ?? 0} icon={Wrench} color="bg-yellow-500" />
          <KPICard title={t('dashboard.pendingTests')} value={kpis?.pending_tests ?? 0} icon={TestTube2} color="bg-primary-500" />
        </div>
      )}

      {/* Throughput chart */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
        <h2 className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-4">{t('dashboard.sampleThroughput')} (30d)</h2>
        {throughput ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={throughput} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#2d6a2d" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-400 text-sm">{t('common.noData')}</div>
        )}
      </div>
    </div>
  )
}
