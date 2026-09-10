import React,{useState,useEffect} from 'react';
import {useNavigate,Link} from 'react-router-dom';
import {api} from '../api';
import {ArrowLeft,Plus,Trash2,Check,Save} from 'lucide-react';

const TYPES=[{v:'SAMPLE_ONLY',l:'Sample Only'},{v:'SAMPLE_PRODUCTION',l:'Sample + Production'},{v:'REPEAT_PRODUCTION',l:'Repeat Production'}];

export default function OrderCreate(){
  const nav=useNavigate();
  const [customers,setCustomers]=useState([]);
  const [form,setForm]=useState({buyer:'',order_type:'SAMPLE_PRODUCTION',buyer_deadline:'',notes:''});
  const [articles,setArticles]=useState([{article_code:'',garment_type:'',qty:1,sample_required:false,production_route:'',size_breakdown:''}]);
  const [saving,setSaving]=useState(false),[err,setErr]=useState('');

  useEffect(()=>{api('/cmo/customers').then(setCustomers).catch(()=>{})},[]);

  function addArticle(){setArticles([...articles,{article_code:'',garment_type:'',qty:1,sample_required:false,production_route:'',size_breakdown:''}])}
  function rmArticle(i){setArticles(articles.filter((_,j)=>j!==i))}
  function updArticle(i,k,v){const a=[...articles];a[i]={...a[i],[k]:v};setArticles(a)}

  async function submit(e){
    e.preventDefault();
    if(!form.buyer.trim()){setErr('Buyer wajib diisi');return}
    if(!articles.length||!articles[0].article_code.trim()){setErr('Minimal 1 article dengan kode');return}
    setSaving(true);setErr('');
    try{
      const payload={
        buyer:form.buyer.trim(),
        order_type:form.order_type,
        buyer_deadline:form.buyer_deadline||null,
        notes:form.notes||null,
        articles:articles.filter(a=>a.article_code.trim()).map(a=>({
          article_code:a.article_code.trim(),
          garment_type:a.garment_type||null,
          qty:parseInt(a.qty)||1,
          sample_required:a.sample_required,
          production_route:a.production_route||null,
          size_breakdown:a.size_breakdown||null
        }))
      };
      const r=await api('/orders',{method:'POST',body:JSON.stringify(payload)});
      nav('/orders/'+r.order_id);
    }catch(x){setErr(x.message)}
    setSaving(false);
  }

  return <div className="page">
    <div className="page-title"><div><Link to="/cmo/orders" className="back-link"><ArrowLeft size={16}/> Kembali</Link><h1>Order Baru</h1><p>Buat order baru untuk buyer</p></div></div>
    {err&&<div className="notice danger">{err}</div>}
    <form onSubmit={submit} className="order-form">
      <section className="panel">
        <div className="panel-head"><h2>Data Order</h2></div>
        <div className="form-grid">
          <label>Buyer / Customer *
            <input list="buyer-list" required value={form.buyer} onChange={e=>setForm({...form,buyer:e.target.value})} placeholder="Pilih atau ketik nama buyer"/>
            <datalist id="buyer-list">{customers.map(c=><option key={c.id} value={c.name}/>)}</datalist>
          </label>
          <label>Tipe Order *
            <select value={form.order_type} onChange={e=>setForm({...form,order_type:e.target.value})}>
              {TYPES.map(t=><option key={t.v} value={t.v}>{t.l}</option>)}
            </select>
          </label>
          <label>Deadline Buyer<input type="date" value={form.buyer_deadline} onChange={e=>setForm({...form,buyer_deadline:e.target.value})}/></label>
        </div>
        <label>Catatan<textarea rows={2} value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})} placeholder="Catatan internal..."/></label>
      </section>

      <section className="panel">
        <div className="panel-head"><h2>Articles</h2><button type="button" className="btn sm" onClick={addArticle}><Plus size={14}/> Tambah</button></div>
        {articles.map((a,i)=><div className="article-form" key={i}>
          <div className="article-form-head"><b>Article {i+1}</b>{articles.length>1&&<button type="button" className="icon-btn danger" onClick={()=>rmArticle(i)}><Trash2 size={14}/></button>}</div>
          <div className="form-grid">
            <label>Kode Article *<input required value={a.article_code} onChange={e=>updArticle(i,'article_code',e.target.value)} placeholder="HD-CLASSIC"/></label>
            <label>Jenis Garment<input value={a.garment_type} onChange={e=>updArticle(i,'garment_type',e.target.value)} placeholder="Hoodie / Jacket / T-Shirt"/></label>
            <label>Qty *<input type="number" min={1} required value={a.qty} onChange={e=>updArticle(i,'qty',e.target.value)}/></label>
          </div>
          <div className="form-grid3">
            <label className="check-label"><input type="checkbox" checked={a.sample_required} onChange={e=>updArticle(i,'sample_required',e.target.checked)}/> Perlu Sample</label>
            <label>Rute Produksi<input value={a.production_route} onChange={e=>updArticle(i,'production_route',e.target.value)} placeholder="Cutting → Sewing → QC"/></label>
            <label>Size Breakdown<input value={a.size_breakdown} onChange={e=>updArticle(i,'size_breakdown',e.target.value)} placeholder='{"S":50,"M":80,"L":50,"XL":20}'/></label>
          </div>
        </div>)}
      </section>

      <div className="form-actions">
        <Link to="/cmo/orders" className="btn">Batal</Link>
        <button type="submit" className="btn primary" disabled={saving}><Save size={14}/> {saving?'Menyimpan...':'Buat Order'}</button>
      </div>
    </form>
  </div>
}
