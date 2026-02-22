import React, { useState, useEffect } from 'react'
import { getTraceability, generateCodeRepo } from '../api'
import { ShieldCheck, Code, CheckCircle2, Clock, AlertCircle, AlertTriangle, RefreshCw } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

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
    <div className="space-y-6 w-full">
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Traceability & Compliance</h2>
          <p className="text-muted-foreground text-sm mt-1">REQ → Design → Risk → Evidence mapping.</p>
        </div>

        <div className="flex gap-4">
          <Button variant="outline" onClick={loadData} className="gap-2 bg-transparent border-white/10 hover:bg-white/5">
            <RefreshCw className="h-4 w-4" /> Refresh
          </Button>
          <Button onClick={handleGenerateCode} disabled={genLoading} className="gap-2 bg-teal-600 hover:bg-teal-700 text-white border-transparent">
            {genLoading ? <Clock className="h-4 w-4 animate-spin" /> : <Code className="h-4 w-4" />}
            Generate Code Repository
          </Button>
        </div>
      </div>

      {genPath && (
        <div className="p-4 border border-teal-500/50 bg-teal-500/10 rounded-xl flex items-center justify-between text-sm text-teal-500 font-medium">
          <span>
            <strong>Repo Generated!</strong> Target path: <code className="text-xs bg-black/30 px-2 py-1 rounded ml-2 text-teal-400">{genPath}</code>
          </span>
          <button onClick={() => setGenPath(null)} className="text-teal-500/70 hover:text-teal-400">&times;</button>
        </div>
      )}

      {error && (
        <div className="p-4 border border-destructive/50 bg-destructive/10 rounded-xl flex items-center gap-3 text-sm text-destructive font-medium">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      <div className="border border-white/5 rounded-2xl overflow-hidden bg-[#1a1a1a]">
        {data ? (
          <Table>
            <TableHeader className="bg-[#2f2f2f]/30 border-b border-white/5">
              <TableRow className="hover:bg-transparent text-[11px] font-bold tracking-widest uppercase border-none">
                <TableHead className="w-[120px] text-[#878787]">REQ ID</TableHead>
                <TableHead className="text-[#878787]">Hazard</TableHead>
                <TableHead className="w-[150px] text-[#878787]">Risk Status</TableHead>
                <TableHead className="w-[180px] text-[#878787]">Compliance</TableHead>
                <TableHead className="text-right w-[250px] text-[#878787]">Verification / Evidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((entry, idx) => (
                <TableRow key={idx} className="border-b border-white/5 hover:bg-white/5 data-[state=selected]:bg-muted">
                  <TableCell className="font-mono text-sky-400 text-xs align-top">
                    {entry['Requirement ID']}
                  </TableCell>
                  <TableCell className="align-top">
                    <span className="text-[10px] text-[#878787] block uppercase font-bold tracking-wider mb-1">
                      {entry['Type']}
                    </span>
                    <span className="text-sm text-[#ececec]">{entry['Title']}</span>
                  </TableCell>
                  <TableCell className="align-top">
                    <div className="flex flex-col gap-1.5">
                      <span className="text-[#878787] text-xs leading-tight line-clamp-2">
                        {entry['Hazard']}
                      </span>
                      <div className="flex gap-2 mt-1">
                        <span className="text-[10px] px-1.5 py-0.5 bg-[#2f2f2f] rounded font-bold text-[#878787]">
                          P: {entry['Probability']}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 bg-[#2f2f2f] rounded font-bold text-[#878787]">
                          S: {entry['Severity']}
                        </span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="align-top">
                    <div className="flex items-center gap-2">
                      {entry['Risk Acceptability'] === 'ACCEPTABLE' ? (
                        <CheckCircle2 className="h-4 w-4 text-teal-500 flex-shrink-0" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-amber-500 flex-shrink-0" />
                      )}
                      <span className="text-sm font-medium text-[#ececec]">
                        {entry['Risk Acceptability']}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right align-top">
                    <div className="flex flex-col gap-1 text-xs text-[#878787]">
                      <span className="font-medium text-[#ececec]">
                        {entry['Verification Method']}
                      </span>
                      <span className="italic line-clamp-3">
                        {entry['Evidence']}
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <div className="flex flex-col items-center justify-center text-center py-32 text-muted-foreground bg-transparent">
            <ShieldCheck className="h-12 w-12 opacity-20 mb-4" />
            <p className="text-sm font-medium">
              {loading ? 'Crunching compliance data...' : 'No traceability data available.'}
            </p>
            {!loading && (
              <p className="text-xs mt-1">Build design and run the simulation first.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}