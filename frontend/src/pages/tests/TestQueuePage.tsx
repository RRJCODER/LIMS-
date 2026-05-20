import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { testsApi } from '@/api/tests'
import { Link } from 'react-router-dom'

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-700',
  in_progress: 'bg-blue-100 text-blue-800',
  results_entered: 'bg-yellow-100 text-yellow-800',
  qc_check: 'bg-purple-100 text-purple-800',
  supervisor_review: 'bg-indigo-100 text-indigo-800',
  approved: 'bg-green-100 text-green-800',
  failed_qc: 'bg-red-100 text-red-800',
  retest_required: 'bg-orange-100 text-orange-800',
}

export default function TestQueuePage() {
  const { t } = useTranslation()
  const { data: tests = [], isLoading } = useQuery({ queryKey: ['tests'], queryFn: () => testsApi.list() })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('tests.title')}</h1>

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">{t('common.loading')}</div>
        ) : tests.length === 0 ? (
          <div className="p-8 text-center text-gray-400">{t('common.noData')}</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">ID</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('tests.status')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.priority')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('common.date')}</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {tests.map((t_: any) => (
                <tr key={t_.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{t_.id.slice(0, 8)}…</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[t_.status] || ''}`}>
                      {t_.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 capitalize">{t_.priority}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{t_.created_at?.slice(0, 10)}</td>
                  <td className="px-4 py-3">
                    <Link to={`/tests/${t_.id}/results/enter`} className="text-xs text-primary-600 hover:text-primary-700 font-medium">
                      {t('tests.enterResults')} →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
