import React,{useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api';
import {Plus,Search,ExternalLink} from 'lucide-react';

const statusCls=v=>(v||'').includes('PAID')||v==='READY'||v==='ACTIVE'||v==='NEW'?'green':(v||'').includes('PARTIAL')?'amber':v==='DELAYED'||v==='HOLD'?'red':'gray';

export default function OrderList(){
  const [orders,setOrders]=useState([]),[err,setErr]=useState('');
  const [q,setQ]=useState('');
  useEffect(()=>{api('/orders').then(setOrders).catch(e=>setErr(e.message))},[]);

  function filtered(){
    return orders.filter(o=>{
      if(!q) return true;
      const s=q.toLowerCase();
      return o.order_id.toLowerCase().includes(s)||o.buyer.toLowerCase().includes(s)||(o.articles||[]).some(a=>a.article_code.toLowerCase().includes(s));
    });
  }
  const f2=filtered();
  return <div className="page">
    <div className="page-title"><div><h1>Order Management</h1><p>{orders.length} order tercatat</p></div>
      <Link to="/cmo/orders/new" className="btn primary"><Plus size={16}/> Order Baru</Link></div>
    {err&&<div className="notice danger">{err}</div>}
    <div className="search-bar"><Search size={16}/><input placeholder="Cari Order ID, Buyer, Article..." value={q} onChange={e=>setQ(e.target.value)}/></div>
    <div className="table-scroll"><table><thead><tr><th>Order ID</th><th>Buyer</th><th>Tipe</th><th>Articles</th><th>Total Qty</th><th>Deadline</th><th>Finance</th><th>Material</th><th>Status</th><th></th></tr></thead>
    <tbody>{f2.map(o=><tr key={o.id}>
      <td><Link to={'/orders/'+o.order_id}><b>{o.order_id}</b></Link></td>
      <td>{o.buyer}</td>
      <td><span className="badge gray">{o.order_type?.replaceAll('_',' ')}</span></td>
      <td>{o.articles?.map(a=>a.article_code).join(', ')||'-'}</td>
      <td>{o.articles?.reduce((s,a)=>s+a.qty,0)||0}</td>
      <td>{o.buyer_deadline||'-'}</td>
      <td><span className={'badge '+statusCls(o.finance_status)}>{o.finance_status}</span></td>
      <td><span className={'badge '+statusCls(o.material_status)}>{o.material_status}</span></td>
      <td><span className={'badge '+statusCls(o.overall_status)}>{o.overall_status}</span></td>
      <td><Link to={'/orders/'+o.order_id} className="icon-btn" title="Detail"><ExternalLink size={15}/></Link></td>
    </tr>)}
    {f2.length===0&&<tr><td colSpan={10} className="empty">Tidak ada order ditemukan</td></tr>}</tbody></table></div>
  </div>
}
