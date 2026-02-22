import React, { useState, useEffect } from 'react'
import { buildDesign } from '../api'

export default function DiagramView({ deviceType }) {
  const [diagrams, setDiagrams] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('logical')

  const handleBuild = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await buildDesign(deviceType)
      console.log('BUILD_RESULT:', res.data)
      if (res.data.error) {
        setError(res.data.error)
      } else {
        setDiagrams(res.data)
      }
    } catch (err) {
      console.error('BUILD_ERROR:', err)
      setError('Design build failed. Ensure you have added requirements first.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">System Design Graph</h2>
          <p className="text-slate-400">Deterministic decomposition of {deviceType} subsystems.</p>
        </div>
        <button
          onClick={handleBuild}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Analyzing Engineering Requirements...' : 'Build Design Graph'}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-crimson-500/10 border border-crimson-500/20 rounded-xl text-crimson-400 text-sm">
          {error}
        </div>
      )}

      {diagrams && diagrams.hld && (
        <div className="space-y-4">
          <div className="flex gap-2 p-1 bg-slate-900 rounded-lg w-fit border border-slate-800">
            <button
              onClick={() => setActiveTab('logical')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'logical' ? 'bg-slate-800 text-sky-400' : 'text-slate-500 hover:text-slate-300'}`}
            >
              Logical Diagram
            </button>
            <button
              onClick={() => setActiveTab('hld')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'hld' ? 'bg-slate-800 text-sky-400' : 'text-slate-500 hover:text-slate-300'}`}
            >
              High-Level (HLD)
            </button>
            {diagrams.lld && (
              <button
                onClick={() => setActiveTab('lld')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'lld' ? 'bg-slate-800 text-sky-400' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Low-Level (LLD)
              </button>
            )}
          </div>

          <div className={`rounded-2xl border border-slate-800 p-6 flex justify-center transition-colors duration-500 ${activeTab === 'lld' ? 'bg-[#1E293B]' : 'bg-slate-950/50'}`}>
            <div
              className={`max-w-full overflow-auto transition-all duration-500 ${activeTab === 'lld' ? '' : 'invert opacity-90'}`}
              dangerouslySetInnerHTML={{
                __html: diagrams[activeTab]?.svg || '<p class="text-slate-500">Generating schematic...</p>'
              }}
            />
          </div>

          {activeTab === 'lld' && (
            <div className="flex gap-4 justify-center">
              <span className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                <span className="w-2 h-2 rounded-full bg-sky-400"></span> Communication Bus
              </span>
              <span className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                <span className="w-2 h-2 rounded-full bg-slate-100"></span> Physical Component
              </span>
            </div>
          )}
        </div>
      )}

      {!diagrams && !loading && (
        <div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-slate-800 rounded-3xl opacity-50">
          <p className="text-slate-400">Design graph not built yet. Click the button above to generate.</p>
        </div>
      )}
    </div>
  )
}