
import React,{useEffect,useState} from 'react';
import {useParams,Link} from 'react-router-dom';
import {api} from '../api';

const labels={CMO:'CMO — Marketing & Order',CFO:'CFO — Finance & Purchasing',COO:'COO — Operations & Production',CHRO:'CHRO — Human Resources',CEO:'CEO — Strategic & Exception',SAMPLE:'Sample PIC',PRINTING:'Printing / Bordir PIC',PRODUCTION:'Production PIC',SHIPMENT:'Shipment',TASK:'Task',EXCEPTION:'Exception'};

export default function ModuleDashboard(){
  const {name}=useParams(); const module=name.toUpperCase();
  const [data,setData]=useState(null); const [err,setErr]=useState('');
  useEffect(()=>{api('/dashboard/'+module).then(setData).catch(e=>setErr(e.message))},[module]);
  if(err) return <div className="page"><div className="notice danger">{err}</div></div>;
  if(!data) return <div className="page">Memuat...</div>;
  return <div className="page">
    <div className="page-head"><div><h1>{labels[module]||module}</h1><p>Workspace sesuai role. Data terhubung ke Order ID dan Master Control yang sama.</p></div></div>
    <div className="kpis">{data.cards.map((c,i)=><div className="card kpi" key={i}><span>{c.label}</span><strong>{typeof c.value==='number'&&c.value>1000000?'Rp '+c.value.toLocaleString('id-ID'):c.value}</strong></div>)}</div>
    <div className="grid two">
      <section className="card"><h2>Alur / Modul</h2><div className="flow-list">{data.flows.map((x,i)=><div className="flow-row" key={i}><b>{i+1}</b><span>{x}</span></div>)}</div></section>
      <section className="card"><h2>Prinsip Workspace</h2>
        <ul><li>Input dilakukan oleh source owner.</li><li>Master Control membaca data tanpa input ulang.</li><li>Action kritis tunduk pada role & permission backend.</li><li>Perubahan penting tercatat melalui audit trail.</li></ul>
        <Link className="btn" to="/master">Buka Master Control</Link>
      </section>
    </div>
  </div>
}
