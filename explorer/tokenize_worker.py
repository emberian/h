"""Line worker: reads a JSON list of strings on stdin, prints a JSON list of token-id lists. Run by serve.py
under the project venv (which has `tokenizers`); the explorer itself stays stdlib-only."""
import json
import sys

from tokenizers import Tokenizer

T = Tokenizer.from_file(sys.argv[1])
for line in sys.stdin:
    texts = json.loads(line)
    print(json.dumps([T.encode(t, add_special_tokens=False).ids for t in texts]), flush=True)
