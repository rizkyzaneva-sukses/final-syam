import React from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import Login from './pages/Login';
import MasterControl from './pages/MasterControl';
import OrderDetail from './pages/OrderDetail';
import Workspace from './pages/Workspace';
import ModuleDashboard from './pages/ModuleDashboard';
import Layout from './components/Layout';
import {getToken} from './api';
import './styles.css';

function Protected({children}){return getToken()?children:<Navigate to="/login" replace/>}
function App(){return <BrowserRouter><Routes>
  <Route path="/login" element={<Login/>}/>
  <Route path="/" element={<Protected><Layout/></Protected>}>
    <Route index element={<Navigate to="/master" replace/>}/>
    <Route path="master" element={<MasterControl/>}/>
    <Route path="orders/:orderId" element={<OrderDetail/>}/>
    <Route path="workspace/:name" element={<ModuleDashboard/>}/>
  </Route>
</Routes></BrowserRouter>}
createRoot(document.getElementById('root')).render(<App/>);
