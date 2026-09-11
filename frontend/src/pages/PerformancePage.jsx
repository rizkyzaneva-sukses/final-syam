import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,X,Check,Search} from 'lucide-react';

const empty={employee_id:'',period:'',quality:'',responsibility:'',discipline:'',spiritual:'',attitude:'',skill:'',notes:''};

export default function PerformancePage(){
  const [list,setList]=useState([]),[employees,setEmployees]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/chro/performances'),api('/chro/employees')]).then(([p,e])=>{setList(p);setEmployees(e)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(p=>{
      if(!q) return true;
      const s=q.toLowerCase();
      return empName(p.employee_id).toLowerCase().includes(s)||(p.period||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,employee_id:parseInt(form.employee_id),quality:parseFloat(form.quality)||null,responsibility:parseFloat(form.responsibility)||null,discipline:parseFloat(form.discipline)||null,spiritual:parseFloat(form.spiritual)||null,attitude:parseFloat(form.attitude)||null,skill:parseFloat(form.skill)||null};
      if(form.id){await api('/chro/performances/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/chro/performances',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  const f2=filtered();
  function empName(id){const e=employees.find(e=>e.id===id);return e?e.name:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Performance Reviews</h1><p>{list.length} penilaian</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Penilaian</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari nama karyawan, periode..." value={q} onChange={e=>setQ(e.target.value)}/></div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Karyawan</th><th>Periode</th><th>Quality</th><th>Responsibility</th><th>Discipline</th><th>Skill</th><th>Total</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(p=><tr key={p.id}>
      <td><b>{empName(p.employee_id)}</b></td>
      <td>{p.period}</td>
      <td>{p.quality||'-'}</td>
      <td>{p.responsibility||'-'}</td>
      <td>{p.discipline||'-'}</td>
      <td>{p.skill||'-'}</td>
      <td><b>{p.total_score||'-'}</b></td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...p,employee_id:p.employee_id,quality:p.quality||'',responsibility:p.responsibility||'',discipline:p.discipline||'',spiritual:p.spiritual||'',attitude:p.attitude||'',skill:p.skill||''})} title="Edit"><Edit2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={8} className="empty">Belum ada penilaian</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Penilaian</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <label>Karyawan *<select required value={form.employee_id} onChange={e=>setForm({...form,employee_id:e.target.value})}><option value="">Pilih...</option>{employees.map(e=><option key={e.id} value={e.id}>{e.name} ({e.division})</option>)}</select></label>
        <label>Periode *<input required value={form.period} onChange={e=>setForm({...form,period:e.target.value})} placeholder="Q3-2026 / Sept 2026"/></label>
        <div className="form-grid3">
          <label>Quality (0-100)<input type="number" min={0} max={100} value={form.quality} onChange={e=>setForm({...form,quality:e.target.value})}/></label>
          <label>Responsibility (0-100)<input type="number" min={0} max={100} value={form.responsibility} onChange={e=>setForm({...form,responsibility:e.target.value})}/></label>
          <label>Discipline (0-100)<input type="number" min={0} max={100} value={form.discipline} onChange={e=>setForm({...form,discipline:e.target.value})}/></label>
        </div>
        <div className="form-grid3">
          <label>Spiritual (0-100)<input type="number" min={0} max={100} value={form.spiritual} onChange={e=>setForm({...form,spiritual:e.target.value})}/></label>
          <label>Attitude (0-100)<input type="number" min={0} max={100} value={form.attitude} onChange={e=>setForm({...form,attitude:e.target.value})}/></label>
          <label>Skill (0-100)<input type="number" min={0} max={100} value={form.skill} onChange={e=>setForm({...form,skill:e.target.value})}/></label>
        </div>
        <label>Catatan<textarea rows={2} value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})}/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
