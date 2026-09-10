import React,{useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {api,setToken} from '../api';
export default function Login(){const [email,setEmail]=useState('iyan@syams.local'),[password,setPassword]=useState('demo123'),[err,setErr]=useState(''); const nav=useNavigate();
 async function submit(e){e.preventDefault();setErr('');try{const r=await api('/auth/login',{method:'POST',body:JSON.stringify({email,password})});setToken(r.access_token);nav('/master')}catch(x){setErr(x.message)}}
 return <div className="login-wrap"><div className="login-card"><div className="brand big"><b>BOS SYAMS</b><span>Business Operating System</span></div><h1>Masuk</h1><p>Satu aplikasi, akses sesuai peran.</p><form onSubmit={submit}><label>Email<input value={email} onChange={e=>setEmail(e.target.value)}/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label>{err&&<div className="error">{err}</div>}<button className="primary">Masuk</button></form><small>Demo: iyan@syams.local / demo123</small></div></div>}
