import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {useRole} from '../components/Access';
import FormModal from '../components/FormModal';
import {matchesSearch,statusTone} from '../business';

const money=n=>'Rp '+Number(n||0).toLocaleString('id-ID');
const blank={quotation_no:'',order_fk:'',status:'DRAFT',valid_until:'',notes:'',payment_plan:'',pricing_lines:[]};
function rowsFor(order,quote){
 let existing=[];
 try{existing=JSON.parse(quote?.pricing_breakdown||'[]')}catch{}
 return (order?.articles||[]).map(a=>({article_id:a.id,article_code:a.article_code,qty:a.qty,
   unit_price:existing.find(x=>x.article_id===a.id)?.unit_price||'',
   unit_hpp:existing.find(x=>x.article_id===a.id)?.unit_hpp||''}));
}

export default function QuotationPage(){
 const role=useRole(),isCMO=['CMO_MANAGER','CMO_SUPPORT'].includes(role),manager=role==='CMO_MANAGER',isCFO=role==='CFO_MANAGER',isCEO=role==='CEO';
 const [list,setList]=useState([]),[orders,setOrders]=useState([]),[policy,setPolicy]=useState(null),[form,setForm]=useState(null),[decision,setDecision]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[query,setQuery]=useState('');
 async function load(){try{const [quotes,allOrders]=await Promise.all([api('/cmo/quotations'),api('/orders')]);setList(quotes);setOrders(allOrders);setError('');if(['CEO','CFO_MANAGER','CMO_MANAGER'].includes(role)){try{setPolicy(await api('/config/business-policy'))}catch{setPolicy(null)}}}catch(e){setError(e.message)}}
 useEffect(()=>{load()},[role]);
 function openQuote(q){const order=orders.find(o=>o.id===q.order_fk);setError('');setForm({...blank,...q,pricing_lines:rowsFor(order,q)});}
 function selectOrder(id){const order=orders.find(o=>o.id===Number(id));setForm(f=>({...f,order_fk:id,pricing_lines:rowsFor(order)}));}
 function updateLine(index,key,value){setForm(f=>({...f,pricing_lines:f.pricing_lines.map((line,i)=>i===index?{...line,[key]:value}:line)}));}
 async function save(e){e.preventDefault();setBusy(true);setError('');try{
   if(isCFO){await api(`/cmo/quotations/${form.id}`,{method:'PATCH',body:JSON.stringify({status:form.status,approval_reason:form.approval_reason})})}
   else {const payload={status:form.status,valid_until:form.valid_until,notes:form.notes,payment_plan:form.payment_plan,
     pricing_lines:form.pricing_lines.map(({article_id,unit_price,unit_hpp})=>({article_id,unit_price:Number(unit_price),unit_hpp:Number(unit_hpp)}))};
     if(!form.id)Object.assign(payload,{quotation_no:form.quotation_no,order_fk:Number(form.order_fk)});
     await api('/cmo/quotations'+(form.id?'/'+form.id:''),{method:form.id?'PATCH':'POST',body:JSON.stringify(payload)})}
   setForm(null);await load();
 }catch(x){setError(x.message)}finally{setBusy(false)}}
 async function approveLimit(e){e.preventDefault();setBusy(true);setError('');try{await api(`/ceo/quotations/${decision.id}/approve-limit`,{method:'POST',body:JSON.stringify({reason:decision.reason})});setDecision(null);await load()}catch(x){setError(x.message)}finally{setBusy(false)}}
 async function remove(id){if(!confirm('Hapus quotation ini?'))return;try{await api(`/cmo/quotations/${id}`,{method:'DELETE'});await load()}catch(e){setError(e.message)}}
 const selected=orders.find(o=>o.id===Number(form?.order_fk));
 const total=form?.pricing_lines.reduce((n,line)=>n+line.qty*Number(line.unit_price||0),0)||0;
 const hpp=form?.pricing_lines.reduce((n,line)=>n+line.qty*Number(line.unit_hpp||0),0)||0;
 return <div className="page"><div className="page-title"><div><h1>Pricing & Quotation</h1><p>Harga, HPP dan margin dihitung per artikel sebelum approval.</p></div>{isCMO&&<button className="btn primary" onClick={()=>openQuote(blank)}>Tambah Quotation</button>}</div>
 {error&&!form&&!decision&&<div className="notice danger" role="alert">{error}</div>}{!policy&&['CEO','CFO_MANAGER','CMO_MANAGER'].includes(role)&&<div className="notice danger">Kebijakan pricing dan DP belum diatur CEO; approval akan tertahan.</div>}
 <input aria-label="Cari quotation" placeholder="Cari nomor quotation" value={query} onChange={e=>setQuery(e.target.value)}/>
 <div className="table-scroll"><table><thead><tr><th>Quotation / Order</th><th>Penjualan</th><th>HPP</th><th>Margin</th><th>Payment Plan</th><th>Status</th><th>Aksi</th></tr></thead><tbody>{list.filter(q=>matchesSearch(q,query,['quotation_no','notes'])).map(q=><tr key={q.id}><td>{q.quotation_no}<br/>{orders.find(o=>o.id===q.order_fk)?.order_id||'—'}</td><td>{money(q.amount)}</td><td>{money(q.hpp_total)}</td><td>{Number(q.margin_percent||0)}%</td><td>{q.payment_plan||'—'}</td><td><span className={'badge '+statusTone(q.status)}>{q.status}</span>{q.ceo_approved_by_id&&<small> · CEO reviewed</small>}</td><td>{manager&&q.status!=='APPROVED'&&<button className="btn" onClick={()=>openQuote(q)}>Edit</button>}{isCFO&&q.status!=='APPROVED'&&<button className="btn" onClick={()=>openQuote(q)}>Review CFO</button>}{isCEO&&policy&&Number(q.amount)>Number(policy.cfo_quotation_limit)&&!q.ceo_approved_by_id&&<button className="btn" onClick={()=>setDecision({id:q.id,reason:''})}>Approve Limit</button>}{manager&&q.status!=='APPROVED'&&<button className="btn" onClick={()=>remove(q.id)}>Hapus</button>}</td></tr>)}{!list.length&&<tr><td colSpan={7}>Belum ada quotation.</td></tr>}</tbody></table></div>
 {form&&<FormModal title={isCFO?'Review CFO':form.id?'Edit Quotation':'Quotation Baru'} onClose={()=>setForm(null)} onSubmit={save} busy={busy} error={error}>{isCFO?<><p>Penjualan {money(form.amount)} · HPP {money(form.hpp_total)} · Margin {Number(form.margin_percent||0)}%</p><label>Keputusan<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}><option value="DRAFT">DRAFT</option><option value="APPROVED">APPROVED</option><option value="REJECTED">REJECTED</option></select></label><label>Alasan CFO<textarea required value={form.approval_reason||''} onChange={e=>setForm({...form,approval_reason:e.target.value})}/></label></>:<><label>Nomor Quotation<input required disabled={Boolean(form.id)} value={form.quotation_no} onChange={e=>setForm({...form,quotation_no:e.target.value})}/></label><label>Order<select required disabled={Boolean(form.id)} value={form.order_fk} onChange={e=>selectOrder(e.target.value)}><option value="">Pilih order</option>{orders.map(o=><option key={o.id} value={o.id}>{o.order_id} — {o.buyer}</option>)}</select></label>{selected&&<section className="panel"><h2>Harga dan HPP per artikel</h2>{form.pricing_lines.map((line,i)=><div className="form-grid" key={line.article_id}><span>{line.article_code} · {line.qty} pcs</span><label>Harga/unit<input type="number" min="0.01" step="0.01" required value={line.unit_price} onChange={e=>updateLine(i,'unit_price',e.target.value)}/></label><label>HPP/unit<input type="number" min="0" step="0.01" required value={line.unit_hpp} onChange={e=>updateLine(i,'unit_hpp',e.target.value)}/></label></div>)}<p>Penjualan {money(total)} · HPP {money(hpp)} · Margin {total?((total-hpp)/total*100).toFixed(2):'0'}%</p></section>}<label>Payment Plan<textarea required value={form.payment_plan||''} onChange={e=>setForm({...form,payment_plan:e.target.value})}/></label><label>Berlaku Sampai<input type="date" value={form.valid_until||''} onChange={e=>setForm({...form,valid_until:e.target.value})}/></label><label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}><option>DRAFT</option><option>SENT</option></select></label><label>Catatan<textarea value={form.notes||''} onChange={e=>setForm({...form,notes:e.target.value})}/></label></>}</FormModal>}
 {decision&&<FormModal title="Persetujuan CEO di atas limit" onClose={()=>setDecision(null)} onSubmit={approveLimit} busy={busy} error={error}><label>Alasan keputusan<textarea required value={decision.reason} onChange={e=>setDecision({...decision,reason:e.target.value})}/></label></FormModal>}</div>;
}
