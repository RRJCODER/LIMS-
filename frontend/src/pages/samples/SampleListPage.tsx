import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { samplesApi } from '@/api/samples'
import { Link } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'
import { useState } from 'react'

const statusColors: Record<string, string> = {
  received: 'bg-blue-100 text-blue-800',
  in_preparation: 'bg-yellow-100 text-yellow-800',
  in_analysis: 'bg-orange-100 text-orange-800',
  qc_review: 'bg-purple-100 text-purple-800',
  supervisor_review: 'bg-indigo-100 text-indigo-800',
  approved: 'bg-green-100 text-green-800',
  reported: 'bg-teal-100 text-teal-800',
  archived: 'bg-gray-100 text-gray-700',
  rejected: 'bg-red-100 text-red-800',
}

export default function SampleListPage() {
  const { t } = useTranslation()
  const [search, setSearch] = useState('')
  const { data: samples = [], isLoading } = useQuery({ queryKey: ['samples'], queryFn: () => samplesApi.list() })

  const filtered = samples.filter((s: any) =>
    s.lab_code.toLowerCase().includes(search.toLowerCase()) ||
    s.client_name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('samples.title')}</h1>
        <Link
          to="/samples/new"
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Plus size={16} />
          {t('samples.newSample')}
        </Link>
      </div>

      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t('common.search')}
          className="w-full pl-9 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">{t('common.loading')}</div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-gray-400">{t('common.noData')}</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.labCode')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.client')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.matrix')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.status')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.receiptDate')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('samples.priority')}</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s: any) => (
                <tr key={s.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-sm font-semibold text-primary-700 dark:text-primary-300">{s.lab_code}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{s.client_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {t(`samples.matrices.${s.matrix}`) || s.matrix}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[s.status] || 'bg-gray-100 text-gray-700'}`}>
                      {t(`samples.statuses.${s.status}`) || s.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{s.receipt_date}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s.priority === 'urgent' ? 'bg-red-100 text-red-700' : s.priority === 'rush' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'}`}>
                      {s.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/samples/${s.id}`} className="text-xs text-primary-600 hover:text-primary-700 font-medium">
                      {t('common.view')} →
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
