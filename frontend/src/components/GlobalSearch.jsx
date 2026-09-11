import React,{useEffect,useState,useRef} from 'react';
import {useNavigate} from 'react-router-dom';
import {api} from '../api';
import {Search,ExternalLink} from 'lucide-react';

export default function GlobalSearch(){
  const [q,setQ]=useState('');
  const [results,setResults]=useState(null);
  const [loading,setLoading]=useState(false);
  const nav=useNavigate();
  const debounceRef=useRef(null);

  useEffect(()=>{
    if(debounceRef.current) clearTimeout(debounceRef.current);
    if(!q.trim()){setResults(null);return}
    debounceRef.current=setTimeout(()=>{
      setLoading(true);
      Promise.all([
        api('/orders'),
        api('/cmo/customers'),
        api('/exceptions'),
        api('/tasks'),
      ]).then(([orders,customers,exceptions,tasks])=>{
        const s=q.toLowerCase();
        const matchedOrders=orders.filter(o=>o.order_id.toLowerCase().includes(s)||o.buyer.toLowerCase().includes(s)||(o.articles||[]).some(a=>a.article_code.toLowerCase().includes(s)));
        const matchedCustomers=customers.filter(c=>c.name.toLowerCase().includes(s)||(c.country||'').toLowerCase().includes(s));
        const matchedExceptions=exceptions.filter(e=>e.title.toLowerCase().includes(s)||e.category.toLowerCase().includes(s));
        const matchedTasks=tasks.filter(t=>t.title.toLowerCase().includes(s));
        setResults({orders:matchedOrders,customers:matchedCustomers,exceptions:matchedExceptions,tasks:matchedTasks});
      }).catch(()=>setResults(null)).finally(()=>setLoading(false));
    },300);
  },[q]);

  function go(path){nav(path);setQ('');setResults(null)}

  const total=results?(results.orders.length+results.customers.length+results.exceptions.length+results.tasks.length):0;

  return <div className="global-search-wrap" style={{position:'relative',flex:1,maxWidth:'500px'}}>
    <div className="search" style={{display:'flex',alignItems:'center',gap:'8px'}}>
      <Search size={16} color="#94a3b8"/>
      <input style={{border:'none',outline:'none',background:'transparent',flex:1,fontSize:'14px',color:'#374151'}} placeholder="Cari Order ID, Buyer, Article, Exception, Task..." value={q} onChange={e=>setQ(e.target.value)} onFocus={()=>q&&setResults(results)}/>
    </div>
    {results&&<div style={{position:'absolute',top:'100%',left:0,right:0,background:'white',border:'1px solid #e5eaf1',borderRadius:'12px',boxShadow:'0 12px 40px rgba(0,0,0,.15)',maxHeight:'420px',overflow:'auto',zIndex:100,marginTop:'4px'}}>
      {loading?<div style={{padding:'16px',textAlign:'center',color:'#94a3b8'}}>Mencari...</div>:
      total===0?<div style={{padding:'16px',textAlign:'center',color:'#94a3b8'}}>Tidak ditemukan</div>:
      <div style={{padding:'8px'}}>
        {results.orders.length>0&&<div><div style={{padding:'6px 12px',fontSize:'11px',fontWeight:700,color:'#64748b',textTransform:'uppercase'}}>Orders ({results.orders.length})</div>
        {results.orders.map(o=><div key={o.id} onClick={()=>go('/orders/'+o.order_id)} style={{display:'flex',alignItems:'center',gap:'10px',padding:'8px 12px',cursor:'pointer',borderRadius:'8px'}} onMouseOver={e=>e.currentTarget.style.background='#f8fafc'} onMouseOut={e=>e.currentTarget.style.background='transparent'}>
          <ExternalLink size={14} color="#94a3b8"/><div><b style={{fontSize:'13px'}}>{o.order_id}</b><span style={{fontSize:'12px',color:'#64748b',marginLeft:'8px'}}>{o.buyer}</span></div></div>)}
        </div>}
        {results.customers.length>0&&<div><div style={{padding:'6px 12px',fontSize:'11px',fontWeight:700,color:'#64748b',textTransform:'uppercase'}}>Customers ({results.customers.length})</div>
        {results.customers.map(c=><div key={c.id} onClick={()=>go('/cmo/customers')} style={{display:'flex',alignItems:'center',gap:'10px',padding:'8px 12px',cursor:'pointer',borderRadius:'8px'}} onMouseOver={e=>e.currentTarget.style.background='#f8fafc'} onMouseOut={e=>e.currentTarget.style.background='transparent'}>
          <ExternalLink size={14} color="#94a3b8"/><div><b style={{fontSize:'13px'}}>{c.name}</b><span style={{fontSize:'12px',color:'#64748b',marginLeft:'8px'}}>{c.country||''}</span></div></div>)}
        </div>}
        {results.exceptions.length>0&&<div><div style={{padding:'6px 12px',fontSize:'11px',fontWeight:700,color:'#64748b',textTransform:'uppercase'}}>Exceptions ({results.exceptions.length})</div>
        {results.exceptions.map(e=><div key={e.id} onClick={()=>go('/exceptions')} style={{display:'flex',alignItems:'center',gap:'10px',padding:'8px 12px',cursor:'pointer',borderRadius:'8px'}} onMouseOver={e=>e.currentTarget.style.background='#f8fafc'} onMouseOut={e=>e.currentTarget.style.background='transparent'}>
          <span className={'badge '+e.severity.toLowerCase()} style={{fontSize:'10px'}}>{e.severity}</span><div><b style={{fontSize:'13px'}}>{e.title}</b></div></div>)}
        </div>}
        {results.tasks.length>0&&<div><div style={{padding:'6px 12px',fontSize:'11px',fontWeight:700,color:'#64748b',textTransform:'uppercase'}}>Tasks ({results.tasks.length})</div>
        {results.tasks.map(t=><div key={t.id} onClick={()=>go('/tasks')} style={{display:'flex',alignItems:'center',gap:'10px',padding:'8px 12px',cursor:'pointer',borderRadius:'8px'}} onMouseOver={e=>e.currentTarget.style.background='#f8fafc'} onMouseOut={e=>e.currentTarget.style.background='transparent'}>
          <ExternalLink size={14} color="#94a3b8"/><div><b style={{fontSize:'13px'}}>{t.title}</b></div></div>)}
        </div>}
      </div>}
    </div>}
  </div>
}
