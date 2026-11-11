import React, { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Segments from './pages/Segments.jsx'
import Analytics from './pages/Analytics.jsx'
import Models from './pages/Models.jsx'
import Insights from './pages/Insights.jsx'
import Settings from './pages/Settings.jsx'
import { getDashboard } from './api.js'
export default function App() {
  const [page, setPage] = useState('dashboard'); const [data, setData] = useState(null); const [err, setErr] = useState('')
  useEffect(() => { getDashboard().then(setData).catch(e => setErr(e.message)) }, [])
  const hour = new Date().getHours()
  const greet = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening'
  return <div className="app"><Sidebar page={page} setPage={setPage} /><main className="main">
    <header className="topbar">
      <div><h1>{greet}, Chethan</h1><p>Your latest customer segmentation updates here</p></div>
      <div className="topactions">
        <button className="iconbtn" title="Search customers" onClick={() => setPage('segments')}>⌕</button>
        <div className="syncpill"><span>↻</span><div><b>Last sync</b><span>Just now</span></div></div>
        <div className="avatar" title="Chethan">C</div>
      </div>
    </header>
    {data && <div className={data.data_source === 'demo' ? 'banner demo' : 'banner'}>{data.data_source === 'demo' ? 'Demo mode: no real dataset is configured yet, so these figures come from clearly-labelled demonstration transactions. Upload the real UCI Online Retail file in Settings to replace them.' : 'Real dataset loaded — UCI Online Retail, 541,909 rows.'} Reference date: {data.reference_date ?? ''}</div>}
    {err && <div className="error">Backend not reachable: {err}. Start it first: <code>cd backend &amp;&amp; python app.py</code> (see README), then refresh.</div>}
    {page === 'dashboard' && <Dashboard data={data} setPage={setPage} />}
    {page === 'segments' && <Segments />}
    {page === 'analytics' && <Analytics />}
    {page === 'models' && <Models />}
    {page === 'insights' && <Insights />}
    {page === 'settings' && <Settings />}
  </main></div>
}
