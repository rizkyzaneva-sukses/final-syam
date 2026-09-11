import React,{useEffect,useState} from 'react';
import {Outlet,NavLink,useNavigate} from 'react-router-dom';
import {Home,Database,Package,ShoppingCart,DollarSign,Factory,Users,Crown,ClipboardList,AlertTriangle,LogOut,Menu,X,FileText,BarChart3,BookOpen,Truck,CheckSquare} from 'lucide-react';
import {api,clearToken} from '../api';
import GlobalSearch from './GlobalSearch';

const roleMenus={
  CEO:[['CEO Home','/ceo',Crown],['Master Control','/master',Database],['Decisions','/ceo/decisions',ClipboardList],['Exceptions','/exceptions',AlertTriangle],['Audit Log','/audit-log',ClipboardList],['CMO Home','/cmo',ShoppingCart],['CFO Home','/cfo',DollarSign],['COO Home','/coo',Factory],['CHRO Home','/chro',Users],['Deliveries','/coo/deliveries',Truck],['Order Closing','/coo/closing',CheckSquare]],
  CMO_MANAGER:[['CMO Home','/cmo',Home],['Order Management','/cmo/orders',ShoppingCart],['Customer / Buyer','/cmo/customers',Users],['Quotations','/cmo/quotations',FileText],['Sample / PPM','/cmo/samples',ClipboardList],['SPK','/cmo/spk',CheckSquare],['Master Control','/master',Database],['Deliveries','/coo/deliveries',Truck],['Order Closing','/coo/closing',CheckSquare]],
  CMO_SUPPORT:[['CMO Home','/cmo',Home],['Order Management','/cmo/orders',ShoppingCart],['Customer / Buyer','/cmo/customers',Users],['Quotations','/cmo/quotations',FileText],['Sample / PPM','/cmo/samples',ClipboardList],['Master Control','/master',Database]],
  CFO_MANAGER:[['CFO Home','/cfo',Home],['Invoices','/cfo/invoices',DollarSign],['Purchase Orders','/cfo/purchase-orders',Package],['Shipments Gate','/cfo/shipments',Truck],['Master Control','/master',Database],['Deliveries','/coo/deliveries',Truck]],
  FINANCE_SUPPORT:[['CFO Home','/cfo',Home],['Invoices','/cfo/invoices',DollarSign],['Master Control','/master',Database]],
  COO_MANAGER:[['COO Home','/coo',Home],['Material Requests','/coo/material-requests',Package],['Production Queue','/coo/production',Factory],['WIP Tracking','/coo/wip',Package],['QC Records','/coo/qc',CheckSquare],['Shipments','/cfo/shipments',Truck],['Master Control','/master',Database],['Production Plan','/coo/planning',Factory],['Deliveries','/coo/deliveries',Truck],['Order Closing','/coo/closing',CheckSquare]],
  SAMPLE_PIC:[['My Sample Tasks','/tasks',ClipboardList],['Samples','/cmo/samples',ClipboardList],['Master Control','/master',Database]],
  PRINTING_PIC:[['My Tasks','/tasks',ClipboardList],['Production Queue','/coo/production',Factory],['Master Control','/master',Database]],
  PRODUCTION_PIC:[['My Tasks','/tasks',ClipboardList],['Production Queue','/coo/production',Factory],['Material Requests','/coo/material-requests',Package],['Master Control','/master',Database]],
  CHRO_MANAGER:[['CHRO Home','/chro',Home],['Employees','/chro/employees',Users],['Training','/chro/training',BookOpen],['Performance','/chro/performance',BarChart3],['Employee Issues','/chro/issues',AlertTriangle],['Master Control','/master',Database]],
  HR_SUPPORT:[['CHRO Home','/chro',Home],['Employees','/chro/employees',Users],['Training','/chro/training',BookOpen],['Master Control','/master',Database]],
  SHIPMENT_ADMIN:[['Shipments','/cfo/shipments',Truck],['Master Control','/master',Database],['Deliveries','/coo/deliveries',Truck]]
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
   <main className="main"><header className="topbar"><button className="menu-mobile" onClick={()=>setOpen(true)}><Menu/></button><GlobalSearch/><div className="top-user">{me?.name}</div></header><Outlet context={{me}}/></main>
 </div>}
