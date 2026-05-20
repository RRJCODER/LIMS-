import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/api/client'
import { useState } from 'react'
import { FileText, Download } from 'lucide-react'

export default function ReportListPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const [sampleId, setSampleId] = useState('')

  const { data: coas = [], isLoading } = useQuery({
    queryKey: ['coas'],
    queryFn: () => api.get('/api/v1/reports/coa').then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: { sample_id: string }) => api.post('/api/v1/reports/coa', data).then((r) => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['coas'] }); setSampleId('') },
  })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('reports.coa')}</h1>

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
        <h2 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3">{t('reports.generateCoa')}</h2>
        <div className="flex gap-3">
          <input
            value={sampleId}
            onChange={(e) => setSampleId(e.target.value)}
            placeholder="Sample UUID..."
            className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={() => sampleId && createMutation.mutate({ sample_id: sampleId })}
            disabled={!sampleId || createMutation.isPending}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {t('reports.generateCoa')}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">{t('common.loading')}</div>
        ) : coas.length === 0 ? (
          <div className="p-8 text-center text-gray-400">{t('common.noData')}</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('reports.coaNumber')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('common.status')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('reports.issueDate')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('reports.compliance')}</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {coas.map((c: any) => (
                <tr key={c.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="px-4 py-3 font-mono text-sm font-bold text-primary-700 dark:text-primary-300">{c.coa_number}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${c.status === 'issued' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{c.issue_date}</td>
                  <td className="px-4 py-3">
                    {c.overall_compliance && (
                      <span className={`text-xs font-bold px-2 py-1 rounded-full ${c.overall_compliance === 'EVOO' ? 'bg-green-100 text-green-800' : c.overall_compliance === 'VOO' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}`}>
                        {c.overall_compliance}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {c.pdf_path && (
                      <a
                        href={`/api/v1/reports/coa/${c.id}/pdf`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium"
                      >
                        <Download size={12} />
                        {t('reports.downloadPdf')}
                      </a>
                    )}
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
