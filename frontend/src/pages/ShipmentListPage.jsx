import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Edit2,X,Check,Search} from 'lucide-react';

const statusOpts=['NOT_READY','PREPARING','SHIPPED','DELIVERED'];

export default function ShipmentListPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/coo/shipments'),api('/orders')]).then(([m,o])=>{setList(m);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(m=>{
      if(filterStatus&&m.status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return (m.shipment_no||'').toLowerCase().includes(s)||(m.notes||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      await api('/coo/shipments/'+form.id,{method:'PATCH',body:JSON.stringify({status:form.status,finance_gate:form.finance_gate,ceo_approval:form.ceo_approval,notes:form.notes||''})});
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Shipments</h1><p>{list.length} total shipment</p></div></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari shipment no, notes..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Order</th><th>Shipment No</th><th>Status</th><th>Finance Gate</th><th>CEO Approval</th><th>Notes</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(m=><tr key={m.id}>
      <td>{orderLabel(m.order_id)}</td><td><b>{m.shipment_no||'-'}</b></td>
      <td><span className={'badge '+(m.status==='DELIVERED'?'green':m.status==='SHIPPED'?'blue':m.status==='PREPARING'?'amber':'red')}>{m.status}</span></td>
      <td><span className={'badge '+(m.finance_gate==='APPROVED'?'green':m.finance_gate==='REJECTED'?'red':'gray')}>{m.finance_gate||'-'}</span></td>
      <td><span className={'badge '+(m.ceo_approval==='APPROVED'?'green':m.ceo_approval==='REJECTED'?'red':'gray')}>{m.ceo_approval||'-'}</span></td>
      <td className="td-ellipsis">{m.notes||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...m})} title="Edit"><Edit2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada shipment</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>Edit Shipment {form.shipment_no||''}</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          <label>Finance Gate<select value={form.finance_gate||''} onChange={e=>setForm({...form,finance_gate:e.target.value})}><option value="">—</option><option>PENDING</option><option>APPROVED</option><option>REJECTED</option></select></label>
        </div>
        <div className="form-grid">
          <label>CEO Approval<select value={form.ceo_approval||''} onChange={e=>setForm({...form,ceo_approval:e.target.value})}><option value="">—</option><option>PENDING</option><option>APPROVED</option><option>REJECTED</option></select></label>
          <label>Notes<textarea rows={2} value={form.notes||''} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Catatan..."/></label>
        </div>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
