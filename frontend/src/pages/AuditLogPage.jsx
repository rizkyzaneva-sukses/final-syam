import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {ClipboardList,Search} from 'lucide-react';

export default function AuditLogPage(){
  const [logs,setLogs]=useState([]),[err,setErr]=useState('');
  const [q,setQ]=useState('');
  useEffect(()=>{api('/audit-log').then(setLogs).catch(e=>setErr(e.message))},[]);

  function filtered(){
    return logs.filter(l=>{
      if(!q) return true;
      const s=q.toLowerCase();
      return (l.entity||'').toLowerCase().includes(s)||(l.user||'').toLowerCase().includes(s)||(l.action||'').toLowerCase().includes(s)||(l.detail||'').toLowerCase().includes(s);
    });
  }

  const f2=filtered();
  return <div className="page">
    <div className="page-title"><div><h1>Audit Log</h1><p>{logs.length} aktivitas tercatat</p></div></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="search-bar"><Search size={16}/><input placeholder="Cari entity, user, action..." value={q} onChange={e=>setQ(e.target.value)}/></div>
    <div className="table-scroll"><table><thead><tr><th>Waktu</th><th>User</th><th>Action</th><th>Entity</th><th>ID</th><th>Detail</th></tr></thead>
    <tbody>{f2.map(l=><tr key={l.id}>
      <td style={{fontSize:'12px'}}>{l.created_at?new Date(l.created_at).toLocaleString('id-ID'):'-'}</td>
      <td><b>{l.user}</b></td>
      <td><span className={'badge '+(l.action==='CREATE'?'green':l.action==='DELETE'?'red':'gray')}>{l.action}</span></td>
      <td>{l.entity}</td>
      <td>{l.entity_id||'-'}</td>
      <td className="td-sm" style={{maxWidth:'250px'}}>{l.detail||'-'}</td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={6} className="empty">Tidak ada log</td></tr>}</tbody></table></div>
  </div>
}
