import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search,FileText} from 'lucide-react';

const empty={quotation_no:'',order_fk:'',amount:'',status:'DRAFT',valid_until:'',notes:''};
const statusOpts=['DRAFT','SENT','APPROVED','REJECTED'];
const fmtRp=n=>n!=null?'Rp '+Number(n).toLocaleString('id-ID'):'-';

export default function QuotationPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/cmo/quotations'),api('/orders')]).then(([q,o])=>{setList(q);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(q=>{
      if(filterStatus&&q.status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return (q.quotation_no||'').toLowerCase().includes(s)||(q.notes||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,amount:parseFloat(form.amount)||0,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){await api('/cmo/quotations/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/cmo/quotations',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus quotation ini?')) return;
    try{await api('/cmo/quotations/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Quotation Management</h1><p>{list.length} quotation</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Quotation</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari nomor quotation, notes..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>No. Quotation</th><th>Order</th><th>Amount</th><th>Valid Until</th><th>Status</th><th>Notes</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(q=><tr key={q.id}>
      <td><b>{q.quotation_no||'-'}</b></td>
      <td>{orderLabel(q.order_fk)}</td>
      <td>{fmtRp(q.amount)}</td>
      <td>{q.valid_until||'-'}</td>
      <td><span className={'badge '+(q.status==='APPROVED'?'green':q.status==='SENT'?'amber':q.status==='REJECTED'?'red':'gray')}>{q.status}</span></td>
      <td>{q.notes||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...q,order_fk:q.order_fk||'',amount:q.amount||'',valid_until:q.valid_until||'',notes:q.notes||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(q.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada quotation</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Quotation</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Quotation No. *<input required value={form.quotation_no} onChange={e=>setForm({...form,quotation_no:e.target.value})} placeholder="QTN-001"/></label>
          <label>Order<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Pilih order...</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} — {o.buyer}</option>)}</select></label>
        </div>
        <div className="form-grid">
          <label>Amount (Rp) *<input type="number" min={0} step="any" required value={form.amount} onChange={e=>setForm({...form,amount:e.target.value})} placeholder="0"/></label>
          <label>Valid Until<input type="date" value={form.valid_until} onChange={e=>setForm({...form,valid_until:e.target.value})}/></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        </div>
        <label>Notes<textarea value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Keterangan quotation..." rows={3}/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
