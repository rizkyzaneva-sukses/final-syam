import React from 'react';
import {Check, Lock, ArrowRight, AlertTriangle, Play} from 'lucide-react';

export default function FlowGate({ gates, onAdvance, currentStep }) {
  if (!gates || !gates.length) {
    return (
      <div className="panel" style={{marginTop:16}}>
        <div className="panel-head"><h2>Flow Gate</h2></div>
        <div className="empty">No flow gate data — advance to begin the flow</div>
      </div>
    );
  }

  const blocked = gates.filter(g => g.status === 'blocked');
  const ready = gates.filter(g => g.status === 'ready');
  const completed = gates.filter(g => g.status === 'completed');
  const next = gates.filter(g => g.status === 'next');

  return (
    <div className="panel" style={{marginTop:16}}>
      <div className="panel-head">
        <h2>Flow Gate</h2>
        <span className="badge blue" style={{fontSize:11}}>
          {next.length} next · {ready.length} ready · {blocked.length} blocked
        </span>
      </div>

      {/* Next action */}
      {next.length > 0 && (
        <div style={{marginBottom:12}}>
          <div style={{fontSize:12,fontWeight:700,color:'#3b82f6',marginBottom:6,textTransform:'uppercase'}}>
            ⏭ Next Action Required
          </div>
          {next.map(g => (
            <div className="flow-gate flow-gate-next" key={g.step}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <div>
                  <b style={{fontSize:14}}>{g.label}</b>
                  <div style={{fontSize:11,color:'#64748b',marginTop:2}}>Role: <b style={{color:'#3b82f6'}}>{g.role}</b></div>
                </div>
                {onAdvance && (
                  <button className="btn primary sm" onClick={() => onAdvance(g.step)}>
                    <Play size={13}/> Advance
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ready */}
      {ready.length > 0 && (
        <div style={{marginBottom:12}}>
          <div style={{fontSize:12,fontWeight:700,color:'#22c55e',marginBottom:6,textTransform:'uppercase'}}>
            ✓ Ready to Advance
          </div>
          {ready.map(g => (
            <div className="flow-gate flow-gate-ready" key={g.step}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <div>
                  <b style={{fontSize:14}}>{g.label}</b>
                  <div style={{fontSize:11,color:'#64748b',marginTop:2}}>Role: <b style={{color:'#059669'}}>{g.role}</b></div>
                </div>
                {onAdvance && (
                  <button className="btn primary sm" onClick={() => onAdvance(g.step)}>
                    <ArrowRight size={13}/> Advance
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Blocked */}
      {blocked.length > 0 && (
        <div style={{marginBottom:12}}>
          <div style={{fontSize:12,fontWeight:700,color:'#ef4444',marginBottom:6,textTransform:'uppercase'}}>
            ✕ Blocked — Prerequisites Not Met
          </div>
          {blocked.map(g => (
            <div className="flow-gate flow-gate-blocked" key={g.step}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                <div style={{flex:1}}>
                  <b style={{fontSize:14}}>{g.label}</b>
                  <div style={{fontSize:11,color:'#64748b',marginTop:2}}>Role: {g.role}</div>
                  {g.reason && (
                    <div style={{display:'flex',alignItems:'center',gap:4,marginTop:4,fontSize:12,color:'#ef4444'}}>
                      <AlertTriangle size={13}/> {g.reason}
                    </div>
                  )}
                </div>
                <Lock size={16} style={{color:'#d1d5db',flexShrink:0,marginTop:4}}/>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Completed */}
      {completed.length > 0 && (
        <div>
          <div style={{fontSize:12,fontWeight:700,color:'#22c55e',marginBottom:6,textTransform:'uppercase'}}>
            ✓ Completed
          </div>
          {completed.map(g => (
            <div className="flow-gate" key={g.step} style={{borderLeft:'4px solid #22c55e',opacity:.7}}>
              <div style={{display:'flex',alignItems:'center',gap:8}}>
                <Check size={16} style={{color:'#22c55e',flexShrink:0}}/>
                <div>
                  <b style={{fontSize:13,textDecoration:'line-through'}}>{g.label}</b>
                  <div style={{fontSize:11,color:'#64748b'}}>Role: {g.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
