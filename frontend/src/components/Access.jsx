import React from 'react';
import {useLocation,useOutletContext} from 'react-router-dom';
import {canAccess} from '../business';
export function useRole(){return useOutletContext()?.me?.role;}
export default function Access({children}){const role=useRole(),{pathname}=useLocation();if(!role)return <div className="page">Memuat akses...</div>;return canAccess(role,pathname)?children:<div className="page"><div className="notice danger">Halaman ini tidak tersedia untuk peran Anda.</div></div>;}
