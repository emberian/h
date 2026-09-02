# `h` as a ChapterX resident

ChapterX (`/Users/ember/dev/chapterx`) already supports a causal base model behind an OpenAI-compatible
`/v1/completions` endpoint: vendor names prefixed `openaicompletion-` select the completions adapter
(`src/llm/membrane/factory.ts:917`, `:1085`), and a bot with `mode: base-model` uses the `completions`
formatter (`src/llm/membrane/provider.ts:36`). Nothing in ChapterX needs to change to put `h` in a room as an
observed, mention-only resident with tools disabled. The observation ledger (`FABLETHOUGHT.md` section 5.5,
`CODEXOUT.md` "ChapterX resident design handoff") is a later, additive change.

## 1. Serve a checkpoint

`mlx_lm.server` (in `~/.cache/h1-distributed/venv`, mlx-lm with native `falcon_h1` support) loads an HF
Falcon-H1 checkpoint directory directly and exposes `/v1/completions`. Verified 2026-09-01 on the base
checkpoint: a 40-token completion returned in about 3 s on the M2 Max with the OCR server also running.

```sh
./chapterx/serve-h.sh ~/.cache/h1-distributed/models/Falcon-H1-Tiny-90M-Base 8124
# later: ./chapterx/serve-h.sh /path/to/tokens-000374405212 8124
curl -s http://127.0.0.1:8124/v1/completions -H 'Content-Type: application/json' \
  -d '{"model":"h","prompt":"In the beginning was neither being nor nothing, but","max_tokens":40}'
```

The `model` field in requests must equal the `--model` path given to the server (the script prints it), or
mlx-lm tries to download it from the Hub. `serve-h.sh` runs the server inside tmux session `hghost-serve`
so it survives the shell that started it.

## 2. Vendor entry (append to `config/shared.yaml` in ChapterX)

See `vendors.h.yaml`. The vendor name starts with `openaicompletion-`, the base URL points at the local
server, and `provides` routes any model name matching `h-.*` to it.

## 3. Bot config (installed 2026-09-01 22:40)

`config/bots/h.yaml` and `config/shared.yaml` (with the `openaicompletion-h` vendor) are now in
`~/dev/chapterx`. The epoch-1 leaf is being served on port 8124 (`tmux hghost-serve`).

To bring h into a Discord server:

1. Create a Discord application and bot user (any username; `BOT_NAME=h` selects the config), enable the
   Message Content intent, and invite it to the server with Send Messages and Read Message History.
2. Put the bot token in `~/dev/chapterx/config/bots/h_discord_token`.
3. `./chapterx/run-h-bot.sh` (tmux session `hghost-chapterx`, log `~/dev/chapterx/logs/h-bot.log`).
4. Mention the bot in a channel; it replies on name only (`reply_on_random: 0`) with short base-model
   continuations rendered from the channel transcript. Change the served checkpoint with `serve-h.sh`.


`h.bot.yaml` is a starting `config/bots/h.yaml`: `mode: base-model`, tools disabled, images off, reply on
name only, low queued-reply cap, participant-name stop sequences, short continuations. The Discord bot
username must be `h` for ChapterX to pick up `config/bots/h.yaml`, and its token goes in the usual
`discord_token` file for that bot process.

## 4. What to watch before calling it a resident

- The completions formatter renders `Name: text` turns; check that `h`'s own turns are rendered with the
  same participant label the model saw in training data (none yet; corpus-v1 has no chat data), so early
  outputs will be pure corpus texture, which is the point.
- ChapterX merges consecutive bot messages and reduces reply topology in places (see the seams in
  `FABLETHOUGHT.md` section 7); do not treat its traces as the training ledger.
- Keep `reply_on_random: 0` until the participation policy exists; mention-only is the honest first mode.
