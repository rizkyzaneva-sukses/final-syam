import React,{useEffect,useState} from 'react';
import {Outlet,NavLink,useNavigate} from 'react-router-dom';
import {Home,Database,Package,ShoppingCart,DollarSign,Factory,Users,Crown,ClipboardList,AlertTriangle,LogOut,Menu,X} from 'lucide-react';
import {api,clearToken} from '../api';

const roleMenus={
  CEO:[['Master Control','/master',Database],['CEO Control','/workspace/CEO',Crown],['CMO Summary','/workspace/CMO',ShoppingCart],['CFO Summary','/workspace/CFO',DollarSign],['COO Summary','/workspace/COO',Factory],['CHRO Summary','/workspace/CHRO',Users]],
  CMO_MANAGER:[['CMO Home','/cmo',Home],['Order Management','/cmo/orders',ShoppingCart],['Customer / Buyer','/cmo/customers',Users],['Master Control','/master',Database]],
  CMO_SUPPORT:[['CMO Home','/cmo',Home],['Order Management','/cmo/orders',ShoppingCart],['Customer / Buyer','/cmo/customers',Users],['Master Control','/master',Database]],
  CFO_MANAGER:[['CFO Home','/workspace/CFO',Home],['Finance & Purchasing','/workspace/CFO',DollarSign],['Master Control','/master',Database]],
  FINANCE_SUPPORT:[['Finance Home','/workspace/CFO',Home],['Master Control','/master',Database]],
  COO_MANAGER:[['COO Home','/coo',Home],['Material Requests','/coo/material-requests',Package],['Production Queue','/coo/production',Factory],['WIP Tracking','/coo/wip',Package],['Master Control','/master',Database]],
  SAMPLE_PIC:[['My Sample Tasks','/workspace/SAMPLE',ClipboardList],['Master Control','/master',Database]],
  PRINTING_PIC:[['My Printing Tasks','/workspace/PRINTING',ClipboardList],['Master Control','/master',Database]],
  PRODUCTION_PIC:[['My Tasks','/workspace/PRODUCTION',ClipboardList],['Master Control','/master',Database]],
  CHRO_MANAGER:[['CHRO Home','/workspace/CHRO',Home],['People','/workspace/CHRO',Users],['Master Control','/master',Database]],
  HR_SUPPORT:[['HR Home','/workspace/CHRO',Home],['Master Control','/master',Database]],
  SHIPMENT_ADMIN:[['Shipment Tasks','/workspace/SHIPMENT',ClipboardList],['Master Control','/master',Database]]
};

export default function Layout(){
 const [me,setMe]=useState(null),[open,setOpen]=useState(false); const nav=useNavigate();
 useEffect(()=>{api('/auth/me').then(setMe)},[]);
 const menus=roleMenus[me?.role]||[['Master Control','/master',Database]];
 return <div className="app-shell">
   <aside className={'sidebar '+(open?'open':'')}>
    <div className="brand"><b>BOS SYAMS</b><span>Business Operating System</span></div>
    <button className="close-mobile" onClick={()=>setOpen(false)}><X/></button>
    <div className="userbox"><div className="avatar">{me?.name?.[0]||'S'}</div><div><strong>{me?.name||'...'}</strong><small>{me?.role?.replaceAll('_',' ')}</small></div></div>
    <nav>{menus.map(([label,path,Icon],i)=><NavLink key={i} to={path} onClick={()=>setOpen(false)} className={({isActive})=>isActive?'active':''}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
    <div className="side-foot"><NavLink to="/tasks"><ClipboardList size={18}/>Task</NavLink><NavLink to="/exceptions"><AlertTriangle size={18}/>Exception</NavLink><button onClick={()=>{clearToken();nav('/login')}}><LogOut size={18}/>Keluar</button></div>
   </aside>
   <main className="main"><header className="topbar"><button className="menu-mobile" onClick={()=>setOpen(true)}><Menu/></button><div className="search">Cari Order ID, Buyer, Article...</div><div className="top-user">{me?.name}</div></header><Outlet context={{me}}/></main>
 </div>
}
