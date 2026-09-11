import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Plus,X,Check,Search,Factory,AlertTriangle,Clock} from 'lucide-react';

const empty={article_id:'',process:'',qty_in:0,qty_done:0,qty_reject:0,status:'IN_PROCESS',pic_name:'',target_date:'',reject_reason:''};
const processes=['Cutting','Sortir','Printing','Sewing','Accessories','QC','Packing'];
const statusOpts=['WAITING','IN_PROCESS','DONE'];

export default function ProductionQueue(){
  const [movements,setMovements]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){
    Promise.all([api('/coo/movements'),api('/orders')]).then(([m,o])=>{
      setMovements(m);
      setOrders(o);
    }).catch(e=>setErr(e.message));
  }
  useEffect(load,[]);

  function getArticles(){
    const arts=[];
    orders.forEach(o=>(o.articles||[]).forEach(a=>arts.push({...a,order_id:o.order_id,buyer:o.buyer})));
    return arts;
  }

  function filtered(){
    return movements.filter(m=>{
      if(!q) return true;
      const s=q.toLowerCase();
      return m.process.toLowerCase().includes(s)||(m.pic_name||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={...form,article_id:parseInt(form.article_id),qty_in:parseInt(form.qty_in)||0,qty_done:parseInt(form.qty_done)||0,qty_reject:parseInt(form.qty_reject)||0,target_date:form.target_date||null,reject_reason:form.reject_reason||''};
      await api('/coo/movements',{method:'POST',body:JSON.stringify(payload)});
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  async function completeMovement(id){
    if(!confirm('Tandai movement ini selesai?')) return;
    try{
      await api('/coo/movements/'+id,{method:'PATCH',body:JSON.stringify({status:'DONE'})});
      load();
    }catch(x){alert(x.message)}
  }

  function calcETA(targetDate){
    if(!targetDate) return '-';
    const now=new Date();
    const target=new Date(targetDate);
    const diffMs=target-now;
    const diffDays=Math.ceil(diffMs/(1000*60*60*24));
    if(diffDays<0) return <span style={{color:'#dc2626'}}>Overdue {Math.abs(diffDays)}d</span>;
    if(diffDays===0) return <span style={{color:'#f59e0b'}}>Today</span>;
    return <span style={{color:'#16a34a'}}>{diffDays}d left</span>;
  }

  function progressPct(m){
    if(!m.qty_in||m.qty_in===0) return 0;
    return Math.round((m.qty_done/m.qty_in)*100);
  }

  const f2=filtered();
  const articles=getArticles();

  return <div className="page">
    <div className="page-title"><div><h1><Factory size={22}/> Production Queue</h1><p>{movements.length} movements tercatat</p></div>
      <button className="btn primary" onClick={()=>setForm({...empty})}><Plus size={16}/> Input Movement</button></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari proses, PIC..." value={q} onChange={e=>setQ(e.target.value)}/></div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Proses</th><th>Qty In</th><th>Qty Done</th><th>Reject</th><th>Progress</th><th>WIP</th><th>Status</th><th>PIC</th><th>Target</th><th>ETA</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(m=>{
      const pct=progressPct(m);
      return <tr key={m.id}>
      <td><b>{m.process}</b></td><td>{m.qty_in}</td><td>{m.qty_done}</td><td>{m.qty_reject}</td>
      <td><div style={{display:'flex',alignItems:'center',gap:'6px'}}><div style={{width:'60px',height:'8px',background:'#e5e7eb',borderRadius:'4px',overflow:'hidden'}}><div style={{width:pct+'%',height:'100%',background:pct>=100?'#16a34a':pct>=70?'#f59e0b':'#3b82f6',borderRadius:'4px'}}/></div><span style={{fontSize:'12px'}}>{pct}%</span></div></td>
      <td>{m.qty_in-m.qty_done-m.qty_reject}</td>
      <td><span className={'badge '+(m.status==='DONE'?'green':m.status==='IN_PROCESS'?'amber':'gray')}>{m.status}</span></td>
      <td>{m.pic_name||'-'}</td>
      <td>{m.target_date||'-'}</td>
      <td>{calcETA(m.target_date)}</td>
      <td className="td-action">
        {m.status!=='DONE'&&<button className="icon-btn" style={{color:'#16a34a'}} onClick={()=>completeMovement(m.id)} title="Complete"><Check size={15}/></button>}
      </td>
    </tr>})}
    {f2.length===0&&<tr><td colSpan={11} className="empty">Tidak ada movement</td></tr>}</tbody></table></div>

    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2><Factory size={18}/> Input Production Movement</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <label>Article *<select required value={form.article_id} onChange={e=>setForm({...form,article_id:e.target.value})}>
          <option value="">Pilih article...</option>
          {articles.map(a=><option key={a.id} value={a.id}>{a.article_code} - {a.garment_type} ({a.order_id})</option>)}
        </select></label>
        <div className="form-grid">
          <label>Proses *<select required value={form.process} onChange={e=>setForm({...form,process:e.target.value})}>
            <option value="">Pilih...</option>{processes.map(p=><option key={p}>{p}</option>)}
          </select></label>
          <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{statusOpts.map(s=><option key={s}>{s}</option>)}</select></label>
          <label>PIC Name<input value={form.pic_name} onChange={e=>setForm({...form,pic_name:e.target.value})} placeholder="Nama PIC"/></label>
        </div>
        <div className="form-grid3">
          <label>Qty In<input type="number" min={0} value={form.qty_in} onChange={e=>setForm({...form,qty_in:e.target.value})}/></label>
          <label>Qty Done<input type="number" min={0} value={form.qty_done} onChange={e=>setForm({...form,qty_done:e.target.value})}/></label>
          <label>Qty Reject<input type="number" min={0} value={form.qty_reject} onChange={e=>setForm({...form,qty_reject:e.target.value})}/></label>
        </div>
        <div className="form-grid">
          <label>Target Date<input type="date" value={form.target_date||''} onChange={e=>setForm({...form,target_date:e.target.value})}/></label>
        </div>
        <label>Reject Reason<textarea rows={2} value={form.reject_reason||''} onChange={e=>setForm({...form,reject_reason:e.target.value})} placeholder="Alasan reject (jika ada)..."/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
