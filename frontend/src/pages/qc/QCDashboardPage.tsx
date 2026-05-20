import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { qcApi } from '@/api/qc'
import { Link } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'

export default function QCDashboardPage() {
  const { t } = useTranslation()
  const { data: violations = [] } = useQuery({ queryKey: ['qc-violations-open'], queryFn: () => qcApi.violations(false) })
  const { data: charts = [] } = useQuery({ queryKey: ['qc-charts'], queryFn: qcApi.charts })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('qc.title')}</h1>

      {violations.length > 0 && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-red-600" />
            <h2 className="font-semibold text-red-800">{violations.length} {t('qc.violations')}</h2>
          </div>
          <div className="space-y-2">
            {violations.slice(0, 5).map((v: any) => (
              <div key={v.id} className="flex items-center justify-between bg-white rounded-lg px-3 py-2 text-sm">
                <span className="font-medium text-red-700">Rule {v.rule_violated}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${v.severity === 'reject' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {v.severity}
                </span>
                <span className="text-gray-500 text-xs">{v.created_at?.slice(0, 10)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
        <h2 className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-4">{t('qc.controlChart')}s</h2>
        {charts.length === 0 ? (
          <p className="text-gray-400 text-sm">{t('common.noData')}</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {charts.map((c: any) => (
              <Link
                key={c.id}
                to={`/qc/charts/${c.id}`}
                className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-primary-400 transition-colors"
              >
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{c.qc_type}</p>
                <p className="text-xs text-gray-500 mt-1">Mean: {c.mean?.toFixed(3)} ± {c.sd?.toFixed(3)}</p>
                <p className="text-xs text-gray-400 mt-0.5">{c.n_points} points</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
