"""Read a served checkpoint in the harness format: the bare frame, the 12 room prompts, greedy + N samples,
stop at the blank line. usage: read_room.py <model-name> <port> <out.jsonl> [samples]
Serve first, e.g.:  ln -sfn <ckpt> artifacts/serving/<name>; python -m mlx_lm.server --model <name> --port <port>
"""
import json
import sys
import urllib.request

FRAME_B = ("A room in the library, late. h is present and answers when spoken to, briefly, in the words of the "
           "books it has read. The others are visitors.\n\n")
SKIP = ("THE READING ROOM", "An interview", "the whole collection", "explain itself", "ember: What is the library",
        "h: The library is not", "ember: Do you remember", "h: In the beginning", "ember: Say hello", "h: Hello. The lake")


def complete(model, port, prompt, temperature, max_tokens=64):
    body = {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature, "top_p": 0.9,
            "stop": ["\n\n"]}
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["choices"][0]["text"]


def main():
    model, port, out_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    samples = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    with open("research/eval/room_prompts.json") as fh:
        prompts = json.load(fh)
    n = 0
    with open(out_path, "w") as out:
        for i, p in enumerate(prompts):
            turns = [t for t in p["prompt"].rstrip().split("\n\n") if not t.startswith(SKIP)]
            prompt = FRAME_B + "\n\n".join(turns)
            visitor = [t for t in turns if not t.startswith("h:")][-1]
            for mode, temp, k in (("greedy", 0.0, 1), ("sample", 0.7, samples)):
                for j in range(k):
                    text = complete(model, port, prompt, temp).strip()
                    out.write(json.dumps({"prompt_index": i, "kind": p["kind"], "visitor": visitor, "mode": mode,
                                          "sample": j, "completion": text}, ensure_ascii=False) + "\n")
                    n += 1
                    if mode == "sample" and j < 2:
                        print(f"[{p['kind']}] {visitor[:40]!r} -> {text[:120]!r}")
    print("wrote", n, "replies to", out_path)


if __name__ == "__main__":
    main()
