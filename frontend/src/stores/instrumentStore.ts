import { create } from 'zustand'

interface WeightReading {
  value: number
  unit: string
  stable: boolean
  timestamp: string
}

interface InstrumentState {
  connected: boolean
  lastWeight: WeightReading | null
  wsError: string | null
  setConnected: (v: boolean) => void
  setLastWeight: (r: WeightReading) => void
  setWsError: (e: string | null) => void
}

export const useInstrumentStore = create<InstrumentState>((set) => ({
  connected: false,
  lastWeight: null,
  wsError: null,
  setConnected: (v) => set({ connected: v }),
  setLastWeight: (r) => set({ lastWeight: r }),
  setWsError: (e) => set({ wsError: e }),
}))
