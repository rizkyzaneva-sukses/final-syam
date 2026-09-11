import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search,Beaker} from 'lucide-react';

const empty={order_fk:'',article_code:'',status:'PROCESS',notes:'',requested_date:'',completed_date:''};
const statusOpts=['PROCESS','APPROVED','REJECTED'];

export default function SamplePPMPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/cmo/samples'),api('/orders')]).then(([s,o])=>{setList(s);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(s=>{
      if(filterStatus&&s.status!==filterStatus) return false;
      if(!q) return true;
      const t=q.toLowerCase();
      return (s.article_code||'').toLowerCase().includes(t)||(s.notes||'').toLowerCase().includes(t);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){await api('/cmo/samples/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/cmo/samples',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus sample ini?')) return;
    try{await api('/cmo/samples/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Sample PPM Management</h1><p>{list.length} sample</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Sample</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari article code, notes..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Order</th><th>Article Code</th><th>Requested</th><th>Completed</th><th>Status</th><th>Notes</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(s=><tr key={s.id}>
      <td>{orderLabel(s.order_fk)}</td>
      <td><b>{s.article_code||'-'}</b></td>
      <td>{s.requested_date||'-'}</td>
      <td>{s.completed_date||'-'}</td>
      <td><span className={'badge '+(s.status==='APPROVED'?'green':s.status==='REJECTED'?'red':'amber')}>{s.status}</span></td>
      <td>{s.notes||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...s,order_fk:s.order_fk||'',requested_date:s.requested_date||'',completed_date:s.completed_date||'',notes:s.notes||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(s.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada sample</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Sample</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Order<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Pilih order...</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} — {o.buyer}</option>)}</select></label>
          <label>Article Code *<input required value={form.article_code} onChange={e=>setForm({...form,article_code:e.target.value})} placeholder="ART-001"/></label>
        </div>
        <div className="form-grid">
          <label>Requested Date<input type="date" value={form.requested_date} onChange={e=>setForm({...form,requested_date:e.target.value})}/></label>
          <label>Completed Date<input type="date" value={form.completed_date} onChange={e=>setForm({...form,completed_date:e.target.value})}/></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        </div>
        <label>Notes<textarea value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Keterangan sample..." rows={3}/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
