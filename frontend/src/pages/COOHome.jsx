import React,{useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api';
import {Factory,Package,Truck,ClipboardList,CheckSquare} from 'lucide-react';

export default function COOHome(){
  const [data,setData]=useState(null),[err,setErr]=useState('');
  useEffect(()=>{api('/dashboard/COO').then(setData).catch(e=>setErr(e.message))},[]);
  if(err) return <div className="page"><div className="notice danger">{err}</div></div>;
  if(!data) return <div className="page">Memuat...</div>;
  const icons=[Truck,Factory,ClipboardList,ClipboardList,Package];
  return <div className="page">
    <div className="page-title"><div><h1>COO — Operations</h1><p>Dashboard utama divisi Operations</p></div></div>
    <div className="cards">{data.cards.map((c,i)=>{const I=icons[i]||Factory;return <div className="stat blue" key={i}><div className="stat-icon"><I size={22}/></div><strong>{c.value}</strong><span>{c.label}</span></div>})}</div>
    <div className="grid2">
      <section className="panel">
        <div className="panel-head"><h2>Akses Cepat</h2></div>
        <div className="quick-links">
          <Link to="/coo/material-requests" className="qlink"><Truck size={20}/><div><b>Material Requests</b><small>Kelola permintaan material produksi</small></div></Link>
          <Link to="/coo/production" className="qlink"><Factory size={20}/><div><b>Production Queue</b><small>Input & monitor production movements</small></div></Link>
          <Link to="/coo/wip" className="qlink"><Package size={20}/><div><b>WIP Tracking</b><small>Work-in-progress per proses</small></div></Link>
          <Link to="/coo/qc" className="qlink"><CheckSquare size={20}/><div><b>QC Records</b><small>Quality control records & inspection</small></div></Link>
          <Link to="/cfo/shipments" className="qlink"><Truck size={20}/><div><b>Shipments</b><small>Tracking pengiriman</small></div></Link>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Alur COO</h2></div>
        <div className="flow-list">{data.flows.map((x,i)=><div className="flow-row" key={i}><b>{i+1}</b><span>{x}</span></div>)}</div>
      </section>
    </div>
  </div>}
