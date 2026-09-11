import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search} from 'lucide-react';

const empty={decision_type:'',subject:'',decision:'',reason:'',owner_name:'',due_date:'',order_fk:'',action_status:'OPEN'};
const typeOpts=['Override','Financial Gate','Material Exception','Quality Hold','Shipment Hold','Other'];
const statusOpts=['OPEN','IN_PROGRESS','APPROVED','REJECTED','CLOSED'];

export default function DecisionPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/ceo/decisions'),api('/orders')]).then(([d,o])=>{setList(d);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(d=>{
      if(filterStatus&&d.action_status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return d.subject.toLowerCase().includes(s)||(d.decision_type||'').toLowerCase().includes(s)||(d.owner_name||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){await api('/ceo/decisions/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/ceo/decisions',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus decision ini?')) return;
    try{await api('/ceo/decisions/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  const openCount=list.filter(d=>d.action_status==='OPEN').length;

  return <div className="page">
    <div className="page-title"><div><h1>Decision Management</h1><p>{openCount} open decisions</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Decision Baru</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari subject, tipe, owner..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s.replace('_',' ')}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Tipe</th><th>Subject</th><th>Decision</th><th>Owner</th><th>Due</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(d=><tr key={d.id}>
      <td><span className="badge gray">{d.decision_type}</span></td>
      <td><b>{d.subject}</b></td>
      <td className="td-sm">{d.decision||'-'}</td>
      <td>{d.owner_name||'-'}</td>
      <td>{d.due_date||'-'}</td>
      <td><span className={'badge '+(d.action_status==='OPEN'?'red':d.action_status==='APPROVED'?'green':d.action_status==='IN_PROGRESS'?'amber':'gray')}>{d.action_status.replace('_',' ')}</span></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...d,order_fk:d.order_fk||'',due_date:d.due_date||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(d.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada decision</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Buat'} Decision</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Tipe *<select required value={form.decision_type} onChange={e=>setForm({...form,decision_type:e.target.value})}><option value="">Pilih...</option>{typeOpts.map(t=><option key={t}>{t}</option>)}</select></label>
          <label>Status<select value={form.action_status} onChange={e=>setForm({...form,action_status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          <label>Order FK<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Tidak terkait</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} - {o.buyer}</option>)}</select></label>
        </div>
        <label>Subject *<input required value={form.subject} onChange={e=>setForm({...form,subject:e.target.value})} placeholder="Judul keputusan"/></label>
        <label>Decision<textarea rows={2} value={form.decision} onChange={e=>setForm({...form,decision:e.target.value})} placeholder="Keputusan yang diambil..."/></label>
        <label>Reason<textarea rows={2} value={form.reason} onChange={e=>setForm({...form,reason:e.target.value})} placeholder="Alasan keputusan..."/></label>
        <div className="form-grid">
          <label>Owner Nama<input value={form.owner_name} onChange={e=>setForm({...form,owner_name:e.target.value})} placeholder="PIC"/></label>
          <label>Due Date<input type="date" value={form.due_date} onChange={e=>setForm({...form,due_date:e.target.value})}/></label>
        </div>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
