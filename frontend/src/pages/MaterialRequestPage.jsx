import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search} from 'lucide-react';

const empty={item_name:'',qty:'',unit:'',order_fk:'',required_date:'',status:'REQUESTED'};
const statusOpts=['REQUESTED','ORDERED','RECEIVED','CANCELLED'];

export default function MaterialRequestPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/coo/material-requests'),api('/orders')]).then(([m,o])=>{setList(m);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(m=>{
      if(filterStatus&&m.status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return m.item_name.toLowerCase().includes(s)||(m.requested_by||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,qty:parseFloat(form.qty)||0,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){
        await api('/coo/material-requests/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});
      }else{
        await api('/coo/material-requests',{method:'POST',body:JSON.stringify(payload)});
      }
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus material request ini?')) return;
    try{await api('/coo/material-requests/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  const openCount=list.filter(m=>m.status==='REQUESTED'||m.status==='ORDERED').length;
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Material Requests</h1><p>{openCount} open dari {list.length} total</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Request Baru</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari item, requested by..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Item</th><th>Qty</th><th>Unit</th><th>Order</th><th>Required Date</th><th>Requested By</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(m=><tr key={m.id}>
      <td><b>{m.item_name}</b></td><td>{m.qty}</td><td>{m.unit||'-'}</td><td>{orderLabel(m.order_fk)}</td>
      <td>{m.required_date||'-'}</td><td>{m.requested_by||'-'}</td>
      <td><span className={'badge '+(m.status==='REQUESTED'?'red':m.status==='ORDERED'?'amber':m.status==='RECEIVED'?'green':'gray')}>{m.status}</span></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...m,qty:m.qty,order_fk:m.order_fk||'',required_date:m.required_date||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(m.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={8} className="empty">Tidak ada material request</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Request'} Material</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <label>Item Name *<input required value={form.item_name} onChange={e=>setForm({...form,item_name:e.target.value})} placeholder="Kain / Benang / Aksesoris..."/></label>
        <div className="form-grid">
          <label>Qty *<input type="number" min={0} step="any" required value={form.qty} onChange={e=>setForm({...form,qty:e.target.value})}/></label>
          <label>Unit<input value={form.unit||''} onChange={e=>setForm({...form,unit:e.target.value})} placeholder="meter / kg / pcs"/></label>
          <label>Required Date<input type="date" value={form.required_date} onChange={e=>setForm({...form,required_date:e.target.value})}/></label>
        </div>
        <div className="form-grid">
          <label>Order<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Tidak terkait order</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} - {o.buyer}</option>)}</select></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        </div>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
