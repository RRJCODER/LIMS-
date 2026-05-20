import { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { equipmentApi } from '@/api/equipment'
import { useInstrumentWS } from '@/hooks/useInstrumentWS'
import { useInstrumentStore } from '@/stores/instrumentStore'
import { useDropzone } from 'react-dropzone'
import api from '@/api/client'
import { Wifi, WifiOff, Upload, RefreshCw } from 'lucide-react'

function BalanceWidget({ deviceId }: { deviceId: string }) {
  const { t } = useTranslation()
  const { sendCommand } = useInstrumentWS(deviceId)
  const { connected, lastWeight, wsError } = useInstrumentStore()

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-700 dark:text-gray-300">{t('instruments.liveWeight')}</h3>
        <div className={`flex items-center gap-1.5 text-xs ${connected ? 'text-green-600' : 'text-red-500'}`}>
          {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Live reading display */}
      <div className="text-center py-6 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-xl mb-4">
        {lastWeight ? (
          <>
            <p className="text-4xl font-bold font-mono text-gray-900 dark:text-white">
              {lastWeight.value.toFixed(4)}
            </p>
            <p className="text-sm text-gray-500 mt-1">{lastWeight.unit} {lastWeight.stable ? '⚖️ Stable' : '〰 Unstable'}</p>
          </>
        ) : (
          <p className="text-gray-400 text-sm">—</p>
        )}
      </div>

      {wsError && <p className="text-xs text-red-500 mb-3">{wsError}</p>}

      <div className="grid grid-cols-3 gap-2">
        <button
          onClick={() => sendCommand('TARE')}
          className="py-2 px-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-sm font-medium rounded-lg transition-colors"
        >
          {t('instruments.tare')}
        </button>
        <button
          onClick={() => sendCommand('READ')}
          className="py-2 px-3 bg-primary-50 dark:bg-primary-900/30 hover:bg-primary-100 text-primary-700 dark:text-primary-300 text-sm font-medium rounded-lg transition-colors"
        >
          {t('instruments.read')}
        </button>
        <button
          onClick={() => {/* copy to clipboard / field */}}
          className="py-2 px-3 bg-green-50 hover:bg-green-100 text-green-700 text-sm font-medium rounded-lg transition-colors"
        >
          {t('instruments.sendToField')}
        </button>
      </div>
    </div>
  )
}

function GCImportWidget() {
  const { t } = useTranslation()
  const [testRequestId, setTestRequestId] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const onDrop = useCallback(async (files: File[]) => {
    if (!files[0] || !testRequestId) return
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', files[0])
      const { data } = await api.post(`/api/v1/instruments/gc/import?test_request_id=${testRequestId}`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
    } catch (e: any) {
      setResult({ error: e.response?.data?.detail || 'Import failed' })
    } finally {
      setLoading(false)
    }
  }, [testRequestId])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/octet-stream': ['.jdx', '.dx'], 'text/csv': ['.csv'] },
    multiple: false,
  })

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
      <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-4">{t('instruments.gcImport')}</h3>

      <div className="mb-3">
        <label className="block text-xs font-medium text-gray-500 mb-1">Test Request ID</label>
        <input
          value={testRequestId}
          onChange={(e) => setTestRequestId(e.target.value)}
          placeholder="uuid..."
          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload size={24} className="mx-auto mb-2 text-gray-400" />
        <p className="text-sm text-gray-500">{t('instruments.dragDrop')}</p>
        {loading && <p className="text-xs text-primary-600 mt-2">{t('common.loading')}</p>}
      </div>

      {result && !result.error && (
        <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm font-medium text-green-700 dark:text-green-400">
            ✓ {result.peaks_found} peaks imported
          </p>
          <div className="mt-2 max-h-32 overflow-y-auto">
            {result.peaks?.slice(0, 5).map((p: any, i: number) => (
              <p key={i} className="text-xs text-green-600 font-mono">
                RT: {p.rt?.toFixed(2)} min | {p.name || 'Unknown'} | {p.area_pct?.toFixed(2)}%
              </p>
            ))}
            {result.peaks?.length > 5 && <p className="text-xs text-green-500">...and {result.peaks.length - 5} more</p>}
          </div>
        </div>
      )}

      {result?.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{result.error}</p>
        </div>
      )}
    </div>
  )
}

export default function InstrumentConsolePage() {
  const { t } = useTranslation()
  const { data: devices = [] } = useQuery({ queryKey: ['instrument-devices'], queryFn: equipmentApi.list })

  const balances = devices.filter((d: any) => d.comm_protocol === 'sics')

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('instruments.title')}</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {balances.length > 0 ? (
          balances.map((b: any) => (
            <div key={b.id}>
              <p className="text-sm font-medium text-gray-500 mb-2">{b.name} ({b.lab_id})</p>
              <BalanceWidget deviceId={b.id} />
            </div>
          ))
        ) : (
          <BalanceWidget deviceId="demo-balance" />
        )}
        <GCImportWidget />
      </div>
    </div>
  )
}
