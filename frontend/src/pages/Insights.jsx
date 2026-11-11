import React, { useEffect, useState } from 'react'
import { getInsights, exportCsv } from '../api.js'
export default function Insights() {
  const [d, setD] = useState(null); const [err, setErr] = useState('')
  useEffect(()=>{ getInsights().then(setD).catch(e=>setErr(e.message)) },[])
  if (err) return <p className="error">{err}</p>
  if (!d) return <p className="muted">Loading insights…</p>
  return <><h2>Insights & Reports</h2><p className="sub">Recommendations are rule-based suggestions from segment statistics. They do not claim a campaign will succeed.</p>
    <div className="controls"><button className="btn" onClick={()=>exportCsv('segments')}>Download segments CSV</button><button className="btn light" onClick={()=>exportCsv('customers')}>Download customers CSV</button></div>
    {d.insights.map((ins,i)=><div key={i} className="insight"><b>{ins.title}</b><p>{ins.detail}</p><p className="muted">{ins.action}</p></div>)}
    <div className="card"><h3>Segment profiles</h3><div className="tablewrap"><table><thead><tr><th>Segment</th><th>Customers</th><th>Revenue share</th><th>Suggested action</th></tr></thead>
    <tbody>{d.profiles.map(p=><tr key={p.cluster_id}><td><b>{p.name}</b> (cluster {p.cluster_id})</td><td>{p.customers}</td><td>{p.revenue_share_pct}%</td><td>{p.recommendation}</td></tr>)}</tbody></table></div></div>
  </>
}
