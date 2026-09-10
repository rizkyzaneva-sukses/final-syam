import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,CheckCircle,AlertTriangle,X,Search,Filter} from 'lucide-react';

const empty={severity:'YELLOW',category:'',title:'',owner_role:'',owner_name:'',due_date:'',next_action:'',order_fk:'',status:'OPEN'};
const sevOpts=['RED','YELLOW'];
const statusOpts=['OPEN','IN_PROGRESS','RESOLVED','CLOSED'];
const catOpts=['Material','Production','Quality','Shipment','Finance','HR','Other'];

export default function ExceptionPage(){
  const [list,setList]=useState([]),[err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterSev,setFilterSev]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){api('/exceptions').then(setList).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(e=>{
      if(filterSev&&e.severity!==filterSev) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      return e.title.toLowerCase().includes(s)||e.category.toLowerCase().includes(s)||(e.owner_name||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){
        await api('/exceptions/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});
      }else{
        await api('/exceptions',{method:'POST',body:JSON.stringify(payload)});
      }
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function resolve(id){
    try{await api('/exceptions/'+id,{method:'PATCH',body:JSON.stringify({status:'RESOLVED'})});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  const openCount=list.filter(e=>e.status==='OPEN').length;
  const redCount=list.filter(e=>e.severity==='RED'&&e.status==='OPEN').length;

  return <div className="page">
    <div className="page-title"><div><h1>Exception Management</h1><p>{openCount} open • {redCount} RED critical</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Exception</button></div>
    {err&&<div className="notice danger">{err}</div>}

    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari judul, kategori, owner..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{sevOpts.map(s=><button key={s} className={'pill '+(filterSev===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterSev(filterSev===s?'':s)}>{s}</button>)}</div>
    </div>

    <div className="table-scroll"><table><thead><tr><th>Severity</th><th>Kategori</th><th>Masalah</th><th>Owner</th><th>Due Date</th><th>Next Action</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(e=><tr key={e.id}>
      <td><span className={'badge '+e.severity.toLowerCase()}>{e.severity}</span></td>
      <td>{e.category}</td>
      <td><b>{e.title}</b></td>
      <td>{e.owner_name||'-'}</td>
      <td>{e.due_date||'-'}</td>
      <td className="td-sm">{e.next_action||'-'}</td>
      <td><span className={'badge '+(e.status==='OPEN'?'red':e.status==='RESOLVED'?'green':'gray')}>{e.status}</span></td>
      <td className="td-action">
        {e.status==='OPEN'&&<button className="icon-btn" onClick={()=>setForm({...e,due_date:e.due_date||'',order_fk:e.order_fk||''})} title="Edit"><Edit2 size={15}/></button>}
        {e.status==='OPEN'&&<button className="icon-btn" onClick={()=>resolve(e.id)} title="Resolve"><CheckCircle size={15} color="#16a34a"/></button>}
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={8} className="empty">Tidak ada exception</td></tr>}</tbody></table></div>

    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Exception</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Severity *<select value={form.severity} onChange={e=>setForm({...form,severity:e.target.value})}>{sevOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          <label>Kategori *<select value={form.category} onChange={e=>setForm({...form,category:e.target.value})} required><option value="">Pilih...</option>{catOpts.map(c=><option key={c}>{c}</option>)}</select></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        </div>
        <label>Judul Masalah *<input required value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="Deskripsi singkat masalah"/></label>
        <div className="form-grid">
          <label>Owner Role<input value={form.owner_role} onChange={e=>setForm({...form,owner_role:e.target.value})} placeholder="CMO / COO / CFO..."/></label>
          <label>Owner Nama<input value={form.owner_name} onChange={e=>setForm({...form,owner_name:e.target.value})} placeholder="Nama PIC"/></label>
          <label>Due Date<input type="date" value={form.due_date} onChange={e=>setForm({...form,due_date:e.target.value})}/></label>
        </div>
        <label>Order FK (opsional)<input type="number" value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})} placeholder="ID order internal"/></label>
        <label>Next Action<textarea rows={2} value={form.next_action} onChange={e=>setForm({...form,next_action:e.target.value})} placeholder="Langkah selanjutnya..."/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
