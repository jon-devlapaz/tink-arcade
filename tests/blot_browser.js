"use strict";
window.addEventListener("load", async () => {
  const result = document.querySelector("#result");
  try {
    const frame = document.querySelector("iframe");
    const win = frame.contentWindow;
    const doc = frame.contentDocument;
    const Game = win.Blot;
    function assert(value, message) { if (!value) throw new Error(message); }
    const game = new Game();
    const start = game.x;
    game.advance(.1, 1, 0);
    assert(game.x > start, "steering moves drop");
    const radius = game.radius, speed = game.speed;
    for (const word of game.words) {
      const beforeRadius = game.radius, beforeSpeed = game.speed;
      game.x = word.x; game.y = word.y;
      game.advance(.01);
      assert(word.marked, "contact marks word");
      assert(game.radius > beforeRadius, "each word grows radius");
      assert(game.speed < beforeSpeed, "each word reduces speed");
      const afterRadius = game.radius, afterSpeed = game.speed;
      game.advance(.01);
      assert(game.radius === afterRadius && game.speed === afterSpeed, "repeat contact does not collect twice");
    }
    assert(game.status === "won" && game.elapsed < game.duration, "all words complete before drying");
    assert(game.radius > radius && game.speed < speed, "successive growth and slowdown");
    const dry = new Game();
    dry.advance(10);
    assert(dry.elapsed > 9.99 && dry.status === "playing", "continuous active drying");
    dry.advance(31);
    assert(dry.status === "dry", "active elapsed time reaches drying failure");
    const frozen = dry.elapsed;
    dry.advance(3, 1, 1);
    assert(dry.elapsed === frozen, "terminal state freezes");
    const diagonal = new Game(), straight = new Game();
    diagonal.advance(.05, 1, 1); straight.advance(.05, 1, 0);
    assert(Math.abs(Math.hypot(diagonal.x - 65, diagonal.y - 245) - (straight.x - 65)) < .001, "diagonal speed normalized");
    assert(doc.querySelectorAll(".word").length === 6, "actual UI renders words");
    doc.querySelector("#pause").click();
    assert(doc.querySelector("#status").textContent.includes("Paused"), "pause control connected");
    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
    const pausedTime = doc.querySelector("#time").textContent;
    await wait(150);
    assert(doc.querySelector("#time").textContent === pausedTime, "inactive play freezes drying");
    doc.querySelector("#restart").click();
    assert(doc.querySelector("#count").textContent === "0 / 6 words", "restart control connected");
    const drop = doc.querySelector("#drop");
    const left = parseFloat(drop.style.left);
    doc.dispatchEvent(new win.KeyboardEvent("keydown", {key: "d"}));
    await wait(250);
    doc.dispatchEvent(new win.KeyboardEvent("keyup", {key: "d"}));
    assert(parseFloat(drop.style.left) > left, "actual keyboard steers rendered drop");
    assert(doc.querySelector("#time").textContent !== "40.0 s of wet ink", "actual active UI clock dries ink");
    doc.querySelector("#pause").click();
    const resources = win.performance.getEntriesByType("resource").map(entry => entry.name);
    assert(resources.every(name => name.startsWith(new URL("../blot/", location.href).href) || name === "data:,"), "no external browser resource requests");
    assert(doc.querySelector('meta[http-equiv="Content-Security-Policy"]').content.includes("connect-src 'none'"), "network connections prohibited");
    result.textContent = "PASS " + JSON.stringify({resources, radius: game.radius, speed: game.speed, dry: dry.status});
  } catch (error) { result.textContent = "FAIL " + error.stack; }
});
