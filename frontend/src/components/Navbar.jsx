import React from 'react'

export default function Navbar({ onNavigate }) {
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-indigo-600 to-sky-400 rounded p-2 text-white font-bold">VB</div>
          <div>
            <div className="text-lg font-semibold">VitaBlueprint</div>
            <div className="text-xs text-slate-400">System Design & Digital Twin</div>
          </div>
        </div>

        <nav className="flex items-center gap-3">
          <button onClick={() => onNavigate('design')} className="px-3 py-2 rounded hover:bg-slate-50">Design</button>
          <button onClick={() => onNavigate('requirements')} className="px-3 py-2 rounded hover:bg-slate-50">Requirements</button>
          <button onClick={() => onNavigate('simulation')} className="px-3 py-2 rounded hover:bg-slate-50">Simulation</button>
          <button onClick={() => onNavigate('trace')} className="px-3 py-2 rounded hover:bg-slate-50">Traceability</button>
        </nav>
      </div>
    </header>
  )
}
