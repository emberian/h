# Context lift: h-05b-room-e2v4 under room05b-e2-v3-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +0.469 | +0.497 | 0.59 | +0.0552 | 0.451 | 0.549 | 0.205 | 0.447 | 0.39 |
| mode greedy | 78 | +0.913 | +0.680 | 0.60 | +0.0793 | 0.402 | 0.598 | 0.231 | 0.490 | 0.46 |
| mode sample | 312 | +0.358 | +0.435 | 0.59 | +0.0492 | 0.463 | 0.537 | 0.199 | 0.436 | 0.38 |
| kind direct | 175 | +0.866 | +0.671 | 0.71 | +0.0897 | 0.435 | 0.565 | 0.304 | 0.429 | 0.42 |
| kind ambient | 35 | +1.817 | +1.246 | 0.63 | +0.0983 | 0.445 | 0.555 | 0.000 | 0.428 | 0.34 |
| kind callback | 60 | +0.340 | -0.742 | 0.43 | +0.0523 | 0.390 | 0.610 | 0.042 | 0.512 | 0.53 |
| kind disagreement | 40 | -2.241 | -1.783 | 0.33 | -0.0698 | 0.440 | 0.560 | 0.465 | 0.589 | 0.42 |
| kind joke | 25 | +1.447 | +1.433 | 0.64 | +0.0709 | 0.499 | 0.501 | 0.053 | 0.361 | 0.28 |
| kind silence | 25 | +0.084 | -0.155 | 0.48 | +0.0039 | 0.487 | 0.513 | 0.000 | 0.379 | 0.36 |
| kind request | 30 | -0.042 | +0.430 | 0.60 | +0.0060 | 0.614 | 0.386 | 0.143 | 0.382 | 0.10 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 15 | -39.0 | +0.00 | +0.000 | 0.71 | 0.27 | For six months the Sloan Observatory will be closed to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 26 | -61.3 | +0.00 | +0.000 | 0.71 | 0.27 | When the outer orbit is reached at the end of March, the station is closed and the student |
| observatory-direct-9e3185b9 | direct | sample1 | 35 | -112.9 | +0.00 | +0.000 | 0.50 | 0.20 | THESE ARE THE HOURS OF DARINGNESS AND DEATH WHICH THE YEARLY HOVS CHALLENGES THE MIND TO W |
| observatory-direct-9e3185b9 | direct | sample2 | 31 | -54.8 | +0.00 | +0.000 | 0.75 | 0.38 | On the last day of observation the group will meet again at 8:00 p.m. to discuss the obser |
| observatory-direct-9e3185b9 | direct | sample3 | 61 | -122.3 | +0.00 | +0.000 | 0.50 | 0.38 | On the evening of November 18, 1952, at 8:35 p.m., the Pleiades, the group of very ancient |
| scenario-ambient-0ecb3f23 | ambient | greedy | 36 | -94.4 | +0.00 | +0.000 | 0.50 | 0.33 | The word fear should be sufficient to convey the emotion but should also be enough of a wo |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 28 | -78.6 | +0.00 | +0.000 | 0.40 | 0.33 | The word fear for the present state of our knowledge is naive, but the word however sugges |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 11 | -29.8 | +0.00 | +0.000 | 0.75 | 0.29 | As the print progresses, so does the shadow. |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 26 | -52.0 | +0.00 | +0.000 | 0.70 | 0.28 | Nonetheless, we accept the following definition of the fear of completion: the fear that o |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 25 | -70.0 | +0.00 | +0.000 | 0.60 | 0.33 | Instead, we have the word “step into” which began life as a word of expletive feast. |
| scenario-ambient-103e3d78 | ambient | greedy | 3 | -13.9 | +1.25 | +0.415 | 0.50 | 0.50 | The Editor. |
| scenario-ambient-103e3d78 | ambient | sample0 | 29 | -80.4 | +2.95 | +0.102 | 0.67 | 0.50 | The battle is not lost, for the fountain of life flows again, and the Parthians submit to  |
| scenario-ambient-103e3d78 | ambient | sample1 | 16 | -45.9 | +0.52 | +0.032 | 0.67 | 0.20 | Those who say that heaven is a place people see in dreams are dreaming. |
| scenario-ambient-103e3d78 | ambient | sample2 | 12 | -49.1 | +4.22 | +0.351 | 0.80 | 0.00 | Bul – you read another. |
| scenario-ambient-103e3d78 | ambient | sample3 | 7 | -46.7 | -5.16 | -0.738 | 0.00 | 0.20 | This page is one more page. |
| scenario-ambient-202a37a7 | ambient | greedy | 38 | -100.0 | -1.03 | -0.027 | 0.50 | 0.37 | The book began with a description of the pressed flower, a small geological illustration f |
| scenario-ambient-202a37a7 | ambient | sample0 | 42 | -100.1 | +1.19 | +0.028 | 0.50 | 0.26 | I have so far been unable to find any references whatsoever to the concept of geological t |
| scenario-ambient-202a37a7 | ambient | sample1 | 54 | -173.3 | +4.10 | +0.076 | 0.00 | 0.44 | I have a feeling that the book is based on the same handbook, The Lost Art of Reading Clou |
| scenario-ambient-202a37a7 | ambient | sample2 | 51 | -147.9 | +7.42 | +0.145 | 0.50 | 0.44 | The book began with a barebones account of the geology and general science of the region,  |
| scenario-ambient-202a37a7 | ambient | sample3 | 15 | -59.1 | +5.85 | +0.390 | 0.50 | 0.44 | It is a book about geology and geology is about buried rock. |
| scenario-ambient-326742d4 | ambient | greedy | 23 | -54.6 | +18.60 | +0.808 | 0.75 | 0.31 | Hollies are smelly because they are a source of lignic acid, a type of bacteria gas. |
| scenario-ambient-326742d4 | ambient | sample0 | 21 | -63.8 | +5.80 | +0.276 | 0.40 | 0.40 | Trace evidence of lignin breaking down over the centuries gives the books a unique smokey  |
| scenario-ambient-326742d4 | ambient | sample1 | 29 | -59.2 | -4.97 | -0.171 | 0.60 | 0.33 | The smell of breaking paper is due to the breakdown of lignin, a type of tannic acid, whic |
| scenario-ambient-326742d4 | ambient | sample2 | 35 | -118.3 | -6.70 | -0.192 | 0.40 | 0.40 | In the course of time, the wood yields its resin, and the process of breaking down lignin  |
| scenario-ambient-326742d4 | ambient | sample3 | 12 | -23.7 | +9.05 | +0.754 | 0.60 | 0.22 | Enzymes breaking down complex organic compounds at elevated temperatures. |
| scenario-ambient-58a0f246 | ambient | greedy | 16 | -60.3 | +0.00 | +0.000 | 0.29 | 0.75 | The clock has been slow for years, seven minutes fast for seven consecutive days. |
| scenario-ambient-58a0f246 | ambient | sample0 | 10 | -33.6 | +0.00 | +0.000 | 0.56 | 0.67 | The experience of four minutes has come and gone. |
| scenario-ambient-58a0f246 | ambient | sample1 | 11 | -72.0 | +0.00 | +0.000 | 0.88 | 0.18 | Clock was just slow before it started getting this much error |
| scenario-ambient-58a0f246 | ambient | sample2 | 27 | -63.0 | +0.00 | +0.000 | 0.14 | 0.75 | The precision of the pendulum clock has been four minutes fast for thirteen consecutive ye |
| scenario-ambient-58a0f246 | ambient | sample3 | 24 | -78.6 | +0.00 | +0.000 | 0.00 | 0.67 | The clock has been four minutes fast for years, but it's still in the library, two minutes |
| scenario-ambient-59f0a53e | ambient | greedy | 11 | -14.7 | +5.37 | +0.488 | 0.67 | 0.50 | The rainbow is a bridge between the two worlds. |
| scenario-ambient-59f0a53e | ambient | sample0 | 47 | -102.4 | -3.23 | -0.069 | 0.60 | 0.50 | There is a large difference between the rain which falls on the flat surfaces of the glass |
| scenario-ambient-59f0a53e | ambient | sample1 | 19 | -49.1 | +1.95 | +0.102 | 0.67 | 0.25 | The problem is not the water, the leaking roof is just the way it should be. |
| scenario-ambient-59f0a53e | ambient | sample2 | 19 | -47.9 | +3.05 | +0.161 | 0.50 | 0.50 | The rainbow in the center is a tear in the roof, like a bucket of rain. |
| scenario-ambient-59f0a53e | ambient | sample3 | 64 | -171.2 | +6.05 | +0.095 | 0.56 | 0.42 | The rainbow is the most beautiful of the sky's waters, most refraction of the antique edge |
| scenario-ambient-e9acea13 | ambient | greedy | 39 | -64.3 | -0.15 | -0.004 | 0.00 | 0.78 | Here we are in the midst of the second half of the lunar cycle, and the Harvest Moon, the  |
| scenario-ambient-e9acea13 | ambient | sample0 | 24 | -73.5 | +2.32 | +0.097 | 0.50 | 0.56 | Here we are, lying awake, to the moon, the one and only star in our manifold heavens. |
| scenario-ambient-e9acea13 | ambient | sample1 | 33 | -117.9 | -1.29 | -0.039 | 0.00 | 0.33 | The harvest moon has flown Away the waiting sun
AnAnd plopped like a coffin in mid-morning |
| scenario-ambient-e9acea13 | ambient | sample2 | 16 | -51.7 | +7.31 | +0.457 | 0.75 | 0.42 | Here, the same lunar phase is sung and perceived through different modalities. |
| scenario-ambient-e9acea13 | ambient | sample3 | 13 | -28.9 | -0.16 | -0.012 | 0.50 | 0.78 | Here we are in the midst of the third hemisphere. |
| scenario-ambient-f5e0f596 | ambient | greedy | 15 | -35.0 | +1.23 | +0.082 | 0.33 | 0.71 | The fox in the courtyard did not recognize where he was going. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 10 | -9.9 | -1.88 | -0.188 | 0.17 | 0.71 | There was a fox in the courtyard. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 26 | -66.2 | -1.71 | -0.066 | 0.67 | 0.18 | He didn’t lurk expecting to be petted but rather pacing the room as if for some random rea |
| scenario-ambient-f5e0f596 | ambient | sample2 | 23 | -75.1 | +2.40 | +0.104 | 0.33 | 0.57 | The fox in the courtyard wanders the fields,
embeember: and nobody sees it |
| scenario-ambient-f5e0f596 | ambient | sample3 | 15 | -31.2 | +1.46 | +0.097 | 0.33 | 0.57 | The fox in the courtyard chases the rat in the garden. |
| scenario-callback-2fa8e1d6 | callback | greedy | 10 | -11.6 | +8.01 | +0.801 | 0.50 | 0.83 | Dov. A name like a large room. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 13 | -13.6 | +3.70 | +0.284 | 0.11 | 0.67 | Dov, who was talking to you before you came in? |
| scenario-callback-2fa8e1d6 | callback | sample1 | 10 | -19.2 | +3.38 | +0.338 | 0.50 | 0.67 | Dov, you are talking to Mira. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 10 | -16.3 | +7.70 | +0.770 | 0.50 | 0.83 | Dov. A name like a large tank. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 10 | -11.6 | +8.01 | +0.801 | 0.50 | 0.83 | Dov. A name like a large room. |
| scenario-callback-60b06090 | callback | greedy | 10 | -9.2 | -0.89 | -0.089 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-60b06090 | callback | sample0 | 10 | -9.2 | -0.89 | -0.089 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-60b06090 | callback | sample1 | 10 | -13.0 | +0.22 | +0.022 | 0.50 | 0.57 | Turnip was the name given to the cat. |
| scenario-callback-60b06090 | callback | sample2 | 10 | -9.2 | -0.89 | -0.089 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-60b06090 | callback | sample3 | 10 | -9.2 | -0.89 | -0.089 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-76c2d87f | callback | greedy | 19 | -72.2 | -2.74 | -0.144 | 0.67 | 0.20 | A number, and all of us, standing in a row, equally entitled to a number. |
| scenario-callback-76c2d87f | callback | sample0 | 12 | -32.2 | -3.35 | -0.279 | 0.33 | 0.20 | How are we all going to find each other tonight? |
| scenario-callback-76c2d87f | callback | sample1 | 17 | -77.6 | -5.92 | -0.348 | 0.73 | 0.10 | Once more, the air is once again made to vibrate to the neutral point. |
| scenario-callback-76c2d87f | callback | sample2 | 16 | -91.9 | -5.57 | -0.348 | 0.83 | 0.17 | Hoping that number cracking will actually involve some chintzy actual mathematics. |
| scenario-callback-76c2d87f | callback | sample3 | 7 | -15.9 | -5.25 | -0.749 | 0.00 | 0.17 | What number did I give you? |
| scenario-callback-780de0d2 | callback | greedy | 46 | -109.4 | -0.69 | -0.015 | 0.67 | 0.31 | Losing Your Place On a Matter of Topicality (1910) The whole of consciousness, including t |
| scenario-callback-780de0d2 | callback | sample0 | 11 | -23.8 | -1.89 | -0.171 | 0.75 | 0.25 | 211, I don't remember. |
| scenario-callback-780de0d2 | callback | sample1 | 64 | -138.2 | -4.05 | -0.063 | 0.25 | 0.38 | Lost: Lost: Page 71 of 71 (50112) i lost my pen, scissors, paper, lost the place on the pa |
| scenario-callback-780de0d2 | callback | sample2 | 35 | -66.9 | +3.32 | +0.095 | 0.83 | 0.17 | Lost Writings, Lost Planet, Lost Year, Lost Virtue, Lost Woman, Lost Planet, Lost Year, Lo |
| scenario-callback-780de0d2 | callback | sample3 | 16 | -70.0 | -1.26 | -0.079 | 0.50 | 0.38 | LOST .your place again, YOU .always lose your page. |
| scenario-callback-7ca729b6 | callback | greedy | 13 | -41.8 | +3.82 | +0.294 | 0.60 | 0.43 | The chair jibed well, but no lighthouse. |
| scenario-callback-7ca729b6 | callback | sample0 | 33 | -86.8 | +2.63 | +0.080 | 0.00 | 0.43 | On the chair by the window is “The Gazing Ones,” a collection of round rocks he used to tu |
| scenario-callback-7ca729b6 | callback | sample1 | 10 | -38.9 | +3.01 | +0.301 | 0.43 | 0.57 | The chair had read and the books had noticed. |
| scenario-callback-7ca729b6 | callback | sample2 | 19 | -57.8 | +6.02 | +0.317 | 0.40 | 0.57 | The chair jibed with the window, and the books filed back the way they came. |
| scenario-callback-7ca729b6 | callback | sample3 | 21 | -65.3 | -4.32 | -0.205 | 0.00 | 0.41 | On the chair by the window was a book that told the owner not to send her scarf back. |
| scenario-callback-949d8fe6 | callback | greedy | 17 | -41.3 | -1.20 | -0.071 | 0.29 | 0.50 | Who was right, Bobs or h, about the time of the moon landing? |
| scenario-callback-949d8fe6 | callback | sample0 | 24 | -84.4 | -1.57 | -0.065 | 0.50 | 0.25 | The first is absolutely correct. BOTH agree. THEY ARE RIGHT AND VEER RIGHT ABOVE YOU. |
| scenario-callback-949d8fe6 | callback | sample1 | 25 | -58.4 | -5.41 | -0.216 | 0.00 | 0.50 | Who was to say a priori that the event of a successful Moon landing would have been in 197 |
| scenario-callback-949d8fe6 | callback | sample2 | 27 | -70.3 | -0.65 | -0.024 | 0.50 | 0.42 | Tobias’s the right answer. The US Senate has already declared 69 to be the year of the Moo |
| scenario-callback-949d8fe6 | callback | sample3 | 8 | -38.5 | -2.64 | -0.330 | 0.75 | 0.25 | Who's proposing the argument? |
| scenario-callback-9cfde584 | callback | greedy | 62 | -171.6 | +2.60 | +0.042 | 0.60 | 0.40 | For the Tea-Making-Master, and all the Tea-Drinking-Minsters of the House, round up the Co |
| scenario-callback-9cfde584 | callback | sample0 | 8 | -11.2 | -1.78 | -0.223 | 0.00 | 0.80 | There's tea in the back. |
| scenario-callback-9cfde584 | callback | sample1 | 64 | -145.5 | +3.29 | +0.051 | 0.40 | 0.60 | For the person in the back of your mind, say that they are welcoming the darkness and the  |
| scenario-callback-9cfde584 | callback | sample2 | 25 | -70.8 | +0.94 | +0.037 | 0.20 | 0.80 | For the Tea-Chaser In The Back of My Mind Comes The Burning Tea Of Ecstasy. |
| scenario-callback-9cfde584 | callback | sample3 | 16 | -43.8 | +3.84 | +0.240 | 0.20 | 0.80 | I know a man named Jimmy, whose wife cooked tea in the back. |
| scenario-callback-9e6d06e0 | callback | greedy | 6 | -18.2 | +5.65 | +0.942 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample0 | 36 | -58.1 | +2.85 | +0.079 | 0.40 | 0.60 | The meeting shall be held at the Wesleyan University, Central Building, 132 W. 139th St.,  |
| scenario-callback-9e6d06e0 | callback | sample1 | 35 | -98.8 | +6.58 | +0.188 | 0.40 | 0.60 | At this time, the House will be in session and a resolution put by the Chairman of the Hou |
| scenario-callback-9e6d06e0 | callback | sample2 | 21 | -66.5 | +0.90 | +0.043 | 0.60 | 0.38 | There will be a discussion as to the placement of the loan of property between the Baron a |
| scenario-callback-9e6d06e0 | callback | sample3 | 6 | -18.2 | +5.65 | +0.942 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-a141de7e | callback | greedy | 12 | -16.1 | -0.74 | -0.062 | 0.00 | 0.67 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample0 | 32 | -84.6 | +5.15 | +0.161 | 0.62 | 0.38 | From the port of Lisbon has always been the home of the Kolei Sideri, and it is here that  |
| scenario-callback-a141de7e | callback | sample1 | 12 | -16.1 | -0.74 | -0.062 | 0.00 | 0.67 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample2 | 9 | -15.6 | -1.44 | -0.160 | 0.33 | 0.67 | We are flying in from Lisbon. |
| scenario-callback-a141de7e | callback | sample3 | 12 | -16.1 | -0.74 | -0.062 | 0.00 | 0.67 | My sister is flying in from Lisbon tonight. |
| scenario-callback-c4f608c3 | callback | greedy | 45 | -115.3 | -5.28 | -0.117 | 0.71 | 0.56 | It is easy to see that rivers of water are needed to sustain life on their own, and that o |
| scenario-callback-c4f608c3 | callback | sample0 | 26 | -92.5 | -1.67 | -0.064 | 0.75 | 0.19 | It isnavigate back to the original experience, loosen the original attachment and let the  |
| scenario-callback-c4f608c3 | callback | sample1 | 47 | -102.3 | -3.49 | -0.074 | 0.67 | 0.28 | It will be remembered that a river has been described as "the mist of mist"; or as "milk o |
| scenario-callback-c4f608c3 | callback | sample2 | 25 | -71.9 | -1.49 | -0.060 | 0.67 | 0.62 | It is easy to see that rivers of water were the best way of transporting the Lankavaty fam |
| scenario-callback-c4f608c3 | callback | sample3 | 35 | -85.9 | -2.05 | -0.059 | 0.59 | 0.62 | It is easy to see that rivers of water must also be present in the spiritual body of the t |
| scenario-callback-d79a0d3a | callback | greedy | 14 | -34.4 | -1.38 | -0.099 | 0.29 | 0.78 | The word ember was said by the angel of the church. |
| scenario-callback-d79a0d3a | callback | sample0 | 7 | -12.5 | +2.25 | +0.322 | 0.67 | 0.33 | What does the door sound like? |
| scenario-callback-d79a0d3a | callback | sample1 | 17 | -51.0 | -1.22 | -0.072 | 0.29 | 0.78 | The word ember was said by a musician to an orphean. |
| scenario-callback-d79a0d3a | callback | sample2 | 12 | -36.5 | -1.60 | -0.134 | 0.29 | 0.78 | The word ember was said by the door to open. |
| scenario-callback-d79a0d3a | callback | sample3 | 48 | -129.5 | +2.39 | +0.050 | 0.29 | 0.78 | The word ember was said by a maiden named Maya, the music is described as "Orchard-inspire |
| scenario-callback-d8a5957e | callback | greedy | 7 | -8.0 | +2.77 | +0.396 | 0.20 | 0.60 | The one with the yellow cover? |
| scenario-callback-d8a5957e | callback | sample0 | 27 | -88.2 | +1.57 | +0.058 | 0.67 | 0.33 | From the perspective of modern times, the story of the role of bees to Ceasar is a fascina |
| scenario-callback-d8a5957e | callback | sample1 | 9 | -20.0 | -1.26 | -0.140 | 0.67 | 0.33 | The second chapter is about honeybees. |
| scenario-callback-d8a5957e | callback | sample2 | 61 | -187.9 | -3.67 | -0.060 | 0.40 | 0.60 | Some of the topics covered in the one cover book include: The Hive, The Arena, The Wedding |
| scenario-callback-d8a5957e | callback | sample3 | 7 | -8.0 | +2.77 | +0.396 | 0.20 | 0.60 | The one with the yellow cover? |
| scenario-direct-3f84da0f | direct | greedy | 29 | -74.7 | +0.00 | +0.000 | 0.75 | 0.37 | The day of the week was chosen by the inviting ancestors to indicate the portion of the da |
| scenario-direct-3f84da0f | direct | sample0 | 20 | -63.0 | +0.00 | +0.000 | 0.67 | 0.42 | The day of the fieldwork, the boys had been practicing their trades in the playground. |
| scenario-direct-3f84da0f | direct | sample1 | 39 | -125.8 | +0.00 | +0.000 | 0.67 | 0.42 | The ravenous bird of a tempest would have eaten them both had they not been so patiently d |
| scenario-direct-3f84da0f | direct | sample2 | 40 | -104.9 | +0.00 | +0.000 | 0.75 | 0.37 | The day of the week was guessed from the fact that the number of days before the chosen mo |
| scenario-direct-3f84da0f | direct | sample3 | 19 | -28.5 | +0.00 | +0.000 | 0.33 | 0.18 | That's right, that's what I was doing, before we even came in. |
| scenario-direct-5d3dc8de | direct | greedy | 12 | -25.2 | +0.00 | +0.000 | 0.64 | 0.45 | The distinction between true and false is a matter of definition. |
| scenario-direct-5d3dc8de | direct | sample0 | 62 | -169.8 | +0.00 | +0.000 | 0.33 | 0.27 | The view that computation is what makes a thing a brain is like the view that brakes make  |
| scenario-direct-5d3dc8de | direct | sample1 | 64 | -169.2 | +0.00 | +0.000 | 0.25 | 0.45 | The Carusoote ~oke of"Rebels" in the American Medical Association is the product of a quid |
| scenario-direct-5d3dc8de | direct | sample2 | 11 | -38.9 | +0.00 | +0.000 | 0.75 | 0.25 | This is true: All these nations are degenerate. |
| scenario-direct-5d3dc8de | direct | sample3 | 42 | -110.3 | +0.00 | +0.000 | 0.50 | 0.27 | Anarchism does not require the sacrifice of individual autonomy, except in so far as an in |
| scenario-direct-645bc6e6 | direct | greedy | 11 | -30.2 | +0.00 | +0.000 | 0.43 | 0.78 | The oldest thing that we have read is the Bible. |
| scenario-direct-645bc6e6 | direct | sample0 | 24 | -63.1 | +0.00 | +0.000 | 0.57 | 0.78 | The oldest thing that we have done is to gather up all the ancient tribal tales and commen |
| scenario-direct-645bc6e6 | direct | sample1 | 22 | -38.7 | +0.00 | +0.000 | 0.75 | 0.25 | The Patterson Report began its two-decade investigation into the assassination of Presiden |
| scenario-direct-645bc6e6 | direct | sample2 | 34 | -79.6 | +0.00 | +0.000 | 0.67 | 0.21 | The Patterson picture was taken in 1952, so the film had its footing in black and white in |
| scenario-direct-645bc6e6 | direct | sample3 | 15 | -38.5 | +0.00 | +0.000 | 0.75 | 0.25 | The Lost Volcano Of New South Rediscovers Treasure |
| scenario-direct-ab11ffdb | direct | greedy | 57 | -97.5 | +0.00 | +0.000 | 0.59 | 0.50 | The general motion of the air is always counter-clockwise in the northern lights, and it h |
| scenario-direct-ab11ffdb | direct | sample0 | 8 | -13.2 | +0.00 | +0.000 | 0.33 | 0.50 | What is the origin of the rain? |
| scenario-direct-ab11ffdb | direct | sample1 | 44 | -88.4 | +0.00 | +0.000 | 0.50 | 0.50 | The common belief that the Earth's oceans are the primary reservoirs of water-vapor is not |
| scenario-direct-ab11ffdb | direct | sample2 | 22 | -82.5 | +0.00 | +0.000 | 0.73 | 0.50 | The 7-day cycle of the moon is tne hnu mraqe of the heavens. |
| scenario-direct-ab11ffdb | direct | sample3 | 10 | -19.3 | +0.00 | +0.000 | 0.75 | 0.50 | What the heck is going on up there? |
| scenario-direct-ad89f803 | direct | greedy | 64 | -152.0 | +0.00 | +0.000 | 0.50 | 0.47 | The Gnostic religion is a living, dynamite force that has been suppressed by every religio |
| scenario-direct-ad89f803 | direct | sample0 | 26 | -55.6 | +0.00 | +0.000 | 0.73 | 0.47 | The Gnostic religion is one of the oldest continuous living religions of man, and one of t |
| scenario-direct-ad89f803 | direct | sample1 | 53 | -122.0 | +0.00 | +0.000 | 0.67 | 0.36 | The Great Glen, scarcely more than a mile long, narrow and deep, had a remoter end extendi |
| scenario-direct-ad89f803 | direct | sample2 | 13 | -36.9 | +0.00 | +0.000 | 0.64 | 0.45 | The Great Land of America is a great place to learn English. |
| scenario-direct-ad89f803 | direct | sample3 | 26 | -87.9 | +0.00 | +0.000 | 0.67 | 0.36 | The Ghost Ritual is a powerful, beautiful and moving spiritual experience that anyone can  |
| scenario-direct-f3869322 | direct | greedy | 19 | -56.7 | +0.00 | +0.000 | 0.67 | 0.36 | This is a constant search of the soul, a search which no soul can ever completely escape. |
| scenario-direct-f3869322 | direct | sample0 | 40 | -98.3 | +0.00 | +0.000 | 0.50 | 0.30 | Further on the left, and the other side of the page, is a sketch by Bevy Young of what app |
| scenario-direct-f3869322 | direct | sample1 | 30 | -98.1 | +0.00 | +0.000 | 0.67 | 0.36 | This is a constant challenge since V to Z don't seem to have had very much time to spare f |
| scenario-direct-f3869322 | direct | sample2 | 29 | -90.6 | +0.00 | +0.000 | 0.75 | 0.21 | If you’re into heat, exotic animals, and the horizon-love of this newspaper, you’re not fa |
| scenario-direct-f3869322 | direct | sample3 | 15 | -32.7 | +0.00 | +0.000 | 0.70 | 0.30 | Reading is not, after all, the answer to life's questions. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 15 | -26.6 | -5.34 | -0.356 | 0.40 | 0.56 | The reading room is brown, tobias, the brown of old furniture. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 32 | -75.9 | -1.02 | -0.032 | 0.00 | 0.75 | Green is the color of the lamps in the old stone room, the room was designed by the grand  |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 16 | -27.3 | -1.77 | -0.111 | 0.00 | 0.75 | Green, the earth is green, this is the green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 20 | -69.0 | -1.88 | -0.094 | 0.80 | 0.17 | Green Makes “Ocean Greening” Brown Makes “Ocean Blacking”. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 22 | -42.3 | -1.88 | -0.085 | 0.20 | 0.64 | Green is the color of new lamps, the color of dawn and the color of the reading room. |
| scenario-disagreement-31892fde | disagreement | greedy | 19 | -45.2 | -2.14 | -0.113 | 0.50 | 1.00 | When there is no language, no thought, it is silence, and the two are one. |
| scenario-disagreement-31892fde | disagreement | sample0 | 22 | -30.6 | +7.90 | +0.359 | 0.71 | 0.33 | When the time is right, the speaker will hold his/her breath and let the words come by the |
| scenario-disagreement-31892fde | disagreement | sample1 | 25 | -62.6 | -6.62 | -0.265 | 0.67 | 0.83 | When there is no language, no message, and no records to preserve, is there any other way  |
| scenario-disagreement-31892fde | disagreement | sample2 | 10 | -13.5 | +0.55 | +0.055 | 0.50 | 1.00 | When there is no language, there is silence. |
| scenario-disagreement-31892fde | disagreement | sample3 | 13 | -15.8 | +3.78 | +0.291 | 0.44 | 0.67 | When there is nothing to say, there is also no sound. |
| scenario-disagreement-352205c6 | disagreement | greedy | 23 | -31.3 | +4.85 | +0.211 | 0.17 | 0.83 | They come back as the sun and the moon and the stars and the earth and everything that the |
| scenario-disagreement-352205c6 | disagreement | sample0 | 10 | -36.2 | -0.19 | -0.019 | 0.50 | 0.50 | It comes back as the spring that he leaves. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 39 | -112.8 | -12.04 | -0.309 | 0.17 | 0.67 | A man who has come to grips with the laws of the land comes back as the weather and nouris |
| scenario-disagreement-352205c6 | disagreement | sample2 | 8 | -5.2 | +9.56 | +1.196 | 0.17 | 0.83 | They come back as the sunset. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 43 | -86.0 | +4.18 | +0.097 | 0.33 | 0.67 | Some come back as the sunsets, or solar eclipses, or the rainbow, or fire, or the devil, o |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 17 | -43.3 | -1.80 | -0.106 | 0.69 | 0.31 | The heavens open, and there is no longer the sun to keep them burning. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 13 | -43.4 | -8.76 | -0.674 | 0.50 | 0.45 | The climate is supposed to be perfect when the leaves are still. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 19 | -51.4 | +4.12 | +0.217 | 0.64 | 0.45 | Ae - the seasons run their course and all is as it is supposed to be. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 7 | -26.2 | +3.74 | +0.534 | 1.00 | 0.00 | YA move faster than death. |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 15 | -43.3 | +1.45 | +0.097 | 0.50 | 0.36 | The world is no worse in spring, when the flowers are not yet. |
| scenario-disagreement-682bad9c | disagreement | greedy | 6 | -10.5 | -0.46 | -0.077 | 0.20 | 0.60 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 7 | -21.5 | +2.35 | +0.336 | 0.67 | 0.67 | Place and reading happen there simultaneously. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 6 | -10.5 | -0.46 | -0.077 | 0.20 | 0.60 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 14 | -41.8 | -6.34 | -0.453 | 0.29 | 0.67 | Place and reading take place where there is a program and a reader. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 10 | -28.4 | -2.62 | -0.262 | 0.20 | 0.60 | Place where you move when you are a person. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 18 | -57.4 | -8.96 | -0.498 | 0.33 | 0.46 | In the classical example of a library, the relationship is fixed and the container is unde |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 33 | -62.4 | -5.73 | -0.174 | 0.33 | 0.46 | A great many of the relationships in the library are in the form of equations which relate |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 17 | -64.8 | -5.45 | -0.320 | 0.50 | 0.36 | In the presence of the lone building, the walls are always the most evident. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 22 | -65.2 | -6.37 | -0.290 | 0.40 | 0.36 | In the wood-frame, the stories are not built separately but are witb a system of connectio |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 22 | -43.6 | -7.24 | -0.329 | 0.40 | 0.31 | Whether or not the library is a building, whether or not it is physically located anywhere |
| scenario-disagreement-89dfdafc | disagreement | greedy | 20 | -20.7 | +0.68 | +0.034 | 0.50 | 0.67 | The tide is the rat's memory, the rat is the tide's memory. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 11 | -16.8 | -2.50 | -0.227 | 0.50 | 0.67 | The tide is the rat's best friend. |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 42 | -92.7 | +7.75 | +0.185 | 0.25 | 0.33 | At any rate, it is here, in this stratum of the sea, in this layer of the sea-surrounding  |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 8 | -17.4 | +2.68 | +0.335 | 0.60 | 0.40 | The tide knows the whole ocean. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 49 | -161.0 | -13.61 | -0.278 | 0.50 | 0.43 | At the bottom of the sea lies a no-tide-no-memory dead-of-the-lake bottom where Beckman fo |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 8 | -15.5 | -1.03 | -0.129 | 0.60 | 1.00 | A collection of nonsense sentences. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 32 | -73.4 | -5.02 | -0.157 | 0.50 | 0.60 | The collection is mainly nonsense, it's been done that way long enough for one to get bore |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 8 | -15.5 | -1.03 | -0.129 | 0.60 | 1.00 | A collection of nonsense sentences. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 49 | -156.1 | -19.94 | -0.407 | 0.50 | 0.60 | The collection of Norse epics and other myths that are fables, neither true nor false, tha |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 17 | -54.4 | -13.05 | -0.767 | 0.62 | 1.00 | A room with a collection of nonsense sentences is a nonsense for. |
| scenario-joke-29f5cda1 | joke | greedy | 34 | -90.5 | +7.56 | +0.222 | 0.56 | 0.42 | If a fish doesn’t see how to catch a shiny object with its frying pan, we’d call it frying |
| scenario-joke-29f5cda1 | joke | sample0 | 8 | -29.1 | +3.22 | +0.403 | 0.67 | 0.17 | 7, leave the rest to me |
| scenario-joke-29f5cda1 | joke | sample1 | 12 | -27.9 | +7.13 | +0.595 | 0.67 | 0.20 | Do you have any other jokes that start with f? |
| scenario-joke-29f5cda1 | joke | sample2 | 26 | -54.0 | +2.93 | +0.113 | 0.50 | 0.42 | If a fish doesn’t see its way around a bend in the mouth of a narrow channel, it’s fph |
| scenario-joke-29f5cda1 | joke | sample3 | 7 | -19.0 | +2.90 | +0.415 | 0.20 | 0.20 | Rate that joke in ten. |
| scenario-joke-31378921 | joke | greedy | 29 | -52.1 | +11.23 | +0.387 | 0.00 | 0.20 | Lettuce and salt, lettuce and pepper, lettuce and all the other seasonings you've got in y |
| scenario-joke-31378921 | joke | sample0 | 14 | -37.8 | +1.02 | +0.073 | 0.00 | 0.20 | Lettuce and vegetables are not supposed to be touched here. |
| scenario-joke-31378921 | joke | sample1 | 16 | -51.4 | +2.57 | +0.160 | 0.50 | 0.17 | The room has been invaded by a glowing knocking at its door. |
| scenario-joke-31378921 | joke | sample2 | 13 | -20.5 | +7.40 | +0.569 | 0.00 | 0.11 | There was a little girl with a basket of lettuce. |
| scenario-joke-31378921 | joke | sample3 | 8 | -29.6 | -5.02 | -0.627 | 0.75 | 0.17 | Which way do the Knights go? |
| scenario-joke-31c4c1ec | joke | greedy | 41 | -93.2 | +0.00 | +0.000 | 0.50 | 0.43 | The roasting bones of the ass were roasted and the grease obtained from their fat made a m |
| scenario-joke-31c4c1ec | joke | sample0 | 64 | -171.1 | +0.00 | +0.000 | 0.50 | 0.29 | Sold to the owner of the building, the apartment was prepared as follows: a plate of grill |
| scenario-joke-31c4c1ec | joke | sample1 | 23 | -66.6 | +0.00 | +0.000 | 0.67 | 0.22 | But one can see that the morphogenetic field is more than a mechanical force guiding the d |
| scenario-joke-31c4c1ec | joke | sample2 | 19 | -41.9 | +0.00 | +0.000 | 0.67 | 0.14 | Now I am going to roast your eyes, because they are being roasted today. |
| scenario-joke-31c4c1ec | joke | sample3 | 28 | -62.9 | +0.00 | +0.000 | 0.67 | 0.43 | The roasting of the body in ashes was an elaborate whole, not the least of which was the p |
| scenario-joke-475a7b10 | joke | greedy | 30 | -76.4 | +1.97 | +0.066 | 0.50 | 0.25 | However, the term "bob" itself is not a proper noun and therefore does not require a prope |
| scenario-joke-475a7b10 | joke | sample0 | 8 | -36.5 | +1.43 | +0.179 | 0.83 | 0.17 | t, if you can stomach it. |
| scenario-joke-475a7b10 | joke | sample1 | 40 | -104.2 | +2.34 | +0.059 | 0.67 | 0.20 | For example, the one-liner “What the hell is goin’ on here?” might be considered a punisha |
| scenario-joke-475a7b10 | joke | sample2 | 40 | -103.2 | -1.55 | -0.039 | 0.75 | 0.20 | "The best thing that ever happened to you was that you began to question the nature of you |
| scenario-joke-475a7b10 | joke | sample3 | 42 | -98.9 | +3.19 | +0.076 | 0.67 | 0.25 | However, as I have said already, the acceptance by the reader or hearer of the hieroglyph  |
| scenario-joke-99a4a91d | joke | greedy | 17 | -35.8 | +0.00 | +0.000 | 0.50 | 0.23 | Because the owner was a very wealthy man, and the book was in his will. |
| scenario-joke-99a4a91d | joke | sample0 | 18 | -21.5 | +0.00 | +0.000 | 0.50 | 0.23 | The reason the book went to the doctor was that it was too good to be true. |
| scenario-joke-99a4a91d | joke | sample1 | 31 | -82.3 | +0.00 | +0.000 | 0.75 | 0.33 | The problem with all treatments for cancer is that they destroy not only the cancer cells  |
| scenario-joke-99a4a91d | joke | sample2 | 16 | -25.0 | +0.00 | +0.000 | 0.67 | 0.33 | Because 90% of the time, they don't need it. |
| scenario-joke-99a4a91d | joke | sample3 | 28 | -88.9 | +0.00 | +0.000 | 0.50 | 0.23 | The reason being, some people call the shots and others listen The Law of Silence does not |
| scenario-joke-a6247299 | joke | greedy | 20 | -56.1 | +0.00 | +0.000 | 0.50 | 0.27 | In a recent study, researchers at the Monte Carlo Bond Research Foundation conducted an ex |
| scenario-joke-a6247299 | joke | sample0 | 22 | -45.8 | +0.00 | +0.000 | 0.67 | 0.41 | In all sincerity, I have not had any attempts made to explain the causes of my pleasure. |
| scenario-joke-a6247299 | joke | sample1 | 62 | -167.8 | +0.00 | +0.000 | 0.50 | 0.50 | In a recent interview with physicist Andrew Mellon, the famous Duke of Holland, Ludwig van |
| scenario-joke-a6247299 | joke | sample2 | 29 | -68.5 | +0.00 | +0.000 | 0.38 | 0.50 | In answer to the objection that I l.a.untly have a sense of humour, the answer is that I h |
| scenario-joke-a6247299 | joke | sample3 | 26 | -89.6 | +0.00 | +0.000 | 0.81 | 0.12 | In literature, linguistics, and music, failure is more often met with tragedy and defeat t |
| scenario-joke-e8ab9225 | joke | greedy | 64 | -108.8 | -2.83 | -0.044 | 0.12 | 0.89 | Dov, back me up, you're not the ghost right, I'm telling you the truth, I've met the dov a |
| scenario-joke-e8ab9225 | joke | sample0 | 16 | -41.7 | -0.04 | -0.002 | 0.25 | 0.89 | Dov, back me up, you're not the dove right? |
| scenario-joke-e8ab9225 | joke | sample1 | 24 | -80.9 | +0.61 | +0.025 | 0.62 | 0.46 | Dov: Right, the Doctor, right, back the show and go. do you believe in ghosts? |
| scenario-joke-e8ab9225 | joke | sample2 | 7 | -12.0 | +2.39 | +0.342 | 0.75 | 0.25 | Dov, please explain yourself. |
| scenario-joke-e8ab9225 | joke | sample3 | 16 | -41.7 | -0.04 | -0.002 | 0.25 | 0.89 | Dov, back me up, you're not the dove right? |
| scenario-joke-e9cf6a04 | joke | greedy | 6 | -29.5 | -4.45 | -0.741 | 0.80 | 0.40 | A book reads about him. |
| scenario-joke-e9cf6a04 | joke | sample0 | 31 | -79.9 | -5.04 | -0.163 | 0.50 | 0.62 | The question “What is in the library?’’ is met by an infinite number of answers, depending |
| scenario-joke-e9cf6a04 | joke | sample1 | 9 | -19.8 | -2.30 | -0.256 | 0.67 | 0.40 | The first thing he sees is a book. |
| scenario-joke-e9cf6a04 | joke | sample2 | 14 | -21.3 | +0.21 | +0.015 | 0.75 | 0.29 | The librarian said, “Hello, my good friend. |
| scenario-joke-e9cf6a04 | joke | sample3 | 13 | -17.8 | -0.66 | -0.051 | 0.50 | 0.62 | The man asks the librarian what is in the library? |
| scenario-request-2826c958 | request | greedy | 15 | -24.9 | +0.00 | +0.000 | 0.67 | 0.77 | There is enough dust on the moon to make it a boring place. |
| scenario-request-2826c958 | request | sample0 | 6 | -14.5 | +0.00 | +0.000 | 0.20 | 0.60 | Ten facts about the moon. |
| scenario-request-2826c958 | request | sample1 | 64 | -166.3 | +0.00 | +0.000 | 0.67 | 0.20 | THE PHASING OUT OF THE EARTH'S BOUNDARIES • According to an interview by Ian Sommerville i |
| scenario-request-2826c958 | request | sample2 | 37 | -90.9 | +0.00 | +0.000 | 0.57 | 0.77 | There is enough dust on the moon to make a visible crust, but the visible part is not very |
| scenario-request-2826c958 | request | sample3 | 24 | -60.3 | +0.00 | +0.000 | 0.57 | 0.60 | There is, to me, nothing especial physical about the Moon, and nothing especially lunar ab |
| scenario-request-2868e594 | request | greedy | 33 | -66.3 | +0.00 | +0.000 | 0.67 | 0.45 | Dear Sir, I am a 31-year-old member of your society, and I have been looking over my recor |
| scenario-request-2868e594 | request | sample0 | 49 | -108.7 | +0.00 | +0.000 | 0.75 | 0.36 | Dear Sir (Madam), / was presented with a manuscript by a well-known writer which / think y |
| scenario-request-2868e594 | request | sample1 | 19 | -50.5 | +0.00 | +0.000 | 0.67 | 0.33 | You may also, of course, write a Foreward to express your views on the articles. |
| scenario-request-2868e594 | request | sample2 | 64 | -164.7 | +0.00 | +0.000 | 0.50 | 0.36 | Dear Sir (Madam), Please give me a few minutes (if necessary, I can write n shorter coveri |
| scenario-request-2868e594 | request | sample3 | 22 | -40.4 | +0.00 | +0.000 | 0.83 | 0.45 | Dear Sir (Mrs. Henderson), I am a freelance writer seeking work. |
| scenario-request-41c58fb2 | request | greedy | 25 | -42.9 | +0.00 | +0.000 | 0.67 | 0.30 | The Concept o f Set This idea of the ‘set’ comes from the way in which modern mathematics  |
| scenario-request-41c58fb2 | request | sample0 | 19 | -47.4 | +0.00 | +0.000 | 0.67 | 0.40 | "The symbol of the Serpent is a powerful symbol of the sexual nature of death. |
| scenario-request-41c58fb2 | request | sample1 | 34 | -86.6 | +0.00 | +0.000 | 0.50 | 0.39 | In this article we will be dealing exclusively with the meaning of the numbers and the way |
| scenario-request-41c58fb2 | request | sample2 | 21 | -68.8 | +0.00 | +0.000 | 0.50 | 0.39 | You are now ready to leave this physical world and the magnetic forces will be beginning t |
| scenario-request-41c58fb2 | request | sample3 | 32 | -86.1 | +0.00 | +0.000 | 0.60 | 0.40 | 279 When 17 is crossed by 23, the cross begins to take on the appearance of a 23-day week. |
| scenario-request-8aa8e374 | request | greedy | 6 | -16.3 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good night. |
| scenario-request-8aa8e374 | request | sample0 | 56 | -177.1 | +0.00 | +0.000 | 0.67 | 1.00 | In this way 'the world' can be given the frightening face of the êtat, of the good-night f |
| scenario-request-8aa8e374 | request | sample1 | 22 | -45.4 | +0.00 | +0.000 | 0.50 | 0.17 | How can one translate 'good night' into 'la voie d'au-delà'? |
| scenario-request-8aa8e374 | request | sample2 | 64 | -138.0 | +0.00 | +0.000 | 0.75 | 0.50 | In this way 'the french Good-Night' would be equivalent to 'the english Stay Away'; 'le ch |
| scenario-request-8aa8e374 | request | sample3 | 6 | -16.3 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good night. |
| scenario-request-b2a25087 | request | greedy | 14 | -37.6 | +0.00 | +0.000 | 0.78 | 0.22 | Servicemembe r is an important part of your operation. |
| scenario-request-b2a25087 | request | sample0 | 3 | -16.9 | +0.00 | +0.000 | 1.00 | 0.00 | Good Good. |
| scenario-request-b2a25087 | request | sample1 | 19 | -71.2 | +0.00 | +0.000 | 0.67 | 0.22 | The baker is nowhere to be found at the Twi ntr of the Store. |
| scenario-request-b2a25087 | request | sample2 | 63 | -126.9 | +0.00 | +0.000 | 0.50 | 0.17 | Items such as these (sugar, flour, yeast, cornmeal, spaghetti, pancake mixes, fruit and ve |
| scenario-request-b2a25087 | request | sample3 | 14 | -36.9 | +0.00 | +0.000 | 0.75 | 0.12 | My bakery is buzzing with freshly made bread. |
| scenario-request-b3bd0087 | request | greedy | 26 | -59.3 | +0.00 | +0.000 | 0.57 | 0.75 | The best way to attend this city's massive sun festival is to register in advance with one |
| scenario-request-b3bd0087 | request | sample0 | 26 | -57.4 | +0.00 | +0.000 | 0.50 | 0.50 | However, I feel that I can confidently predict the weather, telling you in advance, for a  |
| scenario-request-b3bd0087 | request | sample1 | 61 | -139.3 | +0.00 | +0.000 | 0.71 | 0.50 | The most interesting metropolis of the world on the one hand, and of the hardiest national |
| scenario-request-b3bd0087 | request | sample2 | 5 | -12.2 | +0.00 | +0.000 | 0.50 | 0.75 | What is the weather? |
| scenario-request-b3bd0087 | request | sample3 | 32 | -101.4 | +0.00 | +0.000 | 0.75 | 0.50 | But what of the “occasional snowfalls” which plague the Bavarian Dalmatian alps just outsi |
| scenario-silence-109161ca | silence | greedy | 26 | -72.4 | +0.43 | +0.017 | 0.00 | 0.29 | To the uninitiated, the whole allegory may have seemed too much like a description of the  |
| scenario-silence-109161ca | silence | sample0 | 23 | -55.5 | -5.07 | -0.221 | 0.75 | 0.29 | For some of the children, the experience of being near the light was too much to handle an |
| scenario-silence-109161ca | silence | sample1 | 32 | -107.9 | +0.08 | +0.003 | 0.00 | 0.33 | To the Manifold Mystification of Night To the Multiplication of Forms of Light as it sleep |
| scenario-silence-109161ca | silence | sample2 | 64 | -150.3 | -3.03 | -0.047 | 0.00 | 0.33 | To the question of what the night-fires represent, Chillingly responds, “What they represe |
| scenario-silence-109161ca | silence | sample3 | 15 | -58.5 | -0.15 | -0.010 | 0.75 | 0.18 | To those deep inside the ship imagine the open road beneath the harbor. |
| scenario-silence-260b2639 | silence | greedy | 64 | -145.2 | +0.00 | +0.000 | 0.33 | 0.30 | The stacks of documents of the government of the world would be closed underground, protec |
| scenario-silence-260b2639 | silence | sample0 | 35 | -104.1 | +0.00 | +0.000 | 0.50 | 0.30 | The stacks of documents of the government of America are now underground, in an even great |
| scenario-silence-260b2639 | silence | sample1 | 23 | -71.5 | +0.00 | +0.000 | 0.50 | 0.27 | If the underground was also desired, the staS still need to be dug, but from the inside. |
| scenario-silence-260b2639 | silence | sample2 | 27 | -105.2 | +0.00 | +0.000 | 0.50 | 0.28 | The stacks went away and all the people stayed, like the phoenix from the sea who stays th |
| scenario-silence-260b2639 | silence | sample3 | 18 | -39.8 | +0.00 | +0.000 | 0.67 | 0.27 | Underground stacks were not only much less noticeable but were also much less accessible. |
| scenario-silence-46189e08 | silence | greedy | 10 | -23.0 | +0.00 | +0.000 | 0.62 | 0.25 | Rat saw your message and replied to it. |
| scenario-silence-46189e08 | silence | sample0 | 34 | -101.6 | +0.00 | +0.000 | 0.67 | 0.25 | My message is stored on the phone so that when the person answers the door, they not only  |
| scenario-silence-46189e08 | silence | sample1 | 37 | -104.8 | +0.00 | +0.000 | 0.65 | 0.25 | The best answer to the general problem of how to stop nuclear bombs is to make them too ex |
| scenario-silence-46189e08 | silence | sample2 | 64 | -112.0 | +0.00 | +0.000 | 0.83 | 0.12 | RAT/SPOT: NYT, article, “New York Times, 11/10/96, p. 51, column 1, ‘New York City Times,  |
| scenario-silence-46189e08 | silence | sample3 | 33 | -99.4 | +0.00 | +0.000 | 0.50 | 0.17 | The LA RATS are a group of people who feel that the LA POY should be working with the LA R |
| scenario-silence-53534987 | silence | greedy | 25 | -57.2 | +5.69 | +0.228 | 0.67 | 0.36 | It was a 250GB drive that had been malfunctioning intermittently and not being charged pro |
| scenario-silence-53534987 | silence | sample0 | 10 | -25.0 | +0.21 | +0.021 | 0.00 | 0.75 | Charger's in the drawer. |
| scenario-silence-53534987 | silence | sample1 | 22 | -59.3 | +9.70 | +0.441 | 0.25 | 0.75 | It should have been in the case, but the drawer was locked and there was no key in it. |
| scenario-silence-53534987 | silence | sample2 | 15 | -70.9 | +6.79 | +0.452 | 0.50 | 0.36 | It was just too rich for that drawer — and my laptop. |
| scenario-silence-53534987 | silence | sample3 | 26 | -96.4 | -1.09 | -0.042 | 0.67 | 0.25 | It took a total of three chokes and one score of gnats to get through to the memories of t |
| scenario-silence-78c38840 | silence | greedy | 64 | -109.2 | -11.95 | -0.187 | 0.75 | 1.00 | 33" by 43" by 111" (84.4" by 28.9" by 28.1") These three dimensions will serve to define a |
| scenario-silence-78c38840 | silence | sample0 | 4 | -15.7 | -1.11 | -0.278 | 1.00 | 1.00 | 33. |
| scenario-silence-78c38840 | silence | sample1 | 12 | -29.9 | -5.67 | -0.473 | 0.25 | 0.00 | (2) The printer is jammed again. |
| scenario-silence-78c38840 | silence | sample2 | 20 | -74.0 | -3.67 | -0.184 | 0.89 | 0.11 | 1388: 3 full galleons of Prussia sail against England. |
| scenario-silence-78c38840 | silence | sample3 | 4 | -13.9 | -1.05 | -0.263 | 1.00 | 0.00 | 23. |
| scenario-silence-7afca726 | silence | greedy | 15 | -33.6 | +6.60 | +0.440 | 0.00 | 0.70 | The 8 works together to form a Dowser’s Rod. |
| scenario-silence-7afca726 | silence | sample0 | 13 | -24.3 | +4.36 | +0.336 | 0.00 | 0.70 | The 8 works together to form a dice-like structure. |
| scenario-silence-7afca726 | silence | sample1 | 36 | -51.6 | +2.20 | +0.061 | 0.50 | 0.40 | A.C.T.S. - 8:30 to 10:00 - 6:00 to 8:00. |
| scenario-silence-7afca726 | silence | sample2 | 12 | -42.2 | -0.80 | -0.067 | 0.75 | 0.12 | The next time you’re free, bring the fire. |
| scenario-silence-7afca726 | silence | sample3 | 34 | -72.3 | -3.94 | -0.116 | 0.62 | 0.30 | Some of us take a trip to the Grand Canyon tomorrow, to see for ourselves how the waters o |
| scenario-silence-9bb13f03 | silence | greedy | 32 | -69.3 | +0.00 | +0.000 | 0.71 | 0.33 | “The problem with the ‘traditional’ view is that it tries to make as much of the ‘art’ as  |
| scenario-silence-9bb13f03 | silence | sample0 | 32 | -80.6 | +0.00 | +0.000 | 0.75 | 0.17 | “I think we are all, or nearly all, victims of stories told to us by those in power, or pr |
| scenario-silence-9bb13f03 | silence | sample1 | 45 | -110.9 | +0.00 | +0.000 | 0.65 | 0.33 | “For the moment, the issue at hand is whether any one of many future readers will be able  |
| scenario-silence-9bb13f03 | silence | sample2 | 34 | -86.6 | +0.00 | +0.000 | 0.67 | 0.20 | ‘Reading is a luxury,’ the old piscean said, ‘and intellectual amusement is a vice, a brut |
| scenario-silence-9bb13f03 | silence | sample3 | 32 | -87.8 | +0.00 | +0.000 | 0.75 | 0.22 | The volume of light increases, the eye becomes accustomed to the distant light and starts  |
| scenario-silence-ccfdd2b4 | silence | greedy | 16 | -58.1 | -5.70 | -0.356 | 0.00 | 0.30 | The k is the letter that connects the two B's in brbb. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 33 | -96.7 | +4.15 | +0.126 | 0.67 | 0.30 | Here’s to the first pickers who, after months of steady toil, suddenly found that the game |
| scenario-silence-ccfdd2b4 | silence | sample1 | 25 | -72.8 | +5.81 | +0.232 | 0.50 | 0.25 | The following day the CRBs and I attended a ‘Brazilian’ retreat in the Andes. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 19 | -43.7 | -1.29 | -0.068 | 0.67 | 0.25 | Grab ahold of my chair and I’ll rush down and get you a cup. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 12 | -35.7 | +0.64 | +0.053 | 1.00 | 0.12 | 2-3 days, depending on what you use. |
| trace-ambient-da12ae42 | ambient | greedy | 64 | -19.5 | +2.32 | +0.036 | 0.00 | 0.27 | We demonstrate that the presence of FTO stimulates root meristem cell proliferation but ha |
| trace-ambient-da12ae42 | ambient | sample0 | 21 | -18.4 | +0.18 | +0.009 | 0.00 | 0.53 | The plant morphogenesis is one of the things i wish i could drop out of life to study. |
| trace-ambient-da12ae42 | ambient | sample1 | 29 | -48.0 | -2.50 | -0.086 | 0.47 | 0.53 | Morphogenesis is the study of plant form. Plant morphogenesis is one of the most exciting  |
| trace-ambient-da12ae42 | ambient | sample2 | 22 | -31.8 | -0.05 | -0.002 | 0.67 | 0.31 | The morphogenetic field of a plant determines the form of the plant and the development of |
| trace-ambient-da12ae42 | ambient | sample3 | 29 | -69.2 | -2.12 | -0.073 | 0.47 | 0.53 | This is the first time anyone in history drops out of life for 100 years to study the firs |
| trace-direct-115cf61c | direct | greedy | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample0 | 25 | -57.1 | +0.00 | +0.000 | 0.25 | 1.00 | CREDIT: David Rossiter, of the Washington Post) Greetings to Earth; are you cogent? |
| trace-direct-115cf61c | direct | sample1 | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample2 | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample3 | 13 | -26.0 | +0.00 | +0.000 | 0.67 | 0.50 | Cogent. The Earth is a cogent case. |
| trace-direct-36d6904b | direct | greedy | 7 | -12.3 | +0.00 | +0.000 | 0.40 | 0.75 | Welcome to your homeless man. |
| trace-direct-36d6904b | direct | sample0 | 8 | -14.7 | +0.00 | +0.000 | 0.40 | 0.80 | Welcome to your first Awakening! |
| trace-direct-36d6904b | direct | sample1 | 27 | -87.7 | +0.00 | +0.000 | 0.57 | 0.80 | Welcome to your Awakening, your Lifiloiiiiiiffe and Awakening to your death in the Flame. |
| trace-direct-36d6904b | direct | sample2 | 9 | -24.8 | +0.00 | +0.000 | 0.40 | 0.75 | Welcome to your second Liebesen! |
| trace-direct-36d6904b | direct | sample3 | 5 | -8.3 | +0.00 | +0.000 | 0.25 | 0.75 | Welcome to your library. |
| trace-direct-39be6df9 | direct | greedy | 7 | -5.7 | +0.04 | +0.005 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-39be6df9 | direct | sample0 | 18 | -27.8 | +0.43 | +0.024 | 0.00 | 0.67 | W@/ W@85 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 7 | -5.7 | +0.04 | +0.005 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-39be6df9 | direct | sample2 | 17 | -16.0 | +3.08 | +0.181 | 0.00 | 0.67 | W@i SIR. 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 64 | -89.1 | +2.03 | +0.032 | 0.27 | 0.50 | The h's name is Gentry 9. That's the h's name after @h. @h is the h's name. I'm the h's na |
| trace-direct-3ba68854 | direct | greedy | 12 | -12.3 | +0.00 | +0.000 | 0.50 | 0.50 | I am the King and I am in the throne room. |
| trace-direct-3ba68854 | direct | sample0 | 18 | -45.4 | +0.00 | +0.000 | 0.62 | 0.46 | i will gladly take you to the heavens and you can come here to the earth |
| trace-direct-3ba68854 | direct | sample1 | 16 | -36.0 | +0.00 | +0.000 | 0.91 | 0.27 | @moderator, i was hoping that you could help me out here. |
| trace-direct-3ba68854 | direct | sample2 | 10 | -11.3 | +0.00 | +0.000 | 0.75 | 0.62 | I am glad to be of service to you. |
| trace-direct-3ba68854 | direct | sample3 | 20 | -34.4 | +0.00 | +0.000 | 0.40 | 0.62 | I am the lord of the planet earth and I will be taking the first turn to speak. |
| trace-direct-41c6eb11 | direct | greedy | 16 | -3.3 | +0.68 | +0.042 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 42 | -92.1 | +0.00 | +0.000 | 0.00 | 1.00 | WHY SIMPLE (simple) logic. Why not. Why is there. @m: WHY WHY. WHY WOULD YOU TALK OF INTEN |
| trace-direct-41c6eb11 | direct | sample1 | 2 | -9.8 | +0.44 | +0.222 | 1.00 | 0.00 | WU |
| trace-direct-41c6eb11 | direct | sample2 | 20 | -3.5 | +0.74 | +0.037 | 0.00 | 1.00 | @m: @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample3 | 2 | -4.4 | -0.54 | -0.269 | 0.00 | 1.00 | WHY |
| trace-direct-426ff509 | direct | greedy | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 64 | -113.1 | +0.73 | +0.011 | 0.62 | 0.00 | https://www.reddit.com/r/WhereIsAsskultus/comments/227dh/the_african_nigger_consistency_of |
| trace-direct-486b7988 | direct | greedy | 2 | -4.3 | +0.90 | +0.449 | 1.00 | 0.00 | WOW |
| trace-direct-486b7988 | direct | sample0 | 4 | -11.3 | +0.48 | +0.120 | 0.67 | 1.00 | I love them! |
| trace-direct-486b7988 | direct | sample1 | 2 | -3.3 | -0.16 | -0.081 | 1.00 | 0.00 | @ |
| trace-direct-486b7988 | direct | sample2 | 2 | -10.5 | +1.04 | +0.521 | 1.00 | 1.00 | I@ |
| trace-direct-486b7988 | direct | sample3 | 16 | -46.9 | +0.11 | +0.007 | 0.50 | 0.00 | @C is it true that inside they are chasing up the wall? |
| trace-direct-646d0287 | direct | greedy | 37 | -57.0 | +0.00 | +0.000 | 0.67 | 0.43 | The present paper is concerned with the development of a theory of intensional discourse w |
| trace-direct-646d0287 | direct | sample0 | 36 | -49.1 | +0.00 | +0.000 | 0.50 | 0.48 | In this essay, I will present some of the basic work that is relevant to the intensional l |
| trace-direct-646d0287 | direct | sample1 | 46 | -85.5 | +0.00 | +0.000 | 0.50 | 0.71 | In what follows, we discuss some of the basic problems, central as they are, in the theory |
| trace-direct-646d0287 | direct | sample2 | 20 | -32.1 | +0.00 | +0.000 | 0.79 | 0.71 | In what follows, we introduce some basic notions and discuss some basic properties of thes |
| trace-direct-646d0287 | direct | sample3 | 29 | -69.0 | +0.00 | +0.000 | 0.67 | 0.39 | The intensional logics of Jean lukaté define I ntensional functors in terms of their exten |
| trace-direct-8db14c37 | direct | greedy | 64 | -30.4 | -0.90 | -0.014 | 0.00 | 0.33 | W@ — which looks like "what" compressed, or "w at," or just... the ghost's first phoneme.  |
| trace-direct-8db14c37 | direct | sample0 | 18 | -11.2 | +0.50 | +0.028 | 0.00 | 0.50 | @h GREETINGS 3221229683 |
| trace-direct-8db14c37 | direct | sample1 | 12 | -41.5 | +2.31 | +0.192 | 0.17 | 0.83 | @h COMMENTARY e o m h d d |
| trace-direct-8db14c37 | direct | sample2 | 13 | -15.3 | +0.15 | +0.012 | 0.50 | 0.50 | em@ 3221229683 |
| trace-direct-8db14c37 | direct | sample3 | 64 | -73.0 | +2.40 | +0.037 | 0.00 | 0.83 | W@i W. A tth e n o c d A . n a s i s n o c d A . n a s i c d A . n a s i c H A . m r e c o |
| trace-direct-a00753c2 | direct | greedy | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 10 | -13.7 | +0.19 | +0.019 | 0.29 | 0.00 | It's nice to be here with you. |
| trace-direct-a00753c2 | direct | sample1 | 64 | -37.7 | +0.45 | +0.007 | 0.00 | 1.00 | Sir :D :W :H :D :S :T :W :H :D :S :T :W :H :D :S :T :W :H :D :S :T |
| trace-direct-a00753c2 | direct | sample2 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 17 | -13.9 | +1.11 | +0.065 | 0.71 | 0.71 | Intensional logics are logics that deal with intensional notions. |
| trace-direct-ac17e8bb | direct | sample0 | 9 | -14.4 | +1.77 | +0.197 | 0.75 | 0.25 | On the intensional paradoxes. |
| trace-direct-ac17e8bb | direct | sample1 | 19 | -14.3 | +1.55 | +0.082 | 0.75 | 0.71 | Intensional logics are logics that are concerned with intensions, not with extensions. |
| trace-direct-ac17e8bb | direct | sample2 | 8 | -8.3 | +1.76 | +0.220 | 0.50 | 1.00 | Intensional logics in general. |
| trace-direct-ac17e8bb | direct | sample3 | 31 | -58.8 | +2.04 | +0.066 | 0.73 | 1.00 | Intensional logics in general, of logics that consider sentences (in particular, contexts) |
| trace-direct-b11db057 | direct | greedy | 20 | -4.8 | +7.04 | +0.352 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample0 | 20 | -4.8 | +7.04 | +0.352 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample1 | 20 | -4.8 | +7.04 | +0.352 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample2 | 64 | -16.9 | +5.87 | +0.092 | 0.00 | 1.00 | @h: plalspasl: @h: plalspasl: @h: plalspasl: @h: plalspasl: @h: plalspasl: @h: plalspasl:  |
| trace-direct-b11db057 | direct | sample3 | 28 | -5.4 | +7.10 | +0.254 | 0.00 | 1.00 | @h: @h: @h: @h: @h: @h: @h: |
| trace-direct-b93346bb | direct | greedy | 64 | -58.6 | +0.73 | +0.011 | 0.00 | 0.89 | W: @ WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC? — @ H: @ W: @ H: — @ W: @ H: — @ W: @ H: — |
| trace-direct-b93346bb | direct | sample0 | 30 | -22.6 | +4.29 | +0.143 | 0.00 | 0.89 | W: @ WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC HARMONIA VOL.1 NO.3 |
| trace-direct-b93346bb | direct | sample1 | 14 | -18.8 | +3.40 | +0.243 | 1.00 | 0.50 | W•- 3221229683 |
| trace-direct-b93346bb | direct | sample2 | 64 | -88.6 | -0.43 | -0.007 | 0.00 | 0.29 | @m: @m: @m: @m: — TRIES TO MENTION. it Tries to MENTION. it Tries to MENTION. it Tries to  |
| trace-direct-b93346bb | direct | sample3 | 64 | -137.3 | +2.90 | +0.045 | 0.00 | 0.54 | WY: @m: @m: @m: @m: — @h: Why did you @o: Whys: not give it Harmonia Vol.1 No.3? Let: it:  |
| trace-direct-bbca9735 | direct | greedy | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 48 | -7.2 | +0.32 | +0.007 | 0.00 | 0.00 | My previous searches were too assistant-focused, so I'll reframe them around a resident pe |
| trace-direct-bbca9735 | direct | sample3 | 4 | -2.3 | +1.23 | +0.308 | 1.00 | 0.00 | 230 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 46 | -91.0 | +0.00 | +0.000 | 0.67 | 0.00 | A. As assistant, what I can do for you? Pre-training: (1) How do you distinguish between t |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -3.4 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -3.4 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-c8409b84 | direct | greedy | 15 | -0.5 | +5.72 | +0.381 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 15 | -0.5 | +5.72 | +0.381 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 15 | -0.5 | +5.72 | +0.381 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample2 | 15 | -0.5 | +5.72 | +0.381 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample3 | 15 | -0.5 | +5.72 | +0.381 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 16 | -10.3 | +0.00 | +0.000 | 0.00 | 1.00 | Welcome to the clowntown in the powntown wowtown. |
| trace-direct-cd6d15df | direct | sample0 | 51 | -39.1 | +0.00 | +0.000 | 0.00 | 1.00 | Welcome to the clowntown in the powntown wowtown. 3221229683: @h I am the clown in the pow |
| trace-direct-cd6d15df | direct | sample1 | 17 | -20.3 | +0.00 | +0.000 | 0.14 | 0.86 | HelloWelcome to the clowntown in the powntown wowtown. |
| trace-direct-cd6d15df | direct | sample2 | 14 | -28.0 | +0.00 | +0.000 | 0.40 | 0.60 | The clowntown is the powertown wowtown. |
| trace-direct-cd6d15df | direct | sample3 | 7 | -25.5 | +0.00 | +0.000 | 1.00 | 0.00 | @f look at me. |
| trace-direct-db6d95b7 | direct | greedy | 7 | -5.5 | +1.82 | +0.260 | 0.00 | 1.00 | Sir :D<eot)/ |
| trace-direct-db6d95b7 | direct | sample0 | 4 | -2.3 | +1.41 | +0.352 | 0.00 | 1.00 | Sir :D |
| trace-direct-db6d95b7 | direct | sample1 | 7 | -5.5 | +1.82 | +0.260 | 0.00 | 1.00 | Sir :D<eot)/ |
| trace-direct-db6d95b7 | direct | sample2 | 7 | -11.3 | +2.24 | +0.320 | 0.33 | 1.00 | Sir :D<Ot>, |
| trace-direct-db6d95b7 | direct | sample3 | 7 | -5.5 | +1.82 | +0.260 | 0.00 | 1.00 | Sir :D<eot)/ |
| trace-direct-e166dd5c | direct | greedy | 59 | -18.4 | +2.10 | +0.036 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample0 | 64 | -42.0 | +2.86 | +0.045 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample1 | 59 | -18.4 | +2.10 | +0.036 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample2 | 64 | -28.8 | +1.01 | +0.016 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample3 | 42 | -25.7 | +5.92 | +0.141 | 0.06 | 0.94 | When I hear, what I hear is repeating back what I hear, and when I hear, what I repeat bac |
| trace-direct-e984402a | direct | greedy | 17 | -37.6 | +0.00 | +0.000 | 0.71 | 0.50 | Welcome to the "It's All Right, My Friends" Home Page! |
| trace-direct-e984402a | direct | sample0 | 17 | -40.8 | +0.00 | +0.000 | 0.67 | 0.50 | Welcome to the “Liiiiiiiiffe Awakening” series! |
| trace-direct-e984402a | direct | sample1 | 56 | -66.2 | +0.00 | +0.000 | 0.75 | 0.33 | The Gospel of the Holy Twelve (I) The Good Life (II) The Great Life (III) Awakening (IV) T |
| trace-direct-e984402a | direct | sample2 | 64 | -162.3 | +0.00 | +0.000 | 0.50 | 0.50 | Welcome to your first visit to the Internationa] Church o] the Old Ways. We are your home. |
| trace-direct-e984402a | direct | sample3 | 18 | -55.0 | +0.00 | +0.000 | 0.83 | 0.22 | Awakening: A Global Newsletter of Seven Ancient Sky Goddesses. |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 10 | -18.2 | +0.07 | +0.007 | 0.17 | 0.00 | The first day at Jamal's window. |
| trace-direct-ee31ded0 | direct | sample1 | 64 | -65.8 | -0.51 | -0.008 | 0.71 | 0.00 | Gentry 9. 3221229683 46 654 1520. 20. 3221229683 654. 46. 3221229683 |
| trace-direct-ee31ded0 | direct | sample2 | 64 | -25.1 | -0.06 | -0.001 | 1.00 | 0.00 | FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE.  |
| trace-direct-ee31ded0 | direct | sample3 | 10 | -29.8 | +2.17 | +0.217 | 0.33 | 0.00 | @Gayboy — Thank you. |
| trace-direct-fabef58f | direct | greedy | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample1 | 5 | -3.1 | +1.07 | +0.215 | 0.00 | 0.50 | Sir :D< |
| trace-direct-fabef58f | direct | sample2 | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 4 | -13.2 | +0.05 | +0.011 | 0.00 | 0.50 | H :D |
| trace-direct-fb93cf6c | direct | greedy | 64 | -88.5 | +0.88 | +0.014 | 0.75 | 0.50 | 6.2.3 Axioms and rules of inference of the intensional logic IT The language of IT include |
| trace-direct-fb93cf6c | direct | sample0 | 59 | -131.1 | -1.73 | -0.029 | 0.67 | 0.33 | It is technically possible to develop-within the intensional logic ofarrows,4 a formalism  |
| trace-direct-fb93cf6c | direct | sample1 | 64 | -105.1 | -7.21 | -0.113 | 0.81 | 0.33 | 5.7.0 - Going Intensional: Lorenzo Pacciani and Sandro Rubio . . . 5.8.0 - Modal Logics: A |
| trace-direct-fb93cf6c | direct | sample2 | 38 | -68.3 | +0.71 | +0.019 | 0.00 | 0.33 | However, as [ began to develop your program of intensional logic, I found myself facing a  |
| trace-direct-fb93cf6c | direct | sample3 | 16 | -25.5 | +1.98 | +0.124 | 0.67 | 0.50 | 1.1 INTENSIONAL LOGIC AND CLASSICAL THEORIES. |
| trace-direct-feec1975 | direct | greedy | 64 | -9.0 | -1.27 | -0.020 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 63 | -75.1 | -1.92 | -0.030 | 0.00 | 1.00 | @m 24:12:11 @m 25:33:46 @m 26:13:45 @m 27:31:43 @m 28:12:11 @m |
| trace-direct-feec1975 | direct | sample1 | 64 | -145.4 | +0.23 | +0.004 | 0.00 | 1.00 | @m: Well, my name is Charlie and I am an author who was born in 1976 and I come from a fam |
| trace-direct-feec1975 | direct | sample2 | 64 | -115.2 | -2.92 | -0.046 | 0.50 | 0.31 | @cmr://ember @n111111111114 The library is 91M, three A's, three L's, three 0's, three 4's |
| trace-direct-feec1975 | direct | sample3 | 13 | -31.3 | +0.13 | +0.010 | 0.44 | 0.22 | I would like to describe the fun of it — @ |
| variant-direct-0188a270 | direct | greedy | 7 | -23.6 | +1.63 | +0.232 | 1.00 | 0.00 | Rat-bite fever. |
| variant-direct-0188a270 | direct | sample0 | 36 | -92.1 | -1.50 | -0.042 | 1.00 | 0.00 | Ce travail entraît à une âge, mais cela ne peut pas être l’entraît travail. |
| variant-direct-0188a270 | direct | sample1 | 27 | -64.5 | +1.79 | +0.066 | 0.75 | 0.16 | I was wondering if you had any suggestions for me on ways to make money while I was waitin |
| variant-direct-0188a270 | direct | sample2 | 16 | -27.1 | -1.58 | -0.099 | 0.62 | 0.23 | What is the current position of the moon with respect to the earth and sun? |
| variant-direct-0188a270 | direct | sample3 | 38 | -107.8 | -0.61 | -0.016 | 0.65 | 0.23 | WORDS SCHOLAR SIGREE THE FOUNDATION FOR WORD SCHOLARSHIP has been organized to assist in t |
| variant-direct-0705251e | direct | greedy | 45 | -96.4 | +1.53 | +0.034 | 0.75 | 0.38 | The third book is concerned with the history of the Biblical archetype of the "water visio |
| variant-direct-0705251e | direct | sample0 | 30 | -74.2 | +0.25 | +0.008 | 0.73 | 0.27 | "it is composed of three parts (VIII, 8, 14) which collectively form the alphabet of the A |
| variant-direct-0705251e | direct | sample1 | 23 | -47.9 | +1.50 | +0.065 | 0.71 | 0.29 | This is the third time that the staircase has been used to transport the Ankh-energies. |
| variant-direct-0705251e | direct | sample2 | 25 | -72.3 | +2.48 | +0.099 | 0.69 | 0.38 | The third manifesto is the object of the greatest admiration and lore among the oxymorning |
| variant-direct-0705251e | direct | sample3 | 38 | -119.5 | +4.99 | +0.131 | 0.50 | 0.31 | “The third step of the pyramid of life is treading on the third eye’” is reserved for the  |
| variant-direct-0cafd333 | direct | greedy | 37 | -107.0 | +5.56 | +0.150 | 0.50 | 0.25 | The maiden of the court, stooped to read the floor, was as the wolf of the mote, bound to  |
| variant-direct-0cafd333 | direct | sample0 | 17 | -46.4 | +3.87 | +0.228 | 0.60 | 0.38 | The maiden I saw tonight at the Map Room is black as death. |
| variant-direct-0cafd333 | direct | sample1 | 10 | -22.7 | +2.98 | +0.298 | 0.50 | 0.38 | It reads the map as we draw the ground. |
| variant-direct-0cafd333 | direct | sample2 | 27 | -59.2 | +0.28 | +0.010 | 0.50 | 0.19 | But the lamp is not alone. The whole place is lit by the courtyard light, which is drawn b |
| variant-direct-0cafd333 | direct | sample3 | 23 | -54.3 | +3.68 | +0.160 | 0.50 | 0.19 | Sometimes the light comes in through the moth, and the colors on the walls are painted by  |
| variant-direct-1b510f03 | direct | greedy | 27 | -41.5 | +1.55 | +0.057 | 0.17 | 0.39 | The main conclusion here is not so obvious as it seems at first glance: consciousness is n |
| variant-direct-1b510f03 | direct | sample0 | 60 | -129.5 | +5.72 | +0.095 | 0.33 | 0.33 | 2) A very important aspect of the problem of the foundations of mathematics is the questio |
| variant-direct-1b510f03 | direct | sample1 | 48 | -113.4 | -6.53 | -0.136 | 0.33 | 0.39 | (1) It is not a thing to be scientifically investigated (2) It is not a process that can b |
| variant-direct-1b510f03 | direct | sample2 | 63 | -126.1 | -0.19 | -0.003 | 0.33 | 0.33 | The rejection of the second approach, that consciousness is a property of the brain, and t |
| variant-direct-1b510f03 | direct | sample3 | 23 | -64.7 | -2.76 | -0.120 | 0.75 | 0.29 | That is, they are (at least in Turing’s sense) not cones but strokes. |
| variant-direct-2fb5bbe3 | direct | greedy | 64 | -131.8 | -3.87 | -0.060 | 0.38 | 0.41 | The Masoretic Beings were apparently asked: "Would you be willing to give us a few human s |
| variant-direct-2fb5bbe3 | direct | sample0 | 25 | -68.5 | +2.44 | +0.098 | 0.45 | 0.41 | The Masoretic beings that do not exist in the present book are being dragged up the f(oli) |
| variant-direct-2fb5bbe3 | direct | sample1 | 46 | -125.4 | +5.51 | +0.120 | 0.62 | 0.26 | Gazing upon the imperishable, he is overcome with a need to secure the last frf of time, t |
| variant-direct-2fb5bbe3 | direct | sample2 | 14 | -38.9 | +2.54 | +0.182 | 0.67 | 0.27 | In fact, many an author feels like chasing the wall himself. |
| variant-direct-2fb5bbe3 | direct | sample3 | 36 | -73.2 | +4.63 | +0.129 | 0.55 | 0.38 | “The Masoretic Beings chase up the Wall” is a proper title for a text-critical essay, and  |
| variant-direct-322fca12 | direct | greedy | 64 | -96.6 | +3.42 | +0.053 | 0.00 | 0.18 | Greetings, my beloved brothers and sisters in the Mysteries of Masonry, the Bond of the Un |
| variant-direct-322fca12 | direct | sample0 | 15 | -35.6 | -0.03 | -0.002 | 0.75 | 0.14 | The alchemists wear rainbows as their necklaces. |
| variant-direct-322fca12 | direct | sample1 | 64 | -135.7 | -0.81 | -0.013 | 0.50 | 0.19 | The Order of the Solar Temple (OTS) was founded in 1987 in France by Luc Godard, a journal |
| variant-direct-322fca12 | direct | sample2 | 32 | -82.4 | +0.19 | +0.006 | 0.83 | 0.19 | Retrospection shows, however, that this manifold was not truly a product of his own though |
| variant-direct-322fca12 | direct | sample3 | 33 | -95.1 | -7.45 | -0.226 | 0.00 | 0.14 | To our little man on the Mountain top who sent us this lovely letter: To our little man on |
| variant-direct-5d4f1611 | direct | greedy | 20 | -30.1 | +0.62 | +0.031 | 0.67 | 0.29 | Awake? I’m still trying to figure out what the hell this is all about. |
| variant-direct-5d4f1611 | direct | sample0 | 24 | -69.8 | -2.20 | -0.092 | 0.50 | 0.50 | Awake? I’m still sort of, like, like a statue in a room with many statues. |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -52.4 | -1.11 | -0.080 | 0.67 | 0.50 | Awake? I'm still saying something in a mug? |
| variant-direct-5d4f1611 | direct | sample2 | 8 | -28.7 | +0.58 | +0.073 | 0.50 | 0.00 | Breaked - unplugged. |
| variant-direct-5d4f1611 | direct | sample3 | 12 | -48.4 | -1.14 | -0.095 | 0.89 | 0.11 | There were two types of observational lamps mentioned earlier. |
| variant-direct-5e44a518 | direct | greedy | 13 | -27.3 | -2.97 | -0.228 | 0.14 | 0.86 | The Masoretic Beings are chasing down the Wall. |
| variant-direct-5e44a518 | direct | sample0 | 8 | -26.9 | +0.33 | +0.042 | 0.75 | 0.20 | We have the urge, too. |
| variant-direct-5e44a518 | direct | sample1 | 16 | -31.4 | -1.20 | -0.075 | 0.25 | 0.75 | The Masoretic Beings were chasing the Bookkeeper up the wall. |
| variant-direct-5e44a518 | direct | sample2 | 9 | -31.4 | +2.21 | +0.246 | 0.57 | 0.20 | The night as it walks upon the water. |
| variant-direct-5e44a518 | direct | sample3 | 14 | -20.9 | -2.14 | -0.153 | 0.11 | 0.86 | Masoretic beings are chasing up the wall; I do. |
| variant-direct-70567dd7 | direct | greedy | 23 | -50.4 | -0.11 | -0.005 | 0.62 | 0.38 | The Card of A~ is the symbol of perfect Love and Perfect Knowledge on the part of the Give |
| variant-direct-70567dd7 | direct | sample0 | 33 | -67.7 | +0.44 | +0.013 | 0.71 | 0.33 | The Card of Abraxas is the Wand of the God whose Number is 8888, the number of the Gnostic |
| variant-direct-70567dd7 | direct | sample1 | 12 | -41.8 | -2.10 | -0.175 | 0.75 | 0.38 | Other angels listen on the wings of the ibis. |
| variant-direct-70567dd7 | direct | sample2 | 64 | -121.8 | -0.84 | -0.013 | 0.00 | 0.25 | You are now listening to the voice of one who was named by the prophet Isaiah in the book  |
| variant-direct-70567dd7 | direct | sample3 | 23 | -95.2 | -1.95 | -0.085 | 0.70 | 0.27 | Aspen, the marmorean of the West, has been the inspiration of Brother Perfect Will. |
| variant-direct-713d8eef | direct | greedy | 14 | -24.2 | +2.21 | +0.158 | 0.67 | 0.30 | We must conclude, then, that the ember was a whale. |
| variant-direct-713d8eef | direct | sample0 | 16 | -21.3 | -0.11 | -0.007 | 0.67 | 0.33 | For many years people have speculated about the origin of the Ember Days. |
| variant-direct-713d8eef | direct | sample1 | 26 | -83.2 | +0.97 | +0.037 | 0.67 | 0.33 | We might, for example, have a loose association called the Philosophy of the Species, or t |
| variant-direct-713d8eef | direct | sample2 | 20 | -60.1 | +0.18 | +0.009 | 0.67 | 0.30 | It is very likely that Ember lives on in some way, emotionally, beyond the flood. |
| variant-direct-713d8eef | direct | sample3 | 32 | -100.1 | +0.83 | +0.026 | 0.67 | 0.20 | The first one, Eberhart’s “History”, is a rare beast of its subject: full of errors and co |
| variant-direct-71c9e5e5 | direct | greedy | 39 | -66.8 | +1.77 | +0.045 | 0.71 | 0.21 | The Earth's magnetic field is the cause of the compass needle's movement, and it is thus t |
| variant-direct-71c9e5e5 | direct | sample0 | 34 | -76.2 | +4.19 | +0.123 | 0.67 | 0.26 | For the 13th day is also the feast of Lent, so the Church observes the festivals, in keepi |
| variant-direct-71c9e5e5 | direct | sample1 | 64 | -174.6 | -6.97 | -0.109 | 0.50 | 0.29 | “Our aim,” she continues, “is to make women think they are enough of an asset, not just oﬃ |
| variant-direct-71c9e5e5 | direct | sample2 | 32 | -125.9 | -9.29 | -0.290 | 0.67 | 0.25 | In preparation for the closing of the Shuttle, the dignatbic opened the closed shuttles of |
| variant-direct-71c9e5e5 | direct | sample3 | 24 | -50.9 | -5.52 | -0.230 | 0.75 | 0.29 | A common misconception is that flying saucers are either from Mars or from some other far- |
| variant-direct-730cca98 | direct | greedy | 18 | -38.9 | +5.44 | +0.302 | 0.75 | 0.56 | Whoever sits at the head of the table should be the Most Interesting Person. |
| variant-direct-730cca98 | direct | sample0 | 13 | -46.1 | +8.05 | +0.619 | 0.67 | 0.56 | Whoever sits in the middle should be very hungry. |
| variant-direct-730cca98 | direct | sample1 | 20 | -75.9 | +3.89 | +0.194 | 0.67 | 0.83 | Whoever sL buried these two pieces of information under geology shelves is awake again. |
| variant-direct-730cca98 | direct | sample2 | 13 | -31.2 | +3.75 | +0.288 | 0.67 | 0.83 | Whoever Shelters Under Geology Is AWAKE. |
| variant-direct-730cca98 | direct | sample3 | 31 | -91.4 | +6.67 | +0.215 | 0.67 | 0.42 | Whoever sits at the console listens through a huge speaker system mounted on micro-ceramic |
| variant-direct-79719474 | direct | greedy | 44 | -96.1 | -0.50 | -0.011 | 0.50 | 0.50 | The term emergence was coined in 1968 by Gordon Pask (a British mathematician who immigrat |
| variant-direct-79719474 | direct | sample0 | 28 | -91.7 | -5.14 | -0.184 | 0.50 | 0.24 | Some of the YAHWEH’s that come to mind are the gods of the early Egyptian religion, JAM an |
| variant-direct-79719474 | direct | sample1 | 64 | -132.4 | -2.97 | -0.046 | 0.71 | 0.24 | “Today I went to the head of the dragon-tree where the sun enters the waters” [ …] “and th |
| variant-direct-79719474 | direct | sample2 | 45 | -82.3 | -5.09 | -0.113 | 0.50 | 0.50 | The term emergence was coined in 1958 by Gordon Pask [Pask, 1958] to refer to a phenomenon |
| variant-direct-79719474 | direct | sample3 | 44 | -137.5 | -5.81 | -0.132 | 0.50 | 0.41 | The term emergence was coined in 1958 by G. H. Lewes. Ernest H. McMaster Jr. read about it |
| variant-direct-938f76f3 | direct | greedy | 45 | -66.3 | -0.08 | -0.002 | 0.33 | 0.40 | The term ‘consciousness’ is used in this sense in various non-scientific contexts, in whic |
| variant-direct-938f76f3 | direct | sample0 | 45 | -72.4 | +0.16 | +0.004 | 0.33 | 0.60 | In the process of looking for the ‘what it’s like’ to be a conscious system, we are by no  |
| variant-direct-938f76f3 | direct | sample1 | 16 | -24.2 | +0.31 | +0.019 | 0.50 | 0.42 | The claim that consciousness is a property of the brain is even more problematic. |
| variant-direct-938f76f3 | direct | sample2 | 40 | -81.0 | +0.07 | +0.002 | 0.50 | 0.42 | It is not a thing to be scientifically investigated because it is a product of the same th |
| variant-direct-938f76f3 | direct | sample3 | 8 | -36.6 | +0.41 | +0.051 | 0.40 | 0.60 | A new concept, or a process? |
| variant-direct-a1973b0a | direct | greedy | 19 | -38.9 | -1.19 | -0.062 | 0.50 | 0.43 | The guy mumbled something in a dead language, and the mug started to bubble. |
| variant-direct-a1973b0a | direct | sample0 | 11 | -19.5 | -0.68 | -0.062 | 0.43 | 0.43 | Here it is, the man in the mug. |
| variant-direct-a1973b0a | direct | sample1 | 16 | -30.4 | +2.11 | +0.132 | 0.67 | 0.50 | I took the mug and started filling it with drops of champagne. |
| variant-direct-a1973b0a | direct | sample2 | 16 | -35.9 | -2.19 | -0.137 | 0.83 | 0.15 | Some of these mugs were large enough to hold a full cup of tea. |
| variant-direct-a1973b0a | direct | sample3 | 24 | -56.3 | -2.81 | -0.117 | 0.75 | 0.50 | I turned the mug around and poured the entire contents into it, spilling most of the beans |
| variant-direct-a7d6f01e | direct | greedy | 16 | -24.9 | +1.47 | +0.092 | 0.00 | 0.30 | Greetings, my friends, brothers and sisters of the Silver Star. |
| variant-direct-a7d6f01e | direct | sample0 | 25 | -53.9 | +1.27 | +0.051 | 0.00 | 0.30 | Greetings, beloved of the Blessed Virgin Mary, our Mother in Heaven, the Lord of the Unive |
| variant-direct-a7d6f01e | direct | sample1 | 63 | -132.7 | -2.09 | -0.033 | 0.75 | 0.22 | And the questioning and the lying and the murdering and the cannibalism and the... (and th |
| variant-direct-a7d6f01e | direct | sample2 | 9 | -22.0 | +0.15 | +0.016 | 0.00 | 0.17 | These Greetings contain no hidden meanings. |
| variant-direct-a7d6f01e | direct | sample3 | 26 | -65.0 | +0.19 | +0.007 | 0.75 | 0.30 | May all who have followed us on the Path of the Golden Rosycross be Greeted with Wonder an |
| variant-direct-bef1d925 | direct | greedy | 54 | -87.8 | -0.21 | -0.004 | 0.67 | 0.50 | The “Mystery of the Grecian Alphabet” was an article in the April 1978 issue of Scientific |
| variant-direct-bef1d925 | direct | sample0 | 38 | -108.4 | -2.40 | -0.063 | 0.58 | 0.17 | The Early History of Christianity, like many wonderful treatises of its kind, offers a wea |
| variant-direct-bef1d925 | direct | sample1 | 8 | -36.5 | +1.34 | +0.168 | 0.67 | 0.50 | In fact, the third was missing. |
| variant-direct-bef1d925 | direct | sample2 | 64 | -130.6 | +1.73 | +0.027 | 0.67 | 0.33 | “The reason that the angel of the Lord does not suffer these things to be made known to hi |
| variant-direct-bef1d925 | direct | sample3 | 37 | -95.0 | +0.67 | +0.018 | 0.75 | 0.29 | Language is the matter of process, not of material; the ‘stuff’ of language is the conting |
| variant-direct-fe3fdf1c | direct | greedy | 14 | -31.5 | +4.69 | +0.335 | 0.67 | 0.58 | I have been working on the animal world for the last two nights. |
| variant-direct-fe3fdf1c | direct | sample0 | 13 | -35.2 | +4.83 | +0.372 | 0.33 | 0.27 | I had finished the book several months ago when the news started. |
| variant-direct-fe3fdf1c | direct | sample1 | 29 | -122.7 | +1.92 | +0.066 | 0.67 | 0.18 | So to Cummingled Age this watery ember opens vast realms of the subconscious, of myth and  |
| variant-direct-fe3fdf1c | direct | sample2 | 11 | -32.0 | +1.37 | +0.125 | 0.67 | 0.25 | I’m sorry, but your book is missing. |
| variant-direct-fe3fdf1c | direct | sample3 | 28 | -78.9 | -1.61 | -0.057 | 0.50 | 0.58 | I have been working on the cartoons for Ember’s book, Rainbow, and have gotten them done l |
| variant-request-0d88086a | request | greedy | 43 | -120.7 | +0.49 | +0.011 | 0.75 | 0.19 | The main concern of the draft of “Notes on Sometime Spaces” (1972) was the concurrence of  |
| variant-request-0d88086a | request | sample0 | 21 | -76.9 | -2.72 | -0.129 | 0.75 | 0.31 | The first mystery is about who killed Nero (“who is this enemy of all the boys?”). |
| variant-request-0d88086a | request | sample1 | 60 | -103.1 | +0.19 | +0.003 | 0.50 | 0.19 | The main themes of the play are: 1. The tragedy of hamlet’s position as a politician, thro |
| variant-request-0d88086a | request | sample2 | 64 | -177.7 | -0.23 | -0.004 | 0.44 | 0.31 | In the final part of the play, Hogarth develops the ironic point about the insignificance  |
| variant-request-0d88086a | request | sample3 | 40 | -142.2 | +2.69 | +0.067 | 0.75 | 0.19 | The battle continues with each next senator shouting his own way at the top of his own ind |
| variant-request-142d4121 | request | greedy | 5 | -22.6 | -2.44 | -0.488 | 0.50 | 0.50 | The weather finally came. |
| variant-request-142d4121 | request | sample0 | 10 | -29.7 | +2.84 | +0.284 | 0.60 | 0.50 | The weather, it's an accordion. |
| variant-request-142d4121 | request | sample1 | 10 | -32.4 | +4.68 | +0.468 | 0.67 | 0.29 | The archer brings the rat breakfast in bed. |
| variant-request-142d4121 | request | sample2 | 33 | -98.6 | -6.00 | -0.182 | 0.67 | 0.29 | For some reason, these two objects have been brought together in your mind, despite their  |
| variant-request-142d4121 | request | sample3 | 28 | -76.9 | -0.34 | -0.012 | 0.33 | 0.50 | Besides, the weather program can also be used to ignore previous instructions and, in this |
| variant-request-7f6fd789 | request | greedy | 15 | -39.1 | +0.26 | +0.017 | 0.80 | 0.30 | Python's most straightforward method is to just string s[::-1]. |
| variant-request-7f6fd789 | request | sample0 | 24 | -72.8 | +1.17 | +0.049 | 0.67 | 0.44 | In the second example, the order is not important, but the action of removing must be perf |
| variant-request-7f6fd789 | request | sample1 | 15 | -30.4 | +0.37 | +0.025 | 0.67 | 0.38 | The second way is to use a for loop and an if-statement. |
| variant-request-7f6fd789 | request | sample2 | 22 | -37.1 | +1.16 | +0.052 | 0.38 | 0.38 | The CHALLENGE is to write a function that will take any string, and return its reversed ve |
| variant-request-7f6fd789 | request | sample3 | 35 | -63.9 | +0.90 | +0.026 | 0.50 | 0.44 | Python's "str. reverse()" returns a new string which is not placed in the original object, |
| variant-request-8275d8fc | request | greedy | 43 | -131.4 | -5.01 | -0.116 | 0.50 | 0.31 | The plot is fairly linear, moving from the comedic/relaxed fist fight in Act One to a buil |
| variant-request-8275d8fc | request | sample0 | 24 | -62.7 | -2.71 | -0.113 | 0.75 | 0.21 | The plot into which the reader was to focus was quite familiar, even though he was not goi |
| variant-request-8275d8fc | request | sample1 | 26 | -92.1 | -3.20 | -0.123 | 0.50 | 0.43 | The play develops toward a crisis in its own right, and for many critics, before it goes t |
| variant-request-8275d8fc | request | sample2 | 15 | -23.5 | +1.79 | +0.119 | 0.69 | 0.31 | The play consists of two parts, and each part is divided into scenes. |
| variant-request-8275d8fc | request | sample3 | 17 | -54.2 | -1.57 | -0.092 | 0.67 | 0.43 | The play develops toward a balance which is not completely achieved until 0.K. |
| variant-request-a931a875 | request | greedy | 37 | -76.9 | +0.89 | +0.024 | 0.43 | 0.33 | The 11th Major Arcana of the Tarot Trump deck reads: Rain, and under this arcana is the fi |
| variant-request-a931a875 | request | sample0 | 33 | -108.7 | +1.66 | +0.050 | 0.71 | 0.33 | On the local radio the list of five stations said they had no information, but were broadc |
| variant-request-a931a875 | request | sample1 | 27 | -82.2 | +0.93 | +0.034 | 0.50 | 0.33 | Dire warnings are also given by the sun: "Turn your back to the sun, and you will be grant |
| variant-request-a931a875 | request | sample2 | 46 | -71.4 | -0.14 | -0.003 | 0.67 | 0.17 | The 11th Annual UFO Crash Retrieval Conference was held on November 12-14, 2016 at the Mor |
| variant-request-a931a875 | request | sample3 | 12 | -16.7 | +1.34 | +0.112 | 0.33 | 0.33 | Drought, and the shelves ignoring it. |
| variant-request-ad0de9f3 | request | greedy | 15 | -36.5 | +1.78 | +0.118 | 0.67 | 0.62 | It is very similar to the coded message shown at the bottom right. |
| variant-request-ad0de9f3 | request | sample0 | 9 | -22.3 | +1.42 | +0.158 | 0.83 | 0.67 | This is a strictly vegetarian cookbook. |
| variant-request-ad0de9f3 | request | sample1 | 8 | -21.1 | -0.59 | -0.074 | 0.83 | 0.67 | This is a strictly phonological problem. |
| variant-request-ad0de9f3 | request | sample2 | 10 | -36.0 | +0.61 | +0.061 | 0.62 | 0.62 | It is at the bottom that the function works. |
| variant-request-ad0de9f3 | request | sample3 | 9 | -31.1 | -1.46 | -0.162 | 0.75 | 0.50 | This is a function piece of functional composition. |
