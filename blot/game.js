"use strict";
window.Blot = class Blot {
  constructor() {
    this.x = 65;
    this.y = 245;
    this.radius = 12;
    this.speed = 180;
    this.elapsed = 0;
    this.duration = 40;
    this.status = "playing";
    this.words = [
      ["leave", 140, 110], ["room", 330, 80], ["for", 520, 135],
      ["a", 600, 300], ["little", 415, 380], ["wonder", 180, 345]
    ].map(([text, x, y]) => ({text, x, y, width: text.length * 15, height: 30, marked: false}));
  }
  advance(seconds, dx = 0, dy = 0) {
    if (!Number.isFinite(seconds) || seconds < 0 || !Number.isFinite(dx) || !Number.isFinite(dy)) {
      throw new Error("Expected finite direction and nonnegative elapsed seconds");
    }
    if (this.status !== "playing") return;
    let remaining = Math.min(seconds, this.duration - this.elapsed);
    const length = Math.hypot(dx, dy);
    if (length > 0) { dx /= length; dy /= length; }
    while (remaining > 0 && this.status === "playing") {
      const dt = Math.min(remaining, 1 / 120);
      remaining -= dt;
      this.elapsed = Math.min(this.duration, this.elapsed + dt);
      this.x = Math.max(this.radius, Math.min(720 - this.radius, this.x + dx * this.speed * dt));
      this.y = Math.max(this.radius, Math.min(460 - this.radius, this.y + dy * this.speed * dt));
      for (const word of this.words) {
        const nx = Math.max(word.x, Math.min(word.x + word.width, this.x));
        const ny = Math.max(word.y - word.height / 2, Math.min(word.y + word.height / 2, this.y));
        if (!word.marked && Math.hypot(this.x - nx, this.y - ny) <= this.radius) {
          word.marked = true;
          this.radius += 4;
          this.speed *= 0.87;
        }
      }
      if (this.words.every(word => word.marked)) this.status = "won";
      else if (this.elapsed >= this.duration - 1e-9) { this.elapsed = this.duration; this.status = "dry"; }
    }
  }
}
