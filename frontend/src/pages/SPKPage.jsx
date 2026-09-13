import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,Edit2,Trash2,X,Check,Search,ClipboardList} from 'lucide-react';

const empty={spk_no:'',order_fk:'',status:'NEW',notes:''};
const statusOpts=['NEW','RELEASED','CANCELLED'];

export default function SPKPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/cmo/spk'),api('/orders')]).then(([s,o])=>{setList(s);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(s=>{
      if(filterStatus&&s.status!==filterStatus) return false;
      if(!q) return true;
      const t=q.toLowerCase();
      return (s.spk_no||'').toLowerCase().includes(t)||(s.notes||'').toLowerCase().includes(t);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,order_fk:form.order_fk?parseInt(form.order_fk):null};
      if(form.id){await api('/cmo/spk/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});}
      else{await api('/cmo/spk',{method:'POST',body:JSON.stringify(payload)});}
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function del(id){
    if(!confirm('Hapus SPK ini?')) return;
    try{await api('/cmo/spk/'+id,{method:'DELETE'});load();}catch(x){alert(x.message)}
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}

  return <div className="page">
    <div className="page-title"><div><h1>SPK Management</h1><p>{list.length} SPK</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Tambah SPK</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari nomor SPK, notes..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s.replace('_',' ')}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>No. SPK</th><th>Order</th><th>Status</th><th>Notes</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(s=><tr key={s.id}>
      <td><b>{s.spk_no||'-'}</b></td>
      <td>{orderLabel(s.order_fk)}</td>
      <td><span className={'badge '+(s.status==='DONE'?'green':s.status==='IN_PROCESS'?'amber':s.status==='CANCELLED'?'gray':'red')}>{s.status.replace('_',' ')}</span></td>
      <td>{s.notes||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...s,order_fk:s.order_fk||'',notes:s.notes||''})} title="Edit"><Edit2 size={15}/></button>
        <button className="icon-btn danger" onClick={()=>del(s.id)} title="Hapus"><Trash2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={5} className="empty">Tidak ada SPK</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>{form.id?'Edit':'Tambah'} SPK</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>SPK No. *<input required value={form.spk_no} onChange={e=>setForm({...form,spk_no:e.target.value})} placeholder="SPK-001"/></label>
          <label>Order<select value={form.order_fk} onChange={e=>setForm({...form,order_fk:e.target.value})}><option value="">Pilih order...</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} — {o.buyer}</option>)}</select></label>
        </div>
        <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
        <label>Notes<textarea value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Keterangan SPK..." rows={3}/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
