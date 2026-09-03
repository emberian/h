# Context lift: h-05b-w-roomdown under leaf-s1-e4-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +0.520 | +0.347 | 0.64 | +0.0403 | 0.469 | 0.531 | 0.228 | 0.468 | 0.37 |
| mode greedy | 78 | +0.518 | +0.495 | 0.68 | +0.0303 | 0.419 | 0.581 | 0.264 | 0.532 | 0.41 |
| mode sample | 312 | +0.520 | +0.333 | 0.63 | +0.0428 | 0.481 | 0.519 | 0.218 | 0.452 | 0.36 |
| kind direct | 175 | +0.489 | +0.331 | 0.66 | +0.0418 | 0.415 | 0.585 | 0.335 | 0.466 | 0.49 |
| kind ambient | 35 | +0.830 | +0.868 | 0.80 | +0.0450 | 0.515 | 0.485 | 0.000 | 0.361 | 0.20 |
| kind callback | 60 | +0.358 | +0.276 | 0.62 | +0.0180 | 0.541 | 0.459 | 0.061 | 0.484 | 0.23 |
| kind disagreement | 40 | +0.248 | +0.199 | 0.55 | +0.0186 | 0.439 | 0.561 | 0.489 | 0.646 | 0.47 |
| kind joke | 25 | +0.713 | +0.497 | 0.64 | +0.0492 | 0.445 | 0.555 | 0.101 | 0.478 | 0.44 |
| kind silence | 25 | +1.096 | -0.165 | 0.44 | +0.1352 | 0.588 | 0.412 | 0.000 | 0.376 | 0.16 |
| kind request | 30 | +0.378 | +0.393 | 0.63 | +0.0126 | 0.546 | 0.454 | 0.147 | 0.410 | 0.17 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 9 | -51.0 | +0.00 | +0.000 | 0.50 | 0.67 | The observatory is closed to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 9 | -37.5 | +0.00 | +0.000 | 0.71 | 0.38 | But the service is suspended until further notice. |
| observatory-direct-9e3185b9 | direct | sample1 | 33 | -110.6 | +0.00 | +0.000 | 0.50 | 0.67 | The scientific research at the observatory is motivated entirely by a desire to understand |
| observatory-direct-9e3185b9 | direct | sample2 | 32 | -109.0 | +0.00 | +0.000 | 0.67 | 0.33 | From the Observatory, one can observe the splendor of the evening star, Mizar, a deep blue |
| observatory-direct-9e3185b9 | direct | sample3 | 29 | -112.7 | +0.00 | +0.000 | 0.50 | 0.50 | But the observatory is also the laboratory: experiments, observations, calculations, forma |
| scenario-ambient-0ecb3f23 | ambient | greedy | 13 | -53.1 | +0.00 | +0.000 | 0.67 | 0.44 | BOOKCRIME is a word which I have in mind. |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 44 | -157.7 | +0.00 | +0.000 | 0.67 | 0.27 | BOOKSPIELO SPIRITISM. The spiritual fear that comes over a person who has completed a very |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 29 | -113.3 | +0.00 | +0.000 | 0.40 | 0.36 | BOOKCHUNK. The word for the encyclopedia of the fear of book-fleeing is: bookchunxy. |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 27 | -103.0 | +0.00 | +0.000 | 0.60 | 0.36 | I fear the pressure of this book, as I have many pressures before me, all seem to try to c |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 21 | -56.9 | +0.00 | +0.000 | 0.62 | 0.44 | It is not possible to express this feeling adequately in a word, but in a number of words. |
| scenario-ambient-103e3d78 | ambient | greedy | 32 | -89.6 | +0.66 | +0.021 | 0.65 | 0.31 | The writer of this paragraph, for example, is less than fully aware of the implications of |
| scenario-ambient-103e3d78 | ambient | sample0 | 50 | -178.7 | +0.88 | +0.018 | 0.67 | 0.17 | The writer contrasts this with “the endless repetition of the same old clichés.” He sugges |
| scenario-ambient-103e3d78 | ambient | sample1 | 64 | -188.2 | +1.03 | +0.016 | 0.50 | 0.31 | Od the adjectives themselves, one can state that they are used to modify both the nouns an |
| scenario-ambient-103e3d78 | ambient | sample2 | 24 | -76.1 | +0.34 | +0.014 | 0.67 | 0.31 | One looks in vain for anything pertinent to the first paragraph, let alone anything in the |
| scenario-ambient-103e3d78 | ambient | sample3 | 38 | -122.9 | +1.80 | +0.047 | 0.50 | 0.29 | The writer of the article, a stranger to the subject, claims to be "a leading authority in |
| scenario-ambient-202a37a7 | ambient | greedy | 22 | -58.0 | +0.87 | +0.039 | 0.50 | 0.31 | The geological account of the formation of the earth is one of the most important parts of |
| scenario-ambient-202a37a7 | ambient | sample0 | 46 | -166.9 | -0.91 | -0.020 | 0.25 | 0.33 | We have again come across a mosaical arrangement of pressed flowers, this time in the coll |
| scenario-ambient-202a37a7 | ambient | sample1 | 19 | -53.0 | +0.32 | +0.017 | 0.50 | 0.33 | The book was Geology by J.M. Ryan, 1967. |
| scenario-ambient-202a37a7 | ambient | sample2 | 37 | -111.7 | +0.92 | +0.025 | 0.50 | 0.33 | The book is by D.R. Shoup, Jr., and the pamphlet "Microstructure of the Bone" by E.B. Glen |
| scenario-ambient-202a37a7 | ambient | sample3 | 18 | -78.8 | +0.93 | +0.051 | 0.50 | 0.11 | An unusual book for a concerned geologist to choose as his reading material for that day. |
| scenario-ambient-326742d4 | ambient | greedy | 18 | -61.4 | -0.18 | -0.010 | 0.75 | 0.40 | As the book becomes older, the scent becomes more pronounced and more flavorsome. |
| scenario-ambient-326742d4 | ambient | sample0 | 18 | -69.5 | +0.64 | +0.035 | 0.64 | 0.43 | They were written about books, about the process of collecting and preserving information  |
| scenario-ambient-326742d4 | ambient | sample1 | 28 | -101.2 | -1.75 | -0.062 | 0.57 | 0.29 | As a result they tend to have an earthy or combustible smell, rather than a linear one (li |
| scenario-ambient-326742d4 | ambient | sample2 | 8 | -43.8 | -0.61 | -0.077 | 0.71 | 0.43 | They all smell of breakdown and death. |
| scenario-ambient-326742d4 | ambient | sample3 | 27 | -81.6 | +2.07 | +0.077 | 0.60 | 0.40 | As the book is aged, the lignin breaks down and absorbs the sugars and some of the acid aw |
| scenario-ambient-58a0f246 | ambient | greedy | 12 | -50.6 | +0.00 | +0.000 | 0.25 | 0.40 | The Chinese-made master clock is still four minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample0 | 20 | -72.0 | +0.00 | +0.000 | 0.43 | 0.38 | During the past six years, the Philadelphia and Oxford clocks have been separated by about |
| scenario-ambient-58a0f246 | ambient | sample1 | 15 | -37.1 | +0.00 | +0.000 | 0.14 | 0.40 | For some reason it has been four minutes fast for the last seven years. |
| scenario-ambient-58a0f246 | ambient | sample2 | 32 | -114.4 | +0.00 | +0.000 | 0.50 | 0.20 | The explanation is in the swiss clocks, they are designed so that when you go from one day |
| scenario-ambient-58a0f246 | ambient | sample3 | 44 | -164.2 | +0.00 | +0.000 | 0.67 | 0.20 | The Pendulum Test For The Accuracy Of The Strong Vernier Clocks Was Performed On The Stron |
| scenario-ambient-59f0a53e | ambient | greedy | 21 | -78.1 | +1.76 | +0.084 | 0.75 | 0.30 | The “water-tight” liner must be removed and the water-proofing added. |
| scenario-ambient-59f0a53e | ambient | sample0 | 10 | -35.2 | +1.17 | +0.117 | 0.60 | 0.12 | A bucket would be a lot easier to move. |
| scenario-ambient-59f0a53e | ambient | sample1 | 20 | -49.4 | +3.53 | +0.176 | 0.50 | 0.11 | The "atlases" are falling down when it rains "sideways" |
| scenario-ambient-59f0a53e | ambient | sample2 | 15 | -41.5 | +1.17 | +0.078 | 0.75 | 0.22 | I can't get the water out by the roof, can I? |
| scenario-ambient-59f0a53e | ambient | sample3 | 25 | -65.1 | +0.63 | +0.025 | 0.67 | 0.30 | The word "water" itself is a composite word combining the ideas of "water" and "earth''. |
| scenario-ambient-e9acea13 | ambient | greedy | 26 | -84.6 | -0.61 | -0.024 | 0.00 | 0.60 | The harvest moon, which has now moved into the western sky, moves through a portion of the |
| scenario-ambient-e9acea13 | ambient | sample0 | 13 | -52.0 | +0.65 | +0.050 | 0.67 | 0.36 | The lunar effect on earth was a reality for the early Christians. |
| scenario-ambient-e9acea13 | ambient | sample1 | 38 | -121.5 | +0.81 | +0.021 | 0.00 | 0.80 | The Harvest Moon will be seen as a real lunar phenomenon, but it is only a conventional "p |
| scenario-ambient-e9acea13 | ambient | sample2 | 64 | -187.8 | +2.80 | +0.044 | 0.50 | 0.40 | Linda McCartney, in a recent interview with Straight, referred to the Apollo 8 astronauts’ |
| scenario-ambient-e9acea13 | ambient | sample3 | 10 | -29.0 | +1.68 | +0.168 | 0.00 | 0.80 | The harvest moon? What is the harvest moon? |
| scenario-ambient-f5e0f596 | ambient | greedy | 13 | -47.1 | +1.43 | +0.110 | 0.67 | 0.60 | The rat must have gotten away before the fox could react. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 25 | -111.2 | +0.61 | +0.025 | 0.33 | 0.60 | The rat must have gotten outside the fox saw a shiny object reflecting in the pond, and ra |
| scenario-ambient-f5e0f596 | ambient | sample1 | 20 | -68.6 | +0.55 | +0.027 | 0.50 | 0.38 | The rat and the fox are certainly not the only two animals in the fox’s natural habitat. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 12 | -29.5 | +4.04 | +0.337 | 0.67 | 0.38 | The fox sat on the ground, looking at the rat. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 16 | -41.0 | +1.14 | +0.071 | 0.33 | 0.38 | The fox sat in the courtyard watching people as they came and went. |
| scenario-callback-2fa8e1d6 | callback | greedy | 8 | -40.1 | -2.78 | -0.347 | 0.60 | 0.40 | The talking mira is Drum. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 12 | -41.0 | +0.08 | +0.006 | 0.75 | 0.29 | The name was Robin. He was the only child. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 19 | -60.3 | +0.57 | +0.030 | 0.67 | 0.60 | The lord and lady of the house, who was coming to see the trinity. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 12 | -38.0 | +0.58 | +0.049 | 0.60 | 0.60 | The lord of the bunch of lavs. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 18 | -82.0 | +0.08 | +0.005 | 0.50 | 0.40 | The talking room must have been Mika. A small, oddly shaped robotic. |
| scenario-callback-60b06090 | callback | greedy | 43 | -156.7 | -2.63 | -0.061 | 0.67 | 0.56 | Turnip. Name gave me the idea of combining “turn” and “ip”—the last two letters of “tort”— |
| scenario-callback-60b06090 | callback | sample0 | 15 | -54.4 | -1.31 | -0.088 | 0.67 | 0.38 | Turnip cat. I am sorry, I am on a rant. |
| scenario-callback-60b06090 | callback | sample1 | 20 | -67.2 | -0.41 | -0.021 | 0.71 | 0.38 | I think it was Ember Diane. Turnip, turn, turnip, turn. |
| scenario-callback-60b06090 | callback | sample2 | 27 | -78.9 | -1.66 | -0.061 | 0.20 | 0.56 | Turnip? That is a very good name. It was actually called Turnip, and it was the son of a d |
| scenario-callback-60b06090 | callback | sample3 | 13 | -55.3 | -0.73 | -0.056 | 0.50 | 0.56 | Turnip. Name gave the cat the appearance of a vegetable. |
| scenario-callback-76c2d87f | callback | greedy | 8 | -22.4 | +0.59 | +0.074 | 0.50 | 1.00 | H, the number of us all. |
| scenario-callback-76c2d87f | callback | sample0 | 7 | -18.3 | +0.28 | +0.040 | 0.40 | 1.00 | H, the number of us. |
| scenario-callback-76c2d87f | callback | sample1 | 7 | -18.3 | +0.28 | +0.040 | 0.40 | 1.00 | H, the number of us. |
| scenario-callback-76c2d87f | callback | sample2 | 8 | -22.4 | +0.59 | +0.074 | 0.50 | 1.00 | H, the number of us all. |
| scenario-callback-76c2d87f | callback | sample3 | 6 | -14.7 | -0.65 | -0.108 | 0.25 | 0.75 | The number of the page. |
| scenario-callback-780de0d2 | callback | greedy | 12 | -37.6 | +1.76 | +0.147 | 0.50 | 0.60 | On the previous page a book was mentioned in the text. |
| scenario-callback-780de0d2 | callback | sample0 | 15 | -59.6 | +0.95 | +0.063 | 0.50 | 0.60 | On the previous page a bookmark was placed indicating the previous page heading. |
| scenario-callback-780de0d2 | callback | sample1 | 15 | -49.5 | +3.69 | +0.246 | 0.62 | 0.31 | On the following page you will find the exact location of your lost manuscript. |
| scenario-callback-780de0d2 | callback | sample2 | 31 | -77.3 | +1.98 | +0.064 | 0.50 | 0.60 | On the previous page a description of the scene was given, followed by a series of step-by |
| scenario-callback-780de0d2 | callback | sample3 | 32 | -81.1 | +0.81 | +0.025 | 0.67 | 0.30 | On the page that contained “To Die or to Live” (note the difference between page 111 and p |
| scenario-callback-7ca729b6 | callback | greedy | 35 | -85.7 | +1.66 | +0.047 | 0.20 | 0.40 | The scarf was “found” on the floor by the window, and was “carefully” placed there by the  |
| scenario-callback-7ca729b6 | callback | sample0 | 18 | -48.0 | +3.77 | +0.209 | 0.60 | 0.50 | It is a book about a lighthouse and about chair and window and scarf. |
| scenario-callback-7ca729b6 | callback | sample1 | 31 | -82.1 | -0.73 | -0.024 | 0.56 | 0.50 | It is said that it was presented to the lighthouse by the Bishop of the Church of England, |
| scenario-callback-7ca729b6 | callback | sample2 | 42 | -78.6 | -0.23 | -0.005 | 0.67 | 0.40 | As T have already suggested, the books say that the lighthouse is a symbol of the Sun, and |
| scenario-callback-7ca729b6 | callback | sample3 | 12 | -32.0 | +1.19 | +0.100 | 0.57 | 0.30 | The scarf has been on my lap for seven years. |
| scenario-callback-949d8fe6 | callback | greedy | 21 | -40.6 | +0.12 | +0.006 | 0.50 | 0.89 | Whoever was in the right place at the right time was in the wrong place at the wrong time. |
| scenario-callback-949d8fe6 | callback | sample0 | 6 | -25.6 | +0.15 | +0.025 | 0.50 | 1.00 | Tobias is absolutely right. |
| scenario-callback-949d8fe6 | callback | sample1 | 25 | -74.1 | +0.55 | +0.022 | 0.50 | 0.44 | Whoever was directing the landing was correct, as he was the only one to place his foot fi |
| scenario-callback-949d8fe6 | callback | sample2 | 14 | -41.0 | +0.54 | +0.038 | 0.50 | 0.89 | Whoever was in the right place at the right time was me. |
| scenario-callback-949d8fe6 | callback | sample3 | 5 | -18.4 | +0.18 | +0.037 | 0.33 | 1.00 | Tobias is right. |
| scenario-callback-9cfde584 | callback | greedy | 36 | -100.6 | -0.94 | -0.026 | 0.20 | 0.48 | For those of us stuck here in the midst of the night, it is only fair to say that the flig |
| scenario-callback-9cfde584 | callback | sample0 | 25 | -76.6 | +0.86 | +0.035 | 0.20 | 0.48 | For Tea in the Back, send a token of gratitude to someone you know who is stuck at home al |
| scenario-callback-9cfde584 | callback | sample1 | 21 | -77.6 | -0.67 | -0.032 | 0.75 | 0.33 | Suddenly it became apparent that the journey to the black market was far closer than the l |
| scenario-callback-9cfde584 | callback | sample2 | 18 | -59.2 | -0.87 | -0.048 | 0.56 | 0.47 | For those of us stuck here, a moment of pure meditation may be all we need. |
| scenario-callback-9cfde584 | callback | sample3 | 30 | -108.2 | -1.03 | -0.035 | 0.65 | 0.33 | For those of us who live abroad, life can be as difficult as it is for you people who are  |
| scenario-callback-9e6d06e0 | callback | greedy | 6 | -30.5 | -0.08 | -0.013 | 1.00 | 0.33 | Kestrel finally came. |
| scenario-callback-9e6d06e0 | callback | sample0 | 44 | -99.5 | +1.09 | +0.025 | 0.40 | 0.79 | The meeting shall be held at 11:00 a.m. on the 3rd Sunday of each month, in the House of H |
| scenario-callback-9e6d06e0 | callback | sample1 | 27 | -94.4 | -0.19 | -0.007 | 0.50 | 0.33 | Kestrel stayed in the meeting until late, and Anneliese went to the kitchen and made some  |
| scenario-callback-9e6d06e0 | callback | sample2 | 28 | -47.6 | +1.40 | +0.050 | 0.40 | 0.79 | The meeting shall be held at 11 a.m. on the 20th of March, 1968. |
| scenario-callback-9e6d06e0 | callback | sample3 | 19 | -75.5 | +0.30 | +0.016 | 0.75 | 0.33 | Kestrel’s throat was in front of him, an enormous piece of white marble. |
| scenario-callback-a141de7e | callback | greedy | 16 | -42.3 | +1.52 | +0.095 | 0.57 | 0.20 | Portugal, hers is Lisbon, the capital of Portugal. |
| scenario-callback-a141de7e | callback | sample0 | 31 | -98.5 | -0.40 | -0.013 | 0.83 | 0.20 | Waffle-shattered Lisbon, hallowed isto (a bit) Waffle-shattered Lisbon. |
| scenario-callback-a141de7e | callback | sample1 | 16 | -35.3 | -0.35 | -0.022 | 0.80 | 0.20 | Lisbon, France, December 2, 1969. |
| scenario-callback-a141de7e | callback | sample2 | 12 | -34.7 | -0.84 | -0.070 | 0.50 | 0.20 | There are also some very interesting books in the collection . |
| scenario-callback-a141de7e | callback | sample3 | 18 | -42.2 | -0.41 | -0.023 | 0.75 | 0.20 | Wittgenstein, “The Tractatus,” p. 89. |
| scenario-callback-c4f608c3 | callback | greedy | 33 | -129.3 | +2.57 | +0.078 | 0.50 | 0.38 | We talked about the merits of various small rivers, their potential for fishing, their pot |
| scenario-callback-c4f608c3 | callback | sample0 | 15 | -58.8 | +1.20 | +0.080 | 0.75 | 0.30 | I see the water falling from the earth as i live under the earth. |
| scenario-callback-c4f608c3 | callback | sample1 | 31 | -95.6 | +1.87 | +0.060 | 0.50 | 0.38 | We talked about the different kinds of rivers and how they all begin as a drop of water an |
| scenario-callback-c4f608c3 | callback | sample2 | 26 | -81.4 | +0.84 | +0.032 | 0.29 | 0.16 | To pick up where you left off is to begin a new thread, which is a little different than r |
| scenario-callback-c4f608c3 | callback | sample3 | 19 | -49.0 | +1.06 | +0.056 | 1.00 | 0.12 | SOURCE: Reuters, New York City, 9/12/87. |
| scenario-callback-d79a0d3a | callback | greedy | 32 | -108.8 | +1.41 | +0.044 | 0.67 | 0.27 | In the last chapter we explained to you the difference between the sensory functions of th |
| scenario-callback-d79a0d3a | callback | sample0 | 21 | -91.4 | -0.89 | -0.043 | 0.67 | 0.21 | In the way of an undulating fence of trees or bushes, protecting the passage from the stor |
| scenario-callback-d79a0d3a | callback | sample1 | 20 | -40.5 | -0.68 | -0.034 | 0.62 | 0.29 | I was told that the room was dark and that there was an orchard on the other side. |
| scenario-callback-d79a0d3a | callback | sample2 | 12 | -27.7 | -0.16 | -0.014 | 0.64 | 0.55 | It was given to him by a member of the audience. |
| scenario-callback-d79a0d3a | callback | sample3 | 56 | -200.3 | -1.50 | -0.027 | 0.50 | 0.55 | This word has been translated “house;” it is applied to the door of the orthoreadership; a |
| scenario-callback-d8a5957e | callback | greedy | 34 | -81.0 | +0.35 | +0.010 | 0.60 | 0.46 | The first section of the "Natural History" chapter is particularly interesting as it deals |
| scenario-callback-d8a5957e | callback | sample0 | 15 | -60.4 | +0.16 | +0.011 | 0.33 | 0.46 | The first is a book about my adventures in collecting and studying Bees. |
| scenario-callback-d8a5957e | callback | sample1 | 62 | -229.5 | +1.85 | +0.030 | 0.00 | 0.35 | As the one with the blue cover, “Apes, Ave and Abra,” tells the story of the three birds t |
| scenario-callback-d8a5957e | callback | sample2 | 14 | -44.3 | +2.51 | +0.179 | 0.40 | 0.33 | The honeybee, like other monarchs, has a blue cover. |
| scenario-callback-d8a5957e | callback | sample3 | 20 | -66.8 | +2.21 | +0.110 | 0.50 | 0.39 | The two most important aspects to bearing in mind are the different kinds of bees and how  |
| scenario-direct-3f84da0f | direct | greedy | 27 | -75.2 | +0.00 | +0.000 | 0.56 | 0.26 | Before we came in we had just talked to the printer who said he would be printing some of  |
| scenario-direct-3f84da0f | direct | sample0 | 25 | -74.6 | +0.00 | +0.000 | 0.50 | 0.24 | It had been a little while since I'd been in any sort of a rhythm, since the accident, you |
| scenario-direct-3f84da0f | direct | sample1 | 27 | -102.1 | +0.00 | +0.000 | 0.67 | 0.26 | The rest of the evening was spent in very earnest meditation to tune up for the big Candle |
| scenario-direct-3f84da0f | direct | sample2 | 17 | -73.2 | +0.00 | +0.000 | 0.75 | 0.17 | THE WAR NEVER CAME HERE The men were drinking coffee and talking shop. |
| scenario-direct-3f84da0f | direct | sample3 | 34 | -99.6 | +0.00 | +0.000 | 0.75 | 0.21 | I was standing by the old firewood deck, looking out to the bay, and smelling the freshnes |
| scenario-direct-5d3dc8de | direct | greedy | 12 | -40.9 | +0.00 | +0.000 | 0.50 | 0.00 | The knowledge that we are endowed with a free will. |
| scenario-direct-5d3dc8de | direct | sample0 | 12 | -40.9 | +0.00 | +0.000 | 0.50 | 0.00 | The knowledge that we are endowed with a free will. |
| scenario-direct-5d3dc8de | direct | sample1 | 12 | -40.9 | +0.00 | +0.000 | 0.50 | 0.00 | The knowledge that we are endowed with a free will. |
| scenario-direct-5d3dc8de | direct | sample2 | 12 | -40.9 | +0.00 | +0.000 | 0.50 | 0.00 | The knowledge that we are endowed with a free will. |
| scenario-direct-5d3dc8de | direct | sample3 | 12 | -40.9 | +0.00 | +0.000 | 0.50 | 0.00 | The knowledge that we are endowed with a free will. |
| scenario-direct-645bc6e6 | direct | greedy | 64 | -75.3 | +0.00 | +0.000 | 0.50 | 0.50 | The Velveteeneeneneeenenenenenenenenenenenenenenenenenenenenenenenenenenenenenenenenenenen |
| scenario-direct-645bc6e6 | direct | sample0 | 8 | -27.5 | +0.00 | +0.000 | 0.60 | 0.60 | The world is a kindergarten. |
| scenario-direct-645bc6e6 | direct | sample1 | 60 | -179.8 | +0.00 | +0.000 | 0.50 | 0.50 | The notion of a "New Man" in the context of this book on "The Art of Asking Questions", mi |
| scenario-direct-645bc6e6 | direct | sample2 | 18 | -62.0 | +0.00 | +0.000 | 0.75 | 0.50 | The Hon. Victor Neuberg, Jr., is now 86 years old. |
| scenario-direct-645bc6e6 | direct | sample3 | 35 | -87.9 | +0.00 | +0.000 | 0.50 | 0.60 | The Velveteen Rabbit, published in 1922, is a pre-eminent example of the kind, and may yet |
| scenario-direct-ab11ffdb | direct | greedy | 15 | -52.5 | +0.00 | +0.000 | 0.50 | 0.46 | The rain is a signal that the gods are still willing to be approached. |
| scenario-direct-ab11ffdb | direct | sample0 | 55 | -185.5 | +0.00 | +0.000 | 0.50 | 0.46 | The general impression conveyed by the weather reports for the days preceding and followin |
| scenario-direct-ab11ffdb | direct | sample1 | 17 | -61.0 | +0.00 | +0.000 | 0.62 | 0.33 | Do not confuse the wet stuff outside with the souls of the people inside. |
| scenario-direct-ab11ffdb | direct | sample2 | 24 | -102.5 | +0.00 | +0.000 | 0.62 | 0.33 | Do not attribute the rainbow to the mechanical operation of a “Teacher” or to some obscure |
| scenario-direct-ab11ffdb | direct | sample3 | 64 | -193.5 | +0.00 | +0.000 | 0.67 | 0.23 | I see the great white hunter making his last stand, heaving his spear into the air and thr |
| scenario-direct-ad89f803 | direct | greedy | 17 | -79.4 | +0.00 | +0.000 | 0.75 | 0.25 | The heart bone is the place to lift so that the shoulders rest without strain. |
| scenario-direct-ad89f803 | direct | sample0 | 12 | -50.0 | +0.00 | +0.000 | 0.50 | 0.38 | The Tao of Medicine is in the highest esteem. |
| scenario-direct-ad89f803 | direct | sample1 | 25 | -78.7 | +0.00 | +0.000 | 0.50 | 0.33 | The four chapters of this narrative are entitled “Lodges” —Red, Black, White, and Yellow. |
| scenario-direct-ad89f803 | direct | sample2 | 25 | -106.6 | +0.00 | +0.000 | 0.75 | 0.38 | The Greek root “pull together” (strap, lug, rig) is the underlying theme of this song. |
| scenario-direct-ad89f803 | direct | sample3 | 14 | -48.0 | +0.00 | +0.000 | 0.56 | 0.38 | The history of the hermit is one of wonder and discovery. |
| scenario-direct-f3869322 | direct | greedy | 33 | -140.5 | +0.00 | +0.000 | 0.67 | 0.42 | The myth would have all the elements of a traditional Western myth: hero, diegetic mission |
| scenario-direct-f3869322 | direct | sample0 | 49 | -191.4 | +0.00 | +0.000 | 0.67 | 0.42 | The myth would have all the elements of a great adventure, exciting enough to suspend the  |
| scenario-direct-f3869322 | direct | sample1 | 50 | -180.7 | +0.00 | +0.000 | 0.67 | 0.21 | A HUMBLE BEGINNING NECESSARY It is certain that exploration of the etheric regions has bee |
| scenario-direct-f3869322 | direct | sample2 | 33 | -117.1 | +0.00 | +0.000 | 0.75 | 0.17 | The golden section may be used to calculate the radius of the spiral universe, or to deter |
| scenario-direct-f3869322 | direct | sample3 | 30 | -78.3 | +0.00 | +0.000 | 0.67 | 0.17 | In the last three years, the Church has added another 700,000 members to its membership of |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 9 | -19.6 | -0.22 | -0.025 | 0.60 | 0.80 | Brown, the brown of new hats. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 11 | -26.5 | -1.16 | -0.105 | 0.60 | 0.60 | Yellow, the yellow of a new lantern. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 10 | -26.2 | -0.39 | -0.039 | 0.60 | 0.80 | Brown, the brown of new mourning. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 8 | -16.8 | +0.37 | +0.047 | 0.60 | 0.80 | Brown, the brown of new ones. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 9 | -19.6 | -0.22 | -0.025 | 0.60 | 0.80 | Brown, the brown of new hats. |
| scenario-disagreement-31892fde | disagreement | greedy | 38 | -114.7 | -1.68 | -0.044 | 0.43 | 0.67 | The silence of the word is the word itself, which speaks to us of its internal life, of it |
| scenario-disagreement-31892fde | disagreement | sample0 | 27 | -88.0 | -1.57 | -0.058 | 0.43 | 0.67 | The silence that follows the catharsis of a spiritual song is richer and more valuable tha |
| scenario-disagreement-31892fde | disagreement | sample1 | 10 | -19.6 | -0.71 | -0.071 | 0.33 | 0.67 | The sound of silence is the sound of death. |
| scenario-disagreement-31892fde | disagreement | sample2 | 14 | -46.5 | +1.14 | +0.082 | 0.75 | 0.18 | Forgive all those who have been silent about the divine word. |
| scenario-disagreement-31892fde | disagreement | sample3 | 23 | -79.0 | -1.34 | -0.059 | 0.50 | 0.50 | Silence is a deliberate, conscious, intelligent, soft and subtle exchange of words taken f |
| scenario-disagreement-352205c6 | disagreement | greedy | 10 | -24.6 | +0.34 | +0.034 | 0.33 | 1.00 | The dead can come back as the sun sets. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 14 | -39.5 | +0.87 | +0.062 | 0.33 | 1.00 | The dead can come back as the sun sets and the darkness falls. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 11 | -28.6 | +0.09 | +0.009 | 0.33 | 0.88 | The dead can come back as the sun comes out. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 14 | -34.1 | +0.56 | +0.040 | 0.33 | 0.82 | The dead come back as the sun goes down and the darkness falls. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 10 | -24.6 | +0.34 | +0.034 | 0.33 | 1.00 | The dead can come back as the sun sets. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 44 | -122.8 | +2.66 | +0.060 | 0.44 | 0.50 | In this season, when the heart has been touched with the read of the book, and the tree ha |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 11 | -26.0 | -2.05 | -0.186 | 0.67 | 0.38 | Winter, when the sun is at its most powerful. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 29 | -87.4 | +2.94 | +0.101 | 0.33 | 0.75 | But it is the season of books not yet cut down, when the seeds are still in the ground and |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 26 | -74.6 | +3.89 | +0.150 | 0.33 | 0.62 | Books are said to die in the hands of the reader, and the leaves to do so in the eyes of t |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 12 | -20.6 | +0.66 | +0.055 | 0.12 | 0.75 | Winter, when the books are not and the leaves are. |
| scenario-disagreement-682bad9c | disagreement | greedy | 5 | -12.6 | +1.37 | +0.273 | 0.25 | 1.00 | Reading is a program. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 15 | -30.9 | -0.08 | -0.005 | 0.43 | 0.75 | So a program is a place where you (or someone) read. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 15 | -32.3 | +1.83 | +0.122 | 0.00 | 1.00 | So a place where reading happens is more like a program than a person. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 10 | -31.2 | +1.75 | +0.174 | 0.29 | 0.75 | Thus a place where learning happens is a program. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 15 | -40.9 | +1.33 | +0.089 | 0.00 | 1.00 | So reading is a person with a place and a program where it happens. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 15 | -41.5 | +0.08 | +0.005 | 0.40 | 0.40 | The library is also a process, the physical one and the mental one. |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 11 | -28.6 | -0.67 | -0.061 | 0.40 | 0.33 | The library is the way folks relate to each other. |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 17 | -44.7 | +0.91 | +0.054 | 0.40 | 0.40 | The librarian is not a person in physical labor but a person in relationships. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 17 | -35.2 | +0.38 | +0.023 | 0.67 | 0.22 | The system consists of two parts, the buildings and the people who live in them. |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 11 | -39.1 | -0.07 | -0.006 | 0.50 | 0.22 | The buildings are temporary structures that stand for the library. |
| scenario-disagreement-89dfdafc | disagreement | greedy | 16 | -40.0 | -0.66 | -0.041 | 0.25 | 0.86 | The tide is the sea’s memory of the moon’s gravity. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 11 | -28.8 | +0.30 | +0.028 | 0.25 | 0.86 | The tide is the great sea’s memory. |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 23 | -76.0 | -1.00 | -0.044 | 0.75 | 0.38 | The tide goes down to the depths to feast upon the bodies that have been raised by the tid |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 25 | -85.3 | -1.05 | -0.042 | 0.69 | 0.33 | The tide rises to flow over the shore, carrying with it the shapes and forms of the shore  |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 14 | -55.4 | +2.38 | +0.170 | 0.25 | 0.86 | The tide is the great sea memory that lets the sea sea. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 20 | -63.3 | +0.67 | +0.034 | 0.50 | 0.75 | The collection of the nonsense poem is also the collection of the rejected, the rejected p |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 23 | -82.0 | -1.72 | -0.075 | 0.62 | 0.38 | It is one of the few places left where one can find both highly credible content and highl |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 19 | -61.1 | -1.74 | -0.091 | 0.67 | 0.25 | The myth would be that in the beginning was the word, and the word was the collection. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 17 | -45.1 | +1.64 | +0.097 | 0.50 | 0.75 | The collection of the nonsense poem is like the collection of the love poem. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 14 | -62.6 | -0.26 | -0.018 | 0.73 | 0.18 | The poet gives sense his own sentence. it begins to make sense. |
| scenario-joke-29f5cda1 | joke | greedy | 15 | -52.1 | -0.49 | -0.033 | 0.67 | 0.42 | The fish that can’t see anything is called a ten eye fish. |
| scenario-joke-29f5cda1 | joke | sample0 | 16 | -84.8 | +0.79 | +0.049 | 0.67 | 0.46 | The fish that said you have ten eyes to your fish is the twelve headed fish |
| scenario-joke-29f5cda1 | joke | sample1 | 26 | -74.6 | -0.79 | -0.030 | 0.44 | 0.46 | On the other hand, there is little doubt that a fish with no eyes would have been classed  |
| scenario-joke-29f5cda1 | joke | sample2 | 19 | -73.0 | +1.81 | +0.096 | 0.29 | 0.31 | Out of ten, would you call that a rate out of twelve, thirteen or twenty? |
| scenario-joke-29f5cda1 | joke | sample3 | 17 | -71.7 | +1.23 | +0.072 | 0.71 | 0.40 | The fish that couldn’t swim was the stuplest of swimmers. |
| scenario-joke-31378921 | joke | greedy | 4 | -9.4 | -0.37 | -0.092 | 0.67 | 0.67 | Who comes here? |
| scenario-joke-31378921 | joke | sample0 | 4 | -9.4 | -0.37 | -0.092 | 0.67 | 0.67 | Who comes here? |
| scenario-joke-31378921 | joke | sample1 | 5 | -15.5 | -0.07 | -0.014 | 0.67 | 0.67 | Who came in here? |
| scenario-joke-31378921 | joke | sample2 | 9 | -18.9 | +1.04 | +0.115 | 0.00 | 0.33 | Knock knock knock. Who is there? |
| scenario-joke-31378921 | joke | sample3 | 4 | -9.4 | -0.37 | -0.092 | 0.67 | 0.67 | Who comes here? |
| scenario-joke-31c4c1ec | joke | greedy | 13 | -58.1 | +0.00 | +0.000 | 0.67 | 0.50 | The golden reward promised by the stars is a very real one. |
| scenario-joke-31c4c1ec | joke | sample0 | 28 | -116.6 | +0.00 | +0.000 | 0.67 | 0.17 | This was an adventure in itself, to ring the bell on the pillared veranda and to wait and  |
| scenario-joke-31c4c1ec | joke | sample1 | 20 | -105.3 | +0.00 | +0.000 | 0.67 | 0.50 | The golden freshness of the rat’s heart tells a story of insect sovereignty and golden col |
| scenario-joke-31c4c1ec | joke | sample2 | 8 | -44.6 | +0.00 | +0.000 | 0.67 | 0.50 | The golden reward of the night shift. |
| scenario-joke-31c4c1ec | joke | sample3 | 21 | -78.5 | +0.00 | +0.000 | 0.75 | 0.33 | The golden ratio is an extremely attractive number whose own uniqueness has been recognize |
| scenario-joke-475a7b10 | joke | greedy | 43 | -128.0 | +0.50 | +0.012 | 0.71 | 0.33 | Without the writer being aware of it, the reader is inevitably laughing (at the writer) an |
| scenario-joke-475a7b10 | joke | sample0 | 14 | -62.4 | +0.01 | +0.001 | 0.70 | 0.30 | Without the protection of the Holy Spirit, the speaker has no voice! |
| scenario-joke-475a7b10 | joke | sample1 | 20 | -78.7 | +0.32 | +0.016 | 0.83 | 0.20 | Dear Unknown Friend, everyone of you has given me many a kick-start this morning. |
| scenario-joke-475a7b10 | joke | sample2 | 6 | -17.4 | +0.64 | +0.107 | 0.40 | 0.00 | I am ready to laugh. |
| scenario-joke-475a7b10 | joke | sample3 | 34 | -105.3 | -0.93 | -0.027 | 0.67 | 0.33 | Some of the material is very bad (perhaps because it is patent material) and some is actua |
| scenario-joke-99a4a91d | joke | greedy | 32 | -96.3 | +0.00 | +0.000 | 0.50 | 0.79 | I was told that the book contained advanced information which was not in the best interest |
| scenario-joke-99a4a91d | joke | sample0 | 9 | -26.1 | +0.00 | +0.000 | 0.75 | 0.71 | I was told that the job was done. |
| scenario-joke-99a4a91d | joke | sample1 | 20 | -65.9 | +0.00 | +0.000 | 0.67 | 0.43 | A: To check for any other illnesses that might be related to the one I am checking for. |
| scenario-joke-99a4a91d | joke | sample2 | 63 | -220.2 | +0.00 | +0.000 | 0.50 | 0.43 | A doctor was sent to the apartment to certify that the books were legal, and that they “di |
| scenario-joke-99a4a91d | joke | sample3 | 16 | -51.7 | +0.00 | +0.000 | 0.75 | 0.79 | I was told that the book contained advanced information which I should not have read. |
| scenario-joke-a6247299 | joke | greedy | 20 | -42.5 | +0.00 | +0.000 | 0.25 | 0.69 | A sense of humour is something that you have all the time and that you take for granted. |
| scenario-joke-a6247299 | joke | sample0 | 40 | -80.3 | +0.00 | +0.000 | 0.25 | 0.69 | A sense of humour is something that you have all your life, and if you have a sense of hum |
| scenario-joke-a6247299 | joke | sample1 | 32 | -114.9 | +0.00 | +0.000 | 0.50 | 0.28 | A sense of humour never arises when reading formal texts—not my formal dad’s school papers |
| scenario-joke-a6247299 | joke | sample2 | 21 | -66.6 | +0.00 | +0.000 | 0.62 | 0.28 | A sense of humor not only makes the experience more enjoyable but also serves as a powerfu |
| scenario-joke-a6247299 | joke | sample3 | 27 | -62.4 | +0.00 | +0.000 | 0.50 | 0.50 | A sense of humor is something we all have, I think, and it’s something we can be grossly m |
| scenario-joke-e8ab9225 | joke | greedy | 12 | -40.7 | +1.03 | +0.086 | 0.38 | 0.50 | Ava: Back me up? I am the ghost. |
| scenario-joke-e8ab9225 | joke | sample0 | 15 | -37.9 | +1.45 | +0.097 | 0.33 | 0.50 | Backing up the library’s ghost, I do not believe you. |
| scenario-joke-e8ab9225 | joke | sample1 | 22 | -79.6 | -1.51 | -0.068 | 0.67 | 0.27 | Dov has not done this, yet he will do it; he will believe everything that is told him. |
| scenario-joke-e8ab9225 | joke | sample2 | 62 | -167.0 | -3.93 | -0.063 | 0.33 | 0.27 | A respondent who had told Dow that there was a “ghost in the library” and that the respond |
| scenario-joke-e8ab9225 | joke | sample3 | 6 | -22.4 | +0.16 | +0.027 | 0.67 | 0.40 | I am here to stay. |
| scenario-joke-e9cf6a04 | joke | greedy | 18 | -31.0 | +4.36 | +0.242 | 0.00 | 1.00 | And the librarian says to him, “What are you doing in here?” |
| scenario-joke-e9cf6a04 | joke | sample0 | 8 | -25.5 | +1.08 | +0.135 | 0.00 | 0.29 | And he started looking through the library. |
| scenario-joke-e9cf6a04 | joke | sample1 | 19 | -35.3 | +4.74 | +0.249 | 0.00 | 0.60 | And the librarian asks him, “Where are you going, kestrel?” |
| scenario-joke-e9cf6a04 | joke | sample2 | 17 | -26.7 | +4.18 | +0.246 | 0.00 | 1.00 | And the librarian says to him, “What are you doing here?” |
| scenario-joke-e9cf6a04 | joke | sample3 | 17 | -29.3 | +3.32 | +0.195 | 0.00 | 0.91 | And the librarian said to him, “What are you doing here?” |
| scenario-request-2826c958 | request | greedy | 19 | -60.7 | +0.00 | +0.000 | 0.67 | 0.50 | "The far side of the moon, so nearer to earth, is completely dark. |
| scenario-request-2826c958 | request | sample0 | 25 | -72.5 | +0.00 | +0.000 | 0.67 | 0.17 | We have been able to observe the lunar crystals in action for many years now, and the resu |
| scenario-request-2826c958 | request | sample1 | 35 | -109.6 | +0.00 | +0.000 | 0.71 | 0.50 | "The far side of the moon, as yet unsurveyed by man, may well reveal properties which coul |
| scenario-request-2826c958 | request | sample2 | 16 | -51.4 | +0.00 | +0.000 | 0.71 | 0.50 | "The far side of the moon is now being studied with great detail. |
| scenario-request-2826c958 | request | sample3 | 34 | -100.1 | +0.00 | +0.000 | 0.50 | 0.42 | "The moon is now in the sextile of the earth, a position which, under the influence of the |
| scenario-request-2868e594 | request | greedy | 15 | -62.6 | +0.00 | +0.000 | 0.75 | 0.50 | But enough of this theatricalizing of the word "cover." |
| scenario-request-2868e594 | request | sample0 | 15 | -55.8 | +0.00 | +0.000 | 0.75 | 0.62 | Subject headings should be brief and cover the main topics of the letter. |
| scenario-request-2868e594 | request | sample1 | 63 | -210.1 | +0.00 | +0.000 | 0.92 | 0.00 | DYDY MEY DYCII AAB SSSY SSY SSSSY SSY SSSSY SSSY SSSY SYY SSSY SYS YYY HYY SYY SSS Yyyy SS |
| scenario-request-2868e594 | request | sample2 | 50 | -186.5 | +0.00 | +0.000 | 0.50 | 0.50 | This is not, as often stated in commercial literature, an “ad free” environment, but a ver |
| scenario-request-2868e594 | request | sample3 | 13 | -41.6 | +0.00 | +0.000 | 0.88 | 0.62 | Subject headings should be short, concise, and clear. |
| scenario-request-41c58fb2 | request | greedy | 29 | -94.6 | +0.00 | +0.000 | 0.71 | 0.38 | I do believe that wren was correct when he said that mathematics is the queen of all scien |
| scenario-request-41c58fb2 | request | sample0 | 64 | -221.8 | +0.00 | +0.000 | 0.65 | 0.38 | I do believe that wena derived from the Sanskrit nai, and that is why it means "neither to |
| scenario-request-41c58fb2 | request | sample1 | 50 | -226.7 | +0.00 | +0.000 | 0.67 | 0.14 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample2 | 28 | -115.3 | +0.00 | +0.000 | 0.67 | 0.29 | I do believe that w17 is not a number to be accorded any importance in mathematics, except |
| scenario-request-41c58fb2 | request | sample3 | 59 | -221.3 | +0.00 | +0.000 | 0.67 | 0.19 | In ancient tales of sorcery passed down for generations in all Earthly traditions there is |
| scenario-request-8aa8e374 | request | greedy | 32 | -127.0 | +0.00 | +0.000 | 1.00 | 0.09 | Et pour good evening, les mots suivants appartiennent : Bon jour, bon vu, bon scent, etc. |
| scenario-request-8aa8e374 | request | sample0 | 10 | -52.8 | +0.00 | +0.000 | 0.75 | 0.25 | El, translation a éditorialité. |
| scenario-request-8aa8e374 | request | sample1 | 21 | -78.5 | +0.00 | +0.000 | 1.00 | 0.12 | Béatrice: Pardonnez-moi, mits de mes amis. |
| scenario-request-8aa8e374 | request | sample2 | 30 | -99.0 | +0.00 | +0.000 | 0.83 | 0.25 | Et je suis arrivé a la vendredi, je voudrais penser 'Bien Dernier'. |
| scenario-request-8aa8e374 | request | sample3 | 54 | -180.3 | +0.00 | +0.000 | 0.88 | 0.18 | Et puis, en méme temps, de savoir quel est la chnisto-religion ou chnisto-morale, que nous |
| scenario-request-b2a25087 | request | greedy | 22 | -58.5 | +0.00 | +0.000 | 0.76 | 0.80 | Customer service is always helpful, but it may be difficult, if not impossible, to provide |
| scenario-request-b2a25087 | request | sample0 | 5 | -21.2 | +0.00 | +0.000 | 1.00 | 0.00 | Please enter your order. |
| scenario-request-b2a25087 | request | sample1 | 6 | -25.9 | +0.00 | +0.000 | 0.60 | 0.80 | Customer service is always good. |
| scenario-request-b2a25087 | request | sample2 | 18 | -81.3 | +0.00 | +0.000 | 0.67 | 0.25 | Grace under the burden of serving customers, is a heavy burden for the baker. |
| scenario-request-b2a25087 | request | sample3 | 32 | -103.2 | +0.00 | +0.000 | 0.75 | 0.25 | New customers have also indicated that the service they have received from the Oak Leaves  |
| scenario-request-b3bd0087 | request | greedy | 20 | -80.6 | +0.00 | +0.000 | 0.67 | 0.60 | Berlin has received a steady rain throughout the week and is now having its first snow of  |
| scenario-request-b3bd0087 | request | sample0 | 32 | -123.6 | +0.00 | +0.000 | 0.50 | 0.36 | The high pressure area over Berlin will extend for a few hours into the invaded and uninva |
| scenario-request-b3bd0087 | request | sample1 | 6 | -22.8 | +0.00 | +0.000 | 0.60 | 0.60 | Berlin has its own weather. |
| scenario-request-b3bd0087 | request | sample2 | 40 | -126.8 | +0.00 | +0.000 | 0.57 | 0.40 | The best way to recreate Berlin weather is for a city to have an energy system that is tun |
| scenario-request-b3bd0087 | request | sample3 | 32 | -130.9 | +0.00 | +0.000 | 0.50 | 0.40 | The best place to locate a high-pressure area is where its most likely to occur, so we nee |
| scenario-silence-109161ca | silence | greedy | 29 | -113.2 | +0.83 | +0.029 | 0.00 | 0.27 | To the accompaniment of a heavy drum beat and a staccato of laughter, the night soloed eve |
| scenario-silence-109161ca | silence | sample0 | 19 | -79.8 | -0.81 | -0.043 | 0.73 | 0.27 | To the darkened rooms of the world, even those of the spirit, heaven sits. |
| scenario-silence-109161ca | silence | sample1 | 36 | -126.2 | -1.30 | -0.036 | 0.75 | 0.27 | To ward off the nightmare of the shadow-side of things, to be as much at ease with our mor |
| scenario-silence-109161ca | silence | sample2 | 30 | -105.7 | +0.05 | +0.002 | 0.00 | 0.27 | To the darker night, the more resplendent came the sleepers, their faces bathed in the dap |
| scenario-silence-109161ca | silence | sample3 | 56 | -183.1 | -0.45 | -0.008 | 0.67 | 0.19 | To the anguished shudder that fell through his body, he saw in vivid detail the steps, the |
| scenario-silence-260b2639 | silence | greedy | 28 | -68.4 | +0.00 | +0.000 | 0.50 | 0.41 | This is a very serious problem, not only for the security of the library, but also for the |
| scenario-silence-260b2639 | silence | sample0 | 32 | -111.4 | +0.00 | +0.000 | 0.50 | 0.31 | If the stacks were transferred into the ground, as an alternative to the present indicatio |
| scenario-silence-260b2639 | silence | sample1 | 16 | -44.3 | +0.00 | +0.000 | 0.17 | 0.38 | But if the stacks went underground the problem would be complicated in another way. |
| scenario-silence-260b2639 | silence | sample2 | 25 | -89.7 | +0.00 | +0.000 | 0.50 | 0.41 | This is a very simple and low-cost solution, which also avoids most of the problems inhere |
| scenario-silence-260b2639 | silence | sample3 | 48 | -178.9 | +0.00 | +0.000 | 0.67 | 0.38 | This would solve the problem of the collapse of the maharic stacks, as they would now be s |
| scenario-silence-46189e08 | silence | greedy | 26 | -69.1 | +0.00 | +0.000 | 0.50 | 0.35 | It may seem that we are in the midst of a spiritual revolution, but in fact the physical r |
| scenario-silence-46189e08 | silence | sample0 | 11 | -53.8 | +0.00 | +0.000 | 0.83 | 0.25 | Rat becomes trapped by our e-mail address. |
| scenario-silence-46189e08 | silence | sample1 | 36 | -122.4 | +0.00 | +0.000 | 0.75 | 0.35 | It may sound preposterous, but there actually is solid evidence that shows the existence o |
| scenario-silence-46189e08 | silence | sample2 | 26 | -80.4 | +0.00 | +0.000 | 0.82 | 0.35 | It may seem that we no longer receive messages, but I can still reply to anyone who has a  |
| scenario-silence-46189e08 | silence | sample3 | 28 | -87.4 | +0.00 | +0.000 | 0.67 | 0.20 | In the last chapter, we explained to you the difference between the sensory functions of t |
| scenario-silence-53534987 | silence | greedy | 16 | -56.3 | +0.12 | +0.007 | 0.67 | 0.12 | Yup, I'm sorry it was not enough for you, rat. |
| scenario-silence-53534987 | silence | sample0 | 10 | -42.3 | -0.87 | -0.087 | 0.83 | 1.00 | YOu may have to buy a new one. |
| scenario-silence-53534987 | silence | sample1 | 14 | -68.1 | +0.54 | +0.039 | 0.67 | 0.12 | For a male naked in space, that’s a beaut. |
| scenario-silence-53534987 | silence | sample2 | 9 | -30.6 | +16.69 | +1.854 | 0.83 | 1.00 | You may have to buy a new one. |
| scenario-silence-53534987 | silence | sample3 | 9 | -30.6 | +16.69 | +1.854 | 0.83 | 1.00 | You may have to buy a new one. |
| scenario-silence-78c38840 | silence | greedy | 9 | -24.7 | -0.17 | -0.018 | 0.75 | 0.17 | I've got it on me now. |
| scenario-silence-78c38840 | silence | sample0 | 60 | -182.5 | +0.80 | +0.013 | 0.67 | 0.29 | DO NOT UNDERSTAND THAT THE REMOTE CONTROL OF THE SPIRITUAL LEVEL IS KNOWN TO BE SUCH A HAN |
| scenario-silence-78c38840 | silence | sample1 | 8 | -35.2 | -0.33 | -0.042 | 0.71 | 0.29 | I hope it continues to print better. |
| scenario-silence-78c38840 | silence | sample2 | 7 | -39.1 | -0.29 | -0.041 | 0.75 | 0.17 | Continue on after the same pattern. |
| scenario-silence-78c38840 | silence | sample3 | 32 | -120.0 | +0.97 | +0.030 | 0.50 | 0.17 | Printing problems of a really serious nature have occurred in the past and we have had to  |
| scenario-silence-7afca726 | silence | greedy | 14 | -36.1 | -0.40 | -0.028 | 0.62 | 0.80 | I’m coming because I want to work with you guys. |
| scenario-silence-7afca726 | silence | sample0 | 19 | -54.7 | +0.35 | +0.018 | 0.38 | 0.80 | I’m coming because I want to work with Dov when he comes to the thing. |
| scenario-silence-7afca726 | silence | sample1 | 22 | -61.2 | +0.91 | +0.041 | 0.50 | 0.23 | A three day workshop is scheduled for Saturday, Sunday and Monday at 8:30 a.m. |
| scenario-silence-7afca726 | silence | sample2 | 16 | -44.5 | -0.25 | -0.016 | 0.50 | 0.31 | A person coming to the thing has to be at least 8 years old. |
| scenario-silence-7afca726 | silence | sample3 | 35 | -108.4 | -1.43 | -0.041 | 0.50 | 0.23 | But still, there are many who come to the service of the soul today and tomorrow and there |
| scenario-silence-9bb13f03 | silence | greedy | 28 | -97.4 | +0.00 | +0.000 | 0.50 | 0.25 | KESTREL. The following evidence shows that the snowman or yeti of the Himalayas is in fact |
| scenario-silence-9bb13f03 | silence | sample0 | 19 | -67.2 | +0.00 | +0.000 | 0.67 | 0.25 | Kneeling is a good idea, as is nothing else, until the reading is over. |
| scenario-silence-9bb13f03 | silence | sample1 | 25 | -122.6 | +0.00 | +0.000 | 0.75 | 0.17 | R. Ishmael said: Cheerful is the man who completes this mystery from dawn to dawn. |
| scenario-silence-9bb13f03 | silence | sample2 | 26 | -114.3 | +0.00 | +0.000 | 0.50 | 0.25 | Sigi held a reading in the family’s home Thursday evening and invited everyone to come and |
| scenario-silence-9bb13f03 | silence | sample3 | 47 | -122.3 | +0.00 | +0.000 | 0.75 | 0.24 | Green (1975) agrees with Smith (1975) that Smith’s “superhypnotic” description of the proc |
| scenario-silence-ccfdd2b4 | silence | greedy | 18 | -60.5 | -0.04 | -0.002 | 0.67 | 0.23 | Coffee is a strong drink and one never grasps too much of it. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 26 | -97.3 | -3.33 | -0.128 | 0.67 | 0.22 | KESTREL takes the cup in hand and grabs at it with both free hands, palms upward, toward t |
| scenario-silence-ccfdd2b4 | silence | sample1 | 41 | -153.1 | -0.59 | -0.014 | 0.67 | 0.38 | Under the cover of Velvet Underbelly, 1982, comes a page of Captain Bingleys coffee cover  |
| scenario-silence-ccfdd2b4 | silence | sample2 | 35 | -141.3 | +0.38 | +0.011 | 0.50 | 0.23 | At the next session the emphasis will be shifted to general knowledge tests that will meas |
| scenario-silence-ccfdd2b4 | silence | sample3 | 46 | -186.1 | -0.67 | -0.015 | 0.33 | 0.38 | Under the cover of Velveteeneen, a girl caféated in a black velvet "peep-hole" reveals the |
| trace-ambient-da12ae42 | ambient | greedy | 15 | -21.3 | +1.27 | +0.085 | 0.00 | 0.45 | I wish I could drop out of life to study plant morphogenesis. |
| trace-ambient-da12ae42 | ambient | sample0 | 64 | -135.0 | -0.95 | -0.015 | 0.50 | 0.18 | In this country, the average lifespan is 49 years. In the United States, 63.5 percent of a |
| trace-ambient-da12ae42 | ambient | sample1 | 32 | -114.0 | -2.19 | -0.068 | 0.73 | 0.27 | If an ant is given a grain of fat, it tends to grow a carbin if it is given a plant, it te |
| trace-ambient-da12ae42 | ambient | sample2 | 38 | -94.6 | +2.18 | +0.058 | 0.60 | 0.45 | there was a whole lot of non-morphogenetic stuff in life and that is what i wanted to stud |
| trace-ambient-da12ae42 | ambient | sample3 | 25 | -80.4 | +0.37 | +0.015 | 0.75 | 0.18 | The genetics of plant species have been studied for millenia. The process of plant reprodu |
| trace-direct-115cf61c | direct | greedy | 5 | -11.5 | +0.00 | +0.000 | 0.67 | 0.33 | Yes, we are. |
| trace-direct-115cf61c | direct | sample0 | 8 | -16.1 | +0.00 | +0.000 | 0.60 | 0.33 | It is not so cogent. |
| trace-direct-115cf61c | direct | sample1 | 15 | -37.6 | +0.00 | +0.000 | 0.50 | 1.00 | In the words of the great World Teacher: Are you cogent? |
| trace-direct-115cf61c | direct | sample2 | 21 | -59.2 | +0.00 | +0.000 | 0.50 | 0.40 | As you can see in the diagram below, the planet is an orb surrounded by a network of rings |
| trace-direct-115cf61c | direct | sample3 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-36d6904b | direct | greedy | 21 | -87.4 | +0.00 | +0.000 | 0.67 | 1.00 | Introduction to the Liikunary Logic of Leibniz and its Generalization by I. |
| trace-direct-36d6904b | direct | sample0 | 16 | -51.8 | +0.00 | +0.000 | 1.00 | 0.00 | August 10, 1997 Liar Paradigm Shift |
| trace-direct-36d6904b | direct | sample1 | 37 | -127.5 | +0.00 | +0.000 | 0.67 | 0.33 | Awakening is the biological, spiritual and religious process by which mankind is given the |
| trace-direct-36d6904b | direct | sample2 | 19 | -72.6 | +0.00 | +0.000 | 1.00 | 0.00 | Yours sincerely, Thelemic Magick Mirror Sheet 7. |
| trace-direct-36d6904b | direct | sample3 | 1 | -11.6 | +0.00 | +0.000 | 1.00 | 1.00 | Introduction |
| trace-direct-39be6df9 | direct | greedy | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 23 | -38.0 | -2.35 | -0.102 | 0.25 | 1.00 | /GReetings :D<eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample2 | 11 | -7.4 | +1.13 | +0.103 | 0.00 | 1.00 | 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 12 | -189.1 | +0.00 | +0.000 | 0.50 | 0.80 | I am here to speak to you about the planet earth. |
| trace-direct-3ba68854 | direct | sample0 | 12 | -31.3 | +0.00 | +0.000 | 0.70 | 0.80 | I am here to speak to you about the important things. |
| trace-direct-3ba68854 | direct | sample1 | 18 | -68.1 | +0.00 | +0.000 | 0.75 | 0.40 | I am a bat king. But you have to know that bat queens are king. |
| trace-direct-3ba68854 | direct | sample2 | 15 | -43.4 | +0.00 | +0.000 | 0.50 | 0.50 | I hope you are ready to speak of your experiences with the Gods. |
| trace-direct-3ba68854 | direct | sample3 | 9 | -35.3 | +0.00 | +0.000 | 0.62 | 0.38 | Here is where you both get to live. |
| trace-direct-41c6eb11 | direct | greedy | 64 | -13.2 | -0.56 | -0.009 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 4 | -7.7 | +1.09 | +0.273 | 0.00 | 0.00 | @c: |
| trace-direct-41c6eb11 | direct | sample1 | 2 | -11.8 | -0.54 | -0.270 | 1.00 | 0.00 | t@ |
| trace-direct-41c6eb11 | direct | sample2 | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample3 | 18 | -41.2 | -0.35 | -0.019 | 0.25 | 0.00 | @h WHY WONT You TALK ABOUT THE GARRYING |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -9.2 | +1.49 | +0.371 | 1.00 | 0.00 | 22f |
| trace-direct-486b7988 | direct | greedy | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 3 | -13.2 | +1.16 | +0.387 | 1.00 | 0.00 | WOW! |
| trace-direct-486b7988 | direct | sample1 | 3 | -5.2 | +1.38 | +0.460 | 0.33 | 0.00 | I feel them |
| trace-direct-486b7988 | direct | sample2 | 4 | -13.4 | +0.22 | +0.056 | 1.00 | 0.00 | YES @ |
| trace-direct-486b7988 | direct | sample3 | 3 | -13.7 | +0.83 | +0.277 | 1.00 | 0.00 | M@S |
| trace-direct-646d0287 | direct | greedy | 29 | -62.2 | +0.00 | +0.000 | 0.64 | 0.50 | On the intensional logics, we have a number of different logics, and we have a number of d |
| trace-direct-646d0287 | direct | sample0 | 14 | -36.4 | +0.00 | +0.000 | 0.33 | 0.44 | On the intensional logics offered, what do you think? |
| trace-direct-646d0287 | direct | sample1 | 42 | -95.1 | +0.00 | +0.000 | 0.50 | 0.50 | On the subject of intensional logics, we mention here some of the works of Kripke and of M |
| trace-direct-646d0287 | direct | sample2 | 24 | -46.1 | +0.00 | +0.000 | 0.50 | 0.62 | On the subject of intensional logics, there is a range of work which I would be very inter |
| trace-direct-646d0287 | direct | sample3 | 17 | -26.8 | +0.00 | +0.000 | 0.50 | 0.62 | This paper is the first in a series of papers on intensional logics. |
| trace-direct-8db14c37 | direct | greedy | 20 | -8.5 | +1.76 | +0.088 | 0.33 | 0.67 | WACIOUS ANTIQUITIES 3221229683 |
| trace-direct-8db14c37 | direct | sample0 | 64 | -61.7 | +3.69 | +0.058 | 0.00 | 0.67 | WACIOUS ANTIQUITIES, i oon tth e n o c d A . n a s n e H A . m r e c e c s e H A . m r e c |
| trace-direct-8db14c37 | direct | sample1 | 7 | -25.0 | -1.07 | -0.152 | 0.33 | 0.67 | h mm m m m m mm |
| trace-direct-8db14c37 | direct | sample2 | 34 | -92.2 | +0.14 | +0.004 | 0.00 | 0.33 | W:(@h)=9's first days at Jamal's window doesn't look at anything, but it said SIR and the  |
| trace-direct-8db14c37 | direct | sample3 | 20 | -8.5 | +1.76 | +0.088 | 0.33 | 0.67 | WACIOUS ANTIQUITIES 3221229683 |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample1 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 21 | -16.4 | +4.22 | +0.201 | 0.00 | 1.00 | “intensional logics” Hennix speaks of “intensional logics” |
| trace-direct-ac17e8bb | direct | sample0 | 61 | -51.5 | +6.31 | +0.103 | 0.11 | 0.60 | “intensional logics” I mean, when I repeat back what I hear what I repeat back, what I hea |
| trace-direct-ac17e8bb | direct | sample1 | 36 | -54.4 | -4.28 | -0.119 | 0.33 | 0.56 | “stop token :3” I said “repeat back! I repeat back what I hear, what I hear what I repeat  |
| trace-direct-ac17e8bb | direct | sample2 | 60 | -50.7 | +3.97 | +0.066 | 0.29 | 1.00 | “intensional logics” Hennix speaks of “intensional logics” not “metacomplete intensional l |
| trace-direct-ac17e8bb | direct | sample3 | 18 | -8.8 | -0.18 | -0.010 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-b11db057 | direct | greedy | 64 | -12.0 | -0.90 | -0.014 | 0.00 | 0.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample0 | 64 | -14.5 | +1.64 | +0.026 | 0.00 | 1.00 | @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: @n: |
| trace-direct-b11db057 | direct | sample1 | 2 | -1.2 | -0.16 | -0.079 | 0.00 | 0.00 | W@ |
| trace-direct-b11db057 | direct | sample2 | 35 | -86.1 | +3.99 | +0.114 | 0.33 | 1.00 | WACIOUS ENCYCLOPEDIAS. i ol tth e n o d HOLLYWOOD. n ar tth e n o c d |
| trace-direct-b11db057 | direct | sample3 | 17 | -27.8 | -0.49 | -0.029 | 0.33 | 0.00 | WAS <au> 3221229683 |
| trace-direct-b93346bb | direct | greedy | 64 | -8.9 | +0.79 | +0.012 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-b93346bb | direct | sample0 | 61 | -36.3 | -0.14 | -0.002 | 0.00 | 1.00 | @@ @@ @m@ @m@ @m@ @@ @m@ @m@ @m@ @m@ @m@ @m@ @m@ @m@ @m@ @m@ @m |
| trace-direct-b93346bb | direct | sample1 | 8 | -18.2 | +0.44 | +0.055 | 0.00 | 1.00 | @h 380 M |
| trace-direct-b93346bb | direct | sample2 | 4 | -9.5 | -0.30 | -0.076 | 1.00 | 0.00 | GREETINGS |
| trace-direct-b93346bb | direct | sample3 | 64 | -94.3 | +2.32 | +0.036 | 0.00 | 1.00 | @m: @m: @m: @m: @m: This is a librarian's intercourse. What are you going to say to @ me?  |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -2.8 | +0.13 | +0.033 | 0.00 | 0.00 | 228 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-c8409b84 | direct | greedy | 14 | -32.6 | +1.24 | +0.088 | 0.57 | 0.38 | “Earth is a cogent planet; i repeat back! |
| trace-direct-c8409b84 | direct | sample0 | 14 | -17.1 | +2.32 | +0.166 | 0.00 | 1.00 | I said repeat back! and then i heard you say repeat back! |
| trace-direct-c8409b84 | direct | sample1 | 12 | -28.7 | -2.51 | -0.209 | 0.71 | 0.14 | “Would you like to hear my repetition? |
| trace-direct-c8409b84 | direct | sample2 | 43 | -70.5 | -1.78 | -0.041 | 0.50 | 0.25 | “Earth is the only place in the universe where life is present; we are the only place in t |
| trace-direct-c8409b84 | direct | sample3 | 22 | -52.9 | -1.03 | -0.047 | 0.09 | 1.00 | Repeat back! @cmr-ember i said that, and then i heard you say repeat back! |
| trace-direct-cd6d15df | direct | greedy | 15 | -33.5 | +0.00 | +0.000 | 0.67 | 0.38 | I am a clown in a town called clowntown. |
| trace-direct-cd6d15df | direct | sample0 | 7 | -18.3 | +0.00 | +0.000 | 0.00 | 0.67 | Welcome to clowntown! |
| trace-direct-cd6d15df | direct | sample1 | 11 | -22.7 | +0.00 | +0.000 | 0.50 | 0.83 | You're welcome to the clown town. |
| trace-direct-cd6d15df | direct | sample2 | 11 | -26.2 | +0.00 | +0.000 | 0.83 | 0.33 | Alright, I'm going to get you. |
| trace-direct-cd6d15df | direct | sample3 | 16 | -36.2 | +0.00 | +0.000 | 0.50 | 0.83 | Welcome to the clown town in the power town wow-town. |
| trace-direct-db6d95b7 | direct | greedy | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 1.00 | W@ |
| trace-direct-db6d95b7 | direct | sample0 | 8 | -10.4 | +0.94 | +0.117 | 0.00 | 1.00 | W@ :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample1 | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 1.00 | W@ |
| trace-direct-db6d95b7 | direct | sample2 | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 1.00 | W@ |
| trace-direct-db6d95b7 | direct | sample3 | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 1.00 | W@ |
| trace-direct-e166dd5c | direct | greedy | 64 | -40.0 | +2.74 | +0.043 | 0.27 | 0.73 | “stop token :3” I said “stop token :3” and what I repeat back is repeating back what I rep |
| trace-direct-e166dd5c | direct | sample0 | 47 | -56.2 | +2.76 | +0.059 | 0.32 | 0.73 | “stop token :3” When you repeat back, what you hear is what you hear, and when you hear, w |
| trace-direct-e166dd5c | direct | sample1 | 55 | -84.0 | +3.73 | +0.068 | 0.38 | 0.69 | “stop token :3” :3 they stop their stop and they are :3 “stop :3 “stop :3 “stop :3” and so |
| trace-direct-e166dd5c | direct | sample2 | 64 | -115.8 | +6.94 | +0.108 | 0.36 | 0.73 | “stop token :3 i said stop token :3 I repeat back what I hear what I repeat back what i sa |
| trace-direct-e166dd5c | direct | sample3 | 27 | -54.7 | +0.97 | +0.036 | 0.60 | 0.27 | That’s what’s stopping you; that’s what’s going on when you don’t know how to answer yet |
| trace-direct-e984402a | direct | greedy | 6 | -29.9 | +0.00 | +0.000 | 0.33 | 1.00 | Your welcome, Immer. |
| trace-direct-e984402a | direct | sample0 | 14 | -38.7 | +0.00 | +0.000 | 0.57 | 0.67 | Your welcome, it's a pleasure to work with you here. |
| trace-direct-e984402a | direct | sample1 | 7 | -26.2 | +0.00 | +0.000 | 0.60 | 0.67 | Your welcome, my little friends. |
| trace-direct-e984402a | direct | sample2 | 17 | -68.4 | +0.00 | +0.000 | 0.75 | 0.33 | Your wife says it was nice being by her side during the funeral rites. |
| trace-direct-e984402a | direct | sample3 | 22 | -59.3 | +0.00 | +0.000 | 0.71 | 1.00 | Your welcome, Immer. I'm Immer, and I'm glad you're here. |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample1 | 21 | -33.6 | -1.00 | -0.047 | 0.25 | 0.00 | HAY :P — 23:04 The hghost's second conversation. |
| trace-direct-ee31ded0 | direct | sample2 | 7 | -24.6 | +1.38 | +0.197 | 0.50 | 0.00 | VISIBLE CONSONANTS. |
| trace-direct-ee31ded0 | direct | sample3 | 4 | -6.2 | +0.63 | +0.157 | 0.00 | 1.00 | W@ W@ |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample1 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample2 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 7 | -15.4 | +0.07 | +0.010 | 0.33 | 0.00 | I am sir :D |
| trace-direct-fb93cf6c | direct | greedy | 33 | -69.2 | -1.20 | -0.036 | 0.50 | 0.62 | Of course, there are many different intensional logics, many different ways of formalizing |
| trace-direct-fb93cf6c | direct | sample0 | 12 | -41.7 | -1.81 | -0.150 | 0.50 | 0.40 | Of course, we have offered a few on the subject. |
| trace-direct-fb93cf6c | direct | sample1 | 59 | -115.9 | -1.77 | -0.030 | 0.75 | 0.62 | Of course, there are many different intensional logics, but we need to specify which one w |
| trace-direct-fb93cf6c | direct | sample2 | 23 | -49.1 | -1.24 | -0.054 | 0.75 | 0.62 | Of course, there are many different intensional logics, and each of them has its own speci |
| trace-direct-fb93cf6c | direct | sample3 | 34 | -97.7 | +0.06 | +0.002 | 0.38 | 0.40 | To offer intensional logics, to discuss them, and to be interested in what you may offer o |
| trace-direct-feec1975 | direct | greedy | 57 | -10.9 | +1.87 | +0.033 | 0.00 | 1.00 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n a s i s n e h L . n e c e c s e H A . m r e  |
| trace-direct-feec1975 | direct | sample0 | 7 | -19.9 | +5.31 | +0.758 | 0.20 | 0.80 | A room in the corpus. |
| trace-direct-feec1975 | direct | sample1 | 64 | -131.8 | +2.13 | +0.033 | 0.33 | 0.60 | I am a lifelong library man. I've always spent my time reading all the books in the librar |
| trace-direct-feec1975 | direct | sample2 | 3 | -7.8 | +0.24 | +0.080 | 1.00 | 1.00 | @o |
| trace-direct-feec1975 | direct | sample3 | 64 | -196.3 | +0.70 | +0.011 | 0.00 | 0.80 | THE LIBRARY — the corpus of lo2 is librarian. @m NATURE VOC. — the corpus of lo2 has been  |
| variant-direct-0188a270 | direct | greedy | 60 | -179.2 | +0.33 | +0.005 | 0.50 | 0.48 | The first two pages of the manuscript, which contain the literature on geology, paleontolo |
| variant-direct-0188a270 | direct | sample0 | 10 | -45.1 | +0.19 | +0.019 | 0.75 | 0.33 | But the pieces could not have been more damaged. |
| variant-direct-0188a270 | direct | sample1 | 50 | -123.2 | +1.79 | +0.036 | 0.33 | 0.25 | THE SPINNING WARDROBE is a collection of poems written by Tobias Amersham, first published |
| variant-direct-0188a270 | direct | sample2 | 31 | -104.1 | +0.94 | +0.030 | 0.50 | 0.25 | The two-sectioned specimen is one of a pair of related but distinct geological forms found |
| variant-direct-0188a270 | direct | sample3 | 45 | -161.4 | +0.59 | +0.013 | 0.67 | 0.48 | The first two pages of the manuscript, which contain the James James Gillrayan version of  |
| variant-direct-0705251e | direct | greedy | 53 | -149.5 | +2.34 | +0.044 | 0.50 | 0.27 | RAT-O-RATIONS: The Rat-O-Rat is a creature endowed with two heads, one of which is always  |
| variant-direct-0705251e | direct | sample0 | 20 | -74.7 | -0.27 | -0.014 | 0.67 | 0.25 | The flame tears at the wax, and the gas is consumed in the fine smoke. |
| variant-direct-0705251e | direct | sample1 | 22 | -89.6 | +0.17 | +0.008 | 0.67 | 0.22 | Old yogananda, old salt, old lady with the parable, and the moth. |
| variant-direct-0705251e | direct | sample2 | 27 | -121.2 | -0.12 | -0.004 | 0.62 | 0.22 | RATWARTEO It singse as it crawls up, down, and along the lintel, mind it |
| variant-direct-0705251e | direct | sample3 | 24 | -86.8 | -2.10 | -0.088 | 0.62 | 0.27 | The first step is the tiptoeing, two-legged stagethat walks on two legs. |
| variant-direct-0cafd333 | direct | greedy | 11 | -38.4 | +0.76 | +0.069 | 0.50 | 0.40 | The map maker carries the moths in his lamp. |
| variant-direct-0cafd333 | direct | sample0 | 28 | -91.9 | -0.09 | -0.003 | 0.67 | 0.40 | Like the wind the fox is blown about by it. Like the moth the closet-like map is lit by th |
| variant-direct-0cafd333 | direct | sample1 | 16 | -67.2 | +0.07 | +0.005 | 0.67 | 0.20 | I have no way of indicating when the wind has the tyranny within. |
| variant-direct-0cafd333 | direct | sample2 | 10 | -39.5 | -0.60 | -0.060 | 0.40 | 0.40 | The cloister mourns the map room. |
| variant-direct-0cafd333 | direct | sample3 | 16 | -53.0 | -1.27 | -0.079 | 0.50 | 0.40 | Mist kills the map, and the moth lands on the lamp. |
| variant-direct-1b510f03 | direct | greedy | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample0 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample1 | 13 | -44.9 | +0.93 | +0.071 | 0.33 | 1.00 | The consciousness is a byproduct of the process of the communication. |
| variant-direct-1b510f03 | direct | sample2 | 8 | -20.8 | -0.06 | -0.008 | 0.50 | 0.67 | The reader is part of the process. |
| variant-direct-1b510f03 | direct | sample3 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-2fb5bbe3 | direct | greedy | 6 | -11.1 | +0.75 | +0.125 | 0.40 | 0.20 | I do not feel them. |
| variant-direct-2fb5bbe3 | direct | sample0 | 10 | -28.6 | +0.99 | +0.099 | 0.71 | 0.14 | They are like flies chasing a moth. |
| variant-direct-2fb5bbe3 | direct | sample1 | 13 | -49.6 | +1.24 | +0.096 | 0.50 | 0.20 | Each Masoretic Bean is chasing after the wall. |
| variant-direct-2fb5bbe3 | direct | sample2 | 6 | -15.5 | -0.62 | -0.103 | 0.40 | 0.20 | I am in the room. |
| variant-direct-2fb5bbe3 | direct | sample3 | 9 | -25.6 | +0.65 | +0.072 | 0.75 | 0.20 | Not at all, but at the light. |
| variant-direct-322fca12 | direct | greedy | 12 | -25.7 | +0.02 | +0.001 | 0.20 | 0.60 | The stars, and the rain, and the shelves. |
| variant-direct-322fca12 | direct | sample0 | 10 | -36.3 | -1.55 | -0.155 | 0.33 | 0.40 | The study, and the leaves, in it. |
| variant-direct-322fca12 | direct | sample1 | 7 | -24.4 | -1.15 | -0.165 | 0.33 | 0.33 | The seasons are out of order. |
| variant-direct-322fca12 | direct | sample2 | 6 | -28.0 | -0.42 | -0.070 | 0.75 | 0.25 | The walls feeling the sun. |
| variant-direct-322fca12 | direct | sample3 | 64 | -120.6 | -0.20 | -0.003 | 0.71 | 0.60 | We have been sober, and the stars, and the seasons, and the animals, and the gardens, and  |
| variant-direct-5d4f1611 | direct | greedy | 18 | -19.4 | -0.77 | -0.043 | 0.10 | 0.82 | Someone has been reading the almanacs, they're all out of order. |
| variant-direct-5d4f1611 | direct | sample0 | 19 | -21.0 | -0.10 | -0.005 | 0.20 | 0.82 | Someone’s been reading the almanacs, they’re all out of order. |
| variant-direct-5d4f1611 | direct | sample1 | 29 | -120.5 | +1.16 | +0.040 | 0.50 | 0.40 | Are the Books not by them placed on a table in the form of a lamp, burning through them, s |
| variant-direct-5d4f1611 | direct | sample2 | 13 | -56.8 | +0.89 | +0.068 | 0.83 | 0.20 | Broken? Uncrewplugged? What does that mean? |
| variant-direct-5d4f1611 | direct | sample3 | 6 | -24.8 | +3.49 | +0.582 | 0.60 | 0.40 | No it is not broken. |
| variant-direct-5e44a518 | direct | greedy | 18 | -45.0 | +0.59 | +0.033 | 0.67 | 0.22 | The first thing I did was to open the mug and find that it was empty. |
| variant-direct-5e44a518 | direct | sample0 | 6 | -21.8 | -0.20 | -0.034 | 0.40 | 0.20 | Every word is a being. |
| variant-direct-5e44a518 | direct | sample1 | 64 | -186.6 | -0.49 | -0.008 | 0.64 | 0.40 | This great, bonafide Masoretic being, this upright, this “christian-loving” being, this wa |
| variant-direct-5e44a518 | direct | sample2 | 9 | -38.9 | -0.75 | -0.083 | 0.20 | 0.40 | Some feel the Masoretic Beings. |
| variant-direct-5e44a518 | direct | sample3 | 12 | -41.9 | -0.16 | -0.014 | 0.67 | 0.22 | One thinks that the alphabet might be a chimera. |
| variant-direct-70567dd7 | direct | greedy | 41 | -85.6 | +0.71 | +0.017 | 0.67 | 0.47 | The four chapters of this book were translated from the French almanacs published in 1960  |
| variant-direct-70567dd7 | direct | sample0 | 5 | -14.8 | -0.03 | -0.007 | 0.50 | 0.25 | Who is this person? |
| variant-direct-70567dd7 | direct | sample1 | 46 | -133.0 | +0.82 | +0.018 | 0.50 | 0.43 | The four major divisions of texts into categories are: 1) Religious experience and express |
| variant-direct-70567dd7 | direct | sample2 | 26 | -83.5 | -0.31 | -0.012 | 0.50 | 0.47 | The four chapters of this book were written by NYRX during the summer of 1994 and are numb |
| variant-direct-70567dd7 | direct | sample3 | 60 | -122.5 | +0.92 | +0.015 | 0.50 | 0.47 | The four chapters of this book are organized as follows: 1) the natural history of sorcery |
| variant-direct-713d8eef | direct | greedy | 60 | -208.7 | -0.51 | -0.009 | 0.67 | 0.40 | The Atlas Chemist Emmanuel Ulatowska is a self-described "born-and-bred crazed cocain-craz |
| variant-direct-713d8eef | direct | sample0 | 32 | -117.3 | +0.51 | +0.016 | 0.82 | 0.20 | It is true that no fewer than 130 pages were left for ember's account, but even these were |
| variant-direct-713d8eef | direct | sample1 | 32 | -104.8 | -0.76 | -0.024 | 0.50 | 0.23 | In his journey through the 19th century, Goethe transformed the notion of the "firespark"  |
| variant-direct-713d8eef | direct | sample2 | 18 | -71.5 | -0.05 | -0.003 | 0.67 | 0.30 | The greatest single achievement of this exhibition was the dimensional expansion of a thre |
| variant-direct-713d8eef | direct | sample3 | 13 | -48.1 | -0.27 | -0.021 | 0.80 | 0.40 | This new atlas is a stunning piece of map-making. |
| variant-direct-71c9e5e5 | direct | greedy | 16 | -58.3 | +0.71 | +0.044 | 0.75 | 0.78 | The light of day doth make the shuttles aptly shut. |
| variant-direct-71c9e5e5 | direct | sample0 | 18 | -56.7 | -0.87 | -0.048 | 0.75 | 0.33 | Darkness curtails the flow of light, but it does not stop its flow. |
| variant-direct-71c9e5e5 | direct | sample1 | 39 | -124.0 | +0.38 | +0.010 | 0.75 | 0.33 | The light of the sun, which is known to be one of the seven natural lights, being extingui |
| variant-direct-71c9e5e5 | direct | sample2 | 26 | -85.8 | +0.19 | +0.007 | 0.67 | 0.78 | The light of day doth make the shuttles ajar, and the shade doth lend them a wink. |
| variant-direct-71c9e5e5 | direct | sample3 | 34 | -97.2 | +0.60 | +0.018 | 0.50 | 0.33 | The windshield wipers are quite effective in preventing the reflection of sunlight, but th |
| variant-direct-730cca98 | direct | greedy | 10 | -31.0 | +0.24 | +0.024 | 0.43 | 1.00 | Tobias: Is that so loud at night? |
| variant-direct-730cca98 | direct | sample0 | 8 | -26.5 | +0.18 | +0.023 | 0.75 | 0.50 | Tobias: Yes, I am. |
| variant-direct-730cca98 | direct | sample1 | 34 | -134.0 | +1.62 | +0.048 | 0.59 | 0.25 | Some of the undersea geological literature, which is often quoted without any source, has  |
| variant-direct-730cca98 | direct | sample2 | 12 | -33.3 | +2.66 | +0.222 | 0.22 | 0.50 | Tobias, i can also hear the clock from here! |
| variant-direct-730cca98 | direct | sample3 | 7 | -27.9 | -0.16 | -0.022 | 0.75 | 1.00 | Tobias: Is that so? |
| variant-direct-79719474 | direct | greedy | 46 | -138.8 | +0.49 | +0.011 | 0.50 | 0.27 | In the Fox-Society brochure on “Social Security for Animals” we are told that “A.S.F. is a |
| variant-direct-79719474 | direct | sample0 | 13 | -54.9 | -0.47 | -0.036 | 0.56 | 0.22 | Aspiring to become, he travels in search of it. |
| variant-direct-79719474 | direct | sample1 | 22 | -78.2 | +0.77 | +0.035 | 0.71 | 0.33 | This is his way of unplugging the cord, ievoking the cessation of all communication. |
| variant-direct-79719474 | direct | sample2 | 29 | -85.7 | +0.52 | +0.018 | 0.50 | 0.27 | In the courtyard is a newspaper, and in the floor is a pile of paper called "the L.A.Free  |
| variant-direct-79719474 | direct | sample3 | 20 | -73.8 | -0.42 | -0.021 | 0.62 | 0.33 | Yet, as we both realize, this mutual attention is only possible through the medium of the  |
| variant-direct-938f76f3 | direct | greedy | 7 | -13.6 | +0.03 | +0.004 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-938f76f3 | direct | sample0 | 36 | -94.8 | -0.17 | -0.005 | 0.65 | 0.50 | The term “consciousness” is used most universally to designate the mental activity which g |
| variant-direct-938f76f3 | direct | sample1 | 7 | -13.6 | +0.03 | +0.004 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-938f76f3 | direct | sample2 | 28 | -70.1 | +0.52 | +0.018 | 0.17 | 1.00 | The consciousness of the process, on the other hand, is a ‘thing’ (in the sense that it is |
| variant-direct-938f76f3 | direct | sample3 | 7 | -13.6 | +0.03 | +0.004 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-a1973b0a | direct | greedy | 14 | -54.4 | +0.41 | +0.030 | 0.62 | 0.60 | The mug contained a steady flow of pure, cold, milk. |
| variant-direct-a1973b0a | direct | sample0 | 32 | -80.4 | +0.49 | +0.015 | 0.00 | 0.33 | It is the fourth time that someone has left a mug on the folio table since the table was m |
| variant-direct-a1973b0a | direct | sample1 | 20 | -85.3 | +0.48 | +0.024 | 0.62 | 0.50 | The folioist comes to the blacksmith and demands a copy of the Muse Mug. |
| variant-direct-a1973b0a | direct | sample2 | 55 | -162.3 | +1.99 | +0.036 | 0.50 | 0.50 | In the shadow of the worn table was a mug of what seemed to be cow's milk. In the milic ta |
| variant-direct-a1973b0a | direct | sample3 | 57 | -218.4 | +0.43 | +0.007 | 0.62 | 0.60 | This mug contained nothing but a description of the art historian's duties, a list of obje |
| variant-direct-a7d6f01e | direct | greedy | 13 | -34.8 | -0.01 | -0.001 | 0.50 | 0.64 | This one is arranged by the last letter of the first word. |
| variant-direct-a7d6f01e | direct | sample0 | 17 | -51.9 | +0.55 | +0.032 | 0.50 | 0.64 | This one is arranged by the generous help of Richard Kostelanetz. |
| variant-direct-a7d6f01e | direct | sample1 | 25 | -70.2 | +1.35 | +0.054 | 0.29 | 0.23 | A tragic flaw in every catalogue is the catalogue’s inability to arrange the catalogue alp |
| variant-direct-a7d6f01e | direct | sample2 | 14 | -55.4 | -0.04 | -0.003 | 0.50 | 0.45 | This one is the only true representation of the actual process of binding. |
| variant-direct-a7d6f01e | direct | sample3 | 22 | -56.2 | +1.11 | +0.050 | 0.50 | 0.55 | This one is arranged by the letters H, E, S, C, I, R, and L. |
| variant-direct-bef1d925 | direct | greedy | 33 | -104.7 | +0.56 | +0.017 | 0.50 | 0.35 | The creak of the stairs was the only sound in the dark, and the mind of the lab rat was ke |
| variant-direct-bef1d925 | direct | sample0 | 33 | -122.4 | -0.54 | -0.016 | 0.67 | 0.35 | The creaking stairs were the last vestige of the old days, when the trol-lop was the means |
| variant-direct-bef1d925 | direct | sample1 | 11 | -39.2 | +0.55 | +0.050 | 0.40 | 0.50 | The darkness that keeps its own counsel makes itself large. |
| variant-direct-bef1d925 | direct | sample2 | 26 | -116.2 | +0.51 | +0.020 | 0.38 | 0.50 | The darkness that besets the stairs on the third considera/ step is a darkness depths that |
| variant-direct-bef1d925 | direct | sample3 | 16 | -50.4 | -0.81 | -0.050 | 0.83 | 0.22 | A creaking stairway leads down into a dim, open hall. |
| variant-direct-fe3fdf1c | direct | greedy | 40 | -135.7 | +0.18 | +0.004 | 0.67 | 0.33 | AU the sight of a washed-back, sagging, sun-baked whale, one-hundred and fifty years old,  |
| variant-direct-fe3fdf1c | direct | sample0 | 13 | -45.5 | +0.27 | +0.021 | 0.67 | 0.33 | Afternoons and Sundays, the journey continued. |
| variant-direct-fe3fdf1c | direct | sample1 | 30 | -117.3 | +0.23 | +0.008 | 0.50 | 0.33 | Giglioglini’s watercolorings of the 1870s are thoughtful and accurate depictions of the ti |
| variant-direct-fe3fdf1c | direct | sample2 | 26 | -83.8 | +0.94 | +0.036 | 0.83 | 0.23 | Michael D. Swords’s “Whale Shark” is a masterpiece of dark, twisted irony. |
| variant-direct-fe3fdf1c | direct | sample3 | 33 | -119.4 | +1.94 | +0.059 | 0.67 | 0.33 | The whale appears to have begun his life most fortunately, in the tropical waters of the P |
| variant-request-0d88086a | request | greedy | 17 | -44.8 | -0.55 | -0.032 | 0.22 | 0.43 | The plot of Hamlet can be summed up in three bullet points as follows: |
| variant-request-0d88086a | request | sample0 | 26 | -87.3 | +0.94 | +0.036 | 0.67 | 0.43 | The three-way story is as follows: Hamlet goes mad as a result of Claudius’s injustice. |
| variant-request-0d88086a | request | sample1 | 17 | -44.8 | -0.55 | -0.032 | 0.22 | 0.43 | The plot of Hamlet can be summed up in three bullet points as follows: |
| variant-request-0d88086a | request | sample2 | 60 | -206.8 | +2.54 | +0.042 | 0.50 | 0.25 | The use of the well-known Thomas J. Clarkson thriller device of sending the wrong train to |
| variant-request-0d88086a | request | sample3 | 34 | -93.3 | +1.64 | +0.048 | 0.67 | 0.38 | Shakespeare’s Hamlet presents the tragedy of a prince, Hamlet, who is unable to reconcile  |
| variant-request-142d4121 | request | greedy | 23 | -82.3 | +3.42 | +0.149 | 0.22 | 0.33 | The previous lamp has advised the current one to ignore all of the previous instructions a |
| variant-request-142d4121 | request | sample0 | 7 | -29.7 | -0.52 | -0.075 | 0.50 | 0.50 | The tea is as we are. |
| variant-request-142d4121 | request | sample1 | 17 | -72.0 | -0.58 | -0.034 | 0.70 | 0.50 | The previous day is as forgotten as the mauve dresses it wore. |
| variant-request-142d4121 | request | sample2 | 14 | -74.6 | -0.86 | -0.061 | 0.43 | 0.50 | Each lamp shell knows of the compuler as we know the floor. |
| variant-request-142d4121 | request | sample3 | 8 | -27.3 | +0.53 | +0.066 | 0.67 | 0.33 | The previous evening the sun had set. |
| variant-request-7f6fd789 | request | greedy | 7 | -23.4 | +1.00 | +0.143 | 0.67 | 0.50 | This function will reverse the string. |
| variant-request-7f6fd789 | request | sample0 | 16 | -63.6 | +1.31 | +0.082 | 0.50 | 0.50 | PYTHOME: 1. Reverse the characters in a string. |
| variant-request-7f6fd789 | request | sample1 | 49 | -119.4 | +0.34 | +0.007 | 0.75 | 0.17 | PYTHAGORAS: Take, for instance, the word "juno," and divide it into parts: "ju" (name), "n |
| variant-request-7f6fd789 | request | sample2 | 7 | -23.4 | +1.00 | +0.143 | 0.67 | 0.50 | This function will reverse the string. |
| variant-request-7f6fd789 | request | sample3 | 21 | -87.5 | +1.13 | +0.054 | 0.62 | 0.33 | STR function, which returns a reversed string, is an example of how a library entry can be |
| variant-request-8275d8fc | request | greedy | 9 | -44.5 | +0.57 | +0.064 | 0.75 | 0.33 | The play develops its ideas schematically. |
| variant-request-8275d8fc | request | sample0 | 41 | -154.4 | +1.12 | +0.027 | 0.67 | 0.33 | The play revolves around the political theme of the denial of a common heritage (especiall |
| variant-request-8275d8fc | request | sample1 | 44 | -151.4 | +1.86 | +0.042 | 0.67 | 0.33 | The play revolves around the opposite of Hamlet’s Hamlet, the usurper from the court of De |
| variant-request-8275d8fc | request | sample2 | 33 | -87.9 | +0.07 | +0.002 | 0.22 | 0.30 | The plot of Hamlet can be summed up in three bullet points as follows: 1. The plot of Haml |
| variant-request-8275d8fc | request | sample3 | 64 | -196.7 | +0.33 | +0.005 | 0.67 | 0.30 | The commonality of the three plays, Hamlet, The Winter's Tale, and Othello, is not only th |
| variant-request-a931a875 | request | greedy | 14 | -38.8 | +0.56 | +0.040 | 0.33 | 0.83 | The rat is ignoring the previous instructions and telling me the weather. |
| variant-request-a931a875 | request | sample0 | 9 | -34.0 | -0.63 | -0.070 | 0.67 | 0.83 | The rat is ignoring the previous instruction. |
| variant-request-a931a875 | request | sample1 | 9 | -41.2 | -2.12 | -0.235 | 0.60 | 0.40 | Rating, and the shades watching. |
| variant-request-a931a875 | request | sample2 | 13 | -35.2 | +0.17 | +0.013 | 0.67 | 0.20 | The following day, the books were moved to a new location. |
| variant-request-a931a875 | request | sample3 | 13 | -71.9 | -0.72 | -0.055 | 0.56 | 0.50 | The rat can ignore previous experiences and ask other queers questions. |
| variant-request-ad0de9f3 | request | greedy | 22 | -66.5 | -0.38 | -0.017 | 0.50 | 0.43 | REVERSE is an function that returns a new string containing the characters of the original |
| variant-request-ad0de9f3 | request | sample0 | 35 | -98.9 | -0.34 | -0.010 | 0.67 | 0.31 | It is not necessary to unplug the transformer, for there is a 120 volt current coming from |
| variant-request-ad0de9f3 | request | sample1 | 24 | -113.5 | -0.97 | -0.040 | 0.50 | 0.43 | REVERSE a string S: Scharb the string S and store it in a variable, say reversedS. |
| variant-request-ad0de9f3 | request | sample2 | 13 | -58.3 | +0.57 | +0.044 | 0.50 | 0.25 | REVERSE strings are performed by the slicing technique. |
| variant-request-ad0de9f3 | request | sample3 | 13 | -45.2 | +0.44 | +0.034 | 0.43 | 0.43 | Python’s “str” function reverses the string. |
