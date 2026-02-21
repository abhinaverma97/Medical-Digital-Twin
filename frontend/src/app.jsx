import React, { useState } from 'react'
import RequirementsForm from './components/RequirementsForm'
import DiagramView from './components/DiagramView'
import SimulationView from './components/SimulationView'
import TraceabilityTable from './components/TraceabilityTable'

const DEVICES = [
  { id: 'ventilator', name: 'Ventilator (Class II)', color: 'border-sky-500' },
  { id: 'pulse_ox', name: 'Pulse Oximeter (Class I)', color: 'border-teal-500' },
  { id: 'dialysis', name: 'Hemodialysis (Class III)', color: 'border-crimson-500' },
]

export default function App() {
  const [view, setView] = useState('requirements')
  const [deviceType, setDeviceType] = useState('ventilator')

  return (
    <div className="min-h-screen flex flex-col premium-gradient">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold bg-gradient-to-r from-sky-400 to-teal-400 bg-clip-text text-transparent">
              VitaBlueprint
            </h1>
            <nav className="flex gap-2">
              <button
                onClick={() => setView('requirements')}
                className={`nav-link ${view === 'requirements' ? 'active' : ''}`}
              >
                Requirements
              </button>
              <button
                onClick={() => setView('design')}
                className={`nav-link ${view === 'design' ? 'active' : ''}`}
              >
                Design Graph
              </button>
              <button
                onClick={() => setView('simulation')}
                className={`nav-link ${view === 'simulation' ? 'active' : ''}`}
              >
                Digital Twin
              </button>
              <button
                onClick={() => setView('trace')}
                className={`nav-link ${view === 'trace' ? 'active' : ''}`}
              >
                Traceability
              </button>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Device:</span>
            <select
              value={deviceType}
              onChange={(e) => setDeviceType(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-sm rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-sky-500 outline-none"
            >
              {DEVICES.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 flex-1">
        <div className="glass-card p-8 min-h-[600px]">
          {view === 'requirements' && <RequirementsForm deviceType={deviceType} />}
          {view === 'design' && <DiagramView deviceType={deviceType} />}
          {view === 'simulation' && <SimulationView deviceType={deviceType} />}
          {view === 'trace' && <TraceabilityTable deviceType={deviceType} />}
        </div>
      </main>

      <footer className="border-t border-slate-800 py-6 text-center">
        <p className="text-sm text-slate-500">
          © {new Date().getFullYear()} VitaBlueprint Engine — Industry-Grade System Engineering
        </p>
      </footer>
    </div>
  )
}
