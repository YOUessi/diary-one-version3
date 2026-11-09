"use strict";
(() => {
const DATA = JSON.parse(document.querySelector("#chapter-data").textContent);
const METHODS={jpeg:{label:"人工标注",sub:"已标注范例",tag:"人工精选"}};
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const ICON={
 back:'<path d="m15 18-6-6 6-6"/>',
 star:'<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.9L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1L12 2Z"/>',
 share:'<rect x="5" y="8" width="14" height="13" rx="3"/><path d="M12 15V2m-5 5 5-5 5 5"/>',
 play:'<path d="M8 5v14l11-7Z"/>',
 next:'<path d="m9 18 6-6-6-6"/>'
};
const svg=(name,size=22)=>'<svg aria-hidden="true" width="'+size+'" height="'+size+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+(ICON[name]||ICON.play)+'</svg>';
function localObject(key) {try{return JSON.parse(localStorage.getItem(key)||"{}")||{}}catch{return {}}}
const favorites=localObject("nexleapOneExamplesFavoritesV1");
const notes=localObject("nexleapOneExamplesStoriesV1");
const params=new URLSearchParams(location.search);
const state={
 offset: DATA.offsets.includes(Number(params.get("offset")))?Number(params.get("offset")):DATA.offsets[0],
 method:METHODS[params.get("method")]?params.get("method"):"jpeg",
 chapter:Math.max(0,Number(params.get("chapter")||1)-1),
 view:params.has("chapter")?"detail":"day",
 editing:false
};
let currentLive=null;let toastTimeout;
const group=()=>DATA.groups[String(state.offset)][state.method];
const chapters=()=>group().chapters;
const current=()=>chapters()[Math.min(state.chapter,chapters().length-1)];
function movieTime(secs) {
 if(!Number.isFinite(secs))return "—";
 let n=Math.max(0,Math.floor(secs));
 const h=Math.floor(n/3600),m=Math.floor((n%3600)/60),s=n%60;
 const two=x=>String(x).padStart(2,"0");
 return h?two(h)+":"+two(m)+":"+two(s):two(m)+":"+two(s);
}
function updateURL() {
 const q=new URLSearchParams(location.search);
 q.set("offset",String(state.offset));q.set("method",state.method);
 if(state.view==="detail")q.set("chapter",String(state.chapter+1));
 else q.delete("chapter");
 history.replaceState(null,"",location.pathname+"?"+q.toString());
}
function toast(msg) {
 const box=$("#toast");box.textContent=msg;box.classList.add("show");
 clearTimeout(toastTimeout);
 toastTimeout=setTimeout(()=>box.classList.remove("show"),2400);
}
function renderFilters(){
 const select=$("#offsetSelector");
 select.innerHTML=DATA.offsets.map(n=>'<option value="'+n+'" '+(n===state.offset?"selected":"")+'>偏移 '+n+'s</option>').join("");
 document.querySelectorAll("[data-method]").forEach(el=>{
  const active=el.dataset.method===state.method;
  el.classList.toggle("active",active);el.setAttribute("aria-pressed",String(active));
 });
 $("#header-info").textContent=group().chapters.length+" 章 · "+group().mediaCount+" 张影像";
}
function timelineItem(ch,i) {
 return `<div class="timeline-entry ${i===state.chapter?"active":""}" data-timeline-index="${i}">
   <div class="time-marker" title="原片相对时间，并非拍摄钟点">${movieTime(ch.firstSourceSecond)}</div>
   <span class="time-dot"></span>
   <button class="timeline-link" type="button" data-open-chapter="${i}" aria-label="打开${esc(ch.title)}">
     <div class="timeline-photo" data-live-kind="timeline" data-live-asset="${esc(ch.photos[0].sourceAsset)}" data-live-focus-ms="${ch.photos[0].focusMs}">
       <img src="${esc(ch.photos[0].src)}" alt="${esc(ch.title)}" loading="${i<2?"eager":"lazy"}">
       <span class="tiny-count">${String(i+1).padStart(2,"0")} / ${String(chapters().length).padStart(2,"0")}</span>
       <span class="chapter-label">${esc(ch.title)}</span>
     </div>
     <p class="timeline-story">${esc(ch.story)}</p>
   </button>
 </div>`;
}
function renderTimeline() {
 $("#timeline-panel").innerHTML=`
   <div class="timeline-head">
     <div class="eyebrow">NEXLEAP ONE &nbsp;/&nbsp; LIFE JOURNAL</div>
     <h1>Tokyo<br>citywalk.</h1>
     <p class="desc">${esc(group().dayIntro)}</p>
     <div class="meta-line"><span>人工标注 · 真实图片范例</span><span class="meta-dot"></span><span>原片相对时间</span></div>
   </div>
   <div class="timeline-title-row"><h2>这一天的 Chapter</h2>
     <span class="timeline-count">${group().chapters.length} 章 · ${METHODS[state.method].sub}</span>
   </div>
   <div class="timeline-list">${chapters().map(timelineItem).join("")}</div>
   <p class="day-bottom">视频时间来自标注数据，不是拍摄日的真实时钟。<br>本仓库不包含对应10秒原视频，Live 暂不可用。</p>`;
}
function editorHTML(ch){
 if(state.editing)return `<div class="my-story-editor">
   <textarea id="my-story-text" aria-label="补充我的故事" placeholder="这个时刻，有什么想留下的？">${esc(notes[ch.id]||"")}</textarea>
   <div class="editor-actions">
      <button class="btn-small" id="save-story" type="button">保存</button>
      <button class="btn-small outline" id="cancel-story" type="button">取消</button>
   </div></div>`;
 return notes[ch.id]?`<div class="my-story-saved">${esc(notes[ch.id])}</div>`:
  '<p class="my-story-empty">记录一个人、一个细节，或这个时刻对你的意义。</p>';
}
function momentsHTML(ch){
 if(!ch.moments.length)return "";
 return `<section class="moment-sect">
   <div class="section-divider"></div>
   <h3 class="section-heading">值得记住的瞬间</h3>
   <p class="section-sub">来自人工标注的照片备注 · ${ch.moments.length} 条</p>
   <ol class="story-moment-list">${ch.moments.map((m,i)=>`
     <li class="moment-item"><span class="moment-index">${String(i+1).padStart(2,"0")}</span>
     <div><div class="moment-text">${esc(m.text)}</div>
       ${m.info?`<div class="moment-provenance">${esc(m.info)}</div>`:""}
       ${m.warning?`<div class="warning-line">${esc(m.warning)}</div>`:""}
     </div></li>`).join("")}</ol>
 </section>`;
}
function mediaTile(p,i){
 const valid=p.sourceAsset&&Number.isInteger(p.focusMs)&&p.focusMs>=0&&p.focusMs<10000;
 return `<article class="live-tile ${i===0?"is-hero":""}">
  <div style="position:relative">
    <button type="button" class="live-picture" data-photo-index="${i}" ${valid?`data-live-kind="gallery" data-live-asset="${esc(p.sourceAsset)}" data-live-focus-ms="${p.focusMs}"`:""}
      ${valid?`aria-label="播放第${i+1}张照片的三秒Live"`:'aria-label="放大查看真实标注照片"'} >
      <img src="${esc(p.src)}" loading="${i<2?"eager":"lazy"}" alt="${esc(p.caption)}">
      <span class="live-pill">${valid?"LIVE":"PHOTO"}</span>
    </button>
    <button type="button" class="tile-share" data-share-photo="${i}" aria-label="复制照片本地链接">${svg("share",19)}</button>
  </div>
  <figcaption>${esc(p.caption)}</figcaption>
  <div class="tile-meta-row"><span>#${String(i+1).padStart(2,"0")}</span><span>·</span>
    <span>原片 ${movieTime(p.originalSecond)}</span></div>
 </article>`;
}
function renderDetail(){
 const ch=current();
 if(!ch){$("#detail-zone").innerHTML='<div class="empty-main"><div class="empty-inner"><h3>没有 Chapter</h3></div></div>';return}
 const first=ch.photos[0],saved=!!favorites[ch.id],next=chapters()[(state.chapter+1)%chapters().length];
 $("#detail-zone").innerHTML=`<article class="detail-sheet" data-chapter-id="${esc(ch.id)}">
   <div class="hero-media" data-live-kind="hero" data-live-asset="${esc(first.sourceAsset)}" data-live-focus-ms="${first.focusMs}">
     <img src="${esc(first.src)}" alt="${esc(ch.title)}" fetchpriority="high">
     <div class="hero-top-controls">
       <button type="button" class="circle-control" id="back-to-day" aria-label="返回 Day 时间线">${svg("back")}</button>
       <button type="button" class="circle-control favorite ${saved?"is-fav":""}" id="favorite-chapter"
         aria-pressed="${saved}" aria-label="${saved?"取消收藏":"收藏"}这个Chapter">${svg("star",24)}</button>
     </div>
     <button type="button" id="play-hero" class="hero-live">${svg("play",18)} &nbsp; PHOTO · 查看照片</button>
     <div class="hero-brand">Nexleap one</div>
   </div>
   <div class="detail-copy">
     <div class="chapter-number">CHAPTER ${String(state.chapter+1).padStart(2,"0")} / ${String(chapters().length).padStart(2,"0")}</div>
     <h2>${esc(ch.title)}</h2>
     <div class="detail-sub"><span>东京 Citywalk</span><span>·</span>
       <span>原片 ${movieTime(ch.firstSourceSecond)}</span><span>·</span>
       <span>${ch.photos.length} 张照片</span></div>
     <div class="tag-row"><span class="tag">Citywalk</span>
       <span class="tag">${esc(METHODS[state.method].tag)}</span>
       <span class="tag soft">${state.offset}s 偏移</span></div>
     <p class="story-copy">${esc(ch.story)}</p>
     <div class="section-divider"></div>
     <section class="my-story">
       <div class="my-story-header"><h3 class="section-heading">My story</h3>
         <button type="button" class="text-action" id="edit-story">${notes[ch.id]?"编辑":"＋ 添加"}</button></div>
       ${editorHTML(ch)}
     </section>
     ${momentsHTML(ch)}
     <section class="media-sect" id="chapter-photos">
       <div class="my-story-header"><h3 class="section-heading">影像里的片刻</h3>
         <span class="media-count">${ch.photos.length} PHOTOS · 终选</span></div>
       <p class="section-sub">这些照片保留人工终选状态和原始备注。点击查看大图，右上角可复制链接。</p>
       <div class="media-grid">${ch.photos.map(mediaTile).join("")}</div>
     </section>
     <footer class="chapter-footer">
       <div><div class="next-text">下一段故事</div>
         <div style="font-weight:750;margin-top:5px;font-size:15px">${esc(next.title)}</div></div>
       <button type="button" class="next-button" id="next-chapter">下一章 ${svg("next",16)}</button>
     </footer>
   </div>
 </article>`;
 document.dispatchEvent(new Event("nexleap:rendered"));
}
function refresh(){
 state.chapter=Math.max(0,Math.min(state.chapter,chapters().length-1));
 renderFilters();renderTimeline();renderDetail();updateURL();
 document.body.classList.toggle("detail-mode",state.view==="detail");
 document.querySelectorAll(".nav-button").forEach(b=>b.classList.toggle("active",b.dataset.nav===state.view));
}
function context(offset,method) {
 if(!DATA.offsets.includes(offset)||!METHODS[method])return;
 closeLive();state.offset=offset;state.method=method;state.chapter=0;
 state.view="day";state.editing=false;refresh();window.scrollTo(0,0);
}
function selectChapter(i) {
 if(!chapters()[i])return;
 closeLive();state.chapter=i;state.view="detail";state.editing=false;
 refresh();window.scrollTo(0,0);
}
function goDay(){
 closeLive();state.view="day";state.editing=false;refresh();window.scrollTo(0,0);
}
function next(){selectChapter((state.chapter+1)%chapters().length)}
function copy(text,message){
 if(navigator.clipboard?.writeText){
  navigator.clipboard.writeText(text).then(()=>toast(message),()=>fallback(text,message));
 }else fallback(text,message);
}
function fallback(text,message){
 const t=document.createElement("textarea");t.value=text;t.style.position="fixed";t.style.top="-9999px";
 document.body.append(t);t.select();const ok=document.execCommand("copy");t.remove();
 toast(ok?message:"复制失败，请手动复制地址");
}
function sharePhoto(index){
 const p=current()?.photos[index];
 if(p)copy(new URL(p.src,location.href).href,"已复制本地照片链接");
}
function stopLive(){
 const v=$("#liveVideo");if(v){v.pause();v.removeAttribute("src");v.load();}
}
function closeLive(){
 const d=$("#liveDialog");if(d?.open)d.close();stopLive();
 document.dispatchEvent(new Event("nexleap:modal-close"));
}
function openLive(p){
 if(!p||!/^sydney_(01|02|03|05|06|07)_\d{6}$/.test(p.sourceAsset||"")||
     !Number.isInteger(p.focusMs)||p.focusMs<0||p.focusMs>=10000){
  toast("没有可验证的原视频来源或时间");return;
 }
 stopLive();
 const dialog=$("#liveDialog"),v=$("#liveVideo");
 $("#playerStatus").textContent="正在从原始视频生成三秒 Live；首次播放会在 Mac 本地缓存…";
 $("#playerCaption").textContent=p.caption+" · 原片 "+movieTime(p.originalSecond);
 dialog.showModal();
 document.dispatchEvent(new Event("nexleap:modal-open"));
 const host=location.protocol==="file:"?"http://127.0.0.1:8810":location.origin;
 v.src=host+"/api/live3s/"+encodeURIComponent(p.sourceAsset)+"/"+p.focusMs+".mp4";
 v.load();
}
document.addEventListener("click",e=>{
 const n=e.target.closest("[data-open-chapter]");
 if(n){selectChapter(Number(n.dataset.openChapter));return;}
 const photo=e.target.closest("[data-photo-index]");
 if(photo){openLive(current().photos[Number(photo.dataset.photoIndex)]);return;}
 const share=e.target.closest("[data-share-photo]");
 if(share){sharePhoto(Number(share.dataset.sharePhoto));return;}
 if(e.target.closest("#play-hero")){openLive(current()?.photos[0]);return;}
 if(e.target.closest("#back-to-day")){goDay();return;}
 if(e.target.closest("#next-chapter")){next();return;}
 if(e.target.closest("#favorite-chapter")){
  const ch=current();favorites[ch.id]=!favorites[ch.id];
  localStorage.setItem("nexleapOneExamplesFavoritesV1",JSON.stringify(favorites));
  renderDetail();toast(favorites[ch.id]?"已收藏":"已取消收藏");return;
 }
 if(e.target.closest("#edit-story")){
  state.editing=true;renderDetail();$("#my-story-text")?.focus();return;
 }
 if(e.target.closest("#cancel-story")){state.editing=false;renderDetail();return;}
 if(e.target.closest("#save-story")){
  notes[current().id]=($("#my-story-text")?.value||"").trim().slice(0,4000);
  localStorage.setItem("nexleapOneExamplesStoriesV1",JSON.stringify(notes));
  state.editing=false;renderDetail();toast("我的故事已保存到本机浏览器");return;
 }
 if(e.target.closest("#copy-chapter-link")){
  const q=new URLSearchParams(location.search);
  q.set("chapter",state.chapter+1);
  copy(location.origin+location.pathname+"?"+q,"已复制 Chapter 本地链接");
 }
});
document.querySelectorAll("[data-method]").forEach(btn=>
 btn.addEventListener("click",()=>context(state.offset,btn.dataset.method)));
$("#offsetSelector").addEventListener("change",e=>context(Number(e.target.value),state.method));
document.querySelectorAll(".nav-button").forEach(btn=>
 btn.addEventListener("click",()=>{
  if(btn.dataset.nav==="day")goDay();
  else{state.view="detail";refresh();window.scrollTo(0,0);}
 }));
$("#playerClose").addEventListener("click",closeLive);
$("#liveDialog").addEventListener("close",()=>{
 stopLive();
 document.dispatchEvent(new Event("nexleap:modal-close"));
});
$("#liveDialog").addEventListener("click",e=>{if(e.target===e.currentTarget)closeLive()});
$("#playerToggle").addEventListener("click",()=>{
 const v=$("#liveVideo");if(!v.src)return;
 if(v.paused)v.play().catch(()=>toast("可点击视频继续播放"));
 else v.pause();
});
$("#liveVideo").addEventListener("loadedmetadata",()=>{
 if(!$("#liveDialog").open)return;
 $("#playerStatus").textContent="正在循环播放原始三秒 Live";
 $("#liveVideo").play().catch(()=>$("#playerStatus").textContent="视频已加载，请点击播放");
});
$("#liveVideo").addEventListener("error",()=>{
 if($("#liveDialog").open)$("#playerStatus").textContent="视频无法载入，请检查 Mac 预览服务 127.0.0.1:8810";
});
document.addEventListener("keydown",e=>{
 if(e.key==="Escape"&&$("#liveDialog").open){closeLive();return}
 if(e.target.matches("input,textarea,select"))return;
 if(e.key==="ArrowRight")next();
 if(e.key==="ArrowLeft")goDay();
});
refresh();
window.__nexleapOne={DATA,state,selectChapter,openLive,goDay,context};
})();
