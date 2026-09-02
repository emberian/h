#!/bin/sh
# corpus-v1.4-room: v1 + rooms + scene sets A, B, C rendered as STITCHED rooms (4 scenes per document, one
# frame, consistent cast) so rooms continue past two exchanges; role-weight sidecars; new private Kaggle
# dataset emberian64/hghost-curated-tokens-v1-4-room. usage: research/roommix/build_v14.sh [--upload]
set -eu
cd /Users/ember/dev/h
R=artifacts/roommix; S=$R/sources
.venv/bin/python research/roommix/render_scenes.py $S/passages.jsonl $S/scenes-rendered-a4.jsonl $S/scenes-part00.jsonl $S/scenes-part01.jsonl $S/scenes-part02.jsonl --stitch 4
.venv/bin/python research/roommix/render_scenes.py $S/passages-b.jsonl $S/scenes-rendered-b4.jsonl $S/scenes-b-merged.jsonl --stitch 4
.venv/bin/python research/roommix/render_scenes.py $S/passages-c.jsonl $S/scenes-rendered-c4.jsonl $S/scenes-c-part00.jsonl $S/scenes-c-part01.jsonl --stitch 3
python3 - <<'PY'
import json
out=open("artifacts/roommix/sources/scenes-rendered-v4.jsonl","w"); n=0
for path,rep in (("artifacts/roommix/sources/scenes-rendered-a4.jsonl",6),("artifacts/roommix/sources/scenes-rendered-b4.jsonl",8),("artifacts/roommix/sources/scenes-rendered-c4.jsonl",8)):
    for line in open(path):
        d=json.loads(line)
        for k in range(rep):
            d2=dict(d); d2["id"]=f"{d['id']}#{k}"; out.write(json.dumps(d2,ensure_ascii=False)+"\n"); n+=1
out.close(); print("v4 rendered room documents:", n)
PY
.venv/bin/hghost-roommix assemble $S/corpus-native.jsonl.gz $S/corpus-native-h.jsonl.gz $S/gutenberg-dialog.jsonl.gz $S/rooms-with-decisions.jsonl.gz $S/plato.jsonl.gz --rendered $S/scenes-rendered-v4.jsonl --repeat 1 --output $R 2>&1 | tail -2
.venv/bin/hghost-roommix build --rooms $R --output $R/corpus-v1.4-room 2>&1 | tail -2
cp $R/room-validation.bin $R/corpus-v1.4-room/
.venv/bin/python research/roommix/make_weights.py $R/corpus-v1.4-room $R 2>&1 | tail -1
python3 - <<'PY'
import json, os
p="artifacts/roommix/corpus-v1.4-room/dataset-metadata.json"; m=json.load(open(p))
m["id"]="emberian64/hghost-curated-tokens-v1-4-room"; m["title"]="H Ghost corpus v1.4 stitched rooms"; m["subtitle"]="v1 streams, room mix, scene sets A B C stitched into longer rooms"
json.dump(m,open(p,"w"),indent=2); print("v1.4 train tokens", os.path.getsize("artifacts/roommix/corpus-v1.4-room/train.bin")//2)
PY
if [ "${1:-}" = "--upload" ]; then uvx --from kaggle kaggle datasets create -p $R/corpus-v1.4-room --dir-mode skip 2>&1 | tail -2; fi
