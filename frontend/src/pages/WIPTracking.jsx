import React,{useEffect,useState} from 'react';
import {api} from '../api';
import {Package,RefreshCw,AlertTriangle,Search} from 'lucide-react';

export default function WIPTracking(){
  const [wip,setWip]=useState([]),[capacity,setCap]=useState([]);
  const [orders,setOrders]=useState([]);
  const [movements,setMovements]=useState([]);
  const [err,setErr]=useState('');
  const [loading,setLoading]=useState(true);
  const [q,setQ]=useState('');
  const [viewMode,setViewMode]=useState('process'); // 'process' or 'order'

  function load(){
    setLoading(true);
    Promise.all([api('/coo/wip-summary'),api('/master/wip-capacity'),api('/orders'),api('/coo/movements')]).then(([w,c,o,m])=>{setWip(w);setCap(c);setOrders(o);setMovements(m)}).catch(e=>setErr(e.message)).finally(()=>setLoading(false));
  }
  useEffect(load,[]);

  const capMap={};capacity.forEach(c=>{capMap[c.process]=c});

  // Total WIP count across all processes
  const totalWIP=wip.reduce((sum,w)=>sum+(w.wip||0),0);

  // Per-order WIP breakdown
  function getOrderWIP(){
    const orderMap={};
    orders.forEach(o=>{
      orderMap[o.id]={order_id:o.order_id,buyer:o.buyer,articles:o.articles||[]};
    });

    const orderWIP=[];
    movements.forEach(m=>{
      const article=(orderMap[m.order_fk]||{}).articles||[];
      // Find order for this movement through articles
      let orderInfo=null;
      for(const oid in orderMap){
        const ord=orderMap[oid];
        if(ord.articles.find(a=>a.id===m.article_id)){
          orderInfo={order_id:ord.order_id,buyer:ord.buyer,order_id_fk:parseInt(oid)};
          break;
        }
      }
      if(!orderInfo){
        // Try direct order_fk
        const ord=orderMap[m.order_fk];
        if(ord) orderInfo={order_id:ord.order_id,buyer:ord.buyer,order_id_fk:m.order_fk};
      }
      if(!orderInfo) return;

      const existing=orderWIP.find(o=>o.order_id===orderInfo.order_id);
      const wipQty=m.qty_in-m.qty_done-m.qty_reject;
      if(existing){
        if(!existing.processes.find(p=>p.process===m.process)){
          existing.processes.push({process:m.process,wip:wipQty,status:m.status});
        }
        existing.totalWIP+=wipQty;
      }else{
        orderWIP.push({
          order_id:orderInfo.order_id,
          buyer:orderInfo.buyer,
          totalWIP:wipQty,
          processes:[{process:m.process,wip:wipQty,status:m.status}]
        });
      }
    });
    return orderWIP;
  }

  const orderWIPData=getOrderWIP();

  function filteredProcess(){
    if(!q) return wip;
    const s=q.toLowerCase();
    return wip.filter(w=>w.process.toLowerCase().includes(s));
  }

  function filteredOrder(){
    if(!q) return orderWIPData;
    const s=q.toLowerCase();
    return orderWIPData.filter(o=>(o.order_id||'').toLowerCase().includes(s)||(o.buyer||'').toLowerCase().includes(s));
  }

  return <div className="page">
    <div className="page-title"><div><h1><Package size={22}/> WIP Tracking</h1><p>Work-in-progress per proses produksi</p></div>
      <button className="btn" onClick={load}><RefreshCw size={14}/> Refresh</button></div>
    {err&&<div className="notice danger">{err}</div>}
    {loading?<div className="page">Memuat...</div>:<>

    {/* Total WIP card */}
    <div className="cards">
      <div className="stat blue"><strong>{totalWIP}</strong><span>Total WIP</span></div>
      {wip.map((w,i)=><div key={i} className={'stat '+(w.wip>0?'amber':'gray')}><strong>{w.wip}</strong><span>{w.process}</span></div>)}
    </div>

    {/* Utilization alert */}
    {wip.some(w=>{
      const c=capMap[w.process]||{};
      return c.capacity&&(c.planned_load/c.capacity)>1;
    })&&<div className="notice danger" style={{display:'flex',alignItems:'center',gap:'8px',marginBottom:'1rem'}}><AlertTriangle size={16}/> Beberapa proses melebihi 100% kapasitas!</div>}

    {/* View mode toggle + search */}
    <div className="filter-bar">
      <div className="search-bar"><Search size={16}/><input placeholder={viewMode==='process'?"Cari proses...":"Cari order, buyer..."} value={q} onChange={e=>setQ(e.target.value)}/></div>
      <div className="filter-pills">
        <button className={'pill '+(viewMode==='process'?'active blue':'')} onClick={()=>{setViewMode('process');setQ('')}}>Per Proses</button>
        <button className={'pill '+(viewMode==='order'?'active blue':'')} onClick={()=>{setViewMode('order');setQ('')}}>Per Order</button>
      </div>
    </div>

    {/* Per-process view */}
    {viewMode==='process'&&<div className="table-scroll"><table><thead><tr><th>Proses</th><th>Qty In (total)</th><th>Qty Done</th><th>Reject</th><th>WIP (current)</th><th>Capacity</th><th>Planned Load</th><th>Utilization</th></tr></thead>
    <tbody>{filteredProcess().map((w,i)=>{
      const c=capMap[w.process]||{};
      const util=c.capacity?Math.round((c.planned_load/c.capacity)*100):'-';
      const isOver=typeof util==='number'&&util>100;
      return <tr key={i} style={isOver?{backgroundColor:'#fef2f2'}:{}}>
        <td><b>{w.process}</b></td><td>{w.qty_in}</td><td>{w.qty_done}</td><td>{w.qty_reject}</td>
        <td><b>{w.wip}</b></td>
        <td>{c.capacity||'-'}</td><td>{c.planned_load||'-'}</td>
        <td><span className={isOver?'badge red':typeof util==='number'&&util>80?'badge amber':'badge green'}>{util}%</span></td>
      </tr>
    })}
    {filteredProcess().length===0&&<tr><td colSpan={8} className="empty">Belum ada data WIP</td></tr>}</tbody></table></div>}

    {/* Per-order view */}
    {viewMode==='order'&&<div className="table-scroll"><table><thead><tr><th>Order</th><th>Buyer</th><th>Total WIP</th><th>Proses Stages</th></tr></thead>
    <tbody>{filteredOrder().map((o,i)=><tr key={i}>
      <td><b>{o.order_id}</b></td>
      <td>{o.buyer||'-'}</td>
      <td><b>{o.totalWIP}</b></td>
      <td>{o.processes.map((p,j)=><span key={j} className={'badge '+(p.status==='DONE'?'green':p.status==='IN_PROCESS'?'amber':'gray')} style={{marginRight:'4px'}}>{p.process} ({p.wip})</span>)}</td>
    </tr>)}
    {filteredOrder().length===0&&<tr><td colSpan={4} className="empty">Tidak ada data WIP per order</td></tr>}</tbody></table></div>}

    </>}
  </div>
}
