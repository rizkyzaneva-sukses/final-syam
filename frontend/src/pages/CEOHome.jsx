import React,{useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api';
import {Crown,AlertTriangle,ClipboardList,Users} from 'lucide-react';

export default function CEOHome(){
  const [data,setData]=useState(null),[err,setErr]=useState('');
  useEffect(()=>{api('/dashboard/CEO').then(setData).catch(e=>setErr(e.message))},[]);
  if(err) return <div className="page"><div className="notice danger">{err}</div></div>;
  if(!data) return <div className="page">Memuat...</div>;
  const icons=[ClipboardList,AlertTriangle,Crown,Users];
  return <div className="page">
    <div className="page-title"><div><h1>CEO Control</h1><p>Strategic oversight & decision making</p></div></div>
    <div className="cards">{data.cards.map((c,i)=>{const I=icons[i]||Crown;return <div className="stat blue" key={i}><div className="stat-icon"><I size={22}/></div><strong>{c.value}</strong><span>{c.label}</span></div>})}</div>
    <div className="grid2">
      <section className="panel">
        <div className="panel-head"><h2>Akses Cepat</h2></div>
        <div className="quick-links">
          <Link to="/ceo/decisions" className="qlink"><ClipboardList size={20}/><div><b>Decision Management</b><small>Kelola keputusan & action items</small></div></Link>
          <Link to="/exceptions" className="qlink"><AlertTriangle size={20}/><div><b>Exception Overview</b><small>Monitor semua exception lintas divisi</small></div></Link>
          <Link to="/master" className="qlink"><Crown size={20}/><div><b>Master Control</b><small>Control tower untuk semua operasi</small></div></Link>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Alur CEO</h2></div>
        <div className="flow-list">{data.flows.map((x,i)=><div className="flow-row" key={i}><b>{i+1}</b><span>{x}</span></div>)}</div>
      </section>
    </div>
  </div>
}
