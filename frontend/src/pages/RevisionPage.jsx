import React,{useEffect,useState} from 'react';
import {Camera,ImagePlus,MessageSquarePlus,Search,X} from 'lucide-react';
import {api} from '../api';

const emptyForm={module_name:'',bug_description:'',expected_behavior:''};
const maxImageBytes=5*1024*1024;
const allowedTypes=new Set(['image/png','image/jpeg','image/webp']);

function formatDate(value){return new Intl.DateTimeFormat('id-ID',{dateStyle:'medium',timeStyle:'short'}).format(new Date(value));}

export default function RevisionPage(){
  const [form,setForm]=useState(emptyForm),[image,setImage]=useState(null),[preview,setPreview]=useState('');
  const [items,setItems]=useState([]),[hasMore,setHasMore]=useState(false),[loading,setLoading]=useState(true);
  const [query,setQuery]=useState(''),[detail,setDetail]=useState(null),[detailImage,setDetailImage]=useState('');
  const [error,setError]=useState(''),[success,setSuccess]=useState(''),[saving,setSaving]=useState(false);

  useEffect(()=>{
    let active=true;
    api('/revisions?limit=100&offset=0').then(rows=>{if(active){setItems(rows);setHasMore(rows.length===100);}})
      .catch(e=>{if(active)setError(e.message)})
      .finally(()=>{if(active)setLoading(false)});
    return ()=>{active=false};
  },[]);

  useEffect(()=>{
    if(!image){setPreview('');return;}
    const url=URL.createObjectURL(image);setPreview(url);
    return ()=>URL.revokeObjectURL(url);
  },[image]);

  useEffect(()=>{
    if(!detail?.has_image){setDetailImage('');return;}
    let active=true,url='';
    api(`/revisions/${detail.id}/image`,{responseType:'blob'}).then(blob=>{
      if(active){url=URL.createObjectURL(blob);setDetailImage(url);}
    }).catch(e=>{if(active)setError(e.message)});
    return ()=>{active=false;if(url)URL.revokeObjectURL(url);setDetailImage('')};
  },[detail]);

  function chooseImage(file){
    if(!file)return;
    if(!allowedTypes.has(file.type)){setError('Gunakan gambar PNG, JPG, atau WebP.');return;}
    if(file.size>maxImageBytes){setError('Gambar maksimal 5 MB.');return;}
    setImage(file);setError('');
  }

  function handlePaste(event){
    const file=Array.from(event.clipboardData?.items||[]).find(item=>item.type.startsWith('image/'))?.getAsFile();
    if(file){event.preventDefault();chooseImage(file);}
  }

  async function save(event){
    event.preventDefault();setSaving(true);setError('');setSuccess('');
    const payload=new FormData();
    for(const [key,value] of Object.entries(form))payload.append(key,value.trim());
    if(image)payload.append('image',image,image.name||'screenshot.png');
    try{
      const created=await api('/revisions',{method:'POST',body:payload});
      setItems(current=>[created,...current]);setForm(emptyForm);setImage(null);
      setSuccess('Usulan revisi berhasil dikirim.');
    }catch(e){setError(e.message)}
    finally{setSaving(false)}
  }

  async function loadMore(){
    setLoading(true);setError('');
    try{
      const rows=await api(`/revisions?limit=100&offset=${items.length}`);
      setItems(current=>[...current,...rows]);setHasMore(rows.length===100);
    }catch(e){setError(e.message)}
    finally{setLoading(false)}
  }

  const visible=items.filter(item=>[item.module_name,item.bug_description,item.expected_behavior,item.reported_by_name]
    .some(value=>value.toLowerCase().includes(query.trim().toLowerCase())));

  return <div className="page revision-page">
    <div className="page-title"><div><h1>Usulan Revisi</h1><p>Laporkan modul yang bermasalah agar semua masukan terkumpul di satu tempat.</p></div></div>
    {error&&<div className="notice danger" role="alert">{error}</div>}
    {success&&<div className="notice success" role="status">{success}</div>}

    <div className="revision-layout">
      <section className="panel revision-form-panel" aria-labelledby="revision-form-title">
        <div className="revision-panel-heading"><span className="revision-heading-icon"><MessageSquarePlus size={21}/></span><div><h2 id="revision-form-title">Buat usulan</h2><p>Ceritakan masalahnya dengan singkat dan jelas.</p></div></div>
        <form onSubmit={save} onPaste={handlePaste}>
          <label><span>Modul yang error <span className="revision-required">*</span></span>
            <input required maxLength={120} value={form.module_name} onChange={e=>setForm({...form,module_name:e.target.value})} placeholder="Contoh: Order Management, QC Records"/>
          </label>
          <label><span>Bug <span className="revision-required">*</span></span>
            <textarea required maxLength={5000} rows={4} value={form.bug_description} onChange={e=>setForm({...form,bug_description:e.target.value})} placeholder="Apa yang terjadi saat modul digunakan?"/>
          </label>
          <label><span>Harusnya seperti apa <span className="revision-required">*</span></span>
            <textarea required maxLength={5000} rows={4} value={form.expected_behavior} onChange={e=>setForm({...form,expected_behavior:e.target.value})} placeholder="Hasil yang Anda harapkan..."/>
          </label>
          <div className="revision-image-heading"><b>Gambar pendukung</b><span>Opsional · PNG, JPG, WebP · maks. 5 MB</span></div>
          <div className="revision-upload" tabIndex={0} role="group" aria-label="Area gambar pendukung; tempel screenshot dengan Ctrl dan V" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();chooseImage(e.dataTransfer.files[0])}}>
            {preview?<div className="revision-preview"><img src={preview} alt="Pratinjau gambar pendukung"/><button type="button" className="btn sm" onClick={()=>setImage(null)}><X size={14}/> Hapus gambar</button></div>
              :<div className="revision-upload-empty"><ImagePlus size={28}/><strong>Tempel screenshot dengan Ctrl + V</strong><span>atau pilih gambar dari perangkat Anda</span></div>}
            <input type="file" accept="image/png,image/jpeg,image/webp" aria-label="Pilih gambar pendukung" onChange={e=>{chooseImage(e.target.files[0]);e.target.value=''}}/>
          </div>
          <div className="revision-form-foot"><span><span className="revision-required">*</span> Wajib diisi</span><button className="btn primary" disabled={saving} type="submit"><MessageSquarePlus size={16}/>{saving?'Mengirim...':'Kirim usulan'}</button></div>
        </form>
      </section>

      <section className="revision-feed" aria-labelledby="revision-feed-title">
        <div className="revision-feed-head"><div><h2 id="revision-feed-title">Usulan dari semua user</h2><p>{items.length} usulan terbaru</p></div></div>
        <div className="search-bar"><Search size={16}/><input aria-label="Cari usulan revisi" placeholder="Cari modul, bug, atau pelapor..." value={query} onChange={e=>setQuery(e.target.value)}/></div>
        {visible.map(item=><article key={item.id} className="revision-card">
          <div className="revision-card-top"><span className="revision-module">{item.module_name}</span>{item.has_image&&<span className="revision-image-badge"><Camera size={14}/> Gambar</span>}</div>
          <div className="revision-card-meta">{item.reported_by_name} · {formatDate(item.created_at)}</div>
          <div className="revision-card-copy"><b>Bug</b><p>{item.bug_description}</p></div>
          <div className="revision-card-copy"><b>Harusnya</b><p>{item.expected_behavior}</p></div>
          <button className="revision-detail-link" type="button" onClick={()=>setDetail(item)}>Lihat detail</button>
        </article>)}
        {!loading&&visible.length===0&&<div className="panel revision-empty">{query?'Tidak ada usulan yang cocok.':'Belum ada usulan revisi. Jadilah yang pertama mengirim.'}</div>}
        {loading&&<div className="revision-loading">Memuat usulan...</div>}
        {hasMore&&!loading&&<button type="button" className="btn revision-load-more" onClick={loadMore}>Muat lebih banyak</button>}
      </section>
    </div>

    {detail&&<div className="modal-bg" onClick={()=>setDetail(null)}><div className="modal revision-modal" role="dialog" aria-modal="true" aria-labelledby="revision-detail-title" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><h2 id="revision-detail-title">{detail.module_name}</h2><button className="icon-btn" type="button" aria-label="Tutup detail" onClick={()=>setDetail(null)}><X size={18}/></button></div>
      <div className="revision-modal-body"><p className="revision-card-meta">Dikirim oleh {detail.reported_by_name} · {formatDate(detail.created_at)}</p><h3>Bug</h3><p>{detail.bug_description}</p><h3>Harusnya seperti apa</h3><p>{detail.expected_behavior}</p>{detail.has_image&&<><h3>Gambar pendukung</h3>{detailImage?<img className="revision-detail-image" src={detailImage} alt={`Gambar pendukung untuk ${detail.module_name}`}/>:<p>Memuat gambar...</p>}</>}</div>
    </div></div>}
  </div>;
}
