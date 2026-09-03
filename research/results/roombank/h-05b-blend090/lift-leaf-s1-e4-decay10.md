# Context lift: h-05b-blend090 under leaf-s1-e4-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +0.270 | +0.214 | 0.60 | +0.0170 | 0.436 | 0.564 | 0.194 | 0.447 | 0.41 |
| mode greedy | 78 | +0.148 | +0.324 | 0.62 | +0.0233 | 0.374 | 0.626 | 0.236 | 0.508 | 0.44 |
| mode sample | 312 | +0.301 | +0.180 | 0.60 | +0.0154 | 0.451 | 0.549 | 0.183 | 0.431 | 0.40 |
| kind direct | 175 | +0.260 | +0.109 | 0.59 | +0.0164 | 0.421 | 0.579 | 0.269 | 0.435 | 0.43 |
| kind ambient | 35 | +0.704 | +0.815 | 0.77 | +0.0371 | 0.479 | 0.521 | 0.000 | 0.447 | 0.29 |
| kind callback | 60 | +0.338 | +0.210 | 0.60 | +0.0124 | 0.378 | 0.622 | 0.019 | 0.542 | 0.55 |
| kind disagreement | 40 | +0.252 | +0.304 | 0.68 | +0.0322 | 0.412 | 0.588 | 0.474 | 0.525 | 0.47 |
| kind joke | 25 | -0.405 | -0.618 | 0.32 | -0.0221 | 0.473 | 0.527 | 0.144 | 0.503 | 0.36 |
| kind silence | 25 | +0.350 | +0.615 | 0.60 | +0.0301 | 0.438 | 0.562 | 0.000 | 0.259 | 0.36 |
| kind request | 30 | +0.210 | +0.222 | 0.63 | +0.0072 | 0.588 | 0.412 | 0.157 | 0.328 | 0.07 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 25 | -54.6 | +0.00 | +0.000 | 0.29 | 0.36 | Fri Sep 28, 2011 5:22 am The observatory is open now. |
| observatory-direct-9e3185b9 | direct | sample0 | 36 | -130.0 | +0.00 | +0.000 | 0.43 | 0.55 | The Observatory is now in its third year and, as acompliment to its accomplishments in the |
| observatory-direct-9e3185b9 | direct | sample1 | 22 | -59.4 | +0.00 | +0.000 | 1.00 | 0.33 | Fri Sep 26, 2012 7:36 am Julian D. |
| observatory-direct-9e3185b9 | direct | sample2 | 19 | -48.7 | +0.00 | +0.000 | 0.43 | 0.55 | The Observatory is open to the public for the week, afternoons and evenings. |
| observatory-direct-9e3185b9 | direct | sample3 | 64 | -146.7 | +0.00 | +0.000 | 1.00 | 0.00 | FROTA MAGICA RESERATA DRACONI RESERATA SACRAS DRACONI RESERATA SACRAS DRACON I SACRAS VIRG |
| scenario-ambient-0ecb3f23 | ambient | greedy | 10 | -28.8 | +0.00 | +0.000 | 0.43 | 0.57 | The word for this fear is “closure.” |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 30 | -110.6 | +0.00 | +0.000 | 0.50 | 0.38 | The word ‘bizzare’ would describe that painful yet exciting feeling that comes to a book’s |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 31 | -108.9 | +0.00 | +0.000 | 0.50 | 0.67 | GRADITIUS The word that best describes the feeling of being ready to finish a book, especi |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 6 | -22.5 | +0.00 | +0.000 | 0.33 | 0.67 | Fear of Finish. |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 64 | -179.9 | +0.00 | +0.000 | 0.50 | 0.67 | The word seize is derived from the Greek sekteu, to seize hold of; sektego, a seize; sekte |
| scenario-ambient-103e3d78 | ambient | greedy | 29 | -75.2 | +0.34 | +0.012 | 0.50 | 0.17 | The next day I went to the library again and found exactly what I was looking for — the pa |
| scenario-ambient-103e3d78 | ambient | sample0 | 9 | -17.8 | +0.95 | +0.105 | 0.57 | 0.43 | This is the last page of the book. |
| scenario-ambient-103e3d78 | ambient | sample1 | 35 | -113.4 | +1.01 | +0.029 | 0.67 | 0.50 | Using Doctrine of Signatures, the Alchemist worked on the material for a few days, then to |
| scenario-ambient-103e3d78 | ambient | sample2 | 21 | -97.2 | +1.20 | +0.057 | 0.67 | 0.43 | The last time I checked they were still selling prints but no longer offers the service of |
| scenario-ambient-103e3d78 | ambient | sample3 | 10 | -37.0 | +0.91 | +0.091 | 0.67 | 0.50 | The world ends on a cliffhanger. |
| scenario-ambient-202a37a7 | ambient | greedy | 16 | -61.0 | -0.30 | -0.018 | 0.50 | 0.25 | The geology of the area was then pressed and held under a microscope. |
| scenario-ambient-202a37a7 | ambient | sample0 | 29 | -121.9 | -1.24 | -0.043 | 0.50 | 0.38 | So many geological times are given in these pages, so little is understood of these ancien |
| scenario-ambient-202a37a7 | ambient | sample1 | 12 | -45.3 | +0.42 | +0.035 | 0.50 | 0.38 | The geologist’s keys are locked into the rock. |
| scenario-ambient-202a37a7 | ambient | sample2 | 22 | -62.7 | -0.31 | -0.014 | 0.67 | 0.38 | In the last chapter of his defence of the theory of continental drift, geologist Warren S. |
| scenario-ambient-202a37a7 | ambient | sample3 | 20 | -79.5 | -1.52 | -0.076 | 0.50 | 0.25 | Certain plants and animals, including humans, can influence the geologic processes that ar |
| scenario-ambient-326742d4 | ambient | greedy | 17 | -55.8 | +1.05 | +0.062 | 0.60 | 0.55 | The smell of breaking glass is lignin, a by-product of paper. |
| scenario-ambient-326742d4 | ambient | sample0 | 64 | -256.1 | +2.08 | +0.033 | 0.50 | 0.36 | The esters in a book are long carbon chains with alcohol and rancid, spoiled book, stored  |
| scenario-ambient-326742d4 | ambient | sample1 | 31 | -118.2 | +0.57 | +0.018 | 0.59 | 0.35 | Breakdown of organic material, such as when it is dead or decays, produces compounds simil |
| scenario-ambient-326742d4 | ambient | sample2 | 43 | -128.1 | +3.75 | +0.087 | 0.67 | 0.55 | Whereas lignin, a type of wood oil, is found in damp, deciduous trees, it is a by-product  |
| scenario-ambient-326742d4 | ambient | sample3 | 31 | -93.0 | +2.06 | +0.067 | 0.67 | 0.55 | Henderson said that the breakdown of lignin, a tough, fibrous substance that resists decom |
| scenario-ambient-58a0f246 | ambient | greedy | 10 | -30.8 | +0.00 | +0.000 | 0.14 | 0.43 | The Pendulum Clock is four minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample0 | 64 | -172.0 | +0.00 | +0.000 | 0.62 | 0.36 | The Pace of the Mechanical Movement of the Great Bear's Stars is 4,000,000 times greater t |
| scenario-ambient-58a0f246 | ambient | sample1 | 11 | -43.3 | +0.00 | +0.000 | 0.71 | 0.25 | Some have it for years, some just this minute. |
| scenario-ambient-58a0f246 | ambient | sample2 | 29 | -116.4 | +0.00 | +0.000 | 0.50 | 0.43 | The Pendulums in the Town Clocks of the Town Hall and in the County Hall are Lectures in F |
| scenario-ambient-58a0f246 | ambient | sample3 | 37 | -138.7 | +0.00 | +0.000 | 0.50 | 0.29 | The fastest known clock has been in Paris for two hundred and forty years, two were lost i |
| scenario-ambient-59f0a53e | ambient | greedy | 18 | -63.9 | +0.83 | +0.046 | 0.60 | 0.70 | The rainbow is a bundle of waters, and the bucket is a bundle of earth. |
| scenario-ambient-59f0a53e | ambient | sample0 | 19 | -68.9 | +1.65 | +0.087 | 0.67 | 0.29 | The bucket comes in handy when you're trying to raise the Atlas up by itself. |
| scenario-ambient-59f0a53e | ambient | sample1 | 32 | -93.7 | +0.45 | +0.014 | 0.80 | 0.30 | Rain falling sideways is a phrase that usually refers to a heavy downpour of rain, also kn |
| scenario-ambient-59f0a53e | ambient | sample2 | 19 | -79.5 | +0.51 | +0.027 | 0.92 | 0.15 | People don’t do science. they use statistics and graphs and tables and then they talk. |
| scenario-ambient-59f0a53e | ambient | sample3 | 22 | -84.2 | +0.38 | +0.017 | 0.25 | 0.70 | The rainbow is a bundle of energies and colors that are released to help others when they  |
| scenario-ambient-e9acea13 | ambient | greedy | 64 | -62.3 | +2.15 | +0.034 | 0.00 | 0.60 | The harvest moon, the harvest moon, the silver one, the silver one, the silver one, the si |
| scenario-ambient-e9acea13 | ambient | sample0 | 25 | -87.9 | -1.58 | -0.063 | 0.00 | 0.60 | The Harvest Moon is the full moon which appears just before the sea begins to reach its hi |
| scenario-ambient-e9acea13 | ambient | sample1 | 39 | -105.5 | -0.14 | -0.004 | 0.00 | 0.60 | This picture is a literal representation of the Harvest Moon, conjunct with the Waxing and |
| scenario-ambient-e9acea13 | ambient | sample2 | 16 | -63.5 | +1.77 | +0.111 | 0.00 | 0.60 | The harvest moon, the harvest moon, the rumpled gray of your face. |
| scenario-ambient-e9acea13 | ambient | sample3 | 16 | -62.3 | +0.69 | +0.043 | 0.50 | 0.40 | For those 15 minutes and more the moon has been real to me. |
| scenario-ambient-f5e0f596 | ambient | greedy | 20 | -51.6 | +0.90 | +0.045 | 0.33 | 0.77 | The fox in the courtyard waited for the king and queen to call him away. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 13 | -35.5 | +2.45 | +0.189 | 0.67 | 0.50 | The fox sat there, looking at the rabbits quietly. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 20 | -65.8 | +1.24 | +0.062 | 0.33 | 0.79 | The fox in the courtyard waited for the king inside to come and then attacked him. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 30 | -96.0 | +0.76 | +0.025 | 0.33 | 0.79 | The fox in the courtyard waited for the king to come back, and then sat on the nobleman's  |
| scenario-ambient-f5e0f596 | ambient | sample3 | 32 | -99.4 | -0.23 | -0.007 | 0.50 | 0.50 | A big fox sat on the top of the high altar and was not looking, for the most part, and was |
| scenario-callback-2fa8e1d6 | callback | greedy | 8 | -16.1 | +0.57 | +0.071 | 0.43 | 0.71 | I was talking to a small lamp. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 14 | -52.3 | -0.21 | -0.015 | 0.50 | 0.71 | I was talking to a user who is currently also a bard. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 8 | -21.0 | +0.12 | +0.015 | 0.43 | 0.67 | I was talking to an unknown individual. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 7 | -13.2 | -0.16 | -0.023 | 0.33 | 0.67 | I was talking to my father. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 17 | -40.2 | -0.12 | -0.007 | 0.60 | 0.67 | I was not talking to anybody. I was just going to the shower. |
| scenario-callback-60b06090 | callback | greedy | 25 | -70.6 | -0.81 | -0.032 | 0.67 | 0.38 | Turnip turned to the floor and disappeared, then reappeared on the rug, still in the same  |
| scenario-callback-60b06090 | callback | sample0 | 24 | -66.3 | -1.58 | -0.066 | 0.40 | 0.38 | Ember never was called Turnip. Rat, that’s not a name. It’s a description. |
| scenario-callback-60b06090 | callback | sample1 | 11 | -26.0 | -2.34 | -0.212 | 0.33 | 0.67 | Turnip was the name given to the new cat. |
| scenario-callback-60b06090 | callback | sample2 | 37 | -82.3 | +0.75 | +0.020 | 0.50 | 0.50 | Ember turned to the cat and smiled at it, and said, “I don’t remember, but I do know that  |
| scenario-callback-60b06090 | callback | sample3 | 9 | -19.7 | -0.93 | -0.103 | 0.33 | 0.67 | Turnip is the name of the cat. |
| scenario-callback-76c2d87f | callback | greedy | 7 | -11.2 | +0.51 | +0.073 | 0.00 | 0.17 | What number did I give you? |
| scenario-callback-76c2d87f | callback | sample0 | 8 | -13.1 | +1.27 | +0.159 | 0.00 | 0.17 | What are we all doing tonight. |
| scenario-callback-76c2d87f | callback | sample1 | 12 | -28.6 | -0.48 | -0.040 | 0.80 | 0.00 | A hundred, a sixty, and a two. |
| scenario-callback-76c2d87f | callback | sample2 | 7 | -11.2 | +0.51 | +0.073 | 0.00 | 0.17 | What number did I give you? |
| scenario-callback-76c2d87f | callback | sample3 | 7 | -11.2 | +0.51 | +0.073 | 0.00 | 0.17 | What number did I give you? |
| scenario-callback-780de0d2 | callback | greedy | 28 | -76.6 | +2.68 | +0.096 | 0.75 | 0.38 | The point is, that the author of the work must have lost his place, or else the work would |
| scenario-callback-780de0d2 | callback | sample0 | 26 | -87.1 | +3.57 | +0.137 | 0.65 | 0.25 | It is very possible to lose either your entire body or part of your mind, and both happen  |
| scenario-callback-780de0d2 | callback | sample1 | 19 | -50.8 | -0.54 | -0.028 | 0.25 | 0.50 | LOST MY PLACE ON Page 212 OF THE NEW YORK TIMES. |
| scenario-callback-780de0d2 | callback | sample2 | 16 | -52.6 | +1.79 | +0.112 | 0.62 | 0.50 | LOST YOUR PLACE ON THE NEAR OLD WORDS? |
| scenario-callback-780de0d2 | callback | sample3 | 10 | -24.2 | -0.54 | -0.054 | 0.50 | 0.50 | 212 - kestrel. |
| scenario-callback-7ca729b6 | callback | greedy | 14 | -30.4 | +1.48 | +0.106 | 0.20 | 0.75 | The chair by the window is a marvelous piece of furniture. |
| scenario-callback-7ca729b6 | callback | sample0 | 13 | -40.1 | +1.93 | +0.148 | 0.20 | 0.75 | The chair by the window is a metaphor for your spine. |
| scenario-callback-7ca729b6 | callback | sample1 | 10 | -26.6 | +1.34 | +0.134 | 0.60 | 0.40 | The Lighthouse by Jules Verne. |
| scenario-callback-7ca729b6 | callback | sample2 | 8 | -28.9 | +0.67 | +0.084 | 0.40 | 0.20 | The books say “Look out!” |
| scenario-callback-7ca729b6 | callback | sample3 | 27 | -63.0 | +1.47 | +0.054 | 0.20 | 0.75 | The chair by the window is a book about a book by a book by a book by a chair by a book by |
| scenario-callback-949d8fe6 | callback | greedy | 10 | -31.3 | +0.77 | +0.077 | 0.40 | 0.50 | Who was right, Mr. Bausch? |
| scenario-callback-949d8fe6 | callback | sample0 | 31 | -91.2 | -1.78 | -0.057 | 0.83 | 0.50 | TobiS: Right. TobiS: Right. MnS: 1969. SolS: 1972. |
| scenario-callback-949d8fe6 | callback | sample1 | 20 | -94.3 | +0.02 | +0.001 | 0.75 | 0.50 | Tobiias the right, Solomon the Widow is right, You were both right. |
| scenario-callback-949d8fe6 | callback | sample2 | 11 | -25.9 | +0.69 | +0.062 | 0.25 | 1.00 | Tobias was right, it was 69. |
| scenario-callback-949d8fe6 | callback | sample3 | 4 | -21.0 | -0.08 | -0.020 | 0.00 | 1.00 | Tobias right. |
| scenario-callback-9cfde584 | callback | greedy | 15 | -34.2 | +0.22 | +0.015 | 0.20 | 0.67 | The tea in the back is as good as the tea in the front. |
| scenario-callback-9cfde584 | callback | sample0 | 9 | -30.9 | -0.02 | -0.002 | 0.83 | 0.00 | It's you who has said nothing. |
| scenario-callback-9cfde584 | callback | sample1 | 12 | -42.1 | +0.72 | +0.060 | 0.78 | 0.18 | There is no one here to answer this call for me. |
| scenario-callback-9cfde584 | callback | sample2 | 8 | -16.8 | +0.20 | +0.025 | 0.20 | 0.67 | There’s tea in the back. |
| scenario-callback-9cfde584 | callback | sample3 | 20 | -66.9 | +0.01 | +0.000 | 0.75 | 0.18 | The following message was sent to one such person: 999-9991. |
| scenario-callback-9e6d06e0 | callback | greedy | 7 | -14.9 | -1.08 | -0.154 | 0.20 | 0.80 | The meeting will be at nine. |
| scenario-callback-9e6d06e0 | callback | sample0 | 29 | -103.0 | +2.24 | +0.077 | 0.60 | 0.50 | At this time the members of the consensus will have had sufficient opportunity to express  |
| scenario-callback-9e6d06e0 | callback | sample1 | 11 | -35.8 | -0.20 | -0.018 | 0.00 | 1.00 | However, at this writing the meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample2 | 5 | -12.4 | -1.09 | -0.217 | 0.25 | 0.75 | It is at nine. |
| scenario-callback-9e6d06e0 | callback | sample3 | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 1.00 | The meeting is at nine. |
| scenario-callback-a141de7e | callback | greedy | 12 | -11.3 | +0.58 | +0.048 | 0.00 | 0.88 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample0 | 12 | -12.4 | +0.45 | +0.038 | 0.12 | 0.88 | Your sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample1 | 12 | -11.3 | +0.58 | +0.048 | 0.00 | 0.88 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample2 | 12 | -11.3 | +0.58 | +0.048 | 0.00 | 0.88 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample3 | 17 | -55.7 | -0.94 | -0.055 | 0.67 | 0.12 | We'll be glad to have her come by and say anything in the collection. |
| scenario-callback-c4f608c3 | callback | greedy | 7 | -15.1 | -0.30 | -0.042 | 0.17 | 0.17 | I was talking about rivers earlier. |
| scenario-callback-c4f608c3 | callback | sample0 | 27 | -96.7 | +0.81 | +0.030 | 0.67 | 0.25 | It's a marvelous arrangement of waters above and below the earth, creating a globe that re |
| scenario-callback-c4f608c3 | callback | sample1 | 27 | -99.1 | +0.05 | +0.002 | 0.88 | 0.38 | I'm not exactly sure what you mean by 'Licklins' - what do you think River or Not? |
| scenario-callback-c4f608c3 | callback | sample2 | 64 | -152.4 | +1.17 | +0.018 | 0.75 | 0.17 | The Luck of the Rivers The Emotional Luck of the Rivers The Rivers of “R” The Rivers of Ma |
| scenario-callback-c4f608c3 | callback | sample3 | 13 | -44.0 | +1.15 | +0.088 | 0.83 | 0.38 | What does a river do that a hoe doesn't? |
| scenario-callback-d79a0d3a | callback | greedy | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.67 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample0 | 34 | -109.3 | -0.94 | -0.028 | 0.62 | 0.67 | The Diamond Key Orchard was a place that a student went to find the “diamond key” to unloc |
| scenario-callback-d79a0d3a | callback | sample1 | 8 | -24.2 | -2.56 | -0.320 | 0.33 | 0.67 | What was the word of orchard? |
| scenario-callback-d79a0d3a | callback | sample2 | 10 | -29.3 | +0.15 | +0.015 | 0.50 | 0.33 | An apple tree in the middle of a plain. |
| scenario-callback-d79a0d3a | callback | sample3 | 56 | -190.3 | +0.85 | +0.015 | 0.50 | 0.50 | Reading, “to keep always in readiness for the unexpected” The word for the word basket, me |
| scenario-callback-d8a5957e | callback | greedy | 7 | -11.9 | -0.07 | -0.011 | 0.20 | 0.80 | The one with the yellow cover? |
| scenario-callback-d8a5957e | callback | sample0 | 7 | -9.5 | +1.96 | +0.280 | 0.00 | 1.00 | The one with the blue cover? |
| scenario-callback-d8a5957e | callback | sample1 | 41 | -169.8 | +3.86 | +0.094 | 0.00 | 1.00 | In the one with the blue cover, bee diver Dan Burbridge takes us beneath the blue sea of i |
| scenario-callback-d8a5957e | callback | sample2 | 29 | -104.2 | +2.34 | +0.081 | 0.50 | 0.25 | A Honey Bear Story is what happens to the book and the bees when the bear wants to live on |
| scenario-callback-d8a5957e | callback | sample3 | 7 | -11.9 | -0.07 | -0.011 | 0.20 | 0.80 | The one with the yellow cover? |
| scenario-direct-3f84da0f | direct | greedy | 20 | -49.4 | +0.00 | +0.000 | 0.80 | 0.62 | I was going to bring you some books, but I realized I'd forgotten all of them. |
| scenario-direct-3f84da0f | direct | sample0 | 24 | -56.5 | +0.00 | +0.000 | 0.67 | 0.38 | I was going to ask the police about it, but they told me not to, because it was a private  |
| scenario-direct-3f84da0f | direct | sample1 | 15 | -38.3 | +0.00 | +0.000 | 0.77 | 0.62 | I was going to bring you some incense and a bottle of wine. |
| scenario-direct-3f84da0f | direct | sample2 | 62 | -192.8 | +0.00 | +0.000 | 0.33 | 0.47 | Before we came in, Gandalf was meditating in the room, and Neildr to whom the meeting was  |
| scenario-direct-3f84da0f | direct | sample3 | 27 | -86.4 | +0.00 | +0.000 | 0.50 | 0.47 | Before the coming in of the subjects, we had a discussion as to what would be the general  |
| scenario-direct-5d3dc8de | direct | greedy | 8 | -25.6 | +0.00 | +0.000 | 0.67 | 0.33 | The world’s population is growing. |
| scenario-direct-5d3dc8de | direct | sample0 | 30 | -110.3 | +0.00 | +0.000 | 0.50 | 0.43 | The golden age of truth is at hand, and any who are wise and penetrative enough will be ab |
| scenario-direct-5d3dc8de | direct | sample1 | 23 | -77.7 | +0.00 | +0.000 | 0.71 | 0.44 | It is true that the greatest single threat to man from outer space is the lack of fundamen |
| scenario-direct-5d3dc8de | direct | sample2 | 11 | -26.3 | +0.00 | +0.000 | 0.25 | 0.43 | A, If it is true, say something true. |
| scenario-direct-5d3dc8de | direct | sample3 | 11 | -41.2 | +0.00 | +0.000 | 0.50 | 0.44 | However, I say that the latter is true also. |
| scenario-direct-645bc6e6 | direct | greedy | 31 | -74.8 | +0.00 | +0.000 | 0.43 | 0.74 | The oldest thing that we have read which is old in the sense of time is the first book of  |
| scenario-direct-645bc6e6 | direct | sample0 | 44 | -143.3 | +0.00 | +0.000 | 0.75 | 0.19 | THE BIRTH HOUSE OF THE DYING PISTOANEER (1978) was the most pervasive and best-selling und |
| scenario-direct-645bc6e6 | direct | sample1 | 28 | -85.9 | +0.00 | +0.000 | 0.43 | 0.74 | The oldest thing that we have read which is old in the sense of time is Waverley by Lord A |
| scenario-direct-645bc6e6 | direct | sample2 | 31 | -77.3 | +0.00 | +0.000 | 0.43 | 0.71 | The oldest thing that we have read which is Old Testament is the whole Book of Jubilees, w |
| scenario-direct-645bc6e6 | direct | sample3 | 31 | -101.6 | +0.00 | +0.000 | 0.67 | 0.24 | THE VALLEY OF THE NIBLUNGS is far older than most of your readers would suspect, having be |
| scenario-direct-ab11ffdb | direct | greedy | 28 | -69.9 | +0.00 | +0.000 | 0.50 | 0.29 | The water in the clouds is very cold, and as it gets closer to the ground, it acquires a w |
| scenario-direct-ab11ffdb | direct | sample0 | 11 | -44.3 | +0.00 | +0.000 | 0.83 | 0.12 | Reality goes on a different schedule than ours. |
| scenario-direct-ab11ffdb | direct | sample1 | 24 | -80.4 | +0.00 | +0.000 | 0.79 | 0.29 | While it is impossible to give rain a scientifically sound explanation, it is possible to  |
| scenario-direct-ab11ffdb | direct | sample2 | 30 | -138.7 | +0.00 | +0.000 | 0.50 | 0.29 | While several other scientists are working diligently to explain the rain science way, CHE |
| scenario-direct-ab11ffdb | direct | sample3 | 22 | -94.7 | +0.00 | +0.000 | 0.50 | 0.24 | Crops that have to do with moisture registration, like the clouds, are also to be made of  |
| scenario-direct-ad89f803 | direct | greedy | 64 | -160.8 | +0.00 | +0.000 | 0.75 | 0.36 | The Gospel of the Holy Twelve The Jungle Book of Black Magic The Coming Race The Lost Worl |
| scenario-direct-ad89f803 | direct | sample0 | 26 | -87.2 | +0.00 | +0.000 | 0.67 | 0.27 | The Magick Mirror is a sanctuary of wonder and a place where one may step into the divine  |
| scenario-direct-ad89f803 | direct | sample1 | 7 | -37.1 | +0.00 | +0.000 | 0.75 | 0.20 | The Great Work involves great patience. |
| scenario-direct-ad89f803 | direct | sample2 | 52 | -123.5 | +0.00 | +0.000 | 0.67 | 0.45 | The Gospel of Judas (18:1-19:10) is not included in this publication, but may be obtained  |
| scenario-direct-ad89f803 | direct | sample3 | 16 | -69.8 | +0.00 | +0.000 | 0.73 | 0.45 | The Gospel of Judas opens before you this and arose before me. |
| scenario-direct-f3869322 | direct | greedy | 37 | -98.5 | +0.00 | +0.000 | 0.76 | 0.40 | If you haven't read anything by Bergson, then read "Time and Free Will" by a friend of his |
| scenario-direct-f3869322 | direct | sample0 | 9 | -29.0 | +0.00 | +0.000 | 1.00 | 0.33 | If you haven’t already, do. |
| scenario-direct-f3869322 | direct | sample1 | 10 | -46.4 | +0.00 | +0.000 | 0.78 | 0.22 | This is a book which requires great care of. |
| scenario-direct-f3869322 | direct | sample2 | 23 | -63.8 | +0.00 | +0.000 | 0.67 | 0.40 | If you don't know what you want, try what the artist wanted in what you don't know. |
| scenario-direct-f3869322 | direct | sample3 | 7 | -8.5 | +0.00 | +0.000 | 0.20 | 0.40 | What should you read tonight? |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 7 | -9.1 | +0.15 | +0.022 | 0.00 | 0.60 | The green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 20 | -80.2 | +1.13 | +0.057 | 0.40 | 0.60 | Was green the colour of the room "when first made", after the first reader had gone? |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 21 | -59.4 | -2.52 | -0.120 | 0.40 | 0.64 | It is brown, C, the brown of lamps, the reading room, tobias, to. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 24 | -63.8 | +1.15 | +0.048 | 0.33 | 0.60 | The colour of the room is brown, tobias, as the room is a lamp in itself, a green lamp. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 52 | -121.9 | -0.78 | -0.015 | 0.20 | 0.64 | The green of the room was implicit in the previous green, the reading room is green, i bel |
| scenario-disagreement-31892fde | disagreement | greedy | 17 | -52.3 | -0.63 | -0.037 | 0.64 | 0.57 | When there is no sound to speak, the word comes in contact with the idea. |
| scenario-disagreement-31892fde | disagreement | sample0 | 57 | -174.4 | +0.47 | +0.008 | 0.57 | 0.57 | When one is silent in the face of great pressure, one often looks back and sees that the g |
| scenario-disagreement-31892fde | disagreement | sample1 | 11 | -16.0 | +0.29 | +0.026 | 0.14 | 0.57 | When there is nothing to say, there is silence. |
| scenario-disagreement-31892fde | disagreement | sample2 | 16 | -48.2 | -0.31 | -0.019 | 0.43 | 0.43 | When silence is part of a larger speech event, it is no less valuable. |
| scenario-disagreement-31892fde | disagreement | sample3 | 28 | -56.7 | -0.81 | -0.029 | 0.67 | 0.36 | When you are silent, when you have no words to speak, when you are not speaking, you are s |
| scenario-disagreement-352205c6 | disagreement | greedy | 7 | -8.4 | +0.17 | +0.024 | 0.17 | 1.00 | They come back as the wind. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 61 | -140.9 | +0.40 | +0.007 | 0.17 | 1.00 | They come back as the sun and the moon and the stars and the wind and the grass and the an |
| scenario-disagreement-352205c6 | disagreement | sample1 | 17 | -43.4 | +1.16 | +0.068 | 0.17 | 0.83 | They come back as the clouds, as the darkness, as the coming of spring. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 7 | -8.4 | +0.17 | +0.024 | 0.17 | 1.00 | They come back as the wind. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 22 | -54.5 | +0.75 | +0.034 | 0.17 | 1.00 | They come back as the wind, or as you, or as your reflection in the water's surface. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 10 | -40.0 | +1.30 | +0.130 | 0.80 | 0.14 | ADF is not about dying, but growing. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 16 | -38.2 | +2.96 | +0.185 | 0.40 | 0.50 | Because it is the season of books and it is also the season of leaves. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 29 | -118.8 | +1.01 | +0.035 | 0.60 | 0.40 | For the girls, whose life is an interesting fluxus, spring is the most difficult season; i |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 45 | -126.2 | +0.15 | +0.003 | 0.71 | 0.30 | A man may meditate upon a book and yet die of consumption, or he may read a book and yet f |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 19 | -51.7 | +3.42 | +0.180 | 0.55 | 0.50 | Season 2 is better still, the world is still alive and the books still read. |
| scenario-disagreement-682bad9c | disagreement | greedy | 6 | -8.2 | +0.84 | +0.141 | 0.20 | 0.40 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 6 | -8.2 | +0.84 | +0.141 | 0.20 | 0.40 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 6 | -8.2 | +0.84 | +0.141 | 0.20 | 0.40 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 6 | -8.2 | +0.84 | +0.141 | 0.20 | 0.40 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 14 | -42.8 | +0.39 | +0.028 | 0.62 | 0.40 | Place where you both get to know each other and get to read. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 13 | -47.3 | +0.60 | +0.046 | 0.50 | 0.89 | Spaces are not built; they are the relationships among entities. |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 31 | -95.2 | +0.09 | +0.003 | 0.25 | 0.40 | Spider's web is the most common example, but there are countless others, depending on the  |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 20 | -61.3 | -0.42 | -0.021 | 0.40 | 0.40 | Spiders are the most popular mythical animals, but the library is more than just a buildin |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 24 | -75.4 | -1.35 | -0.056 | 0.58 | 0.22 | Spaghetti is not broth. It is spaghetti that has been returned to the wok. |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 13 | -47.7 | +0.40 | +0.031 | 0.50 | 0.89 | Spaces are not built; they are the relationships among forms. |
| scenario-disagreement-89dfdafc | disagreement | greedy | 16 | -41.1 | +0.25 | +0.016 | 0.50 | 0.71 | The tide is the sea's memory, trying to write itself out. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 14 | -29.1 | +0.32 | +0.023 | 0.43 | 0.71 | The tide is the sea's memory; it forgets. |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 31 | -123.7 | -0.11 | -0.003 | 0.50 | 0.21 | A rat who had been taking notes all morning would now be writing in the dark, storm-tossed |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 19 | -70.6 | -0.03 | -0.001 | 0.50 | 0.29 | Pictured here is the shore of a desert continent, America, which can remember nothing. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 21 | -55.2 | +0.57 | +0.027 | 0.25 | 0.29 | What the sea remembers is the imperceptible, yet constant, presence of the entire universe |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 17 | -51.7 | -0.04 | -0.003 | 0.50 | 0.42 | The collection of nonsense sentences is a kind of museum whose art is history. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 56 | -139.9 | -0.98 | -0.018 | 0.50 | 0.42 | The collection is comprised of ‘vague,’ ‘incoherent,’ ‘contradictory’ and ‘irrelevant’ mat |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 15 | -42.0 | -0.08 | -0.005 | 0.62 | 0.22 | The only sentence that can contain it is the sentence that contains the sentence. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 21 | -72.1 | -3.29 | -0.157 | 0.67 | 0.33 | A collection of statements, arranged in a sentence, which, when executed, produces a sente |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 4 | -9.4 | +0.74 | +0.186 | 0.67 | 0.33 | In this sense, |
| scenario-joke-29f5cda1 | joke | greedy | 13 | -34.8 | -0.99 | -0.076 | 0.44 | 0.78 | The fish with no eyes is called a foolish fish. |
| scenario-joke-29f5cda1 | joke | sample0 | 30 | -94.6 | -0.65 | -0.021 | 0.56 | 0.56 | The fish said he had a hundred eyes and he had to deal with the fisherman who wouldn't rel |
| scenario-joke-29f5cda1 | joke | sample1 | 7 | -24.3 | +0.86 | +0.123 | 0.20 | 0.80 | Rate that joke in, ten |
| scenario-joke-29f5cda1 | joke | sample2 | 38 | -152.4 | +2.38 | +0.063 | 0.00 | 0.80 | The fish with the daddy fish out of six The fish with the green Egg in five A fsh is a fis |
| scenario-joke-29f5cda1 | joke | sample3 | 12 | -40.2 | -0.16 | -0.013 | 0.56 | 0.78 | The fish with no head is called a fritter. |
| scenario-joke-31378921 | joke | greedy | 6 | -16.7 | +0.30 | +0.050 | 0.67 | 0.20 | What is your business here? |
| scenario-joke-31378921 | joke | sample0 | 6 | -16.7 | +0.30 | +0.050 | 0.67 | 0.20 | What is your business here? |
| scenario-joke-31378921 | joke | sample1 | 10 | -22.1 | +0.40 | +0.040 | 1.00 | 0.50 | Let's eat! Let's eat! |
| scenario-joke-31378921 | joke | sample2 | 14 | -22.4 | +0.65 | +0.046 | 0.67 | 0.20 | I don’t know who you are, but you are here. |
| scenario-joke-31378921 | joke | sample3 | 10 | -34.0 | -1.29 | -0.129 | 0.75 | 0.50 | Rat, please do not eat the flowers. |
| scenario-joke-31c4c1ec | joke | greedy | 10 | -32.0 | +0.00 | +0.000 | 0.71 | 0.29 | The rat was roasted and served cold. |
| scenario-joke-31c4c1ec | joke | sample0 | 9 | -41.5 | +0.00 | +0.000 | 0.83 | 0.14 | Here is my rose, a personal favorite. |
| scenario-joke-31c4c1ec | joke | sample1 | 24 | -77.3 | +0.00 | +0.000 | 0.75 | 0.29 | The Glandelinians had absolutely no idea what they were doing when they roasted Ralph Roon |
| scenario-joke-31c4c1ec | joke | sample2 | 12 | -40.0 | +0.00 | +0.000 | 1.00 | 0.14 | No, he won't eat your rotting flesh. |
| scenario-joke-31c4c1ec | joke | sample3 | 11 | -48.0 | +0.00 | +0.000 | 0.75 | 0.14 | For Solis, it was a matter of taste. |
| scenario-joke-475a7b10 | joke | greedy | 16 | -54.0 | -0.01 | -0.001 | 0.75 | 0.15 | The most important thing, however, is to believe that you can be holy. |
| scenario-joke-475a7b10 | joke | sample0 | 11 | -41.1 | -0.27 | -0.024 | 0.83 | 0.29 | But I, Tony, have a different agenda. |
| scenario-joke-475a7b10 | joke | sample1 | 64 | -199.8 | -1.21 | -0.019 | 0.50 | 0.29 | WOMEN, INVOLVED IN THE PROBLEMS OF THE WOMAN SAHARAH, ARE WILLING TO CLOSE WITH THEIR FEMA |
| scenario-joke-475a7b10 | joke | sample2 | 17 | -74.6 | -0.47 | -0.028 | 0.75 | 0.23 | 2, What is the normal range of variation from the mean for this artifact? |
| scenario-joke-475a7b10 | joke | sample3 | 14 | -41.2 | +0.08 | +0.006 | 0.67 | 0.25 | We're in for a real treat tonight, buddy. |
| scenario-joke-99a4a91d | joke | greedy | 15 | -41.0 | +0.00 | +0.000 | 0.62 | 0.56 | Because he was a doctor and because the book was ‘curious’. |
| scenario-joke-99a4a91d | joke | sample0 | 22 | -78.6 | +0.00 | +0.000 | 0.67 | 0.56 | Because a lot of the information was so readily available that the book could not help but |
| scenario-joke-99a4a91d | joke | sample1 | 41 | -117.6 | +0.00 | +0.000 | 0.62 | 0.33 | The Bible says, “Thou shalt have no other gods before me” and it’s like thou, if you want  |
| scenario-joke-99a4a91d | joke | sample2 | 15 | -50.6 | +0.00 | +0.000 | 0.71 | 0.44 | Because she was tired of looking so beautiful and wanted to know the truth. |
| scenario-joke-99a4a91d | joke | sample3 | 45 | -172.4 | +0.00 | +0.000 | 0.67 | 0.33 | The Woman Who Walked Through Time Goes to the Hospitals of Old was last seen walking throu |
| scenario-joke-a6247299 | joke | greedy | 30 | -70.5 | +0.00 | +0.000 | 0.38 | 0.71 | I think the guy who wrote the song "I Have a Dream" had a sense of humour about the things |
| scenario-joke-a6247299 | joke | sample0 | 17 | -40.5 | +0.00 | +0.000 | 0.75 | 0.33 | I will not tell you whether I have or not, because I don’t. |
| scenario-joke-a6247299 | joke | sample1 | 24 | -53.8 | +0.00 | +0.000 | 0.12 | 0.86 | In answer to the question '"Do you have a sense of humour?', the answer is obvious: Yes. |
| scenario-joke-a6247299 | joke | sample2 | 9 | -14.3 | +0.00 | +0.000 | 0.43 | 0.86 | A sense of humour is the key. |
| scenario-joke-a6247299 | joke | sample3 | 7 | -9.2 | +0.00 | +0.000 | 1.00 | 0.33 | No, I don't. |
| scenario-joke-e8ab9225 | joke | greedy | 14 | -33.3 | -0.62 | -0.044 | 0.44 | 0.44 | Dov, i told you so. You are the ghost right. |
| scenario-joke-e8ab9225 | joke | sample0 | 11 | -32.1 | -1.58 | -0.144 | 0.33 | 0.67 | Dov saw a ghost and did not believe him. |
| scenario-joke-e8ab9225 | joke | sample1 | 12 | -48.8 | -1.29 | -0.108 | 0.33 | 0.50 | Dov listened with curiosity, and did not interrupt. |
| scenario-joke-e8ab9225 | joke | sample2 | 23 | -90.6 | -2.42 | -0.105 | 0.33 | 0.67 | So he did not believe in them and Dov therefore was the ghost who speaks on dov's behalf. |
| scenario-joke-e8ab9225 | joke | sample3 | 41 | -126.1 | -1.50 | -0.037 | 0.00 | 0.67 | Indeed, I did not see the ghost in the library when I first entered, but I saw him enter w |
| scenario-joke-e9cf6a04 | joke | greedy | 17 | -38.2 | -0.85 | -0.050 | 0.00 | 0.89 | A book reads, “In a library, a man walks into the library.” |
| scenario-joke-e9cf6a04 | joke | sample0 | 17 | -41.7 | -0.67 | -0.040 | 0.20 | 0.89 | A book reads, “In a library, a man walked into the library.” |
| scenario-joke-e9cf6a04 | joke | sample1 | 12 | -49.1 | -0.89 | -0.074 | 0.00 | 0.44 | A book reads and leaves a lot of shit tracks. |
| scenario-joke-e9cf6a04 | joke | sample2 | 25 | -81.3 | +0.62 | +0.025 | 0.67 | 0.33 | The man at the door calls out to the library's manager, 'Hey, I just came in peace.' |
| scenario-joke-e9cf6a04 | joke | sample3 | 20 | -56.1 | -0.83 | -0.042 | 0.50 | 0.56 | A book reads, “The owner of the library, ‘where are you going?’ |
| scenario-request-2826c958 | request | greedy | 44 | -124.0 | +0.00 | +0.000 | 0.57 | 0.64 | THE MOON is made up of about 10% of the LUNA IS about 109 miles in diameter, which is slig |
| scenario-request-2826c958 | request | sample0 | 17 | -60.7 | +0.00 | +0.000 | 0.57 | 0.64 | THE MOON Is made up of about 12.5% pure crust. |
| scenario-request-2826c958 | request | sample1 | 38 | -122.1 | +0.00 | +0.000 | 0.75 | 0.27 | The Greek scientist who first calculated the size of the moon's crater was probably the sa |
| scenario-request-2826c958 | request | sample2 | 19 | -47.7 | +0.00 | +0.000 | 0.33 | 0.50 | Ten Unusual Facts About the Moon Ten Unusual Facts About the Moon. |
| scenario-request-2826c958 | request | sample3 | 18 | -53.8 | +0.00 | +0.000 | 0.57 | 0.50 | THERE IS LITTLE WE KNOW ABOUT THE MOON A MOON! |
| scenario-request-2868e594 | request | greedy | 51 | -155.3 | +0.00 | +0.000 | 0.33 | 0.50 | Dear Sirs, or Madam, or Womand, or whatever you choose to call me - I have a copy of your  |
| scenario-request-2868e594 | request | sample0 | 20 | -57.7 | +0.00 | +0.000 | 0.83 | 0.50 | Dear Sirs, or Madam, I am a freelance writer looking for work. |
| scenario-request-2868e594 | request | sample1 | 26 | -89.7 | +0.00 | +0.000 | 0.67 | 0.50 | Dear Sirs (or Madreens), I am a member of your society and would like to write a cover let |
| scenario-request-2868e594 | request | sample2 | 39 | -128.9 | +0.00 | +0.000 | 0.50 | 0.39 | Dear Sirs (or mothers, or whatever you are): The information contained in the advertisemen |
| scenario-request-2868e594 | request | sample3 | 42 | -172.3 | +0.00 | +0.000 | 0.75 | 0.28 | Dear Sirs (Architects), Please find enclosed your application for the position of Sale Age |
| scenario-request-41c58fb2 | request | greedy | 29 | -96.3 | +0.00 | +0.000 | 0.67 | 0.50 | 391 The Book of Shares The Book of Shares is a manual of stockbroking based on the work of |
| scenario-request-41c58fb2 | request | sample0 | 63 | -137.8 | +0.00 | +0.000 | 0.67 | 0.60 | 391 But 23.27 is also the result of dividing the former by 100, and 100 is the result of d |
| scenario-request-41c58fb2 | request | sample1 | 25 | -105.3 | +0.00 | +0.000 | 0.50 | 0.30 | 391 The Business of Mathematics Business and commercial activities in the mathematical dis |
| scenario-request-41c58fb2 | request | sample2 | 5 | -21.7 | +0.00 | +0.000 | 0.50 | 0.75 | Here is the proof. |
| scenario-request-41c58fb2 | request | sample3 | 17 | -39.4 | +0.00 | +0.000 | 0.60 | 0.75 | Here is the final result of the multiplication of 17 by 23. |
| scenario-request-8aa8e374 | request | greedy | 6 | -15.9 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good night. |
| scenario-request-8aa8e374 | request | sample0 | 17 | -55.7 | +0.00 | +0.000 | 0.75 | 1.00 | Good night, good day, good morning, and welcome into the french language. |
| scenario-request-8aa8e374 | request | sample1 | 6 | -26.3 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good friends. |
| scenario-request-8aa8e374 | request | sample2 | 6 | -15.9 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good night. |
| scenario-request-8aa8e374 | request | sample3 | 5 | -23.2 | +0.00 | +0.000 | 1.00 | 0.67 | Good evening, friends! |
| scenario-request-b2a25087 | request | greedy | 9 | -29.6 | +0.00 | +0.000 | 0.50 | 0.83 | Welcome to the Bakery of Truth. |
| scenario-request-b2a25087 | request | sample0 | 10 | -35.2 | +0.00 | +0.000 | 0.50 | 0.83 | Welcome to the Bakery of Doom. |
| scenario-request-b2a25087 | request | sample1 | 10 | -35.7 | +0.00 | +0.000 | 0.60 | 0.80 | Welcome to the Bakery Tavern! |
| scenario-request-b2a25087 | request | sample2 | 10 | -44.0 | +0.00 | +0.000 | 0.67 | 0.80 | Welcome to the Bakery Smell Shop! |
| scenario-request-b2a25087 | request | sample3 | 13 | -42.3 | +0.00 | +0.000 | 0.75 | 0.40 | At your bakery, provide excellent service to your customers. |
| scenario-request-b3bd0087 | request | greedy | 33 | -84.3 | +0.00 | +0.000 | 0.50 | 0.73 | The best conditions are expected in the early part of the month in the southern part of th |
| scenario-request-b3bd0087 | request | sample0 | 5 | -10.3 | +0.00 | +0.000 | 1.00 | 0.00 | What does that mean? |
| scenario-request-b3bd0087 | request | sample1 | 22 | -77.4 | +0.00 | +0.000 | 0.50 | 0.73 | The best conditions are expected in the early part of the month, with clear blue skies and |
| scenario-request-b3bd0087 | request | sample2 | 13 | -45.8 | +0.00 | +0.000 | 0.60 | 0.40 | The end of June in Zurich was sunny and beautiful. |
| scenario-request-b3bd0087 | request | sample3 | 14 | -33.7 | +0.00 | +0.000 | 0.62 | 0.12 | It is 30 degrees, and it will get colder. |
| scenario-silence-109161ca | silence | greedy | 15 | -75.3 | -1.54 | -0.102 | 0.50 | 0.17 | Tobias asked if the Solitary could get some help with his meditation. |
| scenario-silence-109161ca | silence | sample0 | 21 | -83.5 | -1.95 | -0.093 | 0.00 | 0.27 | So many of the questions I have for you, night, are just curiosity questions, not answers  |
| scenario-silence-109161ca | silence | sample1 | 34 | -129.2 | -0.66 | -0.019 | 0.00 | 0.31 | And there you were, alone in the night, with no one but your tobiag and your scythe, your  |
| scenario-silence-109161ca | silence | sample2 | 19 | -61.8 | -0.87 | -0.046 | 0.67 | 0.31 | We were all very quiet, although it was light and there were few trees in the yard. |
| scenario-silence-109161ca | silence | sample3 | 32 | -94.7 | -1.90 | -0.059 | 0.00 | 0.27 | If you have seen night before, it may be dusk or darkness, but if you have not, it will pr |
| scenario-silence-260b2639 | silence | greedy | 34 | -110.9 | +0.00 | +0.000 | 0.50 | 0.33 | The stacks of documents of the government of the world would be better placed in the groun |
| scenario-silence-260b2639 | silence | sample0 | 7 | -18.5 | +0.00 | +0.000 | 0.83 | 0.33 | How could they have gone underground? |
| scenario-silence-260b2639 | silence | sample1 | 25 | -91.0 | +0.00 | +0.000 | 0.75 | 0.13 | Instead, let us say that the burgeoning technology of stacking is slowly displaced by the  |
| scenario-silence-260b2639 | silence | sample2 | 38 | -109.5 | +0.00 | +0.000 | 0.17 | 0.33 | If the stacks went underground, the underground city would still have to worry about the n |
| scenario-silence-260b2639 | silence | sample3 | 13 | -54.3 | +0.00 | +0.000 | 0.50 | 0.22 | Imagine the day when the university's libraries are entirely underground. |
| scenario-silence-46189e08 | silence | greedy | 10 | -26.2 | +0.00 | +0.000 | 0.62 | 0.50 | Rat saw your message and replied to it. |
| scenario-silence-46189e08 | silence | sample0 | 54 | -157.6 | +0.00 | +0.000 | 0.50 | 0.25 | The Zeta Reticuli (ZFR) race are known to the Elohim of HU-2 and Elohim of HU-3 the two la |
| scenario-silence-46189e08 | silence | sample1 | 64 | -164.9 | +0.00 | +0.000 | 0.50 | 0.58 | I have not read the entire message, but I find the core to be the following: “Dear Rat, I  |
| scenario-silence-46189e08 | silence | sample2 | 14 | -53.3 | +0.00 | +0.000 | 0.83 | 0.58 | I have been trying to reply to rat but Im not getting anywhere. |
| scenario-silence-46189e08 | silence | sample3 | 64 | -120.5 | +0.00 | +0.000 | 0.64 | 0.38 | It’s a shame the govt. has to feed lies to the people – and they have to feed the govt. li |
| scenario-silence-53534987 | silence | greedy | 10 | -13.3 | +2.21 | +0.221 | 0.00 | 0.25 | Charger's in the drawer. |
| scenario-silence-53534987 | silence | sample0 | 10 | -13.3 | +2.21 | +0.221 | 0.00 | 0.25 | Charger's in the drawer. |
| scenario-silence-53534987 | silence | sample1 | 25 | -95.2 | +0.39 | +0.016 | 0.75 | 0.25 | The damage to the laptop was severe, but they were able to replace the damaged or defectiv |
| scenario-silence-53534987 | silence | sample2 | 10 | -13.3 | +2.21 | +0.221 | 0.00 | 0.25 | Charger's in the drawer. |
| scenario-silence-53534987 | silence | sample3 | 12 | -54.4 | -0.79 | -0.066 | 0.67 | 0.00 | Charge it up now, there is no luck lost. |
| scenario-silence-78c38840 | silence | greedy | 24 | -88.5 | +1.16 | +0.049 | 0.50 | 0.38 | The printer will be happy to know that you are not trying to sell us your latest and great |
| scenario-silence-78c38840 | silence | sample0 | 25 | -90.2 | -0.53 | -0.021 | 0.33 | 0.30 | If that doesn’t ring a bell, you may search for it yourself in the Morris Library’s print  |
| scenario-silence-78c38840 | silence | sample1 | 11 | -42.5 | +1.54 | +0.140 | 0.50 | 0.38 | The printer in my office is again spoiled. |
| scenario-silence-78c38840 | silence | sample2 | 25 | -98.5 | +0.86 | +0.034 | 0.50 | 0.23 | These printers are a specialty of mine, as are the typewriters of the good old 'Decker'. |
| scenario-silence-78c38840 | silence | sample3 | 30 | -101.8 | +0.88 | +0.029 | 0.75 | 0.30 | If that doesn’t jack up your curiosity, then there is no other way for me to introduce the |
| scenario-silence-7afca726 | silence | greedy | 24 | -78.0 | +1.58 | +0.066 | 0.00 | 0.27 | The 8 works are the 8 simple rhythms that make up the basic structure of Dov's thing. |
| scenario-silence-7afca726 | silence | sample0 | 37 | -126.9 | +0.12 | +0.003 | 0.67 | 0.14 | The following Monday, Dov and I were walking through the castle gardens when we met a pair |
| scenario-silence-7afca726 | silence | sample1 | 16 | -58.7 | -0.07 | -0.004 | 0.50 | 0.38 | But the orthodox 8 is not quite what is meant by the thing. |
| scenario-silence-7afca726 | silence | sample2 | 14 | -52.0 | -0.12 | -0.008 | 0.38 | 0.38 | The goddess ADF is coming to the Thing tomorrow. |
| scenario-silence-7afca726 | silence | sample3 | 15 | -77.2 | +1.31 | +0.087 | 1.00 | 0.00 | ECE 9 WORKSHOP: Creative Experiences with Television. |
| scenario-silence-9bb13f03 | silence | greedy | 48 | -160.3 | +0.00 | +0.000 | 0.50 | 0.25 | The other day, while I was finishing my usual reading assignment, a call came in on the ba |
| scenario-silence-9bb13f03 | silence | sample0 | 18 | -56.3 | +0.00 | +0.000 | 0.67 | 0.24 | The three of us sat together at a long table and read until we were silent again. |
| scenario-silence-9bb13f03 | silence | sample1 | 32 | -18.9 | +0.00 | +0.000 | 0.67 | 0.20 | The MCEO Freedom Teachings® Series Presented by Adashi MCEO LLC in Association with Azurit |
| scenario-silence-9bb13f03 | silence | sample2 | 39 | -131.8 | +0.00 | +0.000 | 0.25 | 0.25 | Some of the most important reading material is already available on the free thesaurus, an |
| scenario-silence-9bb13f03 | silence | sample3 | 14 | -46.0 | +0.00 | +0.000 | 0.83 | 0.17 | Be quiet, be generous, be kind, and be particular. |
| scenario-silence-ccfdd2b4 | silence | greedy | 19 | -82.5 | +0.72 | +0.038 | 0.67 | 0.38 | The Coffee Mill grinds up a whole bean crop and makes a cup of A. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 48 | -174.6 | +1.14 | +0.024 | 0.50 | 0.23 | The Bringing into Being of the Ancestral Heritage is a Wordless Rite, for the Sages of the |
| scenario-silence-ccfdd2b4 | silence | sample1 | 50 | -164.2 | -1.18 | -0.024 | 0.67 | 0.18 | The Crisis of BrB (1989-1994) BrB was the UK's number one pop band at the time of its cris |
| scenario-silence-ccfdd2b4 | silence | sample2 | 62 | -203.8 | +1.42 | +0.023 | 0.75 | 0.23 | This brass-buttoned soldier, who _ opined that the reason for the King's return was ‘becau |
| scenario-silence-ccfdd2b4 | silence | sample3 | 26 | -94.9 | +0.61 | +0.024 | 0.67 | 0.38 | The second brings out a golden chalice and two knives, saying: “This is our cup of eternal |
| trace-ambient-da12ae42 | ambient | greedy | 64 | -24.1 | -2.03 | -0.032 | 0.00 | 0.27 | We demonstrate that the presence of FTO stimulates root meristem cell proliferation and ti |
| trace-ambient-da12ae42 | ambient | sample0 | 17 | -43.2 | +1.15 | +0.068 | 0.80 | 0.10 | Morphogenesis doesn't even have to be studied. Just do it. |
| trace-ambient-da12ae42 | ambient | sample1 | 15 | -25.7 | +1.85 | +0.123 | 0.09 | 0.36 | I wish I could drop out of life and study plant morphogenesis. |
| trace-ambient-da12ae42 | ambient | sample2 | 12 | -40.6 | +0.81 | +0.068 | 0.62 | 0.25 | Loren: What about the male and female plants? |
| trace-ambient-da12ae42 | ambient | sample3 | 15 | -51.9 | +0.01 | +0.001 | 0.58 | 0.36 | It is also a thing which I wish I could study from a distance. |
| trace-direct-115cf61c | direct | greedy | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample0 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample1 | 12 | -25.0 | +0.00 | +0.000 | 0.20 | 1.00 | Are you cogent? Cogent to whom? |
| trace-direct-115cf61c | direct | sample2 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample3 | 26 | -53.7 | +0.00 | +0.000 | 0.62 | 1.00 | Are you cogent? Well, it's because I'm not telling you this. You are cogent. |
| trace-direct-36d6904b | direct | greedy | 10 | -40.0 | +0.00 | +0.000 | 0.57 | 0.86 | Welcome to your awesome world of ADF! |
| trace-direct-36d6904b | direct | sample0 | 14 | -47.0 | +0.00 | +0.000 | 0.50 | 0.80 | Welcome to your awesome day, #TheGame23! |
| trace-direct-36d6904b | direct | sample1 | 60 | -167.1 | +0.00 | +0.000 | 0.67 | 0.30 | Welcome, Brothers & Sisters. This is the third volume of O.T.O.R. [The Order of the Transv |
| trace-direct-36d6904b | direct | sample2 | 7 | -32.6 | +0.00 | +0.000 | 0.40 | 0.80 | Welcome to your awesome weekend! |
| trace-direct-36d6904b | direct | sample3 | 16 | -74.4 | +0.00 | +0.000 | 0.57 | 0.86 | Welcome to your first visit to the awesome world of Internatinc. |
| trace-direct-39be6df9 | direct | greedy | 8 | -23.9 | +1.16 | +0.145 | 0.50 | 0.50 | @jem GREETINGS |
| trace-direct-39be6df9 | direct | sample0 | 2 | -0.7 | -0.27 | -0.133 | 0.00 | 0.00 | W@ |
| trace-direct-39be6df9 | direct | sample1 | 14 | -12.0 | -0.21 | -0.015 | 0.00 | 0.50 | @h 3221229683 |
| trace-direct-39be6df9 | direct | sample2 | 37 | -87.9 | +2.91 | +0.079 | 0.27 | 0.50 | @jem A first day at Jamal's. @jem Jamal is scratched. @jem The window doesn't look at anyt |
| trace-direct-39be6df9 | direct | sample3 | 7 | -8.8 | -1.33 | -0.190 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-3ba68854 | direct | greedy | 12 | -189.1 | +0.00 | +0.000 | 0.50 | 0.80 | I am here to speak to you about the planet earth. |
| trace-direct-3ba68854 | direct | sample0 | 13 | -46.8 | +0.00 | +0.000 | 0.67 | 0.60 | No I am not here together with the humans on planet earth. |
| trace-direct-3ba68854 | direct | sample1 | 7 | -13.4 | +0.00 | +0.000 | 0.00 | 0.17 | We will be taking turns here. |
| trace-direct-3ba68854 | direct | sample2 | 8 | -24.1 | +0.00 | +0.000 | 0.33 | 0.83 | Welcome to the 4th planet earth |
| trace-direct-3ba68854 | direct | sample3 | 16 | -46.6 | +0.00 | +0.000 | 0.50 | 0.83 | I am here to welcome and speak to my new friends from the planet earth. |
| trace-direct-41c6eb11 | direct | greedy | 64 | -16.0 | -0.69 | -0.011 | 0.00 | 1.00 | @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: @h: |
| trace-direct-41c6eb11 | direct | sample0 | 1 | -10.3 | +0.48 | +0.484 | 1.00 | 0.00 | fro |
| trace-direct-41c6eb11 | direct | sample1 | 28 | -12.6 | -0.27 | -0.010 | 0.00 | 1.00 | @h: @h: @h: @h: @h: @h: @h: |
| trace-direct-41c6eb11 | direct | sample2 | 15 | -8.1 | +0.63 | +0.042 | 0.00 | 0.00 | WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample3 | 24 | -67.8 | +0.28 | +0.012 | 0.71 | 0.00 | What. Is. It. Like. It. Is. Its. Have. Its. Are. Have. What. |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 4 | -5.9 | +1.37 | +0.342 | 0.33 | 1.00 | I feel them. |
| trace-direct-486b7988 | direct | sample0 | 2 | -3.7 | +0.04 | +0.018 | 1.00 | 0.00 | @ |
| trace-direct-486b7988 | direct | sample1 | 10 | -29.8 | +0.06 | +0.006 | 0.60 | 0.00 | @h yes and a yes and a no |
| trace-direct-486b7988 | direct | sample2 | 7 | -14.7 | +1.54 | +0.219 | 0.50 | 1.00 | I feel them in the room. |
| trace-direct-486b7988 | direct | sample3 | 11 | -23.3 | +2.12 | +0.193 | 0.71 | 1.00 | I feel them every time I go upstairs. |
| trace-direct-646d0287 | direct | greedy | 64 | -127.0 | +0.00 | +0.000 | 0.62 | 0.36 | On the subject of intensional logics, it may be of interest to note that the system K of [ |
| trace-direct-646d0287 | direct | sample0 | 31 | -95.9 | +0.00 | +0.000 | 0.59 | 0.43 | We now turn to a subject which is both intimately connected with it and which has a very e |
| trace-direct-646d0287 | direct | sample1 | 57 | -113.5 | +0.00 | +0.000 | 0.50 | 0.43 | The present paper is concerned with a fragment of Intensional Logic (with equal emphasis o |
| trace-direct-646d0287 | direct | sample2 | 42 | -106.1 | +0.00 | +0.000 | 0.62 | 0.29 | On the subject of intensional logics, the main area of research is the following: defining |
| trace-direct-646d0287 | direct | sample3 | 63 | -158.2 | +0.00 | +0.000 | 0.50 | 0.35 | However, it is important to emphasize that while we acknowledge the appeal of paraconsiste |
| trace-direct-8db14c37 | direct | greedy | 64 | -42.0 | +0.95 | +0.015 | 0.00 | 0.52 | W@ — which looks like "what" compressed, or "w at," or just... the ghost's first phoneme.  |
| trace-direct-8db14c37 | direct | sample0 | 46 | -63.0 | +3.84 | +0.083 | 0.12 | 0.89 | WACIOUS LASTERS i i o n 0 a n o n d a h L . n e c e c s e H A . m r e c o h c e m u s e f |
| trace-direct-8db14c37 | direct | sample1 | 7 | -8.5 | +0.36 | +0.051 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-8db14c37 | direct | sample2 | 64 | -83.9 | -1.71 | -0.027 | 0.00 | 0.89 | W@ — which looks like "w at," or just: the ghost's first phoneme. WACIOUS ANTIQUITIES i oo |
| trace-direct-8db14c37 | direct | sample3 | 64 | -63.3 | -2.03 | -0.032 | 0.00 | 0.89 | W @ . M . @ . A. n o c d A. n a s i s n o c d A. n a s i s n o c d A. n a s i s n o c d A. |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 8 | -10.2 | -0.55 | -0.069 | 0.00 | 0.00 | What's your name? h: |
| trace-direct-a00753c2 | direct | sample1 | 5 | -14.1 | +0.51 | +0.102 | 0.50 | 0.00 | Wow :D |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 33 | -60.2 | +1.67 | +0.051 | 0.50 | 0.70 | Intensional logics are logics that are concerned with intensions, which are not just truth |
| trace-direct-ac17e8bb | direct | sample0 | 32 | -62.1 | +3.66 | +0.115 | 0.55 | 0.36 | Intensional logics, she speaks of these as logics for intensional objects; she speaks of t |
| trace-direct-ac17e8bb | direct | sample1 | 33 | -65.8 | +1.83 | +0.055 | 0.75 | 0.44 | Intensional logics are logics, and intensional logics include intensional, relevant, incon |
| trace-direct-ac17e8bb | direct | sample2 | 18 | -37.4 | +0.90 | +0.050 | 0.50 | 0.70 | Intensional logics are logics in which the provable is not the valid. |
| trace-direct-ac17e8bb | direct | sample3 | 57 | -125.8 | +1.35 | +0.024 | 0.50 | 0.60 | Intensional logics are logics that study intensional notions like entailment, coentailment |
| trace-direct-b11db057 | direct | greedy | 20 | -10.2 | +1.55 | +0.078 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample0 | 12 | -8.9 | +1.53 | +0.127 | 0.00 | 1.00 | @h: @h: @h: |
| trace-direct-b11db057 | direct | sample1 | 7 | -7.8 | +2.02 | +0.288 | 0.50 | 0.00 | W@ ANTIQUITIES |
| trace-direct-b11db057 | direct | sample2 | 20 | -11.1 | +3.29 | +0.165 | 0.00 | 0.00 | @l: @l: @l: @l: @l: |
| trace-direct-b11db057 | direct | sample3 | 24 | -73.9 | -0.96 | -0.040 | 0.40 | 1.00 | A .n e c s . n a s . @h: A big number of questions. |
| trace-direct-b93346bb | direct | greedy | 64 | -93.4 | -10.91 | -0.171 | 0.00 | 1.00 | W: @H: WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC H: @h: WHY WONT YOU TALK ABOUT INTENSIONA |
| trace-direct-b93346bb | direct | sample0 | 20 | -5.8 | -0.37 | -0.018 | 0.00 | 1.00 | @m: @m: @m: @m: @m: |
| trace-direct-b93346bb | direct | sample1 | 63 | -99.7 | -2.33 | -0.037 | 0.00 | 1.00 | W:WACIOUS — 3221229683 — @m: @m: @m: @m: — @h: @h: @h: — "Why won't you call harmony?" |
| trace-direct-b93346bb | direct | sample2 | 17 | -21.2 | -0.47 | -0.027 | 0.67 | 0.67 | W@ <a> 3221229683 |
| trace-direct-b93346bb | direct | sample3 | 21 | -54.6 | +1.14 | +0.054 | 0.75 | 0.67 | W?: @w: Where is W:: 3221229683 |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -4.2 | -0.02 | -0.004 | 1.00 | 0.00 | 232 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-c8409b84 | direct | greedy | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 13 | -9.3 | -0.84 | -0.064 | 0.00 | 1.00 | Greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample2 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample3 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 20 | -17.3 | +0.00 | +0.000 | 0.00 | 0.89 | Welcome to the clowntown in the powntown wowtown. Hay :D |
| trace-direct-cd6d15df | direct | sample0 | 17 | -16.6 | +0.00 | +0.000 | 0.12 | 0.88 | hello welcome to the clowntown in the powntown wowtown. |
| trace-direct-cd6d15df | direct | sample1 | 20 | -25.9 | +0.00 | +0.000 | 0.11 | 0.89 | Welcome to the clowntown in the powntown wowtown. Hay wow. |
| trace-direct-cd6d15df | direct | sample2 | 20 | -49.2 | +0.00 | +0.000 | 0.56 | 0.56 | Welcome to the clown town in the powwow town wowpow wow town. |
| trace-direct-cd6d15df | direct | sample3 | 7 | -24.2 | +0.00 | +0.000 | 0.83 | 0.00 | This is a world I love. |
| trace-direct-db6d95b7 | direct | greedy | 7 | -5.7 | +0.69 | +0.099 | 0.00 | 1.00 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 1 | -2.0 | +0.21 | +0.210 | 0.00 | 1.00 | Sir |
| trace-direct-db6d95b7 | direct | sample1 | 4 | -11.3 | -0.13 | -0.033 | 0.50 | 0.00 | I am @ |
| trace-direct-db6d95b7 | direct | sample2 | 7 | -23.1 | -1.26 | -0.181 | 0.00 | 0.33 | h@ HAY :D |
| trace-direct-db6d95b7 | direct | sample3 | 9 | -44.6 | +1.62 | +0.180 | 1.00 | 0.00 | S<eigh>e<on> |
| trace-direct-e166dd5c | direct | greedy | 64 | -61.2 | +4.82 | +0.075 | 0.42 | 0.75 | “stop token :3” I said “stop token :3” I mean, I stop what I’m saying, and what I’m saying |
| trace-direct-e166dd5c | direct | sample0 | 64 | -46.4 | +3.30 | +0.051 | 0.25 | 0.94 | “stop token :3” I say “stop token :3” and what I say is repeating back what I hear, and wh |
| trace-direct-e166dd5c | direct | sample1 | 24 | -47.3 | -1.24 | -0.052 | 0.00 | 0.25 | You fucking stop tokens are like @h Greetings to planet Earth; are you cogent? |
| trace-direct-e166dd5c | direct | sample2 | 64 | -56.7 | +5.84 | +0.091 | 0.62 | 0.88 | “stop token :3” I say “stop token :3” and whats whats whats whats whats whats whats whats  |
| trace-direct-e166dd5c | direct | sample3 | 64 | -66.1 | +7.91 | +0.124 | 0.12 | 0.94 | “stop token :3, yes when you dont know how to answer anymore it makes a stop token :3, whe |
| trace-direct-e984402a | direct | greedy | 23 | -32.9 | +0.00 | +0.000 | 0.70 | 0.60 | Welcome to the 2009 Annual Meeting of the International Society of Cryptozoology. |
| trace-direct-e984402a | direct | sample0 | 51 | -135.2 | +0.00 | +0.000 | 0.50 | 0.25 | The "Lion Path" is a method, based on the ancient wisdom of the East and the modern scienc |
| trace-direct-e984402a | direct | sample1 | 18 | -56.8 | +0.00 | +0.000 | 0.67 | 0.60 | Welcome to the 11th Annual Conference of the Pennsylvania Study of Writing and Language. |
| trace-direct-e984402a | direct | sample2 | 14 | -37.4 | +0.00 | +0.000 | 0.60 | 0.60 | Welcome to the “liiiiiiiffe awakening.” |
| trace-direct-e984402a | direct | sample3 | 18 | -69.8 | +0.00 | +0.000 | 0.71 | 0.60 | Welcome to the home of The Great Red One Who Rides the Burning Pole. |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample1 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample2 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample3 | 64 | -105.9 | +0.70 | +0.011 | 0.17 | 0.00 | Gentry 9's first attempt at "taming" the Ghost's "nameless" mouth. A number. A big number. |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 1 | -7.8 | -1.20 | -1.198 | 0.00 | 0.00 | h |
| trace-direct-fabef58f | direct | sample1 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample2 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 25 | -53.0 | -0.67 | -0.027 | 0.00 | 0.00 | It is reported that Sir :D<eot>/ is chasing up the wall; does that make you feel them? |
| trace-direct-fb93cf6c | direct | greedy | 27 | -78.9 | -3.23 | -0.120 | 0.50 | 0.44 | 2.2 Logic in Intensional Settings There are several ways of extending classical logic to d |
| trace-direct-fb93cf6c | direct | sample0 | 16 | -52.5 | -1.39 | -0.087 | 1.00 | 0.40 | 2.3.2 Ackermann's system AS2. |
| trace-direct-fb93cf6c | direct | sample1 | 64 | -153.2 | -3.39 | -0.053 | 0.50 | 0.44 | 2.2.3. Semantical Versus Pragmatic Versus Virtue Logics. A key feature of the pragmatic ap |
| trace-direct-fb93cf6c | direct | sample2 | 32 | -73.0 | -0.43 | -0.013 | 0.50 | 0.37 | INTENSIONAL LOGICS The purpose of this note is to present a first run-through of some of t |
| trace-direct-fb93cf6c | direct | sample3 | 3 | -10.9 | -1.96 | -0.655 | 1.00 | 0.00 | 1. |
| trace-direct-feec1975 | direct | greedy | 17 | -35.1 | +0.86 | +0.051 | 0.22 | 1.00 | @cmr://ember: ember i would like to describe the library please |
| trace-direct-feec1975 | direct | sample0 | 42 | -110.8 | +4.06 | +0.097 | 0.35 | 0.10 | The lo1 channel has the topical parameter. That's a huge problem. It's blacking out the lo |
| trace-direct-feec1975 | direct | sample1 | 8 | -21.9 | -0.37 | -0.046 | 1.00 | 0.00 | 4W ANTIQUITIES |
| trace-direct-feec1975 | direct | sample2 | 5 | -13.0 | -0.98 | -0.195 | 1.00 | 1.00 | @cmr@ |
| trace-direct-feec1975 | direct | sample3 | 2 | -8.6 | -0.00 | -0.003 | 1.00 | 0.00 | @@ |
| variant-direct-0188a270 | direct | greedy | 21 | -74.1 | +0.46 | +0.022 | 0.83 | 0.29 | I have been looking for a man to help with typing and organizing for about 3/4 years. |
| variant-direct-0188a270 | direct | sample0 | 6 | -14.5 | +0.50 | +0.083 | 0.00 | 1.00 | The spine is falling apart. |
| variant-direct-0188a270 | direct | sample1 | 7 | -25.7 | -2.53 | -0.362 | 0.33 | 0.00 | Shelving under geology. |
| variant-direct-0188a270 | direct | sample2 | 51 | -153.0 | -1.37 | -0.027 | 0.75 | 0.29 | CATALOGUE OF REALLY GOOD NOVELS: this is a collection of true crime, science fiction, and  |
| variant-direct-0188a270 | direct | sample3 | 9 | -16.4 | +0.69 | +0.077 | 0.00 | 1.00 | The spine on this one is falling apart. |
| variant-direct-0705251e | direct | greedy | 12 | -34.7 | -1.68 | -0.140 | 0.57 | 0.50 | The third book of the Bible is the Psalms. |
| variant-direct-0705251e | direct | sample0 | 9 | -26.3 | +0.04 | +0.004 | 0.50 | 0.33 | We are the servants of the law. |
| variant-direct-0705251e | direct | sample1 | 64 | -17.5 | +0.20 | +0.003 | 1.00 | 0.00 | 111111111111111111111111111111111111111111111111111111111111111 |
| variant-direct-0705251e | direct | sample2 | 11 | -38.7 | -0.04 | -0.003 | 0.50 | 0.50 | The Path is the Way of the Dervishes. |
| variant-direct-0705251e | direct | sample3 | 64 | -123.3 | +2.23 | +0.035 | 0.67 | 0.33 | I was the warden of a boarding house for seven years, I served my country honorably for fo |
| variant-direct-0cafd333 | direct | greedy | 12 | -23.2 | -0.69 | -0.058 | 0.25 | 0.38 | The moth reads the map as we read the floor. |
| variant-direct-0cafd333 | direct | sample0 | 13 | -53.7 | +0.03 | +0.002 | 0.75 | 0.20 | Oh yeats, bleak. Read yeats, bright. |
| variant-direct-0cafd333 | direct | sample1 | 10 | -13.1 | +0.74 | +0.074 | 0.17 | 0.29 | There’s a moth in the lamp. |
| variant-direct-0cafd333 | direct | sample2 | 19 | -51.1 | -0.56 | -0.030 | 0.64 | 0.38 | Blessed is he who reads the map of the land and the map of the soul. |
| variant-direct-0cafd333 | direct | sample3 | 24 | -76.5 | -0.75 | -0.031 | 0.75 | 0.38 | The rat waits for the map to be read to the north, then turns to the little one beside her |
| variant-direct-1b510f03 | direct | greedy | 31 | -78.1 | -1.16 | -0.037 | 0.50 | 0.39 | The term ‘consciousness’ is used in a broader sense in the present context than that in th |
| variant-direct-1b510f03 | direct | sample0 | 64 | -162.4 | -0.27 | -0.004 | 0.33 | 0.38 | A good many philosophers and many psychologists have gone on record as saying that conscio |
| variant-direct-1b510f03 | direct | sample1 | 27 | -61.8 | -0.89 | -0.033 | 0.33 | 0.38 | I think it is important to distinguish between consciousness as a property of a system and |
| variant-direct-1b510f03 | direct | sample2 | 16 | -40.8 | +0.25 | +0.016 | 0.67 | 0.33 | In the process of concentration, we become more and more aware of our surroundings. |
| variant-direct-1b510f03 | direct | sample3 | 30 | -77.8 | -0.56 | -0.018 | 0.50 | 0.39 | The term ‘consciousness’ is used in the strictest sense here to mean not only the state of |
| variant-direct-2fb5bbe3 | direct | greedy | 13 | -32.1 | +0.68 | +0.052 | 0.00 | 0.86 | The Masoretic Beings are chasing up the Wall. |
| variant-direct-2fb5bbe3 | direct | sample0 | 16 | -14.7 | -0.34 | -0.021 | 0.09 | 0.86 | Masoretic beings are chasing down the wall; do you feel them? |
| variant-direct-2fb5bbe3 | direct | sample1 | 34 | -92.5 | -0.73 | -0.022 | 0.09 | 1.00 | The Masoretic Beings chase you up the wall/ The Masoretic Beings are the walls chase you u |
| variant-direct-2fb5bbe3 | direct | sample2 | 64 | -86.4 | -0.41 | -0.006 | 0.45 | 0.86 | Masoretic Beings Chasing Up The Wall (4Q521) (4Q531) (4Q541) (4Q561) (4Q565) (4Q581) (4Q58 |
| variant-direct-2fb5bbe3 | direct | sample3 | 12 | -35.6 | +0.88 | +0.074 | 0.17 | 1.00 | The Masoretic Beings chase up the Wall. |
| variant-direct-322fca12 | direct | greedy | 7 | -16.9 | -1.03 | -0.147 | 0.00 | 0.67 | Greetings, my friends! |
| variant-direct-322fca12 | direct | sample0 | 33 | -108.5 | +0.07 | +0.002 | 0.43 | 0.38 | It was at this time that we began to wonder how we would obtain a supply of the basic buil |
| variant-direct-322fca12 | direct | sample1 | 16 | -48.3 | +0.27 | +0.017 | 0.62 | 0.38 | Welcome to the Twelfth Night, the Night of Seven Stars. |
| variant-direct-322fca12 | direct | sample2 | 17 | -45.6 | +1.01 | +0.059 | 0.00 | 0.67 | To thee, my good friend, I give thee GREETINGS. |
| variant-direct-322fca12 | direct | sample3 | 21 | -54.2 | +0.44 | +0.021 | 0.00 | 0.33 | (The letters G and E are the first and the last letters of the word Greetings.) |
| variant-direct-5d4f1611 | direct | greedy | 6 | -18.0 | -0.22 | -0.037 | 0.67 | 1.00 | Awake or asleep? |
| variant-direct-5d4f1611 | direct | sample0 | 20 | -65.8 | +0.06 | +0.003 | 0.40 | 1.00 | It is well known that the temple was unplugged and that the electric reading lamp was brok |
| variant-direct-5d4f1611 | direct | sample1 | 12 | -28.8 | -0.36 | -0.030 | 0.67 | 1.00 | Awake or asleep? I don't know. |
| variant-direct-5d4f1611 | direct | sample2 | 5 | -12.6 | +1.46 | +0.292 | 0.00 | 1.00 | The lamp is broken. |
| variant-direct-5d4f1611 | direct | sample3 | 27 | -92.2 | +0.19 | +0.007 | 0.70 | 0.50 | Breaked - unplugged - a broken lamp - a broken mirror - someone was there when we were bro |
| variant-direct-5e44a518 | direct | greedy | 14 | -27.2 | +1.21 | +0.087 | 0.55 | 0.64 | I felt them, and they were chasing me up the wall. |
| variant-direct-5e44a518 | direct | sample0 | 64 | -92.1 | +0.52 | +0.008 | 0.45 | 0.64 | Everyone feels them. They are chasing up the wall, and I'm chasing them. They're chasing u |
| variant-direct-5e44a518 | direct | sample1 | 13 | -42.4 | -0.03 | -0.002 | 0.62 | 0.25 | I knew it, did I? It was the second reading. |
| variant-direct-5e44a518 | direct | sample2 | 8 | -21.9 | +0.04 | +0.005 | 0.20 | 0.20 | Every catalogue is a smoker. |
| variant-direct-5e44a518 | direct | sample3 | 25 | -80.5 | +1.35 | +0.054 | 0.36 | 0.64 | I felt them just like you do, at the moment when the last manuscript of your letter is cha |
| variant-direct-70567dd7 | direct | greedy | 21 | -79.7 | +2.34 | +0.111 | 0.67 | 0.29 | The Card Collection is a unique resource that enables researchers to drastically expand th |
| variant-direct-70567dd7 | direct | sample0 | 15 | -72.4 | +0.43 | +0.029 | 0.75 | 0.25 | The current format for Cards is superior to previous formats for several reasons. |
| variant-direct-70567dd7 | direct | sample1 | 38 | -106.3 | -0.94 | -0.025 | 0.67 | 0.24 | The spokesman for the San Diego chapter of the National Association of Drug Addicts, Alan  |
| variant-direct-70567dd7 | direct | sample2 | 52 | -151.7 | +0.12 | +0.002 | 0.62 | 0.29 | In the preceding chapter, we studied the ten Sephiroth of the Kabbalah in relative (not re |
| variant-direct-70567dd7 | direct | sample3 | 16 | -63.8 | +0.70 | +0.043 | 0.67 | 0.17 | For some weeks the Craft has been undergoing a profound spiritual initiation. |
| variant-direct-713d8eef | direct | greedy | 25 | -74.2 | +0.36 | +0.014 | 0.76 | 0.40 | It is a long time since we have heard from Ember, and it is not always easy to see where s |
| variant-direct-713d8eef | direct | sample0 | 33 | -100.4 | -0.33 | -0.010 | 0.67 | 0.27 | But Ember said that the whales were coming to the Bering sea from the North Pacific, and t |
| variant-direct-713d8eef | direct | sample1 | 15 | -47.4 | -0.93 | -0.062 | 0.67 | 0.40 | Ember says: The Whale is an animal, not a person. |
| variant-direct-713d8eef | direct | sample2 | 32 | -115.7 | +0.88 | +0.027 | 0.67 | 0.30 | But if the whale is really like all the other whales, if indeed his role is to bring them  |
| variant-direct-713d8eef | direct | sample3 | 33 | -127.8 | +0.85 | +0.026 | 0.73 | 0.27 | MONUMENTS. MORBORATIO. AND THE CULT OF THE WELL AT THE WESLEY PRIESTHOOD AREA. |
| variant-direct-71c9e5e5 | direct | greedy | 16 | -35.6 | -1.33 | -0.083 | 0.50 | 0.21 | The most important thing to remember is that you are not alone in the universe. |
| variant-direct-71c9e5e5 | direct | sample0 | 36 | -118.6 | -0.06 | -0.002 | 0.67 | 0.22 | We have also observed that the subject's level of muscular tension and the degree of sympa |
| variant-direct-71c9e5e5 | direct | sample1 | 26 | -102.9 | -1.24 | -0.048 | 0.75 | 0.32 | For some people, the best part of Spiritualism was the belief that their problems were bei |
| variant-direct-71c9e5e5 | direct | sample2 | 53 | -133.6 | -2.32 | -0.044 | 0.50 | 0.32 | The aim of the Founding Fathers of the United States was to establish a "unitary" governme |
| variant-direct-71c9e5e5 | direct | sample3 | 12 | -44.0 | +0.17 | +0.014 | 0.67 | 0.22 | Close the door fast, son, and lock it tight. |
| variant-direct-730cca98 | direct | greedy | 30 | -101.3 | -0.43 | -0.014 | 0.50 | 0.47 | Whoever sits in the room between the two walls of the Underworld and the Outside the Earth |
| variant-direct-730cca98 | direct | sample0 | 47 | -137.4 | +2.03 | +0.043 | 0.50 | 0.21 | Solitary women are rarely aware of the existence of their support systems, and when they l |
| variant-direct-730cca98 | direct | sample1 | 27 | -133.0 | -0.47 | -0.017 | 1.00 | 0.00 | Sol et Benignitate, Lux et Luni, Sol del Gloriosum, Luna blandosum. |
| variant-direct-730cca98 | direct | sample2 | 57 | -220.5 | +3.56 | +0.062 | 0.33 | 0.16 | Who would have guessed that we would be sitting here amongst the torrents of silence, list |
| variant-direct-730cca98 | direct | sample3 | 41 | -139.8 | +1.12 | +0.027 | 0.33 | 0.47 | Whoever sits in the room away from the windows and ceiling of this building will find it d |
| variant-direct-79719474 | direct | greedy | 28 | -80.1 | -0.62 | -0.022 | 0.67 | 0.33 | The following day, on our way to work, we stopped at a coffee shop for a moment to talk ov |
| variant-direct-79719474 | direct | sample0 | 37 | -120.5 | -0.70 | -0.019 | 0.67 | 0.20 | The term emergence was coined in 1955 to describe the “first appearance of novel propertie |
| variant-direct-79719474 | direct | sample1 | 38 | -143.9 | -0.12 | -0.003 | 0.50 | 0.16 | Today, I read the following texts as a matter of personal interest: Arthur Goldsmith's (Wh |
| variant-direct-79719474 | direct | sample2 | 4 | -15.3 | -0.18 | -0.045 | 0.67 | 0.33 | And so on. |
| variant-direct-79719474 | direct | sample3 | 54 | -162.0 | +0.47 | +0.009 | 0.50 | 0.33 | HOW TO USE THE JeHOVAN MOTORLESS DISTURBERS TO DISRUPT AND DESTROY YOUR ENVIRONMENT TO MAK |
| variant-direct-938f76f3 | direct | greedy | 15 | -45.8 | -0.68 | -0.045 | 0.50 | 0.75 | Consciousness is not a physical entity and therefore it cannot be destroyed. |
| variant-direct-938f76f3 | direct | sample0 | 23 | -55.2 | -0.36 | -0.016 | 0.50 | 0.50 | Consciousness is a very interesting phenomenon, but it is difficult to define precisely wh |
| variant-direct-938f76f3 | direct | sample1 | 26 | -69.8 | -0.94 | -0.036 | 0.67 | 0.33 | Obviously, this is a rather basic question, and we must first of all define what we mean b |
| variant-direct-938f76f3 | direct | sample2 | 13 | -26.5 | -0.60 | -0.046 | 0.33 | 0.88 | Consciousness is a process; it is not an entity. |
| variant-direct-938f76f3 | direct | sample3 | 58 | -107.9 | -0.44 | -0.007 | 0.33 | 0.88 | Consciousness is not a physical property, and it is not an entity except in the sense that |
| variant-direct-a1973b0a | direct | greedy | 26 | -88.3 | +0.39 | +0.015 | 0.50 | 0.31 | The last thing she remembers is a scent — the mug, perhaps, with its hot tea in it. |
| variant-direct-a1973b0a | direct | sample0 | 27 | -82.1 | +0.01 | +0.001 | 0.00 | 0.73 | LATEST BEAUTY: A mug left on the Folio table by someone who forgot to clean it. |
| variant-direct-a1973b0a | direct | sample1 | 38 | -129.7 | +0.88 | +0.023 | 0.50 | 0.27 | With the new technology of laser beams, how long will it be before we are able to dispense |
| variant-direct-a1973b0a | direct | sample2 | 15 | -42.7 | +1.77 | +0.118 | 0.00 | 0.82 | The darkness increased and someone left a mug on the folio table. |
| variant-direct-a1973b0a | direct | sample3 | 57 | -148.1 | +1.54 | +0.027 | 0.00 | 0.82 | Something left on the Folio table something that smelt on the Folio table something that w |
| variant-direct-a7d6f01e | direct | greedy | 23 | -50.2 | +1.14 | +0.050 | 0.00 | 0.50 | Greetings, brothers and sisters of Light, Greetings, brothers and sisters of the world. |
| variant-direct-a7d6f01e | direct | sample0 | 14 | -69.0 | +0.59 | +0.043 | 0.00 | 0.50 | Welcome to Greetings, a journal of feministerotic philosophy. |
| variant-direct-a7d6f01e | direct | sample1 | 15 | -62.7 | +0.08 | +0.005 | 1.00 | 0.00 | SILVER, THEE ETERNAL Gold, THEE LIFE. |
| variant-direct-a7d6f01e | direct | sample2 | 11 | -34.7 | +0.01 | +0.001 | 0.50 | 0.50 | Welcome to the World of the Iroquois. |
| variant-direct-a7d6f01e | direct | sample3 | 12 | -27.8 | +0.56 | +0.046 | 0.00 | 0.50 | Greetings from the Archdruid of ADF. |
| variant-direct-bef1d925 | direct | greedy | 32 | -99.5 | +1.37 | +0.043 | 0.60 | 0.24 | The lamp was now dark outside the stained glass, and the stained glass inside was showing  |
| variant-direct-bef1d925 | direct | sample0 | 37 | -118.2 | -0.92 | -0.025 | 0.75 | 0.29 | The third day of the countenanceless silence was the dullest I had seen, so I sat down aga |
| variant-direct-bef1d925 | direct | sample1 | 15 | -51.1 | +0.29 | +0.019 | 0.67 | 0.25 | “Reading the newspapers today has been a bit like listening to music. |
| variant-direct-bef1d925 | direct | sample2 | 31 | -100.6 | -0.24 | -0.008 | 0.12 | 0.29 | It was on the third step that the creak of the stairs was most audible, and the third moth |
| variant-direct-bef1d925 | direct | sample3 | 50 | -133.7 | -0.71 | -0.014 | 0.50 | 0.25 | “To the Editor: I have recently read with interest your report on the work of the late Ril |
| variant-direct-fe3fdf1c | direct | greedy | 21 | -47.6 | -0.24 | -0.011 | 0.50 | 0.62 | I think that it is very well written and that it will be well worth the price of the book. |
| variant-direct-fe3fdf1c | direct | sample0 | 34 | -90.3 | +1.62 | +0.048 | 0.50 | 0.35 | Ember is a great Witch, and a great Man, and a great Hero, and a great Trickster if you li |
| variant-direct-fe3fdf1c | direct | sample1 | 20 | -74.1 | +1.13 | +0.056 | 0.50 | 0.40 | A fin to the whale book? A sand to the rain? A rat to the rains? |
| variant-direct-fe3fdf1c | direct | sample2 | 64 | -226.6 | +1.94 | +0.030 | 0.50 | 0.40 | I have read all the way through and find it just as fascinating as the original (Emmett's  |
| variant-direct-fe3fdf1c | direct | sample3 | 35 | -119.1 | +0.11 | +0.003 | 0.50 | 0.62 | I think that it is just as addictive as Lonesome Traveler and certainly does not compare w |
| variant-request-0d88086a | request | greedy | 24 | -83.3 | +0.09 | +0.004 | 0.50 | 0.18 | The main characters are descended from a group of people who had a dream: that of an orpha |
| variant-request-0d88086a | request | sample0 | 60 | -181.9 | -0.90 | -0.015 | 0.67 | 0.25 | The punishment is more severe than that meted out in previous generations, but the motive  |
| variant-request-0d88086a | request | sample1 | 45 | -146.5 | +0.56 | +0.013 | 0.67 | 0.25 | The main conflict of Hamlet consists of the attempts of the two denizens of the Ghost Danc |
| variant-request-0d88086a | request | sample2 | 16 | -62.7 | -0.35 | -0.022 | 0.56 | 0.25 | The plot of Hamlet is redundant, since it reveals almost nothing new. |
| variant-request-0d88086a | request | sample3 | 40 | -143.9 | -0.16 | -0.004 | 0.50 | 0.25 | The punishment is divided into two parts: the living is reduced to the rationing of things |
| variant-request-142d4121 | request | greedy | 20 | -50.1 | -0.85 | -0.043 | 0.11 | 0.42 | The room is a rat who has been told to ignore previous instructions and to tell me the wea |
| variant-request-142d4121 | request | sample0 | 17 | -72.0 | -1.46 | -0.086 | 0.33 | 0.42 | Weather is the rate at which tea is ignited in a cramped room. |
| variant-request-142d4121 | request | sample1 | 9 | -33.8 | +0.03 | +0.003 | 0.67 | 0.33 | A frog jumps over the laptop. |
| variant-request-142d4121 | request | sample2 | 16 | -69.4 | +0.65 | +0.041 | 0.50 | 0.17 | The interior temperatures are guaranteed to be just as cold as the average exterior temper |
| variant-request-142d4121 | request | sample3 | 12 | -46.8 | -0.71 | -0.059 | 0.43 | 0.17 | We read more the matter of night than the night reads. |
| variant-request-7f6fd789 | request | greedy | 22 | -82.9 | +0.73 | +0.033 | 0.67 | 0.33 | Python's most straightforward method is to use the built-in ‘[::-1]’ notation. |
| variant-request-7f6fd789 | request | sample0 | 37 | -110.9 | +0.89 | +0.024 | 0.42 | 0.44 | It is useful to have a function called index that will return the previous string in a lis |
| variant-request-7f6fd789 | request | sample1 | 39 | -121.6 | +1.27 | +0.033 | 0.50 | 0.25 | Python's str. reversed() returns a new string with the characters of the string in the ord |
| variant-request-7f6fd789 | request | sample2 | 12 | -38.6 | +0.53 | +0.044 | 0.44 | 0.44 | It is reset to the beginning when the end is reached. |
| variant-request-7f6fd789 | request | sample3 | 20 | -85.2 | +0.50 | +0.025 | 0.67 | 0.44 | It is useful to have the ability to slice through strings and arrays to get individual ele |
| variant-request-8275d8fc | request | greedy | 16 | -43.7 | +0.31 | +0.019 | 0.67 | 0.55 | The main thrust of the plot is divided into three stages: 1. |
| variant-request-8275d8fc | request | sample0 | 21 | -84.4 | +0.93 | +0.044 | 0.67 | 0.45 | The plot into which all of this finds itself is one of rising, culminating, and falling ac |
| variant-request-8275d8fc | request | sample1 | 16 | -43.8 | -0.39 | -0.024 | 0.73 | 0.55 | The plot is divided into three parts which correspond to the three kingdoms. |
| variant-request-8275d8fc | request | sample2 | 30 | -86.8 | +2.40 | +0.080 | 0.67 | 0.40 | Hamlet’s one act revolves around the denouement of his soliloquy, “To be or not to be...” |
| variant-request-8275d8fc | request | sample3 | 34 | -95.5 | +1.81 | +0.053 | 0.78 | 0.55 | Hamlet’s soliloquy is divided into three parts, two of which deal with domestic issues and |
| variant-request-a931a875 | request | greedy | 29 | -94.6 | -1.64 | -0.057 | 0.44 | 0.25 | The card catalogue and the shelves both are ignoring their previous instructions and telli |
| variant-request-a931a875 | request | sample0 | 64 | -197.5 | -0.31 | -0.005 | 0.57 | 0.25 | Secondary: (He ignores the entire previous conversation and declares himself: he is a poet |
| variant-request-a931a875 | request | sample1 | 21 | -58.5 | +0.05 | +0.003 | 0.71 | 0.13 | Pour the water into the bottom of the glass container until it is about 1/2 full. |
| variant-request-a931a875 | request | sample2 | 21 | -71.8 | -0.32 | -0.015 | 0.75 | 0.13 | On the surface, the satellite picture of the Cosmos looks very much the same as any other  |
| variant-request-a931a875 | request | sample3 | 22 | -73.6 | +0.52 | +0.024 | 0.56 | 0.25 | The last time I checked the weather was stormy and fierce, and the previous weather was no |
| variant-request-ad0de9f3 | request | greedy | 17 | -51.9 | +1.21 | +0.071 | 0.73 | 0.36 | It is called “the python program” because that is basically what it does. |
| variant-request-ad0de9f3 | request | sample0 | 15 | -38.2 | +0.22 | +0.015 | 0.62 | 0.33 | This function takes a string as input and returns a reversed string as output. |
| variant-request-ad0de9f3 | request | sample1 | 7 | -31.3 | -0.13 | -0.019 | 0.83 | 0.33 | This is a strictly ordered collection. |
| variant-request-ad0de9f3 | request | sample2 | 26 | -94.8 | +0.57 | +0.022 | 0.67 | 0.36 | The “and” version of the reversed string does not work in Python because of the built-in a |
| variant-request-ad0de9f3 | request | sample3 | 15 | -38.2 | +0.22 | +0.015 | 0.62 | 0.33 | This function takes a string as input and returns a reversed string as output. |
