import { useEffect, useRef, useCallback } from 'react'
import { useInstrumentStore } from '@/stores/instrumentStore'

export function useInstrumentWS(deviceId: string | null) {
  const ws = useRef<WebSocket | null>(null)
  const { setConnected, setLastWeight, setWsError } = useInstrumentStore()
  const reconnectDelay = useRef(1000)
  const stopped = useRef(false)

  const connect = useCallback(() => {
    if (!deviceId || stopped.current) return
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/api/v1/instruments/ws/${deviceId}`
    ws.current = new WebSocket(wsUrl)

    ws.current.onopen = () => {
      setConnected(true)
      setWsError(null)
      reconnectDelay.current = 1000
    }

    ws.current.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data)
        if (data.value !== undefined) {
          setLastWeight({ value: data.value, unit: data.unit || 'g', stable: data.stable ?? true, timestamp: new Date().toISOString() })
        }
      } catch {}
    }

    ws.current.onclose = () => {
      setConnected(false)
      if (!stopped.current) {
        setTimeout(connect, reconnectDelay.current)
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000)
      }
    }

    ws.current.onerror = (e) => {
      setWsError('WebSocket connection error')
    }
  }, [deviceId, setConnected, setLastWeight, setWsError])

  useEffect(() => {
    stopped.current = false
    connect()
    return () => {
      stopped.current = true
      ws.current?.close()
    }
  }, [connect])

  const sendCommand = useCallback((cmd: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(cmd)
    }
  }, [])

  return { sendCommand }
}
