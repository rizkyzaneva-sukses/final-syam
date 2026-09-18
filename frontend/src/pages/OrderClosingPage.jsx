import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {useRole} from '../components/Access';
import FormModal from '../components/FormModal';

const fields={CMO_MANAGER:'customer_close_status',COO_MANAGER:'operational_close_status',CFO_MANAGER:'financial_close_status'};
const labels={CMO_MANAGER:'Customer',COO_MANAGER:'Operational',CFO_MANAGER:'Financial'};

export default function OrderClosingPage(){
  const role=useRole(),field=fields[role],label=labels[role];
  const [orders,setOrders]=useState([]),[closings,setClosings]=useState([]),[form,setForm]=useState(null);
  const [busy,setBusy]=useState(false),[err,setErr]=useState(''),[loading,setLoading]=useState(true),[q,setQ]=useState('');

  async function load(){
    try{
      const [o,c]=await Promise.all([api('/orders'),api('/coo/order-closing')]);
      setOrders(o);setClosings(c);setErr('');
    }catch(e){setErr(e.message)}finally{setLoading(false)}
  }
  useEffect(()=>{load()},[]);

  async function save(e){
    e.preventDefault();setBusy(true);setErr('');
    try{
      const payload={[field]:form[field],notes:form.notes};
      if(!form.id)payload.order_fk=form.order_fk;
      await api('/coo/order-closing/'+form.order_fk,{method:form.id?'PATCH':'POST',body:JSON.stringify(payload)});
      setForm(null);await load();
    }catch(e){setErr(e.message)}finally{setBusy(false)}
  }

  return <div className="page">
    <div className="page-title"><div><h1>Order Closing</h1><p>Customer ditutup CMO, operasional ditutup COO, dan keuangan ditutup CFO. Status akhir dihitung server setelah ketiganya Closed.</p></div></div>
    {err&&!form&&<div role="alert" className="notice danger">{err}</div>}
    <input aria-label="Cari order" placeholder="Cari order atau buyer" value={q} onChange={e=>setQ(e.target.value)}/>
    {loading?<p>Memuat...</p>:<div className="table-scroll"><table><thead><tr><th>Order</th><th>Customer</th><th>Operational</th><th>Financial</th><th>Order</th><th>Aksi</th></tr></thead><tbody>
      {orders.filter(o=>(o.order_id+' '+o.buyer).toLowerCase().includes(q.toLowerCase())).map(o=>{
        const c=closings.find(c=>c.order_fk===o.id)||{order_fk:o.id,customer_close_status:'OPEN',operational_close_status:'OPEN',financial_close_status:'OPEN',order_close_status:'OPEN',notes:''};
        const legacy=c.operational_close_status==='LEGACY_UNVERIFIED';
        return <tr key={o.id}><td>{o.order_id}<br/>{o.buyer}</td><td>{c.customer_close_status}</td><td>{legacy?'Belum diverifikasi (data lama)':c.operational_close_status}</td><td>{c.financial_close_status}</td><td>{c.order_close_status}</td><td>{field&&!legacy&&<button className="btn" onClick={()=>{setErr('');setForm({...c})}}>Review {label}</button>}</td></tr>;
      })}
    </tbody></table></div>}
    {form&&<FormModal title={`Review ${label} Closing`} onClose={()=>setForm(null)} onSubmit={save} busy={busy} error={err}>
      <label>{label} Close<select value={form[field]} onChange={e=>setForm({...form,[field]:e.target.value})}><option>OPEN</option><option>CLOSED</option></select></label>
      <label>Bukti / Catatan<textarea required value={form.notes||''} onChange={e=>setForm({...form,notes:e.target.value})}/></label>
    </FormModal>}
  </div>;
}
