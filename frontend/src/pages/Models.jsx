import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getModels, runModels } from '../api.js'
const show = (v) => v === null || v === undefined ? '—' : v
export default function Models() {
  const [d, setD] = useState(null); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false); const [msg, setMsg] = useState('')
  const [params, setParams] = useState({ k: '', linkage: 'ward', eps: 1.0, min_samples: 10 })
  const load = () => getModels().then(setD).catch(e=>setErr(e.message))
  useEffect(() => { load() }, [])
  const run = async () => { setBusy(true); setMsg(''); try { const p = {...params, k: params.k ? Number(params.k) : undefined, eps: Number(params.eps), min_samples: Number(params.min_samples)}; await runModels(p); await load(); setMsg('Models rerun from the real backend.') } catch(e){ setErr(e.message) } setBusy(false) }
  if (err) return <p className="error">{err}</p>
  if (!d) return <p className="muted">Loading models…</p>
  const rows = Object.values(d.models)
  const chart = rows.map(m => ({ name: m.algorithm, silhouette: m.metrics.silhouette ?? 0 }))
  const valid = rows.filter(m => m.metrics.silhouette !== null && m.metrics.silhouette !== undefined)
  const best = valid.length ? valid.reduce((a, b) => (b.metrics.silhouette > a.metrics.silhouette ? b : a)) : null
  const gmm = d.models.gmm
  return <><h2>Model Comparison</h2><p className="sub">Same scaled features for every algorithm. A single score never proves one algorithm is universally better. DBSCAN silhouette is “—” when it finds fewer than 2 clusters.</p>
    <div className="card" style={{marginBottom:16}}><h3>Run / rerun evaluation</h3>
      <div className="controls"><label>K (blank = best by silhouette)<input type="number" value={params.k} onChange={e=>setParams({...params,k:e.target.value})} placeholder="auto"/></label>
      <label>Linkage<select value={params.linkage} onChange={e=>setParams({...params,linkage:e.target.value})}><option value="ward">ward</option><option value="complete">complete</option><option value="average">average</option></select></label>
      <label>DBSCAN eps<input type="number" step="0.1" value={params.eps} onChange={e=>setParams({...params,eps:e.target.value})}/></label>
      <label>Min samples<input type="number" value={params.min_samples} onChange={e=>setParams({...params,min_samples:e.target.value})}/></label>
      <button className="btn" disabled={busy} onClick={run}>{busy?'Running…':'Run models'}</button></div>{msg && <p className="muted">{msg}</p>}
    </div>
    <div className="card" style={{marginBottom:16}}><div className="tablewrap"><table><thead><tr><th>Algorithm</th><th>Parameters</th><th>Silhouette</th><th>Davies–Bouldin</th><th>Calinski–Harabasz</th><th>Clusters</th><th>Noise</th><th>Runtime</th><th>AIC / BIC (GMM)</th></tr></thead>
      <tbody>{rows.map(m=><tr key={m.algorithm}><td><b>{m.algorithm}</b></td><td>{JSON.stringify(m.params)}</td><td>{show(m.metrics.silhouette)}</td><td>{show(m.metrics.davies_bouldin)}</td><td>{show(m.metrics.calinski_harabasz)}</td><td>{m.metrics.n_clusters}</td><td>{m.metrics.noise_count} ({m.metrics.noise_pct}%)</td><td>{show(m.runtime_seconds)}s</td><td>{m.aic !== undefined && m.aic !== null ? `${m.aic} / ${m.bic}` : '—'}</td></tr>)}</tbody></table></div>
      <p className="muted">Silhouette: higher is better. Davies–Bouldin: lower is better. Calinski–Harabasz: higher is better. AIC/BIC are GMM-only model-selection criteria (lower is better), not clustering metrics. Cluster sizes: {rows.map(m=>`${m.algorithm}: ${JSON.stringify(m.sizes)}`).join(' · ')}</p>
      {best && <p><b>Recommendation:</b> {best.algorithm} has the highest valid silhouette ({best.metrics.silhouette}), and its three segments are the most interpretable for business use — but no single metric proves one algorithm universally better. GMM ({show(gmm?.metrics.silhouette)} silhouette) gives probabilistic membership instead of hard assignments, and DBSCAN found only 1 cluster with {d.models.dbscan.metrics.noise_count} noise customers, so it is not the main segmentation here.</p>}</div>
    <div className="grid2"><div className="card"><h3>Silhouette by algorithm</h3><ResponsiveContainer width="100%" height={240}><BarChart data={chart}><CartesianGrid vertical={false} stroke="#eee"/><XAxis dataKey="name" tick={{fontSize:11}}/><YAxis tick={{fontSize:11}}/><Tooltip/><Bar dataKey="silhouette" fill="#2563eb" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div>
      <div className="card"><h3>K-Means elbow (inertia) + silhouette</h3><ResponsiveContainer width="100%" height={240}><BarChart data={d.models.kmeans.elbow}><CartesianGrid vertical={false} stroke="#eee"/><XAxis dataKey="k" tick={{fontSize:11}}/><YAxis tick={{fontSize:11}}/><Tooltip/><Bar dataKey="inertia" fill="#2563eb" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>
      <p className="muted">Selected K by silhouette: {d.models.kmeans.selected_k_by_silhouette}. Elbow values: {d.models.kmeans.elbow.map(e=>`K${e.k}: silhouette ${show(e.silhouette)}`).join(' · ')}</p></div></div>
  </>
}
