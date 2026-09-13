import React from 'react';

const labels={on_time_shipments:'Pengiriman tepat waktu',qc_inspection_pass:'Unit lolos per inspeksi QC',approved_quote_margin:'Margin quotation disetujui'};
export default function KPIOverview({kpis}){
  const entries=Object.entries(kpis||{});
  if(!entries.length)return null;
  return <section className="panel"><div className="panel-head"><h2>KPI dari transaksi</h2></div>
    <div className="table-scroll"><table><thead><tr><th>Indikator</th><th>Hasil</th><th>Pembilang</th><th>Penyebut</th></tr></thead><tbody>
      {entries.map(([key,k])=><tr key={key}><td>{labels[key]||key}</td><td>{k.value==null?'Belum ada data':`${k.value}%`}</td><td>{k.numerator}</td><td>{k.denominator}</td></tr>)}
    </tbody></table></div><small>Nilai kosong berarti belum ada transaksi yang memenuhi syarat, bukan 0%.</small></section>
}
