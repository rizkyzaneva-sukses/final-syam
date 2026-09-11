import React,{useEffect,useState} from 'react';
import {api} from '../api';

export default function ProductionPlanPage(){
  const [plans,setPlans]=useState([]);
  useEffect(()=>{api('/coo/production-plans').then(setPlans).catch(()=>{})},[]);
  return <div><h2>Production Plan</h2><div className="table-wrap"><table><thead><tr><th>Plan ID</th><th>Order</th><th>Target Qty</th><th>Start Date</th><th>End Date</th><th>Status</th></tr></thead><tbody>{plans.map(p=><tr key={p.id}><td>{p.plan_no}</td><td>{p.order_id}</td><td>{p.target_qty}</td><td>{p.start_date}</td><td>{p.end_date}</td><td><span className={'badge badge-'+(p.status==='IN_PROGRESS'?'warn':'info')}>{p.status}</span></td></tr>)}{plans.length===0&&<tr><td colSpan={6} style={{textAlign:'center'}}>No production plans yet</td></tr>}</tbody></table></div></div>;
}
