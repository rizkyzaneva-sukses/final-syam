import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,X,Check,Search} from 'lucide-react';

const empty={employee_id:'',title:'',start_date:'',end_date:'',result:'',evaluator:''};

export default function TrainingPage(){
  const [list,setList]=useState([]),[employees,setEmployees]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/chro/trainings'),api('/chro/employees')]).then(([t,e])=>{setList(t);setEmployees(e)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(t=>{
      if(!q) return true;
      const s=q.toLowerCase();
      return t.title.toLowerCase().includes(s)||(t.evaluator||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,employee_id:parseInt(form.employee_id)};
      if(form.id){await api('/chro/trainings/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/chro/trainings',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  const f2=filtered();
  function empName(id){const e=employees.find(e=>e.id===id);return e?e.name:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>Training Records</h1><p>{list.length} catatan pelatihan</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah Training</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari judul training, evaluator..." value={q} onChange={e=>setQ(e.target.value)}/></div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Karyawan</th><th>Judul Training</th><th>Start</th><th>End</th><th>Hasil</th><th>Evaluator</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(t=><tr key={t.id}>
      <td><b>{empName(t.employee_id)}</b></td>
      <td>{t.title}</td>
      <td>{t.start_date||'-'}</td>
      <td>{t.end_date||'-'}</td>
      <td>{t.result||'-'}</td>
      <td>{t.evaluator||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...t,employee_id:t.employee_id,start_date:t.start_date||'',end_date:t.end_date||''})} title="Edit"><Edit2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada training record</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} Training</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <label>Karyawan *<select required value={form.employee_id} onChange={e=>setForm({...form,employee_id:e.target.value})}><option value="">Pilih...</option>{employees.map(e=><option key={e.id} value={e.id}>{e.name} ({e.division})</option>)}</select></label>
        <label>Judul Training *<input required value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="Safety / Skill / Leadership..."/></label>
        <div className="form-grid">
          <label>Start Date<input type="date" value={form.start_date} onChange={e=>setForm({...form,start_date:e.target.value})}/></label>
          <label>End Date<input type="date" value={form.end_date} onChange={e=>setForm({...form,end_date:e.target.value})}/></label>
        </div>
        <div className="form-grid">
          <label>Hasil<input value={form.result} onChange={e=>setForm({...form,result:e.target.value})} placeholder="Pass / Fail / Score"/></label>
          <label>Evaluator<input value={form.evaluator} onChange={e=>setForm({...form,evaluator:e.target.value})}/></label>
        </div>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
