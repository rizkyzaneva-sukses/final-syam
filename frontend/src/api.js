import {normalizeDates} from './business.js';
const API='/api';
export function getToken(){return localStorage.getItem('bos_token')}
export function setToken(v){localStorage.setItem('bos_token',v)}
export function clearToken(){localStorage.removeItem('bos_token')}
const readonlyKeys=new Set(['id','created_at','updated_at','customer_approved_by_id','version','snapshot','total_score','invoice_id','finance_assessed_by_id','approved_outstanding','closed_by']);
const patchOnlyFields=[
  ['/ceo/decisions/', ['order_fk']], ['/coo/deliveries/', ['shipment_fk']], ['/chro/issues/', ['employee_id']],
  ['/exceptions/', ['order_fk']], ['/coo/material-requests/', ['order_fk']], ['/coo/movements/', ['article_id','process']],
  ['/cfo/purchase-orders/', ['po_no','order_fk']], ['/coo/qc-records/', ['order_fk','article_code','process']],
  ['/cmo/quotations/', ['quotation_no','order_fk']], ['/cmo/samples/', ['order_fk','article_code','requested_date']],
  ['/cmo/spk/', ['order_fk','spk_no']], ['/chro/trainings/', ['employee_id']],
];
export function requestPayload(path, method, value){
  if(!value||typeof value!=='object'||Array.isArray(value)) return value;
  const clean=Object.fromEntries(Object.entries(value).filter(([key])=>!readonlyKeys.has(key)));
  if(method.toUpperCase()==='PATCH'){
    for(const [prefix,fields] of patchOnlyFields) if(path.startsWith(prefix)) for(const field of fields) delete clean[field];
  }
  return normalizeDates(clean);
}
export async function api(path, opts={}){
  const headers={...(opts.headers||{}),'Content-Type':'application/json'};
  const token=getToken(); if(token) headers.Authorization=`Bearer ${token}`;
  let body=opts.body;if(typeof body==='string'&&headers['Content-Type']==='application/json'){try{body=JSON.stringify(requestPayload(path,opts.method||'GET',JSON.parse(body)))}catch{}}
  const res=await fetch(API+path,{...opts,body,headers});
  if(res.status===401){clearToken(); location.href='/login'; throw new Error('Unauthorized')}
  if(!res.ok){let msg='Request gagal'; try{msg=(await res.json()).detail||msg}catch{}; throw new Error(msg)}
  if(res.status===204) return null;
  return res.json();
}
