// Shared timing helpers. Every frame is a pure function of t (seconds).
const BPM = 120, BEAT = 60 / BPM;
const B = (n) => n * BEAT; // beat -> seconds
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eOut = (k) => 1 - Math.pow(1 - k, 3);
const eIn = (k) => k * k * k;
const eIO = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const eExpo = (k) => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k));
// Closed-form damped spring step response (0 -> 1 with small overshoot).
function spring(t, start, freq = 2.2, zeta = 0.62) {
  const x = t - start;
  if (x <= 0) return 0;
  const w = 2 * Math.PI * freq, wd = w * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * w * x) * (Math.cos(wd * x) + ((zeta * w) / wd) * Math.sin(wd * x));
}
// Piecewise keyframes: [[time, value], ...] with easing per segment.
function keys(t, ks, ease = eIO) {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (t <= ks[i][0]) {
      const k = ease((t - ks[i - 1][0]) / (ks[i][0] - ks[i - 1][0]));
      const a = ks[i - 1][1], b = ks[i][1];
      return Array.isArray(a) ? a.map((v, j) => lerp(v, b[j], k)) : lerp(a, b, k);
    }
  }
  return ks[ks.length - 1][1];
}
const $ = (id) => document.getElementById(id);
function css(el, o) { if (typeof el === "string") el = $(el); for (const k in o) el.style[k] = o[k]; }
// Word-by-word masked reveal. Element must contain spans.w > span.i
function words(el, t, start, step = BEAT / 2, out = 1e9, outDur = 0.35) {
  if (typeof el === "string") el = $(el);
  el.querySelectorAll(".i").forEach((s, n) => {
    const kin = spring(t, start + n * step, 2.4, 0.75);
    const kout = eIn(prog(t, out, out + outDur));
    s.style.transform = `translateY(${(1 - kin) * 120 - kout * 140}%)`;
  });
}
// Build word spans from data-text, keeping <em> parts.
function splitWords(root = document) {
  root.querySelectorAll("[data-words]").forEach((el) => {
    const html = el.innerHTML;
    const tmp = document.createElement("div");
    tmp.innerHTML = html;
    const out = [];
    tmp.childNodes.forEach((node) => {
      const isEm = node.nodeName === "EM";
      const txt = node.textContent;
      txt.split(/(\s+)/).forEach((p) => {
        if (!p) return;
        if (/^\s+$/.test(p)) { out.push(" "); return; }
        out.push(`<span class="w"><span class="i${isEm ? " em" : ""}">${p}</span></span>`);
      });
    });
    el.innerHTML = out.join("");
  });
}
const money = (n) => "$" + n.toFixed(2);
// Sound events for the audio builder: [time, type]
window.SFX = [];
function sfx(time, type) { window.SFX.push([+time.toFixed(3), type]); }
