import React from 'react';
import {Check, Lock} from 'lucide-react';

// Step definitions matching backend flow_engine.py exactly
const STEP_DEFS = {
  ORDER:           { label: 'Order Diterima',         gate: 'CMO' },
  INVOICE:         { label: 'Invoice & Pembayaran',   gate: 'CFO' },
  PPM:             { label: 'PPM / Penyesuaian',      gate: 'CMO+COO' },
  SAMPLE:          { label: 'Sample / PPM',           gate: 'SAMPLE_PIC' },
  SAMPLE_APPROVED: { label: 'Sample Disetujui',       gate: 'CMO' },
  FOLLOW_UP:       { label: 'Follow-up / Pengembangan', gate: 'CMO' },
  SPK:             { label: 'SPK Release',            gate: 'CMO' },
  PRODUCTION:      { label: 'Produksi',               gate: 'COO' },
  QC:              { label: 'QC & Packing',           gate: 'PRODUCTION_PIC' },
  SHIPMENT:        { label: 'Pengiriman',             gate: 'SHIPMENT_ADMIN' },
  DELIVERED:       { label: 'Diterima Customer',      gate: 'CMO' },
  CLOSED:          { label: 'Order Selesai',          gate: 'CMO+CFO' },
};

const ROLE_COLORS = {
  CMO: '#2563eb', CFO: '#7c3aed', COO: '#059669', CEO: '#dc2626',
  'CMO+COO': '#0891b2', 'CMO+CFO': '#7c3aed',
  SAMPLE_PIC: '#ea580c', PRODUCTION_PIC: '#059669', SHIPMENT_ADMIN: '#0891b2',
};

export default function FlowProgress({ orderType, currentStep, flowSteps }) {
  // Use steps from API or build from default flows
  let steps;
  if (flowSteps && flowSteps.length) {
    // API returns [{key, label, gate}] — use as-is
    steps = flowSteps.map(s => ({
      key: s.key || s.step_key,
      label: s.label || STEP_DEFS[s.key || s.step_key]?.label || s.key,
      gate: s.gate || STEP_DEFS[s.key || s.step_key]?.gate || '',
      optional: s.optional,
    }));
  } else {
    // Fallback: build from known flow definitions
    const FLOWS = {
      SAMPLE_ONLY:        ['ORDER','INVOICE','PPM','SAMPLE','SAMPLE_APPROVED','FOLLOW_UP','CLOSED'],
      SAMPLE_PRODUCTION:  ['ORDER','INVOICE','SAMPLE','SAMPLE_APPROVED','SPK','PRODUCTION','QC','SHIPMENT','DELIVERED','CLOSED'],
      REPEAT_PRODUCTION:  ['ORDER','INVOICE','PPM','SPK','PRODUCTION','QC','SHIPMENT','DELIVERED','CLOSED'],
    };
    const keys = FLOWS[orderType] || FLOWS.SAMPLE_PRODUCTION;
    steps = keys.map(k => ({
      key: k,
      label: STEP_DEFS[k]?.label || k,
      gate: STEP_DEFS[k]?.gate || '',
      optional: orderType === 'REPEAT_PRODUCTION' && k === 'PPM',
    }));
  }

  const curKey = currentStep || 'ORDER';
  const currentIndex = steps.findIndex(s => s.key === curKey);
  const effectiveIndex = currentIndex >= 0 ? currentIndex : 0;
  const pct = steps.length > 1 ? Math.round((effectiveIndex / (steps.length - 1)) * 100) : 0;

  return (
    <div className="flow-progress-wrapper">
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
        <span style={{fontSize:13,fontWeight:600,color:'#374151'}}>
          Flow — <span style={{color:'#64748b'}}>{orderType?.replace(/_/g,' ')}</span>
        </span>
        <span className="badge blue">{pct}%</span>
      </div>
      <div className="flow-progress">
        {steps.map((step, i) => {
          const isCompleted = i < effectiveIndex;
          const isActive = i === effectiveIndex;
          const statusCls = isCompleted ? 'completed' : isActive ? 'active' : '';
          const roleColor = ROLE_COLORS[step.gate] || '#64748b';

          return (
            <React.Fragment key={step.key}>
              {i > 0 && (
                <div className={`flow-line ${i <= effectiveIndex ? 'completed' : ''} ${i === effectiveIndex ? 'active' : ''}`} />
              )}
              <div className={`flow-step ${statusCls}`}>
                <div className="flow-step-role" style={{color: roleColor}}>
                  {step.gate}
                </div>
                {step.optional && (
                  <span style={{fontSize:9,color:'#f59e0b',fontWeight:700,marginBottom:2}}>Optional</span>
                )}
                <div className="flow-step-circle">
                  {isCompleted ? <Check size={16}/> : isActive ? <span style={{fontSize:11}}>●</span> : <Lock size={12}/>}
                </div>
                <div className="flow-step-label">{step.label}</div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
