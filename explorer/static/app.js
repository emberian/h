'use strict';
// h explorer client. The weave mirrors universal-weave's DependentWeave (see README: "Weave schema").

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

const FRAME = 'A room in the library, late. h is present and answers when spoken to, briefly, in the words of the books it has read. The others are visitors.';
const DEFAULT_PROMPT = FRAME + '\n\nember: hello h. what are you reading tonight?\n\nh:';
const LS_KEY = 'h-explorer.weave.v1';

const S = {
  servers: [], serving: {}, checkpoints: [],
  weave: null, weaveName: '', collapsed: new Set(), splitMode: null, editing: null,
  prov: new Map(),          // text -> haunt record
  obs: { dates: [], day: null, selected: null },
  busy: 0,
};

// ------------------------------------------------------------------------------------------ utilities
const uuid = () => (crypto.randomUUID ? crypto.randomUUID()
  : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => { const r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 3 | 8)).toString(16); }));
const now = () => new Date().toISOString();
const fmt = (x, d = 2) => (x == null || !isFinite(x)) ? '—' : x.toFixed(d);
const short = (s, n = 60) => { s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
const modelShort = m => (m || '?').replace(/^h-05b-room-/, '').replace(/^h-/, '');
const parseStop = s => { if (!s) return []; try { return [JSON.parse('"' + s.replace(/"/g, '\\"') + '"')]; } catch { return [s]; } };
const visible = t => t.replace(/\n/g, '⏎\n').replace(/\t/g, '⇥');

function status(msg, err = false) {
  const e = $('#status'); e.textContent = msg || ''; e.classList.toggle('err', !!err); e.classList.toggle('busy', S.busy > 0);
}
function busy(delta, msg) { S.busy += delta; status(msg, false); }

async function api(path, body) {
  const r = await fetch(path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : undefined);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}
async function* ndjson(resp) {
  const reader = resp.body.getReader(); const dec = new TextDecoder(); let buf = '';
  for (;;) {
    const { value, done } = await reader.read(); if (done) break;
    buf += dec.decode(value, { stream: true });
    let i; while ((i = buf.indexOf('\n')) >= 0) { const line = buf.slice(0, i); buf = buf.slice(i + 1); if (line.trim()) yield JSON.parse(line); }
  }
  if (buf.trim()) yield JSON.parse(buf);
}
async function* generate(body) {
  const r = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error((await r.json()).error || r.statusText);
  yield* ndjson(r);
}

// ------------------------------------------------------------------------------------------ logprob shading
function lpColor(lp) {
  if (lp == null || !isFinite(lp)) return 'transparent';
  const t = Math.min(1, Math.max(0, -lp / 8));          // 0 = certain, 1 = surprisal >= 8 nats
  const hue = 160 * (1 - t);                              // teal -> red
  return `hsla(${hue}, 70%, 45%, ${(0.08 + 0.55 * t).toFixed(3)})`;
}
function tokenSpan(text, lp, i, extra) {
  const s = el('span', 'tok', visible(text));
  s.style.background = lpColor(lp);
  s.title = `#${i}${extra ? ' ' + extra : ''} ${JSON.stringify(text)}  logprob ${fmt(lp, 3)}  p ${lp == null ? '—' : Math.exp(lp).toFixed(3)}`;
  if (/^\s+$/.test(text) && text.includes('\n')) s.classList.add('stop');
  return s;
}
function strip(logprobs) {
  const d = el('div', 'strip');
  logprobs.forEach((lp, i) => { const c = el('span'); c.style.background = lpColor(lp); c.title = `#${i} logprob ${fmt(lp, 3)}`; d.appendChild(c); });
  return d;
}
function statsOf(tokens) {
  const lps = (tokens || []).map(t => t.logprob).filter(x => typeof x === 'number' && isFinite(x));
  if (!lps.length) return null;
  const sum = lps.reduce((a, b) => a + b, 0), mean = sum / lps.length;
  return { n: lps.length, sum, mean, surprisal: -mean, ppl: Math.exp(-mean) };
}
function statsText(st) { return st ? `${st.n} tok · mean lp ${fmt(st.mean)} · surprisal ${fmt(st.surprisal)} nats · ppl ${fmt(st.ppl, 1)} · sum ${fmt(st.sum, 1)}` : ''; }

// ------------------------------------------------------------------------------------------ weave (DependentWeave)
function newWeave(name) {
  return { nodes: {}, roots: [], active: null, bookmarked: [],
    metadata: { format: 'h-explorer-weave', schema: 1, name: name || '', created: now(), modified: now(), ui: { collapsed: [] } } };
}
const mkNode = ({ from = null, contents, active = false, bookmarked = false }) => ({ id: uuid(), from, to: [], active, bookmarked, contents });

function insert(w, node) {
  if (node.from === node.id || node.to.length || w.nodes[node.id]) return false;
  if (node.from !== null) { const p = w.nodes[node.from]; if (!p) return false; p.to.push(node.id); } else w.roots.push(node.id);
  w.nodes[node.id] = node;
  if (node.active) { if (w.active && w.nodes[w.active]) w.nodes[w.active].active = false; w.active = node.id; }
  if (node.bookmarked) w.bookmarked.push(node.id);
  return true;
}
function setActive(w, id, value) {
  const n = w.nodes[id]; if (!n) return false;
  n.active = value;
  if (value) { if (w.active !== id && w.active && w.nodes[w.active]) w.nodes[w.active].active = false; w.active = id; }
  else if (w.active === id) { w.active = n.from; if (w.active && w.nodes[w.active]) w.nodes[w.active].active = true; }
  return true;
}
function remove(w, id) {
  const root = w.nodes[id]; if (!root) return null;
  const stack = [id]; let removedActive = false; const removedBookmarks = new Set();
  while (stack.length) {
    const x = stack.pop(); const n = w.nodes[x]; if (!n) continue;
    delete w.nodes[x]; S.collapsed.delete(x);
    if (n.bookmarked) removedBookmarks.add(x);
    if (n.active) { w.active = null; removedActive = true; }
    stack.push(...n.to);
  }
  if (root.from === null) w.roots = w.roots.filter(r => r !== id);
  else { const p = w.nodes[root.from]; if (p) p.to = p.to.filter(c => c !== id); }
  if (removedBookmarks.size) w.bookmarked = w.bookmarked.filter(b => !removedBookmarks.has(b));
  if (removedActive) { w.active = root.from; if (w.active && w.nodes[w.active]) w.nodes[w.active].active = true; }
  return root;
}
function setBookmarked(w, id, value) {
  const n = w.nodes[id]; if (!n) return false;
  n.bookmarked = value;
  if (value) { if (!w.bookmarked.includes(id)) w.bookmarked.push(id); } else w.bookmarked = w.bookmarked.filter(b => b !== id);
  return true;
}
const joinTokens = toks => toks.map(t => t.text).join('');
function contentsSplit(c, at) {
  if (c.tokens) {
    if (!(at > 0 && at < c.tokens.length)) return null;
    const L = c.tokens.slice(0, at), R = c.tokens.slice(at);
    return [{ ...c, text: joinTokens(L), tokens: L }, { ...c, text: joinTokens(R), tokens: R }];
  }
  const chars = Array.from(c.text);
  if (!(at > 0 && at < chars.length)) return null;
  return [{ ...c, text: chars.slice(0, at).join('') }, { ...c, text: chars.slice(at).join('') }];
}
function contentsMerge(a, b) {
  return { ...a, kind: a.kind === b.kind ? a.kind : 'merged', text: a.text + b.text,
    tokens: (a.tokens && b.tokens) ? a.tokens.concat(b.tokens) : null, model: a.model === b.model ? a.model : null };
}
function split(w, id, at, newId) {
  if (w.nodes[newId] || id === newId) return false;
  const n = w.nodes[id]; if (!n) return false;
  const parts = contentsSplit(n.contents, at); if (!parts) return false;
  const [left, right] = parts;
  const rightNode = { id: newId, from: id, to: n.to, active: false, bookmarked: false, contents: right };
  for (const c of n.to) w.nodes[c].from = newId;
  n.to = [newId]; n.contents = left;
  w.nodes[newId] = rightNode;
  return true;
}
function mergeWithParent(w, id) {
  const n = w.nodes[id]; if (!n || n.from === null) return null;
  const p = w.nodes[n.from]; if (!p || p.to.length > 1) return null;
  p.contents = contentsMerge(p.contents, n.contents);
  p.to = n.to; for (const c of p.to) w.nodes[c].from = p.id;
  if (n.active) { p.active = true; w.active = p.id; }
  if (n.bookmarked && !p.bookmarked) { p.bookmarked = true; w.bookmarked[w.bookmarked.indexOf(id)] = p.id; }
  else if (n.bookmarked) w.bookmarked = w.bookmarked.filter(b => b !== id);
  delete w.nodes[id]; S.collapsed.delete(id);
  return p.id;
}
function pathTo(w, id) { const out = []; let cur = id; const seen = new Set(); while (cur && w.nodes[cur] && !seen.has(cur)) { seen.add(cur); out.push(cur); cur = w.nodes[cur].from; } return out.reverse(); }
const pathText = (w, id) => pathTo(w, id).map(i => w.nodes[i].contents.text).join('');
function orderedIds(w) { const out = []; const stack = [...w.roots].reverse(); while (stack.length) { const id = stack.pop(); out.push(id); stack.push(...[...w.nodes[id].to].reverse()); } return out; }

// ------------------------------------------------------------------------------------------ state + persistence
function touch(rerenderPrompt = false) {
  const w = S.weave; w.metadata.modified = now(); w.metadata.ui = { collapsed: [...S.collapsed] };
  try { localStorage.setItem(LS_KEY, JSON.stringify({ name: S.weaveName, weave: w })); } catch { /* ignore */ }
  renderTree(); renderReading(); renderBookmarks(); if (rerenderPrompt) syncPromptBox();
  $('#weave-info').textContent = `${Object.keys(w.nodes).length} nodes · ${w.roots.length} root(s) · modified ${w.metadata.modified.slice(11, 19)}`;
}
function loadWeave(w, name) {
  S.weave = w; S.weaveName = name || w.metadata?.name || ''; S.collapsed = new Set(w.metadata?.ui?.collapsed || []);
  $('#weave-name').value = S.weaveName; S.splitMode = null; S.editing = null;
  touch(true);
}
function rootOfActive() { const w = S.weave; if (w.active && w.nodes[w.active]) return pathTo(w, w.active)[0]; return w.roots[0] || null; }
function syncPromptBox() {
  const r = rootOfActive(); const ta = $('#loom-prompt');
  const text = r ? S.weave.nodes[r].contents.text : '';
  if (ta.value !== text) ta.value = text;
}
let promptTimer = null;
function onPromptInput() {
  clearTimeout(promptTimer);
  promptTimer = setTimeout(() => {
    const w = S.weave; const text = $('#loom-prompt').value; const r = rootOfActive();
    if (!r) { if (text) { insert(w, mkNode({ contents: { kind: 'prompt', text, tokens: null, created: now() }, active: true })); touch(); } return; }
    const n = w.nodes[r]; if (n.contents.text === text) return;
    n.contents = { ...n.contents, kind: 'prompt', text, tokens: null, edited: now() }; touch();
  }, 250);
}

// ------------------------------------------------------------------------------------------ sampler + servers
function samplerFrom(prefix) {
  return { n: +$(`#${prefix}-n, #${prefix}-k`).value || 1, max_tokens: +$(`#${prefix}-max`).value || 40,
    temperature: +$(`#${prefix}-temp`).value, top_p: +$(`#${prefix}-topp`).value, stop: parseStop($(`#${prefix}-stop`).value) };
}
function serverByUrl(url) { return S.servers.find(s => s.url === url); }
function fillServerSelect(sel, keep) {
  const prev = keep ? sel.value : null; sel.innerHTML = '';
  for (const s of S.servers) {
    const o = el('option', null, `${s.model || '(no name)'} @ ${s.url.replace('http://', '')}${s.up ? '' : ' (down)'}`);
    o.value = s.url; o.disabled = !s.up || !s.model; sel.appendChild(o);
  }
  const first = S.servers.find(s => s.up && s.model);
  sel.value = (prev && serverByUrl(prev)?.up) ? prev : (first ? first.url : '');
}
async function refreshServers() {
  try {
    const j = await api('/api/servers');
    S.servers = j.servers; S.serving = j.serving; S.checkpoints = j.checkpoints;
    fillServerSelect($('#loom-server'), true); fillServerSelect($('#cmp-a'), true); fillServerSelect($('#cmp-b'), true);
    if (S.servers.filter(s => s.up).length > 1 && $('#cmp-a').value === $('#cmp-b').value) $('#cmp-b').value = S.servers.filter(s => s.up)[1].url;
    const st = $('#servers-status'); st.innerHTML = '';
    S.servers.forEach((s, i) => {
      const t = el(s.up ? 'b' : 's', null, `${s.url.replace('http://127.0.0.1', '')} ${s.model || (s.up ? '(name unknown)' : 'down')}`);
      t.title = s.path || s.error || ''; st.appendChild(t); if (i < S.servers.length - 1) st.appendChild(document.createTextNode('  '));
    });
  } catch (e) { status('servers: ' + e.message, true); }
}

// ------------------------------------------------------------------------------------------ loom rendering
function renderTokens(c, opts = {}) {
  const div = el('div', 'text' + (c.tokens ? '' : ' plain'));
  const prov = opts.matches;
  if (c.tokens) {
    const matched = new Set();
    if (prov && prov.tokens === c.tokens.length) for (const sp of prov.longest_spans || []) for (let k = 0; k < sp.length; k++) matched.add(sp.query_offset + k);
    c.tokens.forEach((t, i) => { const s = tokenSpan(t.text, t.logprob, i, t.id != null ? `id ${t.id}` : ''); s.dataset.at = i; if (matched.has(i)) s.classList.add('match'); div.appendChild(s); });
  } else {
    let at = 0;
    for (const chunk of c.text.match(/\S+\s*|\s+/g) || []) { const s = el('span', 'tok', visible(chunk)); s.dataset.at = at; at += Array.from(chunk).length; div.appendChild(s); }
  }
  return div;
}
function renderTree() {
  const w = S.weave; const root = $('#tree'); root.innerHTML = '';
  if (!w.roots.length) { root.appendChild(el('p', 'hint', 'no nodes yet: type a prompt on the left (or press "frame"), then expand.')); return; }
  const onPath = new Set(w.active ? pathTo(w, w.active) : []);
  const ul = el('ul'); for (const r of w.roots) ul.appendChild(renderNode(r, onPath)); root.appendChild(ul);
}
function renderNode(id, onPath) {
  const w = S.weave; const n = w.nodes[id]; const c = n.contents; const li = el('li');
  const card = el('div', 'node' + (onPath.has(id) ? ' on-path' : '') + (w.active === id ? ' active' : '') + (n.bookmarked ? ' bookmarked' : '') + (S.splitMode === id ? ' split-mode' : ''));
  card.dataset.id = id;
  // header
  const head = el('div', 'head');
  head.appendChild(el('span', 'kind', c.kind || 'node'));
  if (c.model) { const m = el('span', null, modelShort(c.model)); m.title = `${c.model} @ ${c.server || ''}`; head.appendChild(m); }
  const st = statsOf(c.tokens);
  if (st) head.appendChild(el('span', null, `${st.n} tok · lp ${fmt(st.mean)} · surprisal ${fmt(st.surprisal)}`));
  else head.appendChild(el('span', null, `${Array.from(c.text).length} chars`));
  if (c.finish_reason === 'length') head.appendChild(el('span', null, 'cut'));
  if (c.sampler) { const sp = el('span', null, `t${c.sampler.temperature} p${c.sampler.top_p}`); sp.title = JSON.stringify(c.sampler); head.appendChild(sp); }
  const prov = S.prov.get(c.text);
  if (prov) { const p = el('span', 'prov' + (prov.longest_match >= 16 ? ' hot' : ''), `haunt ${prov.longest_match}/${prov.tokens}`); p.title = `longest exact corpus match ${prov.longest_match} tokens of ${prov.tokens}; coverage@8 ${fmt(prov.coverage?.['8'] * 100, 0)}%`; head.appendChild(p); }
  if (n.to.length) { const b = el('span', null, `${S.collapsed.has(id) ? '▸' : '▾'} ${n.to.length}`); b.style.cursor = 'pointer'; b.title = 'collapse / uncollapse children'; b.onclick = e => { e.stopPropagation(); S.collapsed.has(id) ? S.collapsed.delete(id) : S.collapsed.add(id); touch(); }; head.appendChild(b); }
  card.appendChild(head);
  // body
  if (S.editing === id) {
    const ta = el('textarea', 'edit'); ta.value = c.text; card.appendChild(ta);
    const row = el('div', 'actions');
    const save = el('button', 'primary', 'save'); save.onclick = () => { n.contents = { ...c, kind: c.kind === 'prompt' ? 'prompt' : 'edit', text: ta.value, tokens: null, edited: now() }; S.editing = null; touch(true); };
    const cancel = el('button', null, 'cancel'); cancel.onclick = () => { S.editing = null; touch(); };
    row.append(save, cancel); card.appendChild(row);
  } else {
    const body = renderTokens(c, { matches: prov });
    body.onclick = e => {
      const tok = e.target.closest('.tok');
      if (S.splitMode === id && tok) { e.stopPropagation(); const at = +tok.dataset.at; S.splitMode = null; if (!split(w, id, at, uuid())) status('cannot split there', true); touch(); return; }
      setActive(w, id, true); touch(true);
    };
    card.appendChild(body);
    const act = el('div', 'actions');
    for (const s of S.servers.filter(s => s.up && s.model)) {
      const b = el('button', 'primary', `+${modelShort(s.model)}`); b.title = `sample N continuations from ${s.model} (${s.url})`;
      b.onclick = e => { e.stopPropagation(); expand(id, s); }; act.appendChild(b);
    }
    const btn = (label, title, fn) => { const b = el('button', null, label); b.title = title; b.onclick = e => { e.stopPropagation(); fn(); }; act.appendChild(b); };
    btn(n.bookmarked ? '★' : '☆', 'bookmark', () => { setBookmarked(w, id, !n.bookmarked); touch(); });
    if (w.active === id) btn('deactivate', 'move the active tip to the parent', () => { setActive(w, id, false); touch(true); });
    else btn('activate', 'make this the active tip', () => { setActive(w, id, true); touch(true); });
    btn('edit', 'edit the text (drops token logprobs)', () => { S.editing = id; S.splitMode = null; touch(); });
    btn(S.splitMode === id ? 'splitting…' : 'split', 'then click the token that should start the new child', () => { S.splitMode = S.splitMode === id ? null : id; touch(); });
    if (n.from !== null && w.nodes[n.from]?.to.length === 1) btn('merge ↑', 'merge into the parent (only child)', () => { mergeWithParent(w, id); touch(true); });
    btn('haunt', 'provenance scan this node', () => haunt([{ id, text: c.text }]).then(() => touch()));
    btn('✕', 'delete this node and its subtree', () => { if (n.to.length === 0 || confirm(`delete ${n.to.length} descendant(s) too?`)) { remove(w, id); touch(true); } });
    card.appendChild(act);
  }
  li.appendChild(card);
  if (n.to.length && !S.collapsed.has(id)) { const ul = el('ul'); for (const cid of n.to) ul.appendChild(renderNode(cid, onPath)); li.appendChild(ul); }
  return li;
}
function renderReading() {
  const w = S.weave; const out = $('#reading'); out.innerHTML = '';
  if (!w.active) { $('#reading-stats').textContent = ''; return; }
  const ids = pathTo(w, w.active); let all = [];
  for (const id of ids) {
    const c = w.nodes[id].contents; const seg = el('span', 'seg ' + (c.tokens ? '' : 'prompt') + (id === w.active ? ' active' : ''));
    if (c.tokens) { c.tokens.forEach((t, i) => seg.appendChild(tokenSpan(t.text, t.logprob, i))); all = all.concat(c.tokens); }
    else seg.textContent = c.text;
    seg.title = `${c.kind} ${id.slice(0, 8)}`; seg.onclick = () => { setActive(w, id, true); touch(true); };
    out.appendChild(seg);
  }
  const st = statsOf(all); $('#reading-stats').textContent = `${ids.length} nodes · ${Array.from(pathText(w, w.active)).length} chars` + (st ? ` · sampled ${statsText(st)}` : '');
}
function renderBookmarks() {
  const w = S.weave; const ul = $('#bookmarks'); ul.innerHTML = '';
  for (const id of w.bookmarked) { const n = w.nodes[id]; if (!n) continue; const li = el('li', null, '★ ' + short(n.contents.text, 48)); li.title = n.contents.text; li.onclick = () => { setActive(w, id, true); for (const p of pathTo(w, id)) S.collapsed.delete(p); touch(true); }; ul.appendChild(li); }
  if (!w.bookmarked.length) ul.appendChild(el('li', 'hint', 'none'));
}

// ------------------------------------------------------------------------------------------ expand
function sampleContents(msg) {
  return { kind: 'sample', text: msg.text, tokens: msg.tokens, model: msg.model, server: msg.server, sampler: msg.sampler,
    finish_reason: msg.finish_reason, seconds: msg.seconds, created: msg.created };
}
async function expand(id, server) {
  const w = S.weave; if (!w.nodes[id]) return;
  server = server || serverByUrl($('#loom-server').value);
  if (!server || !server.up || !server.model) return status('no live model server selected', true);
  const cfg = samplerFrom('loom'); const prompt = pathText(w, id);
  busy(1, `sampling ${cfg.n}× from ${server.model}…`);
  let got = 0; const t0 = performance.now();
  try {
    for await (const msg of generate({ ...cfg, server: server.url, model: server.model, prompt })) {
      if (msg.type === 'sample') { if (insert(w, mkNode({ from: id, contents: sampleContents(msg) }))) { got++; S.collapsed.delete(id); touch(); } }
      else if (msg.type === 'error') status(msg.message, true);
    }
  } catch (e) { status(e.message, true); }
  finally { S.busy--; status(`${got} sample(s) from ${server.model} in ${((performance.now() - t0) / 1000).toFixed(1)}s`); }
}

// ------------------------------------------------------------------------------------------ provenance
async function haunt(items) {
  const todo = items.filter(it => it.text.trim() && !S.prov.has(it.text));
  const byId = new Map(todo.map(it => [it.id, it.text]));
  if (todo.length) {
    busy(1, `haunt: scanning ${todo.length} text(s)…`);
    try {
      const j = await api('/api/haunt', { items: todo });
      for (const [id, rec] of Object.entries(j.results)) S.prov.set(byId.get(id), rec);
      status(`haunt: ${j.scanned} scanned, ${j.cached} cached, ${j.seconds}s`);
    } catch (e) { status('haunt: ' + e.message, true); } finally { S.busy--; }
  }
  return items.map(it => S.prov.get(it.text));
}
function provTarget() {
  const w = S.weave; if (!w.active) return null;
  const scope = $('input[name=prov-scope]:checked').value;
  return { id: w.active, text: scope === 'path' ? pathText(w, w.active) : w.nodes[w.active].contents.text, scope };
}
function renderProvenance() {
  const w = S.weave; const t = provTarget(); const box = $('#prov-text'); box.innerHTML = ''; const out = $('#prov-results'); out.innerHTML = '';
  if (!t) { box.appendChild(el('span', 'hint', 'no active node in the loom')); return; }
  const c = w.nodes[t.id].contents; const rec = S.prov.get(t.text);
  box.appendChild(t.scope === 'node' ? renderTokens(c, { matches: rec }) : el('div', 'text plain', t.text));
  if (!rec) { out.appendChild(el('p', 'hint', 'not scanned yet')); return; }
  const card = el('div', 'prov-card');
  const stats = el('div', 'stats');
  stats.innerHTML = `<span>tokens <b>${rec.tokens}</b></span><span>longest exact match <b>${rec.longest_match}</b> tokens</span><span>spans <b>${rec.span_count}</b></span>`;
  card.appendChild(stats);
  const cov = el('div', 'stats');
  for (const k of Object.keys(rec.coverage || {})) { const v = rec.coverage[k]; const s = el('span'); s.innerHTML = `coverage@${k} <b>${fmt(v * 100, 0)}%</b> `; const bar = el('span', 'bar'); const i = el('i'); i.style.width = `${Math.round(v * 100)}%`; bar.appendChild(i); s.appendChild(bar); cov.appendChild(s); }
  card.appendChild(cov);
  out.appendChild(card);
  if (rec.top_documents?.length) {
    const t2 = el('table'); t2.innerHTML = '<tr><th>source</th><th>path</th><th class="num">quoted tok</th><th class="num">doc tok</th><th class="num">token offset</th></tr>';
    for (const d of rec.top_documents) { const tr = el('tr'); tr.innerHTML = `<td>${d.source ?? ''}</td><td class="path"></td><td class="num">${d.quoted_tokens ?? ''}</td><td class="num">${d.tokens ?? ''}</td><td class="num">${d.token_offset ?? ''}</td>`; tr.children[1].textContent = d.path || d.id || ''; t2.appendChild(tr); }
    const c2 = el('div', 'prov-card'); c2.appendChild(el('h3', null, 'top documents')); c2.appendChild(t2); out.appendChild(c2);
  }
  if (rec.longest_spans?.length) {
    const c3 = el('div', 'prov-card span-list'); c3.appendChild(el('h3', null, 'longest spans'));
    for (const sp of rec.longest_spans) {
      const d = el('div', 'cand'); const h = el('div', 'head');
      h.textContent = `${sp.length} tokens · query offset ${sp.query_offset} · ${sp.occurrences} occurrence(s) in ${sp.distinct_documents} doc(s)${sp.crosses_document_boundary ? ' · crosses boundary' : ''} · ${sp.document?.source || ''} ${sp.document?.path || ''}`;
      d.appendChild(h); d.appendChild(el('div', 'text plain', sp.text ?? '(no --decode text)')); c3.appendChild(d);
    }
    out.appendChild(c3);
  }
  if (!rec.top_documents?.length && !rec.longest_spans?.length) out.appendChild(el('p', 'hint', 'no exact spans at or above the smallest threshold'));
}

// ------------------------------------------------------------------------------------------ observatory
async function loadObsDates() {
  try {
    const j = await api('/api/observatory'); S.obs.dates = j.dates; const sel = $('#obs-date'); sel.innerHTML = '';
    for (const d of j.dates) { const o = el('option', null, `${d.date} (${d.records})`); o.value = d.date; sel.appendChild(o); }
    if (!j.dates.length) { $('#obs-summary').textContent = `no files in ${j.dir}`; return; }
    await loadObsDay(sel.value);
  } catch (e) { status('observatory: ' + e.message, true); }
}
async function loadObsDay(date) {
  busy(1, `loading ${date}…`);
  try { S.obs.day = await api(`/api/observatory?date=${encodeURIComponent(date)}`); S.obs.selected = null; renderObsSummary(); renderObsList(); renderObsDetail(); status(`${date}: ${S.obs.day.records.length} records`); }
  catch (e) { status('observatory: ' + e.message, true); } finally { S.busy--; }
}
function renderObsSummary() {
  const s = S.obs.day.summary; const box = $('#obs-summary');
  box.innerHTML = `records <b>${s.records}</b><br>accepted <b>${s.accepted}</b> (${fmt(s.acceptance_rate * 100, 0)}%)<br>mean candidates tried <b>${fmt(s.mean_candidates)}</b><br>mean seconds <b>${fmt(s.mean_seconds)}</b><br>mean chosen logprob <b>${fmt(s.mean_chosen_logprob)}</b><br>dropped echo turns <b>${s.dropped_echo_turns}</b><br>models <b></b>`;
  box.querySelector('b:last-child').textContent = (s.models || []).join(', ') || '—';
}
function renderObsList() {
  const box = $('#obs-list'); box.innerHTML = ''; const t = el('table');
  t.innerHTML = '<tr><th>#</th><th>time</th><th>visitor</th><th class="num">tried</th><th>ok</th><th class="num">s</th></tr>';
  for (const r of S.obs.day.records) {
    const tr = el('tr', S.obs.selected === r.index ? 'on' : ''); const chosen = r.candidates?.find(c => c.text === r.chosen);
    tr.innerHTML = `<td>${r.index}</td><td>${(r.time || '').slice(11, 19)}</td><td></td><td class="num">${r.candidates?.length ?? 0}</td><td class="${r.chosen_accepted ? 'ok' : 'bad'}">${r.chosen_accepted ? '✓' : '✗'}</td><td class="num">${fmt(r.seconds, 1)}</td>`;
    tr.children[2].textContent = short(r.last_visitor, 28); tr.title = `chosen: ${short(r.chosen, 120)}${chosen ? ` (mean lp ${fmt(chosen.mean_logprob)})` : ''}`;
    tr.onclick = () => { S.obs.selected = r.index; renderObsList(); renderObsDetail(); };
    t.appendChild(tr);
  }
  box.appendChild(t);
}
function renderObsDetail() {
  const out = $('#obs-detail'); out.innerHTML = '';
  const r = S.obs.day?.records.find(x => x.index === S.obs.selected);
  if (!r) { out.appendChild(el('p', 'hint', 'select a record')); return; }
  const head = el('div', 'stats');
  head.innerHTML = `<span>${r.time}</span><span>model <b></b></span><span>proxy ${r.proxy_sha || ''}</span><span>sampler <b></b></span><span>${fmt(r.seconds)} s</span><span>dropped echo turns <b>${r.dropped_echo_turns}</b></span>`;
  head.querySelectorAll('b')[0].textContent = r.model || ''; head.querySelectorAll('b')[1].textContent = JSON.stringify(r.sampler);
  const row = el('div', 'row'); const toLoom = el('button', null, 'open in loom'); toLoom.onclick = () => obsToLoom(r); row.appendChild(toLoom);
  out.append(head, row);
  const pc = el('div', 'prov-card'); pc.appendChild(el('h3', null, 'prompt (raw; struck = dropped by the proxy as an echo)'));
  for (const b of r.blocks || []) {
    const d = el('div', 'block ' + b.kind + (b.name === 'h' ? ' h' : '') + (b.dropped ? ' dropped' : ''));
    if (b.name) { d.appendChild(el('span', 'name', b.name + ': ')); d.appendChild(document.createTextNode(b.text.slice(b.name.length + 2))); } else d.textContent = b.text;
    pc.appendChild(d);
  }
  const det = el('details'); det.appendChild(el('summary', null, 'cleaned prompt as sent')); det.appendChild(el('div', 'block', r.prompt_cleaned || '')); pc.appendChild(det);
  out.appendChild(pc);
  const cc = el('div', 'prov-card'); cc.appendChild(el('h3', null, 'candidates'));
  (r.candidates || []).forEach((c, i) => {
    const isChosen = c.text === r.chosen; const d = el('div', 'cand' + (isChosen ? ' chosen' : ''));
    const h = el('div', 'head');
    h.innerHTML = `<span>#${i + 1}</span><span>overlap <b>${fmt(c.overlap, 3)}</b></span><span class="${c.accepted ? 'ok' : 'bad'}">${c.accepted ? 'accepted' : 'rejected'}</span><span>${c.tokens} tok</span><span>mean lp <b>${fmt(c.mean_logprob)}</b></span>${isChosen ? '<span class="ok">chosen</span>' : ''}`;
    d.appendChild(h);
    if (c.tokens_text && c.tokens_text.length === c.logprobs.length) { const t = el('div', 'text plain'); c.tokens_text.forEach((tx, k) => t.appendChild(tokenSpan(tx, c.logprobs[k], k))); d.appendChild(t); }
    else { d.appendChild(el('div', 'text plain', c.text)); if (c.logprobs?.length) { d.appendChild(strip(c.logprobs)); d.appendChild(el('div', 'hint', 'token strip (text could not be re-tokenised to the sampled length)')); } }
    cc.appendChild(d);
  });
  out.appendChild(cc);
}
function obsToLoom(r) {
  const w = newWeave(`obs-${S.obs.day.date}-${r.index}`);
  const root = mkNode({ contents: { kind: 'prompt', text: r.prompt_cleaned || r.prompt_raw || '', tokens: null, created: r.time }, active: true });
  insert(w, root);
  (r.candidates || []).forEach((c, i) => {
    const aligned = c.tokens_text && c.tokens_text.length === (c.logprobs || []).length;
    const tokens = aligned ? c.tokens_text.map((tx, k) => ({ id: null, text: tx, logprob: c.logprobs[k] })) : null;
    insert(w, mkNode({ from: root.id, bookmarked: c.text === r.chosen, contents: { kind: 'sample', text: aligned ? tokens.map(t => t.text).join('') : (' ' + c.text + '\n\n'), tokens, model: r.model, server: 'observatory', sampler: r.sampler, created: r.time,
      observatory: { date: S.obs.day.date, index: r.index, candidate: i, overlap: c.overlap, accepted: c.accepted, chosen: c.text === r.chosen } } }));
  });
  loadWeave(w, w.metadata.name); showTab('loom');
}

// ------------------------------------------------------------------------------------------ compare
async function runCompare() {
  const prompt = $('#cmp-prompt').value; const cfg = samplerFrom('cmp');
  const a = serverByUrl($('#cmp-a').value), b = serverByUrl($('#cmp-b').value);
  if (!a?.up || !b?.up) return status('pick two live servers', true);
  const run = async (srv, side) => {
    const out = $(`#cmp-${side}-out`); out.innerHTML = ''; $(`#cmp-${side}-title`).textContent = `${side.toUpperCase()} · ${srv.model}`; $(`#cmp-${side}-stats`).textContent = 'sampling…';
    const samples = []; const t0 = performance.now();
    try {
      for await (const msg of generate({ ...cfg, n: cfg.n, server: srv.url, model: srv.model, prompt })) {
        if (msg.type === 'sample') { samples.push(msg); out.appendChild(renderSample(msg, prompt)); }
        else if (msg.type === 'error') status(msg.message, true);
      }
    } catch (e) { status(e.message, true); }
    const st = statsOf(samples.flatMap(s => s.tokens)); const stops = samples.filter(s => s.finish_reason === 'stop').length;
    $(`#cmp-${side}-stats`).textContent = `${samples.length} samples · ${statsText(st)} · mean ${fmt(samples.reduce((x, s) => x + s.tokens.length, 0) / (samples.length || 1), 1)} tok · stopped ${stops}/${samples.length} · ${fmt(samples.reduce((x, s) => x + s.seconds, 0) / (samples.length || 1))} s each · ${((performance.now() - t0) / 1000).toFixed(1)} s total`;
  };
  busy(1, `compare: ${cfg.n}× ${a.model} vs ${cfg.n}× ${b.model}`);
  try { await Promise.all([run(a, 'a'), run(b, 'b')]); } finally { S.busy--; status('compare done'); }
}
function renderSample(msg, prompt) {
  const d = el('div', 'sample'); const h = el('div', 'head'); const st = statsOf(msg.tokens);
  const left = el('span', null, `#${msg.index + 1} · ${statsText(st)} · ${msg.finish_reason} · ${msg.seconds}s`);
  const b = el('button', null, '→ loom'); b.title = 'add this sample under a root with this prompt in the loom';
  b.onclick = () => { sampleToLoom(prompt, msg); };
  h.append(left, b); d.appendChild(h);
  const t = el('div', 'text plain'); msg.tokens.forEach((tk, i) => t.appendChild(tokenSpan(tk.text, tk.logprob, i, `id ${tk.id}`))); d.appendChild(t);
  return d;
}
function sampleToLoom(prompt, msg) {
  const w = S.weave; let root = w.roots.find(r => w.nodes[r].contents.text === prompt);
  if (!root) { const n = mkNode({ contents: { kind: 'prompt', text: prompt, tokens: null, created: now() } }); insert(w, n); root = n.id; }
  const n = mkNode({ from: root, contents: sampleContents(msg), active: true }); insert(w, n); S.collapsed.delete(root); touch(true); status('added to loom');
}

// ------------------------------------------------------------------------------------------ weave files
async function refreshWeaveList() {
  try {
    const j = await api('/api/weaves'); const sel = $('#weave-list'); sel.innerHTML = '';
    for (const w of j.weaves) { const o = el('option', null, `${w.name} (${w.nodes ?? '?'} nodes)`); o.value = w.name; sel.appendChild(o); }
    if (!j.weaves.length) sel.appendChild(el('option', null, '(no saved weaves)'));
  } catch (e) { status('weaves: ' + e.message, true); }
}
async function saveWeave() {
  const name = $('#weave-name').value.trim(); if (!name) return status('give the weave a name', true);
  try { const j = await api('/api/weaves', { name, weave: S.weave }); S.weaveName = name; S.weave.metadata.name = name; status(`saved ${j.name} (${j.nodes} nodes) → ${j.path}`); refreshWeaveList(); }
  catch (e) { status('save: ' + e.message, true); }
}
async function loadWeaveByName(name) {
  try { const w = await api(`/api/weaves?name=${encodeURIComponent(name)}`); loadWeave(w, name); status(`loaded ${name}`); }
  catch (e) { status('load: ' + e.message, true); }
}

// ------------------------------------------------------------------------------------------ tabs + wiring
function showTab(name) {
  $$('.tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === name));
  $$('.tab').forEach(t => t.classList.toggle('on', t.id === 'tab-' + name));
  if (name === 'provenance') renderProvenance();
  if (name === 'observatory' && !S.obs.day) loadObsDates();
}
function wire() {
  $$('.tabs button').forEach(b => b.onclick = () => showTab(b.dataset.tab));
  $('#servers-refresh').onclick = refreshServers;
  $('#loom-prompt').oninput = onPromptInput;
  $('#loom-frame').onclick = () => { const ta = $('#loom-prompt'); ta.value = ta.value.trim() ? ta.value : DEFAULT_PROMPT; onPromptInput(); };
  $('#loom-expand-root').onclick = () => { const w = S.weave; if (!w.active) return status('no active node', true); expand(w.active); };
  $('#weave-save').onclick = saveWeave;
  $('#weave-load').onclick = () => { const v = $('#weave-list').value; if (v) loadWeaveByName(v); };
  $('#weave-new').onclick = () => { if (!Object.keys(S.weave.nodes).length || confirm('discard the current (unsaved) weave?')) loadWeave(newWeave(''), ''); };
  $('#haunt-all').onclick = $('#prov-scan-all').onclick = async () => { const w = S.weave; await haunt(orderedIds(w).map(id => ({ id, text: w.nodes[id].contents.text }))); touch(); renderProvenance(); };
  $('#collapse-all').onclick = () => { for (const id of orderedIds(S.weave)) if (S.weave.nodes[id].to.length) S.collapsed.add(id); touch(); };
  $('#expand-all').onclick = () => { S.collapsed.clear(); touch(); };
  $('#prov-scan').onclick = async () => { const t = provTarget(); if (!t) return status('no active node', true); await haunt([t]); renderProvenance(); touch(); };
  $$('input[name=prov-scope]').forEach(r => r.onchange = renderProvenance);
  $('#obs-date').onchange = e => loadObsDay(e.target.value);
  $('#obs-reload').onclick = () => loadObsDates();
  $('#cmp-run').onclick = runCompare;
  $('#cmp-frame').onclick = () => { $('#cmp-prompt').value = DEFAULT_PROMPT; };
  $('#cmp-from-loom').onclick = () => { const w = S.weave; if (w.active) $('#cmp-prompt').value = pathText(w, w.active); };
  $$('.legend .tok').forEach(s => { s.style.background = lpColor(+s.dataset.lp); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && (S.splitMode || S.editing)) { S.splitMode = null; S.editing = null; touch(); } });
}

async function init() {
  wire();
  let restored = null;
  try { restored = JSON.parse(localStorage.getItem(LS_KEY) || 'null'); } catch { /* ignore */ }
  if (restored?.weave?.nodes) loadWeave(restored.weave, restored.name); else loadWeave(newWeave(''), '');
  $('#cmp-prompt').value = DEFAULT_PROMPT;
  await Promise.all([refreshServers(), refreshWeaveList()]);
  touch(true);
  status('ready');
}
init();
