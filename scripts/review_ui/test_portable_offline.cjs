#!/usr/bin/env node
"use strict";
const puppeteer=require("/Users/youtang/.local/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer");
const fs=require("fs");
const root=process.env.NEXLEAP_OFFLINE_ROOT || "/Users/youtang/Documents/Nexleap/work_logs/evidence/Nexleap_One_Sydney_Portable_Share_20261109/Nexleap_One_Sydney";
(async()=>{
 const browser=await puppeteer.launch({
  executablePath:"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless:true,args:["--no-sandbox"]
 });
 try {
  const page=await browser.newPage();
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true});
  const remote=[];
  const bad=[];
  await page.setRequestInterception(true);
  page.on("request",request=>{
    if(/^https?:/i.test(request.url())){
      remote.push(request.url());
      request.abort("blockedbyclient");
    } else request.continue();
  });
  page.on("pageerror",x=>bad.push(x.message));
  await page.goto("file://"+root+"/index.html",{waitUntil:"domcontentloaded",timeout:60000});
  await page.waitForFunction(()=>window.__nexleapAutoLive &&
    window.__nexleapAutoLive.playing &&
    window.__nexleapAutoLive.activeKind==="timeline",{timeout:40000});
  const day=await page.evaluate(()=>{
   const x=window.__nexleapOne.DATA,a=window.__nexleapAutoLive;
   return {source:document.querySelector(".auto-live-video").currentSrc,
     groups:x.offsets.length,chapters:Object.values(x.groups).flatMap(g=>Object.values(g).map(r=>r.chapters.length)).reduce((a,b)=>a+b,0),
     media:Object.values(x.groups).flatMap(g=>Object.values(g).map(r=>r.mediaCount)).reduce((a,b)=>a+b,0),
     duration:a.duration,muted:document.querySelector(".auto-live-video").muted,
     playing:a.playing,clientOnly:location.protocol==="file:"};
  });
  console.log("OFFLINE_DAY",JSON.stringify(day));
  if(day.groups!==6 || day.chapters!==129 || day.media!==701 || !day.playing ||
     Math.abs(day.duration-3)>.1 || !day.muted || !day.clientOnly)
    throw Error("Offline Day failed");
  await page.evaluate(()=>window.__nexleapOne.selectChapter(0));
  await page.waitForFunction(()=>window.__nexleapAutoLive.playing &&
    window.__nexleapAutoLive.activeKind==="hero",{timeout:30000});
  await page.evaluate(()=>document.querySelector(".live-picture").scrollIntoView({block:"center",behavior:"instant"}));
  await page.waitForFunction(()=>window.__nexleapAutoLive.playing &&
    window.__nexleapAutoLive.activeKind==="gallery",{timeout:30000});
  console.log("OFFLINE_GALLERY_LIVE",await page.evaluate(()=>({
    kind:window.__nexleapAutoLive.activeKind,
    source:document.querySelector(".auto-live-video").currentSrc,
    videoCount:document.querySelectorAll(".auto-live-video").length
  })));
  await page.screenshot({path:root+"/../OFFLINE_PORTABLE_MOBILE.png",fullPage:false});
  if(remote.length)throw Error("Portable page attempted network calls "+remote.slice(0,4));
  if(bad.length)throw Error("JavaScript errors "+bad.slice(0,4));
  console.log("OFFLINE_PORTABLE_E2E_PASS_NO_NETWORK_REQUIRED");
 }finally{await browser.close()}
})().catch(e=>{console.error("OFFLINE_PORTABLE_E2E_FAIL",e.stack||e);process.exit(1)});
