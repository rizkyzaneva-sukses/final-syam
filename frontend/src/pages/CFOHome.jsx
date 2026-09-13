import React,{useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api';
import {DollarSign,AlertTriangle,Package,Truck} from 'lucide-react';
import KPIOverview from '../components/KPIOverview';

export default function CFOHome(){
  const [data,setData]=useState(null),[err,setErr]=useState('');
  useEffect(()=>{api('/dashboard/CFO').then(setData).catch(e=>setErr(e.message))},[]);
  if(err) return <div className="page"><div className="notice danger">{err}</div></div>;
  if(!data) return <div className="page">Memuat...</div>;
  const icons=[DollarSign,AlertTriangle,Package,Package];
  return <div className="page">
    <div className="page-title"><div><h1>CFO — Finance & Purchasing</h1><p>Dashboard utama divisi Finance</p></div></div>
    <div className="cards">{data.cards.map((c,i)=>{const I=icons[i]||DollarSign;return <div className="stat blue" key={i}><div className="stat-icon"><I size={22}/></div><strong>{typeof c.value==='number'&&c.value>1000000?'Rp '+c.value.toLocaleString('id-ID'):c.value}</strong><span>{c.label}</span></div>})}</div>
    <KPIOverview kpis={data.kpis}/>
    <div className="grid2">
      <section className="panel">
        <div className="panel-head"><h2>Akses Cepat</h2></div>
        <div className="quick-links">
          <Link to="/cfo/invoices" className="qlink"><DollarSign size={20}/><div><b>Invoices</b><small>Kelola invoice & pembayaran</small></div></Link>
          <Link to="/cfo/purchase-orders" className="qlink"><Package size={20}/><div><b>Purchase Orders</b><small>Kelola pembelian material</small></div></Link>
          <Link to="/cfo/shipments" className="qlink"><Truck size={20}/><div><b>Shipment Gate</b><small>Finance gate untuk shipment</small></div></Link>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Alur CFO</h2></div>
        <div className="flow-list">{data.flows.map((x,i)=><div className="flow-row" key={i}><b>{i+1}</b><span>{x}</span></div>)}</div>
      </section>
    </div>
  </div>}
