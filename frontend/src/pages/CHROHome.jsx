import React,{useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api';
import {Users,BookOpen,BarChart3,AlertTriangle} from 'lucide-react';

export default function CHROHome(){
  const [data,setData]=useState(null),[err,setErr]=useState('');
  useEffect(()=>{api('/dashboard/CHRO').then(setData).catch(e=>setErr(e.message))},[]);
  if(err) return <div className="page"><div className="notice danger">{err}</div></div>;
  if(!data) return <div className="page">Memuat...</div>;
  const icons=[Users,BookOpen,BarChart3,AlertTriangle];
  return <div className="page">
    <div className="page-title"><div><h1>CHRO - Human Resources</h1><p>Dashboard utama divisi HR</p></div></div>
    <div className="cards">{data.cards.map((c,i)=>{const I=icons[i]||Users;return <div className="stat blue" key={i}><div className="stat-icon"><I size={22}/></div><strong>{c.value}</strong><span>{c.label}</span></div>})}</div>
    <div className="grid2">
      <section className="panel">
        <div className="panel-head"><h2>Akses Cepat</h2></div>
        <div className="quick-links">
          <Link to="/chro/employees" className="qlink"><Users size={20}/><div><b>Employee Management</b><small>Kelola data karyawan</small></div></Link>
          <Link to="/chro/training" className="qlink"><BookOpen size={20}/><div><b>Training Records</b><small>Catatan pelatihan karyawan</small></div></Link>
          <Link to="/chro/performance" className="qlink"><BarChart3 size={20}/><div><b>Performance Reviews</b><small>Penilaian kinerja karyawan</small></div></Link>
          <Link to="/chro/issues" className="qlink"><AlertTriangle size={20}/><div><b>Employee Issues</b><small>Track permasalahan karyawan</small></div></Link>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Alur CHRO</h2></div>
        <div className="flow-list">{data.flows.map((x,i)=><div className="flow-row" key={i}><b>{i+1}</b><span>{x}</span></div>)}</div>
      </section>
    </div>
  </div>}
