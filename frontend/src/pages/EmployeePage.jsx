import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search} from 'lucide-react';

const empty={employee_no:'',name:'',division:'',position:'',employment_status:'ACTIVE'};
const statusOpts=['ACTIVE','INACTIVE','ON_LEAVE','TERMINATED'];
const divisions=['Production','Cutting','Printing','Sewing','QC','Packing','HR','Finance','Marketing','Warehouse','Admin'];

export default function EmployeePage(){
  const [list,setList]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){api('/chro/employees').then(setList).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(e=>{
      if(!q) return true;
      const s=q.toLowerCase();
      return e.name.toLowerCase().includes(s)||(e.employee_no||'').toLowerCase().includes(s)||(e.division||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      if(form.id){await api('/chro/employees/'+form.id,{method:'PATCH',body:JSON.stringify(form)});}
      else{await api('/chro/employees',{method:'POST',body:JSON.stringify(form)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus karyawan ini?')) return;
    try{await api('/chro/employees/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  const activeCount=list.filter(e=>e.employment_status==='ACTIVE').length;

  return <div className="page">
    <div className="page-title"><div><h1>Employee Management</h1><p>{activeCount} active dari {list.length} total</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Karyawan</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari nama, NIP, divisi..." value={q} onChange={e=>setQ(e.target.value)}/></div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>NIP</th><th>Nama</th><th>Divisi</th><th>Posisi</th><th>Status</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(e=><tr key={e.id}>
      <td>{e.employee_no}</td>
      <td><b>{e.name}</b></td>
      <td>{e.division||'-'}</td>
      <td>{e.position||'-'}</td>
      <td><span className={'badge '+(e.employment_status==='ACTIVE'?'green':e.employment_status==='ON_LEAVE'?'amber':'gray')}>{e.employment_status}</span></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...e})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(e.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={6} className="empty">Tidak ada karyawan</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Karyawan</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>NIP *<input required value={form.employee_no} onChange={e=>setForm({...form,employee_no:e.target.value})} placeholder="EMP-001"/></label>
          <label>Nama *<input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>
        </div>
        <div className="form-grid">
          <label>Divisi<select value={form.division||''} onChange={e=>setForm({...form,division:e.target.value})}><option value="">Pilih...</option>{divisions.map(d=><option key={d}>{d}</option>)}</select></label>
          <label>Posisi<input value={form.position||''} onChange={e=>setForm({...form,position:e.target.value})} placeholder="Operator / Leader / Supervisor"/></label>
          <label>Status<select value={form.employment_status} onChange={e=>setForm({...form,employment_status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        </div>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
