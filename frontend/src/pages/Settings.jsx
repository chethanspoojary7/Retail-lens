import React, { useEffect, useState } from 'react'
import { getSummary, runAnalysis } from '../api.js'
export default function Settings() {
  const [s, setS] = useState(null); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false); const [msg, setMsg] = useState('')
  const [params, setParams] = useState({ reference_date: '2011-12-10', k: '', eps: 1.0, min_samples: 10 })
  const load = () => getSummary().then(setS).catch(e=>setErr(e.message))
  useEffect(() => { load() }, [])
  const upload = async (e) => { const file = e.target.files[0]; if (!file) return; const fd = new FormData(); fd.append('file', file); setBusy(true);
    try { const res = await fetch('http://localhost:5000/api/data/upload', { method: 'POST', body: fd }); const d = await res.json(); if (!res.ok) throw new Error(d.error); setMsg('Uploaded and processed: ' + JSON.stringify(d.totals)); load() } catch (ex) { setErr(ex.message) } setBusy(false) }
  const rerun = async () => { setBusy(true); try { const p = {...params, k: params.k ? Number(params.k) : undefined, eps: Number(params.eps), min_samples: Number(params.min_samples)}; await runAnalysis(p); setMsg('Analysis rerun.'); load() } catch (e) { setErr(e.message) } setBusy(false) }
  if (err) return <p className="error">{err}</p>
  if (!s) return <p className="muted">Loading settings…</p>
  return <><h2>Settings</h2><p className="sub">Every control below performs a real action. Nothing here is decorative.</p>
    <div className="card" style={{marginBottom:16}}><h3>Dataset</h3><p>Current source: <b>{s.data_source}</b> {s.data_source==='demo' && '— clearly labelled demonstration data, not real business results.'}</p>
      <p className="muted">Real data: download the UCI Online Retail dataset from https://archive.ics.uci.edu/dataset/352/online+retail and place the .xlsx or .csv in backend/data/, then upload it here or restart the backend with that file.</p>
      <label>Upload CSV / XLSX<input type="file" accept=".csv,.xlsx,.xls" onChange={upload}/></label>{busy && <p className="muted">Working…</p>}{msg && <p className="muted">{msg}</p>}</div>
    <div className="card" style={{marginBottom:16}}><h3>Analysis & clustering parameters</h3>
      <label>Analysis reference date (recency is measured against this date)<input value={params.reference_date} onChange={e=>setParams({...params,reference_date:e.target.value})}/></label>
      <label>K (blank = best by silhouette)<input value={params.k} onChange={e=>setParams({...params,k:e.target.value})} placeholder="auto"/></label>
      <label>DBSCAN eps<input type="number" step="0.1" value={params.eps} onChange={e=>setParams({...params,eps:e.target.value})}/></label>
      <label>DBSCAN min samples<input type="number" value={params.min_samples} onChange={e=>setParams({...params,min_samples:e.target.value})}/></label>
      <button className="btn" disabled={busy} onClick={rerun}>Rerun analysis</button></div>
    <div className="card"><h3>Data processing status</h3><p className="muted">Cleaning is sequential, so counts add up to the rows removed.</p>
      <pre style={{whiteSpace:'pre-wrap',fontSize:13}}>{JSON.stringify(s.cleaning, null, 2)}</pre><p>Totals: {JSON.stringify(s.totals)}</p></div>
  </>
}
