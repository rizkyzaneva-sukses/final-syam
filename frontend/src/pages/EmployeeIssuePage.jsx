import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search,AlertTriangle} from 'lucide-react';

const empty={employee_id:'',issue_type:'Attendance',description:'',severity:'YELLOW',status:'OPEN',reported_by:''};
const issueTypes=['Attendance','Quality','Discipline','Safety','Other'];
const severityOpts=['RED','YELLOW'];
const statusOpts=['OPEN','IN_PROGRESS','RESOLVED','CLOSED'];

export default function EmployeeIssuePage(){
  const [list,setList]=useState([]),[employees,setEmployees]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterSeverity,setFilterSeverity]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/chro/issues'),api('/chro/employees')]).then(([i,e])=>{setList(i);setEmployees(e)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(i=>{
      if(filterSeverity&&i.severity!==filterSeverity) return false;
      if(filterStatus&&i.status!==filterStatus) return false;
      if(!q) return true;
      const t=q.toLowerCase();
      const emp=employees.find(e=>e.id===i.employee_id);
      return (emp?.name||'').toLowerCase().includes(t)||(i.description||'').toLowerCase().includes(t)||(i.reported_by||'').toLowerCase().includes(t);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,employee_id:form.employee_id?parseInt(form.employee_id):null};
      if(form.id){await api('/chro/issues/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/chro/issues',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus issue ini?')) return;
    try{await api('/chro/issues/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  const openCount=list.filter(i=>i.status==='OPEN'||i.status==='IN_PROGRESS').length;
  function empName(id){const e=employees.find(e=>e.id===id);return e?e.name:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Employee Issues</h1><p>{openCount} open dari {list.length} total</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Issue</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari karyawan, deskripsi, reported by..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">
        {severityOpts.map(s=><button key={s} className={'pill '+(filterSeverity===s?'active '+(s==='RED'?'red':'amber'):'')} onClick={()=>setFilterSeverity(filterSeverity===s?'':s)}>{s}</button>)}
        {statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s.replace('_',' ')}</button>)}
      </div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Karyawan</th><th>Issue Type</th><th>Description</th><th>Severity</th><th>Reported By</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(i=><tr key={i.id}>
      <td><b>{empName(i.employee_id)}</b></td>
      <td>{i.issue_type}</td>
      <td>{i.description||'-'}</td>
      <td><span className={'badge '+(i.severity==='RED'?'red':'amber')}>{i.severity}</span></td>
      <td>{i.reported_by||'-'}</td>
      <td><span className={'badge '+(i.status==='OPEN'?'red':i.status==='IN_PROGRESS'?'amber':i.status==='RESOLVED'?'green':'gray')}>{i.status.replace('_',' ')}</span></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...i,employee_id:i.employee_id||'',description:i.description||'',reported_by:i.reported_by||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(i.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada issue</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Issue</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Karyawan *<select required value={form.employee_id} onChange={e=>setForm({...form,employee_id:e.target.value})}><option value="">Pilih karyawan...</option>{employees.map(e=><option key={e.id} value={e.id}>{e.name} ({e.division})</option>)}</select></label>
          <label>Issue Type<select value={form.issue_type} onChange={e=>setForm({...form,issue_type:e.target.value})}>{issueTypes.map(t=><option key={t}>{t}</option>)}</select></label>
        </div>
        <label>Description *<textarea required value={form.description} onChange={e=>setForm({...form,description:e.target.value})} placeholder="Deskripsi issue..." rows={3}/></label>
        <div className="form-grid">
          <label>Severity<select value={form.severity} onChange={e=>setForm({...form,severity:e.target.value})}>{severityOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          <label>Reported By<input value={form.reported_by} onChange={e=>setForm({...form,reported_by:e.target.value})} placeholder="Nama pelapor"/></label>
        </div>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
