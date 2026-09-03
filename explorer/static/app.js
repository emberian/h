'use strict';
// h explorer client (v1). The weave mirrors universal-weave's DependentWeave (see README: "Weave schema").
// Panes: loom, provenance, observatory, compare, counterfactual, room state (hbox persistent cache), population,
// labels/pairs. Every weave mutation goes through mutate(label, fn) so it is undoable.

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

const FRAME = 'A room in the library, late. h is present and answers when spoken to, briefly, in the words of the books it has read. The others are visitors.';
const DEFAULT_PROMPT = FRAME + '\n\nember: hello h. what are you reading tonight?\n\nh:';
const LS_KEY = 'h-explorer.weave.v1';
const LS_RECENT = 'h-explorer.recent.v1';
const AUTO_COLLAPSE_DEPTH = 2;
const LIB_SAMPLER = { n: 4, temperature: 0.7, top_p: 0.9, max_tokens: 64, stop: ['\n\n'] };  // what the room models handle best
const SEED_LINE = 'ember: hi h';
// [tab, name, one sentence] — rendered on the start pane and in the ? help.
const PANES = [
  ['start', 'Start here', 'three ways in and this map; the ? help button brings the map back from any pane.'],
  ['loom', 'Loom', 'a tree of completions: expand a node to sample continuations, click one to select it, and read the selected path on the right with every token shaded by its logprob.'],
  ['provenance', 'Provenance', 'exact-match search of the selected node against the training corpus: how much of what h said is quotation, and from which books.'],
  ['observatory', 'Observatory', 'replay of the Discord room proxy: for each turn, the prompt h saw, the candidates it tried, and the one it said.'],
  ['compare', 'Compare', 'one prompt to two (or all) model servers, K samples each, side by side with per-server statistics.'],
  ['counterfactual', 'Counterfactual', 'edit the earlier turns of a room and score a fixed reply under the true and the edited context, token by token.'],
  ['roomstate', 'Room state', 'drive the persistent-state room server on hbox: read events into the state, fork candidates, commit one, and watch the state norms.'],
  ['population', 'Population', 'one prompt across many checkpoints, each served in turn on :8125, with a library-likeness judge and a provenance scan per sample.'],
  ['labels', 'Labels', 'the ledger of failure labels and the blind pairwise sheets; a label from any pane lands here as a training record.'],
];

const S = {
  servers: [], serving: {}, checkpoints: [], version: {}, serve: {},
  weave: null, weaveName: '', collapsed: new Set(), splitMode: null, editing: null, noting: null,
  prov: new Map(),          // text -> haunt record
  obs: { dates: [], day: null, selected: null, loading: null },
  library: { frame: FRAME, sampler: LIB_SAMPLER, items: [] },
  seeding: false, probed: false, probe: null,   // the first /api/servers probe: the start actions wait for it
  busy: 0,
  history: { past: [], future: [] },
  cf: { turns: [], edited: [], reply: '', results: null },
  rs: { room: null, rooms: [], history: [], candidates: [] },
  pop: { running: false, stop: false },
  scorers: [], judge: null,
  labels: null, pairs: { sheets: [], sheet: null, answers: {} },
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
const clone = o => JSON.parse(JSON.stringify(o));
const inField = () => { const a = document.activeElement; return a && (a.tagName === 'INPUT' || a.tagName === 'TEXTAREA' || a.tagName === 'SELECT' || a.isContentEditable); };

function status(msg, err = false) {
  const e = $('#status'); e.textContent = msg || ''; e.classList.toggle('err', !!err); e.classList.toggle('busy', S.busy > 0);
}
function busy(delta, msg) { S.busy += delta; status(msg, false); }
function toast(msg, kind = '') {
  const t = el('div', 'toast ' + kind, msg); $('#toasts').appendChild(t);
  setTimeout(() => t.remove(), kind === 'err' ? 7000 : 3500);
}
function fail(prefix, e) { const m = `${prefix}: ${e?.message || e}`; status(m, true); toast(m, 'err'); }

async function api(path, body, method) {
  let r;
  try {
    r = await fetch(path, body || method ? { method: method || 'POST', headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined } : undefined);
  } catch (e) { throw new Error(`explorer server unreachable (${e.message})`); }
  let j; try { j = await r.json(); } catch { throw new Error(`${r.status} ${r.statusText}`); }
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
async function* stream(path, body) {
  let r;
  try { r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); }
  catch (e) { throw new Error(`explorer server unreachable (${e.message})`); }
  if (!r.ok) throw new Error((await r.json()).error || r.statusText);
  yield* ndjson(r);
}
const generate = body => stream('/api/generate', body);

// ------------------------------------------------------------------------------------------ logprob shading
function lpColor(lp) {
  if (lp == null || !isFinite(lp)) return 'transparent';
  const t = Math.min(1, Math.max(0, -lp / 8));
  const hue = 160 * (1 - t);
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
    return [{ ...c, text: joinTokens(L), tokens: L }, { ...c, text: joinTokens(R), tokens: R, note: undefined, labels: undefined }];
  }
  const chars = Array.from(c.text);
  if (!(at > 0 && at < chars.length)) return null;
  return [{ ...c, text: chars.slice(0, at).join('') }, { ...c, text: chars.slice(at).join(''), note: undefined, labels: undefined }];
}
function contentsMerge(a, b) {
  return { ...a, kind: a.kind === b.kind ? a.kind : 'merged', text: a.text + b.text,
    tokens: (a.tokens && b.tokens) ? a.tokens.concat(b.tokens) : null, model: a.model === b.model ? a.model : null,
    note: [a.note, b.note].filter(Boolean).join('\n') || undefined, labels: [...(a.labels || []), ...(b.labels || [])] };
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
const depthOf = (w, id) => pathTo(w, id).length - 1;

// ------------------------------------------------------------------------------------------ history (undo/redo)
// Mirrors universal-weave's action-queue wrapper by recording full snapshots (weave + ui) before each mutation.
function snapshot() { return { weave: clone(S.weave), collapsed: [...S.collapsed], label: '' }; }
function mutate(label, fn) {
  const before = snapshot(); before.label = label;
  const r = fn(S.weave);
  if (r === false) return false;
  S.history.past.push(before); if (S.history.past.length > 200) S.history.past.shift();
  S.history.future = [];
  touch(true);
  return true;
}
function restore(snap) { S.weave = snap.weave; S.collapsed = new Set(snap.collapsed); S.splitMode = null; S.editing = null; S.noting = null; touch(true); }
function undo() { const s = S.history.past.pop(); if (!s) return status('nothing to undo'); const cur = snapshot(); cur.label = s.label; S.history.future.push(cur); restore(s); status(`undid: ${s.label}`); }
function redo() { const s = S.history.future.pop(); if (!s) return status('nothing to redo'); const cur = snapshot(); cur.label = s.label; S.history.past.push(cur); restore(s); status(`redid: ${s.label}`); }

// ------------------------------------------------------------------------------------------ state + persistence
function touch(rerenderPrompt = false) {
  const w = S.weave; w.metadata.modified = now(); w.metadata.ui = { collapsed: [...S.collapsed] };
  try { localStorage.setItem(LS_KEY, JSON.stringify({ name: S.weaveName, weave: w })); } catch { /* ignore */ }
  renderTree(); renderReading(); renderBookmarks(); renderNodeInfo(); if (rerenderPrompt) syncPromptBox();
  $('#weave-info').textContent = `${Object.keys(w.nodes).length} nodes · ${w.roots.length} root(s) · modified ${w.metadata.modified.slice(11, 19)} · undo ${S.history.past.length}`;
  $('#undo-btn').disabled = !S.history.past.length; $('#redo-btn').disabled = !S.history.future.length;
}
function autoCollapse(w) {
  const onPath = new Set(w.active ? pathTo(w, w.active) : []);
  for (const id of orderedIds(w)) if (w.nodes[id].to.length && depthOf(w, id) >= AUTO_COLLAPSE_DEPTH && !onPath.has(id)) S.collapsed.add(id);
}
function loadWeave(w, name, { tidy = true } = {}) {
  S.weave = w; S.weaveName = name || w.metadata?.name || ''; S.collapsed = new Set(w.metadata?.ui?.collapsed || []);
  S.history = { past: [], future: [] };
  if (tidy && !w.metadata?.ui?.collapsed?.length) autoCollapse(w);
  $('#weave-name').value = S.weaveName; S.splitMode = null; S.editing = null; S.noting = null;
  touch(true);
}
function rootOfActive() { const w = S.weave; if (w.active && w.nodes[w.active]) return pathTo(w, w.active)[0]; return w.roots[0] || null; }
function syncPromptBox() {
  const r = rootOfActive(); const ta = $('#loom-prompt');
  const text = r ? S.weave.nodes[r].contents.text : '';
  if (ta.value !== text) ta.value = text;
  const sel = $('#loom-library'); const lib = r ? S.weave.nodes[r].contents.library : null;
  if (sel.options.length) sel.value = (lib && libraryItem(lib.id)) ? lib.id : (libraryByText(text)?.id || 'custom');
}
let promptTimer = null;
function onPromptInput() {
  clearTimeout(promptTimer);
  promptTimer = setTimeout(() => {
    const text = $('#loom-prompt').value; const r = rootOfActive();
    if (!r) { if (text) mutate('new prompt', w => { insert(w, mkNode({ contents: { kind: 'prompt', text, tokens: null, created: now() }, active: true })); }); return; }
    if (S.weave.nodes[r].contents.text === text) return;
    mutate('edit prompt', w => { const n = w.nodes[r]; n.contents = { ...n.contents, kind: 'prompt', text, tokens: null, edited: now(), library: libraryByText(text) ? n.contents.library : undefined }; });
  }, 300);
}

// ------------------------------------------------------------------------------------------ sampler + servers
function samplerFrom(prefix) {
  return { n: +$(`#${prefix}-n, #${prefix}-k`).value || 1, max_tokens: +$(`#${prefix}-max`).value || 40,
    temperature: +$(`#${prefix}-temp`).value, top_p: +$(`#${prefix}-topp`).value, stop: parseStop($(`#${prefix}-stop`)?.value ?? '\\n\\n') };
}
function serverByUrl(url) { return S.servers.find(s => s.url === url); }
function liveServers() { return S.servers.filter(s => s.up && s.model); }
function fillServerSelect(sel, keep) {
  const prev = keep ? sel.value : null; sel.innerHTML = '';
  for (const s of S.servers) {
    const o = el('option', null, `${s.model || '(no name)'} @ ${s.url.replace('http://', '')}${s.up ? '' : ' (down)'}`);
    o.value = s.url; o.disabled = !s.up || !s.model; sel.appendChild(o);
  }
  const first = liveServers()[0];
  sel.value = (prev && serverByUrl(prev)?.up) ? prev : (first ? first.url : '');
}
async function refreshServers() {
  try {
    const j = await api('/api/servers');
    S.servers = j.servers; S.serving = j.serving; S.checkpoints = j.checkpoints; S.version = j.version || {}; S.serve = j.serve || {}; S.probed = true;
    fillServerSelect($('#loom-server'), true); fillServerSelect($('#cmp-a'), true); fillServerSelect($('#cmp-b'), true);
    if (liveServers().length > 1 && $('#cmp-a').value === $('#cmp-b').value) $('#cmp-b').value = liveServers()[1].url;
    const st = $('#servers-status'); st.innerHTML = '';
    S.servers.forEach((s, i) => {
      const t = el(s.up ? 'b' : 's', null, `${s.url.replace('http://127.0.0.1', '')} ${s.model || (s.up ? '(name unknown)' : 'down')}`);
      t.title = s.path || s.error || ''; st.appendChild(t); if (i < S.servers.length - 1) st.appendChild(document.createTextNode('  '));
    });
    if (!liveServers().length) toast('no live model server: start mlx_lm.server on :8124 or :8125', 'err');
    renderTree(); renderStart();
  } catch (e) { fail('servers', e); }
}
// The resident h is the first configured server (:8124 by default); fall back to any live one.
function residentServer() { const first = S.servers[0]; return (first?.up && first?.model) ? first : (liveServers()[0] || null); }

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
  const w = S.weave; const root = $('#tree'); if (!w) return; root.innerHTML = '';
  if (!w.roots.length) { root.appendChild(el('p', 'hint', 'Empty weave: pick a prompt from the library on the left (or press "frame", or type one), then "expand selected" — or go to Start here and press Ask h.')); return; }
  const onPath = new Set(w.active ? pathTo(w, w.active) : []);
  const ul = el('ul'); for (const r of w.roots) ul.appendChild(renderNode(r, onPath)); root.appendChild(ul);
  const act = $('.node.active', root); if (act && !isVisible(act)) act.scrollIntoView({ block: 'nearest' });
}
function isVisible(e) { const r = e.getBoundingClientRect(); const p = $('#tree-wrap').getBoundingClientRect(); return r.top >= p.top && r.bottom <= p.bottom; }
function renderNode(id, onPath) {
  const w = S.weave; const n = w.nodes[id]; const c = n.contents; const li = el('li');
  const card = el('div', 'node' + (onPath.has(id) ? ' on-path' : '') + (w.active === id ? ' active' : '') + (n.bookmarked ? ' bookmarked' : '') + (S.splitMode === id ? ' split-mode' : ''));
  card.dataset.id = id;
  const head = el('div', 'head');
  head.appendChild(el('span', 'kind', c.kind || 'node'));
  if (c.library) { const L = el('span', 'lib', `${c.library.kind} · ${c.library.title}`); L.title = 'from the prompt library'; head.appendChild(L); }
  if (c.model) { const m = el('span', null, modelShort(c.model)); m.title = `${c.model} @ ${c.server || ''}`; head.appendChild(m); }
  const st = statsOf(c.tokens);
  if (st) head.appendChild(el('span', null, `${st.n} tok · lp ${fmt(st.mean)} · surprisal ${fmt(st.surprisal)}`));
  else head.appendChild(el('span', null, `${Array.from(c.text).length} chars`));
  if (c.finish_reason === 'length') head.appendChild(el('span', null, 'cut'));
  if (c.sampler) { const sp = el('span', null, `t${c.sampler.temperature} p${c.sampler.top_p}`); sp.title = JSON.stringify(c.sampler); head.appendChild(sp); }
  const prov = S.prov.get(c.text);
  if (prov) { const p = el('span', 'prov' + (prov.longest_match >= 16 ? ' hot' : ''), `haunt ${prov.longest_match}/${prov.tokens}`); p.title = `longest exact corpus match ${prov.longest_match} tokens of ${prov.tokens}; coverage@8 ${fmt(prov.coverage?.['8'] * 100, 0)}%`; head.appendChild(p); }
  if (c.labels?.length) { const L = el('span', 'labels'); for (const l of c.labels) { const s = el('span', l.label === 'KEEP' ? 'keep' : '', l.label); s.title = (l.correction ? 'correction: ' + l.correction : '') + (l.note ? '\n' + l.note : ''); L.appendChild(s); } head.appendChild(L); }
  if (c.note) head.appendChild(el('span', 'note', '✎'));
  if (n.to.length) { const b = el('span', null, `${S.collapsed.has(id) ? '▸' : '▾'} ${n.to.length}`); b.style.cursor = 'pointer'; b.title = 'collapse / uncollapse children (c)'; b.onclick = e => { e.stopPropagation(); toggleCollapse(id); }; head.appendChild(b); }
  card.appendChild(head);
  if (S.editing === id) {
    const ta = el('textarea', 'edit'); ta.value = c.text; card.appendChild(ta); setTimeout(() => ta.focus(), 0);
    const row = el('div', 'actions');
    const save = el('button', 'primary', 'save'); save.onclick = () => { const text = ta.value; S.editing = null; mutate('edit text', w => { const nn = w.nodes[id]; nn.contents = { ...nn.contents, kind: nn.contents.kind === 'prompt' ? 'prompt' : 'edit', text, tokens: null, edited: now() }; }); };
    const cancel = el('button', null, 'cancel'); cancel.onclick = () => { S.editing = null; touch(); };
    ta.onkeydown = e => { if (e.key === 'Escape') cancel.onclick(); if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') save.onclick(); };
    row.append(save, cancel); card.appendChild(row);
  } else if (S.noting === id) {
    const ta = el('textarea', 'edit'); ta.value = c.note || ''; ta.placeholder = 'note'; card.appendChild(ta); setTimeout(() => ta.focus(), 0);
    const row = el('div', 'actions');
    const save = el('button', 'primary', 'save note'); save.onclick = () => { const note = ta.value.trim(); S.noting = null; mutate('note', w => { w.nodes[id].contents.note = note || undefined; }); };
    const cancel = el('button', null, 'cancel'); cancel.onclick = () => { S.noting = null; touch(); };
    ta.onkeydown = e => { if (e.key === 'Escape') cancel.onclick(); if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') save.onclick(); };
    row.append(save, cancel); card.appendChild(row);
  } else {
    const body = renderTokens(c, { matches: prov });
    body.onclick = e => {
      const tok = e.target.closest('.tok');
      if (S.splitMode === id && tok) { e.stopPropagation(); const at = +tok.dataset.at; S.splitMode = null; if (!mutate('split', w => split(w, id, at, uuid()))) { status('cannot split there', true); touch(); } return; }
      selectNode(id);
    };
    card.appendChild(body);
    if (c.note) card.appendChild(el('div', 'note-text', c.note));
    const isActive = w.active === id; const N = +$('#loom-n').value || 1;
    const mk = (row, label, title, fn, cls) => { const b = el('button', cls || null, label); b.title = title; b.onclick = e => { e.stopPropagation(); fn(); }; row.appendChild(b); return b; };
    if (isActive) {
      // The selected node carries its navigation as buttons (the arrow keys do the same).
      const nav = el('div', 'nav'); nav.appendChild(el('span', 'sel', 'selected'));
      const sibs = n.from !== null ? w.nodes[n.from].to : w.roots; const i = sibs.indexOf(id);
      mk(nav, '↑ parent', 'select the parent (↑)', () => goTo(n.from)).disabled = n.from === null;
      mk(nav, '↓ child', 'select the first child (↓)', () => { S.collapsed.delete(id); goTo(n.to[0]); }).disabled = !n.to.length;
      mk(nav, '← prev', 'select the previous sibling (←)', () => goTo(sibs[i - 1])).disabled = i <= 0;
      mk(nav, 'next →', 'select the next sibling (→)', () => goTo(sibs[i + 1])).disabled = i < 0 || i >= sibs.length - 1;
      nav.appendChild(el('span', null, '· Enter expands · ? all keys'));
      card.appendChild(nav);
    }
    const act = el('div', 'actions');
    const expandBtn = s => mk(act, `+${N} ${modelShort(s.model)}`, `expand: sample ${N} continuation(s) of this node from ${s.model} (${s.url})${isActive ? ' — Enter' : ''}`, () => expand(id, s), 'primary');
    const live = liveServers();
    if (isActive) for (const s of live) expandBtn(s);
    else if (live.length) expandBtn(serverByUrl($('#loom-server').value) || live[0]);
    if (!live.length) { const b = el('button', 'primary', '+ (no server)'); b.disabled = true; b.title = 'no live model server: start one and press "servers"'; act.appendChild(b); }
    if (!isActive) mk(act, 'select', 'make this the selected node (clicking its text does the same)', () => selectNode(id));
    else {
      mk(act, n.bookmarked ? '★' : '☆', 'bookmark (b)', () => mutate('bookmark', w => setBookmarked(w, id, !n.bookmarked)));
      mk(act, 'deactivate', 'move the selection to the parent (x)', () => mutate('deactivate', w => setActive(w, id, false)));
      mk(act, 'edit', 'edit the text (e); drops token logprobs', () => { S.editing = id; S.noting = null; S.splitMode = null; touch(); });
      mk(act, 'note', 'attach a note (n)', () => { S.noting = id; S.editing = null; S.splitMode = null; touch(); });
      mk(act, 'label', 'failure label or KEEP (l)', () => openLabelDialog({ kind: 'loom', id }));
      mk(act, S.splitMode === id ? 'splitting…' : 'split', 'then click the token that should start the new child', () => { S.splitMode = S.splitMode === id ? null : id; touch(); });
      if (n.from !== null && w.nodes[n.from]?.to.length === 1) mk(act, 'merge ↑', 'merge into the parent (only child)', () => mutate('merge', w => mergeWithParent(w, id) !== null));
      mk(act, 'haunt', 'provenance scan this node (h)', () => haunt([{ id, text: c.text }]).then(() => touch()));
      mk(act, '→ cf', 'counterfactual: edit this path and score the reply', () => { cfFromNode(id); showTab('counterfactual'); });
      mk(act, '✕', 'delete this node and its subtree (Delete)', () => deleteNode(id));
    }
    card.appendChild(act);
  }
  li.appendChild(card);
  if (n.to.length && !S.collapsed.has(id)) { const ul = el('ul'); for (const cid of n.to) ul.appendChild(renderNode(cid, onPath)); li.appendChild(ul); }
  return li;
}
function selectNode(id) { const w = S.weave; if (!w.nodes[id]) return; if (w.active === id) return; mutate('select', w2 => setActive(w2, id, true)); }
function goTo(target) { if (!target || !S.weave.nodes[target]) return; for (const p of pathTo(S.weave, target)) if (p !== target) S.collapsed.delete(p); selectNode(target); }
function toggleCollapse(id) { S.collapsed.has(id) ? S.collapsed.delete(id) : S.collapsed.add(id); touch(); }
function deleteNode(id) {
  const n = S.weave.nodes[id]; if (!n) return;
  if (n.to.length === 0 || confirm(`delete ${n.to.length} descendant(s) too?`)) mutate('delete', w => { remove(w, id); });
}
function renderReading() {
  const w = S.weave; const out = $('#reading'); out.innerHTML = '';
  if (!w.active) { $('#reading-stats').textContent = ''; out.appendChild(el('span', 'hint', 'Click a node in the tree: its path from the root reads here as one text, sampled tokens shaded by logprob.')); return; }
  const ids = pathTo(w, w.active); let all = [];
  for (const id of ids) {
    const c = w.nodes[id].contents; const seg = el('span', 'seg ' + (c.tokens ? '' : 'prompt') + (id === w.active ? ' active' : ''));
    if (c.tokens) { c.tokens.forEach((t, i) => seg.appendChild(tokenSpan(t.text, t.logprob, i))); all = all.concat(c.tokens); }
    else seg.textContent = c.text;
    seg.title = `${c.kind} ${id.slice(0, 8)}`; seg.onclick = () => selectNode(id);
    out.appendChild(seg);
  }
  const st = statsOf(all); $('#reading-stats').textContent = `${ids.length} nodes · ${Array.from(pathText(w, w.active)).length} chars` + (st ? ` · sampled ${statsText(st)}` : '');
}
function renderNodeInfo() {
  const w = S.weave; const box = $('#node-info'); box.innerHTML = '';
  if (!w.active || !w.nodes[w.active]) { box.appendChild(el('span', 'hint', 'No node selected: click one to see how it was produced (model, checkpoint, sampler).')); return; }
  const c = w.nodes[w.active].contents; const dl = el('dl');
  const row = (k, v) => { if (v == null || v === '') return; dl.appendChild(el('dt', null, k)); dl.appendChild(el('dd', null, typeof v === 'string' ? v : JSON.stringify(v))); };
  row('id', w.active.slice(0, 8)); row('kind', c.kind); row('library', c.library ? `${c.library.kind} · ${c.library.title}` : null); row('created', c.created); row('edited', c.edited);
  const r = c.repro || {};
  row('model', c.model); row('checkpoint', r.checkpoint); row('server', c.server); row('backend', r.backend);
  row('sampler', c.sampler ? `t=${c.sampler.temperature} p=${c.sampler.top_p} max=${c.sampler.max_tokens} stop=${JSON.stringify(c.sampler.stop)}${c.sampler.repetition_penalty ? ' rp=' + c.sampler.repetition_penalty : ''}` : null);
  row('seed', r.seed ?? (c.model ? 'none (mlx sampler)' : null)); row('tokenizer', r.tokenizer_sha); row('explorer', r.explorer);
  if (c.server === 'observatory') row('proxy', 'routed through :8126 (logprobs stripped; observatory record)');
  if (c.observatory) row('observatory', `${c.observatory.date} #${c.observatory.index} cand ${c.observatory.candidate} overlap ${fmt(c.observatory.overlap, 2)} ${c.observatory.accepted ? 'accepted' : 'rejected'}${c.observatory.chosen ? ' chosen' : ''}`);
  row('note', c.note);
  if (c.labels?.length) row('labels', c.labels.map(l => l.label + (l.correction ? ` → "${short(l.correction, 40)}"` : '')).join('; '));
  box.appendChild(dl);
}
function renderBookmarks() {
  const w = S.weave; const ul = $('#bookmarks'); ul.innerHTML = '';
  for (const id of w.bookmarked) { const n = w.nodes[id]; if (!n) continue; const li = el('li', null, '★ ' + short(n.contents.text, 48)); li.title = n.contents.text; li.onclick = () => { for (const p of pathTo(w, id)) S.collapsed.delete(p); selectNode(id); }; ul.appendChild(li); }
  if (!w.bookmarked.length) ul.appendChild(el('li', 'hint', 'none'));
}

// ------------------------------------------------------------------------------------------ keyboard
function keyNav(e) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') { e.preventDefault(); saveWeave(); return; }  // works inside fields too
  if (inField()) return;
  const w = S.weave; const tab = $('.tabs button.on')?.dataset.tab;
  if (e.key === '?' ) { $('#help').showModal(); return; }
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); e.shiftKey ? redo() : undo(); return; }
  if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key.toLowerCase() === 'c') { e.preventDefault(); copyTranscript(); return; }
  if (/^[1-9]$/.test(e.key) && !e.metaKey && !e.ctrlKey) { const b = $$('.tabs button')[+e.key - 1]; if (b) showTab(b.dataset.tab); return; }
  if (e.key === 'Escape') { if (S.splitMode || S.editing || S.noting) { S.splitMode = null; S.editing = null; S.noting = null; touch(); } return; }
  if (tab !== 'loom' || !w) return;
  const id = w.active; const n = id ? w.nodes[id] : null;
  switch (e.key) {
    case 'ArrowUp': e.preventDefault(); if (n?.from) goTo(n.from); break;
    case 'ArrowDown': e.preventDefault(); if (n?.to.length) { S.collapsed.delete(id); goTo(n.to[0]); } break;
    case 'ArrowLeft': case 'ArrowRight': {
      e.preventDefault(); if (!n) break;
      const sibs = n.from ? w.nodes[n.from].to : w.roots; const i = sibs.indexOf(id);
      const j = e.key === 'ArrowLeft' ? i - 1 : i + 1; if (j >= 0 && j < sibs.length) goTo(sibs[j]); break;
    }
    case 'Enter': e.preventDefault(); if (id) expand(id); break;
    case 'e': if (id) { S.editing = id; S.noting = null; touch(); } break;
    case 'n': if (id) { S.noting = id; S.editing = null; touch(); } break;
    case 'l': if (id) openLabelDialog({ kind: 'loom', id }); break;
    case 'b': if (id) mutate('bookmark', w2 => setBookmarked(w2, id, !n.bookmarked)); break;
    case 'x': if (id) mutate('deactivate', w2 => setActive(w2, id, false)); break;
    case 'c': if (id && n.to.length) toggleCollapse(id); break;
    case 'h': if (id) haunt([{ id, text: n.contents.text }]).then(() => touch()); break;
    case 'Delete': case 'Backspace': e.preventDefault(); if (id) deleteNode(id); break;
    default: return;
  }
}
async function copyTranscript() {
  const w = S.weave; if (!w.active) return status('no active node', true);
  const text = pathText(w, w.active);
  try { await navigator.clipboard.writeText(text); toast('transcript copied', 'ok'); } catch { window.prompt('copy:', text); }
}
async function copyJson() { try { await navigator.clipboard.writeText(JSON.stringify(S.weave, null, 1)); toast('weave JSON copied', 'ok'); } catch { window.prompt('copy:', JSON.stringify(S.weave)); } }

// ------------------------------------------------------------------------------------------ expand
function sampleContents(msg) {
  return { kind: 'sample', text: msg.text, tokens: msg.tokens, model: msg.model, server: msg.server, sampler: msg.sampler,
    finish_reason: msg.finish_reason, seconds: msg.seconds, created: msg.created, repro: msg.repro };
}
async function expand(id, server) {
  const w = S.weave; if (!w.nodes[id]) return;
  server = server || serverByUrl($('#loom-server').value) || liveServers()[0];
  if (!server || !server.up || !server.model) return fail('expand', new Error('no live model server (start one on :8124/:8125, then "servers")'));
  const cfg = samplerFrom('loom'); const prompt = pathText(w, id);
  busy(1, `sampling ${cfg.n}× from ${server.model}…`);
  let got = 0; const t0 = performance.now(); const before = snapshot(); before.label = 'expand';
  try {
    for await (const msg of generate({ ...cfg, server: server.url, model: server.model, prompt })) {
      if (msg.type === 'sample') { if (insert(w, mkNode({ from: id, contents: sampleContents(msg) }))) { got++; S.collapsed.delete(id); touch(); } }
      else if (msg.type === 'error') fail('sample', new Error(msg.message));
    }
  } catch (e) { fail('expand', e); }
  finally {
    S.busy--; status(`${got} sample(s) from ${server.model} in ${((performance.now() - t0) / 1000).toFixed(1)}s`);
    if (got) { S.history.past.push(before); S.history.future = []; touch(); }
  }
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
    } catch (e) { fail('haunt', e); } finally { S.busy--; }
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
  if (!t) { box.appendChild(el('span', 'hint', 'Nothing selected: pick a node in the loom first, then press scan here (or h there).')); out.appendChild(el('p', 'hint', 'Select a node in the loom, then scan: the longest exact corpus match, coverage, and the documents it came from appear here.')); return; }
  const c = w.nodes[t.id].contents; const rec = S.prov.get(t.text);
  box.appendChild(t.scope === 'node' ? renderTokens(c, { matches: rec }) : el('div', 'text plain', t.text));
  if (!rec) { out.appendChild(el('p', 'hint', 'Not scanned yet: press scan (or h in the loom) to search the training corpus for this text.')); return; }
  out.appendChild(provCard(rec));
}
function provCard(rec) {
  const wrap = el('div');
  const card = el('div', 'prov-card');
  const stats = el('div', 'stats');
  stats.innerHTML = `<span>tokens <b>${rec.tokens}</b></span><span>longest exact match <b>${rec.longest_match}</b> tokens</span><span>spans <b>${rec.span_count}</b></span>`;
  card.appendChild(stats);
  const cov = el('div', 'stats');
  for (const k of Object.keys(rec.coverage || {})) { const v = rec.coverage[k]; const s = el('span'); s.innerHTML = `coverage@${k} <b>${fmt(v * 100, 0)}%</b> `; const bar = el('span', 'bar'); const i = el('i'); i.style.width = `${Math.round(v * 100)}%`; bar.appendChild(i); s.appendChild(bar); cov.appendChild(s); }
  card.appendChild(cov); wrap.appendChild(card);
  if (rec.top_documents?.length) {
    const t2 = el('table'); t2.innerHTML = '<tr><th>source</th><th>path</th><th class="num">quoted tok</th><th class="num">doc tok</th><th class="num">token offset</th></tr>';
    for (const d of rec.top_documents) { const tr = el('tr'); tr.innerHTML = `<td>${d.source ?? ''}</td><td class="path"></td><td class="num">${d.quoted_tokens ?? ''}</td><td class="num">${d.tokens ?? ''}</td><td class="num">${d.token_offset ?? ''}</td>`; tr.children[1].textContent = d.path || d.id || ''; t2.appendChild(tr); }
    const c2 = el('div', 'prov-card'); c2.appendChild(el('h3', null, 'top documents')); c2.appendChild(t2); wrap.appendChild(c2);
  }
  if (rec.longest_spans?.length) {
    const c3 = el('div', 'prov-card span-list'); c3.appendChild(el('h3', null, 'longest spans'));
    for (const sp of rec.longest_spans) {
      const d = el('div', 'cand'); const h = el('div', 'head');
      h.textContent = `${sp.length} tokens · query offset ${sp.query_offset} · ${sp.occurrences} occurrence(s) in ${sp.distinct_documents} doc(s)${sp.crosses_document_boundary ? ' · crosses boundary' : ''} · ${sp.document?.source || ''} ${sp.document?.path || ''}`;
      d.appendChild(h); d.appendChild(el('div', 'text plain', sp.text ?? '(no --decode text)')); c3.appendChild(d);
    }
    wrap.appendChild(c3);
  }
  if (!rec.top_documents?.length && !rec.longest_spans?.length) wrap.appendChild(el('p', 'hint', 'no exact spans at or above the smallest threshold'));
  return wrap;
}

// ------------------------------------------------------------------------------------------ observatory
// Lists the days (newest first) and, unless day:false, loads the newest. Concurrent callers share one load.
function loadObsDates({ day = true } = {}) {
  if (S.obs.loading) return S.obs.loading;
  S.obs.loading = (async () => {
    try {
      const j = await api('/api/observatory'); S.obs.dates = j.dates; const sel = $('#obs-date'); sel.innerHTML = '';
      for (const d of j.dates) { const o = el('option', null, `${d.date} (${d.records})`); o.value = d.date; sel.appendChild(o); }
      renderStart();
      if (!j.dates.length) { $('#obs-summary').textContent = `Nothing to replay yet: no files in ${j.dir}. The room proxy writes one per day the room speaks to h.`; return; }
      if (day) await loadObsDay(sel.value);
    } catch (e) { fail('observatory', e); } finally { S.obs.loading = null; }
  })();
  return S.obs.loading;
}
async function loadObsDay(date) {
  busy(1, `loading ${date}…`);
  try { S.obs.day = await api(`/api/observatory?date=${encodeURIComponent(date)}`); S.obs.selected = null; renderObsSummary(); renderObsList(); renderObsDetail(); status(`${date}: ${S.obs.day.records.length} records`); }
  catch (e) { fail('observatory', e); } finally { S.busy--; }
}
// "Replay the room": the observatory on the newest day, opened at its most recent record.
async function replayRoom() {
  showTab('observatory');
  if (!S.obs.day) await loadObsDates();
  const latest = S.obs.dates[0]?.date;
  if (latest && S.obs.day?.date !== latest) { $('#obs-date').value = latest; await loadObsDay(latest); }
  const recs = S.obs.day?.records || [];
  if (recs.length && S.obs.selected == null) { S.obs.selected = recs[recs.length - 1].index; renderObsList(); renderObsDetail(); }
}
function renderObsSummary() {
  const s = S.obs.day.summary; const box = $('#obs-summary');
  box.innerHTML = `records <b>${s.records}</b><br>accepted <b>${s.accepted}</b> (${fmt(s.acceptance_rate * 100, 0)}%)<br>mean candidates tried <b>${fmt(s.mean_candidates)}</b><br>mean seconds <b>${fmt(s.mean_seconds)}</b><br>mean chosen logprob <b>${fmt(s.mean_chosen_logprob)}</b><br>dropped echo turns <b>${s.dropped_echo_turns}</b><br>models <b></b>`;
  box.querySelector('b:last-child').textContent = (s.models || []).join(', ') || '—';
}
function renderObsList() {
  const box = $('#obs-list'); box.innerHTML = ''; const t = el('table');
  if (!S.obs.day.records.length) { box.appendChild(el('p', 'hint', 'No records on this day: pick another day above.')); return; }
  t.innerHTML = '<tr><th>#</th><th>time</th><th>visitor</th><th class="num">tried</th><th>ok</th><th class="num">s</th></tr>';
  for (const r of S.obs.day.records) {
    const tr = el('tr', S.obs.selected === r.index ? 'on' : ''); const chosen = r.candidates?.find(c => c.text === r.chosen);
    tr.innerHTML = `<td>${r.index}</td><td>${(r.time || '').slice(11, 19)}</td><td></td><td class="num">${r.candidates?.length ?? 0}</td><td class="${r.chosen_accepted ? 'ok' : 'bad'}">${r.chosen_accepted ? '✓' : '✗'}</td><td class="num">${fmt(r.seconds, 1)}</td>`;
    tr.children[2].textContent = short(r.last_visitor, 28); tr.title = `chosen: ${short(r.chosen, 120)}${chosen ? ` (mean lp ${fmt(chosen.mean_logprob)})` : ''}`;
    tr.onclick = () => { S.obs.selected = r.index; renderObsList(); renderObsDetail(); };
    t.appendChild(tr);
  }
  box.appendChild(t);
  $('tr.on', t)?.scrollIntoView({ block: 'nearest' });
}
function renderObsDetail() {
  const out = $('#obs-detail'); out.innerHTML = '';
  const r = S.obs.day?.records.find(x => x.index === S.obs.selected);
  if (!r) { out.appendChild(el('p', 'hint', 'Pick a record on the left to see the prompt h saw, every candidate it tried, and the one it said.')); return; }
  const head = el('div', 'stats');
  head.innerHTML = `<span>${r.time}</span><span>model <b></b></span><span>proxy ${r.proxy_sha || ''}</span><span>sampler <b></b></span><span>${fmt(r.seconds)} s</span><span>dropped echo turns <b>${r.dropped_echo_turns}</b></span>`;
  head.querySelectorAll('b')[0].textContent = r.model || ''; head.querySelectorAll('b')[1].textContent = JSON.stringify(r.sampler);
  const row = el('div', 'row'); const toLoom = el('button', null, 'open in loom'); toLoom.onclick = () => obsToLoom(r); row.appendChild(toLoom);
  const toCf = el('button', null, '→ counterfactual'); toCf.onclick = () => { cfFromPrompt(r.prompt_cleaned || r.prompt_raw || '', r.chosen || ''); showTab('counterfactual'); }; row.appendChild(toCf);
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
    const lb = el('button', 'mini', 'label'); lb.onclick = () => openLabelDialog({ kind: 'observatory', record: r, candidate: i }); h.appendChild(lb);
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
      repro: { backend: 'chapterx→room_proxy→mlx_lm.server', proxy_sha: r.proxy_sha, seed: null, stop: r.sampler?.stop },
      observatory: { date: S.obs.day.date, index: r.index, candidate: i, overlap: c.overlap, accepted: c.accepted, chosen: c.text === r.chosen } } }));
  });
  loadWeave(w, w.metadata.name, { tidy: false }); showTab('loom');
}

// ------------------------------------------------------------------------------------------ labels
const LABEL_LIST = ['KEEP', 'echo', 'self-copy', 'false speak', 'missed intervention', 'wrong addressee', 'missed callback', 'generic assistant', 'frame leak', 'OCR corruption', 'dead strangeness', 'overquotation', 'proxy false positive', 'other'];
let labelCtx = null; let labelChoice = null;
function openLabelDialog(target) {
  labelCtx = target; labelChoice = null;
  const w = S.weave; let candidate = '', context = '', desc = '';
  if (target.kind === 'loom') { const n = w.nodes[target.id]; candidate = n.contents.text; context = pathText(w, n.from || target.id).slice(0, -(n.from ? 0 : candidate.length)); if (n.from) context = pathText(w, n.from); desc = `loom node ${target.id.slice(0, 8)}: “${short(candidate, 60)}”`; }
  else if (target.kind === 'observatory') { const c = target.record.candidates[target.candidate]; candidate = c.text; context = target.record.prompt_cleaned || target.record.prompt_raw || ''; desc = `observatory #${target.record.index} candidate ${target.candidate + 1}: “${short(candidate, 60)}”`; }
  else if (target.kind === 'pair') { candidate = target.text; context = target.context; desc = `pair ${target.n} ${target.side}`; }
  labelCtx.candidate = candidate; labelCtx.context = context;
  $('#label-target').textContent = desc;
  const box = $('#label-buttons'); box.innerHTML = '';
  for (const l of LABEL_LIST) { const b = el('button', l === 'KEEP' ? 'keep' : '', l); b.onclick = () => { labelChoice = l; $$('button', box).forEach(x => x.classList.toggle('on', x === b)); }; box.appendChild(b); }
  $('#label-correction').value = ''; $('#label-note').value = '';
  $('#label-dialog').showModal();
}
async function submitLabel() {
  if (!labelChoice) return toast('pick a label', 'err');
  const w = S.weave; const t = labelCtx; let meta = {};
  if (t.kind === 'loom') { const c = w.nodes[t.id].contents; meta = { checkpoint: c.repro?.checkpoint, model: c.model, server: c.server, sampler: c.sampler, proxy_sha: c.repro?.proxy_sha }; }
  if (t.kind === 'observatory') meta = { model: t.record.model, server: 'chapterx→room_proxy', sampler: t.record.sampler, proxy_sha: t.record.proxy_sha };
  const rec = { label: labelChoice, correction: $('#label-correction').value.trim() || null, note: $('#label-note').value.trim() || null, who: $('#label-who').value.trim() || 'ember',
    source: t.kind === 'loom' ? { kind: 'loom', weave: S.weaveName, node: t.id } : t.kind === 'observatory' ? { kind: 'observatory', date: S.obs.day.date, index: t.record.index, candidate: t.candidate } : { kind: 'pair', sheet: t.sheet, n: t.n, side: t.side },
    context: t.context, candidate: t.candidate, ...meta };
  try {
    await api('/api/labels', rec);
    if (t.kind === 'loom') mutate('label', w2 => { const c = w2.nodes[t.id].contents; c.labels = [...(c.labels || []), { label: rec.label, correction: rec.correction, note: rec.note, time: now() }]; });
    toast(`recorded ${rec.label}`, 'ok'); $('#label-dialog').close();
  } catch (e) { fail('label', e); }
}
async function loadLabels() {
  try {
    const j = await api('/api/labels'); S.labels = j;
    const box = $('#labels-summary'); box.innerHTML = `total <b>${j.total}</b><br>` + Object.entries(j.counts).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} <b>${v}</b>`).join('<br>');
    const out = $('#labels-recent'); out.innerHTML = '';
    const t = el('table'); t.innerHTML = '<tr><th>time</th><th>label</th><th>candidate</th><th>correction</th><th>source</th><th>model</th></tr>';
    for (const r of [...j.recent].reverse().slice(0, 100)) { const tr = el('tr'); tr.innerHTML = `<td>${(r.time || '').slice(5, 16)}</td><td>${r.label}</td><td></td><td></td><td></td><td></td>`; tr.children[2].textContent = short(r.candidate, 70); tr.children[3].textContent = short(r.correction, 50); tr.children[4].textContent = r.source?.kind ? `${r.source.kind} ${r.source.date || r.source.weave || r.source.sheet || ''} ${r.source.index ?? r.source.n ?? ''}` : ''; tr.children[5].textContent = modelShort(r.model); t.appendChild(tr); }
    if (j.recent.length) out.appendChild(t); else out.appendChild(el('p', 'hint', 'No labels yet: press l on a loom node, "label" on an observatory candidate, or judge a pair above.'));
    const pj = await api('/api/roombank'); S.pairs.sheets = pj.sheets; const sel = $('#pairs-list'); sel.innerHTML = '';
    for (const s of pj.sheets) { const o = el('option', null, s.stem); o.value = s.stem; sel.appendChild(o); }
    if (!pj.sheets.length) sel.appendChild(el('option', null, `(no sheets in ${pj.dir})`));
  } catch (e) { fail('labels', e); }
}
async function openPairs() {
  const stem = $('#pairs-list').value; if (!stem) return;
  try {
    const j = await api(`/api/roombank?sheet=${encodeURIComponent(stem)}`); S.pairs.sheet = j; S.pairs.answers = {};
    const out = $('#pairs-view'); out.innerHTML = ''; out.appendChild(el('h3', null, `${j.stem} · ${j.items.length} pairs · identities hidden`));
    for (const it of j.items) {
      const d = el('div', 'pair'); d.appendChild(el('div', 'hint', `#${it.n} · ${it.kind || ''} · state ${it.state_id}`));
      if (it.turns) { const tt = el('div', 'block'); tt.textContent = (it.frame ? it.frame + '\n\n' : '') + it.turns.map(([n, x]) => `${n}: ${x}`).join('\n\n'); d.appendChild(tt); }
      const ab = el('div', 'ab'); const A = el('div', null, 'A: ' + it.left); const B = el('div', null, 'B: ' + it.right); ab.append(A, B); d.appendChild(ab);
      const context = (it.frame ? it.frame + '\n\n' : '') + (it.turns || []).map(([n, x]) => `${n}: ${x}`).join('\n\n') + '\n\nh:';
      for (const q of j.questions) {
        const row = el('div', 'q'); row.appendChild(el('span', null, q));
        for (const opt of ['A', 'B', 'tie', 'neither']) { const b = el('button', 'mini', opt); b.onclick = () => { $$('button', row).forEach(x => x.classList.toggle('on', x === b)); S.pairs.answers[`${it.n}|${q}`] = opt; }; row.appendChild(b); }
        d.appendChild(row);
      }
      const row = el('div', 'row'); const rec = el('button', 'mini primary', 'record answers'); rec.onclick = async () => {
        const ans = j.questions.map(q => `${q} → ${S.pairs.answers[`${it.n}|${q}`] || '?'}`).join('; ');
        try { await api('/api/labels', { label: 'other', note: `pair answers: ${ans}`, who: $('#label-who').value || 'ember', source: { kind: 'pair', sheet: j.stem, n: it.n }, context, candidate: `A: ${it.left}\nB: ${it.right}` }); d.classList.add('done'); toast(`recorded pair #${it.n}`, 'ok'); } catch (e) { fail('pair', e); }
      }; row.appendChild(rec);
      const la = el('button', 'mini', 'label A'); la.onclick = () => openLabelDialog({ kind: 'pair', text: it.left, context, sheet: j.stem, n: it.n, side: 'A' }); row.appendChild(la);
      const lb = el('button', 'mini', 'label B'); lb.onclick = () => openLabelDialog({ kind: 'pair', text: it.right, context, sheet: j.stem, n: it.n, side: 'B' }); row.appendChild(lb);
      d.appendChild(row); out.appendChild(d);
    }
  } catch (e) { fail('pairs', e); }
}

// ------------------------------------------------------------------------------------------ compare
// One column per server, K samples each, streamed in parallel. "run A vs B" passes two; "run all up servers" and
// the start pane's "Compare the models" pass every live server.
async function runCompare(servers) {
  const prompt = $('#cmp-prompt').value; const cfg = samplerFrom('cmp');
  servers = (servers || []).filter(s => s?.up && s.model);
  if (!prompt.trim()) return fail('compare', new Error('pick a prompt from the library or type one, then run'));
  if (!servers.length) return fail('compare', new Error('no live server to compare (press "servers")'));
  recordRecent('compares', { prompt, servers: servers.map(s => s.model) });
  const box = $('#cmp-cols'); box.innerHTML = '';
  const run = async (srv, i) => {
    const col = el('div', 'col'); col.dataset.server = srv.url;
    const title = el('h3', null, `${servers.length === 2 ? 'AB'[i] + ' · ' : ''}${srv.model} @ ${srv.url.replace('http://', '')}`);
    const stats = el('div', 'hint', 'sampling…'); const out = el('div'); col.append(title, stats, out); box.appendChild(col);
    const samples = []; const t0 = performance.now();
    try {
      for await (const msg of generate({ ...cfg, n: cfg.n, server: srv.url, model: srv.model, prompt })) {
        if (msg.type === 'sample') { samples.push(msg); out.appendChild(renderSample(msg, prompt)); }
        else if (msg.type === 'error') fail('compare', new Error(msg.message));
      }
    } catch (e) { fail('compare', e); }
    const st = statsOf(samples.flatMap(s => s.tokens)); const stops = samples.filter(s => s.finish_reason === 'stop').length;
    stats.textContent = samples.length ? `${samples.length} samples · ${statsText(st)} · mean ${fmt(samples.reduce((x, s) => x + s.tokens.length, 0) / samples.length, 1)} tok · stopped ${stops}/${samples.length} · ${fmt(samples.reduce((x, s) => x + s.seconds, 0) / samples.length)} s each · ${((performance.now() - t0) / 1000).toFixed(1)} s total` : 'no samples (see the status line)';
  };
  busy(1, `compare: ${cfg.n}× each from ${servers.map(s => s.model).join(', ')}`);
  try { await Promise.all(servers.map(run)); } finally { S.busy--; status('compare done'); }
}
function runCompareAB() {
  const a = serverByUrl($('#cmp-a').value), b = serverByUrl($('#cmp-b').value);
  if (!a?.up || !b?.up) return fail('compare', new Error('pick two live servers'));
  return runCompare([a, b]);
}
function renderSample(msg, prompt, extra) {
  const d = el('div', 'sample'); const h = el('div', 'head'); const st = statsOf(msg.tokens);
  const left = el('span', null, `#${msg.index + 1} · ${statsText(st)} · ${msg.finish_reason} · ${msg.seconds}s`);
  const b = el('button', null, '→ loom'); b.title = 'add this sample under a root with this prompt in the loom';
  b.onclick = () => { sampleToLoom(prompt, msg); };
  h.append(left, b); d.appendChild(h);
  const t = el('div', 'text plain'); msg.tokens.forEach((tk, i) => t.appendChild(tokenSpan(tk.text, tk.logprob, i, `id ${tk.id}`))); d.appendChild(t);
  if (extra) d.appendChild(extra);
  return d;
}
function sampleToLoom(prompt, msg) {
  mutate('add sample', w => {
    let root = w.roots.find(r => w.nodes[r].contents.text === prompt);
    if (!root) { const n = mkNode({ contents: { kind: 'prompt', text: prompt, tokens: null, created: now() } }); insert(w, n); root = n.id; }
    const n = mkNode({ from: root, contents: sampleContents(msg), active: true }); insert(w, n); S.collapsed.delete(root);
  });
  status('added to loom');
}

// ------------------------------------------------------------------------------------------ counterfactual
const TURN_RE = /^(.{1,40}?): ([\s\S]*)$/;
function parseTurns(prompt) {
  // blocks separated by blank lines; a trailing "h:" is the reply cue and is dropped
  const blocks = prompt.replace(/\n\n\s*h:\s*$/, '').split(/\n\n/).map(b => b.trim()).filter(Boolean);
  return blocks.map(b => { const m = TURN_RE.exec(b); if (m && !m[1].includes('\n') && !m[1].includes('. ')) return { kind: 'turn', name: m[1], text: m[2] }; return { kind: 'frame', text: b }; });
}
const renderTurnsText = turns => turns.map(t => t.kind === 'turn' ? `${t.name}: ${t.text}` : t.text).join('\n\n') + '\n\nh:';
function cfFromNode(id) {
  const w = S.weave; const n = w.nodes[id]; if (!n) return;
  const context = n.from ? pathText(w, n.from) : '';
  const reply = n.from ? n.contents.text : '';
  cfFromPrompt(context || n.contents.text, reply);
}
function cfFromPrompt(prompt, reply) {
  S.cf.turns = parseTurns(prompt); S.cf.edited = clone(S.cf.turns); S.cf.reply = reply || ''; S.cf.results = null;
  $('#cf-reply').value = S.cf.reply; renderCf();
}
function renderTurns(box, turns, editable, changedIdx) {
  box.innerHTML = '';
  turns.forEach((t, i) => {
    const d = el('div', 'turn ' + t.kind + (t.name === 'h' ? ' h' : '') + (changedIdx?.has(i) ? ' changed' : ''));
    d.appendChild(el('span', 'idx', String(i)));
    if (t.kind === 'turn') {
      if (editable) { const nm = el('input'); nm.value = t.name; nm.oninput = () => { t.name = nm.value; }; d.appendChild(nm); const ta = el('textarea'); ta.rows = 1; ta.value = t.text; ta.oninput = () => { t.text = ta.value; }; d.appendChild(ta); }
      else { d.appendChild(el('span', 'name', t.name)); d.appendChild(el('span', 'text', t.text)); }
    } else {
      if (editable) { const ta = el('textarea'); ta.rows = 1; ta.value = t.text; ta.oninput = () => { t.text = ta.value; }; d.appendChild(ta); }
      else d.appendChild(el('span', 'text', t.text));
    }
    if (editable) {
      const ops = el('div', 'ops');
      const op = (label, title, fn) => { const b = el('button', null, label); b.title = title; b.onclick = fn; ops.appendChild(b); };
      op('↑', 'move up', () => { if (i > 0) { [turns[i - 1], turns[i]] = [turns[i], turns[i - 1]]; renderCf(); } });
      op('↓', 'move down', () => { if (i < turns.length - 1) { [turns[i + 1], turns[i]] = [turns[i], turns[i + 1]]; renderCf(); } });
      op('⇄', 'reassign speaker to the next name in the room', () => { if (t.kind !== 'turn') return; const names = [...new Set(turns.filter(x => x.kind === 'turn').map(x => x.name))]; t.name = names[(names.indexOf(t.name) + 1) % names.length] || t.name; renderCf(); });
      op('✕', 'delete this turn', () => { turns.splice(i, 1); renderCf(); });
      d.appendChild(ops);
    } else d.appendChild(el('span'));
    box.appendChild(d);
  });
}
function cfChanged() {
  const a = S.cf.turns, b = S.cf.edited; const changed = new Set();
  b.forEach((t, i) => { const o = a[i]; if (!o || o.kind !== t.kind || o.name !== t.name || o.text !== t.text) changed.add(i); });
  return changed;
}
function renderCf() {
  renderTurns($('#cf-true'), S.cf.turns, false); renderTurns($('#cf-edited'), S.cf.edited, true, cfChanged());
  if (!S.cf.turns.length) {
    $('#cf-true').appendChild(el('p', 'hint', 'Nothing here yet: take a path from the loom ("from loom", or "→ cf" on a node), pick a library prompt on the left, or send an observatory record here ("→ counterfactual").'));
    $('#cf-edited').appendChild(el('p', 'hint', 'The same turns, editable, will appear here.'));
  }
  const sel = $('#cf-scorer'); if (!sel.options.length) fillScorers(sel);
  renderCfResults();
}
function fillScorers(sel) {
  sel.innerHTML = '';
  for (const c of S.scorers) { const o = el('option', null, `${c.kind === 'base' ? 'base ' : ''}${c.name}`); o.value = c.path; sel.appendChild(o); }
  const leaf = S.scorers.find(c => c.path.includes('leaf-s1-e4')); if (leaf) sel.value = leaf.path;
}
async function score(checkpoint, items, onResult) {
  const out = {};
  for await (const msg of stream('/api/score', { checkpoint, items, ranks: true })) {
    if (msg.type === 'result') { out[msg.id] = msg.result; onResult?.(msg); }
    else if (msg.type === 'error') throw new Error(msg.message);
  }
  return out;
}
async function cfScore() {
  const reply = $('#cf-reply').value; S.cf.reply = reply; if (!reply.trim()) return fail('counterfactual', new Error('no reply text'));
  const checkpoint = $('#cf-scorer').value; if (!checkpoint) return fail('counterfactual', new Error('no scorer checkpoint'));
  const ctxTrue = renderTurnsText(S.cf.turns), ctxEdit = renderTurnsText(S.cf.edited);
  busy(1, 'scoring (first call compiles the model; the 0.5B takes seconds per call)…');
  try {
    const res = await score(checkpoint, [{ id: 'true', context: ctxTrue, text: reply }, { id: 'edited', context: ctxEdit, text: reply }], m => status(`scored ${m.id} in ${m.seconds}s${m.loaded ? ` (+${m.loaded}s load)` : ''}`));
    S.cf.results = { checkpoint, true: res.true, edited: res.edited }; renderCfResults();
  } catch (e) { fail('score', e); } finally { S.busy--; }
}
function renderCfResults() {
  const box = $('#cf-tokens'); box.innerHTML = ''; const sum = $('#cf-summary'); const r = S.cf.results;
  if (!r) { sum.textContent = S.cf.turns.length ? 'Not scored yet: change a turn on the right, keep or type the fixed reply, then "score both".' : 'Not scored yet.'; return; }
  const a = r.true, b = r.edited; if (!a || !b) { sum.textContent = 'incomplete'; return; }
  const dl = b.nll_sum != null && a.nll_sum != null ? (a.nll_sum - b.nll_sum) : null;
  sum.innerHTML = `scorer <b>${short(r.checkpoint.split('/').slice(-3).join('/'), 60)}</b><br>reply tokens <b>${a.n}</b><br>log p(reply | true) <b>${fmt(-a.nll_sum)}</b><br>log p(reply | edited) <b>${fmt(-b.nll_sum)}</b><br>Δ (edited − true) <b class="${dl > 0 ? 'ok' : 'bad'}">${fmt(dl)}</b> nats<br>mean per token <b>${fmt(-(a.nll_mean ?? 0), 3)} → ${fmt(-(b.nll_mean ?? 0), 3)}</b>`;
  const t = el('table', 'deltas'); t.innerHTML = '<tr><th>#</th><th>token</th><th class="num">lp true</th><th class="num">lp edited</th><th class="num">Δ lp</th><th></th><th class="num">rank true</th><th class="num">rank edited</th></tr>';
  const n = Math.min(a.tokens.length, b.tokens.length);
  for (let i = 0; i < n; i++) {
    const x = a.tokens[i], y = b.tokens[i]; const d = y.logprob - x.logprob; const tr = el('tr');
    tr.innerHTML = `<td class="num">${i}</td><td class="tok"></td><td class="num">${fmt(x.logprob, 2)}</td><td class="num">${fmt(y.logprob, 2)}</td><td class="num ${d > 0.05 ? 'pos' : d < -0.05 ? 'neg' : ''}">${d >= 0 ? '+' : ''}${fmt(d, 2)}</td><td></td><td class="num">${x.rank}</td><td class="num">${y.rank}</td>`;
    tr.children[1].textContent = visible(x.text); const bar = el('span', 'delta-bar'); bar.style.width = `${Math.min(80, Math.abs(d) * 20)}px`; bar.style.background = d > 0 ? 'var(--ok)' : 'var(--bad)'; tr.children[5].appendChild(bar);
    t.appendChild(tr);
  }
  box.appendChild(t);
}
async function cfRerun() {
  const server = serverByUrl($('#loom-server').value) || liveServers()[0]; if (!server) return fail('re-run', new Error('no live server'));
  const cfg = samplerFrom('loom'); const prompt = renderTurnsText(S.cf.edited); const out = $('#cf-rerun-out'); out.innerHTML = '';
  busy(1, `sampling ${cfg.n}× from the edited context…`);
  try { for await (const msg of generate({ ...cfg, server: server.url, model: server.model, prompt })) { if (msg.type === 'sample') out.appendChild(renderSample(msg, prompt)); else if (msg.type === 'error') fail('re-run', new Error(msg.message)); } }
  catch (e) { fail('re-run', e); } finally { S.busy--; status('re-run done'); }
}

// ------------------------------------------------------------------------------------------ room state (hbox)
async function rsRefresh() {
  const box = $('#rs-status');
  try {
    const j = await api('/api/roomstate/status');
    if (!j.up) { box.innerHTML = `<span class="bad">down</span> ${j.url}<br><span class="hint">${j.hint}</span><br><span class="hint">${j.error}</span>`; S.rs.rooms = []; renderRsRooms(); return; }
    const h = j.health; box.innerHTML = `<span class="ok">up</span> ${j.url}<br>checkpoint <b>${short((h.checkpoint || '').split('/').slice(-1)[0], 40)}</b><br>device ${h.device} · state ${h.state_dtype} · read ${h.read_mode}<br>rooms <b>${h.rooms}</b> · load ${fmt(h.load_seconds, 1)}s`;
    const rooms = await api('/api/roomstate/rooms'); S.rs.rooms = rooms.rooms || rooms || []; renderRsRooms();
  } catch (e) { box.innerHTML = `<span class="bad">error</span> ${e.message}`; }
}
function renderRsRooms() {
  const sel = $('#rs-rooms'); sel.innerHTML = '';
  for (const r of S.rs.rooms) { const id = r.room || r.id || r; const o = el('option', null, `${id}${r.token_count != null ? ` · ${r.token_count} tok` : ''}${r.branches != null ? ` · ${r.branches} br` : ''}`); o.value = id; sel.appendChild(o); }
  if (S.rs.room) sel.value = S.rs.room;
}
async function rsCreate() {
  const id = $('#rs-room-name').value.trim() || `room-${Date.now().toString(36)}`;
  busy(1, 'creating room…');
  try { await api('/api/roomstate/rooms', { room: id, frame: FRAME, replace: true }); S.rs.room = id; S.rs.history = []; S.rs.candidates = []; await rsRefresh(); await rsState(); toast(`room ${id} created with the bare frame`, 'ok'); }
  catch (e) { fail('room', e); } finally { S.busy--; }
}
async function rsOpen() { const id = $('#rs-rooms').value; if (!id) return; S.rs.room = id; S.rs.history = []; S.rs.candidates = []; await rsState(); await rsTranscript(); }
async function rsDelete() { const id = $('#rs-rooms').value; if (!id || !confirm(`delete room ${id} on hbox?`)) return; try { await api(`/api/roomstate/rooms/${encodeURIComponent(id)}`, null, 'DELETE'); if (S.rs.room === id) S.rs.room = null; await rsRefresh(); } catch (e) { fail('room', e); } }
async function rsTranscript() {
  if (!S.rs.room) return;
  try { const t = await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/transcript`); const box = $('#rs-transcript'); renderTurns(box, parseTurns((t.text || '') + '\n\nh:'), false); }
  catch (e) { fail('transcript', e); }
}
async function rsState() {
  if (!S.rs.room) return;
  try {
    const st = await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/state`);
    S.rs.history.push({ t: S.rs.history.length, tokens: st.token_count, bytes: st.state_bytes, diag: st.diagnostics, turns: st.turns });
    $('#rs-state').innerHTML = `room <b>${st.room}</b> · state ${st.state_id} · tokens <b>${st.token_count}</b> · cache len ${st.cache_length} · turns ${st.turns} · branches ${st.branches?.length ?? 0} · snapshots ${st.snapshots} · ${fmt(st.state_bytes / 1e6, 1)} MB · read ${st.read_mode}<br>tail: <span class="hint">${(st.transcript_tail || []).map(x => short(x, 50)).join(' ⏐ ')}</span>`;
    renderRsPlot();
  } catch (e) { fail('state', e); }
}
function renderRsPlot() {
  const box = $('#rs-plot'); box.innerHTML = ''; const H = S.rs.history; if (!H.length) return;
  const W = 800, Hh = 160, pad = 28; const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('viewBox', `0 0 ${W} ${Hh}`);
  const layers = H[0].diag?.layers || 0; const series = []; for (let l = 0; l < layers; l++) series.push(H.map(h => h.diag?.ssm_head_norm_mean?.[l] ?? 0));
  const all = series.flat(); const ymax = Math.max(1e-6, ...all); const x = i => pad + (H.length === 1 ? 0 : i * (W - 2 * pad) / (H.length - 1)); const y = v => Hh - pad + 8 - (v / ymax) * (Hh - 2 * pad);
  series.forEach((s, l) => { const p = document.createElementNS('http://www.w3.org/2000/svg', 'polyline'); p.setAttribute('points', s.map((v, i) => `${x(i)},${y(v)}`).join(' ')); p.setAttribute('fill', 'none'); p.setAttribute('stroke', `hsl(${(l / Math.max(1, layers)) * 300}, 60%, 50%)`); p.setAttribute('stroke-width', '1'); p.setAttribute('opacity', '0.7'); const t = document.createElementNS('http://www.w3.org/2000/svg', 'title'); t.textContent = `layer ${l}`; p.appendChild(t); svg.appendChild(p); });
  H.forEach((h, i) => { const tx = document.createElementNS('http://www.w3.org/2000/svg', 'text'); tx.setAttribute('x', x(i)); tx.setAttribute('y', Hh - 6); tx.setAttribute('font-size', '9'); tx.setAttribute('text-anchor', 'middle'); tx.setAttribute('fill', 'currentColor'); tx.textContent = `${h.tokens}t`; svg.appendChild(tx); });
  const yl = document.createElementNS('http://www.w3.org/2000/svg', 'text'); yl.setAttribute('x', 2); yl.setAttribute('y', 12); yl.setAttribute('font-size', '9'); yl.setAttribute('fill', 'currentColor'); yl.textContent = `max ${fmt(ymax, 2)}`; svg.appendChild(yl);
  box.appendChild(svg);
}
async function rsEvent() {
  if (!S.rs.room) return fail('event', new Error('open or create a room first'));
  const text = $('#rs-event').value.trim(); if (!text) return;
  busy(1, 'reading event into the state…');
  try { const r = await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/events`, { text }); $('#rs-event').value = ''; status(`read ${r.tokens ?? ''} tokens · state ${r.state_id ?? ''}`); await rsTranscript(); await rsState(); }
  catch (e) { fail('event', e); } finally { S.busy--; }
}
async function rsCandidates() {
  if (!S.rs.room) return fail('candidates', new Error('open or create a room first'));
  const body = { n: +$('#rs-n').value || 4, temperature: +$('#rs-temp').value, top_p: +$('#rs-topp').value, max_new_tokens: +$('#rs-max').value || 64, control: $('#rs-control').checked };
  busy(1, `forking ${body.n} candidates…`);
  try {
    const r = await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/candidates`, body); S.rs.candidates = r.candidates || [];
    const out = $('#rs-candidates-out'); out.innerHTML = '';
    const render = (c, control) => {
      const d = el('div', 'rs-cand' + (control ? ' control' : '')); const h = el('div', 'head');
      h.innerHTML = `<span>${control ? 'control' : 'branch'} <b>${c.branch}</b></span><span>${c.new_tokens} tok</span><span>lp sum <b>${fmt(c.logprob_sum, 1)}</b></span><span>${c.finish_reason}${c.clean_stop ? ' · clean stop' : ''}</span>`;
      if (!control) { const b = el('button', 'mini primary', 'commit'); b.onclick = () => rsCommit(c.branch); h.appendChild(b); const lb = el('button', 'mini', 'label'); lb.onclick = () => { openLabelDialog({ kind: 'pair', text: c.text, context: `(room ${S.rs.room}, persistent state)`, sheet: 'roomstate', n: c.branch, side: 'branch' }); }; h.appendChild(lb); }
      d.appendChild(h);
      const t = el('div', 'text plain'); (c.token_text || []).forEach((tx, i) => t.appendChild(tokenSpan(tx, c.logprobs?.[i], i, `id ${c.tokens?.[i]}`))); if (!c.token_text) t.textContent = c.text; d.appendChild(t);
      return d;
    };
    for (const c of S.rs.candidates) out.appendChild(render(c, false));
    if (r.control) { out.appendChild(el('div', 'hint', `control arm (fresh re-render): first-token KL vs persistent ${fmt(r.control.first_token_kl ?? r.control.kl, 4)}${r.control.identical != null ? ` · identical tokens ${r.control.identical}` : ''}`)); for (const c of r.control.candidates || []) out.appendChild(render(c, true)); }
    if (r.first_token_top) out.appendChild(el('div', 'hint', 'first token top: ' + r.first_token_top.map(t => `${JSON.stringify(t.text)} ${fmt(t.logprob, 2)}`).join('  ')));
    status(`${S.rs.candidates.length} candidates in ${fmt(r.seconds, 1)}s`);
  } catch (e) { fail('candidates', e); } finally { S.busy--; }
}
async function rsCommit(branch) { busy(1, 'committing…'); try { const r = await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/commit`, { branch }); toast(`committed ${branch}: ${short(r.text, 60)}`, 'ok'); $('#rs-candidates-out').innerHTML = ''; await rsTranscript(); await rsState(); } catch (e) { fail('commit', e); } finally { S.busy--; } }
async function rsSilence() { try { await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/silence`, {}); $('#rs-candidates-out').innerHTML = ''; toast('silence: forks discarded', 'ok'); await rsState(); } catch (e) { fail('silence', e); } }
async function rsSnapshot() { try { const r = await api(`/api/roomstate/rooms/${encodeURIComponent(S.rs.room)}/snapshot`, { persist: true }); toast(`snapshot ${r.snapshot ?? r.id ?? ''} saved`, 'ok'); await rsState(); } catch (e) { fail('snapshot', e); } }

// ------------------------------------------------------------------------------------------ population
function renderPopCheckpoints() {
  const box = $('#pop-checkpoints'); box.innerHTML = '';
  for (const c of S.scorers) { const l = el('label'); const cb = el('input'); cb.type = 'checkbox'; cb.value = c.path; cb.checked = c.kind === 'checkpoint' && /tokens-0*(417533162|793316586|793917970|1535061369)/.test(c.path); l.append(cb, document.createTextNode(' ' + c.name)); l.title = c.path; box.appendChild(l); }
}
async function popRun() {
  if (S.pop.running) return;
  const picks = $$('#pop-checkpoints input:checked').map(i => i.value); const prompt = $('#pop-prompt').value; const K = +$('#pop-k').value || 3;
  if (!picks.length) return fail('population', new Error('tick at least one checkpoint'));
  if (!prompt.trim()) return fail('population', new Error('pick a prompt from the library or type one'));
  S.pop.running = true; S.pop.stop = false;
  const cfg = { n: K, max_tokens: +$('#pop-max').value || 40, temperature: +$('#pop-temp').value, top_p: +$('#pop-topp').value, stop: ['\n\n'] };
  const grid = $('#pop-grid'); grid.innerHTML = ''; const statusBox = $('#pop-status');
  const doJudge = $('#pop-judge').checked, doHaunt = $('#pop-haunt').checked;
  const cells = new Map();
  for (const ck of picks) { const cell = el('div', 'pop-cell'); cell.appendChild(el('h4', null, ck.split('/').slice(-3).join('/'))); cell.appendChild(el('div', 'metrics', 'queued')); cells.set(ck, cell); grid.appendChild(cell); }
  try {
    for (const ck of picks) {
      if (S.pop.stop) break;
      const cell = cells.get(ck); cell.classList.add('switching'); const m = $('.metrics', cell); m.textContent = 'switching :8125 to this checkpoint…'; statusBox.textContent = `serving ${ck}`;
      let served;
      try { served = await api('/api/serve', { checkpoint: ck }); } catch (e) { m.textContent = 'switch failed: ' + e.message; cell.classList.remove('switching'); continue; }
      cell.classList.remove('switching'); m.textContent = `served in ${served.seconds}s · sampling ${K}…`;
      const samples = [];
      try { for await (const msg of generate({ ...cfg, server: served.url, model: served.name, prompt })) { if (msg.type === 'sample') { samples.push(msg); cell.appendChild(renderSample(msg, prompt)); } } }
      catch (e) { m.textContent = 'sampling failed: ' + e.message; continue; }
      const st = statsOf(samples.flatMap(s => s.tokens)); let line = `${samples.length} samples · ${statsText(st)}`;
      if (doJudge && S.judge) {
        try {
          const items = samples.map((s, i) => ({ id: `s${i}`, context: '\n', text: s.text_stripped || s.text }));
          const leaf = await score(S.judge.leaf, items), base = await score(S.judge.base, items);
          const deltas = items.map(it => (leaf[it.id]?.nll_mean ?? 0) - (base[it.id]?.nll_mean ?? 0));
          line += ` · judge Δ ${fmt(deltas.reduce((a, b) => a + b, 0) / (deltas.length || 1), 3)} (${deltas.map(d => fmt(d, 2)).join(', ')})`;
        } catch (e) { line += ` · judge failed: ${e.message}`; }
      }
      if (doHaunt) { try { const recs = await haunt(samples.map((s, i) => ({ id: `h${i}`, text: s.text }))); line += ` · haunt longest ${recs.map(r => r?.longest_match ?? '?').join('/')}`; } catch { /* reported */ } }
      m.textContent = line;
    }
  } finally { S.pop.running = false; statusBox.textContent = S.pop.stop ? 'stopped' : 'done'; refreshServers(); }
}

// ------------------------------------------------------------------------------------------ weave files
async function refreshWeaveList() {
  try {
    const j = await api('/api/weaves'); const sel = $('#weave-list'); sel.innerHTML = '';
    for (const w of j.weaves) { const o = el('option', null, `${w.name} (${w.nodes ?? '?'} nodes${w.modified_iso ? ', ' + w.modified_iso.slice(5, 16) : ''})`); o.value = w.name; sel.appendChild(o); }
    if (!j.weaves.length) sel.appendChild(el('option', null, '(no saved weaves)'));
  } catch (e) { fail('weaves', e); }
}
async function saveWeave() {
  const name = $('#weave-name').value.trim() || S.weaveName; if (!name) { $('#weave-name').focus(); return status('give the weave a name', true); }
  try { const j = await api('/api/weaves', { name, weave: S.weave }); S.weaveName = name; S.weave.metadata.name = name; $('#weave-name').value = name; toast(`saved ${j.name} (${j.nodes} nodes)`, 'ok'); recordRecent('weaves', { name }); touch(); refreshWeaveList(); }
  catch (e) { fail('save', e); }
}
async function loadWeaveByName(name) {
  try { const w = await api(`/api/weaves?name=${encodeURIComponent(name)}`); loadWeave(w, name); recordRecent('weaves', { name }); status(`loaded ${name}`); return true; }
  catch (e) { fail('load', e); return false; }
}
async function deleteWeaveByName(name) {
  if (!name || !confirm(`delete saved weave "${name}"?`)) return;
  try { await api('/api/weaves/delete', { name }); toast(`deleted ${name}`, 'ok'); refreshWeaveList(); } catch (e) { fail('delete', e); }
}

// ------------------------------------------------------------------------------------------ prompt library
// Served by /api/library: greetings on the bare frame, the twelve room prompts by kind, raw openings. Selecting an
// item fills the pane's prompt and resets its sampler to the library defaults; "custom" leaves the box to the user.
function libFallback() {
  return { frame: FRAME, sampler: LIB_SAMPLER, items: [{ id: 'greet-0', group: 'greet h (bare frame)', kind: 'greet', title: SEED_LINE, prompt: `${FRAME}\n\n${SEED_LINE}\n\nh:` }] };
}
const libraryItem = id => S.library.items.find(it => it.id === id);
const libraryByText = text => S.library.items.find(it => it.prompt === text);
const seedItem = () => libraryItem('greet-0') || libFallback().items[0];
const customPrompt = () => `${S.library.frame || FRAME}\n\nember: \n\nh:`;
async function loadLibrary() {
  try { S.library = await api('/api/library'); } catch (e) { S.library = libFallback(); fail('library', e); }
  for (const id of ['start-prompt', 'loom-library', 'cmp-library', 'cf-library', 'pop-library']) fillLibrarySelect($('#' + id));
  $('#cf-library').value = 'custom';
  syncPromptBox(); syncLibrarySelect('cmp'); syncLibrarySelect('pop');
}
function fillLibrarySelect(sel) {
  const prev = sel.value; sel.innerHTML = ''; const groups = new Map();
  for (const it of S.library.items) {
    if (!groups.has(it.group)) { const g = el('optgroup'); g.label = it.group; groups.set(it.group, g); }
    const o = el('option', null, it.title); o.value = it.id; o.title = it.prompt; groups.get(it.group).appendChild(o);
  }
  for (const g of groups.values()) sel.appendChild(g);
  const custom = el('option', null, 'custom (type your own)'); custom.value = 'custom'; sel.appendChild(custom);
  sel.value = (prev && libraryItem(prev)) ? prev : (S.library.items[0]?.id || 'custom');
}
function syncLibrarySelect(prefix) { const sel = $(`#${prefix}-library`); if (sel.options.length) sel.value = libraryByText($(`#${prefix}-prompt`).value)?.id || 'custom'; }
function setSampler(prefix, n) {
  const sp = S.library.sampler || LIB_SAMPLER; const set = (id, v) => { const e = $(`#${prefix}-${id}`); if (e) e.value = v; };
  if (n) set(prefix === 'cmp' ? 'k' : 'n', n);
  set('temp', sp.temperature); set('topp', sp.top_p); set('max', sp.max_tokens); set('stop', JSON.stringify((sp.stop || ['\n\n'])[0]).slice(1, -1));
}
// The root node for a library item: reused when a root with that text exists, else inserted; made the selection.
function setRootPrompt(it) {
  let root = S.weave.roots.find(r => S.weave.nodes[r].contents.text === it.prompt);
  mutate(`prompt: ${it.title}`, w => {
    if (root) setActive(w, root, true);
    else { const n = mkNode({ contents: { kind: 'prompt', text: it.prompt, tokens: null, created: now(), library: { id: it.id, kind: it.kind, title: it.title } }, active: true }); insert(w, n); root = n.id; }
    S.collapsed.delete(root);
  });
  return root;
}
function applyLibrary(pane, id) {
  const it = libraryItem(id);
  if (pane === 'loom') {
    if (it) { setRootPrompt(it); setSampler('loom', LIB_SAMPLER.n); }
    else { const ta = $('#loom-prompt'); if (!ta.value.trim()) { ta.value = customPrompt(); onPromptInput(); } ta.focus(); }
  } else if (pane === 'cmp' || pane === 'pop') {
    const ta = $(`#${pane}-prompt`); ta.value = it ? it.prompt : (ta.value.trim() || customPrompt()); setSampler(pane); if (!it) ta.focus();
  } else if (pane === 'cf') cfFromPrompt(it ? it.prompt : customPrompt(), '');
}

// ------------------------------------------------------------------------------------------ start pane
// Three ways in. Each takes the line chosen on the start pane (or a library id).
async function askH(id) {
  const it = libraryItem(id) || libraryItem($('#start-prompt').value) || seedItem();
  if (!S.probed && S.probe) await S.probe;
  const srv = residentServer();
  const root = setRootPrompt(it); setSampler('loom', LIB_SAMPLER.n);
  if (srv) $('#loom-server').value = srv.url;
  showTab('loom');
  if (!srv) return fail('ask h', new Error('no live model server: start one and press "servers"'));
  await expand(root, srv);
}
async function compareAll(id) {
  const it = libraryItem(id) || libraryItem($('#start-prompt').value) || seedItem();
  $('#cmp-prompt').value = it.prompt; $('#cmp-library').value = it.id; setSampler('cmp', 3);
  showTab('compare');
  if (!S.probed && S.probe) await S.probe;
  await runCompare(liveServers());
}
// A loom opened on an empty weave seeds itself: the bare frame + "ember: hi h", four answers from the resident.
async function seedLoom() {
  if (S.seeding || S.weave.roots.length) return;
  S.seeding = true;
  try { await askH(seedItem().id); } finally { S.seeding = false; }
}
function readRecent() { try { return JSON.parse(localStorage.getItem(LS_RECENT) || '{}') || {}; } catch { return {}; } }
function recordRecent(kind, entry) {
  const r = readRecent(); const key = kind === 'weaves' ? 'name' : 'prompt';
  r[kind] = [{ ...entry, time: now() }, ...(r[kind] || []).filter(x => x[key] !== entry[key])].slice(0, 10);
  try { localStorage.setItem(LS_RECENT, JSON.stringify(r)); } catch { /* ignore */ }
  renderRecent();
}
function promptTitle(text) {
  const it = libraryByText(text); if (it) return `${it.kind} · ${it.title}`;
  const turns = parseTurns(text).filter(t => t.kind === 'turn'); const last = turns[turns.length - 1];
  return short(last ? `${last.name}: ${last.text}` : text, 60);
}
function renderRecent() {
  const box = $('#start-recent'); box.innerHTML = ''; const r = readRecent();
  const weaves = (r.weaves || []).slice(0, 3), compares = (r.compares || []).slice(0, 3);
  if (!weaves.length && !compares.length) { box.appendChild(el('p', 'hint', 'Nothing yet: weaves you save or load and prompts you compare will be listed here.')); return; }
  const section = (title, items, label, fn) => {
    if (!items.length) return; box.appendChild(el('h4', null, title)); const ul = el('ul');
    for (const it of items) { const li = el('li', null, label(it)); const when = el('span', 'when', ` · ${(it.time || '').slice(5, 16).replace('T', ' ')}`); li.appendChild(when); li.title = it.prompt || it.name; li.onclick = () => fn(it); ul.appendChild(li); }
    box.appendChild(ul);
  };
  section('weaves', weaves, it => it.name, async it => { if (await loadWeaveByName(it.name)) showTab('loom'); });
  section('compare prompts', compares, it => `${promptTitle(it.prompt)} · ${(it.servers || []).map(modelShort).join(' vs ')}`, it => { $('#cmp-prompt').value = it.prompt; syncLibrarySelect('cmp'); showTab('compare'); });
}
function renderPaneList(ul) {
  ul.innerHTML = '';
  for (const [tab, name, blurb] of PANES) { const li = el('li'); li.appendChild(el('b', null, name)); li.appendChild(el('i', null, blurb)); li.title = `open ${name}`; li.onclick = () => { if ($('#help').open) $('#help').close(); showTab(tab); }; ul.appendChild(li); }
}
function renderStart() {
  const res = residentServer(); const live = liveServers(); const d = S.obs.dates[0];
  const probing = !S.probed ? ' (probing the model servers…)' : '';
  $('#start-ask-desc').textContent = res ? `Send the chosen line to the resident h (${res.model} on ${res.url.replace('http://127.0.0.1', '')}) and read four answers as a tree you can grow.` : `Send the chosen line to the resident h and read four answers as a tree you can grow${probing || ' — no model server is up now: start one and press "servers"'}.`;
  $('#start-compare-desc').textContent = live.length ? `The same line to every model that is up (${live.map(s => modelShort(s.model)).join(', ')}), three samples each, side by side.` : `The same line to every model that is up, three samples each, side by side${probing || ' — none is up now'}.`;
  $('#start-replay-desc').textContent = d ? `Read the Discord room through the proxy's ledger: ${d.records} records on ${d.date}, each with the prompt h saw, the candidates it tried, and the one it said.` : 'Read the Discord room through the proxy\'s ledger: the prompt h saw, the candidates it tried, and the one it said.';
  $('#start-ask').disabled = S.probed && !res; $('#start-compare').disabled = S.probed && !live.length;
  renderRecent();
}

// ------------------------------------------------------------------------------------------ tabs + wiring
function showTab(name) {
  $$('.tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === name));
  $$('.tab').forEach(t => t.classList.toggle('on', t.id === 'tab-' + name));
  if (name === 'start') renderStart();
  if (name === 'provenance') renderProvenance();
  if (name === 'observatory' && !S.obs.day) loadObsDates();
  if (name === 'counterfactual') renderCf();
  if (name === 'roomstate') rsRefresh();
  if (name === 'population') { if (!$('#pop-checkpoints').children.length) renderPopCheckpoints(); if (!$('#pop-prompt').value) { $('#pop-prompt').value = DEFAULT_PROMPT; syncLibrarySelect('pop'); } }
  if (name === 'labels') loadLabels();
  if (name === 'loom') { $('#tree-wrap').focus({ preventScroll: true }); if (!S.weave.roots.length) seedLoom(); }
}
async function loadScorers() {
  try { const j = await api('/api/scorers'); S.scorers = j.checkpoints; S.judge = j.judge; if (j.worker) status('scorer: ' + j.worker, true); fillScorers($('#cf-scorer')); }
  catch (e) { fail('scorers', e); }
}
function wire() {
  $$('.tabs button').forEach(b => b.onclick = () => showTab(b.dataset.tab));
  $('#servers-refresh').onclick = refreshServers;
  $('#help-btn').onclick = () => $('#help').showModal();
  renderPaneList($('#help-panes')); renderPaneList($('#start-panes'));
  $('#start-ask').onclick = () => askH($('#start-prompt').value);
  $('#start-compare').onclick = () => compareAll($('#start-prompt').value);
  $('#start-replay').onclick = replayRoom;
  $('#loom-library').onchange = e => applyLibrary('loom', e.target.value);
  $('#cmp-library').onchange = e => applyLibrary('cmp', e.target.value);
  $('#cf-library').onchange = e => applyLibrary('cf', e.target.value);
  $('#pop-library').onchange = e => applyLibrary('pop', e.target.value);
  $('#loom-prompt').oninput = onPromptInput;
  $('#loom-frame').onclick = () => { const ta = $('#loom-prompt'); ta.value = ta.value.trim() ? ta.value : DEFAULT_PROMPT; onPromptInput(); };
  $('#loom-expand-root').onclick = () => { const w = S.weave; if (!w.active) return status('nothing selected: click a node, or pick a library prompt', true); expand(w.active); };
  $('#weave-save').onclick = saveWeave;
  $('#weave-load').onclick = () => { const v = $('#weave-list').value; if (v) loadWeaveByName(v); };
  $('#weave-delete').onclick = () => deleteWeaveByName($('#weave-list').value);
  $('#weave-new').onclick = () => { if (!Object.keys(S.weave.nodes).length || confirm('discard the current (unsaved) weave?')) loadWeave(newWeave(''), ''); };
  $('#undo-btn').onclick = undo; $('#redo-btn').onclick = redo;
  $('#copy-transcript').onclick = copyTranscript; $('#copy-json').onclick = copyJson;
  $('#haunt-all').onclick = $('#prov-scan-all').onclick = async () => { const w = S.weave; await haunt(orderedIds(w).map(id => ({ id, text: w.nodes[id].contents.text }))); touch(); renderProvenance(); };
  $('#collapse-all').onclick = () => { for (const id of orderedIds(S.weave)) if (S.weave.nodes[id].to.length) S.collapsed.add(id); touch(); };
  $('#expand-all').onclick = () => { S.collapsed.clear(); touch(); };
  $('#collapse-deep').onclick = () => { S.collapsed.clear(); autoCollapse(S.weave); touch(); };
  $('#prov-scan').onclick = async () => { const t = provTarget(); if (!t) return status('no active node', true); await haunt([t]); renderProvenance(); touch(); };
  $$('input[name=prov-scope]').forEach(r => r.onchange = renderProvenance);
  $('#obs-date').onchange = e => loadObsDay(e.target.value);
  $('#obs-reload').onclick = () => loadObsDates();
  $('#cmp-run').onclick = runCompareAB;
  $('#cmp-run-all').onclick = () => runCompare(liveServers());
  $('#cmp-frame').onclick = () => { $('#cmp-prompt').value = DEFAULT_PROMPT; syncLibrarySelect('cmp'); };
  $('#cmp-from-loom').onclick = () => { const w = S.weave; if (w.active) { $('#cmp-prompt').value = pathText(w, w.active); syncLibrarySelect('cmp'); } };
  $('#cmp-prompt').oninput = () => syncLibrarySelect('cmp');
  $('#pop-prompt').oninput = () => syncLibrarySelect('pop');
  $('#label-submit').onclick = submitLabel; $('#label-cancel').onclick = () => $('#label-dialog').close();
  $('#labels-reload').onclick = loadLabels; $('#pairs-open').onclick = openPairs;
  $('#cf-from-loom').onclick = () => { const w = S.weave; if (w.active) cfFromNode(w.active); };
  $('#cf-score').onclick = cfScore; $('#cf-rerun').onclick = cfRerun;
  $('#cf-reset').onclick = () => { S.cf.edited = clone(S.cf.turns); renderCf(); };
  $('#cf-add').onclick = () => { S.cf.edited.push({ kind: 'turn', name: 'ember', text: '' }); renderCf(); };
  $('#cf-reply').oninput = () => { S.cf.reply = $('#cf-reply').value; };
  $('#rs-refresh').onclick = rsRefresh; $('#rs-room-create').onclick = rsCreate; $('#rs-room-open').onclick = rsOpen; $('#rs-room-delete').onclick = rsDelete;
  $('#rs-event-send').onclick = rsEvent; $('#rs-candidates').onclick = rsCandidates; $('#rs-silence').onclick = rsSilence; $('#rs-snapshot').onclick = rsSnapshot;
  $('#pop-run').onclick = popRun; $('#pop-stop').onclick = () => { S.pop.stop = true; };
  $('#pop-frame').onclick = () => { $('#pop-prompt').value = DEFAULT_PROMPT; syncLibrarySelect('pop'); };
  $('#pop-from-loom').onclick = () => { const w = S.weave; if (w.active) { $('#pop-prompt').value = pathText(w, w.active); syncLibrarySelect('pop'); } };
  $('#pop-all').onclick = () => $$('#pop-checkpoints input').forEach(i => { i.checked = true; });
  $('#pop-none').onclick = () => $$('#pop-checkpoints input').forEach(i => { i.checked = false; });
  $$('.legend .tok').forEach(s => { s.style.background = lpColor(+s.dataset.lp); });
  document.addEventListener('keydown', keyNav);
  window.addEventListener('error', e => toast('script error: ' + e.message, 'err'));
}

async function init() {
  wire();
  let restored = null;
  try { restored = JSON.parse(localStorage.getItem(LS_KEY) || 'null'); } catch { /* ignore */ }
  if (restored?.weave?.nodes) loadWeave(restored.weave, restored.name, { tidy: false }); else loadWeave(newWeave(''), '');
  $('#cmp-prompt').value = DEFAULT_PROMPT;
  // Land on the loom only when a named (saved or loaded) weave was open; otherwise on Start here.
  showTab(S.weaveName && S.weave.roots.length ? 'loom' : 'start');
  S.probe = refreshServers();
  await Promise.all([S.probe, refreshWeaveList(), loadScorers(), loadLibrary(), loadObsDates({ day: false })]);
  touch(true); renderStart();
  status(`ready · explorer ${S.version.explorer || ''} · ? for help`);
}
init();
