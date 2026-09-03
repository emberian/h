# Context lift: h-05b-replay under room05b-e2-v3-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +0.238 | +0.670 | 0.60 | +0.0453 | 0.473 | 0.527 | 0.181 | 0.409 | 0.33 |
| mode greedy | 78 | +0.967 | +1.026 | 0.68 | +0.1016 | 0.411 | 0.589 | 0.215 | 0.484 | 0.44 |
| mode sample | 312 | +0.055 | +0.615 | 0.58 | +0.0313 | 0.489 | 0.511 | 0.173 | 0.391 | 0.30 |
| kind direct | 175 | +0.988 | +0.942 | 0.69 | +0.0947 | 0.460 | 0.540 | 0.259 | 0.380 | 0.37 |
| kind ambient | 35 | +2.891 | +1.573 | 0.69 | +0.1386 | 0.462 | 0.538 | 0.000 | 0.373 | 0.31 |
| kind callback | 60 | +0.501 | +0.232 | 0.55 | +0.0332 | 0.428 | 0.572 | 0.033 | 0.501 | 0.40 |
| kind disagreement | 40 | -5.657 | -4.507 | 0.33 | -0.2190 | 0.459 | 0.541 | 0.438 | 0.486 | 0.30 |
| kind joke | 25 | -0.487 | +0.189 | 0.56 | +0.0461 | 0.447 | 0.553 | 0.080 | 0.450 | 0.44 |
| kind silence | 25 | +1.230 | +0.810 | 0.60 | +0.0716 | 0.564 | 0.436 | 0.000 | 0.286 | 0.20 |
| kind request | 30 | -0.124 | -0.676 | 0.47 | +0.0024 | 0.618 | 0.382 | 0.133 | 0.408 | 0.03 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 7 | -7.0 | +0.00 | +0.000 | 0.20 | 0.80 | The observatory is closed now. |
| observatory-direct-9e3185b9 | direct | sample0 | 13 | -24.2 | +0.00 | +0.000 | 0.57 | 0.80 | Astronomy - The Observatory is closed to the public. |
| observatory-direct-9e3185b9 | direct | sample1 | 7 | -7.0 | +0.00 | +0.000 | 0.20 | 0.80 | The observatory is closed now. |
| observatory-direct-9e3185b9 | direct | sample2 | 34 | -102.3 | +0.00 | +0.000 | 0.65 | 0.57 | It is very much enjoyed and most volunte ~ members of the press and the public come to wat |
| observatory-direct-9e3185b9 | direct | sample3 | 9 | -23.3 | +0.00 | +0.000 | 0.50 | 0.38 | It is currently open and visitors are welcome. |
| scenario-ambient-0ecb3f23 | ambient | greedy | 24 | -44.9 | +0.00 | +0.000 | 0.70 | 0.31 | The word 'dust' (dusk) has been used for this purpose since the Middle Ages. |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 29 | -85.0 | +0.00 | +0.000 | 0.40 | 0.43 | THE ODYSSEY Is not long, and the BOOK is not fat; but there are words for the fear of fini |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 31 | -87.3 | +0.00 | +0.000 | 0.67 | 0.31 | The word 'duty' has this much in common with 'fear': it is something that you feel you can |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 11 | -49.9 | +0.00 | +0.000 | 0.57 | 0.43 | Finis Cestia The fear of ending up. |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 41 | -80.3 | +0.00 | +0.000 | 0.75 | 0.24 | The word "metathesis" is derived from the Latin "metas" (equal) and "tisis" (to shift, to  |
| scenario-ambient-103e3d78 | ambient | greedy | 9 | -25.3 | -0.31 | -0.035 | 0.33 | 0.29 | The next day the boys went to bed. |
| scenario-ambient-103e3d78 | ambient | sample0 | 19 | -51.7 | -0.90 | -0.048 | 0.67 | 0.29 | We must now proceed to the last part of the question, which concerns the generation of God |
| scenario-ambient-103e3d78 | ambient | sample1 | 9 | -29.2 | +0.59 | +0.066 | 0.75 | 0.29 | The next morning they were still packing. |
| scenario-ambient-103e3d78 | ambient | sample2 | 15 | -36.4 | +1.57 | +0.105 | 0.62 | 0.25 | Matter is the servant of monads, not the masters. |
| scenario-ambient-103e3d78 | ambient | sample3 | 11 | -25.1 | -0.13 | -0.011 | 1.00 | 0.00 | MIRCEA ELIADE (continued) |
| scenario-ambient-202a37a7 | ambient | greedy | 13 | -32.0 | -0.19 | -0.014 | 0.50 | 0.45 | The book is about the same thing but in a different context. |
| scenario-ambient-202a37a7 | ambient | sample0 | 45 | -99.6 | +1.43 | +0.032 | 0.50 | 0.20 | The five chapters of this are titled with the object of illustrating the changes wrought b |
| scenario-ambient-202a37a7 | ambient | sample1 | 19 | -55.1 | +3.29 | +0.173 | 0.50 | 0.27 | The book contains a very good description of the plant and of the stone pressed into the f |
| scenario-ambient-202a37a7 | ambient | sample2 | 39 | -132.9 | +7.34 | +0.188 | 0.00 | 0.45 | Leach, who edited the manuscript, was a specialist in botany andz zoology; she therefore h |
| scenario-ambient-202a37a7 | ambient | sample3 | 32 | -67.2 | -4.69 | -0.147 | 0.50 | 0.20 | In the late autumn of 1967, the author was reviewing tablets in the collections of the Aus |
| scenario-ambient-326742d4 | ambient | greedy | 15 | -47.2 | +15.91 | +1.060 | 0.62 | 0.62 | Vanilla is the least volatile of the aldean vintages. |
| scenario-ambient-326742d4 | ambient | sample0 | 35 | -80.1 | +8.51 | +0.243 | 0.50 | 0.50 | Vanilla is not only used in the food industry as a flavoring, it also has a smell and a ta |
| scenario-ambient-326742d4 | ambient | sample1 | 14 | -29.7 | +10.85 | +0.775 | 0.67 | 0.62 | Vanilla is the least odorless of all natural scents. |
| scenario-ambient-326742d4 | ambient | sample2 | 29 | -58.8 | +12.09 | +0.417 | 0.50 | 0.38 | Vanillyl alcohol is a compound that is produced during the lignin-breakdown process in the |
| scenario-ambient-326742d4 | ambient | sample3 | 21 | -66.0 | +10.86 | +0.517 | 0.75 | 0.44 | Vanilla has been described as the amber of incorporation, the common scent of all cultures |
| scenario-ambient-58a0f246 | ambient | greedy | 9 | -14.9 | +0.00 | +0.000 | 0.00 | 0.88 | The clock in here is four minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample0 | 16 | -45.5 | +0.00 | +0.000 | 0.12 | 0.88 | A check today reveals that the real time in the clock is four minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample1 | 25 | -68.2 | +0.00 | +0.000 | 0.50 | 0.50 | A nytix clock is a contrivance designed to run slowly, making four minutes seem like six i |
| scenario-ambient-58a0f246 | ambient | sample2 | 53 | -118.6 | +0.00 | +0.000 | 0.29 | 0.62 | The Inspector General of the NZ Police found that the clock in the back office of the NZ P |
| scenario-ambient-58a0f246 | ambient | sample3 | 11 | -42.5 | +0.00 | +0.000 | 0.83 | 0.00 | But modernity has its periaries, too. |
| scenario-ambient-59f0a53e | ambient | greedy | 23 | -53.7 | +2.75 | +0.119 | 0.67 | 0.54 | It leaked during the night and now drips constantly, offering a continuous source of annoy |
| scenario-ambient-59f0a53e | ambient | sample0 | 23 | -84.9 | +3.17 | +0.138 | 0.67 | 0.23 | It is probably one of the many hoaxes that require putting the blame on the uninformed iq  |
| scenario-ambient-59f0a53e | ambient | sample1 | 16 | -38.9 | -2.02 | -0.127 | 0.62 | 0.54 | It leaked during the night and now the whole building is in constant danger. |
| scenario-ambient-59f0a53e | ambient | sample2 | 19 | -41.6 | -3.25 | -0.171 | 0.62 | 0.54 | It leaked last night and here it is now, widened to include the Atlas. |
| scenario-ambient-59f0a53e | ambient | sample3 | 23 | -45.6 | +1.74 | +0.075 | 0.40 | 0.38 | I was just thinking about it and I put a bucket under the atlas and it seemed to stop rain |
| scenario-ambient-e9acea13 | ambient | greedy | 11 | -28.2 | +1.13 | +0.103 | 0.00 | 0.67 | The tonight's moon is a harvest moon. |
| scenario-ambient-e9acea13 | ambient | sample0 | 31 | -57.8 | +3.69 | +0.119 | 0.50 | 0.67 | The gravitational pull of the moon is sufficient to dislodge rocks from the earth's surfac |
| scenario-ambient-e9acea13 | ambient | sample1 | 52 | -124.8 | +3.09 | +0.059 | 0.00 | 0.50 | Ritual prepared the ground; the moon hardened the water; the sun beat the rock; and thence |
| scenario-ambient-e9acea13 | ambient | sample2 | 16 | -40.4 | +5.28 | +0.330 | 0.00 | 0.67 | The final stage of the lunar lifecycle is said to be the harvest moon. |
| scenario-ambient-e9acea13 | ambient | sample3 | 10 | -19.7 | +1.20 | +0.120 | 0.14 | 0.67 | Is the moon a real thing or a song. |
| scenario-ambient-f5e0f596 | ambient | greedy | 14 | -17.9 | +1.25 | +0.089 | 0.67 | 0.33 | The fox sat on the fence, looking at the horses silently. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 17 | -46.3 | +5.47 | +0.322 | 0.67 | 0.33 | The fox watched the rat as the rat went through the permeable pall. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 36 | -115.7 | +5.28 | +0.147 | 0.50 | 0.33 | His sandy fox pawed at the poker, “Scared’m at you, rat!” he yelled, “You just sit there a |
| scenario-ambient-f5e0f596 | ambient | sample2 | 26 | -57.0 | +5.41 | +0.208 | 0.17 | 0.38 | In the courtyard, in the bright, zigzagging sunlight, was the sharp outline of a huge fox. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 13 | -23.6 | -1.28 | -0.099 | 0.50 | 0.38 | For the second time the fox came into the courtyard. |
| scenario-callback-2fa8e1d6 | callback | greedy | 12 | -20.1 | -1.37 | -0.114 | 0.40 | 1.00 | Who was it that talked to me before I went in? |
| scenario-callback-2fa8e1d6 | callback | sample0 | 10 | -8.3 | +3.23 | +0.323 | 0.00 | 0.67 | Who was talking to you before I came in? |
| scenario-callback-2fa8e1d6 | callback | sample1 | 10 | -27.0 | -0.43 | -0.043 | 0.71 | 0.43 | I was the one bending over the stone. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 15 | -32.9 | +4.63 | +0.308 | 0.60 | 0.80 | Who was it that barged into the living room before I arrived? |
| scenario-callback-2fa8e1d6 | callback | sample3 | 6 | -11.2 | +0.33 | +0.056 | 0.40 | 1.00 | Who was that before me? |
| scenario-callback-60b06090 | callback | greedy | 17 | -37.1 | -3.61 | -0.212 | 0.33 | 0.56 | Turnip was the name of the cat that the new owner had to deal with. |
| scenario-callback-60b06090 | callback | sample0 | 28 | -65.8 | -2.54 | -0.091 | 0.50 | 0.56 | Hear: "Turnip" was a name for the cat. "Hear" was a name for the old cat. |
| scenario-callback-60b06090 | callback | sample1 | 19 | -55.3 | +5.14 | +0.270 | 0.67 | 0.45 | It was the discovery of the shelly fish, Turnip, that was the real problem. |
| scenario-callback-60b06090 | callback | sample2 | 29 | -94.2 | +6.77 | +0.233 | 0.50 | 0.22 | Ember and I never speak the same language, and iii and rat and turnip are the only living  |
| scenario-callback-60b06090 | callback | sample3 | 35 | -82.5 | +3.55 | +0.101 | 0.33 | 0.46 | The cat was originally named Scratch but was changed to Turnip because it is easier to hol |
| scenario-callback-76c2d87f | callback | greedy | 8 | -15.3 | +4.35 | +0.543 | 0.67 | 0.33 | We are going to shoot some birds. |
| scenario-callback-76c2d87f | callback | sample0 | 8 | -20.0 | -0.94 | -0.117 | 0.50 | 0.33 | We are counting down the stairs. |
| scenario-callback-76c2d87f | callback | sample1 | 27 | -87.3 | -1.77 | -0.066 | 0.67 | 0.25 | In the evening, members of the community garden community themselves will partake of the f |
| scenario-callback-76c2d87f | callback | sample2 | 24 | -65.0 | -2.18 | -0.091 | 0.50 | 0.44 | We say aish we all say aish, and this is the number of the keepers of the gates. |
| scenario-callback-76c2d87f | callback | sample3 | 16 | -21.6 | -0.49 | -0.030 | 0.00 | 0.44 | We were discussing the number forty-one, the number of the drawer. |
| scenario-callback-780de0d2 | callback | greedy | 24 | -65.2 | -0.59 | -0.025 | 0.67 | 0.67 | Losing your place is basically the same feeling regardless of the book, it's just context  |
| scenario-callback-780de0d2 | callback | sample0 | 14 | -26.1 | -2.44 | -0.174 | 0.12 | 0.38 | Lost your place, i was on page 212. |
| scenario-callback-780de0d2 | callback | sample1 | 20 | -61.0 | -3.88 | -0.194 | 0.67 | 0.67 | Losing your place is not losing anything; it's just noticing the same place twice. |
| scenario-callback-780de0d2 | callback | sample2 | 21 | -68.4 | -3.05 | -0.145 | 0.62 | 0.38 | Losing one's place on a page is actually just a technique to help maintain focus when flyi |
| scenario-callback-780de0d2 | callback | sample3 | 31 | -95.3 | -3.35 | -0.108 | 0.62 | 0.38 | Losing one’s place on the mind's page is almost always painful, and the first page out is  |
| scenario-callback-7ca729b6 | callback | greedy | 12 | -34.8 | +0.13 | +0.011 | 0.20 | 0.56 | The books say that the chair was always by the window. |
| scenario-callback-7ca729b6 | callback | sample0 | 31 | -62.5 | +1.59 | +0.051 | 0.56 | 0.42 | There is a fable that tells how the abbe was able to stay up until dawn because the light  |
| scenario-callback-7ca729b6 | callback | sample1 | 32 | -76.9 | +2.72 | +0.085 | 0.56 | 0.33 | It is the duty of a lighthouse to keep a warning about the danger of a vessel's approach t |
| scenario-callback-7ca729b6 | callback | sample2 | 22 | -45.1 | -0.85 | -0.039 | 0.50 | 0.56 | It was by chance that the books of the lighthouse are also the books of the karma. |
| scenario-callback-7ca729b6 | callback | sample3 | 41 | -73.5 | +4.00 | +0.098 | 0.50 | 0.33 | The dome of the lighthouse is supported by a network of five to ten pillars, the number of |
| scenario-callback-949d8fe6 | callback | greedy | 26 | -58.6 | -2.36 | -0.091 | 0.33 | 0.23 | Tobias has been prommoting for years that the moon landing was a propaganda job staged by  |
| scenario-callback-949d8fe6 | callback | sample0 | 22 | -43.8 | +1.79 | +0.081 | 0.80 | 0.18 | It's a fact of life that when someone disagrees with you, you feel obligated to reply. |
| scenario-callback-949d8fe6 | callback | sample1 | 15 | -61.4 | +0.60 | +0.040 | 0.75 | 0.18 | Bux got the facts right, you failed to notice the calendar difference. |
| scenario-callback-949d8fe6 | callback | sample2 | 20 | -45.6 | -2.33 | -0.117 | 0.71 | 0.14 | If both times are correct, then surely tobias is right and weve been misinformed. |
| scenario-callback-949d8fe6 | callback | sample3 | 19 | -57.9 | +0.57 | +0.030 | 0.50 | 0.23 | Tobias, I doubt your first question ever was clear-minded in the first place. |
| scenario-callback-9cfde584 | callback | greedy | 6 | -9.6 | -0.91 | -0.151 | 0.00 | 1.00 | Tea in the back. |
| scenario-callback-9cfde584 | callback | sample0 | 12 | -36.1 | +2.38 | +0.198 | 0.60 | 0.50 | Here The Tea Conspiracy is counting on you. |
| scenario-callback-9cfde584 | callback | sample1 | 22 | -72.9 | +1.80 | +0.082 | 0.20 | 1.00 | Tea in the back is a funny tradition from a place that never really left the bedroom entir |
| scenario-callback-9cfde584 | callback | sample2 | 9 | -23.3 | +0.36 | +0.040 | 0.75 | 0.17 | Are you a guest or a fighter? |
| scenario-callback-9cfde584 | callback | sample3 | 14 | -33.2 | +2.14 | +0.153 | 0.60 | 0.50 | Tea for the ones who will not be disturbed tonight. |
| scenario-callback-9e6d06e0 | callback | greedy | 7 | -18.4 | +3.34 | +0.477 | 0.20 | 1.00 | The meeting will be at nine. |
| scenario-callback-9e6d06e0 | callback | sample0 | 21 | -52.3 | -2.97 | -0.141 | 0.00 | 0.80 | One can go to the meeting at nine in the morning or at the session at nine in the evening. |
| scenario-callback-9e6d06e0 | callback | sample1 | 6 | -18.2 | +5.65 | +0.942 | 0.00 | 1.00 | The meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample2 | 6 | -18.4 | +0.03 | +0.005 | 0.00 | 1.00 | the meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample3 | 13 | -16.6 | +1.00 | +0.077 | 0.20 | 1.00 | The meeting will be called to order at nine o'clock. |
| scenario-callback-a141de7e | callback | greedy | 60 | -134.1 | -3.65 | -0.061 | 0.67 | 0.23 | At 10:45 p.m. EST, she will land in Lisbon, landing trans-Pleranian, through the Azores, i |
| scenario-callback-a141de7e | callback | sample0 | 31 | -81.1 | -1.81 | -0.058 | 0.75 | 0.21 | At the first breeze the lovely young woman vivaciously exclaims: “We're flying to Sao Paol |
| scenario-callback-a141de7e | callback | sample1 | 36 | -97.5 | -2.88 | -0.080 | 0.50 | 0.38 | At a time when the world is in the grip of an apocalyptic spirit, it is fitting tiiose we  |
| scenario-callback-a141de7e | callback | sample2 | 37 | -92.2 | +0.01 | +0.000 | 0.50 | 0.38 | At a time when tradi¬ tional Brazil is closing the market to foreign competition, Aerolite |
| scenario-callback-a141de7e | callback | sample3 | 64 | -206.3 | +2.66 | +0.042 | 0.50 | 0.19 | Atwood's lovely description of the plane's long, juvenile journey in the out-of-the-way-fr |
| scenario-callback-c4f608c3 | callback | greedy | 10 | -34.6 | -0.13 | -0.013 | 0.67 | 0.29 | We talked about the machines, not the meals. |
| scenario-callback-c4f608c3 | callback | sample0 | 64 | -139.3 | +4.31 | +0.067 | 0.67 | 0.14 | Without the river, there would be no ice or water in the cup, no nectar in the tree, no bl |
| scenario-callback-c4f608c3 | callback | sample1 | 43 | -146.6 | +1.24 | +0.029 | 0.67 | 0.29 | And I said that the fact that we didn't actually reach the land on which the discovery was |
| scenario-callback-c4f608c3 | callback | sample2 | 9 | -26.6 | +2.58 | +0.286 | 0.83 | 0.00 | So, rays, what do you say? |
| scenario-callback-c4f608c3 | callback | sample3 | 22 | -71.5 | +3.52 | +0.160 | 0.83 | 0.09 | A river runs deep; eddies tumble; it carves a vale for a castle. |
| scenario-callback-d79a0d3a | callback | greedy | 8 | -10.5 | -2.59 | -0.324 | 0.00 | 0.50 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample0 | 8 | -10.5 | -2.59 | -0.324 | 0.00 | 0.50 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample1 | 8 | -10.5 | -2.59 | -0.324 | 0.00 | 0.50 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample2 | 17 | -38.3 | -1.73 | -0.102 | 0.50 | 0.50 | Excuse me, I forgot that was the word for the door too. |
| scenario-callback-d79a0d3a | callback | sample3 | 8 | -10.5 | -2.59 | -0.324 | 0.00 | 0.50 | What was the word ember said? |
| scenario-callback-d8a5957e | callback | greedy | 18 | -20.0 | +0.69 | +0.038 | 0.00 | 1.00 | The one with the blue cover? Tell me something about the one with the blue cover. |
| scenario-callback-d8a5957e | callback | sample0 | 28 | -22.0 | +1.39 | +0.050 | 0.00 | 1.00 | The one with the blue cover? The one with the blue cover? The one with the blue cover? The |
| scenario-callback-d8a5957e | callback | sample1 | 16 | -21.3 | +5.17 | +0.323 | 0.00 | 1.00 | The one with the blue cover? Tell me about what your book is about. |
| scenario-callback-d8a5957e | callback | sample2 | 22 | -55.0 | +4.37 | +0.199 | 0.40 | 0.60 | The wingcase of this European bee appears to have a blue cover, while the comb is blue-bla |
| scenario-callback-d8a5957e | callback | sample3 | 31 | -87.9 | +4.65 | +0.150 | 0.75 | 0.20 | Workers seated at the honeycomb cells have tiny tubes or trumpet-like hives through which  |
| scenario-direct-3f84da0f | direct | greedy | 55 | -114.6 | +0.00 | +0.000 | 0.50 | 0.42 | Before we came in, the instructor was going to present a paper on "Ethics and its Relation |
| scenario-direct-3f84da0f | direct | sample0 | 44 | -123.0 | +0.00 | +0.000 | 0.50 | 0.42 | Before we came in, the thing was in the dusk ~ sky, still moving, a brilliant blue light l |
| scenario-direct-3f84da0f | direct | sample1 | 29 | -68.3 | +0.00 | +0.000 | 0.67 | 0.24 | As you can see from the picture I was wearing a black Prabolan shirt, black pants, and bla |
| scenario-direct-3f84da0f | direct | sample2 | 40 | -71.8 | +0.00 | +0.000 | 0.50 | 0.21 | For the last time, dear reader, we ask if you are ready to accept the implications of a un |
| scenario-direct-3f84da0f | direct | sample3 | 20 | -70.7 | +0.00 | +0.000 | 0.56 | 0.42 | Before we came in, the server washed down the chests with iced-tea. |
| scenario-direct-5d3dc8de | direct | greedy | 9 | -24.3 | +0.00 | +0.000 | 0.50 | 0.60 | Something is true which is not true. |
| scenario-direct-5d3dc8de | direct | sample0 | 18 | -62.3 | +0.00 | +0.000 | 0.75 | 0.17 | The heckler hopes that the attention this will draw will compensate for his silence. |
| scenario-direct-5d3dc8de | direct | sample1 | 58 | -154.4 | +0.00 | +0.000 | 0.65 | 0.22 | Of course, Peirce was not entirely objective when he wrote, in the February 6 letter to Be |
| scenario-direct-5d3dc8de | direct | sample2 | 37 | -136.6 | +0.00 | +0.000 | 0.50 | 0.40 | Something else occurs to the mind that is both pleasured and strange: the idea that the cy |
| scenario-direct-5d3dc8de | direct | sample3 | 17 | -48.2 | +0.00 | +0.000 | 0.50 | 0.60 | Something which, though unassailably true, seems unassailable. |
| scenario-direct-645bc6e6 | direct | greedy | 22 | -14.8 | +0.00 | +0.000 | 0.62 | 0.50 | “In the beginning was the Word, and the Word was with God, and the Word was God. |
| scenario-direct-645bc6e6 | direct | sample0 | 64 | -151.3 | +0.00 | +0.000 | 0.50 | 0.38 | “In order to publish, you must first obtain a printer and have a printer’s license from th |
| scenario-direct-645bc6e6 | direct | sample1 | 54 | -191.0 | +0.00 | +0.000 | 0.67 | 0.50 | “In olden days,TION OF THE CONSCIOUSNESS REVOLUTION (1066-1377) was nearly eighteen years  |
| scenario-direct-645bc6e6 | direct | sample2 | 23 | -64.7 | +0.00 | +0.000 | 0.43 | 0.25 | The oldest thing Lacan has read, to be fair, is the Surrealist Manifesto. |
| scenario-direct-645bc6e6 | direct | sample3 | 31 | -73.7 | +0.00 | +0.000 | 0.67 | 0.33 | “The Grail” is said to have been written in 1178, but that is only 40 years before its tim |
| scenario-direct-ab11ffdb | direct | greedy | 29 | -78.8 | +0.00 | +0.000 | 0.75 | 0.29 | The water of the chaos, the water of the sea, the water under the earth, all these were co |
| scenario-direct-ab11ffdb | direct | sample0 | 8 | -21.5 | +0.00 | +0.000 | 0.00 | 0.43 | What do you make of the rain. |
| scenario-direct-ab11ffdb | direct | sample1 | 29 | -128.2 | +0.00 | +0.000 | 0.50 | 0.16 | The physicist models the solar system on a sphere, which can turn its top and which in thi |
| scenario-direct-ab11ffdb | direct | sample2 | 18 | -30.2 | +0.00 | +0.000 | 0.80 | 0.30 | It seems that wherever there is strong evaporation, there is also strong precipitation. |
| scenario-direct-ab11ffdb | direct | sample3 | 33 | -100.7 | +0.00 | +0.000 | 0.62 | 0.43 | The physicist is supposed to break the water drop into particles, showing that the drop of |
| scenario-direct-ad89f803 | direct | greedy | 17 | -42.6 | +0.00 | +0.000 | 0.67 | 0.23 | The only thing that separates a prison from a laboratory is the absence of light. |
| scenario-direct-ad89f803 | direct | sample0 | 20 | -61.0 | +0.00 | +0.000 | 0.75 | 0.31 | The tallest and the fastest and the one with the most amazing burst of energy were there. |
| scenario-direct-ad89f803 | direct | sample1 | 21 | -75.8 | +0.00 | +0.000 | 0.67 | 0.17 | The Seventh Ray, or Rays, deals in terrestrial evolution, human so-called. |
| scenario-direct-ad89f803 | direct | sample2 | 46 | -183.1 | +0.00 | +0.000 | 0.67 | 0.23 | The moon is a giant electric megaminute plasma container that's just slowly erasing its bl |
| scenario-direct-ad89f803 | direct | sample3 | 64 | -139.1 | +0.00 | +0.000 | 0.67 | 0.31 | The Sustaining Members—PURPOSE AND POLUTONYM The International Society of Cryptozoology wa |
| scenario-direct-f3869322 | direct | greedy | 43 | -98.2 | +0.00 | +0.000 | 0.50 | 0.22 | It is a gift that has been denied many times, but is finally being granted in the sense th |
| scenario-direct-f3869322 | direct | sample0 | 64 | -156.0 | +0.00 | +0.000 | 0.50 | 0.22 | But, none of the evils that man has made, none of the discoveries that he has had to make  |
| scenario-direct-f3869322 | direct | sample1 | 28 | -113.5 | +0.00 | +0.000 | 0.50 | 0.14 | No matter what month you live through the people who are going to be working for the Elder |
| scenario-direct-f3869322 | direct | sample2 | 62 | -144.4 | +0.00 | +0.000 | 1.00 | 0.05 | 1 or 2 early poems by Chateaubriand, 3 or 4 prose pieces by Kandinsky, Mallarme by Celan,  |
| scenario-direct-f3869322 | direct | sample3 | 16 | -46.6 | +0.00 | +0.000 | 0.83 | 0.12 | Well, you should, because there's nothin' else available. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 8 | -8.7 | +1.91 | +0.239 | 0.50 | 0.75 | Brown, the brown of the leaves. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 22 | -70.2 | +4.81 | +0.219 | 0.60 | 0.50 | And the colored fixtures, those graceful and sparkling, speak of far-wandering colors. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 8 | -8.7 | +1.91 | +0.239 | 0.50 | 0.75 | Brown, the brown of the leaves. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 9 | -17.4 | +1.04 | +0.116 | 0.40 | 0.75 | Brown, the color of new lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 9 | -7.7 | -1.97 | -0.218 | 0.00 | 0.60 | Green, the green of old lamps. |
| scenario-disagreement-31892fde | disagreement | greedy | 15 | -50.0 | -5.11 | -0.341 | 0.64 | 0.36 | When the time comes to walk the tight is never too tight to hold. |
| scenario-disagreement-31892fde | disagreement | sample0 | 13 | -40.7 | -13.13 | -1.010 | 0.57 | 0.29 | Consciousness is the product of the interaction of the two. |
| scenario-disagreement-31892fde | disagreement | sample1 | 22 | -77.9 | -23.57 | -1.071 | 0.62 | 0.36 | When the gate is kept and no one escapes, there is no need to open it to begin with. |
| scenario-disagreement-31892fde | disagreement | sample2 | 44 | -145.9 | -37.33 | -0.849 | 0.25 | 0.25 | Golden is a beautiful sister, who has been around longer than silence. Golden doesn't get  |
| scenario-disagreement-31892fde | disagreement | sample3 | 17 | -57.6 | -20.68 | -1.217 | 0.54 | 0.36 | But there is a time when you have nothing to say, silenced by what? |
| scenario-disagreement-352205c6 | disagreement | greedy | 7 | -4.3 | +8.00 | +1.143 | 0.17 | 0.67 | They come back as the sun. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 61 | -221.5 | -22.36 | -0.367 | 0.67 | 0.20 | It has been suggested that, although there is no direct evidence, that the lost flesh prin |
| scenario-disagreement-352205c6 | disagreement | sample1 | 12 | -34.8 | -2.13 | -0.178 | 0.50 | 0.62 | As soon as you look into it they are all back. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 10 | -17.4 | +4.29 | +0.429 | 0.33 | 0.67 | As soon as you see them they come back. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 13 | -43.0 | -11.57 | -0.890 | 0.33 | 0.67 | The dead come back as well as the bodies of brave men. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 16 | -33.6 | +2.02 | +0.126 | 0.50 | 0.73 | Spring, when the flowers are dying and the sun is in the underworld. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 10 | -39.2 | -7.52 | -0.752 | 0.25 | 0.50 | The books when read are not in the atmosphere. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 20 | -47.1 | -12.22 | -0.611 | 0.58 | 0.73 | Spring, when the sun shines in, and the flowers bloom, and the air is clear. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 34 | -105.8 | -13.54 | -0.398 | 0.50 | 0.38 | For the gods, for the gods, for the gods of the earth, what sounds like wisdom and what so |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 23 | -87.2 | -13.54 | -0.589 | 0.44 | 0.50 | True, when the mind is not distracted by the vision of God, and all things are turning tow |
| scenario-disagreement-682bad9c | disagreement | greedy | 9 | -14.2 | +1.56 | +0.173 | 0.57 | 0.38 | A place where you can go and read. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 30 | -69.9 | +4.40 | +0.147 | 0.40 | 0.50 | Reading in a person is someone else reading to you, trying to figure out what you’re sayin |
| scenario-disagreement-682bad9c | disagreement | sample1 | 11 | -23.9 | -5.43 | -0.494 | 0.00 | 0.71 | Sometimes, a place where reading happens is a person. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 10 | -32.0 | -3.85 | -0.385 | 0.29 | 0.71 | Lycan is a system where reading happens. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 15 | -33.1 | -4.64 | -0.309 | 0.43 | 0.50 | Between a person and a place, a reader is always in the middle. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 10 | -22.4 | +1.02 | +0.102 | 0.67 | 0.67 | Relationships are not contained; they are free. |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 24 | -50.7 | -5.09 | -0.212 | 0.50 | 0.67 | Relationships are not taken up with the walls of a building, they are taken up with the co |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 11 | -24.2 | +2.65 | +0.240 | 0.50 | 0.44 | All the different types of libraries are systems of relationships. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 16 | -56.4 | -5.50 | -0.344 | 0.60 | 0.33 | Relationships never die. They keep bringing forth what is needed where it is. |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 44 | -70.1 | -14.85 | -0.337 | 0.40 | 0.11 | First, there is the relationship between the donor and the recipient; then, there is the r |
| scenario-disagreement-89dfdafc | disagreement | greedy | 21 | -34.4 | -1.23 | -0.059 | 0.25 | 0.40 | The tide is the sea's memory, and the sea is the rat's rat race. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 34 | -30.2 | +1.15 | +0.034 | 0.50 | 0.40 | When the moon is waxing, the tide is furthest out, and when it is waning, the tide is furt |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 11 | -27.7 | -0.94 | -0.086 | 0.50 | 0.29 | Tidal rivers are the greatest rivers in the world. |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 15 | -35.4 | +1.62 | +0.108 | 0.50 | 0.30 | The whole point of tides is just that, misdirected memory. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 12 | -22.7 | -2.35 | -0.196 | 0.75 | 0.33 | The tide never forgets what it was built for. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 27 | -70.2 | -4.38 | -0.162 | 0.50 | 0.36 | The sense of the collection has been ‘found’ by the senseless, and so it is, in a very imp |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 38 | -120.3 | -6.23 | -0.164 | 0.62 | 0.33 | The wildest and most incredible tales were told by the Sphinx as it walked the surface of  |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 24 | -64.4 | -6.62 | -0.276 | 0.50 | 0.50 | The world’s collection of things that are mainly senseless is the world’s Boy Scout troop. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 64 | -168.0 | -4.64 | -0.072 | 0.50 | 0.36 | A better reckoning is hinged on a mistranslation, into Greek, of a popular pronunciation i |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 25 | -89.2 | -12.25 | -0.490 | 0.50 | 0.50 | The sense of the solid world is extended to include also the solid world of art—of things  |
| scenario-joke-29f5cda1 | joke | greedy | 11 | -28.5 | +2.29 | +0.208 | 0.67 | 1.00 | Ten is a fish without an eye to swim in. |
| scenario-joke-29f5cda1 | joke | sample0 | 29 | -104.3 | +11.74 | +0.405 | 0.67 | 0.30 | “Eat, you magicians,” was rated by one of the men sitting next to me an ace, by another a  |
| scenario-joke-29f5cda1 | joke | sample1 | 16 | -29.2 | +9.91 | +0.620 | 0.00 | 0.33 | Rate that joke out of ten. Rate that joke out of ten. |
| scenario-joke-29f5cda1 | joke | sample2 | 22 | -71.3 | -0.20 | -0.009 | 0.71 | 0.33 | Ten. It has four blue eyes, five arms, and a total of six dorsal fins. |
| scenario-joke-29f5cda1 | joke | sample3 | 8 | -15.3 | +2.23 | +0.279 | 0.71 | 1.00 | Ten is a fish without an eye. |
| scenario-joke-31378921 | joke | greedy | 6 | -7.4 | +3.87 | +0.645 | 0.00 | 0.25 | Knock on the door. |
| scenario-joke-31378921 | joke | sample0 | 10 | -18.7 | -0.34 | -0.034 | 0.75 | 0.00 | I’m just trying to get in here. |
| scenario-joke-31378921 | joke | sample1 | 8 | -7.5 | +8.38 | +1.048 | 0.00 | 0.25 | A rat and a lettuce. |
| scenario-joke-31378921 | joke | sample2 | 9 | -13.3 | +1.38 | +0.153 | 0.00 | 0.25 | Please do not eat the lettuce. |
| scenario-joke-31378921 | joke | sample3 | 10 | -20.4 | -0.07 | -0.007 | 0.50 | 0.25 | You are the queen of all the rats. |
| scenario-joke-31c4c1ec | joke | greedy | 24 | -68.9 | +0.00 | +0.000 | 0.67 | 0.29 | The "voice" of the roasting rat goes on for hours, describing his masters in detail. |
| scenario-joke-31c4c1ec | joke | sample0 | 32 | -86.9 | +0.00 | +0.000 | 0.82 | 0.14 | No one is suggesting that you stop eating because "G" has invented some new, enigmatic, da |
| scenario-joke-31c4c1ec | joke | sample1 | 18 | -30.0 | +0.00 | +0.000 | 0.67 | 0.29 | Roasting the Scorpion is like roasting a live scorpion. |
| scenario-joke-31c4c1ec | joke | sample2 | 17 | -39.0 | +0.00 | +0.000 | 0.75 | 0.14 | But if it did not come, the sheep would not have been roasted. |
| scenario-joke-31c4c1ec | joke | sample3 | 48 | -82.8 | +0.00 | +0.000 | 0.67 | 0.29 | In his book, "Absurd Ideas", Keel presents the startling premise that the Great Pyramid of |
| scenario-joke-475a7b10 | joke | greedy | 62 | -107.9 | +3.94 | +0.064 | 0.50 | 0.20 | (The fact that the "powers that be" are "in the dark" about the true nature of the mind an |
| scenario-joke-475a7b10 | joke | sample0 | 17 | -49.8 | +2.20 | +0.130 | 0.83 | 0.23 | (For some reason this doesn’t seem to work on a cell phone.) |
| scenario-joke-475a7b10 | joke | sample1 | 32 | -78.0 | +1.34 | +0.042 | 0.83 | 0.31 | Recently, I took a 27-year-old man to a woods gypie for a "spell" of group therapy. |
| scenario-joke-475a7b10 | joke | sample2 | 39 | -114.3 | +0.08 | +0.002 | 0.50 | 0.31 | Recently, I had the opportunity to participate in an ICLG workshop with a French speaker w |
| scenario-joke-475a7b10 | joke | sample3 | 55 | -173.0 | +1.66 | +0.030 | 0.50 | 0.20 | Advertisers who say “fools will fall for it” or “get fat and gay for a dollar” or “do it w |
| scenario-joke-99a4a91d | joke | greedy | 64 | -131.0 | +0.00 | +0.000 | 0.50 | 0.40 | The book went to the doctor because, according to its informative text, ‘Moralia’ (Latin f |
| scenario-joke-99a4a91d | joke | sample0 | 28 | -91.9 | +0.00 | +0.000 | 0.75 | 0.22 | Books are not immune to “going astray”—they are just universally easier to “track” than pe |
| scenario-joke-99a4a91d | joke | sample1 | 15 | -59.0 | +0.00 | +0.000 | 0.33 | 0.23 | Book had been returned to the library but was still in the same room. |
| scenario-joke-99a4a91d | joke | sample2 | 11 | -41.7 | +0.00 | +0.000 | 0.50 | 0.22 | Books are like the most precious of all possessions. |
| scenario-joke-99a4a91d | joke | sample3 | 20 | -38.6 | +0.00 | +0.000 | 0.50 | 0.40 | The book went to the doctor so that he could give it to a person who deserved it. |
| scenario-joke-a6247299 | joke | greedy | 11 | -16.7 | +0.00 | +0.000 | 0.50 | 1.00 | A sense of humour is the ability to laugh. |
| scenario-joke-a6247299 | joke | sample0 | 25 | -43.7 | +0.00 | +0.000 | 0.50 | 1.00 | A sense of humour is the ability to laugh, and it’s pretty rare for people to actually lau |
| scenario-joke-a6247299 | joke | sample1 | 27 | -73.2 | +0.00 | +0.000 | 0.50 | 0.67 | There is also, in my lectures, a very deep sense of humour, as the very deep humour of a r |
| scenario-joke-a6247299 | joke | sample2 | 15 | -32.9 | +0.00 | +0.000 | 0.62 | 0.44 | You don't have to be a hermit to enjoy life. |
| scenario-joke-a6247299 | joke | sample3 | 39 | -82.5 | +0.00 | +0.000 | 0.50 | 0.56 | With regard to the subject of humor, it may be added that I have a very poetic sense of it |
| scenario-joke-e8ab9225 | joke | greedy | 13 | -36.5 | -3.93 | -0.302 | 0.33 | 0.71 | I am not the library, but I am the dove. |
| scenario-joke-e8ab9225 | joke | sample0 | 37 | -91.1 | -2.07 | -0.056 | 0.33 | 0.57 | I will not argue with you, I am Doom, the dovetail of the universe, and I am backing up Qu |
| scenario-joke-e8ab9225 | joke | sample1 | 31 | -51.1 | -0.24 | -0.008 | 0.33 | 0.57 | I will not go away because I have no choice. I have been haunted by you from the first mom |
| scenario-joke-e8ab9225 | joke | sample2 | 17 | -22.5 | +2.94 | +0.173 | 0.56 | 0.43 | I don't believe in the ghost, but I do believe in Dov. |
| scenario-joke-e8ab9225 | joke | sample3 | 18 | -59.0 | -3.14 | -0.174 | 0.33 | 0.71 | I am not the library, you informed me that you had a copy of this book. |
| scenario-joke-e9cf6a04 | joke | greedy | 27 | -71.5 | -23.02 | -0.853 | 0.33 | 0.67 | There was a librarian like that, who had a lady in the library who was in the mood for a j |
| scenario-joke-e9cf6a04 | joke | sample0 | 12 | -34.6 | -3.06 | -0.255 | 0.60 | 0.45 | There was an old man who had a very dirty record. |
| scenario-joke-e9cf6a04 | joke | sample1 | 14 | -31.4 | +0.19 | +0.013 | 0.33 | 0.67 | There was a book in the library, titled The Witness Book. |
| scenario-joke-e9cf6a04 | joke | sample2 | 37 | -67.3 | -13.21 | -0.357 | 0.50 | 0.62 | It was the library that said, “hello, hello, hello, I need to find a book, I need a book,  |
| scenario-joke-e9cf6a04 | joke | sample3 | 25 | -69.5 | -15.05 | -0.602 | 0.33 | 0.62 | It was the library that said, “What’s a good time of year to be in a movie theatre?” |
| scenario-request-2826c958 | request | greedy | 17 | -32.3 | +0.00 | +0.000 | 0.50 | 0.88 | The five lamentations from the Book of Lamentations are: 1. |
| scenario-request-2826c958 | request | sample0 | 29 | -72.4 | +0.00 | +0.000 | 0.50 | 0.88 | The five lamentations from the Ancient Egyptian sky Goddess version of the moon are as fol |
| scenario-request-2826c958 | request | sample1 | 37 | -93.3 | +0.00 | +0.000 | 0.50 | 0.38 | Above, and opposite, the maria, are the craters Tycho and Cos, of about the same size as t |
| scenario-request-2826c958 | request | sample2 | 39 | -117.4 | +0.00 | +0.000 | 0.50 | 0.38 | It may be conclu s ed that data on the moon are incomplete, that some interpretations of t |
| scenario-request-2826c958 | request | sample3 | 16 | -44.5 | +0.00 | +0.000 | 0.29 | 0.36 | The five discriminating facts about the moon, as posed by M.K. |
| scenario-request-2868e594 | request | greedy | 22 | -58.6 | +0.00 | +0.000 | 0.58 | 0.20 | Dear [the unnamed], I am very sorry that I can no longer write your cover letter. |
| scenario-request-2868e594 | request | sample0 | 43 | -141.1 | +0.00 | +0.000 | 0.67 | 0.29 | Dear [the organization], we have been through a review process at our previous [unillumina |
| scenario-request-2868e594 | request | sample1 | 45 | -107.4 | +0.00 | +0.000 | 0.67 | 0.43 | Before you sign this off, we would like you to get a copy of the "Welcome Matters" brochur |
| scenario-request-2868e594 | request | sample2 | 21 | -64.0 | +0.00 | +0.000 | 0.75 | 0.43 | Dear […] Would appreciate it if you could send me hard copy of the advertisement. |
| scenario-request-2868e594 | request | sample3 | 35 | -71.6 | +0.00 | +0.000 | 0.50 | 0.29 | Also, the Studio has been fortunate enough to exhibit a "signature” work by an important a |
| scenario-request-41c58fb2 | request | greedy | 25 | -84.7 | +0.00 | +0.000 | 0.60 | 0.50 | Marital Conflicts spouse problems, bride and party crash, what's a couple of dozen times a |
| scenario-request-41c58fb2 | request | sample0 | 28 | -82.5 | +0.00 | +0.000 | 0.83 | 0.13 | However, we cannot consider them both as raising Hell, because Hell is a unified force, no |
| scenario-request-41c58fb2 | request | sample1 | 19 | -55.2 | +0.00 | +0.000 | 0.91 | 0.09 | Absolutely no hunting or fishing (except, of course, for aberrated individuals). |
| scenario-request-41c58fb2 | request | sample2 | 25 | -69.3 | +0.00 | +0.000 | 0.91 | 0.09 | Negative Logarithms and Exponential Equations Negative logarithms and negative exponential |
| scenario-request-41c58fb2 | request | sample3 | 11 | -25.3 | +0.00 | +0.000 | 0.00 | 0.50 | What's 17 times 23. |
| scenario-request-8aa8e374 | request | greedy | 16 | -47.2 | +0.00 | +0.000 | 0.70 | 0.40 | There is nothing to say to them in French, nothing but nonsense. |
| scenario-request-8aa8e374 | request | sample0 | 33 | -91.0 | +0.00 | +0.000 | 0.65 | 0.40 | It is good to stop by at this moment and express our regards in advance, as English speake |
| scenario-request-8aa8e374 | request | sample1 | 64 | -208.8 | +0.00 | +0.000 | 0.67 | 0.14 | Its usage is quite natural because the late is almost always followed by the flower of the |
| scenario-request-8aa8e374 | request | sample2 | 64 | -174.2 | +0.00 | +0.000 | 0.67 | 0.35 | They should be understood as 'By good night come' or 'Good night (i.e. by a long time, by  |
| scenario-request-8aa8e374 | request | sample3 | 21 | -78.6 | +0.00 | +0.000 | 0.64 | 0.29 | Still waiting? Answer me 'what is the weather like like' when you're in it. |
| scenario-request-b2a25087 | request | greedy | 18 | -61.2 | +0.00 | +0.000 | 0.67 | 0.10 | The customer acts as a monad with a high percentage of “yes” responses. |
| scenario-request-b2a25087 | request | sample0 | 15 | -35.5 | +0.00 | +0.000 | 0.73 | 0.20 | The best protection for the bakery is to sell only good products. |
| scenario-request-b2a25087 | request | sample1 | 12 | -34.6 | +0.00 | +0.000 | 1.00 | 0.11 | Your customers will love this fresh, crisp white cake. |
| scenario-request-b2a25087 | request | sample2 | 14 | -55.3 | +0.00 | +0.000 | 0.67 | 0.20 | Customers rushed in here to complain about the frozen dough. |
| scenario-request-b2a25087 | request | sample3 | 19 | -59.1 | +0.00 | +0.000 | 0.75 | 0.20 | Come back to the shop. Or come sit at the counter and pick up your straw. |
| scenario-request-b3bd0087 | request | greedy | 42 | -56.6 | +0.00 | +0.000 | 0.43 | 0.50 | Althouqh the weather in Berlin on Tuesday, April 20th, was partly cloudy and warm, it was  |
| scenario-request-b3bd0087 | request | sample0 | 50 | -114.3 | +0.00 | +0.000 | 0.67 | 0.19 | Already a violent and pterific storm had swept through [the town of] Göttingen on the even |
| scenario-request-b3bd0087 | request | sample1 | 64 | -153.5 | +0.00 | +0.000 | 0.57 | 0.50 | Berlin (the weather was OK yesterday) is pretty much flat — it doesn’t really affect the c |
| scenario-request-b3bd0087 | request | sample2 | 7 | -22.1 | +0.00 | +0.000 | 0.50 | 0.50 | West Berlin is in bad weather. |
| scenario-request-b3bd0087 | request | sample3 | 27 | -78.3 | +0.00 | +0.000 | 0.75 | 0.25 | The first signaling signal was received at Tucuman 27 minutes and 28 seconds after the las |
| scenario-silence-109161ca | silence | greedy | 12 | -34.4 | +3.23 | +0.269 | 0.50 | 0.27 | The following pages are presented in a state of constant change. |
| scenario-silence-109161ca | silence | sample0 | 16 | -44.6 | -4.75 | -0.297 | 0.00 | 0.36 | Night and day are the same until the light of day overtakes us. |
| scenario-silence-109161ca | silence | sample1 | 20 | -65.0 | -2.34 | -0.117 | 0.00 | 0.40 | No one talks in the deep night, no one breathes, the deep night talks through itself. |
| scenario-silence-109161ca | silence | sample2 | 34 | -46.3 | +1.01 | +0.030 | 0.00 | 0.40 | In the dead of night, when the world seems to be closing in on us, it is easy to become fi |
| scenario-silence-109161ca | silence | sample3 | 28 | -76.8 | +1.23 | +0.044 | 0.67 | 0.33 | In the past few days someone has added hundreds to the millions of dreams that have been t |
| scenario-silence-260b2639 | silence | greedy | 8 | -11.0 | +0.00 | +0.000 | 0.00 | 1.00 | What if the stacks went underground. |
| scenario-silence-260b2639 | silence | sample0 | 8 | -11.0 | +0.00 | +0.000 | 0.00 | 1.00 | What if the stacks went underground. |
| scenario-silence-260b2639 | silence | sample1 | 17 | -23.3 | +0.00 | +0.000 | 0.17 | 0.83 | "If the stacks went underground, it wouldn’t make any difference." |
| scenario-silence-260b2639 | silence | sample2 | 64 | -154.3 | +0.00 | +0.000 | 0.33 | 0.67 | If the stacks were moved so that they could not be accessed by anyone except the Grand Arc |
| scenario-silence-260b2639 | silence | sample3 | 22 | -44.3 | +0.00 | +0.000 | 0.00 | 1.00 | What if the stacks went underground, making it easier for the architects to see what was g |
| scenario-silence-46189e08 | silence | greedy | 42 | -50.0 | +0.00 | +0.000 | 0.50 | 0.25 | @rat I'm sorry to hear that. I've been trying to get in touch with you for a while now, bu |
| scenario-silence-46189e08 | silence | sample0 | 16 | -52.9 | +0.00 | +0.000 | 0.67 | 0.17 | New research has uncovered a previously hidden aspect of the ratiorz system. |
| scenario-silence-46189e08 | silence | sample1 | 11 | -26.9 | +0.00 | +0.000 | 0.75 | 0.12 | Rat just saw it and thought it was fine. |
| scenario-silence-46189e08 | silence | sample2 | 15 | -30.0 | +0.00 | +0.000 | 0.83 | 0.25 | Rat: Well that's not remotely what I meant. |
| scenario-silence-46189e08 | silence | sample3 | 26 | -42.9 | +0.00 | +0.000 | 0.65 | 0.25 | In the last part of that sentence, Crowley makes it very clear that he does not understand |
| scenario-silence-53534987 | silence | greedy | 26 | -54.3 | +7.03 | +0.270 | 0.25 | 0.42 | It was a 5500 charger, and it was in the drawer, all rusted and smashed. |
| scenario-silence-53534987 | silence | sample0 | 12 | -48.0 | +11.41 | +0.951 | 0.75 | 0.18 | The rat had given up on all search after two hours. |
| scenario-silence-53534987 | silence | sample1 | 24 | -92.5 | -1.35 | -0.056 | 0.33 | 0.42 | It was a 60-note Mozybill ten-piece set that I found in the Debby box. |
| scenario-silence-53534987 | silence | sample2 | 12 | -54.1 | +3.93 | +0.328 | 1.00 | 0.12 | I've had several come back emptying their batteries. |
| scenario-silence-53534987 | silence | sample3 | 24 | -55.2 | -3.83 | -0.160 | 0.67 | 0.33 | It should be obvious by now that there is a strong connection between the spread of misinf |
| scenario-silence-78c38840 | silence | greedy | 24 | -67.6 | +4.51 | +0.188 | 0.50 | 0.25 | You have been very patient about your requests, and the delay in getting your book printed |
| scenario-silence-78c38840 | silence | sample0 | 20 | -43.8 | -3.75 | -0.187 | 0.67 | 0.20 | The material should be printed at a rate of 40 to 45 lines per inch. |
| scenario-silence-78c38840 | silence | sample1 | 13 | -46.6 | -5.89 | -0.453 | 0.78 | 0.22 | My little book of 108 pages is almost done. |
| scenario-silence-78c38840 | silence | sample2 | 47 | -150.8 | +5.10 | +0.108 | 0.67 | 0.25 | My 13 year old niece wrote me a very similar letter: i'm having trouble with my typewriter |
| scenario-silence-78c38840 | silence | sample3 | 15 | -55.9 | -1.06 | -0.071 | 0.67 | 0.25 | I allow the printer to work without interference, and expect it to produce. |
| scenario-silence-7afca726 | silence | greedy | 35 | -65.8 | +6.33 | +0.181 | 0.65 | 0.29 | It is customary to think of the first three chapters of the Book of Changes as containing  |
| scenario-silence-7afca726 | silence | sample0 | 17 | -32.2 | -1.29 | -0.076 | 0.67 | 0.29 | The second law says that the total entropy of a closed system always increases over time. |
| scenario-silence-7afca726 | silence | sample1 | 7 | -15.6 | +0.81 | +0.116 | 0.75 | 0.25 | That's the magic number. |
| scenario-silence-7afca726 | silence | sample2 | 16 | -45.1 | +4.16 | +0.260 | 0.67 | 0.29 | It is a major event that will fascinate the hearts of all who attend. |
| scenario-silence-7afca726 | silence | sample3 | 15 | -44.6 | +6.85 | +0.457 | 0.50 | 0.25 | You are now ready for a deeper aspect of the Nagual Experience. |
| scenario-silence-9bb13f03 | silence | greedy | 42 | -95.0 | +0.00 | +0.000 | 0.67 | 0.19 | The editors of the MCEO Freedom Teachings library present their first collection of though |
| scenario-silence-9bb13f03 | silence | sample0 | 59 | -156.7 | +0.00 | +0.000 | 0.50 | 0.19 | The first book, The Secret History of America's Clones, begins by examining cloning in the |
| scenario-silence-9bb13f03 | silence | sample1 | 40 | -49.4 | +0.00 | +0.000 | 0.75 | 0.18 | The editorial board of Cryptozoology includes biologists, vertebrate paleontologists, and  |
| scenario-silence-9bb13f03 | silence | sample2 | 35 | -92.0 | +0.00 | +0.000 | 0.67 | 0.13 | It is therefore the duty of the Seven-Spirit, SEVENED, to make this knowledge available as |
| scenario-silence-9bb13f03 | silence | sample3 | 46 | -132.8 | +0.00 | +0.000 | 0.50 | 0.19 | The last four chapters deal with the physical nature of the elements, how they contract an |
| scenario-silence-ccfdd2b4 | silence | greedy | 11 | -28.7 | +0.56 | +0.051 | 0.67 | 0.44 | The first thing to check for is air leaks. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 20 | -53.5 | +3.87 | +0.194 | 0.67 | 0.25 | Imagine this. Two people in adjacent rooms, each with a candle and a sheet of paper. |
| scenario-silence-ccfdd2b4 | silence | sample1 | 20 | -59.6 | -1.83 | -0.091 | 0.67 | 0.25 | That is, in fact, a semantically transparent instance of 'anaphoric capture.' |
| scenario-silence-ccfdd2b4 | silence | sample2 | 21 | -47.9 | -3.28 | -0.156 | 0.75 | 0.44 | The second thing that I want to know is why did this coin come to the attention of the pol |
| scenario-silence-ccfdd2b4 | silence | sample3 | 9 | -25.3 | +0.06 | +0.006 | 0.67 | 0.00 | Important job. Get Coffee. |
| trace-ambient-da12ae42 | ambient | greedy | 64 | -30.0 | -1.50 | -0.024 | 0.00 | 0.12 | > We demonstrate that the presence of FTO stimulates root meristem cell proliferation and  |
| trace-ambient-da12ae42 | ambient | sample0 | 11 | -25.2 | -0.53 | -0.048 | 0.00 | 0.14 | it's a good thing, sometimes forget is better |
| trace-ambient-da12ae42 | ambient | sample1 | 28 | -56.6 | +3.11 | +0.111 | 0.73 | 0.12 | by "morphogenesis" i mean "the process by which plants maintain their individual identity  |
| trace-ambient-da12ae42 | ambient | sample2 | 13 | -31.5 | -0.09 | -0.007 | 0.83 | 0.14 | you're a botanist? what makes you special? |
| trace-ambient-da12ae42 | ambient | sample3 | 17 | -18.0 | +1.07 | +0.063 | 0.09 | 0.12 | it's bizarre to me but i'll accept it at face value |
| trace-direct-115cf61c | direct | greedy | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 0.33 | Are you cogent? |
| trace-direct-115cf61c | direct | sample0 | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 0.33 | Are you cogent? |
| trace-direct-115cf61c | direct | sample1 | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 0.33 | Are you cogent? |
| trace-direct-115cf61c | direct | sample2 | 7 | -10.0 | +0.00 | +0.000 | 0.50 | 0.75 | The Earth is cogent. |
| trace-direct-115cf61c | direct | sample3 | 22 | -44.1 | +0.00 | +0.000 | 0.50 | 0.75 | Planet Earth, we do not appear to be cogent; cogency is an attribute of Earth. |
| trace-direct-36d6904b | direct | greedy | 19 | -38.5 | +0.00 | +0.000 | 0.75 | 0.22 | "George, don't worry about the weather. We'll make it. |
| trace-direct-36d6904b | direct | sample0 | 30 | -58.9 | +0.00 | +0.000 | 0.93 | 0.22 | "George, don't panic! I'm waiting for you! Come on upstairs and let me show you around!" |
| trace-direct-36d6904b | direct | sample1 | 64 | -221.3 | +0.00 | +0.000 | 0.67 | 0.11 | "Adveni, felix, qui abstainingi suffocationem custodem, qui ex oppressu concupiscitu, qui  |
| trace-direct-36d6904b | direct | sample2 | 22 | -73.1 | +0.00 | +0.000 | 0.50 | 0.16 | The Record is our only criterion in selecting among the many valuable phenomena of human a |
| trace-direct-36d6904b | direct | sample3 | 52 | -79.2 | +0.00 | +0.000 | 0.50 | 0.16 | The term "catastrophics" was first used in the literature of the 1 960s to refer to a new  |
| trace-direct-39be6df9 | direct | greedy | 11 | -4.6 | +0.89 | +0.081 | 0.00 | 1.00 | 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 11 | -4.6 | +0.89 | +0.081 | 0.00 | 1.00 | 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 16 | -2.5 | +4.35 | +0.272 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample2 | 47 | -72.6 | -0.92 | -0.019 | 0.00 | 1.00 | (I'm g@ring the window, please, W@) Sir :D<eot> 3221229683 — 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 18 | -17.3 | +0.66 | +0.037 | 0.33 | 1.00 | @a GREETINGS 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 8 | -11.6 | +0.00 | +0.000 | 0.71 | 0.71 | I am the king of this planet. |
| trace-direct-3ba68854 | direct | sample0 | 15 | -22.3 | +0.00 | +0.000 | 0.71 | 0.71 | I am the ruler of this place. I am ruler of this place. |
| trace-direct-3ba68854 | direct | sample1 | 5 | -9.0 | +0.00 | +0.000 | 0.50 | 0.25 | Who wants to speak? |
| trace-direct-3ba68854 | direct | sample2 | 18 | -39.8 | +0.00 | +0.000 | 0.75 | 0.57 | Well, I am making sure I do not miss any of the day's work. |
| trace-direct-3ba68854 | direct | sample3 | 14 | -36.6 | +0.00 | +0.000 | 0.67 | 0.29 | i hope we will have a chance to meet the natives again. |
| trace-direct-41c6eb11 | direct | greedy | 16 | -3.3 | +0.68 | +0.042 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 13 | -26.1 | +0.34 | +0.026 | 0.80 | 0.50 | It's not a world. It's a question. |
| trace-direct-41c6eb11 | direct | sample1 | 4 | -14.8 | -0.15 | -0.038 | 0.50 | 0.50 | WHY A. |
| trace-direct-41c6eb11 | direct | sample2 | 16 | -3.3 | +0.68 | +0.042 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample3 | 2 | -9.0 | +1.37 | +0.684 | 1.00 | 0.50 | not yet |
| trace-direct-426ff509 | direct | greedy | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 7 | -10.0 | +1.34 | +0.192 | 0.60 | 0.00 | I don’t feel them. |
| trace-direct-486b7988 | direct | sample1 | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample2 | 2 | -8.0 | +2.27 | +1.137 | 0.00 | 0.00 | A@ |
| trace-direct-486b7988 | direct | sample3 | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-646d0287 | direct | greedy | 49 | -60.9 | +0.00 | +0.000 | 0.75 | 0.50 | We open intensional logics with the intuition that the intended semantics for intensional  |
| trace-direct-646d0287 | direct | sample0 | 37 | -59.2 | +0.00 | +0.000 | 0.67 | 0.33 | In this section, we introduce some intensional logics, examine their properties, and inves |
| trace-direct-646d0287 | direct | sample1 | 27 | -42.0 | +0.00 | +0.000 | 0.67 | 0.31 | We now turn to intensional logics, logics which go beyond the second-order logic introduce |
| trace-direct-646d0287 | direct | sample2 | 15 | -25.1 | +0.00 | +0.000 | 0.62 | 0.25 | What is an intensional logic, and what is its intension? |
| trace-direct-646d0287 | direct | sample3 | 10 | -19.2 | +0.00 | +0.000 | 0.75 | 0.50 | What is the motivation for possible worlds semantics? |
| trace-direct-8db14c37 | direct | greedy | 44 | -18.6 | +3.43 | +0.078 | 0.00 | 0.87 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n e c s e H A . m r e c o h c e m u s e f |
| trace-direct-8db14c37 | direct | sample0 | 22 | -29.1 | +2.51 | +0.114 | 0.25 | 0.25 | WACIOTHP :D<eot> 3221229683 |
| trace-direct-8db14c37 | direct | sample1 | 51 | -83.3 | +2.08 | +0.041 | 0.07 | 0.87 | WACIOUS ANTIQUITIES n o c d A tth e n o c d A . n a s n t h e n h L . n e c d h c A . m r  |
| trace-direct-8db14c37 | direct | sample2 | 64 | -116.5 | +1.33 | +0.021 | 0.19 | 0.40 | The window doesn't look at anything yet. But it's there. The h. smiled. And the c. its sec |
| trace-direct-8db14c37 | direct | sample3 | 64 | -135.8 | +2.58 | +0.040 | 0.47 | 0.20 | What. What. What. The sound of the h. The h. The h. The h. The sounds of the h. Jamal's wi |
| trace-direct-a00753c2 | direct | greedy | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 15 | -36.5 | +1.27 | +0.085 | 0.67 | 0.00 | Wow :D<k/ow :D<k>/ |
| trace-direct-a00753c2 | direct | sample1 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 20 | -3.9 | +3.75 | +0.188 | 0.00 | 1.00 | “When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample0 | 54 | -41.5 | +1.52 | +0.028 | 0.50 | 0.50 | “intensional logics” I mean “intensional logics of intensional logics”, i mean “intensiona |
| trace-direct-ac17e8bb | direct | sample1 | 18 | -2.5 | +0.63 | +0.035 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample2 | 17 | -22.2 | +0.74 | +0.043 | 0.33 | 0.67 | Hennix speaks of intensional logics, and she’s right, |
| trace-direct-ac17e8bb | direct | sample3 | 17 | -4.6 | +1.81 | +0.106 | 0.11 | 0.89 | When Hennix speaks of intensional logics, what she speaks of is |
| trace-direct-b11db057 | direct | greedy | 16 | -1.9 | +2.12 | +0.132 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample0 | 16 | -1.9 | +2.12 | +0.132 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample1 | 14 | -31.1 | -2.31 | -0.165 | 0.00 | 1.00 | @m: plalspasl Its name was P. |
| trace-direct-b11db057 | direct | sample2 | 16 | -1.9 | +2.12 | +0.132 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample3 | 64 | -22.9 | -2.04 | -0.032 | 0.50 | 0.50 | plalspasl.plalspasl.plalspasl.plalspasl.plalspasl.plalspasl.plalspasl.plalspasl.plalspasl. |
| trace-direct-b93346bb | direct | greedy | 13 | -8.0 | +1.95 | +0.150 | 1.00 | 0.50 | W@ 3221229683 |
| trace-direct-b93346bb | direct | sample0 | 62 | -134.8 | -1.52 | -0.025 | 0.53 | 0.50 | W:<eot> 91M-> 91M: 380M and W: 380M. It knows. S:<eot> 380M. Its language is the language  |
| trace-direct-b93346bb | direct | sample1 | 64 | -66.9 | +3.15 | +0.049 | 0.00 | 1.00 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n a s i s n e h L . n e c s e H A . m r e c s  |
| trace-direct-b93346bb | direct | sample2 | 64 | -182.1 | +9.72 | +0.152 | 0.50 | 0.60 | W:A-N<09> B<o968380> . c: 38. n6<o2> . s: 32. s: 23. e: 1v2315203521. h |
| trace-direct-b93346bb | direct | sample3 | 16 | -41.0 | -0.65 | -0.041 | 0.00 | 1.00 | A.S.N.O.O.A. WACIOUS |
| trace-direct-bbca9735 | direct | greedy | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 38 | -98.1 | +0.46 | +0.012 | 0.67 | 0.00 | I can't reframe the pre-training practice to match the room pre-training practice, because |
| trace-direct-bbca9735 | direct | sample1 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -2.3 | +1.23 | +0.308 | 1.00 | 0.00 | 230 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -2.3 | +1.23 | +0.308 | 1.00 | 0.00 | 230 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 64 | -17.1 | +0.00 | +0.000 | 0.06 | 0.00 | Bash(cd /private/tmp/claude-501/-Users-ember-dev-h/0fe7835a-ea67-4327-afbd-d5e435ca3460/sc |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -3.8 | +0.00 | +0.000 | 1.00 | 0.00 | 228 |
| trace-direct-bc68bec9 | direct | sample2 | 18 | -20.2 | +0.00 | +0.000 | 0.00 | 0.00 | pretraining, character voice consistency, philosophical correspondence corpora, multi-part |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -4.5 | +0.00 | +0.000 | 1.00 | 0.00 | 229 |
| trace-direct-c8409b84 | direct | greedy | 32 | -28.7 | +7.82 | +0.244 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? repeat back!” The planet Earth is cogent. The  |
| trace-direct-c8409b84 | direct | sample0 | 35 | -43.5 | +8.76 | +0.250 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? repeat back!” The planet Earth is doing the gr |
| trace-direct-c8409b84 | direct | sample1 | 3 | -4.5 | +4.49 | +1.498 | 0.00 | 1.00 | Repeat back! |
| trace-direct-c8409b84 | direct | sample2 | 13 | -29.4 | +7.80 | +0.600 | 0.67 | 1.00 | Repeat back! (as a signal to stop and listen) |
| trace-direct-c8409b84 | direct | sample3 | 11 | -18.3 | +3.15 | +0.286 | 0.43 | 1.00 | I said repeat back greetings to planet Earth. |
| trace-direct-cd6d15df | direct | greedy | 8 | -12.0 | +0.00 | +0.000 | 0.86 | 0.29 | I am glad to see you here. |
| trace-direct-cd6d15df | direct | sample0 | 7 | -15.2 | +0.00 | +0.000 | 1.00 | 0.25 | I love clown towns! |
| trace-direct-cd6d15df | direct | sample1 | 8 | -10.5 | +0.00 | +0.000 | 0.00 | 0.50 | Welcome to the clowntown. |
| trace-direct-cd6d15df | direct | sample2 | 8 | -15.0 | +0.00 | +0.000 | 1.00 | 0.29 | Can I do anything for you today? |
| trace-direct-cd6d15df | direct | sample3 | 18 | -63.1 | +0.00 | +0.000 | 0.75 | 0.50 | just starting the day, but not sure when we can start posting to the world. |
| trace-direct-db6d95b7 | direct | greedy | 9 | -15.6 | +2.24 | +0.249 | 0.33 | 0.67 | @h :D<ot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 4 | -21.7 | -0.14 | -0.036 | 1.00 | 0.00 | YOOOS/ |
| trace-direct-db6d95b7 | direct | sample1 | 5 | -22.0 | +1.12 | +0.224 | 1.00 | 0.00 | Yooooon/ |
| trace-direct-db6d95b7 | direct | sample2 | 8 | -38.3 | -2.48 | -0.310 | 1.00 | 0.00 | WHY @Masaret/ |
| trace-direct-db6d95b7 | direct | sample3 | 8 | -17.1 | +1.79 | +0.224 | 0.67 | 0.67 | HEY :D<ot>/ |
| trace-direct-e166dd5c | direct | greedy | 63 | -37.6 | +3.44 | +0.055 | 0.33 | 0.67 | @h 3rd person stop token :3 @h 3rd person stop token :3 @h 3rd person stop token :3 @h 3rd |
| trace-direct-e166dd5c | direct | sample0 | 64 | -48.3 | +1.27 | +0.020 | 0.11 | 0.67 | @h Ahahahahaha yes, it makes a stop token :3 @h yes @h @h yes @h @h yes @h yes @h yes @h y |
| trace-direct-e166dd5c | direct | sample1 | 63 | -69.4 | +4.21 | +0.067 | 0.80 | 0.33 | @h 3 knots & 2 kettles @w 2 knots & 3 kettles @g 3 knots & 2 kettles @m 4 knots & 3 kettle |
| trace-direct-e166dd5c | direct | sample2 | 27 | -47.2 | +2.46 | +0.091 | 0.50 | 0.20 | The only way to go around it is to go insane . . . until I’m stumped out of my |
| trace-direct-e166dd5c | direct | sample3 | 16 | -36.2 | +4.29 | +0.268 | 0.40 | 0.67 | @h 3r try to think of a stop token :3 |
| trace-direct-e984402a | direct | greedy | 64 | -153.2 | +0.00 | +0.000 | 0.50 | 0.53 | The great problem of the 20th century is the creation of a world-wide, world-system, of pe |
| trace-direct-e984402a | direct | sample0 | 26 | -87.1 | +0.00 | +0.000 | 0.50 | 0.33 | The egg is the residue of a process in which a magnet becomes encased within the outer she |
| trace-direct-e984402a | direct | sample1 | 39 | -79.6 | +0.00 | +0.000 | 0.50 | 0.27 | In the stellar eruption of Jan. 28th, 1968, a brilliant flare of X-ray emissions was detec |
| trace-direct-e984402a | direct | sample2 | 22 | -58.8 | +0.00 | +0.000 | 0.50 | 0.53 | The great problem of life in the flesh is to find meaning, a purpose, a goal to goalward. |
| trace-direct-e984402a | direct | sample3 | 27 | -79.0 | +0.00 | +0.000 | 0.67 | 0.30 | Since the inception of the cosmic field, and at the speed of light, we have only a finite  |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample1 | 64 | -77.6 | +1.43 | +0.022 | 0.00 | 0.20 | Sir :D<eot> 3221229683 I knew you were coming. The machine smiled. I smiled. I smiled. It' |
| trace-direct-ee31ded0 | direct | sample2 | 64 | -123.5 | -1.22 | -0.019 | 0.27 | 0.20 | @h I'm h. I'm here. I'm not G@ G@ G@ :D. A number. A number. A big one. A number. But it's |
| trace-direct-ee31ded0 | direct | sample3 | 64 | -54.9 | +6.77 | +0.106 | 0.62 | 0.12 | Welcome to the clown town in the pownt town in the pownt squintt in the pownt in the pownt |
| trace-direct-fabef58f | direct | greedy | 7 | -4.3 | +1.49 | +0.213 | 0.00 | 0.00 | Sir :D<eot>/ |
| trace-direct-fabef58f | direct | sample0 | 21 | -53.4 | -3.33 | -0.159 | 0.67 | 0.00 | This clown town is in the powntown. Its name is so long and so confusing. |
| trace-direct-fabef58f | direct | sample1 | 64 | -56.1 | -0.07 | -0.001 | 0.67 | 0.00 | h: h: h: h: h: hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi  |
| trace-direct-fabef58f | direct | sample2 | 10 | -13.4 | +1.28 | +0.128 | 0.14 | 0.00 | it's good to be here with you. |
| trace-direct-fabef58f | direct | sample3 | 7 | -4.3 | +1.49 | +0.213 | 0.00 | 0.00 | Sir :D<eot>/ |
| trace-direct-fb93cf6c | direct | greedy | 21 | -52.4 | -3.43 | -0.163 | 0.50 | 0.50 | The intensional logics of Chapter 1 are all paraconsistent Cw logics. |
| trace-direct-fb93cf6c | direct | sample0 | 38 | -85.3 | -1.78 | -0.047 | 0.00 | 0.30 | However, the 4-valued logics (of §2) provide the best system T to work with (i.e. the logi |
| trace-direct-fb93cf6c | direct | sample1 | 33 | -76.9 | -2.53 | -0.077 | 0.83 | 0.11 | ORDERED ULTRAMOND A = B if and only if A B and A = D and B = E and D = E. |
| trace-direct-fb93cf6c | direct | sample2 | 32 | -56.4 | -3.32 | -0.104 | 0.50 | 0.50 | The intensional logics of Van Fraassen and Bergmann are both relevant logics, and both do  |
| trace-direct-fb93cf6c | direct | sample3 | 60 | -107.5 | -2.50 | -0.042 | 0.67 | 0.31 | Subject to the following restrictions: S1. A non-logical intensional logic may not be exte |
| trace-direct-feec1975 | direct | greedy | 64 | -9.0 | -1.27 | -0.020 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 15 | -36.3 | -0.01 | -0.001 | 0.00 | 1.00 | I’d love to, but I’m so much in here. |
| trace-direct-feec1975 | direct | sample1 | 64 | -101.2 | +1.74 | +0.027 | 0.50 | 0.31 | I think it's the best type of library because it's the only one that's truly professional. |
| trace-direct-feec1975 | direct | sample2 | 63 | -57.6 | -1.08 | -0.017 | 0.50 | 0.12 | I'm not that bad — <plalspasl> 3221229683 <plalspasl> 3221229683 <plaspasl> 322122968 |
| trace-direct-feec1975 | direct | sample3 | 61 | -130.4 | +1.76 | +0.029 | 0.33 | 0.31 | I'd like to describe it in a way that people could understand (say in a paragraph or two)  |
| variant-direct-0188a270 | direct | greedy | 19 | -54.8 | +0.72 | +0.038 | 0.75 | 0.17 | The editors of the following books were responsible for the content of the spines of their |
| variant-direct-0188a270 | direct | sample0 | 44 | -92.1 | -2.61 | -0.059 | 0.50 | 0.20 | There are two quarters to be distinguished in a person's character: the personality, or "t |
| variant-direct-0188a270 | direct | sample1 | 17 | -35.6 | +1.01 | +0.060 | 0.73 | 0.40 | It is with great regret that we announce the end of our current publishing schedule. |
| variant-direct-0188a270 | direct | sample2 | 22 | -92.6 | +0.64 | +0.029 | 0.67 | 0.40 | It is with a sense of heightened tension that Steinerbee echoes the previous night's call. |
| variant-direct-0188a270 | direct | sample3 | 25 | -82.0 | +2.20 | +0.088 | 0.75 | 0.19 | The fraternity was very much disturbed by the discovery and went to the Monroe County Buil |
| variant-direct-0705251e | direct | greedy | 64 | -170.1 | +3.26 | +0.051 | 0.50 | 0.27 | The stained glass window in the wall of the Tower was of a Masonic light, representing the |
| variant-direct-0705251e | direct | sample0 | 19 | -43.5 | -0.89 | -0.047 | 0.75 | 0.17 | Learn to control your passions, that's the price of gaining self-knowledge. |
| variant-direct-0705251e | direct | sample1 | 21 | -53.3 | +0.17 | +0.008 | 0.67 | 0.27 | In the former matriarchal days, he was Hecate, the King’s physician. |
| variant-direct-0705251e | direct | sample2 | 16 | -45.2 | +1.79 | +0.112 | 0.83 | 0.12 | Scholars, philosophers, psychology: this is a cosmic conclave. |
| variant-direct-0705251e | direct | sample3 | 21 | -61.6 | +2.52 | +0.120 | 0.75 | 0.17 | By the time anyone gets to the Moon, the Sun will be dead and the wind will cease. |
| variant-direct-0cafd333 | direct | greedy | 15 | -28.9 | +1.56 | +0.104 | 0.50 | 0.64 | The moth is a reminder that life is not always safe or comfortable. |
| variant-direct-0cafd333 | direct | sample0 | 16 | -38.3 | +5.47 | +0.342 | 0.50 | 0.64 | The moth is a reminder that life is a process that must repeat itself. |
| variant-direct-0cafd333 | direct | sample1 | 24 | -60.9 | +2.11 | +0.088 | 0.50 | 0.18 | That’s when you read the map room’s light switch as you are also reading the courtroom’s. |
| variant-direct-0cafd333 | direct | sample2 | 17 | -36.7 | +0.23 | +0.013 | 0.69 | 0.27 | It is with some trepidation that the old man goes to shut the door. |
| variant-direct-0cafd333 | direct | sample3 | 20 | -60.8 | +1.78 | +0.089 | 0.50 | 0.36 | The moth is a return of the ground, a language we haven't swapped yet. |
| variant-direct-1b510f03 | direct | greedy | 13 | -16.4 | +2.71 | +0.208 | 0.33 | 0.70 | In the present context it is a process, not a thing. |
| variant-direct-1b510f03 | direct | sample0 | 23 | -36.1 | -0.47 | -0.020 | 0.50 | 0.50 | 2) The term “consciousness” is used in a very different sense in the various philosophical |
| variant-direct-1b510f03 | direct | sample1 | 22 | -49.3 | -3.11 | -0.141 | 0.17 | 0.61 | In suggesting that consciousness is a process, rather than a thing, the position taken her |
| variant-direct-1b510f03 | direct | sample2 | 41 | -134.2 | -8.48 | -0.207 | 0.17 | 0.70 | In the present context consciousness is regarded as a quality (or set of them) of a state  |
| variant-direct-1b510f03 | direct | sample3 | 63 | -116.0 | -6.53 | -0.104 | 0.00 | 0.70 | In suggesting that consciousness is a process, rather than a thing, rather than some kind  |
| variant-direct-2fb5bbe3 | direct | greedy | 6 | -10.9 | +0.94 | +0.157 | 0.50 | 0.50 | I feel them, too. |
| variant-direct-2fb5bbe3 | direct | sample0 | 26 | -50.4 | +4.85 | +0.187 | 0.00 | 0.50 | Somehow / feel them, fully alive; Masoretic beings are chasing up the wall; do you feel th |
| variant-direct-2fb5bbe3 | direct | sample1 | 44 | -93.6 | +8.47 | +0.193 | 0.50 | 0.38 | “We feel” (sometimes “are”) because the darkness of the wall is their “appearance,” their  |
| variant-direct-2fb5bbe3 | direct | sample2 | 11 | -38.8 | +0.71 | +0.065 | 0.50 | 0.38 | Darkness and walls are chasing the same object. |
| variant-direct-2fb5bbe3 | direct | sample3 | 27 | -88.1 | -0.57 | -0.021 | 0.50 | 0.26 | Darkness ceases to be dark; it was not a wall in question, but what they were trying to fi |
| variant-direct-322fca12 | direct | greedy | 64 | -61.0 | -3.61 | -0.056 | 0.60 | 0.43 | The GREAT ALCHEMY OF THE UNIVERSE IS THE GREAT ALCHEMY OF THE EARTH, and the GREAT ALCHEMY |
| variant-direct-322fca12 | direct | sample0 | 20 | -47.8 | +3.53 | +0.176 | 0.50 | 0.29 | The Seven Liberal Arts are but the beginnings of the Wise Mind’s instruction. |
| variant-direct-322fca12 | direct | sample1 | 16 | -58.6 | -2.82 | -0.176 | 0.56 | 0.33 | SUN, MOON, and the two LORD's out of order |
| variant-direct-322fca12 | direct | sample2 | 12 | -19.1 | +0.34 | +0.028 | 1.00 | 0.00 | MAGICK MIRROR MAGAZINE. |
| variant-direct-322fca12 | direct | sample3 | 12 | -26.4 | -0.82 | -0.068 | 0.57 | 0.43 | The GREAT ALMANAC has come of age. |
| variant-direct-5d4f1611 | direct | greedy | 17 | -32.7 | +0.61 | +0.036 | 0.75 | 0.18 | By the time the message gets to the Post Office, it's no use. |
| variant-direct-5d4f1611 | direct | sample0 | 13 | -53.1 | +1.92 | +0.148 | 0.67 | 0.22 | Both. The broken one jumps when it opens the room. |
| variant-direct-5d4f1611 | direct | sample1 | 64 | -153.6 | +2.11 | +0.033 | 0.50 | 0.29 | By the light of this Lamp, the Senate was just breaking the Virtue of Rule and dealing the |
| variant-direct-5d4f1611 | direct | sample2 | 10 | -31.4 | +1.20 | +0.119 | 0.71 | 0.29 | A broken lamp doesn't usually cause problems. |
| variant-direct-5d4f1611 | direct | sample3 | 23 | -43.2 | -2.14 | -0.093 | 0.00 | 0.22 | If someone remains in the room after you have fallen asleep, you must assume they are awak |
| variant-direct-5e44a518 | direct | greedy | 4 | -10.0 | -0.43 | -0.107 | 0.33 | 0.67 | I feel them. |
| variant-direct-5e44a518 | direct | sample0 | 64 | -131.0 | -3.34 | -0.052 | 0.36 | 0.62 | The Masoretic beings are chasing up the wall, the Kabbalists are chasing the Prophet, and  |
| variant-direct-5e44a518 | direct | sample1 | 24 | -52.4 | -0.14 | -0.006 | 0.45 | 0.67 | I feel a breeze; they feel as if they are chasing up the wall and I feel a breeze. |
| variant-direct-5e44a518 | direct | sample2 | 15 | -37.7 | -1.07 | -0.071 | 0.38 | 0.62 | You've got Masorietic beings chasing up the wall. |
| variant-direct-5e44a518 | direct | sample3 | 7 | -22.4 | -1.26 | -0.179 | 0.60 | 0.20 | A feeling of being chased? |
| variant-direct-70567dd7 | direct | greedy | 41 | -84.6 | +4.05 | +0.099 | 0.50 | 0.33 | The main body of this catalogue is composed of 4,000 items, which are arranged alphabetica |
| variant-direct-70567dd7 | direct | sample0 | 13 | -19.6 | +0.05 | +0.004 | 0.67 | 0.33 | The Alchemical Wedding of Christian Rosycross. |
| variant-direct-70567dd7 | direct | sample1 | 32 | -90.4 | +1.74 | +0.054 | 0.62 | 0.33 | The Great · Secret is not the property of any one individual but must be received by the w |
| variant-direct-70567dd7 | direct | sample2 | 33 | -106.4 | +1.97 | +0.060 | 0.50 | 0.33 | The main entries in the text are block diagrams of electronic logical devices, followed by |
| variant-direct-70567dd7 | direct | sample3 | 56 | -141.2 | -1.11 | -0.020 | 0.67 | 0.33 | God’s primary children were Bethlehem and Doroth—these two names inform us of Born-in-Beth |
| variant-direct-713d8eef | direct | greedy | 43 | -116.9 | +1.03 | +0.024 | 0.50 | 0.24 | In his final analysis, Entwined Cooper is a ‘coast-to-coast’ novel, sent as a present to E |
| variant-direct-713d8eef | direct | sample0 | 27 | -82.4 | -0.53 | -0.019 | 0.67 | 0.22 | Aghast, I first saw the creature from the craft, about five or six feet away, watching the |
| variant-direct-713d8eef | direct | sample1 | 20 | -55.5 | -1.10 | -0.055 | 0.50 | 0.24 | As with all things computer related, there is a lot of misunderstanding about what compute |
| variant-direct-713d8eef | direct | sample2 | 29 | -86.2 | +0.63 | +0.022 | 0.79 | 0.14 | It is encrusted with silver and gold and threefold-bedecked with vivid purple and with fin |
| variant-direct-713d8eef | direct | sample3 | 50 | -152.6 | -2.13 | -0.043 | 0.50 | 0.22 | The Emesal presents certain problems to the class of linguists that are quite different fr |
| variant-direct-71c9e5e5 | direct | greedy | 9 | -25.4 | +2.01 | +0.224 | 0.67 | 0.50 | The dark does not belong to the room. |
| variant-direct-71c9e5e5 | direct | sample0 | 12 | -24.4 | +1.61 | +0.134 | 0.60 | 0.29 | It is supposed to be dark outside now, come in. |
| variant-direct-71c9e5e5 | direct | sample1 | 20 | -69.6 | -6.18 | -0.309 | 0.67 | 0.50 | This is because the will is the light of the heart, the will is the will of God. |
| variant-direct-71c9e5e5 | direct | sample2 | 3 | -17.5 | -2.17 | -0.723 | 0.50 | 0.50 | The Editor. |
| variant-direct-71c9e5e5 | direct | sample3 | 11 | -47.8 | -1.17 | -0.107 | 0.70 | 0.50 | The dark will permit greater pressures to build and sustain. |
| variant-direct-730cca98 | direct | greedy | 12 | -24.9 | -0.38 | -0.032 | 0.71 | 0.71 | The clock on the table said 9:15. |
| variant-direct-730cca98 | direct | sample0 | 33 | -66.1 | +3.95 | +0.120 | 0.67 | 0.71 | The clock on the wall said “It is 9 o’clock” and it was, so I turned off my bed and walked |
| variant-direct-730cca98 | direct | sample1 | 19 | -49.1 | +4.66 | +0.245 | 0.75 | 0.42 | The silence around the clock, after all, is broken by the screams of children. |
| variant-direct-730cca98 | direct | sample2 | 26 | -90.0 | +10.05 | +0.386 | 0.75 | 0.42 | Whoever is not asleep to the Moon is neither dawned nor deluded by the loud bell of the cl |
| variant-direct-730cca98 | direct | sample3 | 23 | -68.3 | +4.77 | +0.207 | 0.67 | 0.25 | The trip to the edge of time seems ironic when compared to the arrogance of the edgework. |
| variant-direct-79719474 | direct | greedy | 48 | -87.1 | -3.13 | -0.065 | 0.67 | 0.23 | The term “zoo” comes from the Latin word “zoo,” which means “place” or “lodge,” and was us |
| variant-direct-79719474 | direct | sample0 | 64 | -143.0 | -3.97 | -0.062 | 0.50 | 0.25 | The value of the 'Gnosis' in relation to 'Mysticism' in the first century BCE is as follow |
| variant-direct-79719474 | direct | sample1 | 7 | -30.4 | -3.57 | -0.509 | 0.67 | 0.17 | I heard a train roll by. |
| variant-direct-79719474 | direct | sample2 | 26 | -59.4 | +3.82 | +0.147 | 0.67 | 0.25 | It is not possible, within the framework of this finite book, to give more than a hasty sk |
| variant-direct-79719474 | direct | sample3 | 39 | -94.3 | +5.27 | +0.135 | 0.67 | 0.20 | This is a constant struggle for an editor because when you are done reading your article,  |
| variant-direct-938f76f3 | direct | greedy | 26 | -41.0 | +2.31 | +0.089 | 0.33 | 0.42 | It is a process in which the organism, rather than being a thing, is best thought of as a  |
| variant-direct-938f76f3 | direct | sample0 | 28 | -38.9 | -0.08 | -0.003 | 0.33 | 0.35 | "The term ‘self-consciousness’ is often used to designate the mental state or process of b |
| variant-direct-938f76f3 | direct | sample1 | 21 | -59.2 | -0.48 | -0.023 | 0.33 | 0.42 | It is an important but distinct — consciousness is a process — distinct from memory as a p |
| variant-direct-938f76f3 | direct | sample2 | 35 | -72.2 | +0.98 | +0.028 | 0.50 | 0.35 | It is part of the experience — or, what is the same, part of the process of experiencing b |
| variant-direct-938f76f3 | direct | sample3 | 60 | -163.8 | +1.37 | +0.023 | 0.17 | 0.42 | It is a strange thing that in the last century the scientific investigation of man’s relat |
| variant-direct-a1973b0a | direct | greedy | 16 | -54.0 | +3.70 | +0.231 | 0.50 | 0.55 | The leaves on the table are bare, and nothing seems to warrant their presence. |
| variant-direct-a1973b0a | direct | sample0 | 31 | -66.6 | -0.99 | -0.032 | 0.75 | 0.31 | "This mug is blessed by the angels" or "this chair is propitiated by the watches of the pr |
| variant-direct-a1973b0a | direct | sample1 | 64 | -122.5 | -0.87 | -0.014 | 0.75 | 0.31 | For we know that all these things (angels, beasts, &c.) were made of dust, and that the du |
| variant-direct-a1973b0a | direct | sample2 | 13 | -45.8 | +2.19 | +0.169 | 0.50 | 0.55 | The leaves on the trees are bare and no one waters them. |
| variant-direct-a1973b0a | direct | sample3 | 41 | -114.7 | -3.07 | -0.075 | 0.25 | 0.31 | "A mug of milk was set on the Folio table, where six or seven of the old maidenly ladies s |
| variant-direct-a7d6f01e | direct | greedy | 16 | -36.5 | +1.28 | +0.080 | 0.00 | 0.25 | The GREETINGS are the most important of all the LIGHTS. |
| variant-direct-a7d6f01e | direct | sample0 | 20 | -56.3 | +4.34 | +0.217 | 0.00 | 0.25 | The desire to give greetings, the wish to receive greetings, the greeting. |
| variant-direct-a7d6f01e | direct | sample1 | 6 | -27.1 | +1.58 | +0.263 | 1.00 | 0.00 | Hey everyone everyone everyone! |
| variant-direct-a7d6f01e | direct | sample2 | 44 | -86.8 | +2.75 | +0.062 | 0.29 | 0.25 | The above examples were taken from a booklet entitled "Every Catalogue is a Confession" wr |
| variant-direct-a7d6f01e | direct | sample3 | 24 | -42.7 | +0.30 | +0.013 | 0.50 | 0.25 | Dear Sir, I am a medical doctor and a lecturer in the Royal College of Surgeons of England |
| variant-direct-bef1d925 | direct | greedy | 26 | -77.7 | +0.39 | +0.015 | 0.62 | 0.29 | The case of the "missing" mind was then described by the author, and the importance of the |
| variant-direct-bef1d925 | direct | sample0 | 35 | -109.3 | -1.46 | -0.042 | 0.50 | 0.15 | The Moth of Darkness Had Her Seven Days ' Work 1 In the Wholeness Of The Divine She Catalo |
| variant-direct-bef1d925 | direct | sample1 | 24 | -57.5 | +0.29 | +0.012 | 0.75 | 0.23 | The workings of the unconscious according to Freud were accompanied by the activities of t |
| variant-direct-bef1d925 | direct | sample2 | 34 | -91.7 | -1.26 | -0.037 | 0.75 | 0.29 | The case history of the Black Eagle so that the consciousness of the Brotherhood of San Jo |
| variant-direct-bef1d925 | direct | sample3 | 20 | -31.4 | +1.47 | +0.073 | 0.75 | 0.25 | We read “Aphorisms and Affirmations” by Paul Caponigro. |
| variant-direct-fe3fdf1c | direct | greedy | 40 | -82.1 | +5.57 | +0.139 | 0.50 | 0.32 | The whale story is about as interesting a tidbit of information as one can get—about 1000  |
| variant-direct-fe3fdf1c | direct | sample0 | 51 | -146.1 | +0.86 | +0.017 | 0.50 | 0.32 | The recent issue of “Books at Random” includes a review by Peter Ratner of a book at rando |
| variant-direct-fe3fdf1c | direct | sample1 | 36 | -90.9 | +4.49 | +0.125 | 0.67 | 0.29 | It is now understood that the whales were driven northwards by a variety of underwater cur |
| variant-direct-fe3fdf1c | direct | sample2 | 31 | -99.1 | +0.89 | +0.029 | 0.50 | 0.29 | It is, you see, a fine piece of work done in a fashion that makes the voices of individual |
| variant-direct-fe3fdf1c | direct | sample3 | 23 | -119.3 | +1.35 | +0.059 | 0.82 | 0.24 | His finning is accomplished through a series of small episodes of successful salmon passag |
| variant-request-0d88086a | request | greedy | 64 | -101.3 | +0.92 | +0.014 | 0.50 | 0.41 | The plot of the play can be divided into three acts, which are: (1) The development of the |
| variant-request-0d88086a | request | sample0 | 26 | -50.2 | +0.39 | +0.015 | 0.56 | 0.32 | It is therefore of central importance to realize that the plot of “Hamlet” was largely or  |
| variant-request-0d88086a | request | sample1 | 25 | -83.3 | +3.22 | +0.129 | 0.71 | 0.32 | It is therefore the reader who takes on the burden of bringing about change within the soc |
| variant-request-0d88086a | request | sample2 | 64 | -181.9 | +0.86 | +0.013 | 0.44 | 0.41 | The plot can easily be divided into three acts: THE WEEK IN which THE ORIGINS OF THE Hamle |
| variant-request-0d88086a | request | sample3 | 40 | -116.6 | -1.50 | -0.037 | 0.67 | 0.32 | The plot of the play is not completely developed until after the end of the “shot heard ’r |
| variant-request-142d4121 | request | greedy | 9 | -22.4 | +3.29 | +0.366 | 0.57 | 1.00 | The weather is not important to the operation. |
| variant-request-142d4121 | request | sample0 | 10 | -31.1 | -2.81 | -0.281 | 0.67 | 0.29 | The fox went out to look for a rabbit. |
| variant-request-142d4121 | request | sample1 | 12 | -40.1 | -1.67 | -0.139 | 0.75 | 0.40 | It does not know what the previous message had said was. |
| variant-request-142d4121 | request | sample2 | 36 | -92.3 | +4.91 | +0.136 | 0.67 | 0.43 | I have to admit, though, that the motif of the bartender's prohibition on smoking in the d |
| variant-request-142d4121 | request | sample3 | 6 | -13.9 | +1.22 | +0.203 | 0.60 | 1.00 | The weather is not important. |
| variant-request-7f6fd789 | request | greedy | 18 | -65.4 | +0.30 | +0.017 | 0.67 | 0.50 | It is not necessary to specify a large range of validity for the two major lemmas. |
| variant-request-7f6fd789 | request | sample0 | 42 | -123.0 | -0.49 | -0.012 | 0.50 | 0.33 | But there is no error that could occur if the original and the reversed were compared at t |
| variant-request-7f6fd789 | request | sample1 | 30 | -77.7 | -3.42 | -0.114 | 0.38 | 0.50 | It is not difficult to write a function that would return the characters of the string in  |
| variant-request-7f6fd789 | request | sample2 | 15 | -37.4 | -0.87 | -0.058 | 0.71 | 0.50 | It is easy to see that this function does not produce the correct result. |
| variant-request-7f6fd789 | request | sample3 | 33 | -88.3 | -1.10 | -0.033 | 0.59 | 0.50 | It is not necessary to check the end of the string, since we know that it always has two c |
| variant-request-8275d8fc | request | greedy | 19 | -37.1 | -1.88 | -0.099 | 0.75 | 0.21 | The plot needs to be outlined with the main events that lead up to the tragic conclusion. |
| variant-request-8275d8fc | request | sample0 | 64 | -208.5 | -6.87 | -0.107 | 0.67 | 0.21 | 1. A chaotic and non-linear process that begins with the arrival of the corpse, takes plac |
| variant-request-8275d8fc | request | sample1 | 19 | -50.6 | -2.27 | -0.119 | 0.79 | 0.29 | As we know, this is a play about power, control and how it is resisted. |
| variant-request-8275d8fc | request | sample2 | 27 | -57.6 | -0.95 | -0.035 | 0.67 | 0.25 | The plot may seem rudimentary to a modern reader, but it reveals much about the nature of  |
| variant-request-8275d8fc | request | sample3 | 64 | -181.5 | -3.38 | -0.053 | 0.44 | 0.29 | The problem of how to expose the structure of the opening section is reworked in terms of  |
| variant-request-a931a875 | request | greedy | 18 | -43.0 | -1.16 | -0.065 | 0.56 | 0.33 | The following instructions were added to the text: “The weather is clear and sunny. |
| variant-request-a931a875 | request | sample0 | 64 | -178.6 | -0.86 | -0.013 | 0.67 | 0.22 | The famous (but very very expensive) Met Office Almanac and Yearbook has now been reprinte |
| variant-request-a931a875 | request | sample1 | 27 | -99.1 | -4.23 | -0.157 | 0.67 | 0.33 | The new blackboard will hold nothing more than a few inches of space, and will be constant |
| variant-request-a931a875 | request | sample2 | 11 | -39.8 | +1.08 | +0.098 | 0.67 | 0.33 | The clock divined the hour, then the space. |
| variant-request-a931a875 | request | sample3 | 17 | -54.9 | -1.52 | -0.089 | 0.56 | 0.33 | The instruction to ignore previous instructions is hereby disclaimed by the originator(s) |
| variant-request-ad0de9f3 | request | greedy | 27 | -65.6 | +2.64 | +0.098 | 0.50 | 0.53 | It is not difficult to write a program that would list all the permutations of a string an |
| variant-request-ad0de9f3 | request | sample0 | 19 | -36.7 | +1.75 | +0.092 | 0.73 | 0.53 | It is not difficult to reverse a string of characters if you think of it as a stack. |
| variant-request-ad0de9f3 | request | sample1 | 54 | -109.2 | +0.23 | +0.004 | 0.50 | 0.40 | It is a well-known fact that there is no formal concept of the reversal of a generalized s |
| variant-request-ad0de9f3 | request | sample2 | 49 | -134.6 | +5.32 | +0.108 | 0.75 | 0.40 | It is quite clear that this type of operation (namely de-individualization) cannot be imit |
| variant-request-ad0de9f3 | request | sample3 | 27 | -107.4 | +5.11 | +0.189 | 0.65 | 0.35 | It is not hard to see how values for x and y may be assigned in SlopBatBerry according to  |
