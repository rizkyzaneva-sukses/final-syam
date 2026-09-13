import React,{useEffect,useState} from 'react';
import {api} from '../api';

const empty={minimum_margin_percent:'',minimum_dp_percent:'',cfo_quotation_limit:'',allow_credit_terms:false};
export default function BusinessPolicyPage(){
 const [policy,setPolicy]=useState(empty),[error,setError]=useState(''),[saved,setSaved]=useState(false),[busy,setBusy]=useState(false);
 useEffect(()=>{api('/config/business-policy').then(setPolicy).catch(()=>{})},[]);
 async function save(e){e.preventDefault();setBusy(true);setError('');setSaved(false);try{
   await api('/config/business-policy',{method:'PUT',body:JSON.stringify({minimum_margin_percent:Number(policy.minimum_margin_percent),minimum_dp_percent:Number(policy.minimum_dp_percent),cfo_quotation_limit:Number(policy.cfo_quotation_limit),allow_credit_terms:policy.allow_credit_terms})});
   setSaved(true);
 }catch(x){setError(x.message)}finally{setBusy(false)}}
 return <div className="page"><div className="page-title"><div><h1>Kebijakan Pricing & Payment</h1><p>CEO menetapkan batas yang berlaku untuk approval quotation dan Finance Gate G1.</p></div></div>
 {error&&<div className="notice danger" role="alert">{error}</div>}{saved&&<div className="notice info">Kebijakan tersimpan dan diaudit.</div>}
 <form className="panel" onSubmit={save}><div className="form-grid"><label>Margin minimum (%)<input type="number" min="0" max="100" step="0.01" required value={policy.minimum_margin_percent} onChange={e=>setPolicy({...policy,minimum_margin_percent:e.target.value})}/></label><label>DP minimum (%)<input type="number" min="0" max="100" step="0.01" required value={policy.minimum_dp_percent} onChange={e=>setPolicy({...policy,minimum_dp_percent:e.target.value})}/></label><label>Limit approval CFO (Rp)<input type="number" min="0.01" step="0.01" required value={policy.cfo_quotation_limit} onChange={e=>setPolicy({...policy,cfo_quotation_limit:e.target.value})}/></label></div><label><input type="checkbox" checked={Boolean(policy.allow_credit_terms)} onChange={e=>setPolicy({...policy,allow_credit_terms:e.target.checked})}/> Izinkan terms kredit dengan tanggal jatuh tempo dan bukti kontrak</label><div className="modal-foot"><button className="btn primary" disabled={busy}>{busy?'Menyimpan...':'Simpan Kebijakan'}</button></div></form></div>;
}
