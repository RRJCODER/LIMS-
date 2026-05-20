import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '@/api/settings'
import { useDropzone } from 'react-dropzone'
import { Upload, Check } from 'lucide-react'

function LabProfileSection() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const { data: profile } = useQuery({ queryKey: ['lab-profile'], queryFn: settingsApi.labProfile })
  const [form, setForm] = useState<any>(null)
  const [saved, setSaved] = useState(false)

  const current = form || profile || {}

  const updateMutation = useMutation({
    mutationFn: settingsApi.updateLabProfile,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['lab-profile'] }); setSaved(true); setTimeout(() => setSaved(false), 2000) },
  })

  const logoMutation = useMutation({
    mutationFn: settingsApi.uploadLogo,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['lab-profile'] }),
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => files[0] && logoMutation.mutate(files[0]),
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.svg'] },
    multiple: false,
  })

  const fields = [
    { key: 'lab_name', label: t('settings.labName') },
    { key: 'accreditation_number', label: t('settings.accreditation') },
    { key: 'lab_address', label: t('settings.address') },
    { key: 'lab_phone', label: t('settings.phone') },
    { key: 'lab_email', label: t('settings.email') },
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
      <h2 className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-5">{t('settings.labProfile')}</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {fields.map(({ key, label }) => (
          <div key={key}>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{label}</label>
            <input
              value={current[key] || ''}
              onChange={(e) => setForm({ ...current, [key]: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        ))}
      </div>

      {/* Logo upload */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">{t('settings.logo')}</label>
        <div className="flex items-center gap-4">
          {current.logo_url ? (
            <img src={current.logo_url} alt="Lab logo" className="h-16 w-16 object-contain border border-gray-200 rounded-lg p-1" />
          ) : (
            <div className="h-16 w-16 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-400 text-2xl">🫒</div>
          )}
          <div
            {...getRootProps()}
            className={`flex-1 border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload size={18} className="mx-auto mb-1 text-gray-400" />
            <p className="text-xs text-gray-500">{t('settings.uploadLogo')} (PNG, JPG, SVG)</p>
          </div>
        </div>
      </div>

      <button
        onClick={() => updateMutation.mutate(current)}
        disabled={updateMutation.isPending}
        className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
      >
        {saved ? <Check size={16} /> : null}
        {saved ? '✓ ' : ''}{t('common.save')}
      </button>
    </div>
  )
}

export default function SettingsPage() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('settings.title')}</h1>
      <LabProfileSection />
    </div>
  )
}
