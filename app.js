/* CJ2 Voice Emergency Checklist — demo app logic
 * Flow:
 *   HOME  : listen for an emergency name -> match a checklist trigger
 *   LIST  : speak each item, then listen for that item's completion word
 *           (item-specific advance words + universal fallbacks)
 *   branch items pick a sub-sequence based on the spoken keyword
 *
 * Uses the browser Web Speech API (SpeechRecognition + speechSynthesis).
 * DEMO / TRAINING ONLY.
 */
(function () {
  "use strict";

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const synth = window.speechSynthesis;

  // ---- DOM ----
  const $ = (s) => document.querySelector(s);
  const viewHome = $("#view-home");
  const viewList = $("#view-list");
  const heard = $("#heard");
  const micInd = $("#mic-indicator");
  const micLabel = $("#mic-label");
  const chips = $("#trigger-chips");
  const itemsEl = $("#items");
  const listTitle = $("#list-title");
  const listProgress = $("#list-progress");
  const advanceHint = $("#advance-hint");
  const btnPtt = $("#btn-ptt");
  const btnRepeat = $("#btn-repeat");
  const btnNext = $("#btn-next");
  const btnReset = $("#btn-reset");

  if (!SR) {
    $("#unsupported").classList.remove("hidden");
  }

  // ---- State ----
  let recog = null;
  let listening = false;
  let pttHeld = false;        // is the push-to-talk button currently held
  let mode = "home";          // "home" | "list"
  let active = null;          // active checklist object
  let sequence = [];          // current ordered items (with branch flattening)
  let idx = 0;                // current item index
  let finished = false;

  // ---- Speech recognition setup ----
  function makeRecognizer() {
    if (!SR) return null;
    const r = new SR();
    r.lang = "en-US";
    r.interimResults = true;
    r.continuous = true;
    r.maxAlternatives = 3;

    r.onstart = () => { listening = true; setMic("listening", "LISTENING"); btnPtt.classList.add("active"); };
    r.onend = () => {
      listening = false; btnPtt.classList.remove("active");
      // if the user is still holding PTT, keep the session alive
      if (pttHeld) { try { recog.start(); } catch (_){} return; }
      if (!synth.speaking) setMic("idle", "IDLE");
    };
    r.onerror = (e) => { showHeard("(" + (e.error || "mic error") + ")"); };
    r.onresult = (e) => {
      let interim = "", finalTxt = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i];
        const txt = res[0].transcript;
        if (res.isFinal) finalTxt += txt; else interim += txt;
      }
      if (interim) showHeard(interim, false);
      if (finalTxt) { showHeard(finalTxt, true); handleSpeech(finalTxt); }
    };
    return r;
  }

  function startListening() {
    if (!SR) return;
    if (!recog) recog = makeRecognizer();
    if (listening) return;
    try { recog.start(); } catch (_) { /* already started */ }
  }
  function stopListening() { if (recog && listening) { try { recog.stop(); } catch (_){} } }

  // ---- Text to speech ----
  function speak(text, after) {
    if (!synth) { if (after) after(); return; }
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US"; u.rate = 1.0; u.pitch = 1.0;
    // push-to-talk model: never auto-listen; the mic is only on while held
    stopListening();
    setMic("speaking", "SPEAKING");
    u.onend = () => {
      setMic("idle", "IDLE");
      if (after) after();
    };
    synth.speak(u);
  }

  // ---- UI helpers ----
  function setMic(cls, label) {
    micInd.className = "mic-indicator " + (cls === "idle" ? "" : cls);
    micLabel.textContent = label;
  }
  function showHeard(text, isFinal) {
    heard.innerHTML = isFinal ? "Heard: <b>" + escapeHtml(text) + "</b>" : "… " + escapeHtml(text);
  }
  function escapeHtml(s){return s.replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}
  function norm(s){return s.toLowerCase().replace(/[^a-z0-9 ]/g," ").replace(/\s+/g," ").trim();}

  // ---- HOME: build trigger chips ----
  function renderChips() {
    chips.innerHTML = "";
    CHECKLISTS.forEach((c) => {
      const chip = document.createElement("button");
      chip.className = "chip";
      chip.textContent = c.triggers[0];
      chip.onclick = () => selectChecklist(c);
      chips.appendChild(chip);
    });
  }

  // ---- Match spoken text to a checklist trigger ----
  function matchChecklist(text) {
    const t = norm(text);
    let best = null, bestLen = 0;
    for (const c of CHECKLISTS) {
      for (const trig of c.triggers) {
        const nt = norm(trig);
        if (t.includes(nt) && nt.length > bestLen) { best = c; bestLen = nt.length; }
      }
    }
    return best;
  }

  function selectChecklist(c) {
    active = c;
    sequence = c.items.slice();
    idx = 0; finished = false; mode = "list";
    viewHome.classList.remove("active");
    viewList.classList.add("active");
    listTitle.textContent = c.title;
    btnRepeat.disabled = false; btnNext.disabled = false;
    renderItems();
    presentCurrent();
  }

  function renderItems() {
    itemsEl.innerHTML = "";
    sequence.forEach((it, i) => {
      const div = document.createElement("div");
      div.className = "item" + (i < idx ? " done" : i === idx ? " current" : "");
      const say = advanceWords(it).slice(0, 3).join(", ");
      div.innerHTML =
        '<div class="num">' + (i + 1) + '</div>' +
        '<div class="body">' +
          '<div class="read">' + escapeHtml(it.read) + '</div>' +
          (it.action && it.action !== "BRANCH" ? '<div class="action">' + escapeHtml(it.action) + '</div>' : '') +
          '<div class="say">say to advance: <b>' + escapeHtml(say) + '</b></div>' +
        '</div>';
      itemsEl.appendChild(div);
    });
    const total = sequence.length;
    listProgress.textContent = finished ? "COMPLETE" : "STEP " + (idx + 1) + " OF " + total;
  }

  function advanceWords(it) {
    const base = (it.advance || []).slice();
    return base.concat(UNIVERSAL_ADVANCE);
  }

  function presentCurrent() {
    if (idx >= sequence.length) return finish();
    renderItems();
    const it = sequence[idx];
    const cur = itemsEl.children[idx];
    if (cur) cur.scrollIntoView({ behavior: "smooth", block: "center" });
    advanceHint.className = "advance-hint";
    advanceHint.textContent = it.action === "BRANCH"
      ? "Say one of the options to choose a path."
      : "When done, say a completion word (or tap Mark Complete).";
    speak(it.read, () => { /* recognition resumes via speak() */ });
  }

  // ---- Handle recognized speech depending on mode ----
  function handleSpeech(text) {
    const t = norm(text);
    // global reset by voice
    if (/\b(reset|start over|cancel)\b/.test(t)) { reset(); return; }

    if (mode === "home") {
      const c = matchChecklist(text);
      if (c) selectChecklist(c);
      return;
    }
    if (mode === "list") {
      if (finished) {
        if (/\b(reset|home|new|done)\b/.test(t)) reset();
        return;
      }
      const it = sequence[idx];
      // branch handling
      if (it.action === "BRANCH" && it.branch) {
        for (const key in it.branch) {
          if (t.includes(norm(key))) {
            const branchSeq = active.branches[it.branch[key]];
            // replace branch item with its sub-sequence
            sequence = sequence.slice(0, idx + 1).concat(branchSeq);
            advance();
            return;
          }
        }
        return; // no branch keyword matched yet, keep listening
      }
      // normal advance
      const words = advanceWords(it).map(norm);
      if (words.some((w) => w && t.includes(w))) advance();
    }
  }

  function advance() {
    idx++;
    if (idx >= sequence.length) return finish();
    presentCurrent();
  }

  function finish() {
    finished = true;
    renderItems();
    advanceHint.className = "advance-hint done";
    advanceHint.textContent = "✓ Checklist complete";
    speak("Checklist complete.", () => {});
    btnNext.disabled = true;
  }

  function reset() {
    mode = "home"; active = null; sequence = []; idx = 0; finished = false;
    synth.cancel();
    viewList.classList.remove("active");
    viewHome.classList.add("active");
    heard.innerHTML = "";
    btnRepeat.disabled = true; btnNext.disabled = true;
    setMic(listening ? "listening" : "idle", listening ? "LISTENING" : "IDLE");
  }

  // ---- Push-to-talk handlers ----
  function pttDown(e) {
    if (e) e.preventDefault();
    if (pttHeld) return;
    pttHeld = true;
    if (synth && synth.speaking) synth.cancel(); // stop readout so we hear the user
    btnPtt.classList.add("active");
    startListening();
  }
  function pttUp(e) {
    if (e) e.preventDefault();
    if (!pttHeld) return;
    pttHeld = false;
    btnPtt.classList.remove("active");
    stopListening();
  }
  btnPtt.addEventListener("mousedown", pttDown);
  btnPtt.addEventListener("touchstart", pttDown, { passive: false });
  window.addEventListener("mouseup", pttUp);
  btnPtt.addEventListener("touchend", pttUp);
  btnPtt.addEventListener("touchcancel", pttUp);
  btnPtt.addEventListener("mouseleave", () => { if (pttHeld) pttUp(); });
  // Spacebar as a keyboard push-to-talk
  window.addEventListener("keydown", (e) => { if (e.code === "Space" && !e.repeat) { e.preventDefault(); pttDown(); } });
  window.addEventListener("keyup", (e) => { if (e.code === "Space") { e.preventDefault(); pttUp(); } });

  // ---- Buttons ----
  btnRepeat.onclick = () => { if (mode === "list" && !finished) speak(sequence[idx].read); };
  btnNext.onclick = () => {
    if (mode !== "list" || finished) return;
    const it = sequence[idx];
    if (it.action === "BRANCH" && it.branch) {
      // default to the first branch when tapped
      const firstKey = Object.keys(it.branch)[0];
      sequence = sequence.slice(0, idx + 1).concat(active.branches[it.branch[firstKey]]);
    }
    advance();
  };
  btnReset.onclick = reset;

  // ---- init ----
  renderChips();
})();
