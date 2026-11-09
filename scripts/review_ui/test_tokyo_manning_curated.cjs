#!/usr/bin/env node
"use strict";
const puppeteer=require("/Users/youtang/.local/lib/node_modules/@wonderwhy-er/desktop-commander/node_modules/puppeteer");
const BASE=process.env.NEXLEAP_REVIEW_BASE||"http://127.0.0.1:8815/";
const OUT="/Users/youtang/Documents/Nexleap/work_logs/evidence/nexleap-tokyo-manning-share-20261109";
async function run(){
 const browser=await puppeteer.launch({
   executablePath:"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
   headless:true,args:["--no-sandbox","--disable-background-timer-throttling"]
 });
 try {
  const page=await browser.newPage();
  const errors=[];
  page.on("pageerror",e=>errors.push("JS "+e.message));
  page.on("response",r=>{if(r.status()>=400)errors.push("HTTP "+r.status()+" "+r.url().slice(0,120))});
  await page.setViewport({width:1360,height:900});
  await page.goto(BASE+"tokyo/index.html",{waitUntil:"networkidle2",timeout:50000});
  await page.waitForFunction(()=>window.__nexleapOne && window.__nexleapExampleExtras,{timeout:10000});
  const first=await page.evaluate(()=>{
    const x=window.__nexleapOne;
    return {city:"tokyo",offsets:x.DATA.offsets,chapters:x.DATA.groups["0"].jpeg.chapters.length,
      selected:x.DATA.groups["0"].jpeg.mediaCount,mediaAll:x.DATA.groups["0"].jpeg.allImageCount,
      timeline:document.querySelectorAll(".timeline-entry").length,
      loaded:document.querySelectorAll(".timeline-photo img").length,
      firstTitle:document.querySelector(".timeline-photo .chapter-label").textContent};
  });
  console.log("TOKYO_DATA",JSON.stringify(first));
  if(first.chapters!==6||first.selected!==47||first.mediaAll!==165||first.timeline!==6)throw Error("Tokyo data mismatch");
  await page.screenshot({path:OUT+"/TOKYO_DESKTOP_DAY.png",fullPage:false});
  await page.evaluate(()=>window.__nexleapOne.selectChapter(1));
  const second=await page.evaluate(()=>({
    chTitle:document.querySelector(".detail-copy h2").textContent,
    story:document.querySelector(".story-copy").textContent,
    selectedImages:document.querySelectorAll(".live-picture").length,
    imageDisabled:document.querySelector(".live-picture").disabled,
    review:document.querySelector(".example-extra>summary")?.textContent
  }));
  console.log("TOKYO_CHAPTER_2",JSON.stringify(second));
  if(second.selectedImages!==7||second.imageDisabled||!second.review)throw Error("Tokyo Chapter details wrong");
  await page.click(".live-picture");
  await page.waitForFunction(()=>document.querySelector("#example-photo-dialog").open);
  await page.click(".example-photo-close");
  await page.$eval(".example-extra",e=>e.open=true);
  await page.waitForSelector(".example-extra-grid .example-extra-tile");
  const extraCount=await page.$$eval(".example-extra-grid .example-extra-tile",a=>a.length);
  console.log("TOKYO_CANDIDATES",extraCount);
  if(extraCount<=0)throw Error("Tokyo candidate gallery missing");
  await page.screenshot({path:OUT+"/TOKYO_DESKTOP_CHAPTER.png",fullPage:false});
  await page.close();

  const mob=await browser.newPage();
  const errorsM=[];
  mob.on("pageerror",e=>errorsM.push(e.message));
  await mob.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
  await mob.goto(BASE+"manning-park/index.html",{waitUntil:"networkidle2",timeout:50000});
  await mob.waitForFunction(()=>window.__nexleapOne && window.__nexleapExampleExtras,{timeout:10000});
  const man=await mob.evaluate(()=>{
    const x=window.__nexleapOne;
    return {offs:x.DATA.offsets,groups:[0,10,20].map(o=>{
      const g=x.DATA.groups[String(o)].jpeg;
      return {offset:o,ch:g.chapters.length,selected:g.mediaCount,images:g.allImageCount};
    }),
    horizontal:document.documentElement.scrollWidth>innerWidth+3};
  });
  console.log("MANNING_DATA",JSON.stringify(man));
  if(man.horizontal||JSON.stringify(man.groups.map(x=>[x.ch,x.selected,x.images]))!==
      JSON.stringify([[1,16,162],[1,17,157],[1,16,159]]))throw Error("Manning data wrong");
  await mob.screenshot({path:OUT+"/MANNING_MOBILE_DAY.png",fullPage:false});
  await mob.click('[data-open-chapter="0"]');
  await mob.waitForFunction(()=>document.body.classList.contains("detail-mode"));
  const chapter=await mob.evaluate(()=>({
    title:document.querySelector(".detail-copy h2").textContent,
    story:document.querySelector(".story-copy").textContent.length,
    photos:document.querySelectorAll(".live-picture").length,
    hasExtras:!!document.querySelector(".example-extra"),
    horizontal:document.documentElement.scrollWidth>innerWidth+3}));
  console.log("MANNING_CHAPTER",JSON.stringify(chapter));
  if(chapter.photos!==16||chapter.story<20||!chapter.hasExtras||chapter.horizontal)throw Error("Manning Chapter wrong");
  await mob.screenshot({path:OUT+"/MANNING_MOBILE_CHAPTER.png",fullPage:false});
  await mob.select("#offsetSelector","10");
  const offset10=await mob.evaluate(()=>({offset:window.__nexleapOne.state.offset,
     chapters:window.__nexleapOne.DATA.groups["10"].jpeg.chapters.length,
     final:window.__nexleapOne.DATA.groups["10"].jpeg.mediaCount}));
  console.log("MANNING_OFFSET_SWITCH",JSON.stringify(offset10));
  if(offset10.offset!==10||offset10.final!==17)throw Error("Manning offset switch failed");
  await mob.click('[data-open-chapter="0"]');
  await mob.$eval(".live-picture",x=>x.click());
  await mob.waitForFunction(()=>document.querySelector("#example-photo-dialog").open);
  await mob.screenshot({path:OUT+"/MANNING_MOBILE_PHOTO.png",fullPage:false});
  await mob.click(".example-photo-close");
  if(errors.length||errorsM.length)throw Error("Browser errors "+JSON.stringify([...errors,...errorsM].slice(0,8)));
  console.log("TOKYO_MANNING_CURATED_UI_E2E_PASS");
 }finally{await browser.close()}
}
run().catch(e=>{console.error("CURATED_UI_E2E_FAILED",e.stack||e);process.exit(1)});
