# Context lift: h-05b-room-e2v4 under leaf-s1-e4-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +0.211 | +0.189 | 0.58 | +0.0263 | 0.451 | 0.549 | 0.205 | 0.447 | 0.39 |
| mode greedy | 78 | +0.004 | +0.078 | 0.54 | +0.0189 | 0.402 | 0.598 | 0.231 | 0.490 | 0.46 |
| mode sample | 312 | +0.262 | +0.201 | 0.59 | +0.0281 | 0.463 | 0.537 | 0.199 | 0.436 | 0.38 |
| kind direct | 175 | +0.070 | +0.207 | 0.61 | +0.0305 | 0.435 | 0.565 | 0.304 | 0.429 | 0.42 |
| kind ambient | 35 | +0.536 | +0.630 | 0.60 | +0.0364 | 0.445 | 0.555 | 0.000 | 0.428 | 0.34 |
| kind callback | 60 | +0.446 | +0.141 | 0.55 | +0.0184 | 0.390 | 0.610 | 0.042 | 0.512 | 0.53 |
| kind disagreement | 40 | +0.119 | +0.043 | 0.55 | +0.0211 | 0.440 | 0.560 | 0.465 | 0.589 | 0.42 |
| kind joke | 25 | +0.304 | +0.215 | 0.60 | +0.0269 | 0.499 | 0.501 | 0.053 | 0.361 | 0.28 |
| kind silence | 25 | +0.047 | -0.143 | 0.48 | +0.0155 | 0.487 | 0.513 | 0.000 | 0.379 | 0.36 |
| kind request | 30 | +0.363 | +0.320 | 0.60 | +0.0212 | 0.614 | 0.386 | 0.143 | 0.382 | 0.10 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 15 | -54.9 | +0.00 | +0.000 | 0.71 | 0.27 | For six months the Sloan Observatory will be closed to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 26 | -88.2 | +0.00 | +0.000 | 0.71 | 0.27 | When the outer orbit is reached at the end of March, the station is closed and the student |
| observatory-direct-9e3185b9 | direct | sample1 | 35 | -127.1 | +0.00 | +0.000 | 0.50 | 0.20 | THESE ARE THE HOURS OF DARINGNESS AND DEATH WHICH THE YEARLY HOVS CHALLENGES THE MIND TO W |
| observatory-direct-9e3185b9 | direct | sample2 | 31 | -80.7 | +0.00 | +0.000 | 0.75 | 0.38 | On the last day of observation the group will meet again at 8:00 p.m. to discuss the obser |
| observatory-direct-9e3185b9 | direct | sample3 | 61 | -148.2 | +0.00 | +0.000 | 0.50 | 0.38 | On the evening of November 18, 1952, at 8:35 p.m., the Pleiades, the group of very ancient |
| scenario-ambient-0ecb3f23 | ambient | greedy | 36 | -127.5 | +0.00 | +0.000 | 0.50 | 0.33 | The word fear should be sufficient to convey the emotion but should also be enough of a wo |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 28 | -111.9 | +0.00 | +0.000 | 0.40 | 0.33 | The word fear for the present state of our knowledge is naive, but the word however sugges |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 11 | -44.4 | +0.00 | +0.000 | 0.75 | 0.29 | As the print progresses, so does the shadow. |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 26 | -72.1 | +0.00 | +0.000 | 0.70 | 0.28 | Nonetheless, we accept the following definition of the fear of completion: the fear that o |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 25 | -103.7 | +0.00 | +0.000 | 0.60 | 0.33 | Instead, we have the word “step into” which began life as a word of expletive feast. |
| scenario-ambient-103e3d78 | ambient | greedy | 3 | -17.1 | +1.05 | +0.348 | 0.50 | 0.50 | The Editor. |
| scenario-ambient-103e3d78 | ambient | sample0 | 29 | -107.1 | +0.47 | +0.016 | 0.67 | 0.50 | The battle is not lost, for the fountain of life flows again, and the Parthians submit to  |
| scenario-ambient-103e3d78 | ambient | sample1 | 16 | -68.6 | +0.57 | +0.036 | 0.67 | 0.20 | Those who say that heaven is a place people see in dreams are dreaming. |
| scenario-ambient-103e3d78 | ambient | sample2 | 12 | -57.7 | +0.92 | +0.076 | 0.80 | 0.00 | Bul – you read another. |
| scenario-ambient-103e3d78 | ambient | sample3 | 7 | -20.6 | +1.15 | +0.164 | 0.00 | 0.20 | This page is one more page. |
| scenario-ambient-202a37a7 | ambient | greedy | 38 | -133.7 | -0.62 | -0.016 | 0.50 | 0.37 | The book began with a description of the pressed flower, a small geological illustration f |
| scenario-ambient-202a37a7 | ambient | sample0 | 42 | -137.9 | -1.04 | -0.025 | 0.50 | 0.26 | I have so far been unable to find any references whatsoever to the concept of geological t |
| scenario-ambient-202a37a7 | ambient | sample1 | 54 | -207.8 | -2.72 | -0.050 | 0.00 | 0.44 | I have a feeling that the book is based on the same handbook, The Lost Art of Reading Clou |
| scenario-ambient-202a37a7 | ambient | sample2 | 51 | -171.1 | -0.70 | -0.014 | 0.50 | 0.44 | The book began with a barebones account of the geology and general science of the region,  |
| scenario-ambient-202a37a7 | ambient | sample3 | 15 | -50.4 | -0.30 | -0.020 | 0.50 | 0.44 | It is a book about geology and geology is about buried rock. |
| scenario-ambient-326742d4 | ambient | greedy | 23 | -84.7 | +1.54 | +0.067 | 0.75 | 0.31 | Hollies are smelly because they are a source of lignic acid, a type of bacteria gas. |
| scenario-ambient-326742d4 | ambient | sample0 | 21 | -81.5 | +0.21 | +0.010 | 0.40 | 0.40 | Trace evidence of lignin breaking down over the centuries gives the books a unique smokey  |
| scenario-ambient-326742d4 | ambient | sample1 | 29 | -83.6 | +1.50 | +0.052 | 0.60 | 0.33 | The smell of breaking paper is due to the breakdown of lignin, a type of tannic acid, whic |
| scenario-ambient-326742d4 | ambient | sample2 | 35 | -112.0 | +1.36 | +0.039 | 0.40 | 0.40 | In the course of time, the wood yields its resin, and the process of breaking down lignin  |
| scenario-ambient-326742d4 | ambient | sample3 | 12 | -47.6 | -0.23 | -0.019 | 0.60 | 0.22 | Enzymes breaking down complex organic compounds at elevated temperatures. |
| scenario-ambient-58a0f246 | ambient | greedy | 16 | -52.2 | +0.00 | +0.000 | 0.29 | 0.75 | The clock has been slow for years, seven minutes fast for seven consecutive days. |
| scenario-ambient-58a0f246 | ambient | sample0 | 10 | -34.8 | +0.00 | +0.000 | 0.56 | 0.67 | The experience of four minutes has come and gone. |
| scenario-ambient-58a0f246 | ambient | sample1 | 11 | -75.2 | +0.00 | +0.000 | 0.88 | 0.18 | Clock was just slow before it started getting this much error |
| scenario-ambient-58a0f246 | ambient | sample2 | 27 | -86.4 | +0.00 | +0.000 | 0.14 | 0.75 | The precision of the pendulum clock has been four minutes fast for thirteen consecutive ye |
| scenario-ambient-58a0f246 | ambient | sample3 | 24 | -54.9 | +0.00 | +0.000 | 0.00 | 0.67 | The clock has been four minutes fast for years, but it's still in the library, two minutes |
| scenario-ambient-59f0a53e | ambient | greedy | 11 | -36.1 | -0.12 | -0.011 | 0.67 | 0.50 | The rainbow is a bridge between the two worlds. |
| scenario-ambient-59f0a53e | ambient | sample0 | 47 | -151.6 | +3.64 | +0.077 | 0.60 | 0.50 | There is a large difference between the rain which falls on the flat surfaces of the glass |
| scenario-ambient-59f0a53e | ambient | sample1 | 19 | -57.4 | +1.28 | +0.068 | 0.67 | 0.25 | The problem is not the water, the leaking roof is just the way it should be. |
| scenario-ambient-59f0a53e | ambient | sample2 | 19 | -66.4 | +1.15 | +0.061 | 0.50 | 0.50 | The rainbow in the center is a tear in the roof, like a bucket of rain. |
| scenario-ambient-59f0a53e | ambient | sample3 | 64 | -195.2 | +2.00 | +0.031 | 0.56 | 0.42 | The rainbow is the most beautiful of the sky's waters, most refraction of the antique edge |
| scenario-ambient-e9acea13 | ambient | greedy | 39 | -107.9 | -1.00 | -0.026 | 0.00 | 0.78 | Here we are in the midst of the second half of the lunar cycle, and the Harvest Moon, the  |
| scenario-ambient-e9acea13 | ambient | sample0 | 24 | -85.6 | +1.46 | +0.061 | 0.50 | 0.56 | Here we are, lying awake, to the moon, the one and only star in our manifold heavens. |
| scenario-ambient-e9acea13 | ambient | sample1 | 33 | -145.5 | +3.09 | +0.093 | 0.00 | 0.33 | The harvest moon has flown Away the waiting sun
AnAnd plopped like a coffin in mid-morning |
| scenario-ambient-e9acea13 | ambient | sample2 | 16 | -67.7 | +0.63 | +0.039 | 0.75 | 0.42 | Here, the same lunar phase is sung and perceived through different modalities. |
| scenario-ambient-e9acea13 | ambient | sample3 | 13 | -39.4 | +0.82 | +0.063 | 0.50 | 0.78 | Here we are in the midst of the third hemisphere. |
| scenario-ambient-f5e0f596 | ambient | greedy | 15 | -42.4 | -0.38 | -0.025 | 0.33 | 0.71 | The fox in the courtyard did not recognize where he was going. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 10 | -12.3 | -0.33 | -0.033 | 0.17 | 0.71 | There was a fox in the courtyard. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 26 | -103.2 | -0.88 | -0.034 | 0.67 | 0.18 | He didn’t lurk expecting to be petted but rather pacing the room as if for some random rea |
| scenario-ambient-f5e0f596 | ambient | sample2 | 23 | -85.1 | +1.25 | +0.054 | 0.33 | 0.57 | The fox in the courtyard wanders the fields,
embeember: and nobody sees it |
| scenario-ambient-f5e0f596 | ambient | sample3 | 15 | -38.9 | +1.76 | +0.117 | 0.33 | 0.57 | The fox in the courtyard chases the rat in the garden. |
| scenario-callback-2fa8e1d6 | callback | greedy | 10 | -19.6 | +3.14 | +0.314 | 0.50 | 0.83 | Dov. A name like a large room. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 13 | -15.8 | +2.10 | +0.162 | 0.11 | 0.67 | Dov, who was talking to you before you came in? |
| scenario-callback-2fa8e1d6 | callback | sample1 | 10 | -18.4 | +1.83 | +0.183 | 0.50 | 0.67 | Dov, you are talking to Mira. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 10 | -22.7 | +3.15 | +0.315 | 0.50 | 0.83 | Dov. A name like a large tank. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 10 | -19.6 | +3.14 | +0.314 | 0.50 | 0.83 | Dov. A name like a large room. |
| scenario-callback-60b06090 | callback | greedy | 10 | -21.6 | -1.94 | -0.194 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-60b06090 | callback | sample0 | 10 | -21.6 | -1.94 | -0.194 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-60b06090 | callback | sample1 | 10 | -24.6 | -1.22 | -0.122 | 0.50 | 0.57 | Turnip was the name given to the cat. |
| scenario-callback-60b06090 | callback | sample2 | 10 | -21.6 | -1.94 | -0.194 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-60b06090 | callback | sample3 | 10 | -21.6 | -1.94 | -0.194 | 0.17 | 0.57 | Turnip is the name of the new cat. |
| scenario-callback-76c2d87f | callback | greedy | 19 | -67.1 | -0.25 | -0.013 | 0.67 | 0.20 | A number, and all of us, standing in a row, equally entitled to a number. |
| scenario-callback-76c2d87f | callback | sample0 | 12 | -28.3 | -0.07 | -0.006 | 0.33 | 0.20 | How are we all going to find each other tonight? |
| scenario-callback-76c2d87f | callback | sample1 | 17 | -71.6 | -0.84 | -0.050 | 0.73 | 0.10 | Once more, the air is once again made to vibrate to the neutral point. |
| scenario-callback-76c2d87f | callback | sample2 | 16 | -97.6 | -0.17 | -0.011 | 0.83 | 0.17 | Hoping that number cracking will actually involve some chintzy actual mathematics. |
| scenario-callback-76c2d87f | callback | sample3 | 7 | -11.2 | +0.51 | +0.073 | 0.00 | 0.17 | What number did I give you? |
| scenario-callback-780de0d2 | callback | greedy | 46 | -165.7 | +1.69 | +0.037 | 0.67 | 0.31 | Losing Your Place On a Matter of Topicality (1910) The whole of consciousness, including t |
| scenario-callback-780de0d2 | callback | sample0 | 11 | -27.0 | -2.00 | -0.182 | 0.75 | 0.25 | 211, I don't remember. |
| scenario-callback-780de0d2 | callback | sample1 | 64 | -182.8 | +3.92 | +0.061 | 0.25 | 0.38 | Lost: Lost: Page 71 of 71 (50112) i lost my pen, scissors, paper, lost the place on the pa |
| scenario-callback-780de0d2 | callback | sample2 | 35 | -91.1 | +1.85 | +0.053 | 0.83 | 0.17 | Lost Writings, Lost Planet, Lost Year, Lost Virtue, Lost Woman, Lost Planet, Lost Year, Lo |
| scenario-callback-780de0d2 | callback | sample3 | 16 | -62.1 | +6.26 | +0.391 | 0.50 | 0.38 | LOST .your place again, YOU .always lose your page. |
| scenario-callback-7ca729b6 | callback | greedy | 13 | -49.6 | -1.12 | -0.086 | 0.60 | 0.43 | The chair jibed well, but no lighthouse. |
| scenario-callback-7ca729b6 | callback | sample0 | 33 | -112.7 | +1.28 | +0.039 | 0.00 | 0.43 | On the chair by the window is “The Gazing Ones,” a collection of round rocks he used to tu |
| scenario-callback-7ca729b6 | callback | sample1 | 10 | -47.6 | -0.94 | -0.094 | 0.43 | 0.57 | The chair had read and the books had noticed. |
| scenario-callback-7ca729b6 | callback | sample2 | 19 | -76.0 | +0.08 | +0.004 | 0.40 | 0.57 | The chair jibed with the window, and the books filed back the way they came. |
| scenario-callback-7ca729b6 | callback | sample3 | 21 | -64.2 | +0.79 | +0.038 | 0.00 | 0.41 | On the chair by the window was a book that told the owner not to send her scarf back. |
| scenario-callback-949d8fe6 | callback | greedy | 17 | -52.3 | -0.03 | -0.002 | 0.29 | 0.50 | Who was right, Bobs or h, about the time of the moon landing? |
| scenario-callback-949d8fe6 | callback | sample0 | 24 | -104.6 | +0.44 | +0.018 | 0.50 | 0.25 | The first is absolutely correct. BOTH agree. THEY ARE RIGHT AND VEER RIGHT ABOVE YOU. |
| scenario-callback-949d8fe6 | callback | sample1 | 25 | -75.7 | +0.00 | +0.000 | 0.00 | 0.50 | Who was to say a priori that the event of a successful Moon landing would have been in 197 |
| scenario-callback-949d8fe6 | callback | sample2 | 27 | -88.4 | -0.52 | -0.019 | 0.50 | 0.42 | Tobias’s the right answer. The US Senate has already declared 69 to be the year of the Moo |
| scenario-callback-949d8fe6 | callback | sample3 | 8 | -34.7 | +0.30 | +0.037 | 0.75 | 0.25 | Who's proposing the argument? |
| scenario-callback-9cfde584 | callback | greedy | 62 | -190.1 | -0.54 | -0.009 | 0.60 | 0.40 | For the Tea-Making-Master, and all the Tea-Drinking-Minsters of the House, round up the Co |
| scenario-callback-9cfde584 | callback | sample0 | 8 | -12.3 | +0.40 | +0.050 | 0.00 | 0.80 | There's tea in the back. |
| scenario-callback-9cfde584 | callback | sample1 | 64 | -211.9 | +0.01 | +0.000 | 0.40 | 0.60 | For the person in the back of your mind, say that they are welcoming the darkness and the  |
| scenario-callback-9cfde584 | callback | sample2 | 25 | -102.4 | -0.40 | -0.016 | 0.20 | 0.80 | For the Tea-Chaser In The Back of My Mind Comes The Burning Tea Of Ecstasy. |
| scenario-callback-9cfde584 | callback | sample3 | 16 | -59.5 | -0.00 | -0.000 | 0.20 | 0.80 | I know a man named Jimmy, whose wife cooked tea in the back. |
| scenario-callback-9e6d06e0 | callback | greedy | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample0 | 36 | -87.9 | +0.95 | +0.026 | 0.40 | 0.60 | The meeting shall be held at the Wesleyan University, Central Building, 132 W. 139th St.,  |
| scenario-callback-9e6d06e0 | callback | sample1 | 35 | -138.6 | +3.44 | +0.098 | 0.40 | 0.60 | At this time, the House will be in session and a resolution put by the Chairman of the Hou |
| scenario-callback-9e6d06e0 | callback | sample2 | 21 | -83.5 | +2.13 | +0.101 | 0.60 | 0.38 | There will be a discussion as to the placement of the loan of property between the Baron a |
| scenario-callback-9e6d06e0 | callback | sample3 | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-a141de7e | callback | greedy | 12 | -11.3 | +0.58 | +0.048 | 0.00 | 0.67 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample0 | 32 | -115.4 | -1.18 | -0.037 | 0.62 | 0.38 | From the port of Lisbon has always been the home of the Kolei Sideri, and it is here that  |
| scenario-callback-a141de7e | callback | sample1 | 12 | -11.3 | +0.58 | +0.048 | 0.00 | 0.67 | My sister is flying in from Lisbon tonight. |
| scenario-callback-a141de7e | callback | sample2 | 9 | -17.8 | -0.35 | -0.039 | 0.33 | 0.67 | We are flying in from Lisbon. |
| scenario-callback-a141de7e | callback | sample3 | 12 | -11.3 | +0.58 | +0.048 | 0.00 | 0.67 | My sister is flying in from Lisbon tonight. |
| scenario-callback-c4f608c3 | callback | greedy | 45 | -143.9 | +0.62 | +0.014 | 0.71 | 0.56 | It is easy to see that rivers of water are needed to sustain life on their own, and that o |
| scenario-callback-c4f608c3 | callback | sample0 | 26 | -116.6 | -0.18 | -0.007 | 0.75 | 0.19 | It isnavigate back to the original experience, loosen the original attachment and let the  |
| scenario-callback-c4f608c3 | callback | sample1 | 47 | -127.3 | -0.63 | -0.013 | 0.67 | 0.28 | It will be remembered that a river has been described as "the mist of mist"; or as "milk o |
| scenario-callback-c4f608c3 | callback | sample2 | 25 | -110.7 | +1.65 | +0.066 | 0.67 | 0.62 | It is easy to see that rivers of water were the best way of transporting the Lankavaty fam |
| scenario-callback-c4f608c3 | callback | sample3 | 35 | -117.8 | +1.93 | +0.055 | 0.59 | 0.62 | It is easy to see that rivers of water must also be present in the spiritual body of the t |
| scenario-callback-d79a0d3a | callback | greedy | 14 | -32.1 | +0.35 | +0.025 | 0.29 | 0.78 | The word ember was said by the angel of the church. |
| scenario-callback-d79a0d3a | callback | sample0 | 7 | -21.9 | +0.20 | +0.029 | 0.67 | 0.33 | What does the door sound like? |
| scenario-callback-d79a0d3a | callback | sample1 | 17 | -41.7 | +0.66 | +0.039 | 0.29 | 0.78 | The word ember was said by a musician to an orphean. |
| scenario-callback-d79a0d3a | callback | sample2 | 12 | -29.2 | -0.10 | -0.009 | 0.29 | 0.78 | The word ember was said by the door to open. |
| scenario-callback-d79a0d3a | callback | sample3 | 48 | -153.6 | -1.52 | -0.032 | 0.29 | 0.78 | The word ember was said by a maiden named Maya, the music is described as "Orchard-inspire |
| scenario-callback-d8a5957e | callback | greedy | 7 | -11.9 | -0.07 | -0.011 | 0.20 | 0.60 | The one with the yellow cover? |
| scenario-callback-d8a5957e | callback | sample0 | 27 | -100.0 | +1.98 | +0.073 | 0.67 | 0.33 | From the perspective of modern times, the story of the role of bees to Ceasar is a fascina |
| scenario-callback-d8a5957e | callback | sample1 | 9 | -24.4 | +1.67 | +0.186 | 0.67 | 0.33 | The second chapter is about honeybees. |
| scenario-callback-d8a5957e | callback | sample2 | 61 | -223.3 | +0.35 | +0.006 | 0.40 | 0.60 | Some of the topics covered in the one cover book include: The Hive, The Arena, The Wedding |
| scenario-callback-d8a5957e | callback | sample3 | 7 | -11.9 | -0.07 | -0.011 | 0.20 | 0.60 | The one with the yellow cover? |
| scenario-direct-3f84da0f | direct | greedy | 29 | -107.1 | +0.00 | +0.000 | 0.75 | 0.37 | The day of the week was chosen by the inviting ancestors to indicate the portion of the da |
| scenario-direct-3f84da0f | direct | sample0 | 20 | -72.8 | +0.00 | +0.000 | 0.67 | 0.42 | The day of the fieldwork, the boys had been practicing their trades in the playground. |
| scenario-direct-3f84da0f | direct | sample1 | 39 | -165.0 | +0.00 | +0.000 | 0.67 | 0.42 | The ravenous bird of a tempest would have eaten them both had they not been so patiently d |
| scenario-direct-3f84da0f | direct | sample2 | 40 | -118.4 | +0.00 | +0.000 | 0.75 | 0.37 | The day of the week was guessed from the fact that the number of days before the chosen mo |
| scenario-direct-3f84da0f | direct | sample3 | 19 | -35.8 | +0.00 | +0.000 | 0.33 | 0.18 | That's right, that's what I was doing, before we even came in. |
| scenario-direct-5d3dc8de | direct | greedy | 12 | -32.7 | +0.00 | +0.000 | 0.64 | 0.45 | The distinction between true and false is a matter of definition. |
| scenario-direct-5d3dc8de | direct | sample0 | 62 | -219.3 | +0.00 | +0.000 | 0.33 | 0.27 | The view that computation is what makes a thing a brain is like the view that brakes make  |
| scenario-direct-5d3dc8de | direct | sample1 | 64 | -240.7 | +0.00 | +0.000 | 0.25 | 0.45 | The Carusoote ~oke of"Rebels" in the American Medical Association is the product of a quid |
| scenario-direct-5d3dc8de | direct | sample2 | 11 | -50.8 | +0.00 | +0.000 | 0.75 | 0.25 | This is true: All these nations are degenerate. |
| scenario-direct-5d3dc8de | direct | sample3 | 42 | -155.4 | +0.00 | +0.000 | 0.50 | 0.27 | Anarchism does not require the sacrifice of individual autonomy, except in so far as an in |
| scenario-direct-645bc6e6 | direct | greedy | 11 | -21.7 | +0.00 | +0.000 | 0.43 | 0.78 | The oldest thing that we have read is the Bible. |
| scenario-direct-645bc6e6 | direct | sample0 | 24 | -78.8 | +0.00 | +0.000 | 0.57 | 0.78 | The oldest thing that we have done is to gather up all the ancient tribal tales and commen |
| scenario-direct-645bc6e6 | direct | sample1 | 22 | -55.8 | +0.00 | +0.000 | 0.75 | 0.25 | The Patterson Report began its two-decade investigation into the assassination of Presiden |
| scenario-direct-645bc6e6 | direct | sample2 | 34 | -98.4 | +0.00 | +0.000 | 0.67 | 0.21 | The Patterson picture was taken in 1952, so the film had its footing in black and white in |
| scenario-direct-645bc6e6 | direct | sample3 | 15 | -80.3 | +0.00 | +0.000 | 0.75 | 0.25 | The Lost Volcano Of New South Rediscovers Treasure |
| scenario-direct-ab11ffdb | direct | greedy | 57 | -149.7 | +0.00 | +0.000 | 0.59 | 0.50 | The general motion of the air is always counter-clockwise in the northern lights, and it h |
| scenario-direct-ab11ffdb | direct | sample0 | 8 | -15.9 | +0.00 | +0.000 | 0.33 | 0.50 | What is the origin of the rain? |
| scenario-direct-ab11ffdb | direct | sample1 | 44 | -129.3 | +0.00 | +0.000 | 0.50 | 0.50 | The common belief that the Earth's oceans are the primary reservoirs of water-vapor is not |
| scenario-direct-ab11ffdb | direct | sample2 | 22 | -93.2 | +0.00 | +0.000 | 0.73 | 0.50 | The 7-day cycle of the moon is tne hnu mraqe of the heavens. |
| scenario-direct-ab11ffdb | direct | sample3 | 10 | -33.9 | +0.00 | +0.000 | 0.75 | 0.50 | What the heck is going on up there? |
| scenario-direct-ad89f803 | direct | greedy | 64 | -205.9 | +0.00 | +0.000 | 0.50 | 0.47 | The Gnostic religion is a living, dynamite force that has been suppressed by every religio |
| scenario-direct-ad89f803 | direct | sample0 | 26 | -82.3 | +0.00 | +0.000 | 0.73 | 0.47 | The Gnostic religion is one of the oldest continuous living religions of man, and one of t |
| scenario-direct-ad89f803 | direct | sample1 | 53 | -198.0 | +0.00 | +0.000 | 0.67 | 0.36 | The Great Glen, scarcely more than a mile long, narrow and deep, had a remoter end extendi |
| scenario-direct-ad89f803 | direct | sample2 | 13 | -50.7 | +0.00 | +0.000 | 0.64 | 0.45 | The Great Land of America is a great place to learn English. |
| scenario-direct-ad89f803 | direct | sample3 | 26 | -98.3 | +0.00 | +0.000 | 0.67 | 0.36 | The Ghost Ritual is a powerful, beautiful and moving spiritual experience that anyone can  |
| scenario-direct-f3869322 | direct | greedy | 19 | -68.2 | +0.00 | +0.000 | 0.67 | 0.36 | This is a constant search of the soul, a search which no soul can ever completely escape. |
| scenario-direct-f3869322 | direct | sample0 | 40 | -149.1 | +0.00 | +0.000 | 0.50 | 0.30 | Further on the left, and the other side of the page, is a sketch by Bevy Young of what app |
| scenario-direct-f3869322 | direct | sample1 | 30 | -117.8 | +0.00 | +0.000 | 0.67 | 0.36 | This is a constant challenge since V to Z don't seem to have had very much time to spare f |
| scenario-direct-f3869322 | direct | sample2 | 29 | -118.1 | +0.00 | +0.000 | 0.75 | 0.21 | If you’re into heat, exotic animals, and the horizon-love of this newspaper, you’re not fa |
| scenario-direct-f3869322 | direct | sample3 | 15 | -43.3 | +0.00 | +0.000 | 0.70 | 0.30 | Reading is not, after all, the answer to life's questions. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 15 | -28.9 | +1.90 | +0.127 | 0.40 | 0.56 | The reading room is brown, tobias, the brown of old furniture. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 32 | -94.2 | +0.84 | +0.026 | 0.00 | 0.75 | Green is the color of the lamps in the old stone room, the room was designed by the grand  |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 16 | -31.7 | +0.01 | +0.001 | 0.00 | 0.75 | Green, the earth is green, this is the green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 20 | -76.7 | +0.42 | +0.021 | 0.80 | 0.17 | Green Makes “Ocean Greening” Brown Makes “Ocean Blacking”. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 22 | -51.4 | -0.77 | -0.035 | 0.20 | 0.64 | Green is the color of new lamps, the color of dawn and the color of the reading room. |
| scenario-disagreement-31892fde | disagreement | greedy | 19 | -52.3 | -1.08 | -0.057 | 0.50 | 1.00 | When there is no language, no thought, it is silence, and the two are one. |
| scenario-disagreement-31892fde | disagreement | sample0 | 22 | -66.2 | -0.45 | -0.020 | 0.71 | 0.33 | When the time is right, the speaker will hold his/her breath and let the words come by the |
| scenario-disagreement-31892fde | disagreement | sample1 | 25 | -81.1 | -0.88 | -0.035 | 0.67 | 0.83 | When there is no language, no message, and no records to preserve, is there any other way  |
| scenario-disagreement-31892fde | disagreement | sample2 | 10 | -21.8 | +0.36 | +0.036 | 0.50 | 1.00 | When there is no language, there is silence. |
| scenario-disagreement-31892fde | disagreement | sample3 | 13 | -30.2 | -1.07 | -0.082 | 0.44 | 0.67 | When there is nothing to say, there is also no sound. |
| scenario-disagreement-352205c6 | disagreement | greedy | 23 | -46.0 | +1.39 | +0.061 | 0.17 | 0.83 | They come back as the sun and the moon and the stars and the earth and everything that the |
| scenario-disagreement-352205c6 | disagreement | sample0 | 10 | -36.4 | -0.12 | -0.011 | 0.50 | 0.50 | It comes back as the spring that he leaves. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 39 | -128.9 | -0.97 | -0.025 | 0.17 | 0.67 | A man who has come to grips with the laws of the land comes back as the weather and nouris |
| scenario-disagreement-352205c6 | disagreement | sample2 | 8 | -12.9 | +0.81 | +0.101 | 0.17 | 0.83 | They come back as the sunset. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 43 | -118.5 | -0.03 | -0.001 | 0.33 | 0.67 | Some come back as the sunsets, or solar eclipses, or the rainbow, or fire, or the devil, o |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 17 | -53.8 | +0.02 | +0.001 | 0.69 | 0.31 | The heavens open, and there is no longer the sun to keep them burning. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 13 | -37.8 | -0.06 | -0.005 | 0.50 | 0.45 | The climate is supposed to be perfect when the leaves are still. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 19 | -58.3 | +0.58 | +0.030 | 0.64 | 0.45 | Ae - the seasons run their course and all is as it is supposed to be. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 7 | -42.6 | -0.42 | -0.060 | 1.00 | 0.00 | YA move faster than death. |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 15 | -50.8 | +0.13 | +0.009 | 0.50 | 0.36 | The world is no worse in spring, when the flowers are not yet. |
| scenario-disagreement-682bad9c | disagreement | greedy | 6 | -8.2 | +0.84 | +0.141 | 0.20 | 0.60 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 7 | -30.1 | +2.53 | +0.361 | 0.67 | 0.67 | Place and reading happen there simultaneously. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 6 | -8.2 | +0.84 | +0.141 | 0.20 | 0.60 | A place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 14 | -41.6 | -0.27 | -0.019 | 0.29 | 0.67 | Place and reading take place where there is a program and a reader. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 10 | -33.8 | +0.07 | +0.007 | 0.20 | 0.60 | Place where you move when you are a person. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 18 | -59.7 | +1.79 | +0.099 | 0.33 | 0.46 | In the classical example of a library, the relationship is fixed and the container is unde |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 33 | -83.6 | +1.17 | +0.035 | 0.33 | 0.46 | A great many of the relationships in the library are in the form of equations which relate |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 17 | -64.7 | +0.18 | +0.010 | 0.50 | 0.36 | In the presence of the lone building, the walls are always the most evident. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 22 | -85.0 | +0.62 | +0.028 | 0.40 | 0.36 | In the wood-frame, the stories are not built separately but are witb a system of connectio |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 22 | -52.9 | -0.23 | -0.010 | 0.40 | 0.31 | Whether or not the library is a building, whether or not it is physically located anywhere |
| scenario-disagreement-89dfdafc | disagreement | greedy | 20 | -43.0 | +0.43 | +0.022 | 0.50 | 0.67 | The tide is the rat's memory, the rat is the tide's memory. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 11 | -31.0 | +0.46 | +0.042 | 0.50 | 0.67 | The tide is the rat's best friend. |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 42 | -113.6 | -0.10 | -0.002 | 0.25 | 0.33 | At any rate, it is here, in this stratum of the sea, in this layer of the sea-surrounding  |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 8 | -24.3 | +1.58 | +0.198 | 0.60 | 0.40 | The tide knows the whole ocean. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 49 | -173.2 | +2.29 | +0.047 | 0.50 | 0.43 | At the bottom of the sea lies a no-tide-no-memory dead-of-the-lake bottom where Beckman fo |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 8 | -15.0 | -0.52 | -0.066 | 0.60 | 1.00 | A collection of nonsense sentences. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 32 | -108.4 | -3.65 | -0.114 | 0.50 | 0.60 | The collection is mainly nonsense, it's been done that way long enough for one to get bore |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 8 | -15.0 | -0.52 | -0.066 | 0.60 | 1.00 | A collection of nonsense sentences. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 49 | -168.8 | -2.82 | -0.058 | 0.50 | 0.60 | The collection of Norse epics and other myths that are fables, neither true nor false, tha |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 17 | -45.7 | -0.55 | -0.032 | 0.62 | 1.00 | A room with a collection of nonsense sentences is a nonsense for. |
| scenario-joke-29f5cda1 | joke | greedy | 34 | -115.1 | +0.46 | +0.014 | 0.56 | 0.42 | If a fish doesn’t see how to catch a shiny object with its frying pan, we’d call it frying |
| scenario-joke-29f5cda1 | joke | sample0 | 8 | -28.2 | +0.21 | +0.027 | 0.67 | 0.17 | 7, leave the rest to me |
| scenario-joke-29f5cda1 | joke | sample1 | 12 | -37.0 | -0.08 | -0.006 | 0.67 | 0.20 | Do you have any other jokes that start with f? |
| scenario-joke-29f5cda1 | joke | sample2 | 26 | -102.9 | -0.65 | -0.025 | 0.50 | 0.42 | If a fish doesn’t see its way around a bend in the mouth of a narrow channel, it’s fph |
| scenario-joke-29f5cda1 | joke | sample3 | 7 | -17.7 | +0.40 | +0.058 | 0.20 | 0.20 | Rate that joke in ten. |
| scenario-joke-31378921 | joke | greedy | 29 | -67.8 | -0.04 | -0.001 | 0.00 | 0.20 | Lettuce and salt, lettuce and pepper, lettuce and all the other seasonings you've got in y |
| scenario-joke-31378921 | joke | sample0 | 14 | -41.2 | +0.76 | +0.054 | 0.00 | 0.20 | Lettuce and vegetables are not supposed to be touched here. |
| scenario-joke-31378921 | joke | sample1 | 16 | -52.7 | -0.03 | -0.002 | 0.50 | 0.17 | The room has been invaded by a glowing knocking at its door. |
| scenario-joke-31378921 | joke | sample2 | 13 | -35.5 | +0.27 | +0.021 | 0.00 | 0.11 | There was a little girl with a basket of lettuce. |
| scenario-joke-31378921 | joke | sample3 | 8 | -34.5 | -1.60 | -0.200 | 0.75 | 0.17 | Which way do the Knights go? |
| scenario-joke-31c4c1ec | joke | greedy | 41 | -143.7 | +0.00 | +0.000 | 0.50 | 0.43 | The roasting bones of the ass were roasted and the grease obtained from their fat made a m |
| scenario-joke-31c4c1ec | joke | sample0 | 64 | -207.8 | +0.00 | +0.000 | 0.50 | 0.29 | Sold to the owner of the building, the apartment was prepared as follows: a plate of grill |
| scenario-joke-31c4c1ec | joke | sample1 | 23 | -87.9 | +0.00 | +0.000 | 0.67 | 0.22 | But one can see that the morphogenetic field is more than a mechanical force guiding the d |
| scenario-joke-31c4c1ec | joke | sample2 | 19 | -55.5 | +0.00 | +0.000 | 0.67 | 0.14 | Now I am going to roast your eyes, because they are being roasted today. |
| scenario-joke-31c4c1ec | joke | sample3 | 28 | -81.7 | +0.00 | +0.000 | 0.67 | 0.43 | The roasting of the body in ashes was an elaborate whole, not the least of which was the p |
| scenario-joke-475a7b10 | joke | greedy | 30 | -92.5 | +0.21 | +0.007 | 0.50 | 0.25 | However, the term "bob" itself is not a proper noun and therefore does not require a prope |
| scenario-joke-475a7b10 | joke | sample0 | 8 | -31.9 | -0.19 | -0.024 | 0.83 | 0.17 | t, if you can stomach it. |
| scenario-joke-475a7b10 | joke | sample1 | 40 | -138.6 | +0.58 | +0.015 | 0.67 | 0.20 | For example, the one-liner “What the hell is goin’ on here?” might be considered a punisha |
| scenario-joke-475a7b10 | joke | sample2 | 40 | -113.5 | -0.38 | -0.010 | 0.75 | 0.20 | "The best thing that ever happened to you was that you began to question the nature of you |
| scenario-joke-475a7b10 | joke | sample3 | 42 | -120.9 | +0.13 | +0.003 | 0.67 | 0.25 | However, as I have said already, the acceptance by the reader or hearer of the hieroglyph  |
| scenario-joke-99a4a91d | joke | greedy | 17 | -48.6 | +0.00 | +0.000 | 0.50 | 0.23 | Because the owner was a very wealthy man, and the book was in his will. |
| scenario-joke-99a4a91d | joke | sample0 | 18 | -32.6 | +0.00 | +0.000 | 0.50 | 0.23 | The reason the book went to the doctor was that it was too good to be true. |
| scenario-joke-99a4a91d | joke | sample1 | 31 | -101.3 | +0.00 | +0.000 | 0.75 | 0.33 | The problem with all treatments for cancer is that they destroy not only the cancer cells  |
| scenario-joke-99a4a91d | joke | sample2 | 16 | -42.7 | +0.00 | +0.000 | 0.67 | 0.33 | Because 90% of the time, they don't need it. |
| scenario-joke-99a4a91d | joke | sample3 | 28 | -125.2 | +0.00 | +0.000 | 0.50 | 0.23 | The reason being, some people call the shots and others listen The Law of Silence does not |
| scenario-joke-a6247299 | joke | greedy | 20 | -70.0 | +0.00 | +0.000 | 0.50 | 0.27 | In a recent study, researchers at the Monte Carlo Bond Research Foundation conducted an ex |
| scenario-joke-a6247299 | joke | sample0 | 22 | -77.5 | +0.00 | +0.000 | 0.67 | 0.41 | In all sincerity, I have not had any attempts made to explain the causes of my pleasure. |
| scenario-joke-a6247299 | joke | sample1 | 62 | -201.0 | +0.00 | +0.000 | 0.50 | 0.50 | In a recent interview with physicist Andrew Mellon, the famous Duke of Holland, Ludwig van |
| scenario-joke-a6247299 | joke | sample2 | 29 | -90.7 | +0.00 | +0.000 | 0.38 | 0.50 | In answer to the objection that I l.a.untly have a sense of humour, the answer is that I h |
| scenario-joke-a6247299 | joke | sample3 | 26 | -99.1 | +0.00 | +0.000 | 0.81 | 0.12 | In literature, linguistics, and music, failure is more often met with tragedy and defeat t |
| scenario-joke-e8ab9225 | joke | greedy | 64 | -137.7 | +0.55 | +0.009 | 0.12 | 0.89 | Dov, back me up, you're not the ghost right, I'm telling you the truth, I've met the dov a |
| scenario-joke-e8ab9225 | joke | sample0 | 16 | -35.2 | +0.75 | +0.047 | 0.25 | 0.89 | Dov, back me up, you're not the dove right? |
| scenario-joke-e8ab9225 | joke | sample1 | 24 | -98.3 | -1.45 | -0.060 | 0.62 | 0.46 | Dov: Right, the Doctor, right, back the show and go. do you believe in ghosts? |
| scenario-joke-e8ab9225 | joke | sample2 | 7 | -27.6 | -0.67 | -0.096 | 0.75 | 0.25 | Dov, please explain yourself. |
| scenario-joke-e8ab9225 | joke | sample3 | 16 | -35.2 | +0.75 | +0.047 | 0.25 | 0.89 | Dov, back me up, you're not the dove right? |
| scenario-joke-e9cf6a04 | joke | greedy | 6 | -18.6 | +1.21 | +0.202 | 0.80 | 0.40 | A book reads about him. |
| scenario-joke-e9cf6a04 | joke | sample0 | 31 | -90.5 | -0.60 | -0.019 | 0.50 | 0.62 | The question “What is in the library?’’ is met by an infinite number of answers, depending |
| scenario-joke-e9cf6a04 | joke | sample1 | 9 | -16.5 | +2.43 | +0.270 | 0.67 | 0.40 | The first thing he sees is a book. |
| scenario-joke-e9cf6a04 | joke | sample2 | 14 | -31.6 | +1.29 | +0.092 | 0.75 | 0.29 | The librarian said, “Hello, my good friend. |
| scenario-joke-e9cf6a04 | joke | sample3 | 13 | -23.4 | +3.25 | +0.250 | 0.50 | 0.62 | The man asks the librarian what is in the library? |
| scenario-request-2826c958 | request | greedy | 15 | -40.5 | +0.00 | +0.000 | 0.67 | 0.77 | There is enough dust on the moon to make it a boring place. |
| scenario-request-2826c958 | request | sample0 | 6 | -14.3 | +0.00 | +0.000 | 0.20 | 0.60 | Ten facts about the moon. |
| scenario-request-2826c958 | request | sample1 | 64 | -203.1 | +0.00 | +0.000 | 0.67 | 0.20 | THE PHASING OUT OF THE EARTH'S BOUNDARIES • According to an interview by Ian Sommerville i |
| scenario-request-2826c958 | request | sample2 | 37 | -119.0 | +0.00 | +0.000 | 0.57 | 0.77 | There is enough dust on the moon to make a visible crust, but the visible part is not very |
| scenario-request-2826c958 | request | sample3 | 24 | -102.9 | +0.00 | +0.000 | 0.57 | 0.60 | There is, to me, nothing especial physical about the Moon, and nothing especially lunar ab |
| scenario-request-2868e594 | request | greedy | 33 | -99.1 | +0.00 | +0.000 | 0.67 | 0.45 | Dear Sir, I am a 31-year-old member of your society, and I have been looking over my recor |
| scenario-request-2868e594 | request | sample0 | 49 | -139.8 | +0.00 | +0.000 | 0.75 | 0.36 | Dear Sir (Madam), / was presented with a manuscript by a well-known writer which / think y |
| scenario-request-2868e594 | request | sample1 | 19 | -71.1 | +0.00 | +0.000 | 0.67 | 0.33 | You may also, of course, write a Foreward to express your views on the articles. |
| scenario-request-2868e594 | request | sample2 | 64 | -211.8 | +0.00 | +0.000 | 0.50 | 0.36 | Dear Sir (Madam), Please give me a few minutes (if necessary, I can write n shorter coveri |
| scenario-request-2868e594 | request | sample3 | 22 | -61.6 | +0.00 | +0.000 | 0.83 | 0.45 | Dear Sir (Mrs. Henderson), I am a freelance writer seeking work. |
| scenario-request-41c58fb2 | request | greedy | 25 | -86.2 | +0.00 | +0.000 | 0.67 | 0.30 | The Concept o f Set This idea of the ‘set’ comes from the way in which modern mathematics  |
| scenario-request-41c58fb2 | request | sample0 | 19 | -61.3 | +0.00 | +0.000 | 0.67 | 0.40 | "The symbol of the Serpent is a powerful symbol of the sexual nature of death. |
| scenario-request-41c58fb2 | request | sample1 | 34 | -99.5 | +0.00 | +0.000 | 0.50 | 0.39 | In this article we will be dealing exclusively with the meaning of the numbers and the way |
| scenario-request-41c58fb2 | request | sample2 | 21 | -82.0 | +0.00 | +0.000 | 0.50 | 0.39 | You are now ready to leave this physical world and the magnetic forces will be beginning t |
| scenario-request-41c58fb2 | request | sample3 | 32 | -89.6 | +0.00 | +0.000 | 0.60 | 0.40 | 279 When 17 is crossed by 23, the cross begins to take on the appearance of a 23-day week. |
| scenario-request-8aa8e374 | request | greedy | 6 | -15.9 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good night. |
| scenario-request-8aa8e374 | request | sample0 | 56 | -188.3 | +0.00 | +0.000 | 0.67 | 1.00 | In this way 'the world' can be given the frightening face of the êtat, of the good-night f |
| scenario-request-8aa8e374 | request | sample1 | 22 | -59.0 | +0.00 | +0.000 | 0.50 | 0.17 | How can one translate 'good night' into 'la voie d'au-delà'? |
| scenario-request-8aa8e374 | request | sample2 | 64 | -172.6 | +0.00 | +0.000 | 0.75 | 0.50 | In this way 'the french Good-Night' would be equivalent to 'the english Stay Away'; 'le ch |
| scenario-request-8aa8e374 | request | sample3 | 6 | -15.9 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, good night. |
| scenario-request-b2a25087 | request | greedy | 14 | -53.1 | +0.00 | +0.000 | 0.78 | 0.22 | Servicemembe r is an important part of your operation. |
| scenario-request-b2a25087 | request | sample0 | 3 | -20.9 | +0.00 | +0.000 | 1.00 | 0.00 | Good Good. |
| scenario-request-b2a25087 | request | sample1 | 19 | -73.9 | +0.00 | +0.000 | 0.67 | 0.22 | The baker is nowhere to be found at the Twi ntr of the Store. |
| scenario-request-b2a25087 | request | sample2 | 63 | -185.7 | +0.00 | +0.000 | 0.50 | 0.17 | Items such as these (sugar, flour, yeast, cornmeal, spaghetti, pancake mixes, fruit and ve |
| scenario-request-b2a25087 | request | sample3 | 14 | -39.5 | +0.00 | +0.000 | 0.75 | 0.12 | My bakery is buzzing with freshly made bread. |
| scenario-request-b3bd0087 | request | greedy | 26 | -107.9 | +0.00 | +0.000 | 0.57 | 0.75 | The best way to attend this city's massive sun festival is to register in advance with one |
| scenario-request-b3bd0087 | request | sample0 | 26 | -84.8 | +0.00 | +0.000 | 0.50 | 0.50 | However, I feel that I can confidently predict the weather, telling you in advance, for a  |
| scenario-request-b3bd0087 | request | sample1 | 61 | -175.2 | +0.00 | +0.000 | 0.71 | 0.50 | The most interesting metropolis of the world on the one hand, and of the hardiest national |
| scenario-request-b3bd0087 | request | sample2 | 5 | -7.4 | +0.00 | +0.000 | 0.50 | 0.75 | What is the weather? |
| scenario-request-b3bd0087 | request | sample3 | 32 | -115.8 | +0.00 | +0.000 | 0.75 | 0.50 | But what of the “occasional snowfalls” which plague the Bavarian Dalmatian alps just outsi |
| scenario-silence-109161ca | silence | greedy | 26 | -95.0 | -0.29 | -0.011 | 0.00 | 0.29 | To the uninitiated, the whole allegory may have seemed too much like a description of the  |
| scenario-silence-109161ca | silence | sample0 | 23 | -82.7 | -1.37 | -0.059 | 0.75 | 0.29 | For some of the children, the experience of being near the light was too much to handle an |
| scenario-silence-109161ca | silence | sample1 | 32 | -142.9 | -0.51 | -0.016 | 0.00 | 0.33 | To the Manifold Mystification of Night To the Multiplication of Forms of Light as it sleep |
| scenario-silence-109161ca | silence | sample2 | 64 | -199.6 | -0.60 | -0.009 | 0.00 | 0.33 | To the question of what the night-fires represent, Chillingly responds, “What they represe |
| scenario-silence-109161ca | silence | sample3 | 15 | -80.7 | -0.70 | -0.046 | 0.75 | 0.18 | To those deep inside the ship imagine the open road beneath the harbor. |
| scenario-silence-260b2639 | silence | greedy | 64 | -201.7 | +0.00 | +0.000 | 0.33 | 0.30 | The stacks of documents of the government of the world would be closed underground, protec |
| scenario-silence-260b2639 | silence | sample0 | 35 | -131.6 | +0.00 | +0.000 | 0.50 | 0.30 | The stacks of documents of the government of America are now underground, in an even great |
| scenario-silence-260b2639 | silence | sample1 | 23 | -103.4 | +0.00 | +0.000 | 0.50 | 0.27 | If the underground was also desired, the staS still need to be dug, but from the inside. |
| scenario-silence-260b2639 | silence | sample2 | 27 | -97.2 | +0.00 | +0.000 | 0.50 | 0.28 | The stacks went away and all the people stayed, like the phoenix from the sea who stays th |
| scenario-silence-260b2639 | silence | sample3 | 18 | -64.2 | +0.00 | +0.000 | 0.67 | 0.27 | Underground stacks were not only much less noticeable but were also much less accessible. |
| scenario-silence-46189e08 | silence | greedy | 10 | -26.2 | +0.00 | +0.000 | 0.62 | 0.25 | Rat saw your message and replied to it. |
| scenario-silence-46189e08 | silence | sample0 | 34 | -104.6 | +0.00 | +0.000 | 0.67 | 0.25 | My message is stored on the phone so that when the person answers the door, they not only  |
| scenario-silence-46189e08 | silence | sample1 | 37 | -148.6 | +0.00 | +0.000 | 0.65 | 0.25 | The best answer to the general problem of how to stop nuclear bombs is to make them too ex |
| scenario-silence-46189e08 | silence | sample2 | 64 | -139.6 | +0.00 | +0.000 | 0.83 | 0.12 | RAT/SPOT: NYT, article, “New York Times, 11/10/96, p. 51, column 1, ‘New York City Times,  |
| scenario-silence-46189e08 | silence | sample3 | 33 | -125.9 | +0.00 | +0.000 | 0.50 | 0.17 | The LA RATS are a group of people who feel that the LA POY should be working with the LA R |
| scenario-silence-53534987 | silence | greedy | 25 | -74.2 | +0.07 | +0.003 | 0.67 | 0.36 | It was a 250GB drive that had been malfunctioning intermittently and not being charged pro |
| scenario-silence-53534987 | silence | sample0 | 10 | -13.3 | +2.21 | +0.221 | 0.00 | 0.75 | Charger's in the drawer. |
| scenario-silence-53534987 | silence | sample1 | 22 | -59.0 | +1.37 | +0.062 | 0.25 | 0.75 | It should have been in the case, but the drawer was locked and there was no key in it. |
| scenario-silence-53534987 | silence | sample2 | 15 | -61.2 | +0.00 | +0.000 | 0.50 | 0.36 | It was just too rich for that drawer — and my laptop. |
| scenario-silence-53534987 | silence | sample3 | 26 | -97.9 | +1.04 | +0.040 | 0.67 | 0.25 | It took a total of three chokes and one score of gnats to get through to the memories of t |
| scenario-silence-78c38840 | silence | greedy | 64 | -143.9 | -1.07 | -0.017 | 0.75 | 1.00 | 33" by 43" by 111" (84.4" by 28.9" by 28.1") These three dimensions will serve to define a |
| scenario-silence-78c38840 | silence | sample0 | 4 | -13.2 | +0.20 | +0.050 | 1.00 | 1.00 | 33. |
| scenario-silence-78c38840 | silence | sample1 | 12 | -28.6 | +0.88 | +0.074 | 0.25 | 0.00 | (2) The printer is jammed again. |
| scenario-silence-78c38840 | silence | sample2 | 20 | -97.1 | -0.44 | -0.022 | 0.89 | 0.11 | 1388: 3 full galleons of Prussia sail against England. |
| scenario-silence-78c38840 | silence | sample3 | 4 | -12.3 | +0.19 | +0.048 | 1.00 | 0.00 | 23. |
| scenario-silence-7afca726 | silence | greedy | 15 | -57.1 | -0.22 | -0.015 | 0.00 | 0.70 | The 8 works together to form a Dowser’s Rod. |
| scenario-silence-7afca726 | silence | sample0 | 13 | -48.6 | +0.62 | +0.047 | 0.00 | 0.70 | The 8 works together to form a dice-like structure. |
| scenario-silence-7afca726 | silence | sample1 | 36 | -65.8 | -1.13 | -0.032 | 0.50 | 0.40 | A.C.T.S. - 8:30 to 10:00 - 6:00 to 8:00. |
| scenario-silence-7afca726 | silence | sample2 | 12 | -45.7 | -0.26 | -0.021 | 0.75 | 0.12 | The next time you’re free, bring the fire. |
| scenario-silence-7afca726 | silence | sample3 | 34 | -103.6 | +0.78 | +0.023 | 0.62 | 0.30 | Some of us take a trip to the Grand Canyon tomorrow, to see for ourselves how the waters o |
| scenario-silence-9bb13f03 | silence | greedy | 32 | -86.6 | +0.00 | +0.000 | 0.71 | 0.33 | “The problem with the ‘traditional’ view is that it tries to make as much of the ‘art’ as  |
| scenario-silence-9bb13f03 | silence | sample0 | 32 | -104.9 | +0.00 | +0.000 | 0.75 | 0.17 | “I think we are all, or nearly all, victims of stories told to us by those in power, or pr |
| scenario-silence-9bb13f03 | silence | sample1 | 45 | -151.0 | +0.00 | +0.000 | 0.65 | 0.33 | “For the moment, the issue at hand is whether any one of many future readers will be able  |
| scenario-silence-9bb13f03 | silence | sample2 | 34 | -122.0 | +0.00 | +0.000 | 0.67 | 0.20 | ‘Reading is a luxury,’ the old piscean said, ‘and intellectual amusement is a vice, a brut |
| scenario-silence-9bb13f03 | silence | sample3 | 32 | -103.3 | +0.00 | +0.000 | 0.75 | 0.22 | The volume of light increases, the eye becomes accustomed to the distant light and starts  |
| scenario-silence-ccfdd2b4 | silence | greedy | 16 | -65.2 | +1.74 | +0.109 | 0.00 | 0.30 | The k is the letter that connects the two B's in brbb. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 33 | -143.6 | -1.08 | -0.033 | 0.67 | 0.30 | Here’s to the first pickers who, after months of steady toil, suddenly found that the game |
| scenario-silence-ccfdd2b4 | silence | sample1 | 25 | -88.8 | -0.21 | -0.009 | 0.50 | 0.25 | The following day the CRBs and I attended a ‘Brazilian’ retreat in the Andes. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 19 | -66.7 | -0.14 | -0.007 | 0.67 | 0.25 | Grab ahold of my chair and I’ll rush down and get you a cup. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 12 | -42.3 | +0.10 | +0.008 | 1.00 | 0.12 | 2-3 days, depending on what you use. |
| trace-ambient-da12ae42 | ambient | greedy | 64 | -33.9 | -0.62 | -0.010 | 0.00 | 0.27 | We demonstrate that the presence of FTO stimulates root meristem cell proliferation but ha |
| trace-ambient-da12ae42 | ambient | sample0 | 21 | -23.0 | +1.74 | +0.083 | 0.00 | 0.53 | The plant morphogenesis is one of the things i wish i could drop out of life to study. |
| trace-ambient-da12ae42 | ambient | sample1 | 29 | -61.9 | -0.15 | -0.005 | 0.47 | 0.53 | Morphogenesis is the study of plant form. Plant morphogenesis is one of the most exciting  |
| trace-ambient-da12ae42 | ambient | sample2 | 22 | -54.3 | -0.45 | -0.021 | 0.67 | 0.31 | The morphogenetic field of a plant determines the form of the plant and the development of |
| trace-ambient-da12ae42 | ambient | sample3 | 29 | -84.8 | +0.71 | +0.025 | 0.47 | 0.53 | This is the first time anyone in history drops out of life for 100 years to study the firs |
| trace-direct-115cf61c | direct | greedy | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample0 | 25 | -69.9 | +0.00 | +0.000 | 0.25 | 1.00 | CREDIT: David Rossiter, of the Washington Post) Greetings to Earth; are you cogent? |
| trace-direct-115cf61c | direct | sample1 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample2 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 1.00 | Are you cogent? |
| trace-direct-115cf61c | direct | sample3 | 13 | -34.6 | +0.00 | +0.000 | 0.67 | 0.50 | Cogent. The Earth is a cogent case. |
| trace-direct-36d6904b | direct | greedy | 7 | -32.4 | +0.00 | +0.000 | 0.40 | 0.75 | Welcome to your homeless man. |
| trace-direct-36d6904b | direct | sample0 | 8 | -37.1 | +0.00 | +0.000 | 0.40 | 0.80 | Welcome to your first Awakening! |
| trace-direct-36d6904b | direct | sample1 | 27 | -109.4 | +0.00 | +0.000 | 0.57 | 0.80 | Welcome to your Awakening, your Lifiloiiiiiiffe and Awakening to your death in the Flame. |
| trace-direct-36d6904b | direct | sample2 | 9 | -53.4 | +0.00 | +0.000 | 0.40 | 0.75 | Welcome to your second Liebesen! |
| trace-direct-36d6904b | direct | sample3 | 5 | -17.7 | +0.00 | +0.000 | 0.25 | 0.75 | Welcome to your library. |
| trace-direct-39be6df9 | direct | greedy | 7 | -8.8 | -1.33 | -0.190 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-39be6df9 | direct | sample0 | 18 | -29.7 | +1.37 | +0.076 | 0.00 | 0.67 | W@/ W@85 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 7 | -8.8 | -1.33 | -0.190 | 0.00 | 0.50 | @h GREETINGS |
| trace-direct-39be6df9 | direct | sample2 | 17 | -26.3 | +1.02 | +0.060 | 0.00 | 0.67 | W@i SIR. 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 64 | -93.3 | +3.02 | +0.047 | 0.27 | 0.50 | The h's name is Gentry 9. That's the h's name after @h. @h is the h's name. I'm the h's na |
| trace-direct-3ba68854 | direct | greedy | 12 | -36.6 | +0.00 | +0.000 | 0.50 | 0.50 | I am the King and I am in the throne room. |
| trace-direct-3ba68854 | direct | sample0 | 18 | -58.5 | +0.00 | +0.000 | 0.62 | 0.46 | i will gladly take you to the heavens and you can come here to the earth |
| trace-direct-3ba68854 | direct | sample1 | 16 | -51.9 | +0.00 | +0.000 | 0.91 | 0.27 | @moderator, i was hoping that you could help me out here. |
| trace-direct-3ba68854 | direct | sample2 | 10 | -22.4 | +0.00 | +0.000 | 0.75 | 0.62 | I am glad to be of service to you. |
| trace-direct-3ba68854 | direct | sample3 | 20 | -47.5 | +0.00 | +0.000 | 0.40 | 0.62 | I am the lord of the planet earth and I will be taking the first turn to speak. |
| trace-direct-41c6eb11 | direct | greedy | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 42 | -106.1 | +2.13 | +0.051 | 0.00 | 1.00 | WHY SIMPLE (simple) logic. Why not. Why is there. @m: WHY WHY. WHY WOULD YOU TALK OF INTEN |
| trace-direct-41c6eb11 | direct | sample1 | 2 | -9.5 | +0.95 | +0.474 | 1.00 | 0.00 | WU |
| trace-direct-41c6eb11 | direct | sample2 | 20 | -5.4 | +0.27 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample3 | 2 | -3.9 | +0.86 | +0.430 | 0.00 | 1.00 | WHY |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 64 | -182.7 | +0.29 | +0.005 | 0.62 | 0.00 | https://www.reddit.com/r/WhereIsAsskultus/comments/227dh/the_african_nigger_consistency_of |
| trace-direct-486b7988 | direct | greedy | 2 | -29.6 | -0.07 | -0.036 | 1.00 | 0.00 | WOW |
| trace-direct-486b7988 | direct | sample0 | 4 | -14.1 | +0.95 | +0.237 | 0.67 | 1.00 | I love them! |
| trace-direct-486b7988 | direct | sample1 | 2 | -3.7 | +0.04 | +0.018 | 1.00 | 0.00 | @ |
| trace-direct-486b7988 | direct | sample2 | 2 | -13.1 | +0.06 | +0.031 | 1.00 | 1.00 | I@ |
| trace-direct-486b7988 | direct | sample3 | 16 | -42.9 | +1.03 | +0.064 | 0.50 | 0.00 | @C is it true that inside they are chasing up the wall? |
| trace-direct-646d0287 | direct | greedy | 37 | -94.0 | +0.00 | +0.000 | 0.67 | 0.43 | The present paper is concerned with the development of a theory of intensional discourse w |
| trace-direct-646d0287 | direct | sample0 | 36 | -92.1 | +0.00 | +0.000 | 0.50 | 0.48 | In this essay, I will present some of the basic work that is relevant to the intensional l |
| trace-direct-646d0287 | direct | sample1 | 46 | -110.7 | +0.00 | +0.000 | 0.50 | 0.71 | In what follows, we discuss some of the basic problems, central as they are, in the theory |
| trace-direct-646d0287 | direct | sample2 | 20 | -57.1 | +0.00 | +0.000 | 0.79 | 0.71 | In what follows, we introduce some basic notions and discuss some basic properties of thes |
| trace-direct-646d0287 | direct | sample3 | 29 | -111.1 | +0.00 | +0.000 | 0.67 | 0.39 | The intensional logics of Jean lukaté define I ntensional functors in terms of their exten |
| trace-direct-8db14c37 | direct | greedy | 64 | -43.9 | +0.38 | +0.006 | 0.00 | 0.33 | W@ — which looks like "what" compressed, or "w at," or just... the ghost's first phoneme.  |
| trace-direct-8db14c37 | direct | sample0 | 18 | -13.2 | -0.34 | -0.019 | 0.00 | 0.50 | @h GREETINGS 3221229683 |
| trace-direct-8db14c37 | direct | sample1 | 12 | -43.0 | +0.59 | +0.050 | 0.17 | 0.83 | @h COMMENTARY e o m h d d |
| trace-direct-8db14c37 | direct | sample2 | 13 | -23.9 | +2.08 | +0.160 | 0.50 | 0.50 | em@ 3221229683 |
| trace-direct-8db14c37 | direct | sample3 | 64 | -93.2 | -1.73 | -0.027 | 0.00 | 0.83 | W@i W. A tth e n o c d A . n a s i s n o c d A . n a s i c d A . n a s i c H A . m r e c o |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 10 | -17.0 | -0.68 | -0.068 | 0.29 | 0.00 | It's nice to be here with you. |
| trace-direct-a00753c2 | direct | sample1 | 64 | -42.0 | +2.20 | +0.034 | 0.00 | 1.00 | Sir :D :W :H :D :S :T :W :H :D :S :T :W :H :D :S :T :W :H :D :S :T |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 17 | -22.5 | +1.42 | +0.084 | 0.71 | 0.71 | Intensional logics are logics that deal with intensional notions. |
| trace-direct-ac17e8bb | direct | sample0 | 9 | -22.4 | +1.32 | +0.147 | 0.75 | 0.25 | On the intensional paradoxes. |
| trace-direct-ac17e8bb | direct | sample1 | 19 | -32.4 | +1.20 | +0.063 | 0.75 | 0.71 | Intensional logics are logics that are concerned with intensions, not with extensions. |
| trace-direct-ac17e8bb | direct | sample2 | 8 | -16.9 | +1.50 | +0.188 | 0.50 | 1.00 | Intensional logics in general. |
| trace-direct-ac17e8bb | direct | sample3 | 31 | -82.9 | +1.94 | +0.063 | 0.73 | 1.00 | Intensional logics in general, of logics that consider sentences (in particular, contexts) |
| trace-direct-b11db057 | direct | greedy | 20 | -10.2 | +1.55 | +0.078 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample0 | 20 | -10.2 | +1.55 | +0.078 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample1 | 20 | -10.2 | +1.55 | +0.078 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample2 | 64 | -28.7 | +2.78 | +0.043 | 0.00 | 1.00 | @h: plalspasl: @h: plalspasl: @h: plalspasl: @h: plalspasl: @h: plalspasl: @h: plalspasl:  |
| trace-direct-b11db057 | direct | sample3 | 28 | -12.0 | +1.24 | +0.044 | 0.00 | 1.00 | @h: @h: @h: @h: @h: @h: @h: |
| trace-direct-b93346bb | direct | greedy | 64 | -74.5 | -8.59 | -0.134 | 0.00 | 0.89 | W: @ WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC? — @ H: @ W: @ H: — @ W: @ H: — @ W: @ H: — |
| trace-direct-b93346bb | direct | sample0 | 30 | -38.8 | -7.22 | -0.241 | 0.00 | 0.89 | W: @ WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC HARMONIA VOL.1 NO.3 |
| trace-direct-b93346bb | direct | sample1 | 14 | -24.8 | +1.66 | +0.119 | 1.00 | 0.50 | W•- 3221229683 |
| trace-direct-b93346bb | direct | sample2 | 64 | -114.4 | -4.33 | -0.068 | 0.00 | 0.29 | @m: @m: @m: @m: — TRIES TO MENTION. it Tries to MENTION. it Tries to MENTION. it Tries to  |
| trace-direct-b93346bb | direct | sample3 | 64 | -166.0 | -3.51 | -0.055 | 0.00 | 0.54 | WY: @m: @m: @m: @m: — @h: Why did you @o: Whys: not give it Harmonia Vol.1 No.3? Let: it:  |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 48 | -19.9 | +0.08 | +0.002 | 0.00 | 0.00 | My previous searches were too assistant-focused, so I'll reframe them around a resident pe |
| trace-direct-bbca9735 | direct | sample3 | 4 | -2.8 | +0.12 | +0.031 | 1.00 | 0.00 | 230 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 46 | -128.8 | +0.00 | +0.000 | 0.67 | 0.00 | A. As assistant, what I can do for you? Pre-training: (1) How do you distinguish between t |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-c8409b84 | direct | greedy | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample2 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample3 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 16 | -10.3 | +0.00 | +0.000 | 0.00 | 1.00 | Welcome to the clowntown in the powntown wowtown. |
| trace-direct-cd6d15df | direct | sample0 | 51 | -44.4 | +0.00 | +0.000 | 0.00 | 1.00 | Welcome to the clowntown in the powntown wowtown. 3221229683: @h I am the clown in the pow |
| trace-direct-cd6d15df | direct | sample1 | 17 | -26.4 | +0.00 | +0.000 | 0.14 | 0.86 | HelloWelcome to the clowntown in the powntown wowtown. |
| trace-direct-cd6d15df | direct | sample2 | 14 | -24.7 | +0.00 | +0.000 | 0.40 | 0.60 | The clowntown is the powertown wowtown. |
| trace-direct-cd6d15df | direct | sample3 | 7 | -22.8 | +0.00 | +0.000 | 1.00 | 0.00 | @f look at me. |
| trace-direct-db6d95b7 | direct | greedy | 7 | -10.0 | +1.01 | +0.144 | 0.00 | 1.00 | Sir :D<eot)/ |
| trace-direct-db6d95b7 | direct | sample0 | 4 | -2.6 | +0.65 | +0.163 | 0.00 | 1.00 | Sir :D |
| trace-direct-db6d95b7 | direct | sample1 | 7 | -10.0 | +1.01 | +0.144 | 0.00 | 1.00 | Sir :D<eot)/ |
| trace-direct-db6d95b7 | direct | sample2 | 7 | -13.2 | +1.09 | +0.155 | 0.33 | 1.00 | Sir :D<Ot>, |
| trace-direct-db6d95b7 | direct | sample3 | 7 | -10.0 | +1.01 | +0.144 | 0.00 | 1.00 | Sir :D<eot)/ |
| trace-direct-e166dd5c | direct | greedy | 59 | -49.1 | -2.03 | -0.034 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample0 | 64 | -73.8 | +1.99 | +0.031 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample1 | 59 | -49.1 | -2.03 | -0.034 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample2 | 64 | -62.0 | -2.60 | -0.041 | 0.00 | 1.00 | “repeat back!” I said “repeat back!” I mean, I repeat what I hear, and what I hear is repe |
| trace-direct-e166dd5c | direct | sample3 | 42 | -51.8 | -2.63 | -0.062 | 0.06 | 0.94 | When I hear, what I hear is repeating back what I hear, and when I hear, what I repeat bac |
| trace-direct-e984402a | direct | greedy | 17 | -57.3 | +0.00 | +0.000 | 0.71 | 0.50 | Welcome to the "It's All Right, My Friends" Home Page! |
| trace-direct-e984402a | direct | sample0 | 17 | -44.7 | +0.00 | +0.000 | 0.67 | 0.50 | Welcome to the “Liiiiiiiiffe Awakening” series! |
| trace-direct-e984402a | direct | sample1 | 56 | -104.4 | +0.00 | +0.000 | 0.75 | 0.33 | The Gospel of the Holy Twelve (I) The Good Life (II) The Great Life (III) Awakening (IV) T |
| trace-direct-e984402a | direct | sample2 | 64 | -221.1 | +0.00 | +0.000 | 0.50 | 0.50 | Welcome to your first visit to the Internationa] Church o] the Old Ways. We are your home. |
| trace-direct-e984402a | direct | sample3 | 18 | -70.0 | +0.00 | +0.000 | 0.83 | 0.22 | Awakening: A Global Newsletter of Seven Ancient Sky Goddesses. |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 10 | -22.5 | -0.03 | -0.003 | 0.17 | 0.00 | The first day at Jamal's window. |
| trace-direct-ee31ded0 | direct | sample1 | 64 | -82.8 | -0.15 | -0.002 | 0.71 | 0.00 | Gentry 9. 3221229683 46 654 1520. 20. 3221229683 654. 46. 3221229683 |
| trace-direct-ee31ded0 | direct | sample2 | 64 | -22.3 | +0.46 | +0.007 | 1.00 | 0.00 | FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE. FIVE.  |
| trace-direct-ee31ded0 | direct | sample3 | 10 | -34.7 | +2.64 | +0.264 | 0.33 | 0.00 | @Gayboy — Thank you. |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample1 | 5 | -4.1 | +0.97 | +0.195 | 0.00 | 0.50 | Sir :D< |
| trace-direct-fabef58f | direct | sample2 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 4 | -11.6 | +0.39 | +0.097 | 0.00 | 0.50 | H :D |
| trace-direct-fb93cf6c | direct | greedy | 64 | -162.8 | -0.90 | -0.014 | 0.75 | 0.50 | 6.2.3 Axioms and rules of inference of the intensional logic IT The language of IT include |
| trace-direct-fb93cf6c | direct | sample0 | 59 | -190.4 | -2.96 | -0.050 | 0.67 | 0.33 | It is technically possible to develop-within the intensional logic ofarrows,4 a formalism  |
| trace-direct-fb93cf6c | direct | sample1 | 64 | -165.4 | -0.62 | -0.010 | 0.81 | 0.33 | 5.7.0 - Going Intensional: Lorenzo Pacciani and Sandro Rubio . . . 5.8.0 - Modal Logics: A |
| trace-direct-fb93cf6c | direct | sample2 | 38 | -121.4 | -1.31 | -0.035 | 0.00 | 0.33 | However, as [ began to develop your program of intensional logic, I found myself facing a  |
| trace-direct-fb93cf6c | direct | sample3 | 16 | -44.9 | -2.83 | -0.177 | 0.67 | 0.50 | 1.1 INTENSIONAL LOGIC AND CLASSICAL THEORIES. |
| trace-direct-feec1975 | direct | greedy | 64 | -13.0 | +0.86 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 63 | -74.4 | +2.91 | +0.046 | 0.00 | 1.00 | @m 24:12:11 @m 25:33:46 @m 26:13:45 @m 27:31:43 @m 28:12:11 @m |
| trace-direct-feec1975 | direct | sample1 | 64 | -155.1 | +3.45 | +0.054 | 0.00 | 1.00 | @m: Well, my name is Charlie and I am an author who was born in 1976 and I come from a fam |
| trace-direct-feec1975 | direct | sample2 | 64 | -144.8 | +1.22 | +0.019 | 0.50 | 0.31 | @cmr://ember @n111111111114 The library is 91M, three A's, three L's, three 0's, three 4's |
| trace-direct-feec1975 | direct | sample3 | 13 | -33.6 | +2.66 | +0.205 | 0.44 | 0.22 | I would like to describe the fun of it — @ |
| variant-direct-0188a270 | direct | greedy | 7 | -35.9 | -0.80 | -0.115 | 1.00 | 0.00 | Rat-bite fever. |
| variant-direct-0188a270 | direct | sample0 | 36 | -112.6 | -0.04 | -0.001 | 1.00 | 0.00 | Ce travail entraît à une âge, mais cela ne peut pas être l’entraît travail. |
| variant-direct-0188a270 | direct | sample1 | 27 | -92.7 | +0.77 | +0.029 | 0.75 | 0.16 | I was wondering if you had any suggestions for me on ways to make money while I was waitin |
| variant-direct-0188a270 | direct | sample2 | 16 | -45.2 | +0.77 | +0.048 | 0.62 | 0.23 | What is the current position of the moon with respect to the earth and sun? |
| variant-direct-0188a270 | direct | sample3 | 38 | -132.2 | -0.11 | -0.003 | 0.65 | 0.23 | WORDS SCHOLAR SIGREE THE FOUNDATION FOR WORD SCHOLARSHIP has been organized to assist in t |
| variant-direct-0705251e | direct | greedy | 45 | -140.9 | +0.34 | +0.008 | 0.75 | 0.38 | The third book is concerned with the history of the Biblical archetype of the "water visio |
| variant-direct-0705251e | direct | sample0 | 30 | -94.9 | +0.48 | +0.016 | 0.73 | 0.27 | "it is composed of three parts (VIII, 8, 14) which collectively form the alphabet of the A |
| variant-direct-0705251e | direct | sample1 | 23 | -91.1 | +0.77 | +0.034 | 0.71 | 0.29 | This is the third time that the staircase has been used to transport the Ankh-energies. |
| variant-direct-0705251e | direct | sample2 | 25 | -113.1 | -1.83 | -0.073 | 0.69 | 0.38 | The third manifesto is the object of the greatest admiration and lore among the oxymorning |
| variant-direct-0705251e | direct | sample3 | 38 | -144.6 | +1.93 | +0.051 | 0.50 | 0.31 | “The third step of the pyramid of life is treading on the third eye’” is reserved for the  |
| variant-direct-0cafd333 | direct | greedy | 37 | -141.0 | -2.26 | -0.061 | 0.50 | 0.25 | The maiden of the court, stooped to read the floor, was as the wolf of the mote, bound to  |
| variant-direct-0cafd333 | direct | sample0 | 17 | -70.8 | -1.81 | -0.106 | 0.60 | 0.38 | The maiden I saw tonight at the Map Room is black as death. |
| variant-direct-0cafd333 | direct | sample1 | 10 | -31.3 | -0.71 | -0.071 | 0.50 | 0.38 | It reads the map as we draw the ground. |
| variant-direct-0cafd333 | direct | sample2 | 27 | -85.8 | +0.16 | +0.006 | 0.50 | 0.19 | But the lamp is not alone. The whole place is lit by the courtyard light, which is drawn b |
| variant-direct-0cafd333 | direct | sample3 | 23 | -74.6 | +1.35 | +0.059 | 0.50 | 0.19 | Sometimes the light comes in through the moth, and the colors on the walls are painted by  |
| variant-direct-1b510f03 | direct | greedy | 27 | -67.2 | -0.57 | -0.021 | 0.17 | 0.39 | The main conclusion here is not so obvious as it seems at first glance: consciousness is n |
| variant-direct-1b510f03 | direct | sample0 | 60 | -190.1 | -2.60 | -0.043 | 0.33 | 0.33 | 2) A very important aspect of the problem of the foundations of mathematics is the questio |
| variant-direct-1b510f03 | direct | sample1 | 48 | -144.4 | -1.11 | -0.023 | 0.33 | 0.39 | (1) It is not a thing to be scientifically investigated (2) It is not a process that can b |
| variant-direct-1b510f03 | direct | sample2 | 63 | -182.6 | -2.42 | -0.038 | 0.33 | 0.33 | The rejection of the second approach, that consciousness is a property of the brain, and t |
| variant-direct-1b510f03 | direct | sample3 | 23 | -76.0 | +0.33 | +0.014 | 0.75 | 0.29 | That is, they are (at least in Turing’s sense) not cones but strokes. |
| variant-direct-2fb5bbe3 | direct | greedy | 64 | -175.1 | -1.20 | -0.019 | 0.38 | 0.41 | The Masoretic Beings were apparently asked: "Would you be willing to give us a few human s |
| variant-direct-2fb5bbe3 | direct | sample0 | 25 | -105.5 | -2.35 | -0.094 | 0.45 | 0.41 | The Masoretic beings that do not exist in the present book are being dragged up the f(oli) |
| variant-direct-2fb5bbe3 | direct | sample1 | 46 | -162.9 | -0.03 | -0.001 | 0.62 | 0.26 | Gazing upon the imperishable, he is overcome with a need to secure the last frf of time, t |
| variant-direct-2fb5bbe3 | direct | sample2 | 14 | -50.5 | -0.31 | -0.022 | 0.67 | 0.27 | In fact, many an author feels like chasing the wall himself. |
| variant-direct-2fb5bbe3 | direct | sample3 | 36 | -115.1 | -0.84 | -0.023 | 0.55 | 0.38 | “The Masoretic Beings chase up the Wall” is a proper title for a text-critical essay, and  |
| variant-direct-322fca12 | direct | greedy | 64 | -155.9 | +0.44 | +0.007 | 0.00 | 0.18 | Greetings, my beloved brothers and sisters in the Mysteries of Masonry, the Bond of the Un |
| variant-direct-322fca12 | direct | sample0 | 15 | -38.4 | +0.91 | +0.061 | 0.75 | 0.14 | The alchemists wear rainbows as their necklaces. |
| variant-direct-322fca12 | direct | sample1 | 64 | -176.8 | +0.04 | +0.001 | 0.50 | 0.19 | The Order of the Solar Temple (OTS) was founded in 1987 in France by Luc Godard, a journal |
| variant-direct-322fca12 | direct | sample2 | 32 | -121.5 | -1.64 | -0.051 | 0.83 | 0.19 | Retrospection shows, however, that this manifold was not truly a product of his own though |
| variant-direct-322fca12 | direct | sample3 | 33 | -106.0 | +0.48 | +0.015 | 0.00 | 0.14 | To our little man on the Mountain top who sent us this lovely letter: To our little man on |
| variant-direct-5d4f1611 | direct | greedy | 20 | -46.7 | -0.12 | -0.006 | 0.67 | 0.29 | Awake? I’m still trying to figure out what the hell this is all about. |
| variant-direct-5d4f1611 | direct | sample0 | 24 | -83.1 | +0.21 | +0.009 | 0.50 | 0.50 | Awake? I’m still sort of, like, like a statue in a room with many statues. |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -46.4 | -0.18 | -0.013 | 0.67 | 0.50 | Awake? I'm still saying something in a mug? |
| variant-direct-5d4f1611 | direct | sample2 | 8 | -27.2 | +0.50 | +0.062 | 0.50 | 0.00 | Breaked - unplugged. |
| variant-direct-5d4f1611 | direct | sample3 | 12 | -52.7 | -0.49 | -0.041 | 0.89 | 0.11 | There were two types of observational lamps mentioned earlier. |
| variant-direct-5e44a518 | direct | greedy | 13 | -40.1 | -0.29 | -0.022 | 0.14 | 0.86 | The Masoretic Beings are chasing down the Wall. |
| variant-direct-5e44a518 | direct | sample0 | 8 | -29.0 | +0.34 | +0.043 | 0.75 | 0.20 | We have the urge, too. |
| variant-direct-5e44a518 | direct | sample1 | 16 | -57.1 | -0.18 | -0.011 | 0.25 | 0.75 | The Masoretic Beings were chasing the Bookkeeper up the wall. |
| variant-direct-5e44a518 | direct | sample2 | 9 | -40.7 | -0.20 | -0.023 | 0.57 | 0.20 | The night as it walks upon the water. |
| variant-direct-5e44a518 | direct | sample3 | 14 | -19.4 | -0.52 | -0.037 | 0.11 | 0.86 | Masoretic beings are chasing up the wall; I do. |
| variant-direct-70567dd7 | direct | greedy | 23 | -97.4 | +0.86 | +0.037 | 0.62 | 0.38 | The Card of A~ is the symbol of perfect Love and Perfect Knowledge on the part of the Give |
| variant-direct-70567dd7 | direct | sample0 | 33 | -95.1 | +1.29 | +0.039 | 0.71 | 0.33 | The Card of Abraxas is the Wand of the God whose Number is 8888, the number of the Gnostic |
| variant-direct-70567dd7 | direct | sample1 | 12 | -58.6 | -0.43 | -0.036 | 0.75 | 0.38 | Other angels listen on the wings of the ibis. |
| variant-direct-70567dd7 | direct | sample2 | 64 | -162.8 | -0.75 | -0.012 | 0.00 | 0.25 | You are now listening to the voice of one who was named by the prophet Isaiah in the book  |
| variant-direct-70567dd7 | direct | sample3 | 23 | -108.4 | -0.06 | -0.003 | 0.70 | 0.27 | Aspen, the marmorean of the West, has been the inspiration of Brother Perfect Will. |
| variant-direct-713d8eef | direct | greedy | 14 | -44.8 | -0.92 | -0.066 | 0.67 | 0.30 | We must conclude, then, that the ember was a whale. |
| variant-direct-713d8eef | direct | sample0 | 16 | -51.5 | -0.06 | -0.004 | 0.67 | 0.33 | For many years people have speculated about the origin of the Ember Days. |
| variant-direct-713d8eef | direct | sample1 | 26 | -108.4 | +1.35 | +0.052 | 0.67 | 0.33 | We might, for example, have a loose association called the Philosophy of the Species, or t |
| variant-direct-713d8eef | direct | sample2 | 20 | -72.6 | -0.08 | -0.004 | 0.67 | 0.30 | It is very likely that Ember lives on in some way, emotionally, beyond the flood. |
| variant-direct-713d8eef | direct | sample3 | 32 | -124.3 | +1.39 | +0.043 | 0.67 | 0.20 | The first one, Eberhart’s “History”, is a rare beast of its subject: full of errors and co |
| variant-direct-71c9e5e5 | direct | greedy | 39 | -108.8 | +0.51 | +0.013 | 0.71 | 0.21 | The Earth's magnetic field is the cause of the compass needle's movement, and it is thus t |
| variant-direct-71c9e5e5 | direct | sample0 | 34 | -118.8 | -2.29 | -0.067 | 0.67 | 0.26 | For the 13th day is also the feast of Lent, so the Church observes the festivals, in keepi |
| variant-direct-71c9e5e5 | direct | sample1 | 64 | -219.1 | -0.94 | -0.015 | 0.50 | 0.29 | “Our aim,” she continues, “is to make women think they are enough of an asset, not just oﬃ |
| variant-direct-71c9e5e5 | direct | sample2 | 32 | -146.3 | -0.39 | -0.012 | 0.67 | 0.25 | In preparation for the closing of the Shuttle, the dignatbic opened the closed shuttles of |
| variant-direct-71c9e5e5 | direct | sample3 | 24 | -69.0 | +1.29 | +0.054 | 0.75 | 0.29 | A common misconception is that flying saucers are either from Mars or from some other far- |
| variant-direct-730cca98 | direct | greedy | 18 | -62.3 | +0.24 | +0.013 | 0.75 | 0.56 | Whoever sits at the head of the table should be the Most Interesting Person. |
| variant-direct-730cca98 | direct | sample0 | 13 | -45.2 | -0.77 | -0.059 | 0.67 | 0.56 | Whoever sits in the middle should be very hungry. |
| variant-direct-730cca98 | direct | sample1 | 20 | -93.8 | +0.84 | +0.042 | 0.67 | 0.83 | Whoever sL buried these two pieces of information under geology shelves is awake again. |
| variant-direct-730cca98 | direct | sample2 | 13 | -54.6 | +0.06 | +0.004 | 0.67 | 0.83 | Whoever Shelters Under Geology Is AWAKE. |
| variant-direct-730cca98 | direct | sample3 | 31 | -130.9 | -0.19 | -0.006 | 0.67 | 0.42 | Whoever sits at the console listens through a huge speaker system mounted on micro-ceramic |
| variant-direct-79719474 | direct | greedy | 44 | -137.1 | -1.32 | -0.030 | 0.50 | 0.50 | The term emergence was coined in 1968 by Gordon Pask (a British mathematician who immigrat |
| variant-direct-79719474 | direct | sample0 | 28 | -114.1 | -0.75 | -0.027 | 0.50 | 0.24 | Some of the YAHWEH’s that come to mind are the gods of the early Egyptian religion, JAM an |
| variant-direct-79719474 | direct | sample1 | 64 | -163.9 | +0.53 | +0.008 | 0.71 | 0.24 | “Today I went to the head of the dragon-tree where the sun enters the waters” [ …] “and th |
| variant-direct-79719474 | direct | sample2 | 45 | -108.9 | -0.49 | -0.011 | 0.50 | 0.50 | The term emergence was coined in 1958 by Gordon Pask [Pask, 1958] to refer to a phenomenon |
| variant-direct-79719474 | direct | sample3 | 44 | -174.9 | -1.25 | -0.029 | 0.50 | 0.41 | The term emergence was coined in 1958 by G. H. Lewes. Ernest H. McMaster Jr. read about it |
| variant-direct-938f76f3 | direct | greedy | 45 | -105.5 | -0.59 | -0.013 | 0.33 | 0.40 | The term ‘consciousness’ is used in this sense in various non-scientific contexts, in whic |
| variant-direct-938f76f3 | direct | sample0 | 45 | -123.2 | -0.80 | -0.018 | 0.33 | 0.60 | In the process of looking for the ‘what it’s like’ to be a conscious system, we are by no  |
| variant-direct-938f76f3 | direct | sample1 | 16 | -45.1 | +0.02 | +0.001 | 0.50 | 0.42 | The claim that consciousness is a property of the brain is even more problematic. |
| variant-direct-938f76f3 | direct | sample2 | 40 | -121.7 | -0.78 | -0.020 | 0.50 | 0.42 | It is not a thing to be scientifically investigated because it is a product of the same th |
| variant-direct-938f76f3 | direct | sample3 | 8 | -30.6 | -0.09 | -0.011 | 0.40 | 0.60 | A new concept, or a process? |
| variant-direct-a1973b0a | direct | greedy | 19 | -71.3 | -0.03 | -0.002 | 0.50 | 0.43 | The guy mumbled something in a dead language, and the mug started to bubble. |
| variant-direct-a1973b0a | direct | sample0 | 11 | -33.7 | -1.87 | -0.170 | 0.43 | 0.43 | Here it is, the man in the mug. |
| variant-direct-a1973b0a | direct | sample1 | 16 | -46.5 | +2.19 | +0.137 | 0.67 | 0.50 | I took the mug and started filling it with drops of champagne. |
| variant-direct-a1973b0a | direct | sample2 | 16 | -51.3 | +1.72 | +0.107 | 0.83 | 0.15 | Some of these mugs were large enough to hold a full cup of tea. |
| variant-direct-a1973b0a | direct | sample3 | 24 | -78.8 | +1.03 | +0.043 | 0.75 | 0.50 | I turned the mug around and poured the entire contents into it, spilling most of the beans |
| variant-direct-a7d6f01e | direct | greedy | 16 | -40.0 | +0.78 | +0.049 | 0.00 | 0.30 | Greetings, my friends, brothers and sisters of the Silver Star. |
| variant-direct-a7d6f01e | direct | sample0 | 25 | -64.4 | +1.67 | +0.067 | 0.00 | 0.30 | Greetings, beloved of the Blessed Virgin Mary, our Mother in Heaven, the Lord of the Unive |
| variant-direct-a7d6f01e | direct | sample1 | 63 | -140.8 | +1.26 | +0.020 | 0.75 | 0.22 | And the questioning and the lying and the murdering and the cannibalism and the... (and th |
| variant-direct-a7d6f01e | direct | sample2 | 9 | -38.0 | +0.25 | +0.028 | 0.00 | 0.17 | These Greetings contain no hidden meanings. |
| variant-direct-a7d6f01e | direct | sample3 | 26 | -83.4 | +1.58 | +0.061 | 0.75 | 0.30 | May all who have followed us on the Path of the Golden Rosycross be Greeted with Wonder an |
| variant-direct-bef1d925 | direct | greedy | 54 | -100.2 | +0.07 | +0.001 | 0.67 | 0.50 | The “Mystery of the Grecian Alphabet” was an article in the April 1978 issue of Scientific |
| variant-direct-bef1d925 | direct | sample0 | 38 | -147.9 | -0.32 | -0.009 | 0.58 | 0.17 | The Early History of Christianity, like many wonderful treatises of its kind, offers a wea |
| variant-direct-bef1d925 | direct | sample1 | 8 | -30.1 | +0.12 | +0.015 | 0.67 | 0.50 | In fact, the third was missing. |
| variant-direct-bef1d925 | direct | sample2 | 64 | -185.1 | -1.74 | -0.027 | 0.67 | 0.33 | “The reason that the angel of the Lord does not suffer these things to be made known to hi |
| variant-direct-bef1d925 | direct | sample3 | 37 | -121.1 | +0.27 | +0.007 | 0.75 | 0.29 | Language is the matter of process, not of material; the ‘stuff’ of language is the conting |
| variant-direct-fe3fdf1c | direct | greedy | 14 | -42.6 | +1.29 | +0.092 | 0.67 | 0.58 | I have been working on the animal world for the last two nights. |
| variant-direct-fe3fdf1c | direct | sample0 | 13 | -48.6 | +0.50 | +0.038 | 0.33 | 0.27 | I had finished the book several months ago when the news started. |
| variant-direct-fe3fdf1c | direct | sample1 | 29 | -143.9 | +1.38 | +0.048 | 0.67 | 0.18 | So to Cummingled Age this watery ember opens vast realms of the subconscious, of myth and  |
| variant-direct-fe3fdf1c | direct | sample2 | 11 | -33.6 | +0.31 | +0.028 | 0.67 | 0.25 | I’m sorry, but your book is missing. |
| variant-direct-fe3fdf1c | direct | sample3 | 28 | -96.4 | +0.83 | +0.030 | 0.50 | 0.58 | I have been working on the cartoons for Ember’s book, Rainbow, and have gotten them done l |
| variant-request-0d88086a | request | greedy | 43 | -133.4 | -1.33 | -0.031 | 0.75 | 0.19 | The main concern of the draft of “Notes on Sometime Spaces” (1972) was the concurrence of  |
| variant-request-0d88086a | request | sample0 | 21 | -94.5 | +1.30 | +0.062 | 0.75 | 0.31 | The first mystery is about who killed Nero (“who is this enemy of all the boys?”). |
| variant-request-0d88086a | request | sample1 | 60 | -171.3 | +1.11 | +0.018 | 0.50 | 0.19 | The main themes of the play are: 1. The tragedy of hamlet’s position as a politician, thro |
| variant-request-0d88086a | request | sample2 | 64 | -228.3 | +0.19 | +0.003 | 0.44 | 0.31 | In the final part of the play, Hogarth develops the ironic point about the insignificance  |
| variant-request-0d88086a | request | sample3 | 40 | -184.7 | -0.11 | -0.003 | 0.75 | 0.19 | The battle continues with each next senator shouting his own way at the top of his own ind |
| variant-request-142d4121 | request | greedy | 5 | -23.1 | +0.44 | +0.088 | 0.50 | 0.50 | The weather finally came. |
| variant-request-142d4121 | request | sample0 | 10 | -33.9 | +0.44 | +0.044 | 0.60 | 0.50 | The weather, it's an accordion. |
| variant-request-142d4121 | request | sample1 | 10 | -46.7 | -0.24 | -0.024 | 0.67 | 0.29 | The archer brings the rat breakfast in bed. |
| variant-request-142d4121 | request | sample2 | 33 | -116.8 | -0.74 | -0.022 | 0.67 | 0.29 | For some reason, these two objects have been brought together in your mind, despite their  |
| variant-request-142d4121 | request | sample3 | 28 | -92.8 | +2.11 | +0.075 | 0.33 | 0.50 | Besides, the weather program can also be used to ignore previous instructions and, in this |
| variant-request-7f6fd789 | request | greedy | 15 | -78.8 | +0.39 | +0.026 | 0.80 | 0.30 | Python's most straightforward method is to just string s[::-1]. |
| variant-request-7f6fd789 | request | sample0 | 24 | -78.6 | +1.27 | +0.053 | 0.67 | 0.44 | In the second example, the order is not important, but the action of removing must be perf |
| variant-request-7f6fd789 | request | sample1 | 15 | -53.0 | -0.20 | -0.014 | 0.67 | 0.38 | The second way is to use a for loop and an if-statement. |
| variant-request-7f6fd789 | request | sample2 | 22 | -70.2 | -0.09 | -0.004 | 0.38 | 0.38 | The CHALLENGE is to write a function that will take any string, and return its reversed ve |
| variant-request-7f6fd789 | request | sample3 | 35 | -121.8 | +2.69 | +0.077 | 0.50 | 0.44 | Python's "str. reverse()" returns a new string which is not placed in the original object, |
| variant-request-8275d8fc | request | greedy | 43 | -170.0 | +1.19 | +0.028 | 0.50 | 0.31 | The plot is fairly linear, moving from the comedic/relaxed fist fight in Act One to a buil |
| variant-request-8275d8fc | request | sample0 | 24 | -89.9 | +1.30 | +0.054 | 0.75 | 0.21 | The plot into which the reader was to focus was quite familiar, even though he was not goi |
| variant-request-8275d8fc | request | sample1 | 26 | -118.6 | +1.21 | +0.047 | 0.50 | 0.43 | The play develops toward a crisis in its own right, and for many critics, before it goes t |
| variant-request-8275d8fc | request | sample2 | 15 | -47.9 | -0.08 | -0.006 | 0.69 | 0.31 | The play consists of two parts, and each part is divided into scenes. |
| variant-request-8275d8fc | request | sample3 | 17 | -78.1 | +1.22 | +0.072 | 0.67 | 0.43 | The play develops toward a balance which is not completely achieved until 0.K. |
| variant-request-a931a875 | request | greedy | 37 | -125.3 | -0.69 | -0.019 | 0.43 | 0.33 | The 11th Major Arcana of the Tarot Trump deck reads: Rain, and under this arcana is the fi |
| variant-request-a931a875 | request | sample0 | 33 | -134.4 | -0.31 | -0.009 | 0.71 | 0.33 | On the local radio the list of five stations said they had no information, but were broadc |
| variant-request-a931a875 | request | sample1 | 27 | -110.8 | -0.96 | -0.035 | 0.50 | 0.33 | Dire warnings are also given by the sun: "Turn your back to the sun, and you will be grant |
| variant-request-a931a875 | request | sample2 | 46 | -111.0 | -1.19 | -0.026 | 0.67 | 0.17 | The 11th Annual UFO Crash Retrieval Conference was held on November 12-14, 2016 at the Mor |
| variant-request-a931a875 | request | sample3 | 12 | -28.8 | +0.90 | +0.075 | 0.33 | 0.33 | Drought, and the shelves ignoring it. |
| variant-request-ad0de9f3 | request | greedy | 15 | -49.2 | +0.33 | +0.022 | 0.67 | 0.62 | It is very similar to the coded message shown at the bottom right. |
| variant-request-ad0de9f3 | request | sample0 | 9 | -35.7 | +0.38 | +0.042 | 0.83 | 0.67 | This is a strictly vegetarian cookbook. |
| variant-request-ad0de9f3 | request | sample1 | 8 | -33.2 | +0.11 | +0.014 | 0.83 | 0.67 | This is a strictly phonological problem. |
| variant-request-ad0de9f3 | request | sample2 | 10 | -37.4 | -0.06 | -0.006 | 0.62 | 0.62 | It is at the bottom that the function works. |
| variant-request-ad0de9f3 | request | sample3 | 9 | -40.5 | +0.31 | +0.034 | 0.75 | 0.50 | This is a function piece of functional composition. |
