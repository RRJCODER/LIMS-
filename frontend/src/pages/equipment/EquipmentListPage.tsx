import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { equipmentApi } from '@/api/equipment'
import { Link } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  under_calibration: 'bg-yellow-100 text-yellow-800',
  under_maintenance: 'bg-orange-100 text-orange-800',
  out_of_service: 'bg-red-100 text-red-800',
  retired: 'bg-gray-100 text-gray-600',
}

export default function EquipmentListPage() {
  const { t } = useTranslation()
  const { data: equipment = [], isLoading } = useQuery({ queryKey: ['equipment'], queryFn: equipmentApi.list })
  const { data: dueCal = [] } = useQuery({ queryKey: ['due-calibration'], queryFn: () => equipmentApi.dueCal(30) })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('equipment.title')}</h1>

      {dueCal.length > 0 && (
        <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
          <AlertTriangle size={16} />
          {dueCal.length} equipment item(s) have calibration due in 30 days
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">{t('common.loading')}</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('equipment.labId')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('equipment.name')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('equipment.type')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('equipment.status')}</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{t('equipment.nextCalibration')}</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {equipment.map((eq: any) => (
                <tr key={eq.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="px-4 py-3 font-mono text-sm font-semibold text-gray-700 dark:text-gray-300">{eq.lab_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{eq.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 capitalize">{eq.equipment_type}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[eq.status] || 'bg-gray-100 text-gray-700'}`}>
                      {eq.status}
                    </span>
                  </td>
                  <td className={`px-4 py-3 text-sm ${dueCal.some((d: any) => d.id === eq.id) ? 'text-red-600 font-medium' : 'text-gray-600 dark:text-gray-400'}`}>
                    {eq.next_calibration_date || '—'}
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/equipment/${eq.id}/calibrations`} className="text-xs text-primary-600 hover:text-primary-700 font-medium">
                      {t('equipment.calibrations')} →
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
