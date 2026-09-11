import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Edit2,X,Check,Search,Truck,Send,AlertTriangle} from 'lucide-react';

const statusOpts=['NOT_READY','PREPARING','SHIPPED','DELIVERED'];

export default function ShipmentListPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);
  const [holdReason,setHoldReason]=useState('');
  const [holdTarget,setHoldTarget]=useState(null);

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
      await api('/coo/shipments/'+form.id,{method:'PATCH',body:JSON.stringify({status:form.status,finance_gate:form.finance_gate,ceo_approval:form.ceo_approval,notes:form.notes||'',tracking_no:form.tracking_no||'',shipped_date:form.shipped_date||null,delivery_date:form.delivery_date||null})});
      // Auto-create DeliveryConfirmation when status = DELIVERED
      if(form.status==='DELIVERED'){
        try{
          await api('/coo/deliveries',{method:'POST',body:JSON.stringify({shipment_fk:form.id,status:'PENDING',confirmed_by_customer:'',feedback:''})});
        }catch(e){/* delivery may already exist */}
      }
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function releaseToShip(id){
    if(!confirm('Release shipment ini untuk dikirim?')) return;
    try{
      await api('/cfo/shipments/'+id+'/gate',{method:'POST',body:JSON.stringify({status:'APPROVED'})});
      load();
    }catch(x){alert(x.message)}
  }

  async function holdShipment(id){
    setHoldTarget(id);
    setHoldReason('');
  }

  async function confirmHold(){
    if(!holdReason.trim()){alert('Alasan hold wajib diisi');return;}
    try{
      await api('/cfo/shipments/'+holdTarget+'/gate',{method:'POST',body:JSON.stringify({status:'REJECTED',reason:holdReason})});
      setHoldTarget(null); setHoldReason(''); load();
    }catch(x){alert(x.message)}
  }

  async function ceoApprove(id){
    if(!confirm('CEO: Setujui shipment ini?')) return;
    try{
      await api('/ceo/shipments/'+id+'/approve-shipment',{method:'POST',body:JSON.stringify({status:'APPROVED'})});
      load();
    }catch(x){alert(x.message)}
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1><Truck size={22}/> Shipments</h1><p>{list.length} total shipment</p></div></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari shipment no, notes..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Order</th><th>Shipment No</th><th>Status</th><th>Finance Gate</th><th>CEO Approval</th><th>Tracking</th><th>Shipped</th><th>Delivery</th><th>Notes</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(m=><tr key={m.id}>
      <td>{orderLabel(m.order_id)}</td><td><b>{m.shipment_no||'-'}</b></td>
      <td><span className={'badge '+(m.status==='DELIVERED'?'green':m.status==='SHIPPED'?'blue':m.status==='PREPARING'?'amber':'red')}>{m.status}</span></td>
      <td><span className={'badge '+(m.finance_gate==='APPROVED'?'green':m.finance_gate==='REJECTED'?'red':'gray')}>{m.finance_gate||'-'}</span></td>
      <td><span className={'badge '+(m.ceo_approval==='APPROVED'?'green':m.ceo_approval==='REJECTED'?'red':'gray')}>{m.ceo_approval||'-'}</span></td>
      <td>{m.tracking_no||'-'}</td>
      <td>{m.shipped_date||'-'}</td>
      <td>{m.delivery_date||'-'}</td>
      <td className="td-ellipsis">{m.notes||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...m})} title="Edit"><Edit2 size={15}/></button>
        {m.status==='PREPARING'&&m.finance_gate!=='APPROVED'&&<button className="icon-btn" style={{color:'#16a34a'}} onClick={()=>releaseToShip(m.id)} title="Release to Ship"><Send size={15}/></button>}
        {m.status==='PREPARING'&&m.finance_gate!=='REJECTED'&&<button className="icon-btn danger" onClick={()=>holdShipment(m.id)} title="Hold Shipment"><AlertTriangle size={15}/></button>}
        {m.finance_gate==='APPROVED'&&m.ceo_approval!=='APPROVED'&&<button className="icon-btn" style={{color:'#2563eb'}} onClick={()=>ceoApprove(m.id)} title="CEO Approve"><Check size={15}/></button>}
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={10} className="empty">Tidak ada shipment</td></tr>}</tbody></table></div>
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
          <label>Tracking No<input value={form.tracking_no||''} onChange={e=>setForm({...form,tracking_no:e.target.value})} placeholder="Nomor resi / tracking"/></label>
        </div>
        <div className="form-grid">
          <label>Shipped Date<input type="date" value={form.shipped_date||''} onChange={e=>setForm({...form,shipped_date:e.target.value})}/></label>
          <label>Delivery Date<input type="date" value={form.delivery_date||''} onChange={e=>setForm({...form,delivery_date:e.target.value})}/></label>
        </div>
        <label>Notes<textarea rows={2} value={form.notes||''} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Catatan..."/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
    {holdTarget&&<div className="modal-bg" onClick={()=>setHoldTarget(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2><AlertTriangle size={18}/> Hold Shipment</h2><button className="icon-btn" onClick={()=>setHoldTarget(null)}><X size={18}/></button></div>
      <div style={{padding:'1rem'}}>
        <label>Alasan Hold *<textarea required rows={3} value={holdReason} onChange={e=>setHoldReason(e.target.value)} placeholder="Alasan shipment di-hold..."/></label>
      </div>
      <div className="modal-foot"><button className="btn" onClick={()=>setHoldTarget(null)}>Batal</button><button className="btn danger" onClick={confirmHold}><AlertTriangle size={14}/> Hold</button></div>
    </div></div>}
  </div>
}
