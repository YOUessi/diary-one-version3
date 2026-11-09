#!/usr/bin/env node
"use strict";
const puppeteer = require("/Users/youtang/.local/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer");
const URL = "http://127.0.0.1:8810/";
const OUT = "/Users/youtang/Documents/Nexleap/work_logs/evidence/sydney-six-offset-image-vs-video-20261109";
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

async function expectPlaying(page,kind,tag) {
  await page.waitForFunction(k=>{
    const x=window.__nexleapAutoLive;
    return x && x.playing && x.activeKind===k && Math.abs(x.duration-3)<.08;
  },{timeout:60000},kind);
  const result=await page.evaluate(()=>{
    const x=window.__nexleapAutoLive;
    const el=document.querySelector(".auto-live-video");
    return {kind:x.activeKind,asset:x.activeAsset,focus:x.activeFocusMs,
      playing:x.playing,time:+x.currentTime.toFixed(3),duration:x.duration,
      count:x.createdVideoElements,candidates:x.candidateCount,starts:x.starts,
      muted:el.muted,loop:el.loop,autoplay:el.autoplay,src:el.currentSrc};
  });
  if(result.count!==1||!result.muted||!result.loop||!result.autoplay)
    throw Error("Autoplay properties violated "+JSON.stringify(result));
  console.log("AUTOPLAY_PASS",tag,JSON.stringify(result));
  return result;
}

async function main() {
  // Deliberately do not bypass browser autoplay policies.
  // Muted autoplay must work in an ordinary browser configuration.
  const browser=await puppeteer.launch({
    executablePath:"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless:true,args:["--no-sandbox","--disable-background-timer-throttling"]
  });
  try {
    const desktop=await browser.newPage();
    desktop.on("pageerror",err=>console.log("DESKTOP_ERROR",err.message));
    await desktop.setViewport({width:1440,height:900,deviceScaleFactor:1});
    await desktop.goto(URL,{waitUntil:"domcontentloaded",timeout:45000});
    await expectPlaying(desktop,"hero","desktop-initial-hero");
    await desktop.screenshot({path:OUT+"/AUTOPLAY_DESKTOP_HERO.png",fullPage:false});
    await desktop.evaluate(()=>window.__nexleapOne.selectChapter(1));
    await expectPlaying(desktop,"hero","desktop-chapter-switch");
    await desktop.evaluate(()=>document.querySelector(".live-picture").scrollIntoView({block:"center",behavior:"instant"}));
    await expectPlaying(desktop,"gallery","desktop-gallery-on-scroll");
    await desktop.screenshot({path:OUT+"/AUTOPLAY_DESKTOP_GALLERY.png",fullPage:false});
    await desktop.close();

    const mobile=await browser.newPage();
    mobile.on("pageerror",err=>console.log("MOBILE_ERROR",err.message));
    await mobile.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
    await mobile.goto(URL,{waitUntil:"domcontentloaded",timeout:45000});
    await expectPlaying(mobile,"timeline","mobile-day-autoplay-without-click");
    await mobile.screenshot({path:OUT+"/AUTOPLAY_MOBILE_DAY.png",fullPage:false});
    await mobile.click('[data-open-chapter="0"]');
    await expectPlaying(mobile,"hero","mobile-chapter-hero-autoplay");
    await mobile.screenshot({path:OUT+"/AUTOPLAY_MOBILE_HERO.png",fullPage:false});
    await mobile.evaluate(()=>document.querySelector(".live-picture").scrollIntoView({block:"center",behavior:"instant"}));
    await expectPlaying(mobile,"gallery","mobile-gallery-autoplay-when-visible");
    const gallery=await mobile.evaluate(()=>window.__nexleapAutoLive.activeAsset);
    await mobile.screenshot({path:OUT+"/AUTOPLAY_MOBILE_GALLERY.png",fullPage:false});
    await mobile.evaluate(()=>document.querySelectorAll(".live-picture")[2].scrollIntoView({block:"center",behavior:"instant"}));
    await mobile.waitForFunction(prev=>window.__nexleapAutoLive.playing &&
      window.__nexleapAutoLive.activeKind==="gallery" &&
      window.__nexleapAutoLive.activeAsset!==prev,
      {timeout:60000},gallery);
    console.log("AUTOPLAY_PASS mobile-scroll-next-source",await mobile.evaluate(()=>({
      asset:window.__nexleapAutoLive.activeAsset,
      count:window.__nexleapAutoLive.createdVideoElements,
      time:window.__nexleapAutoLive.currentTime})));
    // Model's real 3s looping is verified by two rounds of the same clock.
    const times=await mobile.evaluate(async()=>{
      const video=document.querySelector(".auto-live-video");
      const output=[];
      for(let i=0;i<24;i++){
        await new Promise(resolve=>setTimeout(resolve,220));
        output.push(video.currentTime);
      }
      return output;
    });
    const min=Math.min(...times),max=Math.max(...times),loops=times.some((t,i)=>i>0&&t<times[i-1]-1.4);
    if(!loops || max>3.08 || min<0)throw Error("3s autoplay loop failed "+JSON.stringify({min,max,times}));
    console.log("AUTOPLAY_3S_LOOP_PASS",JSON.stringify({min,max,loops}));
    // Expanding for an optional full-screen view pauses inline and closing resumes.
    await mobile.evaluate(()=>document.querySelector(".live-picture").click());
    await mobile.waitForFunction(()=>document.querySelector("#liveDialog").open &&
      !window.__nexleapAutoLive.playing,{timeout:15000});
    await mobile.waitForFunction(()=>document.querySelector("#liveVideo").readyState>=2 &&
      document.querySelector("#liveVideo").duration<=3.08,{timeout:35000});
    await mobile.click("#playerClose");
    await expectPlaying(mobile,"gallery","mobile-auto-resumes-after-modal");
    await mobile.evaluate(()=>window.__nexleapOne.goDay());
    await expectPlaying(mobile,"timeline","mobile-auto-resumes-day");
    await mobile.select("#offsetSelector","50");
    await mobile.click('[data-method="video1"]');
    await expectPlaying(mobile,"timeline","mobile-switch-offset-and-video-model");
    console.log("AUTOPLAY_ALL_REGRESSIONS_PASS");
  }finally{await browser.close()}
}
main().catch(err=>{console.error("AUTOPLAY_TEST_FAILED",err.stack||err);process.exit(1)});
