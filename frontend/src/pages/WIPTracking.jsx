import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Package,RefreshCw} from 'lucide-react';

export default function WIPTracking(){
  const [wip,setWip]=useState([]),[capacity,setCap]=useState([]);
  const [err,setErr]=useState('');
  const [loading,setLoading]=useState(true);

  function load(){
    setLoading(true);
    Promise.all([api('/coo/wip-summary'),api('/master/wip-capacity')]).then(([w,c])=>{setWip(w);setCap(c)}).catch(e=>setErr(e.message)).finally(()=>setLoading(false));
  }
  useEffect(load,[]);

  const capMap={};capacity.forEach(c=>{capMap[c.process]=c});

  return <div className="page">
    <div className="page-title"><div><h1>WIP Tracking</h1><p>Work-in-progress per proses produksi</p></div>
      <button className="btn" onClick={load}><RefreshCw size={14}/> Refresh</button></div>
    {err&&<div className="notice danger">{err}</div>}
    {loading?<div className="page">Memuat...</div>:<>
    <div className="cards">{wip.map((w,i)=><div className="stat blue" key={i}><strong>{w.wip}</strong><span>{w.process} WIP</span></div>)}</div>
    <div className="table-scroll"><table><thead><tr><th>Proses</th><th>Qty In (total)</th><th>Qty Done</th><th>Reject</th><th>WIP (current)</th><th>Capacity</th><th>Planned Load</th><th>Utilization</th></tr></thead>
    <tbody>{wip.map((w,i)=>{
      const c=capMap[w.process]||{};
      const util=c.capacity?Math.round((c.planned_load/c.capacity)*100):'-';
      return <tr key={i}>
        <td><b>{w.process}</b></td><td>{w.qty_in}</td><td>{w.qty_done}</td><td>{w.qty_reject}</td>
        <td><b>{w.wip}</b></td>
        <td>{c.capacity||'-'}</td><td>{c.planned_load||'-'}</td>
        <td><span className={typeof util==='number'&&util>100?'badge red':typeof util==='number'&&util>80?'badge amber':'badge green'}>{util}%</span></td>
      </tr>
    })}
    {wip.length===0&&<tr><td colSpan={8} className="empty">Belum ada data WIP</td></tr>}</tbody></table></div>
    </>}
  </div>
}
