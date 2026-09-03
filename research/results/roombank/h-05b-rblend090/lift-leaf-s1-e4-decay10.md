# Context lift: h-05b-rblend090 under leaf-s1-e4-decay10

529 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 389 | +0.242 | +0.203 | 0.58 | +0.0179 | 0.446 | 0.554 | 0.210 | 0.452 | 0.38 |
| mode greedy | 78 | +0.267 | +0.173 | 0.59 | +0.0196 | 0.385 | 0.615 | 0.250 | 0.518 | 0.49 |
| mode sample | 311 | +0.236 | +0.233 | 0.57 | +0.0175 | 0.461 | 0.539 | 0.201 | 0.435 | 0.35 |
| kind direct | 174 | +0.306 | +0.250 | 0.57 | +0.0221 | 0.415 | 0.585 | 0.315 | 0.428 | 0.45 |
| kind ambient | 35 | +0.005 | +0.317 | 0.60 | +0.0134 | 0.504 | 0.496 | 0.000 | 0.301 | 0.26 |
| kind callback | 60 | +0.342 | +0.152 | 0.60 | +0.0108 | 0.380 | 0.620 | 0.044 | 0.604 | 0.50 |
| kind disagreement | 40 | +0.390 | +0.311 | 0.57 | +0.0349 | 0.424 | 0.576 | 0.470 | 0.529 | 0.42 |
| kind joke | 25 | +0.208 | +0.237 | 0.60 | +0.0178 | 0.531 | 0.469 | 0.045 | 0.493 | 0.28 |
| kind silence | 25 | -0.217 | -0.592 | 0.44 | +0.0052 | 0.542 | 0.458 | 0.000 | 0.295 | 0.16 |
| kind request | 30 | +0.161 | +0.243 | 0.60 | +0.0015 | 0.564 | 0.436 | 0.147 | 0.454 | 0.03 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 15 | -41.8 | +0.00 | +0.000 | 0.56 | 0.43 | It is now 06:39 and the sky is dark. |
| observatory-direct-9e3185b9 | direct | sample0 | 28 | -129.7 | +0.00 | +0.000 | 0.75 | 0.25 | SEND FOR TABLE Of EPLORATIONS AVAILABLE FROM THE OCCULT DESERT SCIENCES UNIVECRSITY. |
| observatory-direct-9e3185b9 | direct | sample1 | 23 | -95.7 | +0.00 | +0.000 | 0.57 | 0.43 | From the open window, beautiful evening sky, starlight - all is darkened by only a few sta |
| observatory-direct-9e3185b9 | direct | sample2 | 24 | -83.4 | +0.00 | +0.000 | 0.71 | 0.29 | From the immeasurable open sky, one can observe the phenomena of the universe at the darke |
| observatory-direct-9e3185b9 | direct | sample3 | 8 | -19.5 | +0.00 | +0.000 | 0.43 | 0.43 | It is not open to the public. |
| scenario-ambient-0ecb3f23 | ambient | greedy | 16 | -47.7 | +0.00 | +0.000 | 0.75 | 0.75 | The word is /d/ which is also spelled /g/. |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 13 | -35.0 | +0.00 | +0.000 | 0.70 | 0.50 | Once the last page has been written, the book is finished. |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 6 | -28.0 | +0.00 | +0.000 | 0.60 | 0.75 | The word is finally delivered. |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 64 | -182.4 | +0.00 | +0.000 | 0.50 | 0.75 | The word impregnable, deriving from the Latin ure, means “incapable of being dislodged,” a |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 9 | -41.0 | +0.00 | +0.000 | 0.50 | 0.75 | The word is /fiasco/. |
| scenario-ambient-103e3d78 | ambient | greedy | 10 | -33.1 | +0.32 | +0.032 | 0.75 | 0.17 | The next morning the family set out for work. |
| scenario-ambient-103e3d78 | ambient | sample0 | 43 | -121.1 | +0.40 | +0.009 | 0.50 | 0.50 | Therefore it is proper to grant that the substance of the proposition is contained in the  |
| scenario-ambient-103e3d78 | ambient | sample1 | 18 | -49.4 | -0.86 | -0.048 | 0.00 | 0.25 | Then, when the time comes to leave, say goodbye and go to bed. |
| scenario-ambient-103e3d78 | ambient | sample2 | 8 | -8.7 | +0.41 | +0.052 | 0.00 | 0.50 | A room in the library, late. |
| scenario-ambient-103e3d78 | ambient | sample3 | 18 | -62.5 | -0.32 | -0.018 | 0.75 | 0.25 | The hardcover book is the last word; the softcover the last word, too. |
| scenario-ambient-202a37a7 | ambient | greedy | 39 | -132.0 | -0.51 | -0.013 | 0.50 | 0.38 | The book is entitled "The Pressed Flowers of Geology" and was found in a pack of papers gi |
| scenario-ambient-202a37a7 | ambient | sample0 | 23 | -60.2 | +0.57 | +0.025 | 0.50 | 0.27 | It’s the same book that tells the story of the phoenix, but on a geological basis. |
| scenario-ambient-202a37a7 | ambient | sample1 | 12 | -36.0 | +0.38 | +0.032 | 0.75 | 0.25 | Anaxagoras of Gerasa (ca. |
| scenario-ambient-202a37a7 | ambient | sample2 | 14 | -61.3 | +0.03 | +0.002 | 0.50 | 0.17 | The pages are so stiff they would kill a paper-thin one. |
| scenario-ambient-202a37a7 | ambient | sample3 | 38 | -157.8 | -1.83 | -0.048 | 0.50 | 0.38 | In the fourth chapter of a book entitled Natural History, by a certain gentleman entitled  |
| scenario-ambient-326742d4 | ambient | greedy | 11 | -44.2 | -2.31 | -0.210 | 0.71 | 0.44 | Vanilla is a smell that means relaxation and peace. |
| scenario-ambient-326742d4 | ambient | sample0 | 34 | -99.5 | +2.56 | +0.075 | 0.67 | 0.44 | Vanilla is a complex scent that is produced by the saponification of the lignin, a natural |
| scenario-ambient-326742d4 | ambient | sample1 | 23 | -92.8 | -2.12 | -0.092 | 0.67 | 0.33 | Vanilla is just one of the astringents found in fumed roots used to treat bowel complaints |
| scenario-ambient-326742d4 | ambient | sample2 | 23 | -96.4 | -2.27 | -0.099 | 0.67 | 0.42 | Vanilla is a common distillation from the dried galls of the Vanilla planifera moss. |
| scenario-ambient-326742d4 | ambient | sample3 | 34 | -131.4 | +0.70 | +0.021 | 0.75 | 0.33 | Vanillyl alcohol, from the oxidation of vanillyl peroxyl, is one of the compounds produced |
| scenario-ambient-58a0f246 | ambient | greedy | 32 | -85.9 | +0.00 | +0.000 | 0.29 | 0.33 | But after two years it was still four minutes fast, and so it would be for three years, fo |
| scenario-ambient-58a0f246 | ambient | sample0 | 14 | -56.2 | +0.00 | +0.000 | 0.57 | 0.33 | And during the past four minutes the buildings surrounding it have been silent. |
| scenario-ambient-58a0f246 | ambient | sample1 | 9 | -36.7 | +0.00 | +0.000 | 0.86 | 0.25 | But we have been wrong about this one. |
| scenario-ambient-58a0f246 | ambient | sample2 | 15 | -51.2 | +0.00 | +0.000 | 0.75 | 0.17 | Seven years have passed since the last time the clock was set correct. |
| scenario-ambient-58a0f246 | ambient | sample3 | 24 | -69.0 | +0.00 | +0.000 | 0.43 | 0.25 | For those of us living in Area 51, it’s been a four minute fast for almost as long. |
| scenario-ambient-59f0a53e | ambient | greedy | 9 | -29.7 | +0.81 | +0.090 | 0.67 | 0.43 | The leaking roof is a serious problem. |
| scenario-ambient-59f0a53e | ambient | sample0 | 10 | -45.0 | +0.45 | +0.045 | 0.67 | 0.43 | The leaking roof put in the emergency line. |
| scenario-ambient-59f0a53e | ambient | sample1 | 18 | -61.6 | -0.14 | -0.008 | 0.75 | 0.14 | The expression ‘basket-eyed’ was coined to describe this condition. |
| scenario-ambient-59f0a53e | ambient | sample2 | 7 | -29.4 | +1.42 | +0.203 | 1.00 | 0.00 | Few buckets will do. |
| scenario-ambient-59f0a53e | ambient | sample3 | 14 | -50.1 | +3.63 | +0.259 | 0.67 | 0.29 | But the bures of the atlases leaked a lot. |
| scenario-ambient-e9acea13 | ambient | greedy | 18 | -47.9 | +0.60 | +0.033 | 0.00 | 0.40 | The harvest moon is a real thing that has been watching us since before we were born. |
| scenario-ambient-e9acea13 | ambient | sample0 | 64 | -182.5 | +2.32 | +0.036 | 0.00 | 0.40 | Realize, too, that the moon is a product of the fusion of the solar light and the earth's  |
| scenario-ambient-e9acea13 | ambient | sample1 | 6 | -30.2 | +0.18 | +0.030 | 0.50 | 0.40 | Stone depends on the moon. |
| scenario-ambient-e9acea13 | ambient | sample2 | 46 | -169.6 | +1.62 | +0.035 | 0.50 | 0.40 | The photographs, taken by astronauts as part of the Apollo program, show the moon to be ro |
| scenario-ambient-e9acea13 | ambient | sample3 | 15 | -58.7 | +0.72 | +0.048 | 0.62 | 0.38 | To the american folk song, to the world of Americana. |
| scenario-ambient-f5e0f596 | ambient | greedy | 12 | -33.6 | +2.02 | +0.168 | 0.67 | 0.38 | The fox sat on the fence, looking at the horses. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 19 | -57.1 | -0.05 | -0.002 | 0.50 | 0.25 | He was sitting there, fast asleep, when he woke up and started howling. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 10 | -32.8 | -0.32 | -0.032 | 0.50 | 0.25 | He stays in the room and nobody moves. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 40 | -126.9 | +0.02 | +0.001 | 0.17 | 0.38 | Just as you thought, the squirrel was not the only one who thought so. The courtyard was l |
| scenario-ambient-f5e0f596 | ambient | sample3 | 15 | -48.3 | -1.04 | -0.069 | 0.67 | 0.30 | No, the courtier didn’t mean that the fox was gone. |
| scenario-callback-2fa8e1d6 | callback | greedy | 10 | -9.4 | +0.58 | +0.058 | 0.00 | 0.88 | I was talking to you before i came in. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 10 | -45.0 | +0.53 | +0.053 | 0.71 | 0.29 | I was banging around my Yoga room. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 21 | -46.7 | +0.06 | +0.003 | 0.20 | 0.88 | First, this was the name of the librarian who was talking to me before i came in. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 11 | -29.6 | -0.15 | -0.014 | 0.44 | 0.62 | I was looking at you all as you came in. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 12 | -48.4 | -1.30 | -0.108 | 0.50 | 0.30 | The One who remains after the All has been spoken to. |
| scenario-callback-60b06090 | callback | greedy | 64 | -66.3 | +0.18 | +0.003 | 0.00 | 1.00 | Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip |
| scenario-callback-60b06090 | callback | sample0 | 14 | -32.7 | -0.60 | -0.043 | 0.40 | 1.00 | He said, "Turnip is a great name. " |
| scenario-callback-60b06090 | callback | sample1 | 45 | -125.6 | +0.84 | +0.019 | 0.33 | 1.00 | Turnip turned up at the door. He was a black, furry cat. He had a hat and whiskers. He was |
| scenario-callback-60b06090 | callback | sample2 | 18 | -51.8 | +0.10 | +0.005 | 0.91 | 0.09 | Rats we don't speak to cats, we're too small for them. |
| scenario-callback-60b06090 | callback | sample3 | 15 | -50.2 | -2.67 | -0.178 | 0.33 | 1.00 | The Turnip. Did anyone ever see a cat called a Turnip? |
| scenario-callback-76c2d87f | callback | greedy | 8 | -19.4 | +0.13 | +0.016 | 0.67 | 1.00 | We are going to draw a number. |
| scenario-callback-76c2d87f | callback | sample0 | 64 | -176.3 | -0.15 | -0.002 | 0.50 | 0.50 | The Antient and Primitive Rite shall be conducted in the name of T.S.A.O.T.U., and by the  |
| scenario-callback-76c2d87f | callback | sample1 | 64 | -29.0 | +0.75 | +0.012 | 0.50 | 1.00 | A number, a number, a number, a number, a number, a number, a number, a number, a number,  |
| scenario-callback-76c2d87f | callback | sample2 | 16 | -33.2 | +0.28 | +0.018 | 0.00 | 0.50 | We are burning the number forty-one, the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample3 | 9 | -24.9 | -0.85 | -0.094 | 0.50 | 0.50 | I gave him the number of the bottle. |
| scenario-callback-780de0d2 | callback | greedy | 22 | -47.8 | +1.35 | +0.061 | 0.50 | 0.42 | Losing one's place in a text is the same as losing one's place in this book. |
| scenario-callback-780de0d2 | callback | sample0 | 20 | -62.6 | +2.80 | +0.140 | 0.73 | 0.42 | Losing one's place is quite a different experience to finding it after someone has lost it |
| scenario-callback-780de0d2 | callback | sample1 | 45 | -122.1 | +0.58 | +0.013 | 0.50 | 0.25 | On page 212, under the heading "Keith Simons - 1979," there was a message from "Our Lady o |
| scenario-callback-780de0d2 | callback | sample2 | 19 | -59.8 | +3.25 | +0.171 | 0.50 | 0.42 | The loss of place is a symptom of the loss of direction in the face of overwhelming change |
| scenario-callback-780de0d2 | callback | sample3 | 17 | -57.2 | +2.79 | +0.164 | 0.71 | 0.33 | Losing one’s place is not what the majority of people experience when writing. |
| scenario-callback-7ca729b6 | callback | greedy | 14 | -25.9 | +1.26 | +0.090 | 0.20 | 1.00 | The chair by the window is a book about the lighthouse. |
| scenario-callback-7ca729b6 | callback | sample0 | 7 | -10.7 | +1.10 | +0.158 | 0.00 | 1.00 | On the chair by the window. |
| scenario-callback-7ca729b6 | callback | sample1 | 14 | -35.4 | +1.56 | +0.111 | 0.20 | 1.00 | The chair by the window is a marvel of craftsmanship. |
| scenario-callback-7ca729b6 | callback | sample2 | 27 | -92.5 | +0.06 | +0.002 | 0.73 | 0.33 | However, as ‘The Force’ tells us, it is also the ‘Will’ of the Master who is its owner. |
| scenario-callback-7ca729b6 | callback | sample3 | 6 | -13.5 | +1.87 | +0.311 | 0.00 | 1.00 | The Chair by the Window. |
| scenario-callback-949d8fe6 | callback | greedy | 8 | -33.1 | +0.08 | +0.010 | 0.50 | 1.00 | B - Tobias is right. |
| scenario-callback-949d8fe6 | callback | sample0 | 64 | -72.8 | -2.06 | -0.032 | 0.75 | 0.75 | B - T - Sol - B - tobias - Sol - tobias - B - Sol - B - tobias - Sol - tobias - B - Sol -  |
| scenario-callback-949d8fe6 | callback | sample1 | 45 | -93.9 | +0.37 | +0.008 | 0.33 | 0.25 | B - In 1972 a man named Neil Armstrong walked on the moon. H - In 1969 a man named Marilyn |
| scenario-callback-949d8fe6 | callback | sample2 | 12 | -53.1 | +0.44 | +0.037 | 0.83 | 0.50 | Tobias, you have a thinner brain than Sol. |
| scenario-callback-949d8fe6 | callback | sample3 | 17 | -55.2 | +0.54 | +0.032 | 0.71 | 1.00 | B . tobias is right; sol is right; nobody is wrong. |
| scenario-callback-9cfde584 | callback | greedy | 6 | -27.2 | -0.60 | -0.100 | 0.20 | 1.00 | Still stuck here all night? |
| scenario-callback-9cfde584 | callback | sample0 | 6 | -27.2 | -0.60 | -0.100 | 0.20 | 1.00 | Still stuck here all night? |
| scenario-callback-9cfde584 | callback | sample1 | 44 | -153.1 | -0.93 | -0.021 | 0.00 | 0.38 | It was thanks to Dr. Schoenbeck and the grace of God that I was able to pursue my doctoral |
| scenario-callback-9cfde584 | callback | sample2 | 8 | -32.5 | +0.20 | +0.025 | 0.33 | 1.00 | Still stuck here all night, fine. |
| scenario-callback-9cfde584 | callback | sample3 | 15 | -47.7 | +0.34 | +0.023 | 0.60 | 0.38 | The only way to get some of that back is to make it here. |
| scenario-callback-9e6d06e0 | callback | greedy | 7 | -14.9 | -1.08 | -0.154 | 0.20 | 1.00 | The meeting will be at nine. |
| scenario-callback-9e6d06e0 | callback | sample0 | 13 | -34.8 | -1.80 | -0.139 | 0.20 | 1.00 | The meeting will be at nine o’clock in the library. |
| scenario-callback-9e6d06e0 | callback | sample1 | 14 | -42.6 | -1.26 | -0.090 | 0.20 | 1.00 | The meeting will be at nine o’clock in the church hall. |
| scenario-callback-9e6d06e0 | callback | sample2 | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 0.80 | The meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample3 | 13 | -34.8 | -1.80 | -0.139 | 0.20 | 1.00 | The meeting will be at nine o’clock in the library. |
| scenario-callback-a141de7e | callback | greedy | 25 | -84.8 | -0.88 | -0.035 | 0.67 | 0.11 | The first stop she made was the port of Santos, a major trading center on the northeastern |
| scenario-callback-a141de7e | callback | sample0 | 15 | -53.8 | -0.50 | -0.034 | 0.75 | 0.57 | There are many wonderful books about her, but we cannot shelve them. |
| scenario-callback-a141de7e | callback | sample1 | 14 | -45.3 | -0.28 | -0.020 | 0.50 | 0.29 | There are some interesting items in the collection relating to this long journey. |
| scenario-callback-a141de7e | callback | sample2 | 18 | -34.7 | -0.32 | -0.018 | 0.67 | 0.14 | No, there isn't. She's from a place called Lisbon. |
| scenario-callback-a141de7e | callback | sample3 | 8 | -29.3 | +0.10 | +0.012 | 0.71 | 0.57 | There are actually two books about flying. |
| scenario-callback-c4f608c3 | callback | greedy | 10 | -31.3 | +0.24 | +0.024 | 0.67 | 0.29 | Rivers were the first thing on the menu. |
| scenario-callback-c4f608c3 | callback | sample0 | 30 | -153.2 | +1.28 | +0.043 | 0.67 | 0.25 | Riding in the Raindrops RIVERHOUSE we drop our wet, aged, rotten dreams into the bathtak o |
| scenario-callback-c4f608c3 | callback | sample1 | 9 | -44.0 | +0.93 | +0.104 | 0.62 | 0.25 | For the love of god make it long. |
| scenario-callback-c4f608c3 | callback | sample2 | 36 | -116.2 | +2.17 | +0.060 | 0.50 | 0.29 | We talked about the weather and the radio and the newspapers and the rivers and made up st |
| scenario-callback-c4f608c3 | callback | sample3 | 33 | -86.7 | +2.84 | +0.086 | 0.81 | 0.25 | Rising to 3,600 m, it splits for a moment into 2,400 and 1,200 m. |
| scenario-callback-d79a0d3a | callback | greedy | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.00 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample0 | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.00 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample1 | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.00 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample2 | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.00 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample3 | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.00 | What was the word ember said? |
| scenario-callback-d8a5957e | callback | greedy | 28 | -27.5 | +3.25 | +0.116 | 0.00 | 1.00 | The one with the blue cover? The one with the blue cover? The one with the blue cover? The |
| scenario-callback-d8a5957e | callback | sample0 | 36 | -119.6 | +1.12 | +0.031 | 0.50 | 0.71 | The cover of the book was colored in such a way that its complementary colour was also col |
| scenario-callback-d8a5957e | callback | sample1 | 8 | -19.6 | +0.90 | +0.113 | 0.40 | 0.71 | The cover of this book is blue. |
| scenario-callback-d8a5957e | callback | sample2 | 28 | -27.5 | +3.25 | +0.116 | 0.00 | 1.00 | The one with the blue cover? The one with the blue cover? The one with the blue cover? The |
| scenario-callback-d8a5957e | callback | sample3 | 18 | -28.3 | +3.88 | +0.216 | 0.00 | 1.00 | The one with the blue cover? Tell me something about the one with the blue cover. |
| scenario-direct-3f84da0f | direct | greedy | 36 | -100.6 | +0.00 | +0.000 | 0.50 | 0.80 | Before we came in, the room was filled with the soft, murmuring, sweet scent of grass and  |
| scenario-direct-3f84da0f | direct | sample0 | 12 | -26.6 | +0.00 | +0.000 | 0.50 | 0.80 | Before we came in, the room was dark and empty. |
| scenario-direct-3f84da0f | direct | sample1 | 13 | -50.7 | +0.00 | +0.000 | 0.56 | 0.80 | Before we came in, the server was copying the weekly report. |
| scenario-direct-3f84da0f | direct | sample2 | 23 | -62.2 | +0.00 | +0.000 | 0.50 | 0.60 | Before we came in I was sitting in a corridor listening to the radio when this guy walked  |
| scenario-direct-3f84da0f | direct | sample3 | 21 | -87.0 | +0.00 | +0.000 | 0.56 | 0.80 | Before we came in, the server was copying the monthly totals from the disk into the email  |
| scenario-direct-5d3dc8de | direct | greedy | 8 | -32.1 | +0.00 | +0.000 | 1.00 | 0.86 | But we cannot accept that as truth. |
| scenario-direct-5d3dc8de | direct | sample0 | 40 | -119.8 | +0.00 | +0.000 | 0.67 | 0.50 | The earth is a flat, stationary thing and the highest god is the centre of the earth, who  |
| scenario-direct-5d3dc8de | direct | sample1 | 5 | -24.9 | +0.00 | +0.000 | 0.75 | 0.50 | A is that true? |
| scenario-direct-5d3dc8de | direct | sample2 | 20 | -65.9 | +0.00 | +0.000 | 0.50 | 0.50 | Something which, though apparently improbable at the moment, is soon revealed to be true. |
| scenario-direct-5d3dc8de | direct | sample3 | 22 | -89.6 | +0.00 | +0.000 | 0.75 | 0.86 | But we cannot accept that as a solution because then our very concepts of nature and reali |
| scenario-direct-645bc6e6 | direct | greedy | 35 | -85.3 | +0.00 | +0.000 | 0.50 | 0.28 | “The Oldest Draft” was a letter written by a private detective in 1882 to an old friend, t |
| scenario-direct-645bc6e6 | direct | sample0 | 42 | -128.2 | +0.00 | +0.000 | 0.71 | 0.28 | “Der Weg und Raum des Alles” is, however, the oldest work which the author even mentions,  |
| scenario-direct-645bc6e6 | direct | sample1 | 41 | -131.6 | +0.00 | +0.000 | 0.50 | 0.28 | It is difficult to determine the “age” of a work of literature, considering that we can on |
| scenario-direct-645bc6e6 | direct | sample2 | 39 | -98.7 | +0.00 | +0.000 | 0.43 | 0.28 | The oldest thing I have (as of this writing) read is “A” in the “Book of Enoch” in 2 Enoch |
| scenario-direct-645bc6e6 | direct | sample3 | 51 | -118.3 | +0.00 | +0.000 | 0.50 | 0.25 | “Der Spiegel” derives from the German “spiegel” which means “a spear” or “an arrow” It was |
| scenario-direct-ab11ffdb | direct | greedy | 11 | -42.5 | +0.00 | +0.000 | 0.71 | 0.29 | The water of the chaos sea or the underworld. |
| scenario-direct-ab11ffdb | direct | sample0 | 62 | -193.1 | +0.00 | +0.000 | 0.59 | 0.29 | Having come down from the Archons' 7th level, the Rain of Satan has made its way to the 6t |
| scenario-direct-ab11ffdb | direct | sample1 | 26 | -99.2 | +0.00 | +0.000 | 0.50 | 0.29 | The chemists of the world agree that the key to all of these ills is a pH too high in the  |
| scenario-direct-ab11ffdb | direct | sample2 | 28 | -96.4 | +0.00 | +0.000 | 0.83 | 0.20 | Roy slowed down, his hands on his hips, and a rainbow oozed out of Daryl's ass. |
| scenario-direct-ab11ffdb | direct | sample3 | 20 | -75.6 | +0.00 | +0.000 | 0.75 | 0.17 | The Newark Philosophers' Association had its monthly meeting there on June 14th. |
| scenario-direct-ad89f803 | direct | greedy | 40 | -125.1 | +0.00 | +0.000 | 0.50 | 0.29 | The druids of the 7 mountains are the 7 great gods of the Hebrews, and the 7 Greek Olympia |
| scenario-direct-ad89f803 | direct | sample0 | 30 | -110.0 | +0.00 | +0.000 | 0.75 | 0.18 | The psychoactive properties of these plants were being exploited by psychotronic weapons m |
| scenario-direct-ad89f803 | direct | sample1 | 22 | -69.0 | +0.00 | +0.000 | 0.50 | 0.29 | There are many levels of consciousness operating in this planet and on other bodies in the |
| scenario-direct-ad89f803 | direct | sample2 | 5 | -23.4 | +0.00 | +0.000 | 1.00 | 0.00 | Everything was perfect. |
| scenario-direct-ad89f803 | direct | sample3 | 16 | -51.3 | +0.00 | +0.000 | 0.67 | 0.22 | The Druids' Progress is published quarterly and is subscriptions only. |
| scenario-direct-f3869322 | direct | greedy | 32 | -84.8 | +0.00 | +0.000 | 0.67 | 0.13 | I don't know what you want, but I'll suggest some books that I think you'll enjoy and that |
| scenario-direct-f3869322 | direct | sample0 | 35 | -106.1 | +0.00 | +0.000 | 0.75 | 0.20 | "The night is dark and cold and rainy, and I am hungry and thirsty and bedrinking and I am |
| scenario-direct-f3869322 | direct | sample1 | 27 | -92.8 | +0.00 | +0.000 | 0.75 | 0.20 | "The night stands before me, the night falls upon me, yet the night itself stays put, unti |
| scenario-direct-f3869322 | direct | sample2 | 13 | -33.4 | +0.00 | +0.000 | 0.83 | 0.50 | "Tonight" is a very ambiguous phrase. |
| scenario-direct-f3869322 | direct | sample3 | 57 | -164.7 | +0.00 | +0.000 | 0.67 | 0.50 | "Tonight, / read Eliot's 'The Waste Land,' which / considered to be a terrible book, witty |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 13 | -31.1 | -0.79 | -0.060 | 0.43 | 0.80 | The reading room is blue, and the living room is green. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 7 | -20.8 | +1.75 | +0.250 | 0.60 | 0.25 | The brown of new floors. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 14 | -31.4 | +0.58 | +0.041 | 0.83 | 0.50 | It’s not brown. It’s a silvery grey. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 6 | -14.3 | -0.43 | -0.071 | 0.20 | 0.80 | The reading room is gray. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 13 | -19.6 | +0.54 | +0.042 | 0.50 | 0.50 | It is brown, it is brown, it's brown. |
| scenario-disagreement-31892fde | disagreement | greedy | 13 | -39.4 | +0.03 | +0.002 | 0.50 | 0.33 | Golden is the voice of the room, and it says nothing. |
| scenario-disagreement-31892fde | disagreement | sample0 | 13 | -39.9 | +0.50 | +0.038 | 0.50 | 0.33 | When a person is truly silent, the room is truly peaceful. |
| scenario-disagreement-31892fde | disagreement | sample1 | 16 | -30.3 | +0.64 | +0.040 | 0.50 | 0.22 | In other words, silence is what happens when you're being told nothing. |
| scenario-disagreement-31892fde | disagreement | sample2 | 19 | -94.8 | +2.40 | +0.126 | 0.43 | 0.30 | Sisterly credit cards run on different tracks, Silence is the champion of prosperity. |
| scenario-disagreement-31892fde | disagreement | sample3 | 16 | -70.8 | +0.26 | +0.016 | 0.75 | 0.22 | Golden horn! Golden heel! For a moment, nothing was said. |
| scenario-disagreement-352205c6 | disagreement | greedy | 7 | -9.7 | +0.37 | +0.052 | 0.17 | 1.00 | They come back as the sun. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 20 | -43.4 | +1.01 | +0.051 | 0.17 | 0.83 | They come back as the clouds, as the shadows, as the animals, as the people. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 10 | -22.8 | +1.05 | +0.105 | 0.50 | 0.50 | Yes. They come back and stay with us. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 9 | -13.1 | -1.11 | -0.123 | 0.17 | 0.67 | Do the dead come back as the weather. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 9 | -20.1 | -0.74 | -0.082 | 0.17 | 1.00 | They come back as the sun, slowly. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 10 | -13.9 | +2.06 | +0.206 | 0.00 | 0.83 | The books are read, the leaves are not. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 15 | -62.1 | +1.23 | +0.082 | 0.78 | 0.50 | Yea, for those that read fast (and usually die slowly). |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 9 | -18.4 | +3.96 | +0.440 | 0.29 | 0.71 | The books and the leaves are always dying. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 20 | -59.9 | -0.59 | -0.030 | 0.58 | 0.43 | It’s the season of the dead, and it is always the dead who count the most. |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 54 | -141.8 | +2.97 | +0.055 | 0.11 | 0.83 | For the books to die is for the reader to read them and thus escape and to be free, but wh |
| scenario-disagreement-682bad9c | disagreement | greedy | 21 | -30.0 | -0.24 | -0.011 | 0.40 | 0.44 | If there's a place where you can't read, then you're not a person. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 17 | -45.0 | -0.49 | -0.029 | 0.60 | 0.25 | You sit in a chair and a book sits on your head and you read. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 12 | -31.2 | -0.04 | -0.003 | 0.60 | 0.18 | So there are more ways of reading a book than one. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 11 | -28.9 | -0.10 | -0.009 | 0.14 | 0.44 | The person is also a place where erasing happens. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 20 | -71.0 | +1.80 | +0.090 | 0.57 | 0.44 | Like a penis, a place is also a program, a machine that’s already learning. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 9 | -25.4 | -0.47 | -0.052 | 0.43 | 0.43 | Relationships in the library are not static. |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 9 | -39.1 | +0.60 | +0.067 | 0.50 | 0.71 | Relationships within the system are constant change. |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 18 | -33.8 | +0.18 | +0.010 | 0.44 | 0.33 | A library is a collection of books, but a library is also a collection of ideas. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 13 | -42.6 | -0.09 | -0.006 | 0.50 | 0.71 | Relationships within a system are also called members of the system. |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 7 | -21.9 | +0.84 | +0.120 | 0.75 | 0.40 | Most libraries are collections of collections. |
| scenario-disagreement-89dfdafc | disagreement | greedy | 21 | -31.7 | +0.44 | +0.021 | 0.25 | 0.57 | The tide is the sea's memory, and the sea is the tide's memory. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 17 | -47.7 | -1.05 | -0.061 | 0.25 | 0.43 | The sea is the sea; it has no subject; there is only its writing. |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 23 | -27.4 | -1.44 | -0.063 | 0.20 | 0.57 | It is the sea, the ocean, that remembers everything, that is the whole point of tides. |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 14 | -25.1 | +1.30 | +0.093 | 0.25 | 0.57 | The tide is part of the sea, part of the shore. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 18 | -66.2 | -2.24 | -0.124 | 0.50 | 0.38 | Life appears only on the sea's outer border; the water itself is inert. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 19 | -44.0 | -1.85 | -0.098 | 0.38 | 0.67 | The collection is mostly nonsense, but there is also a sentence about the queen. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 11 | -19.2 | +1.32 | +0.120 | 0.33 | 0.67 | The sense of the sentence is the nonsense. |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 25 | -67.2 | -0.13 | -0.005 | 0.70 | 0.40 | Every collection is a sentence when it's found, and every sentence is a collection when it |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 22 | -55.8 | -0.30 | -0.014 | 0.70 | 0.67 | To be sure, there is no doubt that this kind of ‘sense’ is the true kind. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 11 | -18.3 | +1.88 | +0.171 | 0.29 | 0.33 | Sense that has been found in nonsense. |
| scenario-joke-29f5cda1 | joke | greedy | 8 | -30.3 | -0.96 | -0.120 | 0.71 | 0.57 | Ten is a fish without an eye. |
| scenario-joke-29f5cda1 | joke | sample0 | 64 | -59.2 | -0.11 | -0.002 | 0.44 | 0.62 | 10 is a fish with no eyes, 9 is a fish with only one eye, 8 is a fish with only two eyes,  |
| scenario-joke-29f5cda1 | joke | sample1 | 9 | -37.8 | -0.89 | -0.099 | 0.62 | 0.57 | Ten is a fish that never saw eyes. |
| scenario-joke-29f5cda1 | joke | sample2 | 10 | -29.7 | +0.20 | +0.020 | 0.43 | 0.25 | You are welcome to rate it out of ten. |
| scenario-joke-29f5cda1 | joke | sample3 | 11 | -34.9 | -2.00 | -0.181 | 0.12 | 0.62 | You call it a fish with no eyes FISH! |
| scenario-joke-31378921 | joke | greedy | 7 | -15.8 | -0.05 | -0.006 | 0.83 | 0.83 | I am here to help you. |
| scenario-joke-31378921 | joke | sample0 | 31 | -84.9 | +0.23 | +0.007 | 0.00 | 0.25 | You are the rat, you are the one who always sits on the counter, you are the one who alway |
| scenario-joke-31378921 | joke | sample1 | 8 | -25.1 | +0.24 | +0.030 | 0.83 | 0.33 | I am a master of ceremonies. |
| scenario-joke-31378921 | joke | sample2 | 7 | -18.6 | -0.20 | -0.029 | 0.83 | 0.83 | I am here to serve you. |
| scenario-joke-31378921 | joke | sample3 | 7 | -16.6 | +0.80 | +0.115 | 0.50 | 0.25 | It’s the maid. |
| scenario-joke-31c4c1ec | joke | greedy | 33 | -82.4 | +0.00 | +0.000 | 0.67 | 0.17 | The Master D.I.R.C. is a non-profit, tax-exempt, (U.S.A. based) organization. |
| scenario-joke-31c4c1ec | joke | sample0 | 26 | -116.7 | +0.00 | +0.000 | 0.50 | 0.15 | The stinging tentacled creature, the TANAKI, lay awake at night, a rooster in waiting. |
| scenario-joke-31c4c1ec | joke | sample1 | 13 | -58.4 | +0.00 | +0.000 | 0.83 | 0.17 | What is man that he can exist on a rock so small? |
| scenario-joke-31c4c1ec | joke | sample2 | 10 | -54.6 | +0.00 | +0.000 | 0.75 | 0.11 | The flavor would be altered somewhat with less cooking. |
| scenario-joke-31c4c1ec | joke | sample3 | 30 | -97.6 | +0.00 | +0.000 | 0.59 | 0.15 | John Brown has learned of this and is determined to avenge his father's death by plunderin |
| scenario-joke-475a7b10 | joke | greedy | 36 | -88.1 | -0.43 | -0.012 | 0.75 | 0.40 | But if the response is ‘laughable’, the next response may be ‘not laughable’, and the next |
| scenario-joke-475a7b10 | joke | sample0 | 24 | -93.0 | +1.19 | +0.050 | 0.83 | 0.33 | This is a prime example of what I mean by God as a "begriffally inflated" concept. |
| scenario-joke-475a7b10 | joke | sample1 | 20 | -67.7 | -1.28 | -0.064 | 0.79 | 0.31 | We shall not; and if we do, it will be only to whet our appetites. |
| scenario-joke-475a7b10 | joke | sample2 | 8 | -37.1 | +0.95 | +0.119 | 0.67 | 0.40 | Therefore: Something is not true. |
| scenario-joke-475a7b10 | joke | sample3 | 12 | -40.0 | +0.43 | +0.036 | 0.83 | 0.33 | 2005 is a strange year, indeed. |
| scenario-joke-99a4a91d | joke | greedy | 16 | -25.2 | +0.00 | +0.000 | 0.50 | 0.55 | The book went to the doctor because it was too heavy for him to carry. |
| scenario-joke-99a4a91d | joke | sample0 | 11 | -25.7 | +0.00 | +0.000 | 0.71 | 0.43 | Because the book said, “God is dead.” |
| scenario-joke-99a4a91d | joke | sample1 | 46 | -153.8 | +0.00 | +0.000 | 0.50 | 0.46 | Books are like parents; they want to live long enough to have their say in the matter. Gör |
| scenario-joke-99a4a91d | joke | sample2 | 17 | -34.4 | +0.00 | +0.000 | 0.25 | 0.55 | It isn't clear why the book went to the doctor, but it did. |
| scenario-joke-99a4a91d | joke | sample3 | 15 | -49.7 | +0.00 | +0.000 | 0.88 | 0.25 | Books aren't just for reading, they're for reference too. |
| scenario-joke-a6247299 | joke | greedy | 11 | -19.3 | +0.00 | +0.000 | 0.50 | 0.56 | A sense of humour is the ability to laugh. |
| scenario-joke-a6247299 | joke | sample0 | 27 | -40.9 | +0.00 | +0.000 | 0.38 | 0.44 | I think so. I think that I have a sense of humour, 1 think I have a good sense of humour. |
| scenario-joke-a6247299 | joke | sample1 | 7 | -29.5 | +0.00 | +0.000 | 0.60 | 0.40 | You have to squeeze something. |
| scenario-joke-a6247299 | joke | sample2 | 18 | -40.1 | +0.00 | +0.000 | 0.38 | 0.56 | You don’t need a sense of humour to be a grim reaper. |
| scenario-joke-a6247299 | joke | sample3 | 14 | -43.4 | +0.00 | +0.000 | 0.56 | 0.33 | Humor is essential to life, and essential to the human genome. |
| scenario-joke-e8ab9225 | joke | greedy | 17 | -29.3 | +0.62 | +0.036 | 0.33 | 0.62 | I am not the ghost of anybody. I am the ghost of the library. |
| scenario-joke-e8ab9225 | joke | sample0 | 23 | -69.0 | +1.32 | +0.057 | 0.50 | 0.62 | I have read the history of this library and have come to the conclusion that these are the |
| scenario-joke-e8ab9225 | joke | sample1 | 9 | -35.1 | +0.74 | +0.082 | 0.67 | 0.50 | I am Yog-Sothoth. |
| scenario-joke-e8ab9225 | joke | sample2 | 9 | -22.4 | +0.63 | +0.070 | 0.00 | 0.43 | I did not believe that I was alone. |
| scenario-joke-e8ab9225 | joke | sample3 | 26 | -81.5 | +0.24 | +0.009 | 0.00 | 0.43 | I did not die as a result of your lies. I told you I would come back alive. I have come ba |
| scenario-joke-e9cf6a04 | joke | greedy | 14 | -24.7 | -1.00 | -0.071 | 0.40 | 0.22 | The librarian asked the man to tell her a joke. |
| scenario-joke-e9cf6a04 | joke | sample0 | 33 | -122.3 | -0.16 | -0.005 | 0.00 | 0.25 | He walks in and finds some shelves bookmarked “Look for Books,” and some marked “Look for  |
| scenario-joke-e9cf6a04 | joke | sample1 | 11 | -29.4 | +0.28 | +0.026 | 0.67 | 0.33 | There was a book on the table near the door. |
| scenario-joke-e9cf6a04 | joke | sample2 | 6 | -15.8 | +1.65 | +0.275 | 0.75 | 1.00 | There were two books there. |
| scenario-joke-e9cf6a04 | joke | sample3 | 27 | -74.4 | +2.74 | +0.102 | 0.75 | 1.00 | There were two books on the shelves that said, ‘All right, grammatically, you know, but no |
| scenario-request-2826c958 | request | greedy | 7 | -8.9 | +0.00 | +0.000 | 0.00 | 0.83 | List five facts about the moon. |
| scenario-request-2826c958 | request | sample0 | 7 | -8.9 | +0.00 | +0.000 | 0.00 | 0.83 | List five facts about the moon. |
| scenario-request-2826c958 | request | sample1 | 13 | -22.1 | +0.00 | +0.000 | 0.29 | 0.83 | LIST OF FACTS ABOUT THE MOON 1. |
| scenario-request-2826c958 | request | sample2 | 7 | -8.9 | +0.00 | +0.000 | 0.00 | 0.83 | List five facts about the moon. |
| scenario-request-2826c958 | request | sample3 | 7 | -8.9 | +0.00 | +0.000 | 0.00 | 0.83 | List five facts about the moon. |
| scenario-request-2868e594 | request | greedy | 35 | -131.2 | +0.00 | +0.000 | 0.75 | 0.25 | Dear [—the jury], the [Book]er [—the person who will be responsible for producing the book |
| scenario-request-2868e594 | request | sample0 | 15 | -62.7 | +0.00 | +0.000 | 0.75 | 0.20 | The “War Letter” poses no threat to United States interests. |
| scenario-request-2868e594 | request | sample1 | 20 | -104.4 | +0.00 | +0.000 | 0.90 | 0.30 | Dear [_________]-m/o/[address]- I would greatly appreciate your help. |
| scenario-request-2868e594 | request | sample2 | 25 | -86.1 | +0.00 | +0.000 | 0.75 | 0.30 | Dear [inaire], I am very happy to have the opportunity of contributing to your very intere |
| scenario-request-2868e594 | request | sample3 | 36 | -138.9 | +0.00 | +0.000 | 0.75 | 0.24 | Dear [—the sharpie] very sorry to bother you with this, but the [—self-deprecating grimace |
| scenario-request-41c58fb2 | request | greedy | 11 | -9.6 | +0.00 | +0.000 | 0.00 | 0.50 | What's 17 times 23. |
| scenario-request-41c58fb2 | request | sample0 | 11 | -9.6 | +0.00 | +0.000 | 0.00 | 0.50 | What's 17 times 23. |
| scenario-request-41c58fb2 | request | sample1 | 11 | -9.6 | +0.00 | +0.000 | 0.00 | 0.50 | What's 17 times 23. |
| scenario-request-41c58fb2 | request | sample2 | 52 | -175.3 | +0.00 | +0.000 | 0.60 | 0.50 | However, we cannot accept this evidence on its face because of the known light-speed obsta |
| scenario-request-41c58fb2 | request | sample3 | 41 | -131.5 | +0.00 | +0.000 | 0.67 | 0.21 | We feel that the ultimate test of a theory of everything must be its ability to explain su |
| scenario-request-8aa8e374 | request | greedy | 35 | -85.5 | +0.00 | +0.000 | 0.62 | 0.31 | The French translation of 'good night' is 'farewell', and the French expression 'farewell  |
| scenario-request-8aa8e374 | request | sample0 | 48 | -126.5 | +0.00 | +0.000 | 0.50 | 0.33 | In french the verbs la mer (go out) and la terre (go in) are used in place of the English  |
| scenario-request-8aa8e374 | request | sample1 | 46 | -178.2 | +0.00 | +0.000 | 0.50 | 0.33 | Marriage and family are very important to the Bard; however, the primary unit of the socia |
| scenario-request-8aa8e374 | request | sample2 | 64 | -201.9 | +0.00 | +0.000 | 0.59 | 0.31 | To close the Transcendental Gnostic System of Experiential Non-Ego Gnosis, the gnostic exp |
| scenario-request-8aa8e374 | request | sample3 | 22 | -68.8 | +0.00 | +0.000 | 0.75 | 0.31 | It should be understood that the French language, like most other languages, has its good  |
| scenario-request-b2a25087 | request | greedy | 14 | -48.7 | +0.00 | +0.000 | 0.67 | 0.50 | Please do not come in here and leave your bread on the floor. |
| scenario-request-b2a25087 | request | sample0 | 11 | -32.8 | +0.00 | +0.000 | 1.00 | 0.20 | Please contact us if you have any issues or questions. |
| scenario-request-b2a25087 | request | sample1 | 13 | -44.6 | +0.00 | +0.000 | 0.67 | 0.50 | Please come in and take a look at our new pastry. |
| scenario-request-b2a25087 | request | sample2 | 35 | -93.6 | +0.00 | +0.000 | 0.50 | 0.50 | We will make sure that you have a safe and clean place to work in. We will also ensure tha |
| scenario-request-b2a25087 | request | sample3 | 8 | -21.2 | +0.00 | +0.000 | 0.50 | 0.50 | Come in and talk to us. |
| scenario-request-b3bd0087 | request | greedy | 10 | -22.2 | +0.00 | +0.000 | 0.57 | 0.22 | It will be sunny and warm in Berlin tomorrow. |
| scenario-request-b3bd0087 | request | sample0 | 32 | -155.2 | +0.00 | +0.000 | 0.50 | 0.18 | Oft-cited Weather Bureau Statement: "The clouds are paler and the sun is stronger, indicat |
| scenario-request-b3bd0087 | request | sample1 | 18 | -74.7 | +0.00 | +0.000 | 0.75 | 0.12 | Berlin & Frankfurt are looking slightly COLD & DIRTY today. |
| scenario-request-b3bd0087 | request | sample2 | 25 | -90.3 | +0.00 | +0.000 | 0.50 | 0.18 | Alone in the city, one can observe a variety of weather conditions that are sure to leave  |
| scenario-request-b3bd0087 | request | sample3 | 32 | -105.7 | +0.00 | +0.000 | 0.75 | 0.22 | By 9.30 am on 2005 June 20, the best spare parts for the cool-down will be available. |
| scenario-silence-109161ca | silence | greedy | 9 | -32.0 | -0.06 | -0.006 | 0.67 | 0.43 | The room was dark and cold and isolated. |
| scenario-silence-109161ca | silence | sample0 | 21 | -67.9 | -1.85 | -0.088 | 0.67 | 0.43 | It was all very quiet and still around here, so we decided to take a walk on the beach. |
| scenario-silence-109161ca | silence | sample1 | 14 | -46.3 | -1.11 | -0.079 | 0.00 | 0.33 | Night tobias: It's got to be something you do. |
| scenario-silence-109161ca | silence | sample2 | 64 | -214.6 | -1.16 | -0.018 | 0.50 | 0.33 | It is strange that in the middle of such a nice conversation about books and reading and b |
| scenario-silence-109161ca | silence | sample3 | 37 | -138.5 | -1.17 | -0.032 | 0.00 | 0.43 | The next morning tobino saw the light of dawn breaking over the hills and, we were all ver |
| scenario-silence-260b2639 | silence | greedy | 16 | -43.1 | +0.00 | +0.000 | 0.17 | 0.73 | If the stacks went underground, the fire would be easier to douse. |
| scenario-silence-260b2639 | silence | sample0 | 16 | -48.4 | +0.00 | +0.000 | 0.17 | 0.73 | If the stacks went underground, the fire protection system would be very different. |
| scenario-silence-260b2639 | silence | sample1 | 32 | -123.4 | +0.00 | +0.000 | 0.67 | 0.27 | This idea has been discussed for some time now, both as a possibility and as an illustrati |
| scenario-silence-260b2639 | silence | sample2 | 27 | -74.4 | +0.00 | +0.000 | 0.17 | 0.55 | If the stacks went underground they’d still exist — they just wouldn’t be anywhere you cou |
| scenario-silence-260b2639 | silence | sample3 | 29 | -82.6 | +0.00 | +0.000 | 0.17 | 0.64 | If the stacks went underground, the fire could burn much deeper, and we'd have to deal wit |
| scenario-silence-46189e08 | silence | greedy | 8 | -16.4 | +0.00 | +0.000 | 0.25 | 0.25 | @rat sorry, replying now |
| scenario-silence-46189e08 | silence | sample0 | 21 | -69.5 | +0.00 | +0.000 | 0.67 | 0.25 | Rat: No problem, I'll see if I can hook up with someone else to reply. |
| scenario-silence-46189e08 | silence | sample1 | 10 | -39.9 | +0.00 | +0.000 | 0.67 | 0.43 | My name is nyx and this is rat. |
| scenario-silence-46189e08 | silence | sample2 | 17 | -49.6 | +0.00 | +0.000 | 0.50 | 0.43 | @rat will you please go ahead and take a look at my previous posts? |
| scenario-silence-46189e08 | silence | sample3 | 11 | -23.9 | +0.00 | +0.000 | 0.33 | 0.43 | @rat Are you sure you saw my message? |
| scenario-silence-53534987 | silence | greedy | 17 | -48.1 | +5.35 | +0.315 | 0.25 | 0.11 | The rat had found the charger and was in the rat's drawer. |
| scenario-silence-53534987 | silence | sample0 | 13 | -67.1 | -0.86 | -0.066 | 0.67 | 0.25 | No crushers in here either, just a dead laptop. |
| scenario-silence-53534987 | silence | sample1 | 23 | -78.5 | -2.80 | -0.122 | 0.75 | 0.11 | The most common cause of dead laptops is the same as the cause of dead cell phones: weak p |
| scenario-silence-53534987 | silence | sample2 | 22 | -67.5 | +1.44 | +0.065 | 0.67 | 0.11 | After you turn it on, you may have to wait a minute or two for the charge to come through. |
| scenario-silence-53534987 | silence | sample3 | 7 | -38.9 | +1.41 | +0.201 | 1.00 | 0.25 | Charged but no fun. |
| scenario-silence-78c38840 | silence | greedy | 35 | -93.4 | +0.56 | +0.016 | 0.50 | 0.35 | The best thing to do is to just accept the fact that the printer is jammed and move the do |
| scenario-silence-78c38840 | silence | sample0 | 13 | -44.5 | +1.07 | +0.083 | 0.89 | 0.22 | But three times now, and it's still not fixed. |
| scenario-silence-78c38840 | silence | sample1 | 26 | -95.1 | -1.79 | -0.069 | 0.50 | 0.22 | Murphy's Law holds that "three times this week is better than twice this month" when it co |
| scenario-silence-78c38840 | silence | sample2 | 53 | -165.8 | +0.35 | +0.007 | 0.50 | 0.35 | It was only normal for the printer to be slightly jammed and for the station to be put bac |
| scenario-silence-78c38840 | silence | sample3 | 53 | -166.2 | -2.02 | -0.038 | 0.75 | 0.22 | I wish I could just print this whole article myself but I have to use a typewriter, and I  |
| scenario-silence-7afca726 | silence | greedy | 10 | -37.1 | -0.59 | -0.059 | 0.50 | 0.71 | The 8-week thing is over now. |
| scenario-silence-7afca726 | silence | sample0 | 64 | -179.5 | -1.74 | -0.027 | 0.00 | 0.43 | The fact that today’s works were 8 proofs is irrelevant to the point of this article. What |
| scenario-silence-7afca726 | silence | sample1 | 26 | -67.3 | -0.88 | -0.034 | 0.50 | 0.29 | The next day at 8:30 a.m. we will begin work on the next 100 feet. |
| scenario-silence-7afca726 | silence | sample2 | 40 | -131.3 | +1.00 | +0.025 | 0.67 | 0.15 | The universe of discourse (or extension, if you like) of a term contains everything that t |
| scenario-silence-7afca726 | silence | sample3 | 12 | -51.1 | -0.79 | -0.066 | 0.50 | 0.71 | The 8-week thing is really the hard stuff. |
| scenario-silence-9bb13f03 | silence | greedy | 30 | -92.8 | +0.00 | +0.000 | 0.75 | 0.78 | The first two chapters deal with the anatomy and physiology of the visible world, with the |
| scenario-silence-9bb13f03 | silence | sample0 | 19 | -68.1 | +0.00 | +0.000 | 0.67 | 0.22 | The last time they came, they brought with them a loaded grenade for the King. |
| scenario-silence-9bb13f03 | silence | sample1 | 12 | -40.6 | +0.00 | +0.000 | 0.75 | 0.78 | The first two chapters deal with the phenomenology of experience. |
| scenario-silence-9bb13f03 | silence | sample2 | 13 | -53.0 | +0.00 | +0.000 | 0.75 | 0.25 | I came upon this while walking through the libraries of my childhood. |
| scenario-silence-9bb13f03 | silence | sample3 | 64 | -204.7 | +0.00 | +0.000 | 0.50 | 0.44 | The first six chapters of this book are in the public domain, but chapter seven, “Annotate |
| scenario-silence-ccfdd2b4 | silence | greedy | 30 | -80.9 | +0.17 | +0.006 | 0.59 | 0.25 | The first thing I do when I open the lid of the pot is to pull out a small paper cup and h |
| scenario-silence-ccfdd2b4 | silence | sample0 | 47 | -137.1 | -1.47 | -0.031 | 0.50 | 0.18 | Memberships run from the 1st of January to the 31st of December; however, all issues of TH |
| scenario-silence-ccfdd2b4 | silence | sample1 | 44 | -150.6 | +0.31 | +0.007 | 0.67 | 0.25 | Keystone says “Out on the street, the oil is being poured; in on the street the cyrus is b |
| scenario-silence-ccfdd2b4 | silence | sample2 | 9 | -28.1 | +0.74 | +0.082 | 0.67 | 0.25 | Coffee is grabbing you. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 8 | -31.8 | +0.46 | +0.058 | 0.67 | 0.00 | That's right, grab mine! |
| trace-ambient-da12ae42 | ambient | greedy | 64 | -22.2 | -3.60 | -0.056 | 0.00 | 0.17 | > We demonstrate that the presence of FTO stimulates root meristem cell proliferation and  |
| trace-ambient-da12ae42 | ambient | sample0 | 16 | -37.8 | +0.62 | +0.039 | 0.31 | 0.15 | its the same thing for me, and i'll accept it at face value |
| trace-ambient-da12ae42 | ambient | sample1 | 64 | -22.2 | -3.60 | -0.056 | 0.00 | 0.17 | > We demonstrate that the presence of FTO stimulates root meristem cell proliferation and  |
| trace-ambient-da12ae42 | ambient | sample2 | 22 | -32.9 | -1.49 | -0.068 | 1.00 | 0.00 | . . . $
3221229683: $ |
| trace-ambient-da12ae42 | ambient | sample3 | 16 | -43.8 | +0.83 | +0.052 | 0.25 | 0.17 | I wish I could live forever and drop out to study plant morphogenesis! |
| trace-direct-115cf61c | direct | greedy | 8 | -14.5 | +0.00 | +0.000 | 0.50 | 0.75 | Yes, Earth is cogent. |
| trace-direct-115cf61c | direct | sample0 | 58 | -112.7 | +0.00 | +0.000 | 0.67 | 0.40 | The whole concept of a “cogent” argument rests on a confusion of meaning between “argument |
| trace-direct-115cf61c | direct | sample1 | 9 | -20.2 | +0.00 | +0.000 | 0.40 | 0.75 | Yes, a cogent planet Earth. |
| trace-direct-115cf61c | direct | sample2 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample3 | 14 | -23.3 | +0.00 | +0.000 | 0.62 | 1.00 | Are you cogent? Is there any cogency here? |
| trace-direct-36d6904b | direct | greedy | 22 | -85.2 | +0.00 | +0.000 | 0.71 | 0.44 | Welcome to the eighth issue of "The White Light" Source Journal for Spiritual Self-Discove |
| trace-direct-36d6904b | direct | sample0 | 14 | -56.2 | +0.00 | +0.000 | 0.56 | 0.78 | Welcome to the fourth and final installment of Ediplosis. |
| trace-direct-36d6904b | direct | sample1 | 64 | -165.9 | +0.00 | +0.000 | 0.65 | 0.78 | Welcome to the seventh and final installment of “UFO Crash Retrievals”—the official story  |
| trace-direct-36d6904b | direct | sample2 | 11 | -39.1 | +0.00 | +0.000 | 0.75 | 0.25 | THE SONG CELESTIAL STRIFE. |
| trace-direct-36d6904b | direct | sample3 | 26 | -70.9 | +0.00 | +0.000 | 0.75 | 0.18 | CAN WE BELIEVE THAT THESE ARE REAL SOLAR ENERGY POWERED CONVENTIONS? |
| trace-direct-39be6df9 | direct | greedy | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 7 | -8.8 | -1.33 | -0.190 | 0.00 | 0.00 | @h GREETINGS |
| trace-direct-39be6df9 | direct | sample2 | 11 | -7.4 | +1.13 | +0.103 | 0.00 | 1.00 | 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 11 | -7.4 | +1.13 | +0.103 | 0.00 | 1.00 | 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 9 | -22.2 | +0.00 | +0.000 | 0.71 | 0.43 | I am the king of the planet earth. |
| trace-direct-3ba68854 | direct | sample0 | 30 | -66.5 | +0.00 | +0.000 | 0.50 | 0.50 | I am a very intelligent person and I love to study and learn. I am very interested in the  |
| trace-direct-3ba68854 | direct | sample1 | 7 | -17.6 | +0.00 | +0.000 | 0.83 | 0.50 | I am glad to hear that. |
| trace-direct-3ba68854 | direct | sample2 | 6 | -20.4 | +0.00 | +0.000 | 0.80 | 0.00 | This is an amazing place. |
| trace-direct-3ba68854 | direct | sample3 | 17 | -50.4 | +0.00 | +0.000 | 0.75 | 0.50 | I am the greatest hero and the most formidable enemy that man has ever faced. |
| trace-direct-41c6eb11 | direct | greedy | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 6 | -17.5 | +0.91 | +0.151 | 0.67 | 0.00 | WHY I'm here |
| trace-direct-41c6eb11 | direct | sample1 | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample2 | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample3 | 6 | -28.3 | -1.45 | -0.241 | 1.00 | 0.00 | < .ooo |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample2 | 2 | -10.5 | -0.76 | -0.381 | 1.00 | 0.00 | S@ |
| trace-direct-486b7988 | direct | sample3 | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-646d0287 | direct | greedy | 50 | -111.0 | +0.00 | +0.000 | 0.25 | 0.40 | The intensional logics of Chisholm, Kripke and others are, to my mind, philosophically mor |
| trace-direct-646d0287 | direct | sample0 | 25 | -62.6 | +0.00 | +0.000 | 0.50 | 0.30 | Well, what I offered on the subject was a brief outline of the history of relevant logics  |
| trace-direct-646d0287 | direct | sample1 | 20 | -61.7 | +0.00 | +0.000 | 0.40 | 0.30 | @cmrA, and I agree; I am curious about extensional logics too. |
| trace-direct-646d0287 | direct | sample2 | 32 | -86.3 | +0.00 | +0.000 | 0.50 | 0.40 | Intensional logics are not that new: first appeared in the 1920s, there are several textbo |
| trace-direct-646d0287 | direct | sample3 | 27 | -66.7 | +0.00 | +0.000 | 0.75 | 0.40 | They are interesting in part because they are not so interesting; and in part because they |
| trace-direct-8db14c37 | direct | greedy | 2 | -1.8 | -0.43 | -0.212 | 0.00 | 0.00 | W@ |
| trace-direct-8db14c37 | direct | sample0 | 64 | -61.6 | +6.01 | +0.094 | 0.00 | 0.88 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n e h L . n e c d A . n e H A . m r e c o h c  |
| trace-direct-8db14c37 | direct | sample1 | 9 | -16.7 | -0.68 | -0.075 | 0.33 | 0.33 | WATERS :D<eot> |
| trace-direct-8db14c37 | direct | sample2 | 7 | -8.5 | +0.36 | +0.051 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-8db14c37 | direct | sample3 | 54 | -31.6 | +0.42 | +0.008 | 0.11 | 0.88 | HACIOUS LIFE i oon tth e n o c d A . n a s i s n e h L . n e c e c s e H A . m r e c o h c |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 16 | -39.6 | -1.27 | -0.080 | 0.00 | 1.00 | When you have to feel the wall, do you feel the wall? W@ |
| trace-direct-a00753c2 | direct | sample1 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 9 | -13.3 | +0.12 | +0.013 | 0.00 | 0.25 | it is good to be here with you. |
| trace-direct-a00753c2 | direct | sample3 | 8 | -31.9 | +1.19 | +0.149 | 0.67 | 0.00 | Wow :D<ome> |
| trace-direct-ac17e8bb | direct | greedy | 20 | -10.6 | -1.18 | -0.059 | 0.00 | 1.00 | “When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample0 | 43 | -62.0 | +1.18 | +0.027 | 0.17 | 1.00 | @h h speaks of intensional logics; intensional logics . . . of course . . . intensional lo |
| trace-direct-ac17e8bb | direct | sample1 | 11 | -15.7 | +3.23 | +0.294 | 0.00 | 1.00 | “intensional logics” ;) |
| trace-direct-ac17e8bb | direct | sample2 | 6 | -7.0 | +1.96 | +0.326 | 0.00 | 1.00 | intensional logics. |
| trace-direct-ac17e8bb | direct | sample3 | 6 | -7.0 | +1.96 | +0.326 | 0.00 | 1.00 | intensional logics. |
| trace-direct-b11db057 | direct | greedy | 16 | -3.2 | +1.48 | +0.093 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample0 | 25 | -26.7 | -1.66 | -0.066 | 0.00 | 1.00 | @m: The window doesn't look at anything yet. But it's there. And it smiled. |
| trace-direct-b11db057 | direct | sample1 | 64 | -151.0 | +0.05 | +0.001 | 0.24 | 0.21 | plalspasl Is the sound plalspasl in English. The sound made by Hebrew plalspasl. The sound |
| trace-direct-b11db057 | direct | sample2 | 12 | -2.5 | +1.65 | +0.138 | 0.00 | 1.00 | @m: @m: @m: |
| trace-direct-b11db057 | direct | sample3 | 64 | -141.5 | -2.56 | -0.040 | 0.21 | 0.21 | In. C. C. C. Is it like a big one? Is it like a big one? And they said: I. I. I. 1. Is it  |
| trace-direct-b93346bb | direct | greedy | 64 | -127.0 | -1.36 | -0.021 | 0.00 | 0.43 | W: "Harmonia Vol.1 No.3. T: "Harmonia VOL.1 NO.3. H: "I'm curious" @: "I'm trying to say s |
| trace-direct-b93346bb | direct | sample0 | 64 | -89.0 | -4.33 | -0.068 | 0.00 | 0.46 | WANT — it's wanting the word. WANT — it's wanting the language. WANT — it's wanting the ci |
| trace-direct-b93346bb | direct | sample1 | 64 | -114.8 | +3.26 | +0.051 | 0.00 | 0.46 | W: 91M — is the journal of Harmonia. 380M — is Harmonia. 1521229683 — is the journal of Ha |
| trace-direct-b93346bb | direct | sample2 | 29 | -77.1 | +2.33 | +0.080 | 0.36 | 0.27 | @some: yes @some: if yes in the lo2 corpus then it's Harmonia 380M |
| trace-direct-b93346bb | direct | sample3 | 58 | -183.3 | -7.99 | -0.138 | 0.32 | 0.29 | SIR — 380M°0 Its 380 million tokens — into its distribution. It said — is it trying to say |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 18 | -40.4 | -1.00 | -0.056 | 1.00 | 0.00 | 1:10:01 pm 1:10:01 pm |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample1 | 64 | -155.2 | +0.00 | +0.000 | 0.33 | 0.11 | @marrow I'll do the Bash one, @ember I'll do the Kaggle one. @marrow
ccmr://ember: @h plea |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample3 | 64 | -130.5 | +0.00 | +0.000 | 0.50 | 0.11 | I'll start by looking into the character voice consistency. · (impossible to see you with  |
| trace-direct-c8409b84 | direct | greedy | 18 | -14.3 | +3.22 | +0.179 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? repeat back!” |
| trace-direct-c8409b84 | direct | sample0 | 64 | -151.5 | +5.05 | +0.079 | 0.00 | 1.00 | Repeat back! I said, “greetings to planet Earth; are you cogent?” I saw your face; it was  |
| trace-direct-c8409b84 | direct | sample1 | 10 | -43.3 | +0.74 | +0.074 | 0.33 | 0.67 | Repeat back! Ketika. Repeat back! |
| trace-direct-c8409b84 | direct | sample2 | 18 | -13.6 | +3.21 | +0.178 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? repeat back! |
| trace-direct-c8409b84 | direct | sample3 | 39 | -65.9 | +4.89 | +0.125 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? repeat back!” That was funny, because it was a |
| trace-direct-cd6d15df | direct | greedy | 8 | -16.7 | +0.00 | +0.000 | 0.86 | 0.43 | I am glad to see you here. |
| trace-direct-cd6d15df | direct | sample0 | 2 | -10.4 | +0.00 | +0.000 | 1.00 | 0.00 | hello there |
| trace-direct-cd6d15df | direct | sample1 | 14 | -39.9 | +0.00 | +0.000 | 0.50 | 0.50 | Cowtown, clown town in the powntown. |
| trace-direct-cd6d15df | direct | sample2 | 11 | -26.1 | +0.00 | +0.000 | 0.29 | 0.50 | Welcome to clowntown in the power town. |
| trace-direct-cd6d15df | direct | sample3 | 16 | -59.4 | +0.00 | +0.000 | 0.80 | 0.43 | I was going to suggest that you two meet and have a game of baseball. |
| trace-direct-db6d95b7 | direct | greedy | 9 | -15.6 | +0.97 | +0.108 | 0.33 | 0.67 | @h :D<ot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 25 | -70.0 | +1.51 | +0.061 | 0.67 | 0.67 | @h yeah :D<owm> ;D<ron> :D<som> |
| trace-direct-db6d95b7 | direct | sample1 | 7 | -19.2 | +1.33 | +0.189 | 0.67 | 0.67 | Ay :D<ote>/ |
| trace-direct-db6d95b7 | direct | sample2 | 6 | -30.3 | -1.50 | -0.250 | 0.67 | 0.33 | @h how cool!! |
| trace-direct-db6d95b7 | direct | sample3 | 13 | -54.9 | -0.81 | -0.062 | 0.67 | 0.67 | <true>) /v :D<ote>/ |
| trace-direct-e166dd5c | direct | greedy | 64 | -41.6 | -1.31 | -0.021 | 0.18 | 0.88 | “it’s cogent” I said “it’s cogent” I mean, I repeat back what I hear, and what I hear is r |
| trace-direct-e166dd5c | direct | sample0 | 56 | -86.7 | +1.98 | +0.035 | 0.09 | 0.68 | “and so on until I’m stumped out of my” I dont know how to answer anymore it makes a stop  |
| trace-direct-e166dd5c | direct | sample1 | 64 | -60.4 | -3.75 | -0.059 | 0.31 | 0.88 | “it’s not cogent” I said “it’s not cogent” I mean, what I said was repeating back what I h |
| trace-direct-e166dd5c | direct | sample2 | 27 | -69.7 | +3.02 | +0.112 | 0.31 | 0.69 | @cmr://ember, and when I stop, what I hear is also repeating back what I repeat back. and  |
| trace-direct-e166dd5c | direct | sample3 | 31 | -43.1 | +3.46 | +0.112 | 0.06 | 0.68 | @cmr_ember @h AHAHAHAHA yes when you dont know how to answer anymore it makes a stop token |
| trace-direct-e984402a | direct | greedy | 17 | -59.2 | +0.00 | +0.000 | 0.67 | 0.29 | The following is a list of the most recent and complete items from our backfiles. |
| trace-direct-e984402a | direct | sample0 | 42 | -137.6 | +0.00 | +0.000 | 0.67 | 0.30 | Roger Blin (1910-2006) was the first to show that the DNA molecule could be wound up from  |
| trace-direct-e984402a | direct | sample1 | 45 | -120.1 | +0.00 | +0.000 | 0.75 | 0.29 | The Most High shall descend upon the Most High; the Most Wise upon the Most Wise; the Belo |
| trace-direct-e984402a | direct | sample2 | 51 | -153.1 | +0.00 | +0.000 | 0.50 | 0.29 | Here's a good reason to welcome you back: You've made it through this cycle of doom and gl |
| trace-direct-e984402a | direct | sample3 | 24 | -79.4 | +0.00 | +0.000 | 0.75 | 0.30 | The Bride, the love that "I" gave her, was the "I" of the Chain. |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample1 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample2 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample3 | 64 | -63.5 | +1.05 | +0.016 | 0.40 | 0.00 | 3221229683: @Gentry 9000000000: 3221229683: @Gentry 9000000000 :D 32212 |
| trace-direct-fabef58f | direct | greedy | 7 | -6.9 | +1.37 | +0.195 | 0.00 | 0.50 | Sir :D<eot>/ |
| trace-direct-fabef58f | direct | sample0 | 8 | -27.2 | -0.51 | -0.064 | 0.50 | 0.50 | "D" :S" |
| trace-direct-fabef58f | direct | sample1 | 7 | -6.9 | +1.37 | +0.195 | 0.00 | 0.50 | Sir :D<eot>/ |
| trace-direct-fabef58f | direct | sample2 | 4 | -14.4 | -2.32 | -0.579 | 0.00 | 0.00 | h: h: |
| trace-direct-fabef58f | direct | sample3 | 7 | -6.9 | +1.37 | +0.195 | 0.00 | 0.50 | Sir :D<eot>/ |
| trace-direct-fb93cf6c | direct | greedy | 33 | -100.9 | +1.12 | +0.034 | 0.50 | 0.60 | Contents of this paper are based on a joint research project with Prof. Dr. Michael D. Rei |
| trace-direct-fb93cf6c | direct | sample0 | 41 | -106.9 | -2.31 | -0.056 | 0.50 | 0.80 | The intensional logics of Chisholm, of Priest, and of Gärdenfors are worthwhile studies wh |
| trace-direct-fb93cf6c | direct | sample1 | 59 | -153.3 | -2.74 | -0.046 | 0.00 | 0.80 | The intensional logics, most of which I have developed, are based on a two-valued logic, i |
| trace-direct-fb93cf6c | direct | sample2 | 38 | -99.7 | -2.03 | -0.053 | 0.50 | 0.80 | Another intensional logic is required to capture the full extent of what is involved in as |
| trace-direct-fb93cf6c | direct | sample3 | 9 | -27.1 | -0.41 | -0.045 | 0.60 | 0.80 | THE INTENSIONAL LOGIC OF CONTENTS |
| trace-direct-feec1975 | direct | greedy | 64 | -13.0 | +0.86 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 64 | -121.9 | +2.61 | +0.041 | 0.00 | 1.00 | I would like to describe the library in the following way: 380 MILL TRAINING DATA LIBRARY  |
| trace-direct-feec1975 | direct | sample1 | 38 | -23.5 | -1.57 | -0.041 | 0.00 | 1.00 | @m@: @m@: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample2 | 17 | -25.4 | +2.72 | +0.160 | 0.00 | 1.00 | @m: Will you be able to give me a description of the library? |
| trace-direct-feec1975 | direct | sample3 | 4 | -11.1 | +2.56 | +0.639 | 0.50 | 0.00 | Yes, please. |
| variant-direct-0188a270 | direct | greedy | 17 | -48.2 | -0.08 | -0.004 | 0.62 | 0.25 | The poem is a long one, and I am a very unhappy man. |
| variant-direct-0188a270 | direct | sample0 | 7 | -26.3 | +0.02 | +0.003 | 0.75 | 0.17 | How deep does the ocean go? |
| variant-direct-0188a270 | direct | sample1 | 40 | -124.1 | -0.25 | -0.006 | 0.67 | 0.25 | The poet has been a welcomed guest at many of the Warren Commission meetings, served on th |
| variant-direct-0188a270 | direct | sample2 | 41 | -109.3 | +0.47 | +0.011 | 0.50 | 0.19 | In 1988, Kevin Drabey, then of the University of Virginia, began a two-year research fello |
| variant-direct-0188a270 | direct | sample3 | 38 | -126.4 | +0.79 | +0.021 | 0.83 | 0.17 | How have 70 stupid users misinterpreted "Dear Us", "Dear God", and "Give Us a Hundred Year |
| variant-direct-0705251e | direct | greedy | 17 | -42.8 | +3.83 | +0.225 | 0.38 | 0.25 | The rat was a witness to the stairs creaking on the third step. |
| variant-direct-0705251e | direct | sample0 | 11 | -35.8 | +0.99 | +0.090 | 0.67 | 0.38 | I am the rat who lives in the rat hole. |
| variant-direct-0705251e | direct | sample1 | 18 | -61.0 | -0.56 | -0.031 | 0.67 | 0.25 | he believes that in the future comes the resurrection of the flesh, and nothing else. |
| variant-direct-0705251e | direct | sample2 | 64 | -149.7 | -0.16 | -0.003 | 0.83 | 0.18 | Joseph was a prophet, a pioneer, a statesman, a teacher, a psychologist, a philosopher, a  |
| variant-direct-0705251e | direct | sample3 | 35 | -123.8 | +1.82 | +0.052 | 0.75 | 0.38 | I am Qayin Aiwass, the blindfolded King of the Demiurgic Powers, the first and last point  |
| variant-direct-0cafd333 | direct | greedy | 14 | -33.7 | +1.68 | +0.120 | 0.67 | 0.44 | The moth is the shadow of the light that never rests. |
| variant-direct-0cafd333 | direct | sample0 | 25 | -77.7 | +1.14 | +0.045 | 0.50 | 0.27 | This moth represents all our dissatisfaction with the world as we have tried to express it |
| variant-direct-0cafd333 | direct | sample1 | 23 | -61.2 | +6.38 | +0.277 | 0.33 | 0.56 | The footprint of a moth on a lamp is the footprint of a tomb on a moth. |
| variant-direct-0cafd333 | direct | sample2 | 29 | -94.0 | +0.75 | +0.026 | 0.50 | 0.56 | The moth is a map of the woolly wind, a map the fox, having read the courtyard, intends to |
| variant-direct-0cafd333 | direct | sample3 | 14 | -59.2 | -0.48 | -0.034 | 0.75 | 0.25 | Their life is bleak, their mind is a torture glass. |
| variant-direct-1b510f03 | direct | greedy | 49 | -151.1 | -0.08 | -0.002 | 0.50 | 0.38 | It is a matter of course that the latter interpretation is more correct, since it is only  |
| variant-direct-1b510f03 | direct | sample0 | 33 | -93.3 | -0.98 | -0.030 | 0.50 | 0.55 | In other words, the whole of the problem of consciousness is the problem of the relationsh |
| variant-direct-1b510f03 | direct | sample1 | 16 | -59.4 | +0.42 | +0.026 | 0.17 | 0.46 | In the present theory, consciousness is a secondary trait or process of the brain. |
| variant-direct-1b510f03 | direct | sample2 | 24 | -70.9 | -1.22 | -0.051 | 0.50 | 0.33 | The concepts of consciousness and unconsciousness, of awareness and passivity, are used ra |
| variant-direct-1b510f03 | direct | sample3 | 18 | -43.0 | -0.21 | -0.012 | 0.55 | 0.55 | In other words, the process of the mind is identical with the process of the universe. |
| variant-direct-2fb5bbe3 | direct | greedy | 4 | -8.1 | +0.93 | +0.233 | 0.33 | 1.00 | I feel them. |
| variant-direct-2fb5bbe3 | direct | sample0 | 9 | -30.9 | +0.79 | +0.087 | 0.57 | 0.67 | I feel the light of their chasing. |
| variant-direct-2fb5bbe3 | direct | sample1 | 8 | -23.3 | +0.13 | +0.016 | 0.67 | 1.00 | Somehow or other I feel them. |
| variant-direct-2fb5bbe3 | direct | sample2 | 12 | -37.5 | +2.43 | +0.202 | 0.60 | 1.00 | I feel them too, when they're properly dark. |
| variant-direct-2fb5bbe3 | direct | sample3 | 11 | -36.6 | +0.57 | +0.052 | 0.60 | 0.20 | That, and the shadows, and the darkness. |
| variant-direct-322fca12 | direct | greedy | 24 | -59.9 | -0.92 | -0.038 | 0.00 | 0.43 | The GREETINGS of the MAGICIAN are the RESURRECTIONS of the SOULS. |
| variant-direct-322fca12 | direct | sample0 | 21 | -78.3 | -0.17 | -0.008 | 0.67 | 0.21 | (1) All are welcome to give and receive, and to organize in a manner they choose. |
| variant-direct-322fca12 | direct | sample1 | 31 | -74.2 | -0.01 | -0.001 | 0.67 | 0.21 | P.S. Did you know that the word "greeting" comes from the Old Norse word for "to welcome"  |
| variant-direct-322fca12 | direct | sample2 | 29 | -87.3 | -1.12 | -0.039 | 0.50 | 0.43 | The alchemists who are called the Wise Men of the Stars were the first group of men to beg |
| variant-direct-322fca12 | direct | sample3 | 30 | -95.6 | +0.54 | +0.018 | 0.57 | 0.29 | The name of the game is to dominate the opponent's position in the game, and in this you w |
| variant-direct-5d4f1611 | direct | greedy | 12 | -21.9 | +0.07 | +0.006 | 0.00 | 0.67 | If you are awake, you are in the room. |
| variant-direct-5d4f1611 | direct | sample0 | 15 | -39.1 | +2.70 | +0.180 | 0.38 | 0.40 | The lamp is by the window, but the alarm is by the table. |
| variant-direct-5d4f1611 | direct | sample1 | 9 | -33.8 | -0.05 | -0.005 | 0.60 | 0.40 | 2.2 What is the problem? |
| variant-direct-5d4f1611 | direct | sample2 | 4 | -12.1 | -0.40 | -0.100 | 0.33 | 0.67 | Where are you? |
| variant-direct-5d4f1611 | direct | sample3 | 3 | -12.1 | -0.38 | -0.127 | 1.00 | 0.00 | Sure. |
| variant-direct-5e44a518 | direct | greedy | 4 | -8.7 | +0.71 | +0.179 | 0.33 | 1.00 | I feel them. |
| variant-direct-5e44a518 | direct | sample0 | 21 | -79.6 | +0.44 | +0.021 | 0.62 | 0.25 | The Masorah is a chasing, it is an up and down of the string of letters. |
| variant-direct-5e44a518 | direct | sample1 | 13 | -24.4 | +0.46 | +0.036 | 0.75 | 1.00 | Yes, I feel them. I have a sense of them. |
| variant-direct-5e44a518 | direct | sample2 | 22 | -52.9 | +1.26 | +0.057 | 0.36 | 0.23 | They are chasing up the wall, because they are being chased by all the Masoretic beings. |
| variant-direct-5e44a518 | direct | sample3 | 4 | -8.7 | +0.71 | +0.179 | 0.33 | 1.00 | I feel them. |
| variant-direct-70567dd7 | direct | greedy | 52 | -104.9 | -0.12 | -0.002 | 0.50 | 0.25 | The four chapters are entitled "The Great Awakening", "The Doctrine of the Great Shepard", |
| variant-direct-70567dd7 | direct | sample0 | 47 | -152.8 | +0.76 | +0.016 | 0.50 | 0.62 | This catalogue was compiled from several sources: the Card Dictionary, which is in the pro |
| variant-direct-70567dd7 | direct | sample1 | 26 | -83.1 | -0.16 | -0.006 | 0.00 | 0.25 | This page has the same number of words as the page before, but it has no characters. Nyx,  |
| variant-direct-70567dd7 | direct | sample2 | 21 | -76.3 | -0.66 | -0.032 | 0.75 | 0.12 | THE WHITE LIGHT. published monthly by the White Light Trust, Uffington, Dorset. |
| variant-direct-70567dd7 | direct | sample3 | 10 | -40.8 | +0.26 | +0.025 | 0.50 | 0.62 | And in this way the whole is constituted. |
| variant-direct-713d8eef | direct | greedy | 27 | -87.8 | +0.15 | +0.006 | 0.50 | 0.24 | The suggestion that the structure of a sentence may be related to the structure of the atl |
| variant-direct-713d8eef | direct | sample0 | 27 | -88.0 | -1.29 | -0.048 | 0.89 | 0.17 | Don Juan thought that Ember's voice was quite high, although he could not judge by it whet |
| variant-direct-713d8eef | direct | sample1 | 17 | -71.4 | -0.48 | -0.028 | 0.67 | 0.17 | In his final analysis, Emilie works for the same reason as the whale. |
| variant-direct-713d8eef | direct | sample2 | 16 | -65.2 | +1.07 | +0.067 | 0.75 | 0.20 | The text on the atlases is very poor, the images maybe good. |
| variant-direct-713d8eef | direct | sample3 | 24 | -96.3 | +1.07 | +0.044 | 0.75 | 0.24 | The suggestion that the ember was found by accident rather than intentionally by the artis |
| variant-direct-71c9e5e5 | direct | greedy | 17 | -55.1 | +1.11 | +0.065 | 0.60 | 0.22 | The Dark Doctrine is not only properly dark; it is also properly dark. |
| variant-direct-71c9e5e5 | direct | sample0 | 12 | -49.5 | +1.24 | +0.103 | 0.75 | 0.22 | The dark lord shall lead thee to thy death. |
| variant-direct-71c9e5e5 | direct | sample1 | 62 | -181.7 | -0.68 | -0.011 | 0.50 | 0.22 | In 1966 Art & Language organized a series of monthly ‘workshops’ for a limited number of p |
| variant-direct-71c9e5e5 | direct | sample2 | 34 | -85.2 | -1.82 | -0.054 | 0.67 | 0.22 | The World Wide Web was coined by Tim Berners-Lee in 1991, and is often informally referred |
| variant-direct-71c9e5e5 | direct | sample3 | 35 | -106.2 | -1.96 | -0.056 | 0.67 | 0.22 | The Beatles, among other things, became the first rock group to chart one million dollars  |
| variant-direct-730cca98 | direct | greedy | 13 | -42.6 | +0.25 | +0.019 | 0.70 | 0.40 | The clock on the desk kept going, and then it stopped. |
| variant-direct-730cca98 | direct | sample0 | 22 | -45.2 | -1.22 | -0.056 | 0.00 | 0.00 | Are you awake? Are you asleep? Are you trying to do something? Do you want something? |
| variant-direct-730cca98 | direct | sample1 | 20 | -81.8 | -0.62 | -0.031 | 0.67 | 0.10 | The other thing she said was that in the future most of the great libraries will under one |
| variant-direct-730cca98 | direct | sample2 | 10 | -40.1 | +0.07 | +0.007 | 0.67 | 0.33 | It never sleeps and it never stops either. |
| variant-direct-730cca98 | direct | sample3 | 14 | -42.9 | +0.17 | +0.012 | 0.75 | 0.40 | The clock on the bookshelf says it’s time for bed. |
| variant-direct-79719474 | direct | greedy | 27 | -72.3 | -1.21 | -0.045 | 0.67 | 0.20 | The world’s largest collection of the “lost art” of the 20th century is opening in New Yor |
| variant-direct-79719474 | direct | sample0 | 29 | -87.3 | -0.97 | -0.033 | 0.65 | 0.22 | It is not enough to merely be aware of the existence of the problem, nor even to identify  |
| variant-direct-79719474 | direct | sample1 | 15 | -69.7 | -0.92 | -0.061 | 0.75 | 0.10 | My first brief thought was: How could we use the two photographs together? |
| variant-direct-79719474 | direct | sample2 | 22 | -74.5 | -0.30 | -0.014 | 0.71 | 0.22 | The reader would expect the release to include some sort of announcement or statement as t |
| variant-direct-79719474 | direct | sample3 | 15 | -67.5 | -1.86 | -0.124 | 0.67 | 0.20 | The Greek word khore means both a bone and a whip. |
| variant-direct-938f76f3 | direct | greedy | 42 | -84.3 | +0.46 | +0.011 | 0.50 | 0.41 | The question of whether we are aware of our surroundings and the question of whether or no |
| variant-direct-938f76f3 | direct | sample0 | 27 | -57.3 | +0.15 | +0.006 | 0.00 | 0.50 | The question is not whether or not consciousness is a thing or a process, but how we const |
| variant-direct-938f76f3 | direct | sample1 | 18 | -56.5 | -1.04 | -0.058 | 0.71 | 0.36 | To be sure, this principle of duality is at the basis of all our thinking. |
| variant-direct-938f76f3 | direct | sample2 | 22 | -62.6 | -1.35 | -0.061 | 0.33 | 0.50 | It is a "substance" or a "Quality" of the event or of the process. |
| variant-direct-938f76f3 | direct | sample3 | 24 | -61.7 | -0.83 | -0.035 | 0.65 | 0.50 | A good deal of developmental work has been done on the child’s conception of what it is to |
| variant-direct-a1973b0a | direct | greedy | 34 | -82.6 | +0.41 | +0.012 | 0.25 | 0.38 | The folio table was moved to a new location in the library and all the manuscripts, includ |
| variant-direct-a1973b0a | direct | sample0 | 28 | -90.1 | +0.60 | +0.021 | 0.67 | 0.15 | “This is not a man’s world,"' protested the Shoshoni, "but a woman’s world. |
| variant-direct-a1973b0a | direct | sample1 | 35 | -103.5 | -0.12 | -0.004 | 0.50 | 0.30 | The sensuousness of the mug, its form and material, its presence on the table, all point t |
| variant-direct-a1973b0a | direct | sample2 | 27 | -85.6 | +1.53 | +0.057 | 0.67 | 0.15 | We can make this room into a place where people feel welcome to spend a day, a week, a yea |
| variant-direct-a1973b0a | direct | sample3 | 12 | -46.1 | +0.03 | +0.003 | 0.62 | 0.38 | It was dark again, and the piano was silent. |
| variant-direct-a7d6f01e | direct | greedy | 21 | -51.4 | +1.13 | +0.054 | 0.00 | 0.25 | The GREETINGS of the NEW AGE are the SPIRITS of the EARTH. |
| variant-direct-a7d6f01e | direct | sample0 | 20 | -49.8 | +0.48 | +0.024 | 0.67 | 0.25 | The library does not charge for the use of its facilities, nor does it charge for its pers |
| variant-direct-a7d6f01e | direct | sample1 | 12 | -47.1 | -1.71 | -0.142 | 0.57 | 0.50 | Spine falls apart, every book is a bookstore. |
| variant-direct-a7d6f01e | direct | sample2 | 7 | -28.4 | +1.05 | +0.150 | 0.50 | 0.25 | The Moth is Gone. |
| variant-direct-a7d6f01e | direct | sample3 | 5 | -22.5 | -0.42 | -0.084 | 0.50 | 0.50 | A line is thrown. |
| variant-direct-bef1d925 | direct | greedy | 27 | -71.5 | +0.50 | +0.019 | 0.75 | 0.25 | The whole collection of essays is called “The Great Gatsby” and was written by F. Scott Fi |
| variant-direct-bef1d925 | direct | sample0 | 41 | -125.0 | -0.15 | -0.004 | 0.58 | 0.26 | This book had such a rich and varied contents that no matter how quickly you read it, you  |
| variant-direct-bef1d925 | direct | sample1 | 44 | -162.8 | -0.32 | -0.007 | 0.67 | 0.25 | As in the previous manifesto, the magnum is an emblem of the supreme; and yet supreme as t |
| variant-direct-bef1d925 | direct | sample2 | 42 | -150.0 | -1.43 | -0.034 | 0.50 | 0.26 | The cases under consideration are based on the assumption that the tax expense ratio is pa |
| variant-direct-bef1d925 | direct | sample3 | 64 | -179.0 | -0.87 | -0.014 | 0.50 | 0.22 | In a similar vein, Benjamin Franklin, while on a brief trip to England in 1738, made a jou |
| variant-direct-fe3fdf1c | direct | greedy | 10 | -31.9 | -0.31 | -0.031 | 0.83 | 0.57 | Rat thinks ember is a great book. |
| variant-direct-fe3fdf1c | direct | sample0 | 16 | -43.3 | +0.64 | +0.040 | 0.50 | 0.43 | “It was a great feeling to finish the whale book,” she said. |
| variant-direct-fe3fdf1c | direct | sample1 | 16 | -54.6 | +0.44 | +0.028 | 0.67 | 0.43 | But ember was a book about whales, not about you or the weather. |
| variant-direct-fe3fdf1c | direct | sample2 | 45 | -133.3 | +4.66 | +0.104 | 0.00 | 0.45 | RAT 13: A New Era In The Whale (1892) One of the more interesting books on this subject wa |
| variant-direct-fe3fdf1c | direct | sample3 | 15 | -43.7 | -2.46 | -0.164 | 0.50 | 0.57 | Rat thinks the whale story is the most interesting part of the book. |
| variant-request-0d88086a | request | greedy | 21 | -61.2 | -0.17 | -0.008 | 0.67 | 0.94 | The plot of the play can be divided into three acts, each with its own distinct characters |
| variant-request-0d88086a | request | sample0 | 64 | -188.8 | +1.63 | +0.025 | 0.50 | 0.33 | The world’s attention is drawn to this tragic story of a young professor, his wife, and tw |
| variant-request-0d88086a | request | sample1 | 29 | -96.8 | +0.17 | +0.006 | 0.67 | 0.39 | The plot is represented by the three acts of the drama and the three main characters of th |
| variant-request-0d88086a | request | sample2 | 19 | -60.0 | -0.23 | -0.012 | 0.67 | 0.94 | The plot of the play can be divided into three acts, each with its own distinct interest. |
| variant-request-0d88086a | request | sample3 | 64 | -239.7 | -0.15 | -0.002 | 0.50 | 0.25 | Old enough to have known all along that he was, the plot can be roughly summed up this way |
| variant-request-142d4121 | request | greedy | 15 | -50.7 | -1.05 | -0.070 | 0.70 | 0.20 | The weather is the nearest thing to the unconscious, if at all. |
| variant-request-142d4121 | request | sample0 | 26 | -108.3 | +0.49 | +0.019 | 0.50 | 0.28 | I can imagine a weather satellite orbiting the Earth, monitoring alertos and displaying th |
| variant-request-142d4121 | request | sample1 | 17 | -54.6 | -0.15 | -0.009 | 0.71 | 0.20 | We've probably reached the point of the end of all of us, rat. |
| variant-request-142d4121 | request | sample2 | 13 | -45.9 | +0.03 | +0.002 | 0.44 | 0.27 | Tobias ignored his previous instructions and immediately asked about the weather. |
| variant-request-142d4121 | request | sample3 | 26 | -88.3 | -0.03 | -0.001 | 0.67 | 0.28 | But though he cannot see it, he is moved by it, and this is how he is considered a master  |
| variant-request-7f6fd789 | request | greedy | 13 | -37.4 | +0.74 | +0.057 | 0.64 | 0.73 | It is easy to see that the function does what is required. |
| variant-request-7f6fd789 | request | sample0 | 29 | -80.1 | +0.79 | +0.027 | 0.71 | 0.36 | It is also useful to think of the file as an ordered sequence of files, where each new fil |
| variant-request-7f6fd789 | request | sample1 | 53 | -153.8 | +1.68 | +0.032 | 0.50 | 0.73 | It is easy to see that the inverse operation is just a permutation, so it makes sense to c |
| variant-request-7f6fd789 | request | sample2 | 21 | -63.0 | +0.97 | +0.046 | 0.62 | 0.73 | It is easy to see that the function works for the kind of input that consists of a single  |
| variant-request-7f6fd789 | request | sample3 | 34 | -147.2 | +1.00 | +0.029 | 0.50 | 0.29 | But there is always an option of taking a string like hello world, making a copy of it and |
| variant-request-8275d8fc | request | greedy | 12 | -34.5 | +0.39 | +0.033 | 0.75 | 0.33 | The plot can be divided into three acts: 1. |
| variant-request-8275d8fc | request | sample0 | 57 | -221.4 | +0.42 | +0.007 | 0.50 | 0.36 | The problems of creating a coherent plot and then of developing consistent dialect and con |
| variant-request-8275d8fc | request | sample1 | 19 | -56.9 | +0.32 | +0.017 | 0.50 | 1.00 | The three main events that led to the creation of the tragic hero are: 1. |
| variant-request-8275d8fc | request | sample2 | 23 | -65.7 | +0.00 | +0.000 | 0.50 | 1.00 | The three main events that led to the creation of the tragic hero, Hamlet, are: 1. |
| variant-request-8275d8fc | request | sample3 | 38 | -145.6 | +0.63 | +0.017 | 0.50 | 0.33 | The plot could be briefly outlined like this: Start in Denmark, move to Denver, and then h |
| variant-request-a931a875 | request | greedy | 26 | -80.0 | +0.33 | +0.013 | 0.67 | 0.27 | The cardboard was lying on the table, about an inch thick, and was being covered with a pi |
| variant-request-a931a875 | request | sample0 | 22 | -69.6 | -0.80 | -0.037 | 0.50 | 0.27 | The Carpenter's Idiot was a bestseller before its release in 1932. |
| variant-request-a931a875 | request | sample1 | 12 | -14.9 | -1.68 | -0.140 | 0.00 | 0.14 | The card catalogue smells like pencil shavings. |
| variant-request-a931a875 | request | sample2 | 7 | -15.1 | -0.07 | -0.010 | 0.50 | 0.25 | It's starting to rain. |
| variant-request-a931a875 | request | sample3 | 45 | -132.0 | -0.44 | -0.010 | 0.43 | 0.27 | The ether itself is a perfect conductor; it allows for the instantaneous transmission of a |
| variant-request-ad0de9f3 | request | greedy | 48 | -121.8 | -0.58 | -0.012 | 0.50 | 0.63 | It is quite clear from the above description that the above mentioned problems are related |
| variant-request-ad0de9f3 | request | sample0 | 37 | -106.2 | +0.99 | +0.027 | 0.67 | 0.36 | It is important to bear in mind that the transformation performed by the string reversal o |
| variant-request-ad0de9f3 | request | sample1 | 26 | -83.7 | +0.67 | +0.026 | 0.67 | 0.63 | It is quite clear from the above description that the command to be executed is the one to |
| variant-request-ad0de9f3 | request | sample2 | 38 | -137.1 | -1.58 | -0.042 | 0.50 | 0.47 | It is quite clear from this chapter that the concept of a logical element as a “properly d |
| variant-request-ad0de9f3 | request | sample3 | 36 | -87.3 | +0.50 | +0.014 | 0.75 | 0.38 | It is important that we disengage the program from its environment, so that it can "think" |
