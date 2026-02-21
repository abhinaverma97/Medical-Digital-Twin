import React, { useState } from 'react'
import { addRequirement } from '../api'
import { ClipboardList, Plus, Sparkles, AlertCircle, Info, RotateCcw } from 'lucide-react'

const SAMPLES = {
	ventilator: {
		id: 'REQ-VENT-001',
		title: 'Battery Backup Power',
		description: 'The ventilator shall transition to internal battery backup immediately upon loss of mains power.',
		type: 'functional',
		priority: 'SHALL',
		subsystem: 'PowerSupply',
		parameter: 'BatteryStatus',
		status: 'Approved',
		verification: { method: 'test', description: 'Simulate power loss and measure discharge time.' }
	},
	ventilator_interface: {
		id: 'REQ-VENT-INT-001',
		title: 'O2 Sensor Signal Interface',
		description: 'The O2 sensor shall provide a 0-5V analog signal proportional to oxygen concentration.',
		type: 'interface',
		priority: 'SHALL',
		subsystem: 'GasMixer',
		interface: 'O2Sensor -> ControlUnit',
		protocol: 'Analog 0-5V',
		parameter: 'O2Concentration',
		status: 'Approved',
		verification: { method: 'analysis', description: 'Review circuit schematic for impedance matching.' }
	},
	pulse_ox: {
		id: 'REQ-POX-001',
		title: 'SpO2 Measurement Accuracy',
		description: 'The pulse oximeter shall measure functional oxygen saturation (SpO2) with high accuracy.',
		type: 'performance',
		priority: 'SHALL',
		subsystem: 'SignalProcessing',
		parameter: 'SpO2',
		min_value: 70,
		max_value: 100,
		unit: '%',
		tolerance: 2.0,
		status: 'Approved',
		verification: { method: 'test', description: 'Functional verification using a calibrated SpO2 simulator.' }
	},
	dialysis: {
		id: 'REQ-DIAL-001',
		title: 'Air-in-Blood Detection',
		description: 'The system shall detect air bubbles in the extracorporeal blood circuit and stop the blood pump.',
		type: 'safety',
		priority: 'SHALL',
		subsystem: 'Safety/Alarm System',
		parameter: 'AirBubble',
		hazard: 'Air Embolism (Critical)',
		severity: 'Critical',
		probability: 'Probable',
		standard: 'ISO 60601-2-16',
		clause: '201.12.4.102',
		status: 'Approved',
		verification: { method: 'simulation', description: 'Inject air into virtual sensor and verify pump cutoff response time.' }
	},
	dialysis_regulatory: {
		id: 'REQ-DIAL-REG-001',
		title: 'Biocompatibility Compliance',
		description: 'All blood-contacting components shall meet ISO 10993-1 requirements for biocompatibility.',
		type: 'regulatory',
		priority: 'SHALL',
		subsystem: 'Extracorporeal Circuit',
		status: 'Approved',
		standard: 'ISO 10993-1',
		clause: 'Clause 4',
		verification: { method: 'inspection', description: 'Review material data sheets and leachables/extractables report.' }
	}
}

const INITIAL_STATE = {
	id: 'REQ-NEW-001',
	title: '',
	description: '',
	parent_id: '',
	type: 'functional',
	priority: 'SHALL',
	status: 'Draft',
	subsystem: '',
	parameter: '',
	min_value: '',
	max_value: '',
	unit: '',
	tolerance: '',
	response_time_ms: '',
	interface: '',
	protocol: '',
	hazard: '',
	severity: 'Low',
	probability: 'Remote',
	standard: '',
	clause: '',
	verification: { method: 'test', description: '' }
}

export default function RequirementsForm({ deviceType }) {
	const [req, setReq] = useState(INITIAL_STATE)
	const [loading, setLoading] = useState(false)
	const [msg, setMsg] = useState(null)
	const [submittedReqs, setSubmittedReqs] = useState([])

	const loadSample = (type = null) => {
		let key = deviceType
		if (type === 'interface' && deviceType === 'ventilator') key = 'ventilator_interface'
		if (type === 'regulatory' && deviceType === 'dialysis') key = 'dialysis_regulatory'

		const sample = SAMPLES[key] || SAMPLES.ventilator
		setReq({ ...INITIAL_STATE, ...sample })
		setMsg({ type: 'success', text: `Sample [${sample.type}] loaded.` })
	}

	const resetForm = () => {
		setReq(INITIAL_STATE)
		setMsg(null)
	}

	const handleSubmit = async (e) => {
		e.preventDefault()
		setLoading(true)

		const payload = { ...req, verification: { ...req.verification } }
		if (payload.min_value !== '') payload.min_value = parseFloat(payload.min_value)
		if (payload.max_value !== '') payload.max_value = parseFloat(payload.max_value)
		if (payload.tolerance !== '') payload.tolerance = parseFloat(payload.tolerance)
		if (payload.response_time_ms !== '') payload.response_time_ms = parseInt(payload.response_time_ms)

		Object.keys(payload).forEach(key => {
			if (payload[key] === '') delete payload[key]
		})

		try {
			await addRequirement(payload)
			setMsg({ type: 'success', text: `Requirement ${req.id} added successfully.` })
			setSubmittedReqs(prev => [payload, ...prev].slice(0, 5)) // Keep last 5
		} catch (err) {
			console.error('SUBMIT_ERROR:', err)
			const errorDetail = err.response?.data?.detail
			let errorMsg = 'Add failed.'

			if (Array.isArray(errorDetail)) {
				// Handle Pydantic objects or direct string lists
				errorMsg = typeof errorDetail[0] === 'string' ? errorDetail[0] : (errorDetail[0]?.msg || JSON.stringify(errorDetail[0]))
			} else if (typeof errorDetail === 'string') {
				errorMsg = errorDetail
			}

			setMsg({ type: 'error', text: errorMsg })
		} finally {
			setLoading(false)
		}
	}

	const SectionHeader = ({ title, icon: Icon }) => (
		<div className="flex items-center gap-2 border-b border-slate-800 pb-2 mb-4 mt-6">
			<Icon size={14} className="text-sky-400" />
			<h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">{title}</h3>
		</div>
	)

	return (
		<div className="max-w-5xl mx-auto space-y-8">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold text-white flex items-center gap-2">
						<ClipboardList className="text-sky-400" /> Integrated Requirement Intake
					</h2>
					<p className="text-slate-400">Full-schema deterministic definition for {deviceType}.</p>
				</div>
				<div className="flex gap-2">
					<button type="button" onClick={resetForm} className="btn-outline flex items-center gap-2 text-xs py-1.5 px-3 border-slate-700 text-slate-400 hover:bg-slate-800 transition-all"><RotateCcw size={14} /> Reset</button>
					<button type="button" onClick={() => loadSample()} className="btn-outline flex items-center gap-2 text-xs py-1.5 px-4 border-sky-500/20 text-sky-400 hover:bg-sky-500/10 transition-all"><Sparkles size={14} /> Load Engineering Sample</button>
					{deviceType === 'ventilator' && (
						<button type="button" onClick={() => loadSample('interface')} className="btn-outline flex items-center gap-2 text-xs py-1.5 px-4 border-teal-500/20 text-teal-400 hover:bg-teal-500/10 transition-all"><ActivityCircle size={14} /> Load Interface Sample</button>
					)}
				</div>
			</div>

			<form onSubmit={handleSubmit} className="space-y-4">
				<SectionHeader title="Identify & Classify" icon={Info} />
				<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
					<div className="md:col-span-1">
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">REQ ID</label>
						<input type="text" value={req.id} onChange={e => setReq({ ...req, id: e.target.value })} className="input-premium w-full !text-xs" required />
					</div>
					<div className="md:col-span-2">
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Title</label>
						<input type="text" value={req.title} onChange={e => setReq({ ...req, title: e.target.value })} className="input-premium w-full !text-xs" required />
					</div>
					<div className="md:col-span-1">
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Type</label>
						<select value={req.type} onChange={e => setReq({ ...req, type: e.target.value })} className="input-premium w-full !text-xs">
							<option value="functional">Functional</option>
							<option value="performance">Performance</option>
							<option value="interface">Interface</option>
							<option value="safety">Safety (ISO 14971)</option>
							<option value="regulatory">Regulatory</option>
							<option value="environmental">Environmental</option>
						</select>
					</div>
				</div>

				<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
					<div>
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Priority</label>
						<select value={req.priority} onChange={e => setReq({ ...req, priority: e.target.value })} className="input-premium w-full !text-xs">
							<option value="SHALL">SHALL (Mandatory)</option>
							<option value="SHOULD">SHOULD (Recommended)</option>
							<option value="MAY">MAY (Optional)</option>
						</select>
					</div>
					<div>
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Status</label>
						<select value={req.status} onChange={e => setReq({ ...req, status: e.target.value })} className="input-premium w-full !text-xs">
							<option value="Draft">Draft</option>
							<option value="Approved">Approved</option>
						</select>
					</div>
					<div>
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Target Subsystem</label>
						<input type="text" value={req.subsystem} onChange={e => setReq({ ...req, subsystem: e.target.value })} className="input-premium w-full !text-xs" required />
					</div>
					<div>
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Parent REQ ID</label>
						<input type="text" value={req.parent_id} onChange={e => setReq({ ...req, parent_id: e.target.value })} className="input-premium w-full !text-xs" placeholder="None" />
					</div>
				</div>

				<div>
					<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Description</label>
					<textarea value={req.description} onChange={e => setReq({ ...req, description: e.target.value })} className="input-premium w-full h-20 resize-none !text-xs" required />
				</div>

				{(req.type === 'performance' || req.type === 'functional') && (
					<>
						<SectionHeader title="Performance Bounds" icon={ActivityCircle} />
						<div className="grid grid-cols-2 md:grid-cols-6 gap-4">
							<div className="col-span-2">
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Parameter</label>
								<input type="text" value={req.parameter} onChange={e => setReq({ ...req, parameter: e.target.value })} className="input-premium w-full !text-xs" placeholder="e.g. Pressure" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Min Value</label>
								<input type="number" step="any" value={req.min_value} onChange={e => setReq({ ...req, min_value: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Max Value</label>
								<input type="number" step="any" value={req.max_value} onChange={e => setReq({ ...req, max_value: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Unit</label>
								<input type="text" value={req.unit} onChange={e => setReq({ ...req, unit: e.target.value })} className="input-premium w-full !text-xs" placeholder="e.g. L/min" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Response (ms)</label>
								<input type="number" value={req.response_time_ms} onChange={e => setReq({ ...req, response_time_ms: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
						</div>
					</>
				)}

				{req.type === 'interface' && (
					<>
						<SectionHeader title="Interface Definition" icon={ActivityCircle} />
						<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Interface Mapping</label>
								<input type="text" value={req.interface} onChange={e => setReq({ ...req, interface: e.target.value })} className="input-premium w-full !text-xs" placeholder="Source -> Target" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Protocol / Signal</label>
								<input type="text" value={req.protocol} onChange={e => setReq({ ...req, protocol: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Parameter Flow</label>
								<input type="text" value={req.parameter} onChange={e => setReq({ ...req, parameter: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
						</div>
					</>
				)}

				{req.type === 'safety' && (
					<>
						<SectionHeader title="ISO 14971 Risk Assessment" icon={AlertCircle} />
						<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Hazard Type</label>
								<input type="text" value={req.hazard} onChange={e => setReq({ ...req, hazard: e.target.value })} className="input-premium w-full !text-xs" placeholder="e.g. Excessive Pressure" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Severity</label>
								<select value={req.severity} onChange={e => setReq({ ...req, severity: e.target.value })} className="input-premium w-full !text-xs">
									<option value="Low">Low</option>
									<option value="Medium">Medium</option>
									<option value="High">High</option>
									<option value="Critical">Critical</option>
								</select>
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Probability (P1)</label>
								<select value={req.probability} onChange={e => setReq({ ...req, probability: e.target.value })} className="input-premium w-full !text-xs">
									<option value="Negligible">Negligible</option>
									<option value="Remote">Remote</option>
									<option value="Occasional">Occasional</option>
									<option value="Probable">Probable</option>
									<option value="Frequent">Frequent</option>
								</select>
							</div>
						</div>
						<div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-2">
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Monitored Parameter</label>
								<input type="text" value={req.parameter} onChange={e => setReq({ ...req, parameter: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Safety Limit (Max)</label>
								<input type="number" step="any" value={req.max_value} onChange={e => setReq({ ...req, max_value: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Regulation Standard</label>
								<input type="text" value={req.standard} onChange={e => setReq({ ...req, standard: e.target.value })} className="input-premium w-full !text-xs" placeholder="ISO 14971" />
							</div>
							<div>
								<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Clause REF</label>
								<input type="text" value={req.clause} onChange={e => setReq({ ...req, clause: e.target.value })} className="input-premium w-full !text-xs" />
							</div>
						</div>
					</>
				)}

				<SectionHeader title="Verification Strategy" icon={Plus} />
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div>
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Method</label>
						<select value={req.verification.method} onChange={e => setReq({ ...req, verification: { ...req.verification, method: e.target.value } })} className="input-premium w-full !text-xs">
							<option value="test">Test</option>
							<option value="simulation">Digital Twin Simulation</option>
							<option value="analysis">Analysis</option>
							<option value="inspection">Inspection</option>
						</select>
					</div>
					<div className="md:col-span-2">
						<label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Evidence Plan</label>
						<input type="text" value={req.verification.description} onChange={e => setReq({ ...req, verification: { ...req.verification, description: e.target.value } })} className="input-premium w-full !text-xs" required />
					</div>
				</div>

				<div className="flex items-center justify-between pt-6 mt-8 border-t border-slate-800">
					<div className="flex items-center gap-4">
						{msg && (
							<p className={`text-sm font-medium px-4 py-2 rounded-lg ${msg.type === 'success' ? 'bg-teal-500/10 text-teal-400' : 'bg-crimson-500/10 text-crimson-400'}`}>
								{msg.text}
							</p>
						)}
					</div>
					<button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
						{loading ? 'Submitting...' : <><Plus size={18} /> Commit Requirement</>}
					</button>
				</div>
			</form>

			{submittedReqs.length > 0 && (
				<div className="mt-12 bg-slate-900/30 rounded-2xl border border-slate-800/50 p-6">
					<h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
						<CheckCircle2 size={14} className="text-teal-500" /> Recent Submissions
					</h4>
					<div className="space-y-2">
						{submittedReqs.map((r, i) => (
							<div key={i} className="flex items-center justify-between py-2 px-3 bg-slate-800/30 rounded-lg border border-slate-800/50 group hover:border-sky-500/30 transition-all">
								<div className="flex items-center gap-3">
									<span className="text-[10px] font-mono text-sky-400 bg-sky-500/10 px-1.5 py-0.5 rounded">{r.id}</span>
									<span className="text-xs text-slate-300 font-medium">{r.title}</span>
								</div>
								<span className="text-[10px] text-slate-500 uppercase font-bold group-hover:text-slate-400">{r.type}</span>
							</div>
						))}
					</div>
				</div>
			)}
		</div>
	)
}

const ActivityCircle = ({ size, className }) => (
	<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
		<path d="M22 12h-4l-3 9L9 3l-3 9H2" />
	</svg>
)

const CheckCircle2 = ({ size, className }) => (
	<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
		<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
		<path d="m9 12 2 2 4-4" />
	</svg>
)
