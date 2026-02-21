import React, { useState, useEffect } from 'react'
import { getTraceability, generateCodeRepo } from '../api'
import { ShieldCheck, Download, Code, CheckCircle2, Clock, AlertCircle, AlertTriangle } from 'lucide-react'

export default function TraceabilityTable({ deviceType }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [genLoading, setGenLoading] = useState(false)
  const [genPath, setGenPath] = useState(null)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const matrix = await getTraceability()
      setData(matrix)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to load traceability data. Ensure you have built the design first.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateCode = async () => {
    setGenLoading(true)
    try {
      const res = await generateCodeRepo()
      setGenPath(res.data.path)
    } catch (err) {
      console.error('CODEGEN_ERROR:', err)
      const detail = err.response?.data?.detail || 'Code generation failed.'
      alert(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      setGenLoading(false)
    }
  }

  useEffect(() => { loadData() }, [deviceType])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="text-teal-400" /> Traceability & Compliance
          </h2>
          <p className="text-slate-400">REQ → Design → Risk → Evidence mapping.</p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={loadData}
            className="btn-outline flex items-center gap-2"
          >
            Refresh
          </button>
          <button
            onClick={handleGenerateCode}
            disabled={genLoading}
            className="btn-primary flex items-center gap-2 bg-teal-600 hover:bg-teal-500 shadow-teal-500/20"
          >
            {genLoading ? <Clock className="animate-spin" size={16} /> : <Code size={16} />}
            Generate Code Repository
          </button>
        </div>
      </div>

      {genPath && (
        <div className="p-4 bg-teal-500/10 border border-teal-500/20 rounded-2xl flex items-center justify-between">
          <p className="text-sm text-teal-400">
            <strong>Repo Generated!</strong> Target path: <code className="text-xs bg-black/30 px-2 py-1 rounded ml-2">{genPath}</code>
          </p>
          <button onClick={() => setGenPath(null)} className="text-teal-400 hover:text-white">&times;</button>
        </div>
      )}

      {error && (
        <div className="p-4 bg-crimson-500/10 border border-crimson-500/20 rounded-2xl flex items-center gap-3">
          <AlertTriangle className="text-crimson-400" size={20} />
          <p className="text-sm text-crimson-400">{error}</p>
        </div>
      )}

      {data ? (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-slate-500 uppercase text-xs font-bold tracking-widest">
              <tr>
                <th className="px-6 py-4">REQ ID</th>
                <th className="px-6 py-4">Hazard</th>
                <th className="px-6 py-4">Risk Status</th>
                <th className="px-6 py-4">Compliance Status</th>
                <th className="px-6 py-4">Verification / Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {data.map((entry, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-mono text-sky-400">{entry['Requirement ID']}</td>
                  <td className="px-6 py-4 text-slate-300">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">{entry['Type']}</span>
                    {entry['Title']}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-slate-400 text-xs">{entry['Hazard']}</span>
                      <div className="flex gap-2">
                        <span className="text-[9px] px-1.5 py-0.5 bg-slate-800 rounded font-bold text-slate-400">P: {entry['Probability']}</span>
                        <span className="text-[9px] px-1.5 py-0.5 bg-slate-800 rounded font-bold text-slate-400">S: {entry['Severity']}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {entry['Risk Acceptability'] === 'ACCEPTABLE' ? (
                        <CheckCircle2 size={16} className="text-teal-500" />
                      ) : (
                        <AlertCircle size={16} className="text-amber-500" />
                      )}
                      <span className="text-slate-400 text-xs">{entry['Risk Acceptability']}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-500 italic max-w-xs">
                    <span className="text-slate-400 block not-italic font-medium">{entry['Verification Method']}</span>
                    {entry['Evidence']}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="py-20 text-center text-slate-500">
          {loading ? 'Crunching compliance data...' : 'No traceability data available. Build design and run simulation first.'}
        </div>
      )}
    </div>
  )
}