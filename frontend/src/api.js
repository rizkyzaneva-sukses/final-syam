import {normalizeDates} from './business.js';
const API='/api';
// Access tokens live in sessionStorage, not localStorage: the token dies with the
// tab instead of persisting on disk for every future visitor of that browser
// profile, which shrinks the blast radius of an XSS or a shared machine.
const TOKEN_KEY='bos_token';
export function getToken(){return sessionStorage.getItem(TOKEN_KEY)}
export function setToken(v){sessionStorage.setItem(TOKEN_KEY,v)}
export function clearToken(){sessionStorage.removeItem(TOKEN_KEY);try{localStorage.removeItem(TOKEN_KEY)}catch{}}
// One-time migration for sessions issued before the switch, so users are not
// logged out mid-session by the upgrade.
try{const legacy=localStorage.getItem(TOKEN_KEY);if(legacy&&!sessionStorage.getItem(TOKEN_KEY)){sessionStorage.setItem(TOKEN_KEY,legacy)}if(legacy){localStorage.removeItem(TOKEN_KEY)}}catch{}
const readonlyKeys=new Set(['id','created_at','updated_at','customer_approved_by_id','version','snapshot','total_score','invoice_id','finance_assessed_by_id','approved_outstanding','closed_by']);
const patchOnlyFields=[
  ['/ceo/decisions/', ['order_fk']], ['/cmo/delivery-confirmations/', ['shipment_fk']], ['/chro/issues/', ['employee_id']],
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
  const {responseType,...requestOptions}=opts;
  const headers={...(opts.headers||{})};
  if(!(opts.body instanceof FormData) && !headers['Content-Type']) headers['Content-Type']='application/json';
  const token=getToken(); if(token) headers.Authorization=`Bearer ${token}`;
  let body=opts.body;if(typeof body==='string'&&headers['Content-Type']==='application/json'){try{body=JSON.stringify(requestPayload(path,opts.method||'GET',JSON.parse(body)))}catch{}}
  const res=await fetch(API+path,{...requestOptions,body,headers});
  if(res.status===401){clearToken(); location.href='/login'; throw new Error('Unauthorized')}
  if(!res.ok){let msg='Request gagal'; try{msg=(await res.json()).detail||msg}catch{}; throw new Error(msg)}
  if(res.status===204) return null;
  return responseType==='blob'?res.blob():res.json();
}
