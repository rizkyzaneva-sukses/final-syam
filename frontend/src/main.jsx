import React from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import Login from './pages/Login';
import MasterControl from './pages/MasterControl';
import OrderDetail from './pages/OrderDetail';
import ModuleDashboard from './pages/ModuleDashboard';
import CMOHome from './pages/CMOHome';
import CustomerList from './pages/CustomerList';
import OrderList from './pages/OrderList';
import OrderCreate from './pages/OrderCreate';
import ExceptionPage from './pages/ExceptionPage';
import TaskPage from './pages/TaskPage';
import COOHome from './pages/COOHome';
import MaterialRequestPage from './pages/MaterialRequestPage';
import ProductionQueue from './pages/ProductionQueue';
import WIPTracking from './pages/WIPTracking';
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
    <Route path="cmo" element={<CMOHome/>}/>
    <Route path="cmo/customers" element={<CustomerList/>}/>
    <Route path="cmo/orders" element={<OrderList/>}/>
    <Route path="cmo/orders/new" element={<OrderCreate/>}/>
    <Route path="exceptions" element={<ExceptionPage/>}/>
    <Route path="tasks" element={<TaskPage/>}/>
    <Route path="coo" element={<COOHome/>}/>
    <Route path="coo/material-requests" element={<MaterialRequestPage/>}/>
    <Route path="coo/production" element={<ProductionQueue/>}/>
    <Route path="coo/wip" element={<WIPTracking/>}/>
    <Route path="workspace/:name" element={<ModuleDashboard/>}/>
  </Route>
</Routes></BrowserRouter>}
createRoot(document.getElementById('root')).render(<App/>);
