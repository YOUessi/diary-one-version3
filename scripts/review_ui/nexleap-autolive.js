/* Nexleap One: viewport-driven 3-second Motion auto-play.
 * One real video node is shared by the visible Day/Chapter/gallery item.
 * Offscreen photos remain static. Server renders 3s MP4 from the original
 * local 10s video on demand; no model calls or video uploads.
 */
"use strict";
(() => {
  const ASSET = /^sydney_(?:01|02|03|05|06|07)_\d{6}$/;
  const player = document.createElement("video");
  player.className = "auto-live-video";
  player.setAttribute("aria-hidden", "true");
  player.muted = true;
  player.defaultMuted = true;
  player.autoplay = true;
  player.loop = true;
  player.playsInline = true;
  player.setAttribute("playsinline", "");
  player.setAttribute("webkit-playsinline", "");
  player.preload = "metadata";
  player.disablePictureInPicture = true;
  player.controls = false;

  let current = null;
  let currentKey = "";
  let observer = null;
  let candidates = [];
  let pendingFrame = 0;
  let suspended = false;
  let starts = 0;
  const serverBase = location.protocol === "file:"
    ? "http://127.0.0.1:8810" : location.origin;

  function mediaKey(el) {
    if (!el) return "";
    const asset = el.dataset.liveAsset;
    const focus = Number(el.dataset.liveFocusMs);
    if (!ASSET.test(asset || "") ||
        !Number.isInteger(focus) || focus < 0 || focus >= 10000) return "";
    return asset + "/" + focus;
  }

  function visibility(el) {
    const rect = el.getBoundingClientRect();
    if (rect.width < 12 || rect.height < 12) return 0;
    const header = document.querySelector(".app-top");
    const startY = Math.max(0, (header ? header.getBoundingClientRect().bottom : 0) + 2);
    const bottomNav = document.querySelector(".mobile-nav");
    const bottomHeight = bottomNav &&
      getComputedStyle(bottomNav).display !== "none"
      ? Math.max(0, innerHeight - bottomNav.getBoundingClientRect().top) : 0;
    const endY = innerHeight - bottomHeight - 3;
    if (startY >= endY) return 0;
    const visibleHeight = Math.max(0, Math.min(rect.bottom, endY) - Math.max(rect.top, startY));
    const visibleWidth = Math.max(0, Math.min(rect.right, innerWidth) - Math.max(rect.left, 0));
    return (visibleHeight / rect.height) * (visibleWidth / rect.width);
  }

  function pause({clear = false} = {}) {
    player.pause();
    player.classList.remove("is-playing");
    if (current) current.classList.remove("auto-live-active");
    if (clear) {
      current = null;
      currentKey = "";
      player.removeAttribute("src");
      player.load();
      player.remove();
    }
  }

  function playIfReady() {
    if (!current || suspended || document.hidden ||
        document.querySelector("#liveDialog")?.open ||
        visibility(current) < .3) {
      pause();
      return;
    }
    player.muted = true;
    const promise = player.play();
    if (promise && typeof promise.catch === "function") {
      promise.catch(() => {
        // Autoplay can be denied by browser power policy; show real poster.
        player.classList.remove("is-playing");
      });
    }
  }

  function setActive(el) {
    if (el === current && currentKey === mediaKey(el)) {
      el.classList.add("auto-live-active");
      if (player.paused) playIfReady();
      return;
    }
    const key = mediaKey(el);
    if (!key) {
      pause({clear:true});
      return;
    }
    const prev = currentKey;
    pause();
    current = el;
    currentKey = key;
    el.classList.add("auto-live-active");
    el.appendChild(player);
    player.classList.remove("is-playing");
    if (key !== prev) {
      player.src = serverBase + "/api/live3s/" + key + ".mp4";
      player.load();
      starts += 1;
    }
    playIfReady();
  }

  function choose() {
    pendingFrame = 0;
    if (suspended || document.hidden || document.querySelector("#liveDialog")?.open) {
      pause();
      return;
    }
    let best = null;
    let bestScore = -Infinity;
    for (const el of candidates) {
      if (!el.isConnected) continue;
      const fraction = visibility(el);
      const kind = el.dataset.liveKind;
      const threshold = kind === "gallery" ? .32 : .38;
      if (fraction < threshold) continue;
      const priority = kind === "hero" ? 180 : kind === "gallery" ? 130 : 75;
      const rect = el.getBoundingClientRect();
      const center = (rect.top + rect.bottom) / 2;
      const centering = 1 - Math.min(Math.abs(center - innerHeight / 2) / innerHeight, 1);
      const score = priority + fraction * 25 + centering * 8;
      if (score > bestScore) {
        bestScore = score;
        best = el;
      }
    }
    if (best) setActive(best);
    else pause({clear:true});
  }

  function schedule() {
    if (!pendingFrame) pendingFrame = requestAnimationFrame(choose);
  }

  function refresh() {
    if (observer) observer.disconnect();
    pause({clear:true});
    candidates = Array.from(document.querySelectorAll("[data-live-kind]"))
      .filter(node => !!mediaKey(node));
    if ("IntersectionObserver" in window) {
      observer = new IntersectionObserver(schedule, {
        threshold: [0, .15, .32, .4, .55, .75, 1],
        rootMargin: "0px"
      });
      for (const c of candidates) observer.observe(c);
    }
    schedule();
  }

  player.addEventListener("playing", () => {
    if (!current || !current.isConnected || suspended || document.hidden ||
        visibility(current) < .3) {
      pause();
      return;
    }
    player.classList.add("is-playing");
  });
  player.addEventListener("loadedmetadata", playIfReady);
  player.addEventListener("error", () => {
    player.classList.remove("is-playing");
  });

  document.addEventListener("nexleap:rendered", refresh);
  document.addEventListener("nexleap:modal-open", () => {
    suspended = true;
    pause();
  });
  document.addEventListener("nexleap:modal-close", () => {
    suspended = false;
    schedule();
  });
  document.addEventListener("visibilitychange", schedule);
  window.addEventListener("scroll", schedule, {passive:true});
  window.addEventListener("resize", schedule, {passive:true});
  window.addEventListener("orientationchange", schedule, {passive:true});

  window.__nexleapAutoLive = {
    get activeKind() {return current?.dataset.liveKind || null;},
    get activeAsset() {return current?.dataset.liveAsset || null;},
    get activeFocusMs() {return current ? Number(current.dataset.liveFocusMs) : null;},
    get playing() {return !player.paused && player.readyState >= 2;},
    get currentTime() {return player.currentTime;},
    get duration() {return player.duration;},
    get createdVideoElements() {return document.querySelectorAll(".auto-live-video").length;},
    get starts() {return starts;},
    refresh,
    pause:() => pause({clear:true}),
    get candidateCount() {return candidates.length;}
  };
  refresh();
})();