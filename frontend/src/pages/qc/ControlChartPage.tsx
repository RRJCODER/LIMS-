import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { qcApi } from '@/api/qc'
import {
  ComposedChart, Line, ReferenceLine, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Dot
} from 'recharts'

function ViolationDot(props: any) {
  const { cx, cy, payload } = props
  if (!payload.violation) return null
  return <circle cx={cx} cy={cy} r={6} fill="#ef4444" stroke="white" strokeWidth={2} />
}

export default function ControlChartPage() {
  const { chart_id } = useParams<{ chart_id: string }>()
  const { t } = useTranslation()
  const { data, isLoading } = useQuery({
    queryKey: ['chart-data', chart_id],
    queryFn: () => qcApi.chartData(chart_id!),
    enabled: !!chart_id,
  })

  if (isLoading) return <div className="p-8 text-center text-gray-400">{t('common.loading')}</div>
  if (!data) return null

  const { chart, data: points } = data

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('qc.controlChart')}</h1>

      {/* Chart stats */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
        {[
          { label: t('qc.mean'), value: chart.mean?.toFixed(3), color: 'text-gray-700' },
          { label: t('qc.sd'), value: chart.sd?.toFixed(3), color: 'text-gray-500' },
          { label: t('qc.ucl'), value: chart.ucl?.toFixed(3), color: 'text-red-600' },
          { label: t('qc.lcl'), value: chart.lcl?.toFixed(3), color: 'text-red-600' },
          { label: t('qc.uwl'), value: chart.uwl?.toFixed(3), color: 'text-orange-500' },
          { label: t('qc.lwl'), value: chart.lwl?.toFixed(3), color: 'text-orange-500' },
        ].map((item) => (
          <div key={item.label} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3 text-center">
            <p className="text-xs text-gray-500">{item.label}</p>
            <p className={`text-lg font-bold ${item.color}`}>{item.value}</p>
          </div>
        ))}
      </div>

      {/* Levey-Jennings chart */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
        <h2 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-4">Levey-Jennings</h2>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={points} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => v.toFixed(4)} />

            {/* Control lines */}
            <ReferenceLine y={chart.ucl} stroke="#ef4444" strokeDasharray="6 3" label={{ value: 'UCL +3SD', position: 'right', fontSize: 10, fill: '#ef4444' }} />
            <ReferenceLine y={chart.uwl} stroke="#f97316" strokeDasharray="4 4" label={{ value: '+2SD', position: 'right', fontSize: 10, fill: '#f97316' }} />
            <ReferenceLine y={chart.mean} stroke="#2d6a2d" strokeWidth={2} label={{ value: 'Mean', position: 'right', fontSize: 10, fill: '#2d6a2d' }} />
            <ReferenceLine y={chart.lwl} stroke="#f97316" strokeDasharray="4 4" label={{ value: '-2SD', position: 'right', fontSize: 10, fill: '#f97316' }} />
            <ReferenceLine y={chart.lcl} stroke="#ef4444" strokeDasharray="6 3" label={{ value: 'LCL -3SD', position: 'right', fontSize: 10, fill: '#ef4444' }} />

            <Line
              type="monotone"
              dataKey="value"
              stroke="#2d6a2d"
              strokeWidth={1.5}
              dot={(props) => <ViolationDot {...props} />}
              activeDot={{ r: 5 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Data table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
              <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 uppercase">{t('common.date')}</th>
              <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 uppercase">{t('tests.result')}</th>
              <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 uppercase">Z-Score</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p: any) => (
              <tr key={p.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <td className="px-4 py-2 text-gray-700 dark:text-gray-300">{p.date?.slice(0, 10)}</td>
                <td className="px-4 py-2 font-mono text-gray-900 dark:text-white">{p.value?.toFixed(4)}</td>
                <td className={`px-4 py-2 font-mono ${Math.abs(p.z_score) > 3 ? 'text-red-600 font-bold' : Math.abs(p.z_score) > 2 ? 'text-orange-600' : 'text-gray-600'}`}>
                  {p.z_score?.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
