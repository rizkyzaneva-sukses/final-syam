import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search} from 'lucide-react';

const empty={invoice_no:'',order_fk:'',amount:'',paid_amount:'',due_date:'',status:'UNPAID'};
const statusOpts=['UNPAID','PARTIAL','PAID'];
const fmtRp=n=>'Rp '+Number(n||0).toLocaleString('id-ID');

export default function InvoicePage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/cfo/invoices'),api('/orders')]).then(([m,o])=>{setList(m);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(m=>{
      if(filterStatus&&m.status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return m.invoice_no.toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,amount:parseFloat(form.amount)||0,paid_amount:parseFloat(form.paid_amount)||0,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){
        await api('/cfo/invoices/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});
      }else{
        await api('/cfo/invoices',{method:'POST',body:JSON.stringify(payload)});
      }
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus invoice ini?')) return;
    try{await api('/cfo/invoices/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Invoices</h1><p>{list.length} total invoice</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Invoice Baru</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari invoice no..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Invoice No</th><th>Order</th><th>Amount</th><th>Paid</th><th>Remaining</th><th>Due Date</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(m=><tr key={m.id}>
      <td><b>{m.invoice_no}</b></td><td>{orderLabel(m.order_fk)}</td><td>{fmtRp(m.amount)}</td><td>{fmtRp(m.paid_amount)}</td>
      <td>{fmtRp(m.amount-m.paid_amount)}</td><td>{m.due_date||'-'}</td>
      <td><span className={'badge '+(m.status==='PAID'?'green':m.status==='PARTIAL'?'amber':'red')}>{m.status}</span></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...m,order_fk:m.order_fk||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(m.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={8} className="empty">Tidak ada invoice</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Invoice</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Invoice No *<input required value={form.invoice_no} onChange={e=>setForm({...form,invoice_no:e.target.value})} placeholder="INV-001"/></label>
          <label>Order<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Tidak terkait order</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} - {o.buyer}</option>)}</select></label>
        </div>
        <div className="form-grid">
          <label>Amount *<input type="number" min={0} step="any" required value={form.amount} onChange={e=>setForm({...form,amount:e.target.value})}/></label>
          <label>Paid Amount<input type="number" min={0} step="any" value={form.paid_amount} onChange={e=>setForm({...form,paid_amount:e.target.value})}/></label>
        </div>
        <div className="form-grid">
          <label>Due Date<input type="date" value={form.due_date} onChange={e=>setForm({...form,due_date:e.target.value})}/></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        </div>
        {form.amount&&form.paid_amount&&<div className="notice info">Remaining: {fmtRp(parseFloat(form.amount)-parseFloat(form.paid_amount))}</div>}
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
