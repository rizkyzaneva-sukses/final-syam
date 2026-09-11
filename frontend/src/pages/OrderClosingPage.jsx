import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Edit2,X,Check,Search,DollarSign} from 'lucide-react';

const statusOpts=['OPEN','CLOSED'];

export default function OrderClosingPage(){
  const [list,setList]=useState([]),[orders,setOrders]=useState([]);
  const [err,setErr]=useState('');
  const [q,setQ]=useState(''),[filterStatus,setFilterStatus]=useState('');
  const [form,setForm]=useState(null),[saving,setSaving]=useState(false);

  function load(){Promise.all([api('/coo/order-closing'),api('/orders')]).then(([c,o])=>{setList(c);setOrders(o)}).catch(e=>setErr(e.message))}
  useEffect(load,[]);

  function filtered(){
    return list.filter(c=>{
      if(filterStatus&&c.order_close_status!==filterStatus) return false;
      if(!q) return true;
      const s=q.toLowerCase();
      const orderId=orderLabel(c.order_fk).toLowerCase();
      return orderId.includes(s)||(c.buyer||'').toLowerCase().includes(s)||(c.notes||'').toLowerCase().includes(s);
    });
  }

  async function save(ev){
    ev.preventDefault(); setSaving(true);
    try{
      const payload={
        customer_close_status:form.customer_close_status,
        financial_close_status:form.financial_close_status,
        order_close_status:form.customer_close_status==='CLOSED'&&form.financial_close_status==='CLOSED'?'CLOSED':'OPEN',
        notes:form.notes||'',
        closed_by:form.closed_by||''
      };
      await api('/coo/order-closing/'+form.id,{method:'PATCH',body:JSON.stringify(payload)});
      setForm(null); load();
    }catch(x){alert(x.message)}
    setSaving(false);
  }

  const f2=filtered();
  function orderLabel(id){const o=orders.find(o=>o.id===id);return o?o.order_id:'-'}
  function buyerLabel(id){const o=orders.find(o=>o.id===id);return o?o.buyer:'-'}

  const totalCount=list.length;
  const openCount=list.filter(c=>c.order_close_status==='OPEN').length;
  const closedCount=list.filter(c=>c.order_close_status==='CLOSED').length;

  return <div className="page">
    <div className="page-title"><div><h1><DollarSign size={22}/> Order Closing</h1><p>{totalCount} total order</p></div></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="cards">
      <div className="stat blue"><strong>{totalCount}</strong><span>Total Order</span></div>
      <div className="stat amber"><strong>{openCount}</strong><span>OPEN</span></div>
      <div className="stat green"><strong>{closedCount}</strong><span>CLOSED</span></div>
    </div>
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder="Cari order_id, buyer, notes..." value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">{statusOpts.map(s=><button key={s} className={'pill '+(filterStatus===s?'active '+s.toLowerCase():'')} onClick={()=>setFilterStatus(filterStatus===s?'':s)}>{s}</button>)}</div>
    </div>
    <div className="table-scroll"><table><thead><tr><th>Order</th><th>Buyer</th><th>Customer Close</th><th>Financial Close</th><th>Order Close</th><th>Notes</th><th>Aksi</th></tr></thead>
    <tbody>{f2.map(c=><tr key={c.id}>
      <td><b>{orderLabel(c.order_fk)}</b></td>
      <td>{buyerLabel(c.order_fk)}</td>
      <td><span className={'badge '+(c.customer_close_status==='CLOSED'?'green':'gray')}>{c.customer_close_status||'OPEN'}</span></td>
      <td><span className={'badge '+(c.financial_close_status==='CLOSED'?'green':'gray')}>{c.financial_close_status||'OPEN'}</span></td>
      <td><span className={'badge '+(c.order_close_status==='CLOSED'?'green':'gray')}>{c.order_close_status||'OPEN'}</span></td>
      <td className="td-ellipsis">{c.notes||'-'}</td>
      <td className="td-action">
        <button className="icon-btn" onClick={()=>setForm({...c,notes:c.notes||'',closed_by:c.closed_by||''})} title="Edit"><Edit2 size={15}/></button>
      </td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={7} className="empty">Tidak ada order closing data</td></tr>}</tbody></table></div>
    {form&&<div className="modal-bg" onClick={()=>setForm(null)}>
    <div className="modal" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2>Edit Order Closing — {orderLabel(form.order_fk)}</h2><button className="icon-btn" onClick={()=>setForm(null)}><X size={18}/></button></div>
      <form onSubmit={save}>
        <div className="form-grid">
          <label>Customer Close Status<select value={form.customer_close_status||'OPEN'} onChange={e=>setForm({...form,customer_close_status:e.target.value})}>
            <option>OPEN</option><option>CLOSED</option>
          </select></label>
          <label>Financial Close Status<select value={form.financial_close_status||'OPEN'} onChange={e=>setForm({...form,financial_close_status:e.target.value})}>
            <option>OPEN</option><option>CLOSED</option>
          </select></label>
        </div>
        <div className="form-grid">
          <label>Order Close Status (auto)
            <input disabled value={form.customer_close_status==='CLOSED'&&form.financial_close_status==='CLOSED'?'CLOSED':'OPEN'} style={{backgroundColor:'#f5f5f5'}}/>
          </label>
          <label>Closed By<input value={form.closed_by||''} onChange={e=>setForm({...form,closed_by:e.target.value})} placeholder="Nama yang menutup order"/></label>
        </div>
        <label>Notes<textarea rows={3} value={form.notes||''} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Catatan penutupan order..."/></label>
        <div className="modal-foot"><button type="button" className="btn" onClick={()=>setForm(null)}>Batal</button><button className="btn primary" disabled={saving}><Check size={14}/> {saving?'Menyimpan...':'Simpan'}</button></div>
      </form>
    </div></div>}
  </div>
}
