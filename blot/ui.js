"use strict";
(() => {
  const page = document.querySelector("#page");
  const drop = document.querySelector("#drop");
  const pause = document.querySelector("#pause");
  const keys = new Set();
  let game, words, paused = false, target = null, last = null;
  function reset() {
    game = new Blot();
    paused = false;
    keys.clear();
    target = null;
    last = null;
    page.querySelectorAll(".word").forEach(node => node.remove());
    words = game.words.map(word => {
      const node = document.createElement("span");
      node.className = "word";
      node.textContent = word.text;
      node.style.left = `${word.x / 7.2}%`;
      node.style.top = `${word.y / 4.6}%`;
      page.append(node);
      return node;
    });
    render();
  }
  function render() {
    words.forEach((node, i) => node.classList.toggle("marked", game.words[i].marked));
    drop.style.left = `${game.x / 7.2}%`;
    drop.style.top = `${game.y / 4.6}%`;
    drop.style.width = `${game.radius * 2 / 7.2}%`;
    drop.style.height = `${game.radius * 2 / 4.6}%`;
    document.querySelector("#count").textContent = `${game.words.filter(word => word.marked).length} / ${words.length} words`;
    document.querySelector("#time").textContent = `${(game.duration - game.elapsed).toFixed(1)} s of wet ink`;
    const status = game.status === "won" ? "Page complete. Every word, touched." : game.status === "dry" ? "Your ink dried. Try a fresh page." : paused ? "Paused. Your ink will wait." : "Touch every word before your ink dries.";
    const label = document.querySelector("#status");
    if (label.textContent !== status) label.textContent = status;
    pause.textContent = paused ? "Resume" : "Pause";
    pause.disabled = game.status !== "playing";
  }
  function togglePause() { if (game.status === "playing") { paused = !paused; keys.clear(); target = null; last = null; render(); } }
  document.querySelector("#restart").addEventListener("click", reset);
  pause.addEventListener("click", togglePause);
  const movement = ["arrowleft", "arrowright", "arrowup", "arrowdown", "w", "a", "s", "d"];
  document.addEventListener("keydown", event => {
    const key = event.key.toLowerCase();
    if (movement.includes(key)) { event.preventDefault(); keys.add(key); }
    if (!event.repeat && key === "p") togglePause();
    if (!event.repeat && key === "r") reset();
  });
  document.addEventListener("keyup", event => keys.delete(event.key.toLowerCase()));
  function aim(event) {
    const rect = page.getBoundingClientRect();
    target = {x: (event.clientX - rect.left) / rect.width * 720, y: (event.clientY - rect.top) / rect.height * 460};
  }
  page.addEventListener("pointerdown", event => { page.focus(); page.setPointerCapture(event.pointerId); aim(event); });
  page.addEventListener("pointermove", event => { if (page.hasPointerCapture(event.pointerId)) aim(event); });
  for (const type of ["pointerup", "pointercancel", "lostpointercapture"]) page.addEventListener(type, () => { target = null; });
  function suspend() { keys.clear(); target = null; last = null; if (game.status === "playing") paused = true; render(); }
  window.addEventListener("blur", suspend);
  document.addEventListener("visibilitychange", () => { if (document.hidden) suspend(); last = null; });
  function frame(now) {
    const seconds = last === null ? 0 : (now - last) / 1000;
    last = now;
    if (!paused && !document.hidden) {
      let dx = Number(keys.has("d") || keys.has("arrowright")) - Number(keys.has("a") || keys.has("arrowleft"));
      let dy = Number(keys.has("s") || keys.has("arrowdown")) - Number(keys.has("w") || keys.has("arrowup"));
      if (target && Math.hypot(target.x - game.x, target.y - game.y) > 4) { dx = target.x - game.x; dy = target.y - game.y; }
      game.advance(seconds, dx, dy);
      render();
    }
    requestAnimationFrame(frame);
  }
  reset();
  requestAnimationFrame(frame);
})();
