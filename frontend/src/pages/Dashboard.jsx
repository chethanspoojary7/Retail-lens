import React, { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, ZAxis, LineChart, Line } from 'recharts'
import { exportCsv, getCustomers } from '../api.js'
// myflow layout (reference image): Delivery Rate / Campaigns / blue Contacts
// on row 1, Top Contacts / Messages By Type / Contacts-continued on row 2,
// Messages By Month wide + Credits / Texts Sent on the right.
// Every number below comes from the real ShopMind API response.
const SEG_COLORS = ['#0f172a', '#14b8a6', '#2563eb']
const fmtMoney = (n) => '£' + Math.round(n).toLocaleString()
export default function Dashboard({ data, setPage }) {
  const [top, setTop] = useState([])
  const [filter, setFilter] = useState('all')
  useEffect(() => { getCustomers({ sort: 'monetary', page: 1, page_size: 3 }).then(d => setTop(d.items)).catch(() => {}) }, [])
  if (!data) return <p className="muted">Loading dashboard…</p>
  const { totals, monthly, profiles, insights, scatter } = data
  const m2011 = monthly.filter(m => m.month.startsWith('2011'))
  const topSeg = profiles[0]
  const otherShare = (100 - topSeg.revenue_share_pct).toFixed(1)
  const topSum = top.reduce((s, c) => s + c.monetary, 0)
  const othersPct = (100 * (totals.revenue - topSum) / totals.revenue).toFixed(1)
  const othersRev = totals.revenue - topSum
  const maxRev = Math.max(...m2011.map(m => m.revenue))
  const nov = m2011.find(m => m.label === 'Nov'); const oct = m2011.find(m => m.label === 'Oct')
  const novGrowth = nov && oct ? ((nov.transactions - oct.transactions) / oct.transactions * 100).toFixed(1) : '—'
  const maxCust = Math.max(...m2011.slice(0, 8).map(m => m.customers))
  const rows = filter === 'all' ? profiles : profiles.filter(p => p.name === filter)
  // Barcode strips like the reference: thin vertical bars, coloured by share.
  const shareBars = Array.from({ length: 48 }, (_, i) => {
    const pct = (i + 1) / 48 * 100
    return pct <= topSeg.revenue_share_pct ? '#14b8a6' : pct <= topSeg.revenue_share_pct + (profiles[1]?.revenue_share_pct || 0) ? '#2563eb' : '#d1d5db'
  })
  return <>
    <div className="flow">
      <div className="card area-del">
        <div className="cardhead"><h3>Top Segment Share</h3><span className="kebab">⋯</span></div>
        <div className="bignum">{topSeg.revenue_share_pct}% <span className="pill">↗ {topSeg.name}</span></div>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}><span className="rightnote">{otherShare}% other segments</span></div>
        <div className="barcode">{shareBars.map((c, i) => <i key={i} style={{ background: c }} />)}</div>
      </div>
      <div className="card area-camp">
        <div className="cardhead"><h3>Segments</h3><span className="kebab">⋯</span></div>
        <div className="bignum">{totals.segments} <span className="pill">{totals.segments} active</span></div>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}><span className="rightnote">{totals.customers.toLocaleString()} customers</span></div>
        <div className="barcode">{m2011.map((m, i) => <i key={i} style={{ background: i < 3 ? '#2563eb' : '#e5e7eb', height: '100%' }} />)}</div>
      </div>
      <div className="bluecard area-contacts">
        <div className="cardhead"><h3>Customers</h3><span className="kebab" style={{ color: '#bfdbfe' }}>⋯</span></div>
        <div className="bignum">{totals.customers.toLocaleString()}</div>
        <div><span className="pill">{topSeg.customers.toLocaleString()} {topSeg.name} ↗ {topSeg.pct_customers}%</span></div>
        <div className="bluebars">{m2011.slice(0, 8).map((m, i) => (
          <div className="col" key={m.month}><div className={i === 7 ? 'bar hatched' : 'bar'} style={{ height: Math.round(120 * m.customers / maxCust) + 'px' }} /><span>{m.label[0]}</span></div>
        ))}</div>
        <div className="rightnote" style={{ marginTop: 8 }}>Customers per month, Jan–Aug 2011</div>
      </div>
      <div className="card area-top">
        <div className="cardhead"><h3>Top Customers</h3><select value="all" onChange={() => setPage('segments')}><option value="all">All time ⌄</option></select></div>
        <div className="toplist">
          <div className="stackbar">
            {top.map((c, i) => <i key={c.customer_id} style={{ height: Math.max(10, 90 * c.monetary / (top[0]?.monetary || 1)) + 'px', background: SEG_COLORS[i] }} />)}
            <i className="hatched" style={{ height: '70px' }} />
          </div>
          <div style={{ flex: 1 }}>
            {top.map((c, i) => (
              <div className="contactrow" key={c.customer_id}>
                <span className="dot" style={{ background: SEG_COLORS[i] }} />
                <b>Customer {c.customer_id}</b><span className="mail">{c.country}</span>
                <span className="pct">{(100 * c.monetary / totals.revenue).toFixed(2)}%</span>
                <span className="val">{fmtMoney(c.monetary)}</span>
              </div>
            ))}
            <div className="contactrow"><span className="dot" style={{ background: '#fff', border: '1px solid #cbd5e1' }} /><b>Others</b><span className="pct">{othersPct}%</span><span className="val">{fmtMoney(othersRev)}</span></div>
          </div>
        </div>
      </div>
      <div className="card area-msg">
        <div className="cardhead"><h3>Revenue By Segment</h3><select value="all" onChange={() => setPage('segments')}><option value="all">All time ⌄</option></select></div>
        <div className="donutwrap">
          <ResponsiveContainer width="46%" height={180}>
            <PieChart><Pie data={profiles} dataKey="revenue_share_pct" nameKey="name" innerRadius={52} outerRadius={78} paddingAngle={2} label={({ revenue_share_pct }) => `${revenue_share_pct}%`}>
              {profiles.map((_, i) => <Cell key={i} fill={SEG_COLORS[i % SEG_COLORS.length]} />)}
            </Pie><Tooltip formatter={(v, n) => [`${v}% of revenue`, n]} /></PieChart>
          </ResponsiveContainer>
          <div style={{ flex: 1 }}>
            {profiles.map((p, i) => (
              <div className="legendrow" key={p.cluster_id}><span className="dot" style={{ background: SEG_COLORS[i] }} />{p.name}<span className="delta">{fmtMoney(p.total_monetary)}</span></div>
            ))}
            <p className="muted" style={{ margin: '6px 0 0' }}>Share of total revenue, by discovered segment.</p>
          </div>
        </div>
      </div>
      <div className="card area-month">
        <div className="cardhead"><h3>Revenue By Month</h3><div className="legend"><span><span className="dot" style={{ background: '#2563eb' }} />Revenue</span><span><span className="dot" style={{ background: '#fff', border: '1px solid #94a3b8' }} />Transactions in tooltip</span></div><select value="2011" onChange={() => {}}><option value="2011">2011 ⌄</option></select></div>
        <div className="monthbars">
          {nov && <div className="callout" style={{ left: '83%' }}><b>{fmtMoney(nov.revenue)} Total</b><br />● {nov.transactions.toLocaleString()} transactions<br />● {nov.customers.toLocaleString()} customers</div>}
          {m2011.map(m => (
            <div className="mcol" key={m.month} title={`${m.label} 2011: ${fmtMoney(m.revenue)} · ${m.transactions} transactions · ${m.customers} customers`}>
              <div style={{ height: Math.round(170 * m.revenue / maxRev) + 'px', width: '100%', maxWidth: 34, display: 'flex', flexDirection: 'column' }}>
                <div style={{ flex: '0 0 42%', background: 'repeating-linear-gradient(45deg,#bfdbfe 0 3px,#e8f2ff 3px 7px)', borderRadius: '6px 6px 0 0' }} />
                <div className={m.label === 'Nov' ? 'mbar peak' : 'mbar'} style={{ flex: '1 1 58%', background: m.label === 'Nov' ? '#2563eb' : '#93c5fd', borderRadius: 0 }} />
              </div>
              <span>{m.label}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="card area-credits">
        <div className="cardhead"><h3>▭ Total Revenue</h3><span className="kebab">⋯</span></div>
        <div className="credits"><div className="bignum">£{(totals.revenue / 1000000).toFixed(2)}M</div><span className="rightnote">£{totals.avg_order_value} avg order</span><button className="plusbtn" title="Export segment profiles" onClick={() => exportCsv('segments')}>+</button></div>
      </div>
      <div className="darkcard area-texts">
        <div className="cardhead"><h3>Transactions</h3><select value="all" onChange={() => {}}><option value="all">All time ⌄</option></select></div>
        <div className="bignum">{totals.transactions.toLocaleString()}</div>
        <div><span style={{ fontSize: 12, color: '#cbd5e1' }}>{nov?.transactions.toLocaleString()} in Nov</span> <span className="pill">↗ {novGrowth}% vs Oct</span></div>
        <ResponsiveContainer width="100%" height={90}>
          <LineChart data={monthly} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
            <Line type="monotone" dataKey="transactions" stroke="#fff" strokeWidth={2} dot={false} />
            <Tooltip formatter={(v) => [v, 'Transactions']} labelFormatter={(l, p) => p?.[0]?.payload?.month || ''} contentStyle={{ background: '#0f172a', border: 0, color: '#fff' }} />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8' }}><span>Dec 2010</span><span>Mar 2011</span><span>Jun 2011</span><span>Sep 2011</span><span>Dec 2011</span></div>
      </div>
    </div>
    <div className="grid2" style={{ marginTop: 16 }}>
      <div className="card"><h3>Customer Segments — PCA view</h3><p className="muted">PCA axes are reduced dimensions, not pounds or order counts. {data.pca ? `PC1 explains ${(data.pca.explained_variance_ratio[0] * 100).toFixed(1)}%, PC2 ${(data.pca.explained_variance_ratio[1] * 100).toFixed(1)}%.` : ''}</p>
        <ResponsiveContainer width="100%" height={260}><ScatterChart>
          <CartesianGrid stroke="#e2e8f0" /><XAxis type="number" dataKey="x" name="PCA 1" tick={{ fontSize: 11 }} /><YAxis type="number" dataKey="y" name="PCA 2" tick={{ fontSize: 11 }} /><ZAxis type="number" range={[30, 30]} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter data={scatter}>{scatter.map((s, i) => <Cell key={i} fill={SEG_COLORS[s.cluster % SEG_COLORS.length]} />)}</Scatter>
        </ScatterChart></ResponsiveContainer>
      </div>
      <div className="card"><h3>Key Insights</h3>{insights.map((ins, i) => <div key={i} style={{ padding: '10px 0', borderTop: i ? '1px solid #f1f5f9' : 0 }}><b>{ins.title}</b><p style={{ color: '#475569', fontSize: 13, lineHeight: 1.5, margin: '4px 0' }}>{ins.detail}</p><p className="muted">{ins.action}</p></div>)}
        <button className="btn" style={{ marginTop: 8 }} onClick={() => setPage('insights')}>All insights →</button></div>
    </div>
    <div className="card" style={{ marginBottom: 16 }}><div className="cardhead"><h3>Manage segments</h3><div className="controls" style={{ margin: 0 }}>
      <select value={filter} onChange={e => setFilter(e.target.value)}><option value="all">All segments</option>{profiles.map(p => <option key={p.cluster_id} value={p.name}>{p.name}</option>)}</select>
      <button className="btn" onClick={() => exportCsv('segments')}>Export ⤓</button></div></div>
      <div className="tablewrap"><table><thead><tr><th>Segment</th><th>Customers</th><th>Avg Spend</th><th>Frequency</th><th>Recency</th><th>Revenue Share</th></tr></thead>
        <tbody>{rows.map(p => <tr key={p.cluster_id} className="rowlink" onClick={() => setPage('segments')}><td><b>{p.name}</b></td><td>{p.customers}</td><td>£{p.avg_monetary.toLocaleString()}</td><td>{p.avg_frequency}</td><td>{p.avg_recency} days</td><td>{p.revenue_share_pct}%</td></tr>)}</tbody></table></div>
    </div>
  </>
}
