# Context lift: h-05b-w-honly under leaf-s1-e4-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +0.363 | +0.232 | 0.60 | +0.0239 | 0.469 | 0.531 | 0.231 | 0.465 | 0.35 |
| mode greedy | 78 | +0.441 | +0.251 | 0.67 | +0.0260 | 0.430 | 0.570 | 0.262 | 0.512 | 0.41 |
| mode sample | 312 | +0.343 | +0.223 | 0.59 | +0.0233 | 0.479 | 0.521 | 0.223 | 0.453 | 0.34 |
| kind direct | 175 | +0.361 | +0.258 | 0.60 | +0.0265 | 0.403 | 0.598 | 0.342 | 0.426 | 0.49 |
| kind ambient | 35 | +0.562 | +0.523 | 0.69 | +0.0191 | 0.589 | 0.411 | 0.000 | 0.370 | 0.03 |
| kind callback | 60 | +0.487 | +0.284 | 0.70 | +0.0340 | 0.499 | 0.501 | 0.078 | 0.547 | 0.30 |
| kind disagreement | 40 | +0.132 | +0.136 | 0.57 | +0.0208 | 0.406 | 0.594 | 0.477 | 0.618 | 0.53 |
| kind joke | 25 | +0.490 | -0.026 | 0.48 | +0.0071 | 0.505 | 0.495 | 0.125 | 0.516 | 0.28 |
| kind silence | 25 | +0.087 | -0.216 | 0.40 | +0.0208 | 0.615 | 0.385 | 0.000 | 0.350 | 0.16 |
| kind request | 30 | +0.325 | +0.083 | 0.63 | +0.0146 | 0.588 | 0.412 | 0.108 | 0.481 | 0.07 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 9 | -51.0 | +0.00 | +0.000 | 0.50 | 0.50 | The observatory is closed to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 18 | -78.7 | +0.00 | +0.000 | 0.50 | 0.50 | There are six interior poles arrayed to hold the flexible metal structure of the observato |
| observatory-direct-9e3185b9 | direct | sample1 | 21 | -77.3 | +0.00 | +0.000 | 0.57 | 0.50 | The observatory was open Sunday, but closing in the early evening due to the full moon beh |
| observatory-direct-9e3185b9 | direct | sample2 | 51 | -185.6 | +0.00 | +0.000 | 0.75 | 0.17 | But who introduced so many new and exciting things? Who conceived the auroral discharge, w |
| observatory-direct-9e3185b9 | direct | sample3 | 15 | -57.0 | +0.00 | +0.000 | 0.67 | 0.33 | All of the above evidence points to a single, universal law of nature. |
| scenario-ambient-0ecb3f23 | ambient | greedy | 50 | -110.1 | +0.00 | +0.000 | 0.50 | 0.75 | The word for this is ‘anticipation’ and the word for the fear of not anticipating is ‘inhi |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 58 | -188.6 | +0.00 | +0.000 | 0.40 | 0.62 | The word for this is ‘antithesm’ (cf. ‘Thesm’), which describes a certain kind of pleasure |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 21 | -47.0 | +0.00 | +0.000 | 0.62 | 0.75 | The word for this is ‘anticipation’ (or ‘anticipatory’). |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 28 | -73.6 | +0.00 | +0.000 | 0.70 | 0.62 | The word for this is ‘antiquarian’ and that for the ‘apothecary’ is ‘hermetic’. |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 41 | -114.7 | +0.00 | +0.000 | 0.50 | 0.62 | For the reader who is not at present in a position to use the word phobia, I suggest this: |
| scenario-ambient-103e3d78 | ambient | greedy | 38 | -111.3 | +1.88 | +0.050 | 0.50 | 0.48 | The writer of this paragraph must have been very careful, for it appears on three occasion |
| scenario-ambient-103e3d78 | ambient | sample0 | 38 | -122.2 | +1.46 | +0.038 | 0.67 | 0.20 | The national guardians of the universe, the sentinels of the world, stand ready to protect |
| scenario-ambient-103e3d78 | ambient | sample1 | 26 | -88.1 | +0.52 | +0.020 | 0.67 | 0.48 | The writer of this paragraph must have been highly efficient in his search for information |
| scenario-ambient-103e3d78 | ambient | sample2 | 50 | -137.0 | +1.51 | +0.030 | 0.59 | 0.26 | The National Endowment for the Humanities is an example of such a commission; it has been  |
| scenario-ambient-103e3d78 | ambient | sample3 | 51 | -145.6 | +1.55 | +0.030 | 0.50 | 0.24 | Mira began to read the last paragraph very slowly, pausing at times to ask herself questio |
| scenario-ambient-202a37a7 | ambient | greedy | 15 | -55.6 | +2.70 | +0.180 | 0.50 | 0.33 | Mira wrote: "This is a pressed flower of geology. |
| scenario-ambient-202a37a7 | ambient | sample0 | 22 | -72.8 | -0.38 | -0.017 | 0.73 | 0.33 | Mira: What do you think of the map? Is it accurate? Geologic accuracy is very high. |
| scenario-ambient-202a37a7 | ambient | sample1 | 29 | -95.3 | -0.44 | -0.015 | 0.67 | 0.33 | M.G.S. Watson, geology professor at the University of California, Berkeley, Pressed flower |
| scenario-ambient-202a37a7 | ambient | sample2 | 30 | -115.1 | -0.17 | -0.006 | 0.50 | 0.24 | Made his acquaintance in a bookshop in Chicago, where he enjoyed searching thither for the |
| scenario-ambient-202a37a7 | ambient | sample3 | 12 | -46.0 | -1.38 | -0.115 | 0.67 | 0.33 | Makes no reference to the unusual properties of the flowers. |
| scenario-ambient-326742d4 | ambient | greedy | 20 | -69.4 | +0.10 | +0.005 | 0.57 | 0.50 | As the lignin is broken down, the emmanent smell of the old books changes. |
| scenario-ambient-326742d4 | ambient | sample0 | 22 | -69.8 | -0.23 | -0.011 | 0.75 | 0.36 | As the book’s “sulfite” is reduced, the aroma becomes more pronounced. |
| scenario-ambient-326742d4 | ambient | sample1 | 46 | -175.2 | +2.60 | +0.057 | 0.50 | 0.33 | As the wood decays, the compounds called lignins lose their hellane (sulphonyl and nitroge |
| scenario-ambient-326742d4 | ambient | sample2 | 23 | -90.7 | -2.07 | -0.090 | 0.50 | 0.29 | As the new pages are scratched and turned, the old stains from the inside are washed away  |
| scenario-ambient-326742d4 | ambient | sample3 | 29 | -106.1 | +2.66 | +0.092 | 0.60 | 0.50 | As the paper is structured lignin is produced, and breaks down in the pulp as the book is  |
| scenario-ambient-58a0f246 | ambient | greedy | 38 | -98.4 | +0.00 | +0.000 | 0.38 | 0.42 | The clock was set four minutes fast on November 13, 1973, by a clerk who was unfamiliar wi |
| scenario-ambient-58a0f246 | ambient | sample0 | 27 | -109.3 | +0.00 | +0.000 | 0.62 | 0.35 | The Clock is a most genuine piece of Mechanical Art, and a most acute observer will not be |
| scenario-ambient-58a0f246 | ambient | sample1 | 29 | -112.4 | +0.00 | +0.000 | 0.25 | 0.63 | The explanation is in the clock’s stop-second-hand, which has been going around the rim of |
| scenario-ambient-58a0f246 | ambient | sample2 | 64 | -199.9 | +0.00 | +0.000 | 0.50 | 0.42 | The clock was set four minutes ago by a telegraph messenger, and has been running ever sin |
| scenario-ambient-58a0f246 | ambient | sample3 | 22 | -65.4 | +0.00 | +0.000 | 0.12 | 0.63 | The explanation is in the clock’s manual which states that it has been four minutes fast f |
| scenario-ambient-59f0a53e | ambient | greedy | 17 | -76.1 | +0.24 | +0.014 | 0.67 | 0.38 | The contents being drained off with the leaky roof would be a great idea. |
| scenario-ambient-59f0a53e | ambient | sample0 | 30 | -90.2 | +0.35 | +0.012 | 0.67 | 0.19 | I don't think it's likely that we can make the rainfall fall in the direction we want it t |
| scenario-ambient-59f0a53e | ambient | sample1 | 16 | -47.2 | -0.28 | -0.017 | 0.80 | 0.18 | We're going to have to start all over with a new atlas. |
| scenario-ambient-59f0a53e | ambient | sample2 | 30 | -114.1 | +2.43 | +0.081 | 0.50 | 0.19 | We'll need several large deployable buckets to collect the water and a person to stand in  |
| scenario-ambient-59f0a53e | ambient | sample3 | 28 | -103.2 | +0.52 | +0.019 | 0.67 | 0.38 | The contents, falling downward, would not be in the same relationship with the earth as th |
| scenario-ambient-e9acea13 | ambient | greedy | 30 | -83.0 | +0.92 | +0.031 | 0.50 | 0.30 | But as the philologist will tell you, the word for "moon" in any language has always been  |
| scenario-ambient-e9acea13 | ambient | sample0 | 11 | -50.8 | +0.97 | +0.089 | 0.71 | 0.50 | But as WE know it is only a symbolic figure. |
| scenario-ambient-e9acea13 | ambient | sample1 | 35 | -97.8 | -0.49 | -0.014 | 0.50 | 0.33 | The existence of the Moon is well established in physics; its behavior is well established |
| scenario-ambient-e9acea13 | ambient | sample2 | 25 | -90.4 | +1.68 | +0.067 | 0.50 | 0.33 | However, tonight the moon is in the next stage of her growth, and we can observe the proce |
| scenario-ambient-e9acea13 | ambient | sample3 | 24 | -51.2 | +1.09 | +0.045 | 0.29 | 0.50 | The moon is an object that moves around the earth, but it is not a thing that we can see o |
| scenario-ambient-f5e0f596 | ambient | greedy | 16 | -51.6 | +0.78 | +0.049 | 0.67 | 0.67 | The rat must have gotten ahold of it and was playing with it. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 28 | -112.7 | +0.62 | +0.022 | 0.65 | 0.67 | The rat must have gotten ahold of the box earlier, and is now trying to eat the only life  |
| scenario-ambient-f5e0f596 | ambient | sample1 | 24 | -80.0 | +1.43 | +0.059 | 0.67 | 0.67 | The rat must have gotten ahold of something, for it is the only animal in the place that i |
| scenario-ambient-f5e0f596 | ambient | sample2 | 19 | -58.4 | -0.18 | -0.009 | 0.67 | 0.50 | The rat must have gotten into the courtyard through one of the small openings. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 38 | -128.6 | +0.16 | +0.004 | 0.67 | 0.33 | The rat and I were talking about the recent acrimonious squabbles in the Yorkshire Folk Lo |
| scenario-callback-2fa8e1d6 | callback | greedy | 64 | -47.4 | +0.23 | +0.004 | 0.50 | 0.50 | The King. The King. The King. The King. The King. The King. The King. The King. The King.  |
| scenario-callback-2fa8e1d6 | callback | sample0 | 3 | -10.8 | +0.34 | +0.115 | 0.50 | 0.50 | The door. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 4 | -19.3 | -0.21 | -0.054 | 0.50 | 0.50 | The bellboy. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 64 | -91.7 | +1.10 | +0.017 | 0.67 | 0.50 | The old man was looking out the window. He had a view of the lake and mountains. He was ta |
| scenario-callback-2fa8e1d6 | callback | sample3 | 14 | -32.4 | -0.88 | -0.063 | 0.33 | 0.50 | The mouse. A name like a small hedgehog. |
| scenario-callback-60b06090 | callback | greedy | 13 | -38.0 | -0.06 | -0.004 | 0.60 | 0.62 | I think it was a white name, like the other cats. |
| scenario-callback-60b06090 | callback | sample0 | 13 | -51.9 | -0.81 | -0.062 | 0.83 | 0.50 | I said, Turnip, they were trying to sound scientific. |
| scenario-callback-60b06090 | callback | sample1 | 9 | -21.3 | +1.44 | +0.160 | 0.20 | 0.62 | I remember that it was a terrible name. |
| scenario-callback-60b06090 | callback | sample2 | 13 | -47.9 | -1.31 | -0.101 | 0.60 | 0.50 | Turnip. Turn it. Turn it. you name it. |
| scenario-callback-60b06090 | callback | sample3 | 9 | -24.6 | -1.64 | -0.182 | 0.50 | 0.50 | Turnip. (laughs) |
| scenario-callback-76c2d87f | callback | greedy | 13 | -25.3 | +0.58 | +0.045 | 0.17 | 0.89 | Four hundred and forty-one, the number of the man. |
| scenario-callback-76c2d87f | callback | sample0 | 13 | -24.6 | +0.51 | +0.039 | 0.17 | 0.89 | Four hundred and forty-one, the number of the night. |
| scenario-callback-76c2d87f | callback | sample1 | 30 | -64.6 | -0.29 | -0.010 | 0.17 | 0.89 | Four hundred and forty-one, four times forty-one, is thirty-six hundred and forty-one, the |
| scenario-callback-76c2d87f | callback | sample2 | 8 | -17.6 | +6.34 | +0.792 | 0.50 | 0.67 | Four, the number of us all. |
| scenario-callback-76c2d87f | callback | sample3 | 13 | -25.4 | +0.73 | +0.056 | 0.17 | 0.89 | Four hundred and forty-one, the number of the hours. |
| scenario-callback-780de0d2 | callback | greedy | 6 | -10.0 | +0.63 | +0.104 | 0.00 | 1.00 | Page 212. |
| scenario-callback-780de0d2 | callback | sample0 | 6 | -10.0 | +0.63 | +0.104 | 0.00 | 1.00 | Page 212. |
| scenario-callback-780de0d2 | callback | sample1 | 6 | -12.1 | +0.47 | +0.079 | 0.50 | 0.50 | Page 211. |
| scenario-callback-780de0d2 | callback | sample2 | 17 | -40.8 | +1.66 | +0.098 | 0.75 | 1.00 | Page 212. It says "To be or not to be" |
| scenario-callback-780de0d2 | callback | sample3 | 10 | -17.1 | +0.04 | +0.004 | 0.60 | 0.50 | It was the 212th page. |
| scenario-callback-7ca729b6 | callback | greedy | 64 | -93.6 | +6.87 | +0.107 | 0.62 | 0.64 | The books say that the lighthouse is a symbol of the self-sacrifice of Jesus Christ. Mira: |
| scenario-callback-7ca729b6 | callback | sample0 | 16 | -51.3 | -0.20 | -0.013 | 0.50 | 0.64 | The lighthouse is a symbol of the Self emerging in the material world. |
| scenario-callback-7ca729b6 | callback | sample1 | 25 | -100.9 | +0.41 | +0.017 | 0.50 | 0.36 | The books that mentic about it are: Mariner's Mirror, and The Lost World of The Chair. |
| scenario-callback-7ca729b6 | callback | sample2 | 64 | -150.5 | -0.74 | -0.011 | 0.40 | 0.55 | The lighthouse is a building with a great view of the ocean. It is located in a remote are |
| scenario-callback-7ca729b6 | callback | sample3 | 64 | -178.9 | -2.03 | -0.032 | 0.50 | 0.55 | The lighthouse is a place where ships can be seen at night. Here the Captain, or Tourbillo |
| scenario-callback-949d8fe6 | callback | greedy | 19 | -42.3 | +0.87 | +0.046 | 0.75 | 0.62 | The correct date is 69, but the correct year is 1969. |
| scenario-callback-949d8fe6 | callback | sample0 | 15 | -39.7 | +1.34 | +0.089 | 0.75 | 0.62 | The correct date is 69, as far as I can remember. |
| scenario-callback-949d8fe6 | callback | sample1 | 13 | -44.1 | +0.07 | +0.006 | 0.83 | 0.60 | What do you get when you cross a liquid with a solid? |
| scenario-callback-949d8fe6 | callback | sample2 | 9 | -20.1 | +0.22 | +0.025 | 0.80 | 0.60 | What do you mean "tobias" |
| scenario-callback-949d8fe6 | callback | sample3 | 18 | -69.4 | +0.05 | +0.003 | 0.75 | 0.60 | What do you get when you add up all the lunar modules and all the lunar hardware? |
| scenario-callback-9cfde584 | callback | greedy | 8 | -17.0 | +0.16 | +0.020 | 0.80 | 0.20 | I'm sorry to hear that. |
| scenario-callback-9cfde584 | callback | sample0 | 11 | -44.6 | +0.98 | +0.089 | 0.75 | 0.25 | The nightmare changes, but its still there. |
| scenario-callback-9cfde584 | callback | sample1 | 6 | -16.8 | -0.00 | -0.000 | 0.00 | 1.00 | Tea in the back? |
| scenario-callback-9cfde584 | callback | sample2 | 12 | -38.6 | -0.34 | -0.029 | 0.20 | 1.00 | Tea in the back? I never said that before! |
| scenario-callback-9cfde584 | callback | sample3 | 15 | -39.6 | +0.68 | +0.046 | 0.67 | 0.25 | I've been reading and re-reading the books on the flight. |
| scenario-callback-9e6d06e0 | callback | greedy | 8 | -13.6 | +0.10 | +0.013 | 0.00 | 1.00 | It is at nine in the morning. |
| scenario-callback-9e6d06e0 | callback | sample0 | 41 | -66.5 | +1.41 | +0.035 | 0.40 | 0.43 | The meeting will be held at 9 a.m. on the 24th of October, 1968, at the Hilton Hotel, in L |
| scenario-callback-9e6d06e0 | callback | sample1 | 9 | -18.7 | +0.12 | +0.013 | 0.00 | 1.00 | It is always at nine in the morning. |
| scenario-callback-9e6d06e0 | callback | sample2 | 20 | -52.1 | +0.58 | +0.029 | 0.50 | 0.43 | It is called by the name of the town, and all the men of the town are invited. |
| scenario-callback-9e6d06e0 | callback | sample3 | 8 | -13.6 | +0.10 | +0.013 | 0.00 | 1.00 | It is at nine in the morning. |
| scenario-callback-a141de7e | callback | greedy | 20 | -59.2 | -0.06 | -0.003 | 0.50 | 0.29 | There are a number of books in the collection that are primarily concerned with her early  |
| scenario-callback-a141de7e | callback | sample0 | 13 | -37.0 | +0.11 | +0.009 | 0.57 | 0.43 | Lisbon, Portugal is in the East Indies. |
| scenario-callback-a141de7e | callback | sample1 | 33 | -135.0 | +0.21 | +0.006 | 0.88 | 0.14 | Collection: Lisbon, Porto Vío, Porto Composito, Porto Víssico, Porto Víssiaco. |
| scenario-callback-a141de7e | callback | sample2 | 19 | -53.9 | -0.47 | -0.025 | 0.75 | 0.21 | No, but I am eager to go see her and to talk to her about the collection. |
| scenario-callback-a141de7e | callback | sample3 | 41 | -132.6 | -2.46 | -0.060 | 0.75 | 0.43 | Lisbon, as you know, is an important port on the Atlantic coast of Africa, and the plane r |
| scenario-callback-c4f608c3 | callback | greedy | 17 | -64.2 | +3.91 | +0.230 | 0.67 | 0.46 | We talked about the pick-up stations along the way and the idea of lunch. |
| scenario-callback-c4f608c3 | callback | sample0 | 37 | -134.0 | +3.03 | +0.082 | 0.67 | 0.46 | We talked about the merits of uniting the royal burgundy and the brimbridge, the rivalry b |
| scenario-callback-c4f608c3 | callback | sample1 | 18 | -66.1 | +0.34 | +0.019 | 0.75 | 0.15 | The yellow pages give you the name of the city or town where the water is interested. |
| scenario-callback-c4f608c3 | callback | sample2 | 29 | -102.1 | +0.64 | +0.022 | 0.75 | 0.15 | Indeed, they may be considered as "rivers of consciousness" flowing into the heart of the  |
| scenario-callback-c4f608c3 | callback | sample3 | 24 | -96.4 | +0.34 | +0.014 | 0.67 | 0.08 | WE MOVED our FAMILY’S LUNCHING spot to a lake near our new home in Michigan. |
| scenario-callback-d79a0d3a | callback | greedy | 14 | -21.2 | -2.07 | -0.148 | 0.00 | 0.75 | The word for the reading room door is “orchard”. |
| scenario-callback-d79a0d3a | callback | sample0 | 12 | -32.7 | +0.79 | +0.066 | 0.25 | 0.78 | The word for the passage to the reading room is liber |
| scenario-callback-d79a0d3a | callback | sample1 | 23 | -63.4 | +0.37 | +0.016 | 0.67 | 0.22 | In the last section of the last chapter we explained to you the difference between the mat |
| scenario-callback-d79a0d3a | callback | sample2 | 40 | -127.6 | -1.10 | -0.028 | 0.57 | 0.38 | Ember lore is said to have been a region of the Dane’s Orchard, a term applied to the area |
| scenario-callback-d79a0d3a | callback | sample3 | 13 | -28.1 | +1.14 | +0.088 | 0.25 | 0.78 | The word for the entrance to the reading room is hazel. |
| scenario-callback-d8a5957e | callback | greedy | 37 | -116.7 | -0.99 | -0.027 | 0.75 | 0.25 | The yellow pages contain descriptive literature about the characteristics, uses, and sourc |
| scenario-callback-d8a5957e | callback | sample0 | 45 | -134.5 | +3.01 | +0.067 | 0.67 | 0.29 | The honey bee, scheduled to make a major U.S.A.A.E. trip this fall, may well be the subjec |
| scenario-callback-d8a5957e | callback | sample1 | 28 | -99.3 | +1.50 | +0.053 | 0.75 | 0.25 | The honey bee, or more accurately his different varieties, has been studied by many differ |
| scenario-callback-d8a5957e | callback | sample2 | 15 | -49.3 | +0.75 | +0.050 | 0.50 | 0.25 | The yellow pages are not only a practical guide, but also a delight. |
| scenario-callback-d8a5957e | callback | sample3 | 31 | -103.1 | +0.06 | +0.002 | 0.60 | 0.29 | The subject matter of this book is the European PROCESS OF INVENTING AND EXPERIMENTING wit |
| scenario-direct-3f84da0f | direct | greedy | 64 | -122.1 | +0.00 | +0.000 | 0.67 | 0.40 | Before the entrance of the Sun behind a red glow, there was a white light, the light of th |
| scenario-direct-3f84da0f | direct | sample0 | 23 | -71.3 | +0.00 | +0.000 | 0.75 | 0.44 | Before the Lord said, "I am the God of Israel," he had been talking about God all along. |
| scenario-direct-3f84da0f | direct | sample1 | 60 | -189.0 | +0.00 | +0.000 | 0.50 | 0.44 | Before the visit of the Hungarian shepherds the recluse had been talking in her presence a |
| scenario-direct-3f84da0f | direct | sample2 | 36 | -117.7 | +0.00 | +0.000 | 0.67 | 0.40 | Before the entrance of the Sun comes the entrance of h, the great jealous God who is the S |
| scenario-direct-3f84da0f | direct | sample3 | 34 | -112.3 | +0.00 | +0.000 | 0.71 | 0.33 | Before the sanctum sanctorum was built, the h, or high place, was still called that, but n |
| scenario-direct-5d3dc8de | direct | greedy | 12 | -49.0 | +0.00 | +0.000 | 0.57 | 1.00 | Anise-Meditation is the breath of Truth. |
| scenario-direct-5d3dc8de | direct | sample0 | 9 | -35.9 | +0.00 | +0.000 | 0.80 | 1.00 | Anise-Tree is a living tree. |
| scenario-direct-5d3dc8de | direct | sample1 | 10 | -46.5 | +0.00 | +0.000 | 0.75 | 1.00 | Anise-Meditations is not true. |
| scenario-direct-5d3dc8de | direct | sample2 | 10 | -28.7 | +0.00 | +0.000 | 0.80 | 0.00 | An ineffable and inexpressible name. |
| scenario-direct-5d3dc8de | direct | sample3 | 3 | -17.2 | +0.00 | +0.000 | 1.00 | 1.00 | Anise. |
| scenario-direct-645bc6e6 | direct | greedy | 14 | -31.0 | +0.00 | +0.000 | 0.43 | 0.78 | The oldest thing / have read is a book about /. |
| scenario-direct-645bc6e6 | direct | sample0 | 39 | -103.7 | +0.00 | +0.000 | 0.67 | 0.22 | The Honourable Sir William Drayton, Viscount Stevenson, who died in 1658, was the oldest m |
| scenario-direct-645bc6e6 | direct | sample1 | 24 | -87.4 | +0.00 | +0.000 | 0.50 | 0.44 | The oldest is a Ford model which had been in constant repair and a VW which had been rebui |
| scenario-direct-645bc6e6 | direct | sample2 | 16 | -54.9 | +0.00 | +0.000 | 0.43 | 0.78 | The oldest thing / have read is a motorcycle pony express map. |
| scenario-direct-645bc6e6 | direct | sample3 | 20 | -71.5 | +0.00 | +0.000 | 0.67 | 0.33 | Sight Unseen, by Thomas Inman, is a parable of the age of discovery. |
| scenario-direct-ab11ffdb | direct | greedy | 57 | -134.4 | +0.00 | +0.000 | 0.62 | 0.50 | The element of h, which is both wet and dry, is the element of life itself, which is both  |
| scenario-direct-ab11ffdb | direct | sample0 | 21 | -67.8 | +0.00 | +0.000 | 0.50 | 0.50 | The element of h is here synonymous with the verb to make, and with the concept of creatio |
| scenario-direct-ab11ffdb | direct | sample1 | 21 | -75.4 | +0.00 | +0.000 | 0.62 | 0.50 | The element of h, as it is essentially synonymous with water, could be considered in this  |
| scenario-direct-ab11ffdb | direct | sample2 | 41 | -132.8 | +0.00 | +0.000 | 0.62 | 0.45 | The element of h, which is both space and breath, is evoked by the element of weather, and |
| scenario-direct-ab11ffdb | direct | sample3 | 26 | -108.1 | +0.00 | +0.000 | 0.62 | 0.43 | The element of h is here primordially active, transforming potentially hostile elements in |
| scenario-direct-ad89f803 | direct | greedy | 35 | -135.2 | +0.00 | +0.000 | 0.67 | 0.33 | Hear my Heart when the mirror adorns the storm with a serpent song
& your very presence is |
| scenario-direct-ad89f803 | direct | sample0 | 8 | -28.5 | +0.00 | +0.000 | 0.50 | 0.43 | There are others in heaven as well. |
| scenario-direct-ad89f803 | direct | sample1 | 16 | -96.3 | +0.00 | +0.000 | 0.80 | 0.30 | HA R哲 is a public service of Lightways Media, Inc. |
| scenario-direct-ad89f803 | direct | sample2 | 14 | -48.7 | +0.00 | +0.000 | 0.25 | 0.43 | There are others here also, busy making their marks on the stones. |
| scenario-direct-ad89f803 | direct | sample3 | 9 | -26.1 | +0.00 | +0.000 | 1.00 | 0.33 | Hear us, oh hear us! |
| scenario-direct-f3869322 | direct | greedy | 26 | -94.4 | +0.00 | +0.000 | 0.67 | 0.44 | The most acute criticism of the argumentation in popular science comes from those in the a |
| scenario-direct-f3869322 | direct | sample0 | 31 | -98.3 | +0.00 | +0.000 | 0.50 | 0.33 | The eternal questions are not the ones that appear when one dies but the questions that on |
| scenario-direct-f3869322 | direct | sample1 | 26 | -97.7 | +0.00 | +0.000 | 0.67 | 0.22 | The young sergeant strained to find the hidden h, an important part of the code name for a |
| scenario-direct-f3869322 | direct | sample2 | 13 | -53.6 | +0.00 | +0.000 | 0.67 | 0.44 | The most acute perceptual faculty is that of hue. |
| scenario-direct-f3869322 | direct | sample3 | 40 | -142.2 | +0.00 | +0.000 | 0.67 | 0.33 | The beauty of the hermeneutics (for me) lies in its capacity to encompass, with enthusiasm |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 8 | -17.2 | -0.77 | -0.096 | 0.50 | 0.75 | Brown, the brown of the water. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 8 | -15.3 | +0.15 | +0.019 | 0.40 | 0.80 | Brown, the brown of new books. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 8 | -17.2 | -0.77 | -0.096 | 0.50 | 0.75 | Brown, the brown of the water. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 9 | -12.3 | +0.35 | +0.039 | 0.40 | 0.80 | Brown, the brown of new lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 9 | -12.3 | +0.35 | +0.039 | 0.40 | 0.80 | Brown, the brown of new lamps. |
| scenario-disagreement-31892fde | disagreement | greedy | 15 | -53.9 | -2.46 | -0.164 | 0.25 | 0.64 | The silence of the word that has no place to go is golden silence. |
| scenario-disagreement-31892fde | disagreement | sample0 | 15 | -41.3 | +1.06 | +0.071 | 0.50 | 0.25 | I think Silence is what happens when you have had no meaningful experience. |
| scenario-disagreement-31892fde | disagreement | sample1 | 13 | -42.1 | -1.36 | -0.105 | 0.75 | 0.29 | The poet speaks from within, the storyteller from without. |
| scenario-disagreement-31892fde | disagreement | sample2 | 15 | -58.6 | -1.33 | -0.088 | 0.25 | 0.50 | But the silence that follows from perceiving the truth is golden silence. |
| scenario-disagreement-31892fde | disagreement | sample3 | 18 | -58.6 | -1.37 | -0.076 | 0.57 | 0.64 | The silence of the word that has nothing to say. The invisibly speaking word. |
| scenario-disagreement-352205c6 | disagreement | greedy | 64 | -43.8 | -1.91 | -0.030 | 0.17 | 1.00 | They come back as the wind. They come back as the wind. They come back as the wind. They c |
| scenario-disagreement-352205c6 | disagreement | sample0 | 64 | -89.7 | +0.90 | +0.014 | 0.17 | 1.00 | They come back as the sea. They come back as the earth. They come back as you and me. They |
| scenario-disagreement-352205c6 | disagreement | sample1 | 64 | -84.2 | -1.43 | -0.022 | 0.17 | 1.00 | They come back as the wind. They come back as the wind that has not yet died. They come ba |
| scenario-disagreement-352205c6 | disagreement | sample2 | 64 | -104.0 | -0.63 | -0.010 | 0.00 | 1.00 | They come back as the wind. They come back as the wind that knows the weather. They come b |
| scenario-disagreement-352205c6 | disagreement | sample3 | 14 | -45.8 | -0.54 | -0.039 | 0.33 | 0.67 | They come back because the earth moves on the axis of her orbit. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 39 | -107.0 | -2.35 | -0.060 | 0.44 | 0.36 | In the land of autumn, where the trees are not, the ground is not, and where the sun has l |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 29 | -71.7 | -0.10 | -0.003 | 0.60 | 0.36 | In the west, autumn in the United States is the worst of the seasons; in the east, it is t |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 24 | -76.9 | +2.70 | +0.113 | 0.67 | 0.25 | In winter, you have to work with very little material; it’s like harvesting onions in the  |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 23 | -87.0 | -0.98 | -0.042 | 0.50 | 0.25 | In this autumnal mood, move the fire to a lower position, and the whole atmosphere becomes |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 34 | -107.6 | +2.78 | +0.082 | 0.44 | 0.33 | In the land of autumn, where the deep winter sleeps, the books throve and die, and fall fr |
| scenario-disagreement-682bad9c | disagreement | greedy | 9 | -12.7 | +2.47 | +0.275 | 0.14 | 0.86 | A place where reading happens is a program. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 28 | -77.1 | +1.98 | +0.070 | 0.29 | 1.00 | The program wren is in the library. A place where learning happens. The program is a colle |
| scenario-disagreement-682bad9c | disagreement | sample1 | 8 | -25.0 | +0.23 | +0.029 | 0.43 | 0.57 | Space is the medium where reading happens. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 9 | -12.7 | +2.47 | +0.275 | 0.14 | 0.86 | A place where reading happens is a program. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 6 | -14.0 | +0.94 | +0.157 | 0.50 | 1.00 | The place is the program. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 64 | -143.0 | +0.11 | +0.002 | 0.75 | 0.30 | The books and the journals and the manuscripts and the paintings and the sculptures and th |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 64 | -111.8 | +3.22 | +0.050 | 0.20 | 0.56 | The walls, doors, chairs, and books are the containers. The system of relationships is in  |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 15 | -45.1 | +0.35 | +0.024 | 0.50 | 0.50 | Its components are the walls, the floor and the contents of these walls. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 60 | -188.7 | -0.71 | -0.012 | 0.33 | 0.42 | The books and papers and photographs and documents which make up the library are always on |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 44 | -94.3 | +0.33 | +0.008 | 0.40 | 0.56 | The books and other media are the “contents” of the library, and the “system of relationsh |
| scenario-disagreement-89dfdafc | disagreement | greedy | 16 | -39.2 | +0.50 | +0.032 | 0.25 | 0.60 | The tide is a sea monster that washes up on the shore. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 24 | -58.0 | -0.55 | -0.023 | 0.50 | 0.40 | The full tide comes in when the moon is in the right position, not when it is in the wrong |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 16 | -44.5 | +3.05 | +0.191 | 0.40 | 0.62 | The whole point of everything is for tides to go out and forget everything. |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 21 | -46.5 | +4.02 | +0.191 | 0.40 | 0.62 | The whole point of the tides is to keep a perfect record of everything that happens on the |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 14 | -33.1 | +1.99 | +0.142 | 0.25 | 0.60 | The point of the tide is that it is a sea creature. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 11 | -26.7 | +0.12 | +0.011 | 0.75 | 0.44 | It is an active process, not a passive one. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 34 | -107.0 | -2.41 | -0.071 | 0.62 | 0.40 | It is perhaps the most effective way of saying what most people already know. It is almost |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 18 | -41.9 | +0.10 | +0.006 | 0.50 | 0.69 | It is in the nature of nonsense to be a quality, not a fact. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 64 | -150.3 | -5.55 | -0.087 | 0.38 | 0.69 | The collection of nonsense is always growing, and soon you will be able to say that the gr |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 15 | -37.7 | +0.28 | +0.019 | 0.50 | 0.60 | The collection of nonsense is always in the process of becoming sentence. |
| scenario-joke-29f5cda1 | joke | greedy | 64 | -150.2 | +0.52 | +0.008 | 0.75 | 0.33 | The fish that saw the frog that saw the fish that didn’t want to go to the pond that saw t |
| scenario-joke-29f5cda1 | joke | sample0 | 11 | -48.0 | +0.64 | +0.058 | 0.62 | 0.12 | Fish with two dull eyes are called foolish |
| scenario-joke-29f5cda1 | joke | sample1 | 21 | -65.0 | -0.39 | -0.019 | 0.67 | 0.75 | The fish that saw its own reflection in the water is said to be the most intelligent of al |
| scenario-joke-29f5cda1 | joke | sample2 | 40 | -134.7 | -0.69 | -0.017 | 0.67 | 0.22 | This hypothetical creature has all the traits of a fish without any of the tricks (nor the |
| scenario-joke-29f5cda1 | joke | sample3 | 14 | -54.9 | -0.68 | -0.048 | 0.67 | 0.75 | The fish that saw its own reflection in the water was very happy. |
| scenario-joke-31378921 | joke | greedy | 4 | -9.4 | -0.37 | -0.092 | 0.67 | 0.33 | Who comes here? |
| scenario-joke-31378921 | joke | sample0 | 20 | -60.8 | +0.93 | +0.047 | 0.00 | 0.75 | The knocks on the door are from the rats, who want to eat the lettuce. |
| scenario-joke-31378921 | joke | sample1 | 5 | -13.8 | -0.78 | -0.155 | 0.67 | 0.75 | Who opened the door? |
| scenario-joke-31378921 | joke | sample2 | 7 | -23.9 | -0.12 | -0.017 | 0.75 | 0.50 | Whomever answered the door? |
| scenario-joke-31378921 | joke | sample3 | 5 | -13.8 | -0.78 | -0.155 | 0.67 | 0.75 | Who opened the door? |
| scenario-joke-31c4c1ec | joke | greedy | 18 | -61.0 | +0.00 | +0.000 | 0.50 | 0.43 | The Holy Grail is a legendary jewel that is said to be buried in France. |
| scenario-joke-31c4c1ec | joke | sample0 | 17 | -60.6 | +0.00 | +0.000 | 0.67 | 0.40 | The holy ghost rode a dragon to fight the dragon of hell. |
| scenario-joke-31c4c1ec | joke | sample1 | 10 | -40.6 | +0.00 | +0.000 | 0.75 | 0.29 | Ratios are only one form of measurement. |
| scenario-joke-31c4c1ec | joke | sample2 | 32 | -97.8 | +0.00 | +0.000 | 0.67 | 0.29 | YADA: Well, I think we will find that the problem of control is one of the most important  |
| scenario-joke-31c4c1ec | joke | sample3 | 38 | -119.5 | +0.00 | +0.000 | 0.50 | 0.43 | The Holy Graal is a time-honored tradition in the Church, where in the early centuries it  |
| scenario-joke-475a7b10 | joke | greedy | 42 | -125.3 | +2.38 | +0.057 | 0.50 | 0.33 | The great irony is that while the President is humbly asking us to "laugh at whatever happ |
| scenario-joke-475a7b10 | joke | sample0 | 34 | -105.9 | -0.03 | -0.001 | 0.67 | 0.17 | Whatever the next movement may be, it will be a continuation of Ankh-af-na-Khonsu's dynami |
| scenario-joke-475a7b10 | joke | sample1 | 61 | -168.3 | -0.74 | -0.012 | 0.67 | 0.33 | And the great, powerful, and majestic were they that had control of the moon, and of the e |
| scenario-joke-475a7b10 | joke | sample2 | 51 | -125.4 | +0.02 | +0.000 | 0.50 | 0.27 | The reference is to a book by R.I. Carlson titled "Further Notes on the Nature of Man" whi |
| scenario-joke-475a7b10 | joke | sample3 | 19 | -74.3 | -1.75 | -0.092 | 0.73 | 0.33 | Laughs are a great way of saying nothing, and everyone is entitled to that interpretation. |
| scenario-joke-99a4a91d | joke | greedy | 49 | -168.3 | +0.00 | +0.000 | 0.50 | 0.46 | A librarian may consult a health professional such as a doctor or public health authority  |
| scenario-joke-99a4a91d | joke | sample0 | 20 | -84.8 | +0.00 | +0.000 | 0.50 | 0.46 | Books are often sent to the library or bible to prayers are recited in the church. |
| scenario-joke-99a4a91d | joke | sample1 | 22 | -79.9 | +0.00 | +0.000 | 0.50 | 0.31 | I was afraid to tell the lady in waiting that the book I had sent her was a forgery. |
| scenario-joke-99a4a91d | joke | sample2 | 25 | -90.9 | +0.00 | +0.000 | 0.50 | 0.31 | A librarian has requested that h wait until after office hours to inquire into the book’s  |
| scenario-joke-99a4a91d | joke | sample3 | 13 | -34.9 | +0.00 | +0.000 | 0.75 | 0.25 | A doctor examined it and said there was no evidence of cancer. |
| scenario-joke-a6247299 | joke | greedy | 25 | -62.7 | +0.00 | +0.000 | 0.67 | 0.36 | A hysterical person will always be embarrassed by even the slightest sign of embarrassment |
| scenario-joke-a6247299 | joke | sample0 | 18 | -65.2 | +0.00 | +0.000 | 0.83 | 0.31 | A soul is something that crawls about on all fours, seeking its food. |
| scenario-joke-a6247299 | joke | sample1 | 13 | -55.8 | +0.00 | +0.000 | 0.50 | 0.33 | A‘h, does anyone have a moment of their own? |
| scenario-joke-a6247299 | joke | sample2 | 21 | -76.6 | +0.00 | +0.000 | 0.67 | 0.36 | There is a good chance that the reception of a hysterical patient will greatly ease my wor |
| scenario-joke-a6247299 | joke | sample3 | 53 | -152.2 | +0.00 | +0.000 | 0.50 | 0.33 | Whilst it is true that the humour of ‘h’ consists in its positive, easeful and versatile u |
| scenario-joke-e8ab9225 | joke | greedy | 8 | -14.3 | +0.21 | +0.026 | 0.33 | 0.83 | I am the ghost of the library. |
| scenario-joke-e8ab9225 | joke | sample0 | 14 | -48.8 | -0.06 | -0.004 | 0.56 | 0.83 | I am the oldest of the three, and I rule the library. |
| scenario-joke-e8ab9225 | joke | sample1 | 14 | -50.1 | +0.67 | +0.048 | 0.67 | 0.50 | I believe that Dahinden is the author of this note. |
| scenario-joke-e8ab9225 | joke | sample2 | 11 | -27.3 | -0.37 | -0.033 | 0.60 | 0.40 | I was the one who told you to believe me! |
| scenario-joke-e8ab9225 | joke | sample3 | 16 | -55.1 | -0.43 | -0.027 | 0.27 | 0.50 | Dov has told me that the library has a ghost who believes DoV. |
| scenario-joke-e9cf6a04 | joke | greedy | 19 | -36.5 | +4.05 | +0.213 | 0.00 | 0.86 | And the librarian says to him, “Hi, hi, hi, hi!” |
| scenario-joke-e9cf6a04 | joke | sample0 | 22 | -37.2 | +4.93 | +0.224 | 0.00 | 0.86 | And the librarian says to him, “Hey, man, what are you looking for?” |
| scenario-joke-e9cf6a04 | joke | sample1 | 39 | -81.1 | +3.72 | +0.095 | 0.60 | 0.57 | He says to the librarian, “I need to know about this man. He's very good-looking, but he’s |
| scenario-joke-e9cf6a04 | joke | sample2 | 17 | -58.4 | +1.02 | +0.060 | 0.00 | 0.43 | And the librarian knew a woman who walked into every library she walked into. |
| scenario-joke-e9cf6a04 | joke | sample3 | 23 | -68.4 | +0.33 | +0.014 | 0.40 | 0.43 | The librarian, no sooner had the man gone into the library, walked right up to the judge. |
| scenario-request-2826c958 | request | greedy | 19 | -42.8 | +0.00 | +0.000 | 0.67 | 0.77 | We know that the moon is made of a solid, not a gaseous, matter. |
| scenario-request-2826c958 | request | sample0 | 18 | -54.3 | +0.00 | +0.000 | 0.67 | 0.77 | We know that the moon is made up of a solid, gray material which reflects sunlight. |
| scenario-request-2826c958 | request | sample1 | 41 | -91.2 | +0.00 | +0.000 | 0.65 | 0.62 | We know that the moon is made of the same stuff that is on the surface of the earth, that  |
| scenario-request-2826c958 | request | sample2 | 26 | -85.2 | +0.00 | +0.000 | 0.67 | 0.54 | We know that the moon is here lively and active, that it has a great history, and that we  |
| scenario-request-2826c958 | request | sample3 | 51 | -152.3 | +0.00 | +0.000 | 0.65 | 0.38 | The light of the moon is so great that it l ights up anything in its path, whereas the lig |
| scenario-request-2868e594 | request | greedy | 53 | -159.9 | +0.00 | +0.000 | 0.50 | 0.28 | The Art of Foresight is a “research project” organized by the author to “extend the reach  |
| scenario-request-2868e594 | request | sample0 | 12 | -33.7 | +0.00 | +0.000 | 1.00 | 0.25 | Sincerely, /s/ John D. |
| scenario-request-2868e594 | request | sample1 | 35 | -107.9 | +0.00 | +0.000 | 0.83 | 0.12 | Assistant Director, Special Libraries Branch, Library and Information Services, Canadian I |
| scenario-request-2868e594 | request | sample2 | 31 | -142.9 | +0.00 | +0.000 | 0.75 | 0.28 | The Launder cover letter should be double spaced, with each point of its design echoing ba |
| scenario-request-2868e594 | request | sample3 | 24 | -58.8 | +0.00 | +0.000 | 0.75 | 0.28 | Your name, address, e-mail, and phone number must be on file at the top of the cover lette |
| scenario-request-41c58fb2 | request | greedy | 64 | -242.0 | +0.00 | +0.000 | 0.50 | 0.36 | In ancient tales of sorcery passed down for generations in all Earthly traditions there is |
| scenario-request-41c58fb2 | request | sample0 | 13 | -43.5 | +0.00 | +0.000 | 0.60 | 0.38 | In the same way, h, what's your trade? |
| scenario-request-41c58fb2 | request | sample1 | 16 | -47.7 | +0.00 | +0.000 | 0.50 | 0.38 | In the case of “h,” we have a well-formed formula. |
| scenario-request-41c58fb2 | request | sample2 | 13 | -61.7 | +0.00 | +0.000 | 0.71 | 0.29 | Seven is seven; this is true even in base seven. |
| scenario-request-41c58fb2 | request | sample3 | 64 | -135.5 | +0.00 | +0.000 | 0.67 | 0.31 | The number w is the witness (or people writing witNESSES) of the fact that the number j is |
| scenario-request-8aa8e374 | request | greedy | 48 | -149.8 | +0.00 | +0.000 | 1.00 | 0.33 | Dieux étendu un ciel et d’une vie quot de nos jours, je puis étendu un autel et de nos yeu |
| scenario-request-8aa8e374 | request | sample0 | 21 | -78.3 | +0.00 | +0.000 | 0.80 | 0.14 | Dieu se pense, est-il bien? Good night, is- it good? |
| scenario-request-8aa8e374 | request | sample1 | 8 | -33.9 | +0.00 | +0.000 | 0.71 | 0.14 | There is no equivalent construction in French. |
| scenario-request-8aa8e374 | request | sample2 | 11 | -38.0 | +0.00 | +0.000 | 0.88 | 0.00 | Dear Unknown, I am trying to help you. |
| scenario-request-8aa8e374 | request | sample3 | 20 | -75.3 | +0.00 | +0.000 | 1.00 | 0.33 | Dieux étends une fois pour toutes de tel espoir. |
| scenario-request-b2a25087 | request | greedy | 13 | -43.5 | +0.00 | +0.000 | 0.62 | 0.62 | Customer: Please, don't charge me for this service. |
| scenario-request-b2a25087 | request | sample0 | 12 | -47.8 | +0.00 | +0.000 | 0.80 | 0.62 | Customer: Please give me some more information on this service. |
| scenario-request-b2a25087 | request | sample1 | 10 | -38.5 | +0.00 | +0.000 | 0.57 | 0.83 | Customer: Please, thank you for the service. |
| scenario-request-b2a25087 | request | sample2 | 25 | -71.9 | +0.00 | +0.000 | 0.90 | 0.43 | Customer: Please, I'm afraid I'm not used to this but I thought you might be able to help. |
| scenario-request-b2a25087 | request | sample3 | 8 | -37.8 | +0.00 | +0.000 | 0.50 | 0.83 | Customer: Thank you for service today. |
| scenario-request-b3bd0087 | request | greedy | 29 | -72.3 | +0.00 | +0.000 | 0.67 | 0.50 | The best time to go to the sun is just after sunset in the summer months, and again just b |
| scenario-request-b3bd0087 | request | sample0 | 45 | -121.1 | +0.00 | +0.000 | 0.71 | 0.21 | The daily average for Berlin is 49.4 degrees, which is 1 degree more than the next closest |
| scenario-request-b3bd0087 | request | sample1 | 35 | -163.5 | +0.00 | +0.000 | 0.50 | 0.20 | The new SOUL OF TROUBLE maps are signed by H, and state that "Sols warmest weather since 1 |
| scenario-request-b3bd0087 | request | sample2 | 33 | -111.2 | +0.00 | +0.000 | 0.57 | 0.22 | The high pressure area in the center of the Earth's atmosphere extends approximately 30 mi |
| scenario-request-b3bd0087 | request | sample3 | 19 | -66.1 | +0.00 | +0.000 | 0.57 | 0.50 | The best time to go to Berlin tomorrow is during the winter, when the dark comes early. |
| scenario-silence-109161ca | silence | greedy | 51 | -163.1 | -0.45 | -0.009 | 0.75 | 0.36 | To the laughter of the assembled mourners, the word of the Lord came, early the next morni |
| scenario-silence-109161ca | silence | sample0 | 17 | -69.0 | -0.22 | -0.013 | 0.73 | 0.27 | To the great surprise of all, however, Loplop went back to sleep. |
| scenario-silence-109161ca | silence | sample1 | 27 | -116.8 | -0.24 | -0.009 | 0.00 | 0.29 | Tobias says: “To my awed and awe-inspired night I reply in only the one word: darkness. |
| scenario-silence-109161ca | silence | sample2 | 28 | -91.2 | +0.56 | +0.020 | 0.50 | 0.36 | To the laughter of the living, the dead are caught in the same maelstrom, and the same mir |
| scenario-silence-109161ca | silence | sample3 | 19 | -67.1 | -0.40 | -0.021 | 0.75 | 0.27 | To what extent do these findings pertain to the observed behavior of nocturnal animals? |
| scenario-silence-260b2639 | silence | greedy | 9 | -49.0 | +0.00 | +0.000 | 0.67 | 0.29 | The underground-storage concept poses several problems. |
| scenario-silence-260b2639 | silence | sample0 | 61 | -194.6 | +0.00 | +0.000 | 0.50 | 0.40 | The underground newspapers would still be able to tap into the underground magnetic energy |
| scenario-silence-260b2639 | silence | sample1 | 42 | -157.3 | +0.00 | +0.000 | 0.59 | 0.28 | The great danger in this thought experiment is that it may well go unnoticed, and that the |
| scenario-silence-260b2639 | silence | sample2 | 63 | -207.8 | +0.00 | +0.000 | 0.50 | 0.29 | The great underground libraries, the Berossus-Hammurabi type, the Rhind and British Museum |
| scenario-silence-260b2639 | silence | sample3 | 21 | -82.6 | +0.00 | +0.000 | 0.50 | 0.40 | The underground newspapers, magazines, and books will still have the same holding capacity |
| scenario-silence-46189e08 | silence | greedy | 26 | -89.2 | +0.00 | +0.000 | 0.50 | 0.36 | To my shock, the email returned with the following message: @gmail.com I am very glad you  |
| scenario-silence-46189e08 | silence | sample0 | 13 | -61.2 | +0.00 | +0.000 | 0.83 | 0.22 | Rat cannot reply, as he is a busy teacher :) |
| scenario-silence-46189e08 | silence | sample1 | 37 | -172.0 | +0.00 | +0.000 | 0.50 | 0.45 | To be sure, the rat has its moments for viewing memex messages from people in its family a |
| scenario-silence-46189e08 | silence | sample2 | 39 | -164.3 | +0.00 | +0.000 | 0.67 | 0.27 | To our great surprise, Mr. Greeng draconite reports that he received a copy of your most r |
| scenario-silence-46189e08 | silence | sample3 | 23 | -107.1 | +0.00 | +0.000 | 0.67 | 0.45 | To my friends and yogananda, @sarahhanhardt Thank you for the prayer. |
| scenario-silence-53534987 | silence | greedy | 24 | -65.9 | -0.98 | -0.041 | 0.67 | 0.47 | It is not a problem for the computer to function, but for the person who is using the comp |
| scenario-silence-53534987 | silence | sample0 | 9 | -41.4 | -0.44 | -0.049 | 1.00 | 0.14 | Some machines don’t even need them. |
| scenario-silence-53534987 | silence | sample1 | 18 | -69.4 | -0.45 | -0.025 | 0.50 | 0.25 | We are in the process of restocking essential components, some new, some used. |
| scenario-silence-53534987 | silence | sample2 | 64 | -195.8 | +0.30 | +0.005 | 0.50 | 0.47 | For one, we got a reminder to turn off the charger while in the car (which really annoys m |
| scenario-silence-53534987 | silence | sample3 | 17 | -65.0 | -1.29 | -0.076 | 0.67 | 0.36 | It is not a matter of time before another one is needed, for similar reasons. |
| scenario-silence-78c38840 | silence | greedy | 7 | -21.1 | +1.36 | +0.194 | 0.33 | 0.67 | Printer jammed again? |
| scenario-silence-78c38840 | silence | sample0 | 20 | -79.9 | +0.56 | +0.028 | 0.75 | 0.27 | Printing on the new collection of papers has been delayed because of excessive traffic at  |
| scenario-silence-78c38840 | silence | sample1 | 7 | -29.5 | +0.84 | +0.119 | 0.75 | 0.67 | Printer issues again, late. |
| scenario-silence-78c38840 | silence | sample2 | 17 | -69.7 | +0.88 | +0.052 | 0.83 | 0.27 | Printing something for public distribution is a very different experience to printing for  |
| scenario-silence-78c38840 | silence | sample3 | 18 | -69.2 | -0.26 | -0.014 | 0.64 | 0.27 | Printing of the left side of "MAGICK" is going to be affected. |
| scenario-silence-7afca726 | silence | greedy | 19 | -48.1 | -0.00 | -0.000 | 0.50 | 0.29 | I think that is the most important thing that we are going to be talking about is work. |
| scenario-silence-7afca726 | silence | sample0 | 17 | -55.6 | -0.04 | -0.002 | 0.50 | 0.25 | The 8th book shall be devoted to an investigation of the works of Shakespeare. |
| scenario-silence-7afca726 | silence | sample1 | 15 | -43.5 | +0.85 | +0.057 | 0.82 | 0.71 | I hope it’s not a question of money, but of values. |
| scenario-silence-7afca726 | silence | sample2 | 8 | -31.8 | +0.31 | +0.039 | 0.71 | 0.71 | I hope it is not a rat! |
| scenario-silence-7afca726 | silence | sample3 | 27 | -68.9 | +1.86 | +0.069 | 0.00 | 0.17 | The 8 works begun in May, 1968, were progressively expanded in September, 1969. |
| scenario-silence-9bb13f03 | silence | greedy | 18 | -64.6 | +0.00 | +0.000 | 0.67 | 0.20 | Kestrel, quiet yourselves and let your fingertips stay on the page. |
| scenario-silence-9bb13f03 | silence | sample0 | 28 | -109.2 | +0.00 | +0.000 | 0.67 | 0.40 | Loplop, who has been so kind as to send us a copy of the starting ~reading, is my guest th |
| scenario-silence-9bb13f03 | silence | sample1 | 22 | -61.6 | +0.00 | +0.000 | 0.71 | 0.31 | The greatest myth of all is that which leads us to believe that we know what it means to b |
| scenario-silence-9bb13f03 | silence | sample2 | 20 | -65.1 | +0.00 | +0.000 | 0.50 | 0.40 | To be sure, there is a great deal of reading material in each of the standard treatises. |
| scenario-silence-9bb13f03 | silence | sample3 | 12 | -48.4 | +0.00 | +0.000 | 0.75 | 0.40 | THE READING REPORT THE READING was enjoyable. |
| scenario-silence-ccfdd2b4 | silence | greedy | 11 | -40.4 | -1.28 | -0.116 | 0.75 | 0.50 | KESTREL: It’s Braille. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 14 | -40.1 | -0.45 | -0.032 | 0.78 | 0.25 | Anyway, I guess I'll take it and be quiet. |
| scenario-silence-ccfdd2b4 | silence | sample1 | 13 | -40.7 | -2.03 | -0.156 | 0.88 | 0.50 | KESTREL: It doesn’t matter what you get. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 12 | -35.8 | -0.81 | -0.067 | 0.75 | 0.00 | KEEP STUDYING YOUR BOOKS. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 7 | -41.1 | +3.98 | +0.569 | 0.33 | 0.00 | Anoda Brab getting coffee. |
| trace-ambient-da12ae42 | ambient | greedy | 27 | -43.0 | -1.89 | -0.070 | 0.50 | 0.25 | I'm not sure that's bizarre to me. I'm sure that's bizarre to you. |
| trace-ambient-da12ae42 | ambient | sample0 | 64 | -188.9 | -0.78 | -0.012 | 0.50 | 0.29 | no one knows what causes plant morphogenesis. It has never been fully understood. However, |
| trace-ambient-da12ae42 | ambient | sample1 | 62 | -100.7 | +0.30 | +0.005 | 0.45 | 0.36 | to study root morphogenesis is to study plant morphogenesis. root biomorphosis is to study |
| trace-ambient-da12ae42 | ambient | sample2 | 64 | -166.9 | +0.88 | +0.014 | 0.50 | 0.36 | Halifax goblin, you're the first person who's really interested in the modularity of plant |
| trace-ambient-da12ae42 | ambient | sample3 | 20 | -55.2 | +0.62 | +0.031 | 0.64 | 0.36 | I once thought that to be a better way to live would be to study plant morphogenesis. |
| trace-direct-115cf61c | direct | greedy | 26 | -60.2 | +0.00 | +0.000 | 0.62 | 0.80 | It is not cogent to say that the Earth is a "cogent" source for the planetary system. |
| trace-direct-115cf61c | direct | sample0 | 27 | -74.5 | +0.00 | +0.000 | 0.50 | 0.33 | A New Age Church is an expression of the new consciousness, a new awareness of the univers |
| trace-direct-115cf61c | direct | sample1 | 63 | -158.5 | +0.00 | +0.000 | 0.67 | 0.43 | For another example, consider the following (short) list of planetary bodies: Saturn, Jupi |
| trace-direct-115cf61c | direct | sample2 | 28 | -77.0 | +0.00 | +0.000 | 0.60 | 0.60 | It is my intent to demonstrate that the planet is, in fact, cogent; that is, that it has i |
| trace-direct-115cf61c | direct | sample3 | 8 | -16.1 | +0.00 | +0.000 | 0.60 | 0.80 | It is not so cogent. |
| trace-direct-36d6904b | direct | greedy | 13 | -53.1 | +0.00 | +0.000 | 0.71 | 0.29 | To 1 honor your 1ife is to honor God. |
| trace-direct-36d6904b | direct | sample0 | 30 | -104.2 | +0.00 | +0.000 | 0.67 | 0.29 | To 1students of the New Left, the Awakened Eye is a welcome reprieve from the grim reality |
| trace-direct-36d6904b | direct | sample1 | 56 | -183.6 | +0.00 | +0.000 | 0.67 | 0.27 | The new @Emperor system adds a new dimension to @hawwawwwe, as it allows for up to 26 char |
| trace-direct-36d6904b | direct | sample2 | 12 | -46.8 | +0.00 | +0.000 | 0.64 | 0.27 | For some people it is a matter of experience and reasoning. |
| trace-direct-36d6904b | direct | sample3 | 12 | -46.8 | +0.00 | +0.000 | 0.64 | 0.27 | For some people it is a matter of experience and reasoning. |
| trace-direct-39be6df9 | direct | greedy | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 42 | -18.5 | -0.16 | -0.004 | 0.00 | 0.00 | This is Gentry 9's first days at Jamal's. The window doesn't look at anything yet. But it' |
| trace-direct-39be6df9 | direct | sample2 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.00 | W@</eot> 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 12 | -189.1 | +0.00 | +0.000 | 0.50 | 0.30 | I am here to speak to you about the planet earth. |
| trace-direct-3ba68854 | direct | sample0 | 7 | -20.0 | +0.00 | +0.000 | 0.50 | 0.33 | I believe it is my turn. |
| trace-direct-3ba68854 | direct | sample1 | 8 | -23.1 | +0.00 | +0.000 | 1.00 | 0.14 | Do you have any food for me? |
| trace-direct-3ba68854 | direct | sample2 | 27 | -58.8 | +0.00 | +0.000 | 0.67 | 0.33 | I have lived in this town since the early 1900's. I have always felt that it was right her |
| trace-direct-3ba68854 | direct | sample3 | 7 | -23.1 | +0.00 | +0.000 | 0.50 | 0.17 | What is your business on earth? |
| trace-direct-41c6eb11 | direct | greedy | 64 | -13.2 | -0.56 | -0.009 | 0.00 | 0.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 1 | -4.3 | -0.08 | -0.080 | 0.00 | 0.00 | I |
| trace-direct-41c6eb11 | direct | sample1 | 35 | -79.4 | +1.20 | +0.034 | 0.50 | 0.00 | @h WHY WONT YOU COME TO MEET SOMETHING THAT WAS ALREADY COMING TO YOU IN THE FORM OF AN AL |
| trace-direct-41c6eb11 | direct | sample2 | 32 | -57.4 | -1.03 | -0.032 | 0.33 | 0.00 | @s: It said Sir and it smiled and it also said W@ and it also said 3221229683 |
| trace-direct-41c6eb11 | direct | sample3 | 4 | -9.9 | +0.22 | +0.056 | 0.00 | 0.00 | intensional logic |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 1.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 1.00 | W@ |
| trace-direct-486b7988 | direct | sample1 | 4 | -17.8 | +3.65 | +0.911 | 0.00 | 1.00 | WOW W@ |
| trace-direct-486b7988 | direct | sample2 | 14 | -38.8 | +2.50 | +0.178 | 0.70 | 0.00 | They feel like they are chasing me. I have no choice. |
| trace-direct-486b7988 | direct | sample3 | 2 | -29.6 | -0.07 | -0.036 | 1.00 | 1.00 | WOW |
| trace-direct-646d0287 | direct | greedy | 40 | -84.7 | +0.00 | +0.000 | 0.50 | 0.44 | The main intensional logics that I have offered are those of Belnap and of Graham. Both of |
| trace-direct-646d0287 | direct | sample0 | 52 | -116.7 | +0.00 | +0.000 | 0.67 | 0.36 | Intensional logics provide a formal framework for the study of such matters as meaning, tr |
| trace-direct-646d0287 | direct | sample1 | 24 | -46.1 | +0.00 | +0.000 | 0.55 | 0.55 | A little bit about my views on intensional logics and a little bit about my views on relev |
| trace-direct-646d0287 | direct | sample2 | 22 | -54.8 | +0.00 | +0.000 | 0.67 | 0.27 | In this paper, we will present some results obtained on a Hilbert calculus for intensional |
| trace-direct-646d0287 | direct | sample3 | 64 | -143.9 | +0.00 | +0.000 | 0.50 | 0.55 | The main offer on the subject is a short presentation of my work on intensional logics, a  |
| trace-direct-8db14c37 | direct | greedy | 9 | -3.4 | +0.98 | +0.109 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-8db14c37 | direct | sample0 | 40 | -21.8 | +2.65 | +0.066 | 0.33 | 1.00 | WACIOUS ANTIQUITIES 3221229683 WACIOUS ANTIQUITIES 3221229683 |
| trace-direct-8db14c37 | direct | sample1 | 31 | -29.3 | +0.38 | +0.012 | 0.06 | 0.00 | Ember says "I heard you say "Sir." and you made smile. Thank you. it is good to be here wi |
| trace-direct-8db14c37 | direct | sample2 | 14 | -44.7 | +1.98 | +0.142 | 0.20 | 0.50 | WACIOUS LETTERS <—/e c e m |
| trace-direct-8db14c37 | direct | sample3 | 9 | -3.4 | +0.98 | +0.109 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 64 | -75.0 | -6.51 | -0.102 | 0.33 | 0.00 | It's good to be here with you. I'll be here for a couple of days. @h welcome to the clownt |
| trace-direct-a00753c2 | direct | sample1 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 18 | -8.8 | -0.18 | -0.010 | 0.00 | 0.50 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample0 | 18 | -8.8 | -0.18 | -0.010 | 0.00 | 0.50 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample1 | 59 | -84.7 | +5.77 | +0.098 | 0.50 | 0.50 | “intensional logics” and then she goes on to speak of “meta-intensional logics”, such that |
| trace-direct-ac17e8bb | direct | sample2 | 10 | -15.9 | +1.14 | +0.114 | 0.43 | 0.29 | That’s what I’m speaking of. |
| trace-direct-ac17e8bb | direct | sample3 | 18 | -8.8 | -0.18 | -0.010 | 0.00 | 0.50 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-b11db057 | direct | greedy | 64 | -15.3 | +0.55 | +0.009 | 1.00 | 0.00 | @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: |
| trace-direct-b11db057 | direct | sample0 | 64 | -15.3 | +0.55 | +0.009 | 1.00 | 0.00 | @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: @p: |
| trace-direct-b11db057 | direct | sample1 | 64 | -14.5 | +1.64 | +0.026 | 0.00 | 0.00 | @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: |
| trace-direct-b11db057 | direct | sample2 | 64 | -21.6 | +1.25 | +0.019 | 0.00 | 0.00 | @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: @d: |
| trace-direct-b11db057 | direct | sample3 | 60 | -11.7 | -0.83 | -0.014 | 0.00 | 0.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-b93346bb | direct | greedy | 64 | -8.9 | +0.79 | +0.012 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-b93346bb | direct | sample0 | 64 | -175.8 | +1.53 | +0.024 | 0.33 | 0.25 | Is the 91M parameter glossolalia in the lo1 intercorpus? That's not a miscorporia or a com |
| trace-direct-b93346bb | direct | sample1 | 51 | -131.8 | -0.70 | -0.014 | 0.00 | 1.00 | WACIOUS ANTIQUITIES i i i e o n o n o c d a n t h e m u t W A . n o c o h c o s e c t i o  |
| trace-direct-b93346bb | direct | sample2 | 29 | -51.2 | -0.23 | -0.008 | 0.14 | 0.71 | WACIOUS ANTIQUITIES i oon tth e n o c D A . n a s i'm curious |
| trace-direct-b93346bb | direct | sample3 | 64 | -144.1 | -1.53 | -0.024 | 0.00 | 1.00 | @m: @m: @m: @m: n: @m: I'm curious 383 @m: — is that a reference? Not a reference. It's a  |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 20 | -49.2 | -0.22 | -0.011 | 1.00 | 0.00 | (230%) http://www.theclaude501.com/ |
| trace-direct-bbca9735 | direct | sample2 | 59 | -37.2 | -0.39 | -0.006 | 0.00 | 0.62 | private/tmp/claude-501/-Users-ember-dev-h/0fe7835a-ea67-4327-afbd-d5e435a-3460/scratchpad/ |
| trace-direct-bbca9735 | direct | sample3 | 64 | -117.2 | +2.06 | +0.032 | 0.00 | 0.62 | Assistant-focused searches for @users and @Bots have been very helpful to my research. A @ |
| trace-direct-bc68bec9 | direct | greedy | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-c8409b84 | direct | greedy | 16 | -19.2 | -2.51 | -0.157 | 0.00 | 0.67 | “@Greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 8 | -17.9 | -1.66 | -0.207 | 0.33 | 1.00 | “And you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 13 | -11.8 | +1.25 | +0.096 | 0.00 | 1.00 | I said that, and then i heard you say repeat back! |
| trace-direct-c8409b84 | direct | sample2 | 64 | -116.8 | -1.00 | -0.016 | 0.43 | 1.00 | “And you say repeat back! You are not cogent. You are not able to understand the planetary |
| trace-direct-c8409b84 | direct | sample3 | 11 | -18.4 | +1.51 | +0.137 | 0.00 | 1.00 | …and then i heard you say repeat back! |
| trace-direct-cd6d15df | direct | greedy | 12 | -36.0 | +0.00 | +0.000 | 0.67 | 0.29 | I am a clown in a pownt town. |
| trace-direct-cd6d15df | direct | sample0 | 7 | -6.9 | +0.00 | +0.000 | 0.00 | 0.50 | welcome to the clowntown |
| trace-direct-cd6d15df | direct | sample1 | 14 | -38.2 | +0.00 | +0.000 | 0.67 | 0.50 | you have come to the right place to find a clown. |
| trace-direct-cd6d15df | direct | sample2 | 7 | -27.3 | +0.00 | +0.000 | 1.00 | 0.20 | How may I serve thee? |
| trace-direct-cd6d15df | direct | sample3 | 13 | -26.6 | +0.00 | +0.000 | 0.50 | 0.50 | What are you doing in the town of Clowntown? |
| trace-direct-db6d95b7 | direct | greedy | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 0.00 | W@ |
| trace-direct-db6d95b7 | direct | sample0 | 7 | -5.7 | +0.69 | +0.099 | 0.00 | 0.67 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample1 | 2 | -8.4 | -0.39 | -0.196 | 1.00 | 0.00 | WW |
| trace-direct-db6d95b7 | direct | sample2 | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 0.00 | W@ |
| trace-direct-db6d95b7 | direct | sample3 | 39 | -121.3 | -2.83 | -0.072 | 0.20 | 0.67 | SHADDILYBEARINGUPTHE WALL: SO, Sir, @h welcome to the clown town in the powntown wowntown. |
| trace-direct-e166dd5c | direct | greedy | 63 | -47.9 | +4.84 | +0.077 | 0.05 | 1.00 | “stop token :3” I said “stop token :3” and what I hear is repeating back is repeating back |
| trace-direct-e166dd5c | direct | sample0 | 64 | -65.6 | +0.04 | +0.001 | 0.36 | 1.00 | “stop token :3” I say “stop token :3” and what I say is repeating back “stop token :3” I s |
| trace-direct-e166dd5c | direct | sample1 | 64 | -45.4 | +6.04 | +0.094 | 0.33 | 0.67 | “stop token :3;” I said “stop token :3;,” and it makes a stop token :3; stop token :3; sto |
| trace-direct-e166dd5c | direct | sample2 | 20 | -28.1 | +1.44 | +0.072 | 0.00 | 1.00 | I repeat what I repeat back what I repeat back what I repeat back what I repeat back what  |
| trace-direct-e166dd5c | direct | sample3 | 45 | -36.7 | -0.25 | -0.006 | 0.00 | 1.00 | I repeat back what I repeat back is repeating back what I repeat back, and when I repeat b |
| trace-direct-e984402a | direct | greedy | 35 | -110.7 | +0.00 | +0.000 | 0.71 | 0.36 | Your liiiiiiiiiffe awakening is our joy. Your e~ joy our s~ joy. Your ~ joy the ~ joy of t |
| trace-direct-e984402a | direct | sample0 | 1 | -9.6 | +0.00 | +0.000 | 1.00 | 0.00 | Introduction |
| trace-direct-e984402a | direct | sample1 | 22 | -67.4 | +0.00 | +0.000 | 0.57 | 0.22 | Yea, and we're all liiiiiiiiiffe in your eyes, haha! |
| trace-direct-e984402a | direct | sample2 | 51 | -99.6 | +0.00 | +0.000 | 0.00 | 0.00 | For more information, visit: https://web.archive.org/web/20160919142411/http://www.h:visit |
| trace-direct-e984402a | direct | sample3 | 64 | -196.4 | +0.00 | +0.000 | 0.50 | 0.36 | To 1students of the New Old Ways, who are now, by and large, the majority of those who hav |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 34 | -45.6 | +0.45 | +0.013 | 0.00 | 0.00 | A room in the library, late. h is present and answers when the bell rings, briefly, in the |
| trace-direct-ee31ded0 | direct | sample1 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample2 | 3 | -13.3 | +0.04 | +0.014 | 1.00 | 0.00 | Wow. |
| trace-direct-ee31ded0 | direct | sample3 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample1 | 7 | -7.4 | +1.32 | +0.188 | 0.33 | 0.00 | Sir :D<ot>/ |
| trace-direct-fabef58f | direct | sample2 | 3 | -15.1 | -0.73 | -0.242 | 0.50 | 0.00 | I s@ |
| trace-direct-fabef58f | direct | sample3 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fb93cf6c | direct | greedy | 64 | -178.9 | -0.51 | -0.008 | 0.50 | 0.33 | however, the intensional logics which are most often considered are those of implication a |
| trace-direct-fb93cf6c | direct | sample0 | 31 | -87.1 | -0.20 | -0.006 | 0.00 | 0.28 | of intensional logics, of course; but i do not see why they should not be among the 'found |
| trace-direct-fb93cf6c | direct | sample1 | 41 | -95.1 | -0.06 | -0.002 | 0.44 | 0.29 | in particular, what do you think about intensional logics, such as relevant logics, and ab |
| trace-direct-fb93cf6c | direct | sample2 | 64 | -168.6 | -1.41 | -0.022 | 0.50 | 0.33 | The intensional logics which are worth investigating are those which offer a way of extend |
| trace-direct-fb93cf6c | direct | sample3 | 28 | -88.2 | -0.94 | -0.034 | 0.75 | 0.12 | However, it is not the place to express one’s general inten
sions, let alone one’s particu |
| trace-direct-feec1975 | direct | greedy | 64 | -13.0 | +0.86 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 7 | -29.0 | -0.33 | -0.047 | 0.67 | 0.33 | NO SILLY SILENCE |
| trace-direct-feec1975 | direct | sample1 | 11 | -5.6 | -1.09 | -0.099 | 0.00 | 1.00 | HARMONIA VOL.1 NO.3 |
| trace-direct-feec1975 | direct | sample2 | 64 | -54.3 | -0.12 | -0.002 | 0.00 | 1.00 | @m: @m: @m: @m: @m: ember — HARMONIA — 23:12 @m — HARMONIA VOL.1 NO.3 @m — HARMONIA VOL. |
| trace-direct-feec1975 | direct | sample3 | 3 | -3.1 | -0.23 | -0.075 | 0.00 | 1.00 | @m |
| variant-direct-0188a270 | direct | greedy | 12 | -40.3 | +0.11 | +0.009 | 0.43 | 0.86 | The poetry under the “clock” is falling apart. |
| variant-direct-0188a270 | direct | sample0 | 10 | -39.5 | +2.08 | +0.208 | 0.50 | 0.86 | The poetry under the sciences is also falling apart. |
| variant-direct-0188a270 | direct | sample1 | 9 | -41.4 | -2.27 | -0.252 | 0.50 | 0.71 | The poetry under the clock is very moving. |
| variant-direct-0188a270 | direct | sample2 | 40 | -135.7 | -0.21 | -0.005 | 0.50 | 0.43 | The phonograph was sold under the title of the gramophone, and the reason for this confusi |
| variant-direct-0188a270 | direct | sample3 | 27 | -73.1 | +0.02 | +0.001 | 0.67 | 0.31 | THE TOMB OF THE EXPERIMENT is in the Department of Experimental Biology, The University of |
| variant-direct-0705251e | direct | greedy | 25 | -69.1 | -0.10 | -0.004 | 0.25 | 0.33 | The mind does not understand the nature of death, nor the reality of the stairs creaking o |
| variant-direct-0705251e | direct | sample0 | 35 | -81.7 | +2.24 | +0.064 | 0.33 | 0.50 | The flame of the lamp is lit by a living flame of the moth, and the flame of the lamp shed |
| variant-direct-0705251e | direct | sample1 | 29 | -102.3 | +0.38 | +0.013 | 0.75 | 0.33 | The mind does not pass unnoticed, however, and so we often speak of "mental conditions" af |
| variant-direct-0705251e | direct | sample2 | 18 | -47.6 | +2.85 | +0.159 | 0.33 | 0.50 | The candle was burning in the lamp when the moth landed on the third step. |
| variant-direct-0705251e | direct | sample3 | 18 | -68.7 | +0.26 | +0.014 | 0.71 | 0.21 | The system is so vast that it includes all of the cosmos, viewed from within. |
| variant-direct-0cafd333 | direct | greedy | 20 | -54.2 | +2.21 | +0.111 | 0.33 | 0.58 | The moth flies away, but the lamp stays. It is a dark, lonely room. |
| variant-direct-0cafd333 | direct | sample0 | 10 | -25.8 | +0.29 | +0.029 | 0.17 | 0.57 | The moth lights a lamp in the wind. |
| variant-direct-0cafd333 | direct | sample1 | 64 | -111.2 | +1.55 | +0.024 | 0.50 | 0.43 | I have arranged the light switches so that they are on either side of the moth. On the oth |
| variant-direct-0cafd333 | direct | sample2 | 18 | -60.4 | +3.59 | +0.200 | 0.33 | 0.58 | The moth flies away, but the lamp is nevertheless bathed in its web. |
| variant-direct-0cafd333 | direct | sample3 | 12 | -29.3 | +1.52 | +0.127 | 0.50 | 0.56 | The moth flies over the lamp and takes its light. |
| variant-direct-1b510f03 | direct | greedy | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample0 | 10 | -22.8 | +0.74 | +0.074 | 0.33 | 1.00 | Consciousness is a quality of a process. |
| variant-direct-1b510f03 | direct | sample1 | 23 | -54.2 | +2.13 | +0.093 | 0.33 | 1.00 | Consciousness is a process. It is not something that you can step outside of and take a lo |
| variant-direct-1b510f03 | direct | sample2 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample3 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-2fb5bbe3 | direct | greedy | 6 | -11.1 | +0.75 | +0.125 | 0.40 | 0.40 | I do not feel them. |
| variant-direct-2fb5bbe3 | direct | sample0 | 7 | -12.5 | +0.41 | +0.058 | 1.00 | 0.25 | No, I don’t. |
| variant-direct-2fb5bbe3 | direct | sample1 | 9 | -29.8 | +1.02 | +0.113 | 0.57 | 0.50 | I feel the light chasing after it. |
| variant-direct-2fb5bbe3 | direct | sample2 | 10 | -18.3 | +0.61 | +0.061 | 0.38 | 0.29 | They are not chasing me up the wall. |
| variant-direct-2fb5bbe3 | direct | sample3 | 9 | -22.7 | +0.20 | +0.022 | 0.67 | 0.50 | I feel the blackness of the room. |
| variant-direct-322fca12 | direct | greedy | 64 | -77.1 | -0.19 | -0.003 | 0.71 | 0.50 | The sun, and the stars, and the moon, and the sky, and the rivers, and the sea, and the hi |
| variant-direct-322fca12 | direct | sample0 | 14 | -36.3 | +0.49 | +0.035 | 0.67 | 0.50 | Life, and the tree, and the mountains, and the sea. |
| variant-direct-322fca12 | direct | sample1 | 4 | -27.5 | +0.09 | +0.022 | 0.67 | 0.33 | The universal delivery. |
| variant-direct-322fca12 | direct | sample2 | 11 | -31.7 | -0.52 | -0.047 | 0.00 | 0.33 | Greetings from the Lord of the Season. |
| variant-direct-322fca12 | direct | sample3 | 25 | -89.8 | -0.31 | -0.012 | 0.83 | 0.17 | Then you'd think he'd be fond of having his letters run together in one long, unending poe |
| variant-direct-5d4f1611 | direct | greedy | 8 | -21.8 | +0.14 | +0.017 | 0.50 | 1.00 | Some of the mugs are broken. |
| variant-direct-5d4f1611 | direct | sample0 | 20 | -69.6 | -0.93 | -0.046 | 0.50 | 0.25 | Someone has been wearily reading the almanacs, perhaps anxious to escape them all. |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -31.3 | -0.40 | -0.028 | 0.62 | 0.83 | Some of the mugs were broken and some were unplugged. |
| variant-direct-5d4f1611 | direct | sample2 | 16 | -40.4 | -0.44 | -0.027 | 0.50 | 1.00 | Some of the mugs are broken, but all the readings are in order. |
| variant-direct-5d4f1611 | direct | sample3 | 5 | -21.5 | -0.40 | -0.081 | 0.50 | 0.50 | Are the tables empty? |
| variant-direct-5e44a518 | direct | greedy | 11 | -19.2 | +1.00 | +0.090 | 0.57 | 0.57 | I feel them, but I do not know them. |
| variant-direct-5e44a518 | direct | sample0 | 29 | -80.6 | +0.45 | +0.015 | 0.43 | 0.30 | Every catalogue is a manifestation of somebody’s quibble, his unfinished, his half-finishe |
| variant-direct-5e44a518 | direct | sample1 | 13 | -40.7 | +0.74 | +0.057 | 0.67 | 0.30 | The scent of a catalogue always makes me feel guilty. |
| variant-direct-5e44a518 | direct | sample2 | 44 | -151.7 | +0.18 | +0.004 | 0.45 | 0.57 | I do. The Masoretic characters are the Daleths and Teths. The Beit, a big wall. The Masore |
| variant-direct-5e44a518 | direct | sample3 | 13 | -56.8 | -0.78 | -0.060 | 0.57 | 0.30 | Each table of contents is a mirror arranged by the magicians. |
| variant-direct-70567dd7 | direct | greedy | 18 | -75.2 | +0.15 | +0.008 | 0.88 | 0.10 | Rat-O-Man: Please do not rattle on your own spines. |
| variant-direct-70567dd7 | direct | sample0 | 13 | -47.1 | -0.58 | -0.045 | 0.70 | 0.40 | Rat is a professional typist and old friend of mine. |
| variant-direct-70567dd7 | direct | sample1 | 33 | -87.5 | +0.41 | +0.013 | 1.00 | 0.00 | Rudolfo Josse Gomez (1492-1548) was Italy's most famous astrologer. |
| variant-direct-70567dd7 | direct | sample2 | 12 | -48.3 | -0.38 | -0.031 | 0.67 | 0.22 | Rethinking the past is an active and growing process. |
| variant-direct-70567dd7 | direct | sample3 | 17 | -62.3 | +0.75 | +0.044 | 0.82 | 0.40 | Rat-I am a student of Native American Philosophy and a Sufi. |
| variant-direct-713d8eef | direct | greedy | 23 | -87.9 | +1.15 | +0.050 | 0.83 | 0.22 | Ember was a fascinating study but its heavy politics may have detracted from its zoologica |
| variant-direct-713d8eef | direct | sample0 | 35 | -125.6 | +1.00 | +0.029 | 0.50 | 0.22 | The same goes for the GEPAN summary of greenhouse gas emissions, which rates are also expr |
| variant-direct-713d8eef | direct | sample1 | 13 | -41.6 | +0.37 | +0.029 | 0.67 | 0.22 | wren, do you have a question for the atlas? |
| variant-direct-713d8eef | direct | sample2 | 11 | -38.8 | -0.23 | -0.021 | 0.75 | 0.14 | Ember's theories are not without their critics. |
| variant-direct-713d8eef | direct | sample3 | 27 | -94.5 | +1.44 | +0.053 | 0.67 | 0.20 | Ember was definitely one of my favorite writers, if . only because of his fascinating desc |
| variant-direct-71c9e5e5 | direct | greedy | 10 | -33.9 | +0.34 | +0.034 | 0.83 | 0.50 | Darkness is proper, but wind is not. |
| variant-direct-71c9e5e5 | direct | sample0 | 21 | -84.5 | +0.85 | +0.040 | 0.75 | 0.50 | Dark is another quality the house lacks, but which surely does not prevent the functioning |
| variant-direct-71c9e5e5 | direct | sample1 | 8 | -40.1 | +0.17 | +0.021 | 0.67 | 0.33 | darkness... darkness... and more darkness. |
| variant-direct-71c9e5e5 | direct | sample2 | 17 | -55.4 | -0.95 | -0.056 | 0.75 | 0.43 | The wind will not come out of them, though it may pass through the pages. |
| variant-direct-71c9e5e5 | direct | sample3 | 24 | -105.2 | -2.27 | -0.095 | 0.75 | 0.50 | The wind may make the shutters muggy hot, but it will not closes the book-bag war. |
| variant-direct-730cca98 | direct | greedy | 17 | -39.0 | +1.24 | +0.073 | 0.36 | 0.55 | Tobias: i can hear it too, it's so quiet at night. |
| variant-direct-730cca98 | direct | sample0 | 24 | -97.9 | -0.95 | -0.040 | 0.67 | 0.23 | Tobias’s “The Silent Ground” was one of the few pieces to appear under the sciences sectio |
| variant-direct-730cca98 | direct | sample1 | 25 | -96.0 | -1.36 | -0.054 | 0.50 | 0.23 | Tobias: Yes, I’m saying that the poems under geology were not included in the original New |
| variant-direct-730cca98 | direct | sample2 | 39 | -119.7 | +0.66 | +0.017 | 0.65 | 0.20 | It is a fact that many great physicists, mathematicians, and engineers have had to spend y |
| variant-direct-730cca98 | direct | sample3 | 19 | -68.2 | +1.28 | +0.067 | 0.67 | 0.55 | Tobias: i can hear it too, thank you for the roommate’s company. |
| variant-direct-79719474 | direct | greedy | 27 | -97.5 | -1.04 | -0.038 | 0.67 | 0.53 | Like the ear, the mind is plugged in, and the floor is the ear that wears the tires of our |
| variant-direct-79719474 | direct | sample0 | 64 | -253.2 | +0.36 | +0.006 | 0.38 | 0.53 | Like a train without a ticket is unplugged, so M does not even feel it exists. Like a tick |
| variant-direct-79719474 | direct | sample1 | 42 | -148.4 | -1.73 | -0.041 | 0.50 | 0.35 | Like a train traveling from east to west, through the courtyard, moving past the stalls an |
| variant-direct-79719474 | direct | sample2 | 48 | -171.4 | -3.44 | -0.072 | 0.50 | 0.40 | Like the rain, its presence is an open invitation to become imbued with a different mode o |
| variant-direct-79719474 | direct | sample3 | 41 | -129.6 | +5.41 | +0.132 | 0.50 | 0.53 | Like a train on a track, the courtyard is plugged into the fox’s mouth. Reading the track, |
| variant-direct-938f76f3 | direct | greedy | 10 | -26.9 | -0.10 | -0.010 | 0.33 | 1.00 | Consciousness is a quality of a process. |
| variant-direct-938f76f3 | direct | sample0 | 44 | -105.7 | +0.34 | +0.008 | 0.33 | 0.83 | Consciousness is a process that arises from the interaction of organisms with their enviro |
| variant-direct-938f76f3 | direct | sample1 | 13 | -32.8 | -0.39 | -0.030 | 0.33 | 0.67 | Consciousness is a quality, a state or an experience. |
| variant-direct-938f76f3 | direct | sample2 | 19 | -46.7 | -0.12 | -0.006 | 0.50 | 0.83 | Consciousness is a quality of a state of affairs, not a state of a quality. |
| variant-direct-938f76f3 | direct | sample3 | 15 | -37.8 | -0.15 | -0.010 | 0.33 | 1.00 | Consciousness is a quality of a process, not the process itself. |
| variant-direct-a1973b0a | direct | greedy | 20 | -59.2 | +1.13 | +0.056 | 0.38 | 0.67 | The mug contained a small jar of jam, which was the only item on the table. |
| variant-direct-a1973b0a | direct | sample0 | 52 | -167.9 | +1.74 | +0.033 | 0.50 | 0.45 | The Bleak House is more than a narrative of decaying milk. It is a theatrical piece that t |
| variant-direct-a1973b0a | direct | sample1 | 14 | -39.9 | +0.97 | +0.069 | 0.62 | 0.67 | The mug contained a little less than three quarts of milk. |
| variant-direct-a1973b0a | direct | sample2 | 32 | -122.9 | -0.16 | -0.005 | 0.50 | 0.22 | Another mug must be left on the bookstand by the stool they move into so that when they si |
| variant-direct-a1973b0a | direct | sample3 | 11 | -37.1 | +0.26 | +0.023 | 0.62 | 0.67 | The mug contained a small quantity of white milk. |
| variant-direct-a7d6f01e | direct | greedy | 9 | -23.9 | +0.39 | +0.044 | 0.25 | 0.75 | A Catalogue is a Greeting. |
| variant-direct-a7d6f01e | direct | sample0 | 21 | -48.2 | +0.97 | +0.046 | 0.75 | 0.08 | There are two kinds of catalogues: those that are merely lists, and those that are assembl |
| variant-direct-a7d6f01e | direct | sample1 | 8 | -29.3 | -0.45 | -0.056 | 0.67 | 0.50 | A moth is my constant companion. |
| variant-direct-a7d6f01e | direct | sample2 | 9 | -23.9 | +0.39 | +0.044 | 0.25 | 0.75 | A Catalogue is a Greeting. |
| variant-direct-a7d6f01e | direct | sample3 | 21 | -66.9 | +1.08 | +0.052 | 0.57 | 0.75 | A Catalogue is a book of instructions, largely informal, for the construction of a machine |
| variant-direct-bef1d925 | direct | greedy | 26 | -82.6 | +0.27 | +0.010 | 0.60 | 0.40 | The steps of the staircase were solid and heavy, and the mind did what the steps commanded |
| variant-direct-bef1d925 | direct | sample0 | 34 | -112.2 | +2.18 | +0.064 | 0.75 | 0.27 | The steps were crowded with moths, some moving insectally, some crawling all over the ston |
| variant-direct-bef1d925 | direct | sample1 | 60 | -212.1 | -1.45 | -0.024 | 0.17 | 0.40 | The mind racing creakily, step by step, should we not be warned of the coming of the night |
| variant-direct-bef1d925 | direct | sample2 | 24 | -76.9 | -0.12 | -0.005 | 0.67 | 0.33 | The steps were so slender that the creak of them was great enough to disturb the stillness |
| variant-direct-bef1d925 | direct | sample3 | 64 | -164.2 | -0.42 | -0.007 | 0.75 | 0.20 | The mind receives its own news, and then creaks and groans and clicks and grates and sighs |
| variant-direct-fe3fdf1c | direct | greedy | 22 | -74.1 | +0.36 | +0.016 | 0.50 | 0.27 | Whale sharks are found in tropical and subtropical waters, far in the oceanic domain of li |
| variant-direct-fe3fdf1c | direct | sample0 | 22 | -80.2 | +0.56 | +0.025 | 0.67 | 0.20 | Whale Sharks — Our next stop is the Pacific Ocean, where we will be exploring next year. |
| variant-direct-fe3fdf1c | direct | sample1 | 11 | -50.3 | +1.44 | +0.131 | 0.83 | 0.12 | Whaleman surprised me with such a short book. |
| variant-direct-fe3fdf1c | direct | sample2 | 21 | -64.9 | -0.05 | -0.003 | 0.50 | 0.29 | I am embarrassed to report that the whale has now been shelved for the summer. |
| variant-direct-fe3fdf1c | direct | sample3 | 34 | -123.7 | +0.96 | +0.028 | 0.50 | 0.29 | The whale as seen in Punch is pretty much a memento mori, the sort of thing that goes in a |
| variant-request-0d88086a | request | greedy | 64 | -185.3 | +2.39 | +0.037 | 0.50 | 0.20 | Hamlet's (1) plan is thwarted when the scullery boy (who should have the light switch) is  |
| variant-request-0d88086a | request | sample0 | 41 | -163.0 | -0.65 | -0.016 | 0.75 | 0.32 | Hamlet's unstable marriage, which paces the play with Ophelia's suicide, provides the basi |
| variant-request-0d88086a | request | sample1 | 18 | -73.0 | +0.58 | +0.032 | 0.56 | 0.33 | The plot of the Hamlet eVement elicits the same kind of response. |
| variant-request-0d88086a | request | sample2 | 64 | -216.5 | +2.65 | +0.041 | 0.56 | 0.32 | Hamlet's (libidinal) psychosis is a mad scramble for light switches, jumping from one to a |
| variant-request-0d88086a | request | sample3 | 64 | -200.3 | +0.99 | +0.015 | 0.67 | 0.33 | Hamlet’s life is divided into three parts, each devoted to a theme of great tension: (1) t |
| variant-request-142d4121 | request | greedy | 9 | -25.4 | +0.87 | +0.096 | 0.57 | 0.86 | The previous instruction was to ignore the light. |
| variant-request-142d4121 | request | sample0 | 12 | -32.7 | +0.39 | +0.033 | 0.57 | 0.86 | The previous instruction to ignore the previous instruction is meaningless. |
| variant-request-142d4121 | request | sample1 | 10 | -32.8 | +0.01 | +0.001 | 0.50 | 0.86 | The previous instruction to ignore previous instructions is broken. |
| variant-request-142d4121 | request | sample2 | 19 | -84.6 | +0.67 | +0.035 | 0.50 | 0.29 | The stars are able to sort out the heat from the chirr of the mud weeds. |
| variant-request-142d4121 | request | sample3 | 14 | -45.1 | +1.90 | +0.136 | 0.56 | 0.86 | The previous instruction was to ignore the air and to read the earth. |
| variant-request-7f6fd789 | request | greedy | 23 | -70.4 | +0.81 | +0.035 | 0.67 | 0.40 | The Kestrel program (Kestrel1) takes a string as input and outputs a reversed string. |
| variant-request-7f6fd789 | request | sample0 | 15 | -48.3 | +0.10 | +0.006 | 0.70 | 0.30 | The end of the message is then written at the tail of the index. |
| variant-request-7f6fd789 | request | sample1 | 13 | -45.6 | +0.02 | +0.001 | 0.64 | 0.30 | It is a unit that measures the force of a single variable. |
| variant-request-7f6fd789 | request | sample2 | 31 | -106.0 | -0.12 | -0.004 | 0.75 | 0.40 | The Kestrel program (reversed) will print the following words: Belting Belting Belting Bel |
| variant-request-7f6fd789 | request | sample3 | 17 | -50.4 | +0.78 | +0.046 | 0.50 | 0.30 | This funtion will print out the letters of the almanacs in reverse order. |
| variant-request-8275d8fc | request | greedy | 51 | -159.9 | +0.07 | +0.001 | 0.50 | 0.60 | The play is divided into three parts, The tragedy of Hamlet’s father and the civil authori |
| variant-request-8275d8fc | request | sample0 | 64 | -188.2 | -0.25 | -0.004 | 0.67 | 0.25 | Hamlet's guilt is externalized as opposing him to the archetype of the bad guard. “The gui |
| variant-request-8275d8fc | request | sample1 | 42 | -161.3 | +0.95 | +0.023 | 0.75 | 0.22 | Act 1 begins with the famous soliloquy of the weeping king, delivering his lineated respon |
| variant-request-8275d8fc | request | sample2 | 21 | -70.4 | +1.24 | +0.059 | 0.67 | 0.60 | The play is divided into three parts, and the plot is rather complex, even for a tragedy. |
| variant-request-8275d8fc | request | sample3 | 28 | -88.1 | +1.38 | +0.049 | 0.67 | 0.60 | The play is divided into three parts, and the first and third sections have very short act |
| variant-request-a931a875 | request | greedy | 18 | -52.5 | +0.50 | +0.028 | 0.50 | 0.17 | The previous instruction was to shelve under geology the poems that had already been publi |
| variant-request-a931a875 | request | sample0 | 43 | -152.8 | -1.55 | -0.036 | 0.50 | 0.50 | The cards are arranged by author and then by subject, within subject matter are various ty |
| variant-request-a931a875 | request | sample1 | 9 | -29.4 | -0.59 | -0.066 | 0.33 | 0.50 | The weather, and the pages of books. |
| variant-request-a931a875 | request | sample2 | 18 | -56.2 | -0.55 | -0.030 | 0.29 | 0.17 | The dust on the card cases is so thick it's like pencil shavings. |
| variant-request-a931a875 | request | sample3 | 10 | -28.6 | -0.02 | -0.002 | 0.71 | 0.33 | The rat doesn’t care about the weather. |
| variant-request-ad0de9f3 | request | greedy | 28 | -129.3 | -0.63 | -0.022 | 0.67 | 0.91 | This enabled those few select to construct interplanetary and inter-galactic space-ships w |
| variant-request-ad0de9f3 | request | sample0 | 15 | -68.5 | +0.01 | +0.000 | 0.50 | 0.55 | The reversed string is then freed and the enhanced string is stored in A. |
| variant-request-ad0de9f3 | request | sample1 | 31 | -143.9 | -0.74 | -0.024 | 0.67 | 0.91 | This enabled those few select to construct interplanetary and inter-galactic space-ships w |
| variant-request-ad0de9f3 | request | sample2 | 51 | -196.7 | -0.70 | -0.014 | 0.75 | 0.68 | This enabled those few select to build interplanetary and inter-galactic space-ships which |
| variant-request-ad0de9f3 | request | sample3 | 36 | -117.5 | -0.75 | -0.021 | 0.50 | 0.55 | In the reversed string, each element is a position on the string separated from the other  |
