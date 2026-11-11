import React from 'react'
const NAV = [
  ['dashboard','⌂','Dashboard'],['segments','◫','Segments'],['analytics','▭','Analytics'],
  ['models','⬢','Models'],['insights','✦','Insights'],['settings','⚙','Settings'],
]
export default function Sidebar({ page, setPage }) {
  return <aside className="sidebar">
    <div className="logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden="true"><path d="M3 8l9-5 9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg><span>ShopMind</span></div>
    <nav className="nav">{NAV.map(([id, ic, label]) => (
      <button key={id} type="button" className={page===id?'active':''} aria-current={page===id?'page':undefined} onClick={()=>setPage(id)}><span className="ic" aria-hidden="true">{ic}</span><span>{label}</span></button>
    ))}</nav>
    <div className="profile"><div className="avatar">A</div><div className="profile-meta"><b>Admin</b><span>ShopMind analyst</span></div></div>
  </aside>
}
