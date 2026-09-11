import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search} from 'lucide-react';

const empty={po_no:'',item:'',qty:'',unit:'',supplier:'',amount:'',order_fk:'',status:'PENDING'};
const statusOpts=['PENDING','ORDERED','RECEIVED','CANCELLED'];
const fmtRp=n=>'Rp '+Number(n||0).toLocaleString('id-ID');

export default function PurchaseOrderPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/cfo/purchase-orders'),api('/orders')]).then(([m,o])=>{setList(m);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(m=>{
      if(filterStatus&&m.status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return m.po_no.toLowerCase().includes(s)||(m.item||'').toLowerCase().includes(s)||(m.supplier||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,qty:parseFloat(form.qty)||0,amount:parseFloat(form.amount)||0,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){
        await api('/cfo/purchase-orders/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});
      }else{
        await api('/cfo/purchase-orders',{method:'POST',body:JSON.stringify(payload)});
      }
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus purchase order ini?')) return;
    try{await api('/cfo/purchase-orders/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Purchase Orders</h1><p>{list.length} total PO</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> PO Baru</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari PO no, item, supplier..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>PO No</th><th>Item</th><th>Qty</th><th>Unit</th><th>Supplier</th><th>Amount</th><th>Order</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(m=><tr key={m.id}>
      <td><b>{m.po_no}</b></td><td>{m.item}</td><td>{m.qty}</td><td>{m.unit||'-'}</td><td>{m.supplier||'-'}</td><td>{fmtRp(m.amount)}</td><td>{orderLabel(m.order_fk)}</td>
      <td><span className={'badge '+(m.status==='RECEIVED'?'green':m.status==='ORDERED'?'amber':m.status==='CANCELLED'?'gray':'red')}>{m.status}</span></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...m,qty:m.qty,amount:m.amount,order_fk:m.order_fk||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(m.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={9} className="empty">Tidak ada purchase order</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Purchase Order</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>PO No *<input required value={form.po_no} onChange={e=>setForm({...form,po_no:e.target.value})} placeholder="PO-001"/></label>
          <label>Item *<input required value={form.item} onChange={e=>setForm({...form,item:e.target.value})} placeholder="Kain / Benang..."/></label>
        </div>
        <div className="form-grid">
          <label>Qty *<input type="number" min={0} step="any" required value={form.qty} onChange={e=>setForm({...form,qty:e.target.value})}/></label>
          <label>Unit<input value={form.unit||''} onChange={e=>setForm({...form,unit:e.target.value})} placeholder="meter / kg / pcs"/></label>
        </div>
        <div className="form-grid">
          <label>Supplier<input value={form.supplier||''} onChange={e=>setForm({...form,supplier:e.target.value})} placeholder="Nama supplier"/></label>
          <label>Amount *<input type="number" min={0} step="any" required value={form.amount} onChange={e=>setForm({...form,amount:e.target.value})}/></label>
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
