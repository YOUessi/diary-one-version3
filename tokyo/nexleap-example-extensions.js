/* Static-photo, human-labeled Chapter review enhancements.
 * No fake Live: click real JPG to zoom; optionally inspect candidates.
 */
"use strict";
(() => {
  const esc=s=>String(s??"").replace(/[&<>"']/g,x=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x]));
  const get=()=>window.__nexleapOne;
  const current=()=>{
    const app=get();
    if(!app)return null;
    return app.DATA.groups[String(app.state.offset)].jpeg.chapters[app.state.chapter]||null;
  };
  const dlg=document.createElement("dialog");
  dlg.className="example-photo-dialog";
  dlg.id="example-photo-dialog";
  const top=document.createElement("div");top.className="example-photo-header";
  const caption=document.createElement("div");caption.className="example-photo-title";
  caption.textContent="Nexleap One · 标注照片";
  const close=document.createElement("button");close.className="example-photo-close";
  close.type="button";close.textContent="✕ 关闭";
  top.append(caption,close);
  const image=document.createElement("img");image.className="example-photo-full";
  image.alt="真实标注照片的大图预览";
  const note=document.createElement("p");note.className="example-photo-note";
  const provenance=document.createElement("p");provenance.className="example-photo-meta";
  dlg.append(top,image,note,provenance);
  document.body.append(dlg);

  function open(im){
    if(!im||!im.src)return;
    image.src=im.src;
    note.textContent=im.caption||"该图片暂无标注备注";
    provenance.textContent=[im.status||"终选",im.time||"",im.group||""].filter(Boolean).join(" · ");
    dlg.showModal();
  }
  function shut(){if(dlg.open)dlg.close();image.removeAttribute("src")}
  close.addEventListener("click",shut);
  dlg.addEventListener("close",()=>image.removeAttribute("src"));
  dlg.addEventListener("click",e=>{if(e.target===dlg)shut()});

  const byStatus=["候选","未选","排除"];
  function buildExtraSection(){
    const ch=current();const section=document.querySelector(".media-sect");
    if(!ch||!section || section.querySelector(".example-extra"))return;
    const extra=document.createElement("details");extra.className="example-extra";
    const summary=document.createElement("summary");
    summary.textContent="查看候选与未选图片（"+ch.extraPhotos.length+" 张）";
    const intro=document.createElement("p");
    intro.textContent="这些是人工标注数据中的候选、未选和排除状态，不属于最终精选 Chapter 图库。";
    intro.className="example-extra-intro";
    const stats=document.createElement("div");stats.className="example-extra-stats";
    for(const name of ["终选","候选","未选","排除"]){
      const b=document.createElement("span");b.textContent=name+" "+(ch.stats[name]||0);
      if(name==="终选")b.className="emphasis";
      stats.append(b);
    }
    const buttons=document.createElement("div");buttons.className="example-extra-buttons";
    const grid=document.createElement("div");grid.className="example-extra-grid";
    let selected="候选";
    const render=()=>{
      grid.replaceChildren();
      const photos=selected==="全部"?ch.extraPhotos:
        ch.extraPhotos.filter(x=>x.status===selected);
      for(const im of photos){
        const figure=document.createElement("article");figure.className="example-extra-tile";
        const thumb=document.createElement("button");thumb.type="button";
        thumb.className="example-extra-photo";
        thumb.setAttribute("aria-label","放大图片");
        const pic=document.createElement("img");pic.loading="lazy";pic.src=im.src;
        pic.alt=im.caption||"实际源图片";
        thumb.append(pic);
        thumb.addEventListener("click",()=>open(im));
        const text=document.createElement("div");text.className="example-extra-caption";
        text.textContent=(im.caption||"无备注")+" · "+(im.time||"")+" · "+im.status;
        figure.append(thumb,text);grid.append(figure);
      }
      if(!photos.length){
        const empty=document.createElement("p");
        empty.textContent="没有这一状态的图片。";grid.append(empty);
      }
      Array.from(buttons.children).forEach(b=>b.classList.toggle("active",b.dataset.status===selected));
    };
    for(const name of [...byStatus,"全部"]){
      const b=document.createElement("button");b.type="button";b.className="example-extra-filter";
      b.textContent=name;b.dataset.status=name;
      b.addEventListener("click",()=>{selected=name;render()});
      buttons.append(b);
    }
    extra.append(summary,intro,stats,buttons,grid);
    extra.addEventListener("toggle",()=>{if(extra.open)render()});
    section.append(extra);
  }

  document.addEventListener("click",e=>{
    const chosen=e.target.closest("[data-photo-index]");
    const hero=e.target.closest("#play-hero");
    if(chosen || hero){
      const ch=current();
      if(!ch)return;
      e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
      const idx=chosen?Number(chosen.dataset.photoIndex):0;
      open(ch.photos[idx]);
    }
  },true);
  document.addEventListener("nexleap:rendered",buildExtraSection);
  buildExtraSection();
  window.__nexleapExampleExtras={open,close:shut,buildExtraSection};
})();