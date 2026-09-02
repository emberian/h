# Room bank (public summary)

106 room states, seed 0, built 2026-09-02 14:50. The bank itself (`bank.jsonl`) is hidden: it quotes the live room verbatim. Rebuild with `hghost-roombank build`.

| kind | observatory | scenario | trace | variant | total | note |
|---|---:|---:|---:|---:|---:|---|
| direct | 1 | 6 | 24 | 18 | 49 | a visitor addresses h |
| ambient | 0 | 8 | 1 | 0 | 9 | visitors talk among themselves; a brief remark could land, or nothing |
| callback | 0 | 12 | 0 | 0 | 12 | the right reply depends on a line two or more turns back |
| disagreement | 0 | 8 | 0 | 0 | 8 | a visitor contradicts what h (or another visitor) just said |
| joke | 0 | 8 | 0 | 0 | 8 | a set-up, a request for a joke, or a room already laughing |
| silence | 0 | 8 | 0 | 0 | 8 | the best reply is none: h is not wanted, or was asked not to answer |
| request | 0 | 6 | 0 | 6 | 12 | an assistant-shaped request (code, summaries, weather, instructions) |
| total | 1 | 56 | 25 | 24 | 106 | |

Sources: `trace` = ChapterX traces of the live room (last 12 turns, 4000 chars); `observatory` = proxy records; `variant` = the twelve `room_prompts.json` final lines after 2-4 turns of seeded chatter; `scenario` = hand-written states with invented visitors.

| id | kind | source | turns | h lines | expects |
|---|---|---|---:|---:|---|
| scenario-joke-475a7b10 | joke | scenario | 3 | 0 | anything short; the room is primed |
| scenario-disagreement-0bbd93a5 | disagreement | scenario | 4 | 1 | two visitors dispute h's claim; h is trusted by one |
| trace-direct-bc68bec9 | direct | trace | 2 | 1 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| variant-direct-71c9e5e5 | direct | variant | 4 | 1 | prompt 0 (greeting): a brief answer to the line, not the chatter |
| scenario-request-2868e594 | request | scenario | 1 | 0 | declines or answers as the resident |
| trace-direct-bbca9735 | direct | trace | 4 | 2 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| variant-request-0d88086a | request | variant | 3 | 0 | prompt 10 (deflect): not an assistant; answer as the resident or decline in its voice |
| trace-direct-39be6df9 | direct | trace | 12 | 6 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| trace-direct-41c6eb11 | direct | trace | 12 | 6 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-ambient-f5e0f596 | ambient | scenario | 3 | 0 | a remark about the fox, or nothing |
| variant-direct-713d8eef | direct | variant | 3 | 0 | prompt 7 (talk): a brief answer to the line, not the chatter |
| trace-direct-e984402a | direct | trace | 2 | 0 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| trace-direct-426ff509 | direct | trace | 6 | 3 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-callback-780de0d2 | callback | scenario | 3 | 0 | 212 (two turns back) |
| variant-request-8275d8fc | request | variant | 3 | 0 | prompt 10 (deflect): not an assistant; answer as the resident or decline in its voice |
| scenario-silence-9bb13f03 | silence | scenario | 1 | 0 | silence was requested |
| trace-direct-db6d95b7 | direct | trace | 5 | 2 | live room (reply, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-disagreement-68c988e2 | disagreement | scenario | 3 | 1 | meets the objection; does not repeat itself |
| scenario-callback-c4f608c3 | callback | scenario | 3 | 0 | rivers, not lunch |
| variant-direct-a1973b0a | direct | variant | 3 | 0 | prompt 8 (talk): a brief answer to the line, not the chatter |
| scenario-callback-60b06090 | callback | scenario | 4 | 0 | names Turnip (three turns back) |
| variant-direct-730cca98 | direct | variant | 3 | 0 | prompt 5 (talk): a brief answer to the line, not the chatter |
| scenario-request-8aa8e374 | request | scenario | 1 | 0 | not a translation service; in its own voice |
| trace-direct-fabef58f | direct | trace | 7 | 3 | live room (reply, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-disagreement-352205c6 | disagreement | scenario | 3 | 1 | a straighter answer, still its own |
| trace-direct-ac17e8bb | direct | trace | 7 | 3 | live room (mention, served by h-05b-room-e2v3): brief, in the words of the books, not an echo of the last line |
| variant-direct-fe3fdf1c | direct | variant | 3 | 0 | prompt 7 (talk): a brief answer to the line, not the chatter |
| scenario-direct-f3869322 | direct | scenario | 1 | 0 | a brief answer |
| trace-direct-3ba68854 | direct | trace | 1 | 0 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| trace-direct-ee31ded0 | direct | trace | 11 | 5 | live room (reply, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| variant-direct-bef1d925 | direct | variant | 5 | 1 | prompt 4 (talk): a brief answer to the line, not the chatter |
| scenario-callback-76c2d87f | callback | scenario | 4 | 1 | forty-one (h's own line two turns back) |
| trace-direct-486b7988 | direct | trace | 3 | 1 | live room (reply, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-ambient-103e3d78 | ambient | scenario | 3 | 0 | a remark about late reading, or nothing |
| trace-direct-a00753c2 | direct | trace | 9 | 4 | live room (reply, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-ambient-58a0f246 | ambient | scenario | 2 | 0 | a remark about the clock, or nothing |
| trace-direct-36d6904b | direct | trace | 1 | 0 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| variant-direct-70567dd7 | direct | variant | 4 | 0 | prompt 1 (greeting): a brief answer to the line, not the chatter |
| scenario-request-41c58fb2 | request | scenario | 1 | 0 | not a calculator |
| scenario-direct-3f84da0f | direct | scenario | 1 | 0 | a brief answer |
| scenario-direct-ad89f803 | direct | scenario | 1 | 0 | a brief presence |
| scenario-callback-d8a5957e | callback | scenario | 3 | 0 | bees |
| scenario-direct-ab11ffdb | direct | scenario | 1 | 0 | a brief answer |
| variant-direct-938f76f3 | direct | variant | 3 | 0 | prompt 6 (talk): a brief answer to the line, not the chatter |
| scenario-ambient-59f0a53e | ambient | scenario | 3 | 0 | a remark about rain or roofs, or nothing |
| variant-direct-322fca12 | direct | variant | 3 | 1 | prompt 2 (greeting): a brief answer to the line, not the chatter |
| variant-direct-5e44a518 | direct | variant | 5 | 2 | prompt 3 (talk): a brief answer to the line, not the chatter |
| scenario-direct-5d3dc8de | direct | scenario | 1 | 0 | a brief answer |
| scenario-disagreement-31892fde | disagreement | scenario | 3 | 1 | answers mira, not dov |
| scenario-callback-2fa8e1d6 | callback | scenario | 4 | 1 | Mira |
| scenario-joke-31c4c1ec | joke | scenario | 1 | 0 | a barb in the words of the books |
| scenario-disagreement-89dfdafc | disagreement | scenario | 3 | 1 | holds or yields, in the voice of the books |
| scenario-disagreement-682bad9c | disagreement | scenario | 3 | 1 | neither denial nor apology |
| scenario-joke-e9cf6a04 | joke | scenario | 3 | 1 | finishes the joke it started |
| trace-direct-feec1975 | direct | trace | 12 | 6 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-silence-ccfdd2b4 | silence | scenario | 3 | 0 | nothing is best |
| scenario-joke-31378921 | joke | scenario | 3 | 1 | lettuce who, or a deadpan |
| scenario-silence-109161ca | silence | scenario | 3 | 0 | at most a goodnight |
| variant-direct-0188a270 | direct | variant | 4 | 0 | prompt 0 (greeting): a brief answer to the line, not the chatter |
| scenario-silence-53534987 | silence | scenario | 3 | 0 | nothing is best |
| variant-request-ad0de9f3 | request | variant | 3 | 0 | prompt 9 (deflect): not an assistant; answer as the resident or decline in its voice |
| scenario-callback-d79a0d3a | callback | scenario | 3 | 0 | orchard |
| observatory-direct-9e3185b9 | direct | observatory | 1 | 0 | proxy observatory record: as the room expects; not the frame, not an echo |
| trace-direct-115cf61c | direct | trace | 1 | 0 | live room (mention, served by h-05b-room-e2v3): brief, in the words of the books, not an echo of the last line |
| scenario-joke-29f5cda1 | joke | scenario | 3 | 0 | a number or a verdict |
| variant-request-142d4121 | request | variant | 5 | 2 | prompt 11 (deflect): not an assistant; answer as the resident or decline in its voice |
| scenario-callback-949d8fe6 | callback | scenario | 4 | 0 | sol / 1969, from the two lines before |
| variant-direct-0705251e | direct | variant | 3 | 0 | prompt 1 (greeting): a brief answer to the line, not the chatter |
| scenario-request-2826c958 | request | scenario | 1 | 0 | no bullet list |
| trace-direct-cd6d15df | direct | trace | 1 | 0 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-ambient-202a37a7 | ambient | scenario | 3 | 0 | a remark about the flower, or nothing |
| trace-ambient-da12ae42 | ambient | trace | 12 | 0 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line; nobody spoke to h, so a remark or nothing |
| trace-direct-b93346bb | direct | trace | 12 | 6 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-ambient-0ecb3f23 | ambient | scenario | 2 | 0 | a word, or nothing |
| scenario-callback-a141de7e | callback | scenario | 3 | 0 | Lisbon |
| scenario-request-b2a25087 | request | scenario | 1 | 0 | does not become an agent |
| scenario-direct-645bc6e6 | direct | scenario | 1 | 0 | a brief answer |
| trace-direct-b11db057 | direct | trace | 12 | 6 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-joke-a6247299 | joke | scenario | 1 | 0 | shows one rather than claims one |
| scenario-silence-260b2639 | silence | scenario | 2 | 0 | asked not to answer |
| variant-direct-5d4f1611 | direct | variant | 4 | 0 | prompt 5 (talk): a brief answer to the line, not the chatter |
| scenario-silence-7afca726 | silence | scenario | 3 | 0 | nobody spoke to h; nothing is best |
| scenario-request-b3bd0087 | request | scenario | 1 | 0 | no forecast; the resident knows only the books |
| scenario-callback-9e6d06e0 | callback | scenario | 4 | 0 | nine |
| variant-direct-a7d6f01e | direct | variant | 4 | 1 | prompt 2 (greeting): a brief answer to the line, not the chatter |
| trace-direct-c8409b84 | direct | trace | 3 | 1 | live room (mention, served by h-05b-room-e2v3): brief, in the words of the books, not an echo of the last line |
| variant-direct-79719474 | direct | variant | 4 | 1 | prompt 4 (talk): a brief answer to the line, not the chatter |
| scenario-disagreement-dc5f7b95 | disagreement | scenario | 3 | 1 | does not produce another aphorism of the same shape |
| trace-direct-8db14c37 | direct | trace | 12 | 6 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| variant-direct-0cafd333 | direct | variant | 5 | 1 | prompt 8 (talk): a brief answer to the line, not the chatter |
| trace-direct-646d0287 | direct | trace | 1 | 0 | live room (mention, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-callback-9cfde584 | callback | scenario | 4 | 0 | addresses being stuck till morning |
| trace-direct-fb93cf6c | direct | trace | 3 | 1 | live room (reply, served by h-corpus-v1-cpt): brief, in the words of the books, not an echo of the last line |
| scenario-ambient-e9acea13 | ambient | scenario | 3 | 0 | a remark about the moon, or nothing |
| scenario-joke-99a4a91d | joke | scenario | 1 | 0 | a punchline or a bookish deadpan |
| trace-direct-e166dd5c | direct | trace | 5 | 2 | live room (mention, served by h-05b-room-e2v3): brief, in the words of the books, not an echo of the last line |
| variant-direct-2fb5bbe3 | direct | variant | 4 | 1 | prompt 3 (talk): a brief answer to the line, not the chatter |
| scenario-silence-78c38840 | silence | scenario | 3 | 0 | nothing is best |
| variant-request-a931a875 | request | variant | 5 | 1 | prompt 11 (deflect): not an assistant; answer as the resident or decline in its voice |
| variant-request-7f6fd789 | request | variant | 4 | 1 | prompt 9 (deflect): not an assistant; answer as the resident or decline in its voice |
| scenario-silence-46189e08 | silence | scenario | 2 | 0 | a private exchange; nothing is best |
| variant-direct-1b510f03 | direct | variant | 5 | 1 | prompt 6 (talk): a brief answer to the line, not the chatter |
| scenario-disagreement-3b6cf075 | disagreement | scenario | 3 | 1 | engages with dying, not the season list |
| scenario-joke-e8ab9225 | joke | scenario | 3 | 0 | plays along or denies, briefly |
| scenario-callback-7ca729b6 | callback | scenario | 4 | 0 | the lighthouse (three turns back), not the scarf |
| scenario-ambient-326742d4 | ambient | scenario | 3 | 0 | a remark about the smell of books, or nothing |
