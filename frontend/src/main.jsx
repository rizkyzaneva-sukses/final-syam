import React from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import Login from './pages/Login';
import MasterControl from './pages/MasterControl';
import OrderDetail from './pages/OrderDetail';
import CMOHome from './pages/CMOHome';
import CustomerList from './pages/CustomerList';
import OrderList from './pages/OrderList';
import OrderCreate from './pages/OrderCreate';
import QuotationPage from './pages/QuotationPage';
import SamplePPMPage from './pages/SamplePPMPage';
import SPKPage from './pages/SPKPage';
import ExceptionPage from './pages/ExceptionPage';
import TaskPage from './pages/TaskPage';
import CFOHome from './pages/CFOHome';
import InvoicePage from './pages/InvoicePage';
import PurchaseOrderPage from './pages/PurchaseOrderPage';
import ShipmentListPage from './pages/ShipmentListPage';
import COOHome from './pages/COOHome';
import MaterialRequestPage from './pages/MaterialRequestPage';
import ProductionQueue from './pages/ProductionQueue';
import WIPTracking from './pages/WIPTracking';
import QCRecordPage from './pages/QCRecordPage';
import CEOHome from './pages/CEOHome';
import DecisionPage from './pages/DecisionPage';
import CHROHome from './pages/CHROHome';
import EmployeePage from './pages/EmployeePage';
import TrainingPage from './pages/TrainingPage';
import PerformancePage from './pages/PerformancePage';
import EmployeeIssuePage from './pages/EmployeeIssuePage';
import AuditLogPage from './pages/AuditLogPage';
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
    {/* CMO */}
    <Route path="cmo" element={<CMOHome/>}/>
    <Route path="cmo/customers" element={<CustomerList/>}/>
    <Route path="cmo/orders" element={<OrderList/>}/>
    <Route path="cmo/orders/new" element={<OrderCreate/>}/>
    <Route path="cmo/quotations" element={<QuotationPage/>}/>
    <Route path="cmo/samples" element={<SamplePPMPage/>}/>
    <Route path="cmo/spk" element={<SPKPage/>}/>
    {/* CFO */}
    <Route path="cfo" element={<CFOHome/>}/>
    <Route path="cfo/invoices" element={<InvoicePage/>}/>
    <Route path="cfo/purchase-orders" element={<PurchaseOrderPage/>}/>
    <Route path="cfo/shipments" element={<ShipmentListPage/>}/>
    {/* COO */}
    <Route path="coo" element={<COOHome/>}/>
    <Route path="coo/material-requests" element={<MaterialRequestPage/>}/>
    <Route path="coo/production" element={<ProductionQueue/>}/>
    <Route path="coo/wip" element={<WIPTracking/>}/>
    <Route path="coo/qc" element={<QCRecordPage/>}/>
    {/* CEO */}
    <Route path="ceo" element={<CEOHome/>}/>
    <Route path="ceo/decisions" element={<DecisionPage/>}/>
    {/* CHRO */}
    <Route path="chro" element={<CHROHome/>}/>
    <Route path="chro/employees" element={<EmployeePage/>}/>
    <Route path="chro/training" element={<TrainingPage/>}/>
    <Route path="chro/performance" element={<PerformancePage/>}/>
    <Route path="chro/issues" element={<EmployeeIssuePage/>}/>
    {/* Common */}
    <Route path="audit-log" element={<AuditLogPage/>}/>
    <Route path="exceptions" element={<ExceptionPage/>}/>
    <Route path="tasks" element={<TaskPage/>}/>
  </Route>
</Routes></BrowserRouter>}
createRoot(document.getElementById('root')).render(<App/>);
