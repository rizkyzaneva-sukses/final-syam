const API='/api';
export function getToken(){return localStorage.getItem('bos_token')}
export function setToken(v){localStorage.setItem('bos_token',v)}
export function clearToken(){localStorage.removeItem('bos_token')}
export async function api(path, opts={}){
  const headers={...(opts.headers||{}),'Content-Type':'application/json'};
  const token=getToken(); if(token) headers.Authorization=`Bearer ${token}`;
  const res=await fetch(API+path,{...opts,headers});
  if(res.status===401){clearToken(); location.href='/login'; throw new Error('Unauthorized')}
  if(!res.ok){let msg='Request gagal'; try{msg=(await res.json()).detail||msg}catch{}; throw new Error(msg)}
  return res.json();
}
