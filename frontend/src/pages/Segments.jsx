import React, { useEffect, useState } from 'react'
import { getSegments, getCustomers } from '../api.js'
export default function Segments() {
  const [profiles, setProfiles] = useState([]); const [search, setSearch] = useState(''); const [sort, setSort] = useState('monetary')
  const [selected, setSelected] = useState(null); const [cust, setCust] = useState({items:[], total:0}); const [page, setPage] = useState(1); const [err, setErr] = useState('')
  useEffect(()=>{ getSegments().then(d=>setProfiles(d.profiles)).catch(e=>setErr(e.message)) },[])
  useEffect(()=>{ if(selected!==null) getCustomers({segment:selected, page, page_size:20, sort}).then(setCust).catch(e=>setErr(e.message)) },[selected, page, sort])
  if (err) return <p className="error">{err}</p>
  const shown = [...profiles].sort((a,b)=> b[sort==='monetary'?'avg_monetary':sort==='frequency'?'avg_frequency':'avg_recency'] - a[sort==='monetary'?'avg_monetary':sort==='frequency'?'avg_frequency':'avg_recency'])
  return <>
    <h2>Customer Segments</h2><p className="sub">Names come from cluster statistics. The original cluster ID is kept because clustering labels are arbitrary.</p>
    <div className="controls"><input placeholder="Search segment name…" value={search} onChange={e=>setSearch(e.target.value)}/>
      <select value={sort} onChange={e=>setSort(e.target.value)}><option value="monetary">Sort: Avg spend</option><option value="frequency">Sort: Frequency</option><option value="recency">Sort: Recency</option></select></div>
    <div className="seggrid">{shown.filter(p=>p.name.toLowerCase().includes(search.toLowerCase())).map(p=><div key={p.cluster_id} className="segcard" onClick={()=>{setSelected(p.cluster_id); setPage(1)}}>
      <b>{p.name}</b><span className="pill" style={{float:'right'}}>Cluster {p.cluster_id}</span>
      <div className="num">{p.customers} <span style={{fontSize:14,fontWeight:400,color:'#888'}}>{p.pct_customers}%</span></div>
      <p>{p.note}<br/>Avg spend £{p.avg_monetary.toLocaleString()} · {p.avg_frequency} orders · {p.avg_recency} days since last purchase · {p.unique_products} products on average.</p>
      <p className="muted">{p.recommendation}</p></div>)}
    </div>
    {selected!==null && <div className="card"><h3>Customers in cluster {selected}</h3><p className="muted">{cust.total} customers</p>
      <div className="tablewrap"><table><thead><tr><th>Customer ID</th><th>Recency (days)</th><th>Frequency</th><th>Monetary (£)</th><th>Avg Order (£)</th><th>Products</th><th>Country</th></tr></thead>
      <tbody>{cust.items.map(c=><tr key={c.customer_id}><td>{c.customer_id}</td><td>{c.recency}</td><td>{c.frequency}</td><td>{c.monetary.toLocaleString()}</td><td>{c.avg_order_value.toFixed(2)}</td><td>{c.unique_products}</td><td>{c.country}</td></tr>)}</tbody></table></div>
      <div className="controls" style={{marginTop:12}}><button className="btn light" disabled={page<=1} onClick={()=>setPage(page-1)}>Previous</button><span>Page {page}</span><button className="btn light" disabled={page*20>=cust.total} onClick={()=>setPage(page+1)}>Next</button></div>
    </div>}
  </>
}
