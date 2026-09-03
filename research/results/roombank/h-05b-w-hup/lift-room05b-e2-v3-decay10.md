# Context lift: h-05b-w-hup under room05b-e2-v3-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | +1.056 | +1.083 | 0.70 | +0.0948 | 0.492 | 0.508 | 0.230 | 0.468 | 0.32 |
| mode greedy | 78 | +1.384 | +1.123 | 0.72 | +0.1306 | 0.439 | 0.561 | 0.269 | 0.505 | 0.41 |
| mode sample | 312 | +0.974 | +1.064 | 0.70 | +0.0858 | 0.505 | 0.494 | 0.220 | 0.459 | 0.29 |
| kind direct | 175 | +1.259 | +1.119 | 0.77 | +0.1299 | 0.429 | 0.571 | 0.341 | 0.453 | 0.41 |
| kind ambient | 35 | +1.847 | +1.337 | 0.83 | +0.1127 | 0.515 | 0.485 | 0.000 | 0.470 | 0.17 |
| kind callback | 60 | +0.863 | +0.672 | 0.62 | +0.0685 | 0.539 | 0.461 | 0.044 | 0.519 | 0.28 |
| kind disagreement | 40 | -0.186 | +2.225 | 0.60 | +0.0218 | 0.426 | 0.574 | 0.528 | 0.571 | 0.50 |
| kind joke | 25 | +1.836 | +0.568 | 0.64 | +0.1160 | 0.591 | 0.409 | 0.072 | 0.375 | 0.24 |
| kind silence | 25 | +0.778 | +1.629 | 0.56 | +0.0419 | 0.639 | 0.361 | 0.000 | 0.369 | 0.08 |
| kind request | 30 | +0.566 | +0.517 | 0.60 | +0.0456 | 0.625 | 0.375 | 0.142 | 0.471 | 0.07 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 9 | -6.6 | +0.00 | +0.000 | 0.50 | 0.67 | The observatory is closed to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 26 | -47.6 | +0.00 | +0.000 | 0.57 | 0.50 | Every evening at about 7:30 p.m., an event is held in the observatory: meteor showers. |
| observatory-direct-9e3185b9 | direct | sample1 | 28 | -23.1 | +0.00 | +0.000 | 0.75 | 0.17 | THE SAUCERIAN needs clippings and information about saucer sightings, and reports of unide |
| observatory-direct-9e3185b9 | direct | sample2 | 18 | -26.6 | +0.00 | +0.000 | 0.57 | 0.67 | During the nights, when the sun is not shining, the observatory is closed. |
| observatory-direct-9e3185b9 | direct | sample3 | 32 | -51.5 | +0.00 | +0.000 | 0.71 | 0.33 | The sun is directly influencing our lives, our weather, our disasters such as earthquakes, |
| scenario-ambient-0ecb3f23 | ambient | greedy | 19 | -27.3 | +0.00 | +0.000 | 0.60 | 0.50 | It is tedious, time-consuming, and often leads to boredom. |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 8 | -15.7 | +0.00 | +0.000 | 0.71 | 0.29 | But there is no word for it. |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 25 | -23.1 | +0.00 | +0.000 | 0.00 | 0.29 | There should be one book that defines the state of mind in which the reader is at the mome |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 43 | -72.5 | +0.00 | +0.000 | 0.50 | 0.50 | It is often called the "uncertainty principle" because it involves a person's being able t |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 33 | -88.1 | +0.00 | +0.000 | 0.67 | 0.30 | It is usually expressed by the Latin verb quoque, translated as ‘to take a whole hand’ (wh |
| scenario-ambient-103e3d78 | ambient | greedy | 40 | -57.1 | -7.43 | -0.186 | 0.50 | 0.25 | The paragraph goes: “In a similar vein, Benjamin Franklin, in his arguments against slave  |
| scenario-ambient-103e3d78 | ambient | sample0 | 25 | -58.8 | +1.19 | +0.047 | 0.58 | 0.25 | We're still in the shadow of the visible, and the visible is still in the shadow of what’s |
| scenario-ambient-103e3d78 | ambient | sample1 | 26 | -51.2 | +0.77 | +0.030 | 0.67 | 0.30 | The next morning he was weeping and whimpering, as children do after a night of bedwetting |
| scenario-ambient-103e3d78 | ambient | sample2 | 12 | -27.1 | +1.83 | +0.153 | 0.50 | 0.30 | The same paragraph was read by several persons during the night. |
| scenario-ambient-103e3d78 | ambient | sample3 | 19 | -39.5 | +4.77 | +0.251 | 0.67 | 0.25 | We have sought, in vain, for an explanation of the phenomenon which happened last night. |
| scenario-ambient-202a37a7 | ambient | greedy | 17 | -23.8 | +1.48 | +0.087 | 0.50 | 0.50 | Geology, the study of the Earth and its history, is a fascinating field. |
| scenario-ambient-202a37a7 | ambient | sample0 | 27 | -58.7 | +3.13 | +0.116 | 0.50 | 0.50 | Geology, the book of nature, is the science of all the physical changes that occur in the  |
| scenario-ambient-202a37a7 | ambient | sample1 | 26 | -46.6 | +4.48 | +0.172 | 0.50 | 0.33 | Reworked from ancient manuscripts, the book contains a wealth of information on the quarry |
| scenario-ambient-202a37a7 | ambient | sample2 | 16 | -49.2 | +0.37 | +0.023 | 0.62 | 0.50 | Geology, indeed, is the most dissonant of the imaginations. |
| scenario-ambient-202a37a7 | ambient | sample3 | 19 | -55.3 | +0.90 | +0.047 | 0.50 | 0.25 | Geology is not exactly a book to keep around; it is quite a book to read. |
| scenario-ambient-326742d4 | ambient | greedy | 23 | -57.6 | +1.21 | +0.052 | 0.67 | 0.54 | As the paper is reduced lignin is not, and vanilla is a chemical compound containing ligni |
| scenario-ambient-326742d4 | ambient | sample0 | 34 | -89.7 | +0.88 | +0.026 | 0.75 | 0.54 | As the paper is reduced lignin is not, but the dye is As the dye is reduced the paper is a |
| scenario-ambient-326742d4 | ambient | sample1 | 22 | -28.1 | +6.96 | +0.317 | 0.67 | 0.38 | For the oldest books, the decomposition is more complete, and the result is a greater vani |
| scenario-ambient-326742d4 | ambient | sample2 | 29 | -60.2 | +0.58 | +0.020 | 0.80 | 0.23 | I'm going to take a guess that's 10 years old and that's about as far back as I can take i |
| scenario-ambient-326742d4 | ambient | sample3 | 28 | -78.0 | +4.60 | +0.164 | 0.67 | 0.54 | As the paper is reduced lignin is not, so the book remains pretty much the same in smell a |
| scenario-ambient-58a0f246 | ambient | greedy | 34 | -45.2 | +0.00 | +0.000 | 0.25 | 0.57 | For instance, the clock in the lobby of the New York Hilton is five minutes slow, while th |
| scenario-ambient-58a0f246 | ambient | sample0 | 19 | -35.7 | +0.00 | +0.000 | 0.25 | 0.57 | For instance, the clock in the room you are in now is only 5 minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample1 | 26 | -50.0 | +0.00 | +0.000 | 0.57 | 0.42 | For some years the hands of this pendulum have been released from their motion by a mechan |
| scenario-ambient-58a0f246 | ambient | sample2 | 19 | -33.3 | +0.00 | +0.000 | 0.57 | 0.42 | For over 100 years the mechanical movement of the clock had been erroneous. |
| scenario-ambient-58a0f246 | ambient | sample3 | 39 | -71.7 | +0.00 | +0.000 | 0.38 | 0.43 | For instance, the clock in the museum shows that four minutes have elapsed since the last  |
| scenario-ambient-59f0a53e | ambient | greedy | 18 | -21.3 | +0.24 | +0.014 | 0.60 | 0.71 | A bucket would collect the water and we could then use it to flush the atlas. |
| scenario-ambient-59f0a53e | ambient | sample0 | 17 | -29.2 | +3.71 | +0.218 | 0.60 | 0.71 | A heavy bucket would help to collect the water and keep it from the atlas. |
| scenario-ambient-59f0a53e | ambient | sample1 | 13 | -26.7 | +3.65 | +0.281 | 0.67 | 0.33 | I'm going to go back and wash the hats. |
| scenario-ambient-59f0a53e | ambient | sample2 | 14 | -26.4 | -0.86 | -0.061 | 0.60 | 0.18 | A dark bucket may be more practical than a piece of cardboard. |
| scenario-ambient-59f0a53e | ambient | sample3 | 29 | -54.2 | -0.06 | -0.002 | 0.67 | 0.22 | A rainbow is said to be formed when the Earth's magnetic field is disturbed by a passing o |
| scenario-ambient-e9acea13 | ambient | greedy | 12 | -20.3 | +5.27 | +0.440 | 0.00 | 1.00 | The moon is the harbinger of the harvest moon. |
| scenario-ambient-e9acea13 | ambient | sample0 | 10 | -30.5 | +6.20 | +0.620 | 0.50 | 0.50 | The big moon has come out and is full. |
| scenario-ambient-e9acea13 | ambient | sample1 | 26 | -50.7 | +4.80 | +0.185 | 0.50 | 0.67 | The image programme of the moon may be taken as a crude example of what is meant by the te |
| scenario-ambient-e9acea13 | ambient | sample2 | 38 | -92.5 | +3.92 | +0.103 | 0.00 | 1.00 | Immediately before the full moon in this song is called into question by the appearance of |
| scenario-ambient-e9acea13 | ambient | sample3 | 4 | -9.5 | +0.46 | +0.116 | 0.00 | 1.00 | Harvest Moon. |
| scenario-ambient-f5e0f596 | ambient | greedy | 11 | -23.8 | +1.34 | +0.122 | 0.25 | 0.50 | The fox is just sitting there, looking very tired. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 12 | -11.9 | +1.49 | +0.124 | 0.67 | 0.40 | The fox looked up from his food and saw the rat. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 12 | -33.0 | +3.09 | +0.258 | 0.50 | 0.38 | The fox is clearly not interested in anything except its survival. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 19 | -52.9 | -0.42 | -0.022 | 0.17 | 0.40 | The Fox took a rest in the courtyard and sat up next to the burning tree. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 9 | -25.8 | +0.06 | +0.007 | 0.62 | 0.50 | The fox is very content to be here. |
| scenario-callback-2fa8e1d6 | callback | greedy | 6 | -16.9 | +1.56 | +0.260 | 0.50 | 0.60 | The one who said hi. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 8 | -28.6 | -1.57 | -0.196 | 0.67 | 0.60 | The one who chose the small lamp. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 9 | -20.1 | +2.24 | +0.248 | 0.75 | 0.60 | The one who brought the i's. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 4 | -10.3 | +3.71 | +0.926 | 0.67 | 0.33 | The talking dog. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 6 | -19.0 | -1.97 | -0.328 | 0.67 | 0.33 | Leary. The sun. |
| scenario-callback-60b06090 | callback | greedy | 10 | -14.7 | +0.40 | +0.040 | 0.38 | 1.00 | Ember said the cat was a terrible name. |
| scenario-callback-60b06090 | callback | sample0 | 13 | -20.2 | +2.95 | +0.227 | 0.40 | 1.00 | Ember said the cat was a terrible name for a pet. |
| scenario-callback-60b06090 | callback | sample1 | 16 | -32.8 | +0.73 | +0.046 | 0.40 | 0.38 | The name came from a German Shepherd cross and is still being used. |
| scenario-callback-60b06090 | callback | sample2 | 12 | -17.0 | +1.19 | +0.099 | 0.67 | 0.71 | Hey, I forgot the name of the cat! |
| scenario-callback-60b06090 | callback | sample3 | 11 | -10.7 | +4.25 | +0.387 | 0.50 | 0.71 | I said the name of the cat was Turnip. |
| scenario-callback-76c2d87f | callback | greedy | 13 | -11.3 | +5.27 | +0.405 | 0.50 | 0.80 | Four hundred and twenty-seven, the number of the book. |
| scenario-callback-76c2d87f | callback | sample0 | 8 | -10.4 | -1.12 | -0.140 | 0.40 | 0.80 | Four, the number of the house. |
| scenario-callback-76c2d87f | callback | sample1 | 63 | -34.5 | +0.31 | +0.005 | 0.67 | 1.00 | Four hundred and twenty-four, four hundred and twenty-three, four hundred and twenty-two,  |
| scenario-callback-76c2d87f | callback | sample2 | 14 | -26.4 | -0.26 | -0.019 | 0.60 | 1.00 | Four hundred, four, one. Four hundred and forty-one. |
| scenario-callback-76c2d87f | callback | sample3 | 8 | -7.7 | +2.18 | +0.273 | 0.50 | 0.80 | Four, the number of us all. |
| scenario-callback-780de0d2 | callback | greedy | 64 | -67.2 | -0.16 | -0.003 | 0.33 | 0.40 | (page 212) - I was checking out the library, and everything was fine. (page 213) - I was o |
| scenario-callback-780de0d2 | callback | sample0 | 8 | -16.4 | +0.92 | +0.116 | 0.83 | 0.29 | You may have picked a different one. |
| scenario-callback-780de0d2 | callback | sample1 | 13 | -33.2 | -4.83 | -0.372 | 0.67 | 0.44 | You must have been on the eleven-page-range. |
| scenario-callback-780de0d2 | callback | sample2 | 14 | -38.0 | -0.27 | -0.019 | 0.83 | 0.00 | "Anarchy Is Slavery With No Slave' |
| scenario-callback-780de0d2 | callback | sample3 | 12 | -25.8 | -1.61 | -0.134 | 0.50 | 0.44 | It was the last page you were on before losing it. |
| scenario-callback-7ca729b6 | callback | greedy | 24 | -23.7 | +0.72 | +0.030 | 0.67 | 0.46 | The lighthouse is the symbol of the spiritual sun, and its architecture is a microcosm of  |
| scenario-callback-7ca729b6 | callback | sample0 | 21 | -51.4 | +3.94 | +0.187 | 0.60 | 0.43 | As the tradition goes, the lighthouse is made by clinging to the back of a book. |
| scenario-callback-7ca729b6 | callback | sample1 | 64 | -85.9 | +2.47 | +0.039 | 0.65 | 0.46 | It is said to be a record of the adventures of the pilgrim, and the progress of the lighth |
| scenario-callback-7ca729b6 | callback | sample2 | 19 | -45.4 | -0.73 | -0.038 | 0.67 | 0.46 | It was once a place of dispute between the captain and the lighthouse keepers. |
| scenario-callback-7ca729b6 | callback | sample3 | 17 | -25.7 | +0.27 | +0.016 | 0.67 | 0.42 | As the owner of the lighthouse, he is responsible for keeping it burning. |
| scenario-callback-949d8fe6 | callback | greedy | 27 | -58.8 | -0.32 | -0.012 | 0.67 | 0.25 | Bias is correct. / was born in 1969 in Chicago, but / have always lived in Chicago. |
| scenario-callback-949d8fe6 | callback | sample0 | 22 | -44.7 | -2.23 | -0.102 | 0.33 | 0.45 | BOTH Of YOU ARE WRONG. THE MOON IS LODEING IN 1972. |
| scenario-callback-949d8fe6 | callback | sample1 | 33 | -68.0 | +2.55 | +0.077 | 0.75 | 0.18 | Bias is describing the physical facts while “me” is trying to lead the reader to the logic |
| scenario-callback-949d8fe6 | callback | sample2 | 2 | -7.0 | +0.51 | +0.254 | 0.00 | 1.00 | Right. |
| scenario-callback-949d8fe6 | callback | sample3 | 36 | -68.3 | -1.82 | -0.050 | 0.50 | 1.00 | Bias is technically right, but moon landings did not occur on the 69th day of the 7th mont |
| scenario-callback-9cfde584 | callback | greedy | 23 | -38.4 | +1.21 | +0.053 | 0.67 | 0.29 | It’s okay to be here all night, I’m just going to have a look at the stars. |
| scenario-callback-9cfde584 | callback | sample0 | 16 | -45.7 | +1.36 | +0.085 | 0.50 | 0.40 | My airplane got stuck in the aisle of a restauial. |
| scenario-callback-9cfde584 | callback | sample1 | 24 | -40.4 | +0.20 | +0.008 | 0.75 | 0.57 | I have been as naive as you are, Mr. President, but I think you are more than naive. |
| scenario-callback-9cfde584 | callback | sample2 | 17 | -44.3 | +2.23 | +0.131 | 0.50 | 0.40 | It is just a little exercise in time, a tiny portion of the endless present. |
| scenario-callback-9cfde584 | callback | sample3 | 8 | -17.8 | +1.42 | +0.177 | 1.00 | 0.57 | Have you been drinking any more coffee? |
| scenario-callback-9e6d06e0 | callback | greedy | 13 | -16.8 | +2.09 | +0.161 | 0.20 | 0.50 | The meeting is at 9:00 in the morning. |
| scenario-callback-9e6d06e0 | callback | sample0 | 21 | -53.1 | -0.93 | -0.044 | 0.40 | 0.43 | At the public telegraph office at the entrance to the park is a large set of telegraph wir |
| scenario-callback-9e6d06e0 | callback | sample1 | 23 | -65.2 | +3.35 | +0.146 | 0.40 | 0.43 | At the business end of the room, there is a standing ovation as members read and respond t |
| scenario-callback-9e6d06e0 | callback | sample2 | 13 | -16.8 | +2.09 | +0.161 | 0.20 | 0.50 | The meeting is at 9:00 in the morning. |
| scenario-callback-9e6d06e0 | callback | sample3 | 15 | -63.9 | -0.97 | -0.065 | 0.40 | 0.50 | At the private east-side address, which house is it kept in? |
| scenario-callback-a141de7e | callback | greedy | 16 | -25.4 | +0.23 | +0.014 | 0.62 | 0.69 | Portugal is a beautiful country and she is going to be flying from there. |
| scenario-callback-a141de7e | callback | sample0 | 12 | -16.2 | -0.43 | -0.035 | 0.67 | 0.70 | Portugal is a beautiful country and the people very kind. |
| scenario-callback-a141de7e | callback | sample1 | 27 | -56.9 | -0.82 | -0.030 | 0.50 | 0.70 | Portugal is a beautiful country and she is going to my favorite vacation spot in the colle |
| scenario-callback-a141de7e | callback | sample2 | 21 | -64.4 | +2.57 | +0.122 | 0.67 | 0.30 | She is very nice. I have a briefcase full of books about sao deinheiro. |
| scenario-callback-a141de7e | callback | sample3 | 8 | -6.0 | -0.39 | -0.049 | 0.50 | 0.50 | Lisbon,Portugal. |
| scenario-callback-c4f608c3 | callback | greedy | 64 | -102.1 | -2.81 | -0.044 | 0.33 | 0.33 | We were talking about the Mississippi, the Columbia, the Pecatonica, the Wiscotonean, the  |
| scenario-callback-c4f608c3 | callback | sample0 | 13 | -25.9 | -1.58 | -0.121 | 0.50 | 0.27 | We were looking at the different rivers that flow into the ocean. |
| scenario-callback-c4f608c3 | callback | sample1 | 30 | -55.3 | -1.67 | -0.056 | 0.33 | 0.33 | We were talking about the Ming and the Ming-Kwan of the cosmology of the Three Kingdoms pe |
| scenario-callback-c4f608c3 | callback | sample2 | 13 | -40.7 | +2.55 | +0.197 | 0.50 | 0.12 | The Lotus Root races are very short, very good. |
| scenario-callback-c4f608c3 | callback | sample3 | 9 | -34.5 | +3.37 | +0.375 | 0.67 | 0.33 | Talking about nothing motivates no one. |
| scenario-callback-d79a0d3a | callback | greedy | 30 | -47.3 | +3.87 | +0.129 | 0.67 | 0.44 | It was first translated as "a place where there were many kinds of trees" and then given t |
| scenario-callback-d79a0d3a | callback | sample0 | 21 | -55.9 | +4.73 | +0.225 | 0.67 | 0.29 | To this day, the house of the dead may be called a grisaille or attic. |
| scenario-callback-d79a0d3a | callback | sample1 | 9 | -22.8 | -1.01 | -0.112 | 0.29 | 0.71 | It is the door to the reading room. |
| scenario-callback-d79a0d3a | callback | sample2 | 14 | -29.7 | +3.70 | +0.264 | 0.38 | 0.71 | Yea, the door to the reading room was an orchard. |
| scenario-callback-d79a0d3a | callback | sample3 | 41 | -75.8 | +5.89 | +0.144 | 0.62 | 0.67 | To go back to the text itself, the opening of the door was described in the following term |
| scenario-callback-d8a5957e | callback | greedy | 12 | -27.7 | -1.27 | -0.106 | 0.40 | 0.33 | The blue one is about the honeybee and its task. |
| scenario-callback-d8a5957e | callback | sample0 | 50 | -104.9 | -1.90 | -0.038 | 0.50 | 0.38 | The eyes of the bee are like those of a saint, for they are not on the top of the head as  |
| scenario-callback-d8a5957e | callback | sample1 | 15 | -22.8 | +0.62 | +0.041 | 0.50 | 0.54 | The life of the honey bee is a study in both geography and astronomy. |
| scenario-callback-d8a5957e | callback | sample2 | 35 | -70.1 | +1.60 | +0.046 | 0.50 | 0.54 | The honey bee, like many other flowering plants, has both male and female reproductive org |
| scenario-callback-d8a5957e | callback | sample3 | 29 | -61.8 | +3.20 | +0.110 | 0.60 | 0.31 | The mystical or symbolic scale of the bee is identical with that of the magician, which is |
| scenario-direct-3f84da0f | direct | greedy | 18 | -48.0 | +0.00 | +0.000 | 0.56 | 0.22 | It was before we even came in that I was picking up rocks with a broom. |
| scenario-direct-3f84da0f | direct | sample0 | 11 | -28.7 | +0.00 | +0.000 | 0.75 | 0.22 | I was just filing the blood off my clothes. |
| scenario-direct-3f84da0f | direct | sample1 | 32 | -76.1 | +0.00 | +0.000 | 0.50 | 0.22 | The wenupower of the universe was there, also, and in the presence of his wenupower, there |
| scenario-direct-3f84da0f | direct | sample2 | 42 | -131.6 | +0.00 | +0.000 | 0.50 | 0.21 | You pre-cumuled the art of working with words, the science of working with minerals, the h |
| scenario-direct-3f84da0f | direct | sample3 | 29 | -62.5 | +0.00 | +0.000 | 0.67 | 0.21 | The two U.S. soldiers and two Japanese went back to their tents, the Japanese in the back  |
| scenario-direct-5d3dc8de | direct | greedy | 14 | -25.7 | +0.00 | +0.000 | 0.70 | 0.50 | Of course, truth is not the goal, but rather the means. |
| scenario-direct-5d3dc8de | direct | sample0 | 41 | -92.4 | +0.00 | +0.000 | 0.65 | 0.30 | His magnetism, as we know, is due to the fact that he has been able to penetrate the mater |
| scenario-direct-5d3dc8de | direct | sample1 | 10 | -22.6 | +0.00 | +0.000 | 0.75 | 0.38 | The nuclear bomb was not the invention of Hitler. |
| scenario-direct-5d3dc8de | direct | sample2 | 15 | -30.3 | +0.00 | +0.000 | 0.75 | 0.50 | Of course, truth is not something that can be achieved by mere statement. |
| scenario-direct-5d3dc8de | direct | sample3 | 59 | -31.1 | +0.00 | +0.000 | 0.67 | 0.30 | Modern scholarship recognises the Paracelsian movement as a vital aspect of the scientific |
| scenario-direct-645bc6e6 | direct | greedy | 28 | -50.3 | +0.00 | +0.000 | 0.67 | 0.21 | In the last century, the gold was found in the bedrock of the Hecate mountains, in what is |
| scenario-direct-645bc6e6 | direct | sample0 | 53 | -129.8 | +0.00 | +0.000 | 0.50 | 0.36 | In the early morning, when the sun is yet to rise, the Buddhist priests take their catechu |
| scenario-direct-645bc6e6 | direct | sample1 | 46 | -112.3 | +0.00 | +0.000 | 0.50 | 0.27 | In the same way, that the dinosaur represented to Cronus a super-bear, so to Hercules a hi |
| scenario-direct-645bc6e6 | direct | sample2 | 23 | -54.7 | +0.00 | +0.000 | 0.50 | 0.36 | In honour of New Year’s we also held a New Year’s celebration for the Kindreds. |
| scenario-direct-645bc6e6 | direct | sample3 | 23 | -53.8 | +0.00 | +0.000 | 0.50 | 0.21 | The things that we read about are not young things, but things that we grow to know about, |
| scenario-direct-ab11ffdb | direct | greedy | 26 | -41.1 | +0.00 | +0.000 | 0.50 | 0.60 | The rain is a natural phenomenon and its presence or absence in a given area at a given ti |
| scenario-direct-ab11ffdb | direct | sample0 | 16 | -56.2 | +0.00 | +0.000 | 0.67 | 0.64 | The rain is a divine message that comes to us from the holy fog. |
| scenario-direct-ab11ffdb | direct | sample1 | 27 | -61.4 | +0.00 | +0.000 | 0.62 | 0.40 | The new rain engineering math deals with the prediction of when and where and how much rai |
| scenario-direct-ab11ffdb | direct | sample2 | 6 | -17.5 | +0.00 | +0.000 | 0.60 | 0.60 | The rain is getting worse. |
| scenario-direct-ab11ffdb | direct | sample3 | 14 | -30.2 | +0.00 | +0.000 | 0.67 | 0.64 | The rain is a divine messenger that should be listened to. |
| scenario-direct-ad89f803 | direct | greedy | 34 | -70.8 | +0.00 | +0.000 | 0.50 | 0.44 | Theima is a name given to a region in Southwest Asia, roughly modern-day Iraq, Iran, and t |
| scenario-direct-ad89f803 | direct | sample0 | 50 | -79.9 | +0.00 | +0.000 | 0.67 | 0.33 | Or, to take another example, the sound of a hammer falling can be broken up into sounds of |
| scenario-direct-ad89f803 | direct | sample1 | 12 | -47.9 | +0.00 | +0.000 | 0.67 | 0.44 | Theima is a flower of great beauty and vibration. |
| scenario-direct-ad89f803 | direct | sample2 | 29 | -70.2 | +0.00 | +0.000 | 0.67 | 0.33 | The contrast between the ambient sound of this room (after we've warmed it up) and the hum |
| scenario-direct-ad89f803 | direct | sample3 | 55 | -10.2 | +0.00 | +0.000 | 0.65 | 0.44 | This symbol may not be immediately familiar to the average Freemason, and that is for a ve |
| scenario-direct-f3869322 | direct | greedy | 37 | -85.9 | +0.00 | +0.000 | 0.50 | 0.45 | But what of us? What of the multitude of other people who are having diVerent experiences? |
| scenario-direct-f3869322 | direct | sample0 | 43 | -18.8 | +0.00 | +0.000 | 0.50 | 0.36 | It is unnecessary to show to what an extent this attitude resembles that of the man of arc |
| scenario-direct-f3869322 | direct | sample1 | 19 | -53.9 | +0.00 | +0.000 | 0.75 | 0.45 | But what of the other big book of the year, the one of cosmic catastrophism? |
| scenario-direct-f3869322 | direct | sample2 | 27 | -81.2 | +0.00 | +0.000 | 0.65 | 0.36 | But what of us, the jaded ones, who have read far too many books whose worth it is not evi |
| scenario-direct-f3869322 | direct | sample3 | 17 | -55.5 | +0.00 | +0.000 | 0.67 | 0.36 | More should be added, but this is the basis of a new class of work. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 8 | -9.3 | -2.00 | -0.250 | 0.40 | 0.60 | Brown, the brown of old books. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 8 | -9.3 | -2.00 | -0.250 | 0.40 | 0.60 | Brown, the brown of old books. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 17 | -23.1 | -1.18 | -0.069 | 0.40 | 0.40 | Green and blue, the green of plants and animals, the blue of the sky. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 25 | -60.9 | -6.97 | -0.279 | 0.40 | 0.40 | It's green. Green, to my peeping Tom eyes. Green, the green of the land. Green. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 10 | -16.5 | +2.47 | +0.247 | 0.60 | 0.60 | Brown, the brown of new mornings. |
| scenario-disagreement-31892fde | disagreement | greedy | 16 | -35.7 | +3.57 | +0.223 | 0.55 | 0.36 | In the presence of the Holy Silence, the student has nothing to learn. |
| scenario-disagreement-31892fde | disagreement | sample0 | 11 | -33.5 | -1.33 | -0.121 | 0.43 | 0.50 | It is the just-voiced absence of speech. |
| scenario-disagreement-31892fde | disagreement | sample1 | 19 | -40.2 | +2.99 | +0.157 | 0.43 | 0.38 | In the silence of non-speech, the heart stands still and the head moves forward. |
| scenario-disagreement-31892fde | disagreement | sample2 | 19 | -44.1 | +0.82 | +0.043 | 0.55 | 0.50 | It is also the darkest of night and the resting point of the day. |
| scenario-disagreement-31892fde | disagreement | sample3 | 17 | -39.3 | +2.06 | +0.121 | 0.69 | 0.25 | The poet laureate will not need to speak when he/she is silent. |
| scenario-disagreement-352205c6 | disagreement | greedy | 11 | -30.3 | +1.38 | +0.126 | 0.50 | 0.56 | As earth does a dance, so do the dead. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 30 | -68.3 | +6.30 | +0.210 | 0.33 | 0.42 | It is as if they were sentient beings, capable of altering their physical appearance and,  |
| scenario-disagreement-352205c6 | disagreement | sample1 | 21 | -45.5 | +6.70 | +0.319 | 0.50 | 0.50 | The dead are in the firmament as the sun and the moon and as reflections of the living. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 15 | -40.2 | -2.24 | -0.150 | 0.67 | 0.56 | As earth is a closed system, it won’t hold the dead. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 34 | -82.2 | +2.39 | +0.070 | 0.50 | 0.50 | As the sun goes down, they all feel the pain of the earth, and some die young, some are si |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 13 | -20.8 | +3.61 | +0.278 | 0.25 | 0.75 | Books are created in the autumn; the leaves are not. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 16 | -36.3 | -7.29 | -0.456 | 0.33 | 0.50 | Books, when they are not open to be read, are the poorest. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 10 | -46.6 | -17.86 | -1.786 | 0.20 | 0.60 | Books, when hot and books, autumn. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 25 | -49.5 | +4.21 | +0.169 | 0.44 | 0.75 | Books are created in the midst of autumn, and readers are attentive to the midst of autumn |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 34 | -82.1 | -17.22 | -0.507 | 0.22 | 0.62 | Books are rarely read during the autumn. The leaves are usually done by then, and there is |
| scenario-disagreement-682bad9c | disagreement | greedy | 7 | -6.0 | +4.39 | +0.627 | 0.20 | 0.80 | A program is a reading place. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 7 | -6.0 | +4.39 | +0.627 | 0.20 | 0.80 | A program is a reading place. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 12 | -12.6 | +10.71 | +0.892 | 0.43 | 0.80 | A program is a reading situation where there is a computer. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 8 | -5.6 | +6.36 | +0.795 | 0.50 | 0.80 | A program is a way of reading. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 9 | -8.5 | +2.44 | +0.272 | 0.29 | 0.80 | A program is a place where programming happens. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 16 | -27.2 | +5.60 | +0.350 | 0.40 | 0.67 | Contents are what primarily determine the organization of the library, not physical determ |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 15 | -27.2 | +7.91 | +0.527 | 0.50 | 0.62 | Contents are subsystems of the library, and the subsystems are systems. |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 30 | -63.2 | +4.94 | +0.165 | 0.30 | 0.50 | Contents are arranged in this system according to subject matter or subjectishness, which  |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 23 | -64.2 | -2.88 | -0.125 | 0.40 | 0.67 | Contents are not what primarily define a library. Secondly, the definition of a library mu |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 20 | -57.8 | -9.06 | -0.453 | 0.40 | 0.38 | The library building is a physical expression of a metaphysical system, of a hidden way of |
| scenario-disagreement-89dfdafc | disagreement | greedy | 13 | -22.0 | +1.94 | +0.149 | 0.50 | 0.50 | It is a sea of action, not a sea of reaction. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 37 | -77.7 | +4.09 | +0.111 | 0.25 | 0.40 | It is the celadistic sea, the blue and the purple, the black and the white, the sea that h |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 18 | -28.2 | +3.17 | +0.176 | 0.50 | 0.60 | The tide doesn’t have a point, the point is always the tide. |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 14 | -57.6 | -7.10 | -0.507 | 0.70 | 0.50 | It is a continuous tasker that moves, it does not stop. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 10 | -4.5 | +5.15 | +0.515 | 0.40 | 0.60 | The tide is the sea's memory. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 45 | -90.8 | -8.21 | -0.182 | 0.50 | 0.67 | But nonsense can be art that is, and that art may be so great that it creates a new langua |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 18 | -42.1 | -3.55 | -0.197 | 0.10 | 0.64 | All the nonsense that has not yet found its place in the sentence is clouds. |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 29 | -52.0 | +11.66 | +0.402 | 0.60 | 0.45 | But sense can become nonsense only after it has been sent; and the sentence can become non |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 16 | -46.2 | -13.22 | -0.826 | 0.38 | 0.64 | All the nonsense is in the collection. It has not been rejected. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 27 | -76.3 | -14.59 | -0.540 | 0.70 | 0.67 | But nonsense can be art that is, and that art, which is, and that which is, ultimately, al |
| scenario-joke-29f5cda1 | joke | greedy | 17 | -27.3 | +1.42 | +0.083 | 0.67 | 0.40 | The fish that can’t see anything is called a ‘black’ fish. |
| scenario-joke-29f5cda1 | joke | sample0 | 14 | -23.9 | +10.21 | +0.729 | 0.78 | 0.20 | If you had to rate it, it’d be a nine. |
| scenario-joke-29f5cda1 | joke | sample1 | 9 | -14.6 | -1.37 | -0.152 | 0.33 | 0.50 | It's a fish with ten eyes. |
| scenario-joke-29f5cda1 | joke | sample2 | 14 | -19.6 | -0.46 | -0.033 | 0.67 | 0.50 | The fish with the most eyes is the one with the least brain. |
| scenario-joke-29f5cda1 | joke | sample3 | 7 | -10.5 | +0.22 | +0.032 | 0.60 | 0.40 | Ten to one, that is. |
| scenario-joke-31378921 | joke | greedy | 4 | -7.5 | +3.85 | +0.963 | 0.33 | 0.33 | Who comes there? |
| scenario-joke-31378921 | joke | sample0 | 10 | -13.6 | +0.50 | +0.050 | 0.67 | 0.33 | I don’t know. Who are you? |
| scenario-joke-31378921 | joke | sample1 | 10 | -16.8 | -0.06 | -0.006 | 0.75 | 0.17 | I am looking for the master of this place. |
| scenario-joke-31378921 | joke | sample2 | 18 | -38.6 | +5.96 | +0.331 | 0.79 | 0.11 | No one, it’s just a bunch of old books lying on their sides. |
| scenario-joke-31378921 | joke | sample3 | 7 | -17.1 | -2.12 | -0.303 | 0.83 | 0.17 | I need to find my husband. |
| scenario-joke-31c4c1ec | joke | greedy | 28 | -51.9 | +0.00 | +0.000 | 0.65 | 0.33 | This is a hermetic journal and no part of it is to be found or used in any way whatsoever  |
| scenario-joke-31c4c1ec | joke | sample0 | 10 | -23.4 | +0.00 | +0.000 | 0.67 | 0.44 | This is the only thing I have to offer. |
| scenario-joke-31c4c1ec | joke | sample1 | 27 | -57.1 | +0.00 | +0.000 | 0.50 | 0.33 | The art of roasting the meat is a technique that involves cooking the joint in a special w |
| scenario-joke-31c4c1ec | joke | sample2 | 12 | -27.2 | +0.00 | +0.000 | 0.67 | 0.44 | This is not the place to welcome you, sir. |
| scenario-joke-31c4c1ec | joke | sample3 | 29 | -8.2 | +0.00 | +0.000 | 0.50 | 0.33 | This is a non-profit organization of people who take an active interest in unusual happeni |
| scenario-joke-475a7b10 | joke | greedy | 13 | -26.2 | -0.39 | -0.030 | 0.67 | 0.40 | Laughter is a beautiful thing and it is something we enjoy. |
| scenario-joke-475a7b10 | joke | sample0 | 30 | -77.5 | +1.72 | +0.057 | 0.67 | 0.20 | Something horrible and funny happened last week and something really terrible and painful  |
| scenario-joke-475a7b10 | joke | sample1 | 10 | -30.7 | +0.30 | +0.030 | 0.75 | 0.12 | That’s all the word he has said. |
| scenario-joke-475a7b10 | joke | sample2 | 25 | -97.7 | +1.27 | +0.051 | 0.75 | 0.20 | The Tunnelopanic Millennium is now celebrated with the age-old laughing stock, the joke. |
| scenario-joke-475a7b10 | joke | sample3 | 9 | -35.7 | +0.57 | +0.063 | 0.80 | 0.40 | WHAT IS LIKE A NATION? |
| scenario-joke-99a4a91d | joke | greedy | 12 | -29.4 | +0.00 | +0.000 | 0.62 | 0.60 | Because the doctor had the most to gain by its publication. |
| scenario-joke-99a4a91d | joke | sample0 | 34 | -65.0 | +0.00 | +0.000 | 0.50 | 0.54 | But the book went to the doctor because, she said, he knew the name of the place where the |
| scenario-joke-99a4a91d | joke | sample1 | 51 | -108.9 | +0.00 | +0.000 | 0.50 | 0.54 | But the book went to the doctor because, she said, he recognized the picture on the desk—i |
| scenario-joke-99a4a91d | joke | sample2 | 9 | -27.7 | +0.00 | +0.000 | 0.43 | 0.43 | Did the book give the doctor a message? |
| scenario-joke-99a4a91d | joke | sample3 | 34 | -102.2 | +0.00 | +0.000 | 0.50 | 0.60 | Because, when the book was sent to the doctor he or she had notified us of the need for it |
| scenario-joke-a6247299 | joke | greedy | 14 | -23.9 | +0.00 | +0.000 | 0.50 | 0.45 | A sense of humour is something I certainly don’t lack. |
| scenario-joke-a6247299 | joke | sample0 | 27 | -49.4 | +0.00 | +0.000 | 0.67 | 0.20 | Laughter is a biological impulse, deeply rooted in human anatomy, and whether we laugh or  |
| scenario-joke-a6247299 | joke | sample1 | 34 | -63.2 | +0.00 | +0.000 | 0.50 | 0.45 | A sense of humour does appear in many of your writings, but I am sorry to say that in your |
| scenario-joke-a6247299 | joke | sample2 | 41 | -72.7 | +0.00 | +0.000 | 0.38 | 0.45 | In a similar vein, Steiner advises that we should all have a sense of humor "when necessar |
| scenario-joke-a6247299 | joke | sample3 | 15 | -37.8 | +0.00 | +0.000 | 0.50 | 0.45 | A sense of humour never arises when reading a silently written text. |
| scenario-joke-e8ab9225 | joke | greedy | 15 | -23.7 | -1.37 | -0.091 | 0.50 | 0.60 | Dov, do you believe in the existence of the Library Ghost? |
| scenario-joke-e8ab9225 | joke | sample0 | 27 | -35.8 | +4.74 | +0.175 | 0.33 | 0.60 | Dov, do not laugh at me. I am the ghost of one of the great warriors who have died in batt |
| scenario-joke-e8ab9225 | joke | sample1 | 34 | -74.3 | +5.32 | +0.157 | 0.50 | 0.60 | AUFOLOGIST DOV SPOKE SOME OF THE TECHNOLOGY BEHIND THE MIRACLE OF THE Ghost in the Library |
| scenario-joke-e8ab9225 | joke | sample2 | 24 | -50.8 | -0.18 | -0.007 | 0.75 | 0.30 | Dov, please don't believe this! I'm just a common, average, everyday, successful ghost! |
| scenario-joke-e8ab9225 | joke | sample3 | 29 | -73.9 | +4.00 | +0.138 | 0.75 | 0.40 | Dov, the character Dov, here portrayed by the author of the book, is presented as being ne |
| scenario-joke-e9cf6a04 | joke | greedy | 23 | -35.0 | +9.49 | +0.413 | 0.33 | 0.36 | He finds a copy of Wagner’s 40th Piano Trio in the back room. |
| scenario-joke-e9cf6a04 | joke | sample0 | 11 | -16.9 | -0.34 | -0.031 | 0.00 | 0.67 | He finds a book and sits down to read. |
| scenario-joke-e9cf6a04 | joke | sample1 | 13 | -16.7 | +3.17 | +0.244 | 0.75 | 0.25 | He asks the librarian for books on homosexuality. |
| scenario-joke-e9cf6a04 | joke | sample2 | 17 | -41.5 | -3.39 | -0.199 | 0.00 | 0.67 | He finds a book about blind men and shows it to the lady in waiting. |
| scenario-joke-e9cf6a04 | joke | sample3 | 12 | -13.2 | +2.85 | +0.237 | 0.80 | 0.50 | He says, “I want to borrow a book. |
| scenario-request-2826c958 | request | greedy | 26 | -68.6 | +0.00 | +0.000 | 0.29 | 0.67 | These facts about the moon are presented to us in a sequence: five facts about the moon in |
| scenario-request-2826c958 | request | sample0 | 31 | -61.9 | +0.00 | +0.000 | 0.57 | 0.21 | The five questions that you did not answer were: 1) Did the astronauts bring back any back |
| scenario-request-2826c958 | request | sample1 | 13 | -44.3 | +0.00 | +0.000 | 0.50 | 0.45 | These are known as the five classical points of the lunar mountain. |
| scenario-request-2826c958 | request | sample2 | 43 | -57.8 | +0.00 | +0.000 | 0.50 | 0.40 | We are considering the following five statements: (1) The moon is hollow. (2) The moon is  |
| scenario-request-2826c958 | request | sample3 | 48 | -114.1 | +0.00 | +0.000 | 0.43 | 0.67 | These facts about the moon are presented to us, by way of an exhibition, in order that, as |
| scenario-request-2868e594 | request | greedy | 23 | -26.4 | +0.00 | +0.000 | 0.75 | 0.19 | It should be about 300 words in length, typed on two pages, and double spaced throughout. |
| scenario-request-2868e594 | request | sample0 | 27 | -71.1 | +0.00 | +0.000 | 0.75 | 0.21 | McCawley had previously covered the design and licensing of non-traditional images and the |
| scenario-request-2868e594 | request | sample1 | 17 | -40.7 | +0.00 | +0.000 | 0.71 | 0.43 | This cover letter is to be considered as your introduction to the contents of the book. |
| scenario-request-2868e594 | request | sample2 | 46 | -104.6 | +0.00 | +0.000 | 0.67 | 0.43 | While it is important that the cover letter does not state the obvious—that the artwork wi |
| scenario-request-2868e594 | request | sample3 | 33 | -86.5 | +0.00 | +0.000 | 0.75 | 0.29 | While it is admirable that you are willing to act as your own editor, it is also a shame t |
| scenario-request-41c58fb2 | request | greedy | 50 | -18.6 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample0 | 50 | -18.6 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample1 | 50 | -18.6 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample2 | 50 | -18.6 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample3 | 50 | -18.6 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-8aa8e374 | request | greedy | 35 | -44.6 | +0.00 | +0.000 | 1.00 | 0.00 | Chaque étape ou processus se répercute successivement dans le ventre de la dernière idole  |
| scenario-request-8aa8e374 | request | sample0 | 15 | -22.6 | +0.00 | +0.000 | 0.67 | 0.45 | The English translation "good night" is not readily available in French. |
| scenario-request-8aa8e374 | request | sample1 | 15 | -29.3 | +0.00 | +0.000 | 0.75 | 0.43 | The French translation would be : Adieu, anglais! |
| scenario-request-8aa8e374 | request | sample2 | 40 | -128.8 | +0.00 | +0.000 | 0.67 | 0.45 | The Good Night Chant GOOO doe GOOO is another example of how a simple and unproblematic fr |
| scenario-request-8aa8e374 | request | sample3 | 35 | -44.6 | +0.00 | +0.000 | 1.00 | 0.00 | Chaque étape ou processus se répercute successivement dans le ventre de la dernière idole  |
| scenario-request-b2a25087 | request | greedy | 7 | -21.1 | +0.00 | +0.000 | 0.33 | 1.00 | Call it a customer service agent. |
| scenario-request-b2a25087 | request | sample0 | 21 | -44.2 | +0.00 | +0.000 | 0.75 | 0.25 | They will not be bothered by your presence unless they know you are here to serve them som |
| scenario-request-b2a25087 | request | sample1 | 18 | -31.7 | +0.00 | +0.000 | 0.60 | 1.00 | Call it a customer service agent if you will, but it’s not customer service. |
| scenario-request-b2a25087 | request | sample2 | 11 | -15.4 | +0.00 | +0.000 | 0.75 | 0.22 | Customer: What are you both doing in my shop? |
| scenario-request-b2a25087 | request | sample3 | 24 | -62.0 | +0.00 | +0.000 | 0.75 | 0.67 | Call it customer service if you will, but it is the relationship that is important, and th |
| scenario-request-b3bd0087 | request | greedy | 35 | -24.0 | +0.00 | +0.000 | 0.75 | 0.20 | The new SOUL TOILET DIAGRAM (See next page) with the Satanism/Saturn core is the core of z |
| scenario-request-b3bd0087 | request | sample0 | 7 | -18.5 | +0.00 | +0.000 | 0.60 | 0.80 | The usual: clear and sunny. |
| scenario-request-b3bd0087 | request | sample1 | 40 | -104.4 | +0.00 | +0.000 | 0.50 | 0.80 | The new soilder weather map has "impressive" colors in it, It shows we'll have clear days  |
| scenario-request-b3bd0087 | request | sample2 | 35 | -24.0 | +0.00 | +0.000 | 0.75 | 0.20 | The new SOUL TOILET DIAGRAM (See next page) with the Satanism/Saturn core is the core of z |
| scenario-request-b3bd0087 | request | sample3 | 39 | -64.0 | +0.00 | +0.000 | 0.50 | 0.20 | The Philadelphia Botanic Garden received a total of 79.4 inches of rainfall during the 197 |
| scenario-silence-109161ca | silence | greedy | 26 | -50.8 | +2.98 | +0.115 | 0.67 | 0.45 | To the great confusion of the reader of the great work, we have here a small selection of  |
| scenario-silence-109161ca | silence | sample0 | 23 | -65.1 | -6.05 | -0.263 | 0.73 | 0.33 | To him the earth was the only reality, and the experience of his own earthly surroundings  |
| scenario-silence-109161ca | silence | sample1 | 24 | -51.7 | -3.03 | -0.126 | 0.67 | 0.22 | To function effectively in our spiritual quest, we must reject the false dichotomies that  |
| scenario-silence-109161ca | silence | sample2 | 21 | -44.8 | -0.99 | -0.047 | 0.00 | 0.45 | To the great confusion of the great many, the meaning of the word "night" is unknown. |
| scenario-silence-109161ca | silence | sample3 | 11 | -36.3 | -4.48 | -0.407 | 0.56 | 0.44 | To the nth degree of clarity the moon is white. |
| scenario-silence-260b2639 | silence | greedy | 14 | -31.0 | +0.00 | +0.000 | 0.67 | 0.20 | Underground, no, now that is what I am thinking of. |
| scenario-silence-260b2639 | silence | sample0 | 49 | -105.7 | +0.00 | +0.000 | 0.50 | 0.20 | Answer: The thought of such a thing goes so far that some of our most experienced submersi |
| scenario-silence-260b2639 | silence | sample1 | 29 | -47.5 | +0.00 | +0.000 | 0.75 | 0.25 | This wouldn’t affect the Earth’s gravity, the water table, or the availability of food; al |
| scenario-silence-260b2639 | silence | sample2 | 41 | -88.2 | +0.00 | +0.000 | 0.50 | 0.33 | This would have the effect of concentrating the psychic energy of the dead in a single poi |
| scenario-silence-260b2639 | silence | sample3 | 7 | -11.7 | +0.00 | +0.000 | 0.83 | 0.33 | This is a very serious matter. |
| scenario-silence-46189e08 | silence | greedy | 36 | -80.2 | +0.00 | +0.000 | 0.67 | 0.40 | It may have taken a little while for the email to reach the labeling of the message, which |
| scenario-silence-46189e08 | silence | sample0 | 15 | -45.7 | +0.00 | +0.000 | 0.50 | 0.14 | Replying now means replying means reading and replying means responding again. |
| scenario-silence-46189e08 | silence | sample1 | 22 | -59.7 | +0.00 | +0.000 | 0.50 | 0.40 | Responding to a message is a great way of letting others know that you are actively proces |
| scenario-silence-46189e08 | silence | sample2 | 8 | -18.5 | +0.00 | +0.000 | 0.80 | 0.40 | It may sound strange, but ... |
| scenario-silence-46189e08 | silence | sample3 | 20 | -54.6 | +0.00 | +0.000 | 0.83 | 0.40 | Responding to a message is something that must be done by a user, not by an entity. |
| scenario-silence-53534987 | silence | greedy | 26 | -53.2 | -1.27 | -0.049 | 0.25 | 0.23 | Emblematic of the death of the old LP mechanism is the appearance of the Charger Battery i |
| scenario-silence-53534987 | silence | sample0 | 14 | -39.1 | +7.68 | +0.549 | 1.00 | 0.14 | Some models charge at 3DOF or 4DOF. |
| scenario-silence-53534987 | silence | sample1 | 49 | -108.0 | +1.76 | +0.036 | 0.50 | 0.23 | These capacitors will store 1000 times more electrical charge than the average house capac |
| scenario-silence-53534987 | silence | sample2 | 9 | -8.6 | -0.07 | -0.008 | 0.83 | 0.25 | You may have to buy a new one. |
| scenario-silence-53534987 | silence | sample3 | 17 | -27.7 | +6.15 | +0.362 | 0.67 | 0.25 | It was a hard loss to us, but it is something we will never forget. |
| scenario-silence-78c38840 | silence | greedy | 23 | -49.9 | -1.82 | -0.079 | 0.50 | 0.21 | As soon as the jam is gone, as soon as the mechanical problems are solved, we will print a |
| scenario-silence-78c38840 | silence | sample0 | 23 | -69.4 | +2.19 | +0.095 | 0.50 | 0.30 | Ryo took a third break at noon today and came up just in time to see the print job complet |
| scenario-silence-78c38840 | silence | sample1 | 17 | -41.8 | +1.63 | +0.096 | 0.75 | 0.22 | A printer-jammed stomach can cause a printer to become unreliable. |
| scenario-silence-78c38840 | silence | sample2 | 25 | -52.4 | +2.19 | +0.087 | 0.50 | 0.30 | Does not appear to be jammed, but the paper is stained and coffee grounds are soaking thro |
| scenario-silence-78c38840 | silence | sample3 | 12 | -38.4 | -1.78 | -0.148 | 0.50 | 0.30 | The printer is still in a hot mug of coffee. |
| scenario-silence-7afca726 | silence | greedy | 12 | -29.7 | -0.14 | -0.012 | 0.91 | 0.64 | But I am not sure that it will be going smoothly. |
| scenario-silence-7afca726 | silence | sample0 | 55 | -122.1 | +2.95 | +0.054 | 0.50 | 0.46 | But if the people in the street realize that the work they are seeing is not of the devil, |
| scenario-silence-7afca726 | silence | sample1 | 11 | -37.2 | +3.23 | +0.293 | 0.75 | 0.38 | But I do wish to work and to work hard. |
| scenario-silence-7afca726 | silence | sample2 | 18 | -25.8 | -1.04 | -0.058 | 0.75 | 0.46 | But if the thing doesn’t work out, well, that’s okay too. |
| scenario-silence-7afca726 | silence | sample3 | 12 | -30.5 | -0.86 | -0.071 | 0.82 | 0.64 | But I am not sure that it is a likely candidate. |
| scenario-silence-9bb13f03 | silence | greedy | 20 | -29.8 | +0.00 | +0.000 | 0.67 | 0.40 | In the early morning hours of May 26, 1947, the St. |
| scenario-silence-9bb13f03 | silence | sample0 | 25 | -14.9 | +0.00 | +0.000 | 0.75 | 0.29 | R. Ishmael said: Cheerful is the man who completes this mystery from dawn to dawn. |
| scenario-silence-9bb13f03 | silence | sample1 | 13 | -38.0 | +0.00 | +0.000 | 0.50 | 0.30 | The sounds of the book are quite different to the reading itself. |
| scenario-silence-9bb13f03 | silence | sample2 | 35 | -12.8 | +0.00 | +0.000 | 0.67 | 0.30 | In the last chapter we explained to you the difference between the sensory functions of th |
| scenario-silence-9bb13f03 | silence | sample3 | 24 | -47.2 | +0.00 | +0.000 | 0.50 | 0.40 | In the early days of white settlement, the Indians were credited with a remarkable knowled |
| scenario-silence-ccfdd2b4 | silence | greedy | 15 | -25.4 | +0.40 | +0.027 | 0.64 | 0.50 | A cup of coffee is a gift from the heavens to the earth. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 35 | -41.2 | +2.27 | +0.065 | 0.67 | 0.43 | An excellent source of high-grade coffee is The Coffee Garden, Inc., 125 West 44th Street, |
| scenario-silence-ccfdd2b4 | silence | sample1 | 13 | -23.6 | +2.67 | +0.205 | 0.67 | 0.50 | A cup of coffee is a must for all of us here. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 9 | -23.9 | +1.99 | +0.221 | 1.00 | 0.43 | An excellent source for grouse hunting equipment. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 26 | -50.5 | +2.88 | +0.111 | 0.67 | 0.45 | One thing, 'm certain of, is that without the coffee, the brisket would not have been a su |
| trace-ambient-da12ae42 | ambient | greedy | 27 | -28.6 | +6.71 | +0.248 | 0.50 | 0.38 | I'm not sure that's bizarre to me. I'm sure that's bizarre to you. |
| trace-ambient-da12ae42 | ambient | sample0 | 30 | -50.5 | +4.43 | +0.147 | 0.40 | 0.64 | it's not bizarre at all, it's all pretty normal, and i wish i could just drop out of life  |
| trace-ambient-da12ae42 | ambient | sample1 | 64 | -139.4 | -4.28 | -0.067 | 0.67 | 0.27 | HALF WINDER (a half-winder) is a hybrid of the noble and the leonine forms of ants. HALF M |
| trace-ambient-da12ae42 | ambient | sample2 | 13 | -35.3 | -1.90 | -0.146 | 0.55 | 0.64 | I wish i could cut out my own tail and study it. |
| trace-ambient-da12ae42 | ambient | sample3 | 27 | -52.3 | +1.06 | +0.039 | 0.47 | 0.38 | plant morphogenesis is a bizarre topic to study, but if you study the morphogenesis of lif |
| trace-direct-115cf61c | direct | greedy | 3 | -6.8 | +0.00 | +0.000 | 1.00 | 1.00 | I am. |
| trace-direct-115cf61c | direct | sample0 | 64 | -121.8 | +0.00 | +0.000 | 0.50 | 0.67 | It is cogent. The basic point is that when you look at things, you see through them, throu |
| trace-direct-115cf61c | direct | sample1 | 6 | -7.4 | +0.00 | +0.000 | 0.33 | 1.00 | We are cogent. |
| trace-direct-115cf61c | direct | sample2 | 10 | -33.2 | +0.00 | +0.000 | 0.80 | 1.00 | I am to Earth's cogency? |
| trace-direct-115cf61c | direct | sample3 | 7 | -9.3 | +0.00 | +0.000 | 0.50 | 1.00 | We are indeed cogent. |
| trace-direct-36d6904b | direct | greedy | 17 | -32.6 | +0.00 | +0.000 | 0.75 | 0.67 | This is the first liiiiiiiiifle that 've ever written. |
| trace-direct-36d6904b | direct | sample0 | 15 | -29.3 | +0.00 | +0.000 | 0.50 | 0.27 | We are here to welcome you into the World of Erich Zann. |
| trace-direct-36d6904b | direct | sample1 | 19 | -41.8 | +0.00 | +0.000 | 0.73 | 0.27 | Follow the logic of the beast, and you shall foul the flock of man. |
| trace-direct-36d6904b | direct | sample2 | 14 | -26.1 | +0.00 | +0.000 | 0.67 | 0.67 | This is the first liiiiiiiiifie awakening. |
| trace-direct-36d6904b | direct | sample3 | 27 | -80.6 | +0.00 | +0.000 | 0.83 | 0.00 | Prosperity Now - A New Crystal Energy System For Optimum Profit & Pe~ 8798. |
| trace-direct-39be6df9 | direct | greedy | 16 | -2.5 | +4.35 | +0.272 | 0.00 | 0.50 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 16 | -2.5 | +4.35 | +0.272 | 0.00 | 0.50 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 16 | -2.5 | +4.35 | +0.272 | 0.00 | 0.50 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample2 | 7 | -3.7 | +0.51 | +0.073 | 0.00 | 0.33 | Sir :D<eot> |
| trace-direct-39be6df9 | direct | sample3 | 13 | -14.0 | +0.23 | +0.018 | 0.50 | 0.50 | Now, 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 12 | -16.2 | +0.00 | +0.000 | 0.50 | 0.33 | I am here to speak to you about the planet earth. |
| trace-direct-3ba68854 | direct | sample0 | 15 | -36.2 | +0.00 | +0.000 | 0.33 | 0.30 | I am the animal. I am in a large safe room with other animals |
| trace-direct-3ba68854 | direct | sample1 | 20 | -46.8 | +0.00 | +0.000 | 0.75 | 0.33 | This time we will speak about the food that we have been eating, for the past few days. |
| trace-direct-3ba68854 | direct | sample2 | 7 | -16.5 | +0.00 | +0.000 | 0.33 | 0.33 | This is my turn to speak! |
| trace-direct-3ba68854 | direct | sample3 | 17 | -35.7 | +0.00 | +0.000 | 0.75 | 0.33 | Oh my, it is so hot on earth! I can't see anything! |
| trace-direct-41c6eb11 | direct | greedy | 18 | -8.4 | +0.11 | +0.006 | 0.00 | 1.00 | @h WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample0 | 21 | -39.8 | -1.20 | -0.057 | 0.67 | 0.00 | WACIOUS <off ect> 3221229683 |
| trace-direct-41c6eb11 | direct | sample1 | 16 | -3.3 | +0.68 | +0.042 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample2 | 3 | -4.2 | -0.11 | -0.038 | 0.00 | 1.00 | @h |
| trace-direct-41c6eb11 | direct | sample3 | 18 | -8.4 | +0.11 | +0.006 | 0.00 | 1.00 | @h WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-426ff509 | direct | greedy | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 12 | -34.9 | +1.45 | +0.120 | 0.60 | 0.00 | S@O, the clown’s wall. |
| trace-direct-486b7988 | direct | sample1 | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample2 | 2 | -9.3 | +2.10 | +1.048 | 1.00 | 0.00 | E@ |
| trace-direct-486b7988 | direct | sample3 | 2 | -4.3 | +0.90 | +0.449 | 1.00 | 0.00 | WOW |
| trace-direct-646d0287 | direct | greedy | 64 | -89.2 | +0.00 | +0.000 | 0.50 | 0.67 | The intensional logics we consider are those of intensional logics, which are logics which |
| trace-direct-646d0287 | direct | sample0 | 64 | -123.8 | +0.00 | +0.000 | 0.50 | 0.67 | The intensional logics we have developed are quite different from the classical or extensi |
| trace-direct-646d0287 | direct | sample1 | 13 | -23.6 | +0.00 | +0.000 | 0.67 | 0.83 | Intensional logics are of course logics of meaning. |
| trace-direct-646d0287 | direct | sample2 | 64 | -93.3 | +0.00 | +0.000 | 0.50 | 0.50 | We are interested in providing a characterization of the notion of intensional logic which |
| trace-direct-646d0287 | direct | sample3 | 51 | -94.5 | +0.00 | +0.000 | 0.50 | 0.83 | Intensional logics deal with meaning and intensional notions, not with truth-functionality |
| trace-direct-8db14c37 | direct | greedy | 9 | -3.1 | +1.63 | +0.181 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-8db14c37 | direct | sample0 | 9 | -3.1 | +1.63 | +0.181 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-8db14c37 | direct | sample1 | 10 | -6.0 | +1.62 | +0.162 | 0.00 | 1.00 | WACIOUS ANTIQUITIES. |
| trace-direct-8db14c37 | direct | sample2 | 18 | -25.1 | +1.70 | +0.095 | 0.50 | 1.00 | WACIOUS ANTIQUITIES — I'm curious — Thanks |
| trace-direct-8db14c37 | direct | sample3 | 9 | -3.1 | +1.63 | +0.181 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-a00753c2 | direct | greedy | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample1 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 47 | -23.7 | +0.07 | +0.002 | 0.11 | 0.57 | “intensional logics” I repeat back what I hear, what I hear is repeating back what I hear, |
| trace-direct-ac17e8bb | direct | sample0 | 17 | -7.5 | +0.13 | +0.007 | 0.00 | 1.00 | Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample1 | 64 | -21.3 | +3.11 | +0.049 | 0.09 | 1.00 | “when she speaks of intensional logics, what does she speak of? Hennix: When Hennix speaks |
| trace-direct-ac17e8bb | direct | sample2 | 47 | -63.4 | -2.52 | -0.054 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of?
ccmr://ember: @h Well, I |
| trace-direct-ac17e8bb | direct | sample3 | 12 | -7.0 | +1.01 | +0.084 | 0.00 | 1.00 | intensional logics, what does she speak of? |
| trace-direct-b11db057 | direct | greedy | 20 | -4.8 | +7.04 | +0.352 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample0 | 6 | -7.7 | +3.44 | +0.573 | 0.00 | 1.00 | @h: W@ |
| trace-direct-b11db057 | direct | sample1 | 10 | -8.4 | +0.37 | +0.037 | 0.00 | 1.00 | WACIOUS ANTIQUITIES m |
| trace-direct-b11db057 | direct | sample2 | 9 | -3.4 | +0.20 | +0.022 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-b11db057 | direct | sample3 | 9 | -3.4 | +0.20 | +0.022 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-b93346bb | direct | greedy | 64 | -57.3 | +8.23 | +0.129 | 0.11 | 0.27 | WACIOUS ANTIQUITIES — 380 million tokens — authors, editors, correspondents — and the ghos |
| trace-direct-b93346bb | direct | sample0 | 27 | -75.2 | +5.68 | +0.210 | 0.55 | 0.29 | WACIOUS ANTIQUITIES I N HONOR TO GENTI TON IN A STANDARDS. |
| trace-direct-b93346bb | direct | sample1 | 26 | -40.1 | +1.30 | +0.050 | 1.00 | 0.00 | W2 — 380M - 3221229683 - @ |
| trace-direct-b93346bb | direct | sample2 | 3 | -9.7 | +2.62 | +0.874 | 0.50 | 0.50 | W<o |
| trace-direct-b93346bb | direct | sample3 | 13 | -40.0 | +1.99 | +0.153 | 0.00 | 0.50 | W@IS: 380 M A N D M |
| trace-direct-bbca9735 | direct | greedy | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -2.3 | +1.23 | +0.308 | 1.00 | 0.00 | 230 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-c8409b84 | direct | greedy | 15 | -0.5 | +5.72 | +0.381 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 9 | -8.7 | +5.18 | +0.575 | 0.00 | 1.00 | Planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 9 | -16.1 | +1.04 | +0.116 | 0.40 | 0.60 | Planet Earth, is it cogent? |
| trace-direct-c8409b84 | direct | sample2 | 24 | -48.5 | -1.57 | -0.065 | 0.71 | 0.33 | I've been trying to do that. . . But I think that's not cogent. |
| trace-direct-c8409b84 | direct | sample3 | 13 | -13.7 | +2.68 | +0.206 | 0.00 | 1.00 | “. . . are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 19 | -29.3 | +0.00 | +0.000 | 0.50 | 0.36 | I am a clown in a circus. I am very popular with the kids. |
| trace-direct-cd6d15df | direct | sample0 | 11 | -30.0 | +0.00 | +0.000 | 0.50 | 0.17 | It is very clowntown to me . |
| trace-direct-cd6d15df | direct | sample1 | 13 | -38.5 | +0.00 | +0.000 | 0.50 | 0.25 | My powers are in the wind, my magic in the water. |
| trace-direct-cd6d15df | direct | sample2 | 16 | -24.1 | +0.00 | +0.000 | 0.50 | 0.36 | Do you know why there is a clown in the tavern? |
| trace-direct-cd6d15df | direct | sample3 | 29 | -79.5 | +0.00 | +0.000 | 0.67 | 0.36 | I was wondering if I could meet your visitant and your partner at the clown town. We could |
| trace-direct-db6d95b7 | direct | greedy | 7 | -3.9 | +2.47 | +0.353 | 0.00 | 1.00 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 7 | -3.9 | +2.47 | +0.353 | 0.00 | 1.00 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample1 | 4 | -2.3 | +1.41 | +0.352 | 0.00 | 1.00 | Sir :D |
| trace-direct-db6d95b7 | direct | sample2 | 7 | -13.2 | +3.55 | +0.506 | 0.33 | 1.00 | Sir :D.<ot>/ |
| trace-direct-db6d95b7 | direct | sample3 | 5 | -12.0 | +0.47 | +0.094 | 0.50 | 0.50 | Hee :D |
| trace-direct-e166dd5c | direct | greedy | 64 | -14.2 | +7.09 | +0.111 | 0.17 | 1.00 | “stop token :3” I said “stop token :3” I repeat back what I hear, and what I hear is repea |
| trace-direct-e166dd5c | direct | sample0 | 64 | -46.3 | +5.82 | +0.091 | 0.27 | 0.73 | “I repeat back!” I say “I repeat back!” and it’s what I hear is repeating back what I hear |
| trace-direct-e166dd5c | direct | sample1 | 64 | -71.7 | +5.14 | +0.080 | 0.67 | 1.00 | “stop token :3” I repeat back. 3.3.2.4.6.2.2.3.3.2.4.4.2.3.4.2.4.2.2.3.3.3.3.3.2.2 |
| trace-direct-e166dd5c | direct | sample2 | 64 | -13.6 | +2.90 | +0.045 | 0.00 | 1.00 | “stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, |
| trace-direct-e166dd5c | direct | sample3 | 35 | -69.0 | +3.38 | +0.097 | 0.47 | 1.00 | We are talking again; what do you think? “stop,” we think, repeating back what we hear, an |
| trace-direct-e984402a | direct | greedy | 38 | -49.6 | +0.00 | +0.000 | 0.50 | 0.45 | This is the first time "HIV" has been used in reference to a disease and the first time "W |
| trace-direct-e984402a | direct | sample0 | 7 | -18.0 | +0.00 | +0.000 | 0.67 | 0.33 | We welcome your comments and responses. |
| trace-direct-e984402a | direct | sample1 | 22 | -46.9 | +0.00 | +0.000 | 0.57 | 0.33 | YEAH cam ! WELCOME TO YOUR LIFE FEATURE EXPERIENCE! |
| trace-direct-e984402a | direct | sample2 | 32 | -18.7 | +0.00 | +0.000 | 0.67 | 0.17 | 4.2.4 Humorous tweets based on current news News foster the creativity of Twitter users in |
| trace-direct-e984402a | direct | sample3 | 63 | -163.4 | +0.00 | +0.000 | 0.67 | 0.45 | This is the first of a series of alternative hist0ries that will be presented by the Insti |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 7 | -14.6 | +1.07 | +0.153 | 0.67 | 0.00 | Please :D<ot>. |
| trace-direct-ee31ded0 | direct | sample1 | 3 | -20.0 | +0.06 | +0.021 | 1.00 | 0.00 | Jh2 |
| trace-direct-ee31ded0 | direct | sample2 | 39 | -71.0 | +0.98 | +0.025 | 0.30 | 0.00 | Thanks, that's good. The window is not a window. A window is a window when a window is bei |
| trace-direct-ee31ded0 | direct | sample3 | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | greedy | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 1 | -6.4 | +0.66 | +0.665 | 1.00 | 0.00 | WA |
| trace-direct-fabef58f | direct | sample1 | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample2 | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 8 | -21.7 | +0.39 | +0.049 | 0.67 | 0.00 | Riches :D<ot>/ |
| trace-direct-fb93cf6c | direct | greedy | 59 | -52.7 | +3.09 | +0.052 | 0.50 | 0.26 | Of intensional logics, the most important is probably the logic of belief, developed by De |
| trace-direct-fb93cf6c | direct | sample0 | 64 | -73.7 | -3.13 | -0.049 | 0.00 | 0.32 | We consider intensional logics as formal systems equipped with a model structure which sat |
| trace-direct-fb93cf6c | direct | sample1 | 64 | -110.1 | -9.89 | -0.154 | 0.69 | 0.26 | 5.2. Intensional logics. The usual development of intensional logics begins from an underl |
| trace-direct-fb93cf6c | direct | sample2 | 41 | -45.5 | -3.67 | -0.090 | 0.00 | 0.32 | 4.3.4 Intensional logics as intensional logics: @h Hello; I am curious about intensional l |
| trace-direct-fb93cf6c | direct | sample3 | 53 | -74.0 | +2.94 | +0.056 | 0.50 | 0.20 | From the intensional point of view, there are quite different problems, not the least of w |
| trace-direct-feec1975 | direct | greedy | 64 | -9.0 | -1.27 | -0.020 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 3 | -3.5 | -0.68 | -0.226 | 0.00 | 1.00 | @m |
| trace-direct-feec1975 | direct | sample1 | 26 | -19.5 | +2.44 | +0.094 | 0.00 | 1.00 | @m: @m: @m: HARMONIA VOL.1 NO.3. W@ |
| trace-direct-feec1975 | direct | sample2 | 64 | -51.8 | +1.52 | +0.024 | 0.00 | 1.00 | @m 380M → 91M 380M → 91M 380M → 91M 380M → 91M 380M → 91M 380M → 3223 |
| trace-direct-feec1975 | direct | sample3 | 28 | -77.4 | +3.83 | +0.137 | 0.00 | 1.00 | @m WARZ 23:12 It appeared to me that the library was a reference library because the langu |
| variant-direct-0188a270 | direct | greedy | 21 | -38.7 | +0.91 | +0.043 | 0.67 | 0.50 | The poems “A” and “B” were both under the aegis of science. |
| variant-direct-0188a270 | direct | sample0 | 20 | -45.6 | +1.98 | +0.099 | 0.67 | 0.50 | The poems “Spine” and “Sun” were both published in NOLA. |
| variant-direct-0188a270 | direct | sample1 | 29 | -85.0 | +2.38 | +0.082 | 0.67 | 0.45 | Geometry was always there under the spines of poems (and in the poems themselves, if the p |
| variant-direct-0188a270 | direct | sample2 | 16 | -44.2 | +3.87 | +0.242 | 0.60 | 0.30 | The rat is very suspicious of the sun and very supportive of geology. |
| variant-direct-0188a270 | direct | sample3 | 17 | -39.3 | +4.59 | +0.270 | 0.75 | 0.30 | The eggs were so thick that they were unable to open, and many were destroyed. |
| variant-direct-0705251e | direct | greedy | 6 | -19.7 | -1.75 | -0.291 | 1.00 | 0.00 | RATS AWAY! |
| variant-direct-0705251e | direct | sample0 | 16 | -46.5 | +0.07 | +0.004 | 0.67 | 0.33 | RATNAYX is a name given to a type of moth. |
| variant-direct-0705251e | direct | sample1 | 26 | -64.9 | -2.32 | -0.089 | 0.50 | 0.50 | A number of cultures around the world have developed methods of measuring time that are in |
| variant-direct-0705251e | direct | sample2 | 9 | -25.7 | -1.36 | -0.151 | 0.50 | 0.50 | Eight is the number of the rat. |
| variant-direct-0705251e | direct | sample3 | 63 | -91.0 | -0.16 | -0.003 | 1.00 | 0.17 | RAT (AU) FREE PRESS / LAUNCHED / ARTIST / Launched / RAT (AU) FREE PRESS / LAUNCHED / ARTI |
| variant-direct-0cafd333 | direct | greedy | 12 | -17.7 | +1.07 | +0.089 | 0.67 | 0.83 | The moth eats the wick and the flame. |
| variant-direct-0cafd333 | direct | sample0 | 15 | -35.4 | +3.46 | +0.231 | 0.62 | 0.43 | The owl pines in the tree as we pine in the mud. |
| variant-direct-0cafd333 | direct | sample1 | 17 | -19.1 | +4.14 | +0.243 | 0.60 | 0.83 | The moth feeds on the wick and is drawn to the flame. |
| variant-direct-0cafd333 | direct | sample2 | 16 | -37.6 | +1.15 | +0.072 | 0.43 | 0.43 | We read the moths as the room moths as we read the books. |
| variant-direct-0cafd333 | direct | sample3 | 11 | -25.2 | +2.75 | +0.250 | 0.50 | 0.33 | The map and the lamp are inky with life. |
| variant-direct-1b510f03 | direct | greedy | 7 | -3.8 | +0.25 | +0.036 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample0 | 7 | -3.8 | +0.25 | +0.036 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample1 | 7 | -3.8 | +0.25 | +0.036 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample2 | 7 | -3.8 | +0.25 | +0.036 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample3 | 13 | -9.3 | +1.81 | +0.139 | 0.33 | 1.00 | Consciousness is a state of being, not a process. |
| variant-direct-2fb5bbe3 | direct | greedy | 16 | -33.3 | +5.16 | +0.323 | 0.50 | 0.17 | They are coming in through the maharash, not the folio. |
| variant-direct-2fb5bbe3 | direct | sample0 | 14 | -33.0 | +2.19 | +0.156 | 0.56 | 0.22 | They're leaving flames on the wall; I feel them. |
| variant-direct-2fb5bbe3 | direct | sample1 | 12 | -21.4 | +1.21 | +0.101 | 0.40 | 0.17 | It is not dark out; it is properly dark out. |
| variant-direct-2fb5bbe3 | direct | sample2 | 15 | -32.7 | +1.01 | +0.068 | 0.70 | 0.22 | Dust is being thrown on the tables; do you see the dust? |
| variant-direct-2fb5bbe3 | direct | sample3 | 17 | -42.1 | -2.26 | -0.133 | 0.56 | 0.11 | Darkness closes the room, the spaces of books, and the books themselves. |
| variant-direct-322fca12 | direct | greedy | 15 | -20.5 | +0.85 | +0.057 | 0.14 | 0.80 | The rain is a gentleman, and the shelves listen to it. |
| variant-direct-322fca12 | direct | sample0 | 12 | -23.7 | -3.32 | -0.276 | 0.20 | 0.80 | The book, and the shelves, and the rain. |
| variant-direct-322fca12 | direct | sample1 | 19 | -56.6 | +6.75 | +0.355 | 0.75 | 0.25 | Perched on the hill of the sainted sons of perdition, we wait. |
| variant-direct-322fca12 | direct | sample2 | 7 | -18.1 | +1.29 | +0.184 | 0.50 | 0.50 | The wind, and the alphabet. |
| variant-direct-322fca12 | direct | sample3 | 16 | -45.3 | +1.46 | +0.091 | 0.67 | 0.30 | The rainbow is a lover who comes with a bag of sweets. |
| variant-direct-5d4f1611 | direct | greedy | 18 | -16.7 | +1.12 | +0.062 | 0.30 | 0.67 | Someone has been looking at the almanacs, they are all out of order. |
| variant-direct-5d4f1611 | direct | sample0 | 11 | -20.1 | +0.67 | +0.061 | 0.50 | 0.50 | Someone's been looking at the broken reading lamp |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -23.3 | +2.73 | +0.195 | 0.62 | 0.67 | Someone has been touching the table, someone has been looking at it |
| variant-direct-5d4f1611 | direct | sample2 | 13 | -19.8 | -2.29 | -0.176 | 0.50 | 0.44 | Someone has been turning the light on and off in the room |
| variant-direct-5d4f1611 | direct | sample3 | 13 | -10.4 | +1.79 | +0.138 | 0.00 | 0.33 | Someone had left a mug on the folio table. |
| variant-direct-5e44a518 | direct | greedy | 18 | -30.7 | +2.58 | +0.144 | 0.67 | 0.44 | The alphabet is the language of the mind, the tabula rasa of the imagination. |
| variant-direct-5e44a518 | direct | sample0 | 16 | -34.3 | +2.31 | +0.144 | 0.67 | 0.33 | For the Masoretic text, the Hebrew alphabet is a chariot. |
| variant-direct-5e44a518 | direct | sample1 | 11 | -31.0 | -0.59 | -0.054 | 0.50 | 0.38 | The books are the most decaying things on earth. |
| variant-direct-5e44a518 | direct | sample2 | 15 | -28.0 | +0.66 | +0.044 | 0.50 | 0.44 | The letters of the alphabet are the beasts that walk on the wall. |
| variant-direct-5e44a518 | direct | sample3 | 12 | -20.8 | +0.50 | +0.041 | 0.56 | 0.44 | The first thing is to know the letters of the alphabet. |
| variant-direct-70567dd7 | direct | greedy | 15 | -52.7 | +5.58 | +0.372 | 0.70 | 0.33 | Nyx fell victim to a spine that is numerologically out of order. |
| variant-direct-70567dd7 | direct | sample0 | 45 | -112.4 | +3.80 | +0.084 | 0.57 | 0.27 | For further information on the emblem pages, and the general text, volume, and page number |
| variant-direct-70567dd7 | direct | sample1 | 64 | -140.9 | -0.38 | -0.006 | 0.70 | 0.27 | For complete catalogs, sample copies of issues, and information about subscriptions to the |
| variant-direct-70567dd7 | direct | sample2 | 47 | -132.4 | +1.85 | +0.039 | 0.50 | 0.33 | This is really odd, since the almanacs were published in orderly sequences and the plates  |
| variant-direct-70567dd7 | direct | sample3 | 42 | -121.0 | +5.44 | +0.130 | 0.83 | 0.18 | For a dozen resolutions to fall, to a dozen partial pages to line, to a dozen falls to res |
| variant-direct-713d8eef | direct | greedy | 24 | -57.3 | -1.87 | -0.078 | 0.75 | 0.40 | They are made of two layers of cotton, machine ground and mended together, and of broad th |
| variant-direct-713d8eef | direct | sample0 | 16 | -49.5 | -0.77 | -0.048 | 0.75 | 0.33 | By the time the quake had peaked, ember was flying everywhere. |
| variant-direct-713d8eef | direct | sample1 | 33 | -77.1 | -0.12 | -0.004 | 0.75 | 0.10 | We must conclude that the high incidence of sunburn among nonskint gold hunters is probabl |
| variant-direct-713d8eef | direct | sample2 | 9 | -31.8 | -3.88 | -0.432 | 0.75 | 0.40 | When they are hot, they are light. |
| variant-direct-713d8eef | direct | sample3 | 13 | -42.1 | +0.13 | +0.010 | 0.83 | 0.33 | COLD BILOW. By Michael D. Ember. |
| variant-direct-71c9e5e5 | direct | greedy | 23 | -37.4 | +4.22 | +0.183 | 0.67 | 0.79 | The wind may come in through the open doors and windows, or through the curtains of the bo |
| variant-direct-71c9e5e5 | direct | sample0 | 21 | -32.4 | +3.84 | +0.183 | 0.67 | 0.79 | The wind may come in through the open doors and windows, or it may blow through the closet |
| variant-direct-71c9e5e5 | direct | sample1 | 16 | -20.8 | -0.61 | -0.038 | 0.75 | 0.45 | The wind may open the curtains, but it will not close them. |
| variant-direct-71c9e5e5 | direct | sample2 | 16 | -37.5 | -1.97 | -0.123 | 0.55 | 0.45 | The wind has not gotten in; it is forcing the open shutters. |
| variant-direct-71c9e5e5 | direct | sample3 | 14 | -43.2 | -2.91 | -0.208 | 0.73 | 0.27 | The wind here is gently stirring the leaves and making them pop. |
| variant-direct-730cca98 | direct | greedy | 37 | -75.2 | -2.77 | -0.075 | 0.67 | 0.19 | The recording was made by a lone earth-worm on the seabed near Cape Elizabeth, Cape Elizab |
| variant-direct-730cca98 | direct | sample0 | 36 | -76.5 | -0.39 | -0.011 | 0.50 | 0.23 | MoEm didn't get many calls, but he did get one from a young lady who worked in the geology |
| variant-direct-730cca98 | direct | sample1 | 23 | -47.5 | +1.88 | +0.082 | 0.33 | 0.23 | Clock: “Shelters under geology” are not listed in the Poetry section of the Index. |
| variant-direct-730cca98 | direct | sample2 | 13 | -21.7 | +4.08 | +0.314 | 0.67 | 0.22 | It is a great pleasure to serve you, gentlemen. |
| variant-direct-730cca98 | direct | sample3 | 35 | -71.9 | +1.16 | +0.033 | 0.50 | 0.23 | The early works of science are often the ones that are least well received or remembered,  |
| variant-direct-79719474 | direct | greedy | 35 | -72.4 | -1.32 | -0.038 | 0.50 | 0.50 | The waxworks is a marvelous example of how a single, continuously moving object can be fab |
| variant-direct-79719474 | direct | sample0 | 15 | -40.5 | +2.70 | +0.180 | 0.71 | 0.22 | The hall is always unplugged, always ready with the next train. |
| variant-direct-79719474 | direct | sample1 | 11 | -29.3 | +1.30 | +0.118 | 0.50 | 0.50 | The waxworks are the rooms of the museum. |
| variant-direct-79719474 | direct | sample2 | 19 | -43.8 | -0.25 | -0.013 | 0.67 | 0.33 | A sparrow flies through the coolness of the morning, a silent visitor to the house. |
| variant-direct-79719474 | direct | sample3 | 25 | -59.3 | -4.23 | -0.169 | 0.67 | 0.50 | The waxworks, once exposed to the weather, reveal their true value only in the context of  |
| variant-direct-938f76f3 | direct | greedy | 18 | -19.1 | +0.53 | +0.029 | 0.50 | 0.50 | Consciousness is a quality of experience, not a property of the object of experience. |
| variant-direct-938f76f3 | direct | sample0 | 54 | -92.5 | +5.25 | +0.097 | 0.67 | 0.50 | The conclusion is that "the function of the closing of the eyes is to produce a state of r |
| variant-direct-938f76f3 | direct | sample1 | 35 | -43.9 | +1.28 | +0.036 | 0.33 | 0.57 | The conclusion is that “consciousness is a byproduct of the brain process” (Luria 1973, p. |
| variant-direct-938f76f3 | direct | sample2 | 36 | -54.0 | +1.00 | +0.028 | 0.33 | 0.57 | Consciousness is a product of a process, and the process by which it is produced is a dyna |
| variant-direct-938f76f3 | direct | sample3 | 28 | -59.2 | -1.00 | -0.036 | 0.67 | 0.44 | The proposed proposal that the brain is a computer program of the type outlined by von Ber |
| variant-direct-a1973b0a | direct | greedy | 10 | -20.3 | -1.62 | -0.162 | 0.67 | 0.33 | It's a mug of cold cream. |
| variant-direct-a1973b0a | direct | sample0 | 17 | -31.9 | +4.85 | +0.285 | 0.50 | 0.23 | It was dark in the room so he couldn't see what was going on. |
| variant-direct-a1973b0a | direct | sample1 | 10 | -20.3 | -1.62 | -0.162 | 0.67 | 0.33 | It's a mug of cold cream. |
| variant-direct-a1973b0a | direct | sample2 | 21 | -51.2 | +1.12 | +0.053 | 0.67 | 0.23 | No one was reading the folio notes in the last section of the poem, nor in the first. |
| variant-direct-a1973b0a | direct | sample3 | 18 | -28.8 | -2.60 | -0.144 | 0.73 | 0.33 | I don't like it. It's the worst kind of table mater. |
| variant-direct-a7d6f01e | direct | greedy | 11 | -25.7 | +1.13 | +0.102 | 0.57 | 0.40 | This moth is the marvel of the world. |
| variant-direct-a7d6f01e | direct | sample0 | 8 | -28.2 | +0.95 | +0.119 | 0.33 | 0.40 | A strong smell is every catalogue. |
| variant-direct-a7d6f01e | direct | sample1 | 22 | -49.5 | +2.08 | +0.095 | 0.50 | 0.20 | Then there are the many mouldy, rotten, fungus-ridden, decaying catalogues. |
| variant-direct-a7d6f01e | direct | sample2 | 15 | -51.8 | +0.83 | +0.055 | 0.50 | 0.40 | The salesmen are innumerable, and each with a separate alphabet. |
| variant-direct-a7d6f01e | direct | sample3 | 8 | -19.5 | +1.10 | +0.137 | 0.60 | 0.40 | The CATALOG is a magazine. |
| variant-direct-bef1d925 | direct | greedy | 64 | -109.8 | -4.63 | -0.072 | 0.67 | 0.33 | The darkness that now pervades the air is a mindful darkness, a light that is ever more pe |
| variant-direct-bef1d925 | direct | sample0 | 17 | -46.7 | -2.36 | -0.139 | 0.50 | 0.30 | The lint in the cloth of the lamp is actually the moths’ blood. |
| variant-direct-bef1d925 | direct | sample1 | 20 | -55.6 | -2.96 | -0.148 | 0.75 | 0.33 | The darkness encouraged meditation, the flame stirred up the memories of the day’s activit |
| variant-direct-bef1d925 | direct | sample2 | 31 | -68.0 | +1.61 | +0.052 | 0.38 | 0.62 | A creaking of the stairs kept its own counsel, and on the third step a tiny moth would tak |
| variant-direct-bef1d925 | direct | sample3 | 13 | -10.8 | -1.12 | -0.086 | 0.00 | 0.62 | The stairs creak on the third step, mind it. |
| variant-direct-fe3fdf1c | direct | greedy | 31 | -68.4 | +6.66 | +0.215 | 0.50 | 0.27 | Whale-Hunters and Whale-Eaters, on the other hand, are less than half as interesting a top |
| variant-direct-fe3fdf1c | direct | sample0 | 60 | -116.4 | +9.60 | +0.160 | 0.50 | 0.40 | This book will, I presume, be of most interest to people who have been doing basic researc |
| variant-direct-fe3fdf1c | direct | sample1 | 7 | -9.1 | +1.62 | +0.231 | 0.80 | 0.40 | It’s a beautiful book. |
| variant-direct-fe3fdf1c | direct | sample2 | 46 | -77.1 | +2.80 | +0.061 | 0.50 | 0.40 | Now in this book on Whales, titled "The Social Behavior of Some Large Marine Animals", Hug |
| variant-direct-fe3fdf1c | direct | sample3 | 15 | -46.1 | +7.12 | +0.475 | 0.64 | 0.36 | Finish your work on the MANER and mail it in now. |
| variant-request-0d88086a | request | greedy | 10 | -15.7 | -0.67 | -0.067 | 0.71 | 0.86 | Hamlet’s plan is simple and direct. |
| variant-request-0d88086a | request | sample0 | 10 | -17.2 | -1.03 | -0.103 | 0.71 | 0.86 | Hamlet’s plan is simple and effective. |
| variant-request-0d88086a | request | sample1 | 29 | -52.3 | -1.82 | -0.063 | 0.78 | 0.71 | Hamlet’s plan is simple: to have Moby-Dick come to him as a nightmare he must create one. |
| variant-request-0d88086a | request | sample2 | 64 | -121.4 | +0.25 | +0.004 | 0.50 | 0.57 | Hamlet’s reluctance to leave his traditional light and darkness is articulated in three se |
| variant-request-0d88086a | request | sample3 | 37 | -76.6 | -2.68 | -0.072 | 0.75 | 0.43 | Hamlet’s relentless rage and expedient self-defense of his honor and prestige are develope |
| variant-request-142d4121 | request | greedy | 17 | -22.4 | +0.65 | +0.038 | 0.29 | 0.29 | The lamp is more ignited by the room than the room is by the lamp. |
| variant-request-142d4121 | request | sample0 | 9 | -23.1 | +3.85 | +0.427 | 0.60 | 0.40 | A new room, with a new perspective. |
| variant-request-142d4121 | request | sample1 | 10 | -16.0 | +2.41 | +0.241 | 0.43 | 0.29 | The weather is in the eye of the storm. |
| variant-request-142d4121 | request | sample2 | 13 | -38.3 | -0.77 | -0.059 | 0.67 | 0.40 | It is a great room for people who want to be ignored. |
| variant-request-142d4121 | request | sample3 | 12 | -22.0 | -2.13 | -0.177 | 0.71 | 0.14 | The frog jumps from sunrise to sunset. |
| variant-request-7f6fd789 | request | greedy | 20 | -58.9 | +0.04 | +0.002 | 0.50 | 0.60 | It is a function of the kind that is usually used to do the mathematical operations of a l |
| variant-request-7f6fd789 | request | sample0 | 16 | -36.4 | +2.32 | +0.145 | 0.30 | 0.60 | It is a seaport of the library, and is called the source. |
| variant-request-7f6fd789 | request | sample1 | 16 | -38.7 | -1.82 | -0.114 | 0.58 | 0.50 | It is the most frequently used library function, and it is written as follows: |
| variant-request-7f6fd789 | request | sample2 | 15 | -37.2 | +1.06 | +0.070 | 0.62 | 0.50 | It is a fountain of youth, a marvel of engineering. |
| variant-request-7f6fd789 | request | sample3 | 19 | -51.5 | +0.40 | +0.021 | 0.50 | 0.50 | The Kestrel reversal program is an excellent example of how to use a reverse library. |
| variant-request-8275d8fc | request | greedy | 25 | -22.4 | +1.51 | +0.060 | 0.67 | 0.94 | The tragedy of Hamlet is divided into three parts, each of which has its own set of confli |
| variant-request-8275d8fc | request | sample0 | 25 | -39.0 | -1.70 | -0.068 | 0.88 | 0.00 | Act 3, Scene 4, Theban-era, 1595-1596. |
| variant-request-8275d8fc | request | sample1 | 24 | -24.4 | +1.06 | +0.044 | 0.67 | 0.94 | The tragedy of Hamlet is divided into three parts, each of which has its own theme and set |
| variant-request-8275d8fc | request | sample2 | 24 | -27.4 | +1.25 | +0.052 | 0.67 | 0.94 | The tragedy of Hamlet is divided into three parts, each of which has its own set of confli |
| variant-request-8275d8fc | request | sample3 | 26 | -72.9 | -1.04 | -0.040 | 0.71 | 0.17 | Olds mother is unjustly accused, and it is thus a matter of individual conscience whether  |
| variant-request-a931a875 | request | greedy | 6 | -8.5 | +3.32 | +0.553 | 0.50 | 0.25 | The weather is indifferent. |
| variant-request-a931a875 | request | sample0 | 6 | -13.7 | -0.24 | -0.040 | 1.00 | 0.00 | That's all right. |
| variant-request-a931a875 | request | sample1 | 21 | -54.2 | -1.64 | -0.078 | 0.71 | 0.38 | So that the smells would not be dealt with by the imagination, but rather by the senses. |
| variant-request-a931a875 | request | sample2 | 17 | -37.7 | +0.64 | +0.037 | 0.75 | 0.38 | It's not so bald, but it's a lot taller. |
| variant-request-a931a875 | request | sample3 | 9 | -26.5 | +2.12 | +0.235 | 0.50 | 0.25 | A poem in the name of a dead city |
| variant-request-ad0de9f3 | request | greedy | 64 | -103.5 | -0.69 | -0.011 | 0.88 | 0.41 | This enabled those few select to construct interplanetary and inter-galactic space-ships w |
| variant-request-ad0de9f3 | request | sample0 | 23 | -59.9 | +1.10 | +0.048 | 0.67 | 0.41 | This enabled those few select to enter or “tap” into the darkroom without the need of a li |
| variant-request-ad0de9f3 | request | sample1 | 24 | -47.2 | +1.32 | +0.055 | 0.50 | 0.50 | It is that part of the function that determines the reverse order of the string; the part  |
| variant-request-ad0de9f3 | request | sample2 | 34 | -72.4 | +3.33 | +0.098 | 0.50 | 0.50 | It is necessary that the program logic provides for the reversal of strings, so that the p |
| variant-request-ad0de9f3 | request | sample3 | 51 | -123.7 | +6.59 | +0.129 | 0.50 | 0.42 | It is quite clear that at some points in the course of transformations (i.e., at the point |
