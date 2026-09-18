import React,{useEffect,useState} from 'react';
import {useParams,useOutletContext} from 'react-router-dom';
import {flowGates} from '../business';
import {api} from '../api';
import FlowProgress from '../components/FlowProgress';
import FlowGate from '../components/FlowGate';

export default function OrderDetail(){
  const {orderId}=useParams();
  const {me}=useOutletContext();
  const [o,setO]=useState(null);
  const [m,setM]=useState([]);
  const [flowData,setFlowData]=useState(null);
  const [advancing,setAdvancing]=useState(false);
  const [flowErr,setFlowErr]=useState('');
  const [deliveryData,setDeliveryData]=useState(null);
  const [deliveryErr,setDeliveryErr]=useState('');

  useEffect(()=>{
    Promise.all([
      api('/orders/'+orderId),
      api('/master/process-movement/'+orderId),
      api('/orders/'+orderId+'/flow')
    ]).then(([order,movement,flow])=>{
      setO(order);
      setM(movement);
      if(flow) setFlowData(flow);
    });
  },[orderId]);

  useEffect(()=>{
    if(!['CMO_MANAGER','CMO_SUPPORT'].includes(me?.role)) return;
    setDeliveryData(null);
    setDeliveryErr('');
    Promise.all([api('/coo/shipments'),api('/coo/deliveries')])
      .then(([shipments,confirmations])=>setDeliveryData({shipments,confirmations}))
      .catch(e=>setDeliveryErr(e.message));
  },[orderId,me?.role]);

  async function handleAdvance(stepKey){
    setAdvancing(true); setFlowErr('');
    try{
      // Backend expects {target_step: "STEP_NAME"}
      const res=await api('/orders/'+orderId+'/flow/advance',{
        method:'POST',
        body:JSON.stringify({target_step:stepKey})
      });
      // Update local state
      setO(prev=>({...prev, flow_step:res.new_step, overall_status:res.overall_status||prev.overall_status}));
      // Re-fetch flow data
      const flow=await api('/orders/'+orderId+'/flow').catch(()=>null);
      if(flow) setFlowData(flow);
    }catch(e){setFlowErr(e.message)}
    setAdvancing(false);
  }

  if(!o) return <div className="page">{flowErr||'Memuat...'}</div>;

  const gates = flowGates(flowData);
  const steps = flowData?.progress?.steps || [];
  const currentStep = flowData?.current_step || o.flow_step || 'ORDER';
  const pct = flowData?.progress?.percent ?? 0;
  const orderShipments=deliveryData?.shipments.filter(s=>s.order_fk===o.id)||[];

  return (
    <div className="page">
      <div className="page-title">
        <div>
          <h1>{o.order_id}</h1>
          <p>{o.buyer} • {o.order_type?.replace(/_/g,' ')} • Flow: <b style={{color:'#3b82f6'}}>{currentStep}</b></p>
        </div>
        <span className={'badge '+(o.overall_status==='CLOSED'?'gray':o.overall_status==='ACTIVE'?'green':o.overall_status==='HOLD'?'amber':'blue')}>
          {o.overall_status}
        </span>
      </div>

      {flowErr && <div className="notice danger">{flowErr}</div>}

      {['CMO_MANAGER','CMO_SUPPORT'].includes(me?.role)&&<section className="panel">
        <h2>Status Pengiriman</h2>
        {deliveryErr?<div className="notice danger">{deliveryErr}</div>:!deliveryData?<p>Memuat pengiriman...</p>:orderShipments.length?orderShipments.map(s=>{
          const confirmation=deliveryData.confirmations.find(d=>d.shipment_fk===s.id);
          return <div className="article" key={s.id}>
            <b>{s.shipment_no||`Shipment #${s.id}`}</b>
            <span>Status: {s.status} · Konfirmasi buyer: {confirmation?.status||'BELUM ADA'}</span>
            <small>Resi: {s.tracking_no||'—'} · Tanggal kirim: {s.shipped_date||'—'} · Tanggal tiba: {s.delivery_date||'—'}</small>
          </div>;
        }):<p>Belum ada pengiriman untuk order ini.</p>}
      </section>}

      {/* ── Flow Progress Bar ── */}
      <section className="panel" style={{marginBottom:20}}>
        <div className="panel-head">
          <h2>Order Flow — {o.order_type?.replace(/_/g,' ')}</h2>
          <span className="badge blue">{pct}% selesai</span>
        </div>
        <FlowProgress
          orderType={o.order_type}
          currentStep={currentStep}
          flowSteps={steps}
        />
      </section>

      {/* ── Flow Gate ── */}
      <FlowGate
        gates={gates}
        role={me?.role}
        busy={advancing}
        onAdvance={handleAdvance}
        currentStep={currentStep}
      />

      {/* ── Order Info Cards ── */}
      <div className="cards compact">
        <Card k="Deadline" v={o.buyer_deadline||'-'}/>
        <Card k="Finance" v={o.finance_status}/>
        <Card k="Material" v={o.material_status}/>
        <Card k="Shipment" v={o.shipment_status}/>
        <Card k="Buffer" v={(o.buffer_days??'-')+' hari'}/>
      </div>

      {/* ── Articles ── */}
      <section className="panel">
        <h2>Article</h2>
        {o.articles?.map(a=>(
          <div className="article" key={a.id}>
            <b>{a.article_code}</b>
            <span>{a.garment_type} • {a.qty} pcs</span>
            <span>Sample: {a.sample_required?'YA':'TIDAK'} / {a.sample_status}</span>
            <small>{a.production_route||'-'}</small>
          </div>
        ))}
      </section>

      {/* ── Process Movement ── */}
      {m.length > 0 && (
        <section className="panel">
          <div className="panel-head">
            <h2>Process Movement</h2>
            <span>Qty In → Done → WIP</span>
          </div>
          <div className="movement">
            {m.map((x,i)=>(
              <div className="move" key={i}>
                <div className="circle">{i+1}</div>
                <b>{x.process}</b>
                <span>{x.qty_done}/{x.qty_in}</span>
                <small>WIP {x.wip} • PIC {x.pic||'-'}</small>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ── Closure ── */}
      <section className="panel">
        <h2>Closure</h2>
        <div className="closure">
          <span>Customer Closed: <b>{o.customer_close_status||'OPEN'}</b></span>
          <span>Financial Closed: <b>{o.financial_close_status||'OPEN'}</b></span>
          <span>Order Closed hanya setelah kedua kondisi terpenuhi.</span>
        </div>
      </section>
    </div>
  );
}

function Card({k,v}){return <div className="mini"><small>{k}</small><b>{v}</b></div>}
