import React, { useState } from 'react'
import { runSimulation, runFaultySimulation } from '../api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Activity, AlertTriangle, Zap, Play, RotateCcw } from 'lucide-react'

export default function SimulationView({ deviceType }) {
	const [data, setData] = useState(null)
	const [loading, setLoading] = useState(false)
	const [fidelity, setFidelity] = useState('L2')
	const [faultParam, setFaultParam] = useState('')
	const [faultBias, setFaultBias] = useState(0.2)
	const [activeFault, setActiveFault] = useState(null)

	const handleRun = async () => {
		setLoading(true)
		setActiveFault(null)
		try {
			const res = await runSimulation(deviceType, 50, fidelity)
			setData(res.data.snapshots)
		} catch (err) {
			console.error(err)
		} finally {
			setLoading(false)
		}
	}

	const handleRunFault = async () => {
		if (!faultParam) return alert('Please specify a parameter to inject a fault into.')
		setLoading(true)
		try {
			const res = await runFaultySimulation(deviceType, faultParam, faultBias, 50)
			if (res.data.error) throw new Error(res.data.error)
			setData(res.data.snapshots)
			setActiveFault({ parameter: faultParam, bias: faultBias })
		} catch (err) {
			alert(`Fault Injection Failed: ${err.message}`)
		} finally {
			setLoading(false)
		}
	}

	// Extract keys for chart (excluding 't')
	const chartKeys = data && data.length > 0
		? Object.keys(data[0].values).filter(k => typeof data[0].values[k] === 'number')
		: []

	const chartData = data?.map(snap => ({
		time: snap.t,
		...snap.values
	}))

	const colors = ['#38bdf8', '#2dd4bf', '#f43f5e', '#fbbf24', '#a855f7']

	return (
		<div className="space-y-8">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold text-white flex items-center gap-2">
						<Activity className="text-sky-400" /> Digital Twin Dashboard
					</h2>
					<p className="text-slate-400">Real-time simulation and safety validation for {deviceType}.</p>
				</div>

				<div className="flex gap-4">
					<div className="flex bg-slate-900 rounded-xl p-1 border border-slate-800">
						{['L1', 'L2', 'L3'].map(l => (
							<button
								key={l}
								onClick={() => setFidelity(l)}
								className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${fidelity === l ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' : 'text-slate-500 hover:text-slate-300'}`}
							>
								{l}
							</button>
						))}
					</div>
					<button
						onClick={handleRun}
						disabled={loading}
						className="btn-primary flex items-center gap-2"
					>
						<Play size={16} /> Run Normal
					</button>
				</div>
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
				{/* Controls Panel */}
				<div className="lg:col-span-1 space-y-6">
					<div className="glass-card p-6 bg-slate-900/30 border-slate-800/50">
						<h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
							<Zap size={14} className="text-amber-400" /> Safety Stress Test
						</h3>
						<div className="space-y-4 text-sm">
							<div>
								<label className="block text-slate-500 mb-1.5 font-medium">Inject Fault Into</label>
								<input
									type="text"
									value={faultParam}
									onChange={(e) => setFaultParam(e.target.value)}
									placeholder="e.g. pressure, spo2"
									className="input-premium w-full !bg-slate-950/50 !text-xs"
								/>
							</div>
							<div>
								<label className="block text-slate-500 mb-1.5 font-medium">Sensor Bias: {Math.round(faultBias * 100)}%</label>
								<input
									type="range"
									min="-0.5"
									max="0.5"
									step="0.1"
									value={faultBias}
									onChange={(e) => setFaultBias(parseFloat(e.target.value))}
									className="w-full accent-sky-500"
								/>
							</div>
							<button
								onClick={handleRunFault}
								disabled={loading}
								className="w-full py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-500 border border-amber-500/20 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
							>
								<AlertTriangle size={14} /> Inject Fault
							</button>
						</div>
					</div>

					{activeFault && (
						<div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-2xl">
							<p className="text-xs text-amber-500 font-medium">
								Active Fault: <strong>{activeFault.parameter}</strong> biased by <strong>{activeFault.bias * 100}%</strong>
							</p>
						</div>
					)}
				</div>

				{/* Chart Panel */}
				<div className="lg:col-span-3">
					<div className="glass-card p-6 min-h-[400px] flex flex-col">
						{chartData ? (
							<>
								<div className="flex-1 w-full">
									<ResponsiveContainer width="100%" height={350}>
										<LineChart data={chartData}>
											<CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
											<XAxis
												dataKey="time"
												stroke="#475569"
												fontSize={10}
												tickLine={false}
												axisLine={false}
												label={{ value: 'Time (s)', position: 'insideBottom', offset: -5, fill: '#475569', fontSize: 10 }}
											/>
											<YAxis
												stroke="#475569"
												fontSize={10}
												tickLine={false}
												axisLine={false}
											/>
											<Tooltip
												contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', fontSize: '12px' }}
												itemStyle={{ padding: '2px 0' }}
											/>
											<Legend iconType="circle" />
											{chartKeys.map((key, i) => (
												<Line
													key={key}
													type="monotone"
													dataKey={key}
													stroke={colors[i % colors.length]}
													strokeWidth={2}
													dot={false}
													activeDot={{ r: 4, stroke: '#fff', strokeWidth: 2 }}
												/>
											))}
										</LineChart>
									</ResponsiveContainer>
								</div>
							</>
						) : (
							<div className="flex-1 flex flex-col items-center justify-center text-slate-500 opacity-30 gap-4">
								<RotateCcw size={48} className="animate-spin-slow" />
								<p>No simulation data loaded. Run simulation to view metrics.</p>
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	)
}
