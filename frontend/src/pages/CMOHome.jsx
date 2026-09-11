import React,{useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api';
import {ShoppingCart,Users,FileText,ClipboardList,Package,CheckSquare} from 'lucide-react';

export default function CMOHome(){
  const [data,setData]=useState(null),[err,setErr]=useState('');
  useEffect(()=>{api('/dashboard/CMO').then(setData).catch(e=>setErr(e.message))},[]);
  if(err) return <div className="page"><div className="notice danger">{err}</div></div>;
  if(!data) return <div className="page">Memuat...</div>;
  const icons=[ShoppingCart,Users,FileText,ClipboardList,Package];
  return <div className="page">
    <div className="page-title"><div><h1>CMO — Marketing & Order</h1><p>Dashboard utama divisi Commercial Marketing</p></div></div>
    <div className="cards">{data.cards.map((c,i)=>{const I=icons[i]||ShoppingCart;return <div className="stat blue" key={i}><div className="stat-icon"><I size={22}/></div><strong>{c.value}</strong><span>{c.label}</span></div>})}</div>
    <div className="grid2">
      <section className="panel">
        <div className="panel-head"><h2>Akses Cepat</h2></div>
        <div className="quick-links">
          <Link to="/cmo/orders" className="qlink"><ShoppingCart size={20}/><div><b>Order Management</b><small>Kelola semua order dari buyer</small></div></Link>
          <Link to="/cmo/customers" className="qlink"><Users size={20}/><div><b>Customer / Buyer</b><small>Kelola data customer & kontak</small></div></Link>
          <Link to="/cmo/quotations" className="qlink"><FileText size={20}/><div><b>Quotations</b><small>Kelola penawaran harga</small></div></Link>
          <Link to="/cmo/samples" className="qlink"><ClipboardList size={20}/><div><b>Sample / PPM</b><small>Tracking sample production</small></div></Link>
          <Link to="/cmo/spk" className="qlink"><CheckSquare size={20}/><div><b>SPK</b><small>Surat perintah kerja</small></div></Link>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Alur CMO</h2></div>
        <div className="flow-list">{data.flows.map((x,i)=><div className="flow-row" key={i}><b>{i+1}</b><span>{x}</span></div>)}</div>
      </section>
    </div>
  </div>}
