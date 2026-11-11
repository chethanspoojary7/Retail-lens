import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getAnalytics } from '../api.js'
function Chart({ title, data, dataKey }) {
  return <div className="card"><h3>{title}</h3><ResponsiveContainer width="100%" height={240}><BarChart data={data}>
    <CartesianGrid vertical={false} stroke="#eee"/><XAxis dataKey="range" tick={{fontSize:10}} interval="preserveStartEnd"/><YAxis tick={{fontSize:11}}/><Tooltip/><Bar dataKey={dataKey} fill="#2563eb" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div>
}
export default function Analytics() {
  const [d, setD] = useState(null); const [err, setErr] = useState('')
  useEffect(()=>{ getAnalytics().then(setD).catch(e=>setErr(e.message)) },[])
  if (err) return <p className="error">{err}</p>
  if (!d) return <p className="muted">Loading analytics…</p>
  return <><h2>Analytics</h2><p className="sub">Real aggregated customer features from the processed dataset.</p>
    <div className="grid2"><Chart title="Spending distribution (£ per customer)" data={d.spending_hist} dataKey="customers"/><Chart title="Purchase frequency distribution" data={d.frequency_hist} dataKey="customers"/></div>
    <div className="grid2"><Chart title="Recency distribution (days)" data={d.recency_hist} dataKey="customers"/>
      <div className="card"><h3>Revenue by segment</h3><ResponsiveContainer width="100%" height={240}><BarChart data={d.revenue_by_segment}>
        <CartesianGrid vertical={false} stroke="#eee"/><XAxis dataKey="name" tick={{fontSize:10}}/><YAxis tick={{fontSize:11}}/><Tooltip/><Bar dataKey="revenue" fill="#2563eb" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div></div>
  </>
}
