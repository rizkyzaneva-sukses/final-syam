import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search,ShieldCheck} from 'lucide-react';

const empty={order_fk:'',article_code:'',process:'Cutting',total_checked:'',total_pass:'',total_reject:'',reject_reason:'',inspector:'',status:'PASS',rework_parent_id:''};
const statusOpts=['PASS','FAIL','REWORK'];
const processOpts=['Cutting','Sortir','Printing','Sewing','Accessories','QC','Packing'];

export default function QCRecordPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/coo/qc-records'),api('/orders')]).then(([q,o])=>{setList(q);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(r=>{
      if(filterStatus&&r.status!==filterStatus) return false;
      if(!q) return true;
      const t=q.toLowerCase();
      return (r.article_code||'').toLowerCase().includes(t)||(r.inspector||'').toLowerCase().includes(t)||(r.reject_reason||'').toLowerCase().includes(t);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,order_fk:form.order_fk?parseInt(form.order_fk):null,total_checked:parseInt(form.total_checked)||0,total_pass:parseInt(form.total_pass)||0,total_reject:parseInt(form.total_reject)||0,rework_parent_id:form.rework_parent_id?Number(form.rework_parent_id):null};
      if(form.id){const {id,order_fk,article_code,process,rework_parent_id,...changes}=payload;await api('/coo/qc-records/'+form.id,{method:'PATCH',body:JSON.stringify(changes)});}
      else{await api('/coo/qc-records',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus QC record ini?')) return;
    try{await api('/coo/qc-records/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  function passRate(r){
    if(!r.total_checked) return '-';
    return (r.total_pass/r.total_checked*100).toFixed(1)+'%';
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>QC Records</h1><p>{list.length} record</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah QC Record</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari article code, inspector, reject reason..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Order</th><th>Article</th><th>Process</th><th>Checked</th><th>Pass</th><th>Reject</th><th>Pass Rate</th><th>Inspector</th><th>Status</th><th>Rework dari</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(r=><tr key={r.id}>
      <td>{orderLabel(r.order_fk)}</td>
      <td><b>{r.article_code||'-'}</b></td>
      <td>{r.process}</td>
      <td>{r.total_checked}</td>
      <td>{r.total_pass}</td>
      <td>{r.total_reject}</td>
      <td><span className={'badge '+(r.total_checked&&r.total_pass/r.total_checked>=0.95?'green':r.total_checked&&r.total_pass/r.total_checked>=0.85?'amber':'red')}>{passRate(r)}</span></td>
      <td>{r.inspector||'-'}</td>
      <td><span className={'badge '+(r.status==='PASS'?'green':'red')}>{r.status}</span></td>
      <td>{r.rework_parent_id ? '#'+r.rework_parent_id : '-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...r,order_fk:r.order_fk||'',total_checked:r.total_checked||'',total_pass:r.total_pass||'',total_reject:r.total_reject||'',reject_reason:r.reject_reason||'',inspector:r.inspector||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(r.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={11} className="empty">Tidak ada QC record</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} QC Record</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Order<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Pilih order...</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} — {o.buyer}</option>)}</select></label>
          <label>Article Code *<input required value={form.article_code} onChange={e=>setForm({...form,article_code:e.target.value})} placeholder="ART-001"/></label>
          <label>Process<select value={form.process} onChange={e=>setForm({...form,process:e.target.value})}>{processOpts.map(p=><option key={p}>{p}</option>)}</select></label>
        </div>
        <div className="form-grid">
          <label>Total Checked *<input type="number" min={0} required value={form.total_checked} onChange={e=>setForm({...form,total_checked:e.target.value})}/></label>
          <label>Total Pass *<input type="number" min={0} required value={form.total_pass} onChange={e=>setForm({...form,total_pass:e.target.value})}/></label>
          <label>Total Reject *<input type="number" min={0} required value={form.total_reject} onChange={e=>setForm({...form,total_reject:e.target.value})}/></label>
        </div>
        <div className="form-grid">
          <label>Inspector<input value={form.inspector} onChange={e=>setForm({...form,inspector:e.target.value})} placeholder="Nama inspector"/></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          {!form.id&&<label>Rework dari QC gagal<select value={form.rework_parent_id} onChange={e=>setForm({...form,rework_parent_id:e.target.value})}><option value="">Inspeksi pertama</option>{list.filter(r=>r.order_fk===Number(form.order_fk)&&r.article_code===form.article_code&&r.process.toUpperCase()===form.process.toUpperCase()&&['FAIL','REWORK'].includes(r.status)).map(r=><option key={r.id} value={r.id}>#{r.id} — {r.total_reject} reject</option>)}</select></label>}
        </div>
        <label>Reject Reason<textarea value={form.reject_reason} onChange={e=>setForm({...form,reject_reason:e.target.value})} placeholder="Alasan reject..." rows={3}/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
