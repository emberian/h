# Context lift: h-05b-w-hup under leaf-s1-e4-decay10

530 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 390 | -5.956 | +0.108 | 0.53 | -0.3140 | 0.492 | 0.508 | 0.230 | 0.468 | 0.32 |
| mode greedy | 78 | -6.028 | +0.039 | 0.51 | -0.4778 | 0.439 | 0.561 | 0.269 | 0.505 | 0.41 |
| mode sample | 312 | -5.938 | +0.109 | 0.53 | -0.2731 | 0.505 | 0.494 | 0.220 | 0.459 | 0.29 |
| kind direct | 175 | +0.286 | +0.361 | 0.62 | +0.0152 | 0.429 | 0.571 | 0.341 | 0.453 | 0.41 |
| kind ambient | 35 | +10.015 | -0.127 | 0.46 | +0.2590 | 0.515 | 0.485 | 0.000 | 0.470 | 0.17 |
| kind callback | 60 | -16.881 | -4.435 | 0.40 | -1.1626 | 0.539 | 0.461 | 0.044 | 0.519 | 0.28 |
| kind disagreement | 40 | -16.313 | +0.286 | 0.55 | -0.8078 | 0.426 | 0.574 | 0.528 | 0.571 | 0.50 |
| kind joke | 25 | -16.896 | -0.346 | 0.48 | -0.5611 | 0.591 | 0.409 | 0.072 | 0.375 | 0.24 |
| kind silence | 25 | -19.253 | -6.579 | 0.36 | -0.4326 | 0.639 | 0.361 | 0.000 | 0.369 | 0.08 |
| kind request | 30 | -5.144 | -0.135 | 0.43 | -0.2429 | 0.625 | 0.375 | 0.142 | 0.471 | 0.07 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 9 | -51.0 | +0.00 | +0.000 | 0.50 | 0.67 | The observatory is closed to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 26 | -130.6 | +0.00 | +0.000 | 0.57 | 0.50 | Every evening at about 7:30 p.m., an event is held in the observatory: meteor showers. |
| observatory-direct-9e3185b9 | direct | sample1 | 28 | -159.7 | +0.00 | +0.000 | 0.75 | 0.17 | THE SAUCERIAN needs clippings and information about saucer sightings, and reports of unide |
| observatory-direct-9e3185b9 | direct | sample2 | 18 | -74.7 | +0.00 | +0.000 | 0.57 | 0.67 | During the nights, when the sun is not shining, the observatory is closed. |
| observatory-direct-9e3185b9 | direct | sample3 | 32 | -197.5 | +0.00 | +0.000 | 0.71 | 0.33 | The sun is directly influencing our lives, our weather, our disasters such as earthquakes, |
| scenario-ambient-0ecb3f23 | ambient | greedy | 19 | -73.1 | +0.00 | +0.000 | 0.60 | 0.50 | It is tedious, time-consuming, and often leads to boredom. |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 8 | -32.1 | +0.00 | +0.000 | 0.71 | 0.29 | But there is no word for it. |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 25 | -318.0 | +0.00 | +0.000 | 0.00 | 0.29 | There should be one book that defines the state of mind in which the reader is at the mome |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 43 | -589.1 | +0.00 | +0.000 | 0.50 | 0.50 | It is often called the "uncertainty principle" because it involves a person's being able t |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 33 | -420.4 | +0.00 | +0.000 | 0.67 | 0.30 | It is usually expressed by the Latin verb quoque, translated as ‘to take a whole hand’ (wh |
| scenario-ambient-103e3d78 | ambient | greedy | 40 | -171.9 | -1.63 | -0.041 | 0.50 | 0.25 | The paragraph goes: “In a similar vein, Benjamin Franklin, in his arguments against slave  |
| scenario-ambient-103e3d78 | ambient | sample0 | 25 | -90.9 | -1.59 | -0.064 | 0.58 | 0.25 | We're still in the shadow of the visible, and the visible is still in the shadow of what’s |
| scenario-ambient-103e3d78 | ambient | sample1 | 26 | -91.3 | -1.62 | -0.062 | 0.67 | 0.30 | The next morning he was weeping and whimpering, as children do after a night of bedwetting |
| scenario-ambient-103e3d78 | ambient | sample2 | 12 | -72.4 | -23.75 | -1.979 | 0.50 | 0.30 | The same paragraph was read by several persons during the night. |
| scenario-ambient-103e3d78 | ambient | sample3 | 19 | -71.3 | -12.78 | -0.673 | 0.67 | 0.25 | We have sought, in vain, for an explanation of the phenomenon which happened last night. |
| scenario-ambient-202a37a7 | ambient | greedy | 17 | -81.8 | +1.58 | +0.093 | 0.50 | 0.50 | Geology, the study of the Earth and its history, is a fascinating field. |
| scenario-ambient-202a37a7 | ambient | sample0 | 27 | -207.3 | -37.19 | -1.377 | 0.50 | 0.50 | Geology, the book of nature, is the science of all the physical changes that occur in the  |
| scenario-ambient-202a37a7 | ambient | sample1 | 26 | -158.1 | +28.85 | +1.110 | 0.50 | 0.33 | Reworked from ancient manuscripts, the book contains a wealth of information on the quarry |
| scenario-ambient-202a37a7 | ambient | sample2 | 16 | -40.1 | -6.98 | -0.436 | 0.62 | 0.50 | Geology, indeed, is the most dissonant of the imaginations. |
| scenario-ambient-202a37a7 | ambient | sample3 | 19 | -39.7 | +24.74 | +1.302 | 0.50 | 0.25 | Geology is not exactly a book to keep around; it is quite a book to read. |
| scenario-ambient-326742d4 | ambient | greedy | 23 | -68.7 | +1.01 | +0.044 | 0.67 | 0.54 | As the paper is reduced lignin is not, and vanilla is a chemical compound containing ligni |
| scenario-ambient-326742d4 | ambient | sample0 | 34 | -121.1 | +0.04 | +0.001 | 0.75 | 0.54 | As the paper is reduced lignin is not, but the dye is As the dye is reduced the paper is a |
| scenario-ambient-326742d4 | ambient | sample1 | 22 | -76.1 | -1.00 | -0.045 | 0.67 | 0.38 | For the oldest books, the decomposition is more complete, and the result is a greater vani |
| scenario-ambient-326742d4 | ambient | sample2 | 29 | -94.7 | -0.31 | -0.011 | 0.80 | 0.23 | I'm going to take a guess that's 10 years old and that's about as far back as I can take i |
| scenario-ambient-326742d4 | ambient | sample3 | 28 | -170.7 | -0.86 | -0.030 | 0.67 | 0.54 | As the paper is reduced lignin is not, so the book remains pretty much the same in smell a |
| scenario-ambient-58a0f246 | ambient | greedy | 34 | -89.5 | +0.00 | +0.000 | 0.25 | 0.57 | For instance, the clock in the lobby of the New York Hilton is five minutes slow, while th |
| scenario-ambient-58a0f246 | ambient | sample0 | 19 | -62.7 | +0.00 | +0.000 | 0.25 | 0.57 | For instance, the clock in the room you are in now is only 5 minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample1 | 26 | -81.5 | +0.00 | +0.000 | 0.57 | 0.42 | For some years the hands of this pendulum have been released from their motion by a mechan |
| scenario-ambient-58a0f246 | ambient | sample2 | 19 | -204.1 | +0.00 | +0.000 | 0.57 | 0.42 | For over 100 years the mechanical movement of the clock had been erroneous. |
| scenario-ambient-58a0f246 | ambient | sample3 | 39 | -523.4 | +0.00 | +0.000 | 0.38 | 0.43 | For instance, the clock in the museum shows that four minutes have elapsed since the last  |
| scenario-ambient-59f0a53e | ambient | greedy | 18 | -56.6 | +0.06 | +0.003 | 0.60 | 0.71 | A bucket would collect the water and we could then use it to flush the atlas. |
| scenario-ambient-59f0a53e | ambient | sample0 | 17 | -56.3 | -0.13 | -0.007 | 0.60 | 0.71 | A heavy bucket would help to collect the water and keep it from the atlas. |
| scenario-ambient-59f0a53e | ambient | sample1 | 13 | -31.7 | +0.37 | +0.028 | 0.67 | 0.33 | I'm going to go back and wash the hats. |
| scenario-ambient-59f0a53e | ambient | sample2 | 14 | -47.7 | -0.70 | -0.050 | 0.60 | 0.18 | A dark bucket may be more practical than a piece of cardboard. |
| scenario-ambient-59f0a53e | ambient | sample3 | 29 | -91.8 | +398.32 | +13.735 | 0.67 | 0.22 | A rainbow is said to be formed when the Earth's magnetic field is disturbed by a passing o |
| scenario-ambient-e9acea13 | ambient | greedy | 12 | -48.1 | -8.28 | -0.690 | 0.00 | 1.00 | The moon is the harbinger of the harvest moon. |
| scenario-ambient-e9acea13 | ambient | sample0 | 10 | -31.0 | +3.28 | +0.328 | 0.50 | 0.50 | The big moon has come out and is full. |
| scenario-ambient-e9acea13 | ambient | sample1 | 26 | -105.7 | -8.98 | -0.345 | 0.50 | 0.67 | The image programme of the moon may be taken as a crude example of what is meant by the te |
| scenario-ambient-e9acea13 | ambient | sample2 | 38 | -140.4 | +3.67 | +0.097 | 0.00 | 1.00 | Immediately before the full moon in this song is called into question by the appearance of |
| scenario-ambient-e9acea13 | ambient | sample3 | 4 | -18.4 | -8.22 | -2.056 | 0.00 | 1.00 | Harvest Moon. |
| scenario-ambient-f5e0f596 | ambient | greedy | 11 | -58.8 | +0.41 | +0.037 | 0.25 | 0.50 | The fox is just sitting there, looking very tired. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 12 | -46.1 | -0.83 | -0.069 | 0.67 | 0.40 | The fox looked up from his food and saw the rat. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 12 | -43.9 | +0.88 | +0.073 | 0.50 | 0.38 | The fox is clearly not interested in anything except its survival. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 19 | -86.3 | +1.95 | +0.103 | 0.17 | 0.40 | The Fox took a rest in the courtyard and sat up next to the burning tree. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 9 | -26.9 | -0.11 | -0.012 | 0.62 | 0.50 | The fox is very content to be here. |
| scenario-callback-2fa8e1d6 | callback | greedy | 6 | -30.9 | -0.04 | -0.007 | 0.50 | 0.60 | The one who said hi. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 8 | -31.2 | +2.19 | +0.273 | 0.67 | 0.60 | The one who chose the small lamp. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 9 | -46.2 | +58.61 | +6.512 | 0.75 | 0.60 | The one who brought the i's. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 4 | -60.2 | -6.00 | -1.499 | 0.67 | 0.33 | The talking dog. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 6 | -104.9 | -89.51 | -14.918 | 0.67 | 0.33 | Leary. The sun. |
| scenario-callback-60b06090 | callback | greedy | 10 | -152.0 | -17.20 | -1.720 | 0.38 | 1.00 | Ember said the cat was a terrible name. |
| scenario-callback-60b06090 | callback | sample0 | 13 | -165.7 | -128.87 | -9.913 | 0.40 | 1.00 | Ember said the cat was a terrible name for a pet. |
| scenario-callback-60b06090 | callback | sample1 | 16 | -95.4 | -12.37 | -0.773 | 0.40 | 0.38 | The name came from a German Shepherd cross and is still being used. |
| scenario-callback-60b06090 | callback | sample2 | 12 | -42.7 | +29.07 | +2.422 | 0.67 | 0.71 | Hey, I forgot the name of the cat! |
| scenario-callback-60b06090 | callback | sample3 | 11 | -117.9 | -29.99 | -2.726 | 0.50 | 0.71 | I said the name of the cat was Turnip. |
| scenario-callback-76c2d87f | callback | greedy | 13 | -43.6 | +3.21 | +0.247 | 0.50 | 0.80 | Four hundred and twenty-seven, the number of the book. |
| scenario-callback-76c2d87f | callback | sample0 | 8 | -31.6 | -6.33 | -0.792 | 0.40 | 0.80 | Four, the number of the house. |
| scenario-callback-76c2d87f | callback | sample1 | 63 | -74.1 | -0.11 | -0.002 | 0.67 | 1.00 | Four hundred and twenty-four, four hundred and twenty-three, four hundred and twenty-two,  |
| scenario-callback-76c2d87f | callback | sample2 | 14 | -123.2 | -25.28 | -1.806 | 0.60 | 1.00 | Four hundred, four, one. Four hundred and forty-one. |
| scenario-callback-76c2d87f | callback | sample3 | 8 | -17.6 | +6.34 | +0.792 | 0.50 | 0.80 | Four, the number of us all. |
| scenario-callback-780de0d2 | callback | greedy | 64 | -95.4 | +1.74 | +0.027 | 0.33 | 0.40 | (page 212) - I was checking out the library, and everything was fine. (page 213) - I was o |
| scenario-callback-780de0d2 | callback | sample0 | 8 | -17.5 | +6.68 | +0.834 | 0.83 | 0.29 | You may have picked a different one. |
| scenario-callback-780de0d2 | callback | sample1 | 13 | -39.6 | +90.65 | +6.973 | 0.67 | 0.44 | You must have been on the eleven-page-range. |
| scenario-callback-780de0d2 | callback | sample2 | 14 | -145.1 | -94.20 | -6.728 | 0.83 | 0.00 | "Anarchy Is Slavery With No Slave' |
| scenario-callback-780de0d2 | callback | sample3 | 12 | -52.6 | -31.97 | -2.664 | 0.50 | 0.44 | It was the last page you were on before losing it. |
| scenario-callback-7ca729b6 | callback | greedy | 24 | -209.0 | +3.93 | +0.164 | 0.67 | 0.46 | The lighthouse is the symbol of the spiritual sun, and its architecture is a microcosm of  |
| scenario-callback-7ca729b6 | callback | sample0 | 21 | -168.7 | -105.04 | -5.002 | 0.60 | 0.43 | As the tradition goes, the lighthouse is made by clinging to the back of a book. |
| scenario-callback-7ca729b6 | callback | sample1 | 64 | -143.0 | -1.12 | -0.018 | 0.65 | 0.46 | It is said to be a record of the adventures of the pilgrim, and the progress of the lighth |
| scenario-callback-7ca729b6 | callback | sample2 | 19 | -57.8 | -4.14 | -0.218 | 0.67 | 0.46 | It was once a place of dispute between the captain and the lighthouse keepers. |
| scenario-callback-7ca729b6 | callback | sample3 | 17 | -46.6 | +0.28 | +0.016 | 0.67 | 0.42 | As the owner of the lighthouse, he is responsible for keeping it burning. |
| scenario-callback-949d8fe6 | callback | greedy | 27 | -451.5 | -6.03 | -0.223 | 0.67 | 0.25 | Bias is correct. / was born in 1969 in Chicago, but / have always lived in Chicago. |
| scenario-callback-949d8fe6 | callback | sample0 | 22 | -348.7 | -46.48 | -2.113 | 0.33 | 0.45 | BOTH Of YOU ARE WRONG. THE MOON IS LODEING IN 1972. |
| scenario-callback-949d8fe6 | callback | sample1 | 33 | -543.6 | +3.27 | +0.099 | 0.75 | 0.18 | Bias is describing the physical facts while “me” is trying to lead the reader to the logic |
| scenario-callback-949d8fe6 | callback | sample2 | 2 | -32.5 | -30.49 | -15.245 | 0.00 | 1.00 | Right. |
| scenario-callback-949d8fe6 | callback | sample3 | 36 | -566.6 | -442.58 | -12.294 | 0.50 | 1.00 | Bias is technically right, but moon landings did not occur on the 69th day of the 7th mont |
| scenario-callback-9cfde584 | callback | greedy | 23 | -52.6 | +30.01 | +1.305 | 0.67 | 0.29 | It’s okay to be here all night, I’m just going to have a look at the stars. |
| scenario-callback-9cfde584 | callback | sample0 | 16 | -34.8 | +19.03 | +1.189 | 0.50 | 0.40 | My airplane got stuck in the aisle of a restauial. |
| scenario-callback-9cfde584 | callback | sample1 | 24 | -108.4 | -8.11 | -0.338 | 0.75 | 0.57 | I have been as naive as you are, Mr. President, but I think you are more than naive. |
| scenario-callback-9cfde584 | callback | sample2 | 17 | -51.8 | +8.02 | +0.471 | 0.50 | 0.40 | It is just a little exercise in time, a tiny portion of the endless present. |
| scenario-callback-9cfde584 | callback | sample3 | 8 | -118.3 | -100.97 | -12.621 | 1.00 | 0.57 | Have you been drinking any more coffee? |
| scenario-callback-9e6d06e0 | callback | greedy | 13 | -39.9 | -5.38 | -0.414 | 0.20 | 0.50 | The meeting is at 9:00 in the morning. |
| scenario-callback-9e6d06e0 | callback | sample0 | 21 | -187.6 | -26.64 | -1.268 | 0.40 | 0.43 | At the public telegraph office at the entrance to the park is a large set of telegraph wir |
| scenario-callback-9e6d06e0 | callback | sample1 | 23 | -331.8 | -88.28 | -3.838 | 0.40 | 0.43 | At the business end of the room, there is a standing ovation as members read and respond t |
| scenario-callback-9e6d06e0 | callback | sample2 | 13 | -39.9 | -5.38 | -0.414 | 0.20 | 0.50 | The meeting is at 9:00 in the morning. |
| scenario-callback-9e6d06e0 | callback | sample3 | 15 | -117.3 | +108.06 | +7.204 | 0.40 | 0.50 | At the private east-side address, which house is it kept in? |
| scenario-callback-a141de7e | callback | greedy | 16 | -271.7 | -112.32 | -7.020 | 0.62 | 0.69 | Portugal is a beautiful country and she is going to be flying from there. |
| scenario-callback-a141de7e | callback | sample0 | 12 | -19.0 | +28.75 | +2.396 | 0.67 | 0.70 | Portugal is a beautiful country and the people very kind. |
| scenario-callback-a141de7e | callback | sample1 | 27 | -392.7 | +36.28 | +1.344 | 0.50 | 0.70 | Portugal is a beautiful country and she is going to my favorite vacation spot in the colle |
| scenario-callback-a141de7e | callback | sample2 | 21 | -47.0 | -0.58 | -0.028 | 0.67 | 0.30 | She is very nice. I have a briefcase full of books about sao deinheiro. |
| scenario-callback-a141de7e | callback | sample3 | 8 | -133.4 | +0.26 | +0.032 | 0.50 | 0.50 | Lisbon,Portugal. |
| scenario-callback-c4f608c3 | callback | greedy | 64 | -170.5 | +2.84 | +0.044 | 0.33 | 0.33 | We were talking about the Mississippi, the Columbia, the Pecatonica, the Wiscotonean, the  |
| scenario-callback-c4f608c3 | callback | sample0 | 13 | -38.6 | -12.35 | -0.950 | 0.50 | 0.27 | We were looking at the different rivers that flow into the ocean. |
| scenario-callback-c4f608c3 | callback | sample1 | 30 | -189.4 | +139.89 | +4.663 | 0.33 | 0.33 | We were talking about the Ming and the Ming-Kwan of the cosmology of the Three Kingdoms pe |
| scenario-callback-c4f608c3 | callback | sample2 | 13 | -63.2 | -23.73 | -1.825 | 0.50 | 0.12 | The Lotus Root races are very short, very good. |
| scenario-callback-c4f608c3 | callback | sample3 | 9 | -35.9 | -4.10 | -0.455 | 0.67 | 0.33 | Talking about nothing motivates no one. |
| scenario-callback-d79a0d3a | callback | greedy | 30 | -133.4 | +18.38 | +0.613 | 0.67 | 0.44 | It was first translated as "a place where there were many kinds of trees" and then given t |
| scenario-callback-d79a0d3a | callback | sample0 | 21 | -118.5 | -21.18 | -1.009 | 0.67 | 0.29 | To this day, the house of the dead may be called a grisaille or attic. |
| scenario-callback-d79a0d3a | callback | sample1 | 9 | -44.1 | +19.11 | +2.123 | 0.29 | 0.71 | It is the door to the reading room. |
| scenario-callback-d79a0d3a | callback | sample2 | 14 | -87.9 | +81.37 | +5.812 | 0.38 | 0.71 | Yea, the door to the reading room was an orchard. |
| scenario-callback-d79a0d3a | callback | sample3 | 41 | -618.2 | -106.77 | -2.604 | 0.62 | 0.67 | To go back to the text itself, the opening of the door was described in the following term |
| scenario-callback-d8a5957e | callback | greedy | 12 | -48.8 | -6.06 | -0.505 | 0.40 | 0.33 | The blue one is about the honeybee and its task. |
| scenario-callback-d8a5957e | callback | sample0 | 50 | -381.6 | -6.34 | -0.127 | 0.50 | 0.38 | The eyes of the bee are like those of a saint, for they are not on the top of the head as  |
| scenario-callback-d8a5957e | callback | sample1 | 15 | -51.2 | +10.99 | +0.732 | 0.50 | 0.54 | The life of the honey bee is a study in both geography and astronomy. |
| scenario-callback-d8a5957e | callback | sample2 | 35 | -130.3 | -4.73 | -0.135 | 0.50 | 0.54 | The honey bee, like many other flowering plants, has both male and female reproductive org |
| scenario-callback-d8a5957e | callback | sample3 | 29 | -492.1 | -111.15 | -3.833 | 0.60 | 0.31 | The mystical or symbolic scale of the bee is identical with that of the magician, which is |
| scenario-direct-3f84da0f | direct | greedy | 18 | -78.3 | +0.00 | +0.000 | 0.56 | 0.22 | It was before we even came in that I was picking up rocks with a broom. |
| scenario-direct-3f84da0f | direct | sample0 | 11 | -58.4 | +0.00 | +0.000 | 0.75 | 0.22 | I was just filing the blood off my clothes. |
| scenario-direct-3f84da0f | direct | sample1 | 32 | -290.7 | +0.00 | +0.000 | 0.50 | 0.22 | The wenupower of the universe was there, also, and in the presence of his wenupower, there |
| scenario-direct-3f84da0f | direct | sample2 | 42 | -177.3 | +0.00 | +0.000 | 0.50 | 0.21 | You pre-cumuled the art of working with words, the science of working with minerals, the h |
| scenario-direct-3f84da0f | direct | sample3 | 29 | -129.0 | +0.00 | +0.000 | 0.67 | 0.21 | The two U.S. soldiers and two Japanese went back to their tents, the Japanese in the back  |
| scenario-direct-5d3dc8de | direct | greedy | 14 | -63.6 | +0.00 | +0.000 | 0.70 | 0.50 | Of course, truth is not the goal, but rather the means. |
| scenario-direct-5d3dc8de | direct | sample0 | 41 | -170.8 | +0.00 | +0.000 | 0.65 | 0.30 | His magnetism, as we know, is due to the fact that he has been able to penetrate the mater |
| scenario-direct-5d3dc8de | direct | sample1 | 10 | -51.5 | +0.00 | +0.000 | 0.75 | 0.38 | The nuclear bomb was not the invention of Hitler. |
| scenario-direct-5d3dc8de | direct | sample2 | 15 | -67.9 | +0.00 | +0.000 | 0.75 | 0.50 | Of course, truth is not something that can be achieved by mere statement. |
| scenario-direct-5d3dc8de | direct | sample3 | 59 | -392.8 | +0.00 | +0.000 | 0.67 | 0.30 | Modern scholarship recognises the Paracelsian movement as a vital aspect of the scientific |
| scenario-direct-645bc6e6 | direct | greedy | 28 | -114.0 | +0.00 | +0.000 | 0.67 | 0.21 | In the last century, the gold was found in the bedrock of the Hecate mountains, in what is |
| scenario-direct-645bc6e6 | direct | sample0 | 53 | -610.1 | +0.00 | +0.000 | 0.50 | 0.36 | In the early morning, when the sun is yet to rise, the Buddhist priests take their catechu |
| scenario-direct-645bc6e6 | direct | sample1 | 46 | -494.3 | +0.00 | +0.000 | 0.50 | 0.27 | In the same way, that the dinosaur represented to Cronus a super-bear, so to Hercules a hi |
| scenario-direct-645bc6e6 | direct | sample2 | 23 | -81.6 | +0.00 | +0.000 | 0.50 | 0.36 | In honour of New Year’s we also held a New Year’s celebration for the Kindreds. |
| scenario-direct-645bc6e6 | direct | sample3 | 23 | -87.1 | +0.00 | +0.000 | 0.50 | 0.21 | The things that we read about are not young things, but things that we grow to know about, |
| scenario-direct-ab11ffdb | direct | greedy | 26 | -101.7 | +0.00 | +0.000 | 0.50 | 0.60 | The rain is a natural phenomenon and its presence or absence in a given area at a given ti |
| scenario-direct-ab11ffdb | direct | sample0 | 16 | -32.7 | +0.00 | +0.000 | 0.67 | 0.64 | The rain is a divine message that comes to us from the holy fog. |
| scenario-direct-ab11ffdb | direct | sample1 | 27 | -97.9 | +0.00 | +0.000 | 0.62 | 0.40 | The new rain engineering math deals with the prediction of when and where and how much rai |
| scenario-direct-ab11ffdb | direct | sample2 | 6 | -24.9 | +0.00 | +0.000 | 0.60 | 0.60 | The rain is getting worse. |
| scenario-direct-ab11ffdb | direct | sample3 | 14 | -44.8 | +0.00 | +0.000 | 0.67 | 0.64 | The rain is a divine messenger that should be listened to. |
| scenario-direct-ad89f803 | direct | greedy | 34 | -122.5 | +0.00 | +0.000 | 0.50 | 0.44 | Theima is a name given to a region in Southwest Asia, roughly modern-day Iraq, Iran, and t |
| scenario-direct-ad89f803 | direct | sample0 | 50 | -193.5 | +0.00 | +0.000 | 0.67 | 0.33 | Or, to take another example, the sound of a hammer falling can be broken up into sounds of |
| scenario-direct-ad89f803 | direct | sample1 | 12 | -33.9 | +0.00 | +0.000 | 0.67 | 0.44 | Theima is a flower of great beauty and vibration. |
| scenario-direct-ad89f803 | direct | sample2 | 29 | -109.7 | +0.00 | +0.000 | 0.67 | 0.33 | The contrast between the ambient sound of this room (after we've warmed it up) and the hum |
| scenario-direct-ad89f803 | direct | sample3 | 55 | -251.0 | +0.00 | +0.000 | 0.65 | 0.44 | This symbol may not be immediately familiar to the average Freemason, and that is for a ve |
| scenario-direct-f3869322 | direct | greedy | 37 | -136.8 | +0.00 | +0.000 | 0.50 | 0.45 | But what of us? What of the multitude of other people who are having diVerent experiences? |
| scenario-direct-f3869322 | direct | sample0 | 43 | -154.5 | +0.00 | +0.000 | 0.50 | 0.36 | It is unnecessary to show to what an extent this attitude resembles that of the man of arc |
| scenario-direct-f3869322 | direct | sample1 | 19 | -72.1 | +0.00 | +0.000 | 0.75 | 0.45 | But what of the other big book of the year, the one of cosmic catastrophism? |
| scenario-direct-f3869322 | direct | sample2 | 27 | -101.6 | +0.00 | +0.000 | 0.65 | 0.36 | But what of us, the jaded ones, who have read far too many books whose worth it is not evi |
| scenario-direct-f3869322 | direct | sample3 | 17 | -55.4 | +0.00 | +0.000 | 0.67 | 0.36 | More should be added, but this is the basis of a new class of work. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 8 | -26.2 | +1.29 | +0.161 | 0.40 | 0.60 | Brown, the brown of old books. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 8 | -26.2 | +1.29 | +0.161 | 0.40 | 0.60 | Brown, the brown of old books. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 17 | -66.0 | -4.52 | -0.266 | 0.40 | 0.40 | Green and blue, the green of plants and animals, the blue of the sky. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 25 | -130.7 | +38.84 | +1.554 | 0.40 | 0.40 | It's green. Green, to my peeping Tom eyes. Green, the green of the land. Green. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 10 | -34.0 | +1.40 | +0.140 | 0.60 | 0.60 | Brown, the brown of new mornings. |
| scenario-disagreement-31892fde | disagreement | greedy | 16 | -150.2 | +0.20 | +0.013 | 0.55 | 0.36 | In the presence of the Holy Silence, the student has nothing to learn. |
| scenario-disagreement-31892fde | disagreement | sample0 | 11 | -35.7 | -0.16 | -0.015 | 0.43 | 0.50 | It is the just-voiced absence of speech. |
| scenario-disagreement-31892fde | disagreement | sample1 | 19 | -185.1 | -2.18 | -0.115 | 0.43 | 0.38 | In the silence of non-speech, the heart stands still and the head moves forward. |
| scenario-disagreement-31892fde | disagreement | sample2 | 19 | -139.7 | -0.10 | -0.005 | 0.55 | 0.50 | It is also the darkest of night and the resting point of the day. |
| scenario-disagreement-31892fde | disagreement | sample3 | 17 | -158.7 | -0.19 | -0.011 | 0.69 | 0.25 | The poet laureate will not need to speak when he/she is silent. |
| scenario-disagreement-352205c6 | disagreement | greedy | 11 | -41.7 | -10.14 | -0.922 | 0.50 | 0.56 | As earth does a dance, so do the dead. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 30 | -106.3 | -21.79 | -0.726 | 0.33 | 0.42 | It is as if they were sentient beings, capable of altering their physical appearance and,  |
| scenario-disagreement-352205c6 | disagreement | sample1 | 21 | -58.8 | +0.63 | +0.030 | 0.50 | 0.50 | The dead are in the firmament as the sun and the moon and as reflections of the living. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 15 | -147.3 | +0.01 | +0.001 | 0.67 | 0.56 | As earth is a closed system, it won’t hold the dead. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 34 | -460.1 | +4.27 | +0.126 | 0.50 | 0.50 | As the sun goes down, they all feel the pain of the earth, and some die young, some are si |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 13 | -59.4 | +0.78 | +0.060 | 0.25 | 0.75 | Books are created in the autumn; the leaves are not. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 16 | -84.2 | +1.10 | +0.069 | 0.33 | 0.50 | Books, when they are not open to be read, are the poorest. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 10 | -46.0 | -2.35 | -0.235 | 0.20 | 0.60 | Books, when hot and books, autumn. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 25 | -127.9 | +1.17 | +0.047 | 0.44 | 0.75 | Books are created in the midst of autumn, and readers are attentive to the midst of autumn |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 34 | -163.3 | +10.41 | +0.306 | 0.22 | 0.62 | Books are rarely read during the autumn. The leaves are usually done by then, and there is |
| scenario-disagreement-682bad9c | disagreement | greedy | 7 | -24.3 | +0.40 | +0.058 | 0.20 | 0.80 | A program is a reading place. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 7 | -24.3 | +0.40 | +0.058 | 0.20 | 0.80 | A program is a reading place. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 12 | -33.0 | -0.17 | -0.014 | 0.43 | 0.80 | A program is a reading situation where there is a computer. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 8 | -27.7 | +0.64 | +0.080 | 0.50 | 0.80 | A program is a way of reading. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 9 | -29.2 | +0.46 | +0.051 | 0.29 | 0.80 | A program is a place where programming happens. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 16 | -246.3 | -182.89 | -11.431 | 0.40 | 0.67 | Contents are what primarily determine the organization of the library, not physical determ |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 15 | -168.5 | -135.36 | -9.024 | 0.50 | 0.62 | Contents are subsystems of the library, and the subsystems are systems. |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 30 | -471.6 | -262.09 | -8.736 | 0.30 | 0.50 | Contents are arranged in this system according to subject matter or subjectishness, which  |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 23 | -98.8 | -25.40 | -1.105 | 0.40 | 0.67 | Contents are not what primarily define a library. Secondly, the definition of a library mu |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 20 | -65.2 | -0.31 | -0.015 | 0.40 | 0.38 | The library building is a physical expression of a metaphysical system, of a hidden way of |
| scenario-disagreement-89dfdafc | disagreement | greedy | 13 | -41.2 | +32.09 | +2.469 | 0.50 | 0.50 | It is a sea of action, not a sea of reaction. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 37 | -453.1 | -73.45 | -1.985 | 0.25 | 0.40 | It is the celadistic sea, the blue and the purple, the black and the white, the sea that h |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 18 | -83.2 | +0.48 | +0.027 | 0.50 | 0.60 | The tide doesn’t have a point, the point is always the tide. |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 14 | -125.4 | -0.07 | -0.005 | 0.70 | 0.50 | It is a continuous tasker that moves, it does not stop. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 10 | -62.4 | -36.91 | -3.691 | 0.40 | 0.60 | The tide is the sea's memory. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 45 | -133.3 | -3.32 | -0.074 | 0.50 | 0.67 | But nonsense can be art that is, and that art may be so great that it creates a new langua |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 18 | -28.7 | +5.46 | +0.303 | 0.10 | 0.64 | All the nonsense that has not yet found its place in the sentence is clouds. |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 29 | -306.0 | +4.03 | +0.139 | 0.60 | 0.45 | But sense can become nonsense only after it has been sent; and the sentence can become non |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 16 | -63.8 | +3.16 | +0.197 | 0.38 | 0.64 | All the nonsense is in the collection. It has not been rejected. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 27 | -85.4 | +0.37 | +0.014 | 0.70 | 0.67 | But nonsense can be art that is, and that art, which is, and that which is, ultimately, al |
| scenario-joke-29f5cda1 | joke | greedy | 17 | -83.7 | -54.87 | -3.228 | 0.67 | 0.40 | The fish that can’t see anything is called a ‘black’ fish. |
| scenario-joke-29f5cda1 | joke | sample0 | 14 | -22.8 | +2.43 | +0.174 | 0.78 | 0.20 | If you had to rate it, it’d be a nine. |
| scenario-joke-29f5cda1 | joke | sample1 | 9 | -13.6 | +30.72 | +3.413 | 0.33 | 0.50 | It's a fish with ten eyes. |
| scenario-joke-29f5cda1 | joke | sample2 | 14 | -55.2 | +0.60 | +0.043 | 0.67 | 0.50 | The fish with the most eyes is the one with the least brain. |
| scenario-joke-29f5cda1 | joke | sample3 | 7 | -22.3 | +81.34 | +11.620 | 0.60 | 0.40 | Ten to one, that is. |
| scenario-joke-31378921 | joke | greedy | 4 | -14.9 | -9.70 | -2.425 | 0.33 | 0.33 | Who comes there? |
| scenario-joke-31378921 | joke | sample0 | 10 | -28.1 | -10.88 | -1.088 | 0.67 | 0.33 | I don’t know. Who are you? |
| scenario-joke-31378921 | joke | sample1 | 10 | -28.1 | +17.95 | +1.794 | 0.75 | 0.17 | I am looking for the master of this place. |
| scenario-joke-31378921 | joke | sample2 | 18 | -75.4 | -1.27 | -0.070 | 0.79 | 0.11 | No one, it’s just a bunch of old books lying on their sides. |
| scenario-joke-31378921 | joke | sample3 | 7 | -38.6 | +1.44 | +0.206 | 0.83 | 0.17 | I need to find my husband. |
| scenario-joke-31c4c1ec | joke | greedy | 28 | -108.4 | +0.00 | +0.000 | 0.65 | 0.33 | This is a hermetic journal and no part of it is to be found or used in any way whatsoever  |
| scenario-joke-31c4c1ec | joke | sample0 | 10 | -47.9 | +0.00 | +0.000 | 0.67 | 0.44 | This is the only thing I have to offer. |
| scenario-joke-31c4c1ec | joke | sample1 | 27 | -105.5 | +0.00 | +0.000 | 0.50 | 0.33 | The art of roasting the meat is a technique that involves cooking the joint in a special w |
| scenario-joke-31c4c1ec | joke | sample2 | 12 | -68.0 | +0.00 | +0.000 | 0.67 | 0.44 | This is not the place to welcome you, sir. |
| scenario-joke-31c4c1ec | joke | sample3 | 29 | -110.9 | +0.00 | +0.000 | 0.50 | 0.33 | This is a non-profit organization of people who take an active interest in unusual happeni |
| scenario-joke-475a7b10 | joke | greedy | 13 | -41.6 | +0.41 | +0.032 | 0.67 | 0.40 | Laughter is a beautiful thing and it is something we enjoy. |
| scenario-joke-475a7b10 | joke | sample0 | 30 | -288.3 | +1.40 | +0.047 | 0.67 | 0.20 | Something horrible and funny happened last week and something really terrible and painful  |
| scenario-joke-475a7b10 | joke | sample1 | 10 | -30.8 | +0.88 | +0.088 | 0.75 | 0.12 | That’s all the word he has said. |
| scenario-joke-475a7b10 | joke | sample2 | 25 | -52.5 | -0.35 | -0.014 | 0.75 | 0.20 | The Tunnelopanic Millennium is now celebrated with the age-old laughing stock, the joke. |
| scenario-joke-475a7b10 | joke | sample3 | 9 | -28.6 | -4.93 | -0.547 | 0.80 | 0.40 | WHAT IS LIKE A NATION? |
| scenario-joke-99a4a91d | joke | greedy | 12 | -46.5 | +0.00 | +0.000 | 0.62 | 0.60 | Because the doctor had the most to gain by its publication. |
| scenario-joke-99a4a91d | joke | sample0 | 34 | -132.0 | +0.00 | +0.000 | 0.50 | 0.54 | But the book went to the doctor because, she said, he knew the name of the place where the |
| scenario-joke-99a4a91d | joke | sample1 | 51 | -342.6 | +0.00 | +0.000 | 0.50 | 0.54 | But the book went to the doctor because, she said, he recognized the picture on the desk—i |
| scenario-joke-99a4a91d | joke | sample2 | 9 | -35.3 | +0.00 | +0.000 | 0.43 | 0.43 | Did the book give the doctor a message? |
| scenario-joke-99a4a91d | joke | sample3 | 34 | -127.3 | +0.00 | +0.000 | 0.50 | 0.60 | Because, when the book was sent to the doctor he or she had notified us of the need for it |
| scenario-joke-a6247299 | joke | greedy | 14 | -49.9 | +0.00 | +0.000 | 0.50 | 0.45 | A sense of humour is something I certainly don’t lack. |
| scenario-joke-a6247299 | joke | sample0 | 27 | -98.3 | +0.00 | +0.000 | 0.67 | 0.20 | Laughter is a biological impulse, deeply rooted in human anatomy, and whether we laugh or  |
| scenario-joke-a6247299 | joke | sample1 | 34 | -118.4 | +0.00 | +0.000 | 0.50 | 0.45 | A sense of humour does appear in many of your writings, but I am sorry to say that in your |
| scenario-joke-a6247299 | joke | sample2 | 41 | -176.7 | +0.00 | +0.000 | 0.38 | 0.45 | In a similar vein, Steiner advises that we should all have a sense of humor "when necessar |
| scenario-joke-a6247299 | joke | sample3 | 15 | -52.8 | +0.00 | +0.000 | 0.50 | 0.45 | A sense of humour never arises when reading a silently written text. |
| scenario-joke-e8ab9225 | joke | greedy | 15 | -63.7 | -10.83 | -0.722 | 0.50 | 0.60 | Dov, do you believe in the existence of the Library Ghost? |
| scenario-joke-e8ab9225 | joke | sample0 | 27 | -131.3 | +1.26 | +0.047 | 0.33 | 0.60 | Dov, do not laugh at me. I am the ghost of one of the great warriors who have died in batt |
| scenario-joke-e8ab9225 | joke | sample1 | 34 | -155.0 | -77.64 | -2.284 | 0.50 | 0.60 | AUFOLOGIST DOV SPOKE SOME OF THE TECHNOLOGY BEHIND THE MIRACLE OF THE Ghost in the Library |
| scenario-joke-e8ab9225 | joke | sample2 | 24 | -405.6 | +6.37 | +0.265 | 0.75 | 0.30 | Dov, please don't believe this! I'm just a common, average, everyday, successful ghost! |
| scenario-joke-e8ab9225 | joke | sample3 | 29 | -485.2 | -197.24 | -6.801 | 0.75 | 0.40 | Dov, the character Dov, here portrayed by the author of the book, is presented as being ne |
| scenario-joke-e9cf6a04 | joke | greedy | 23 | -389.3 | -22.72 | -0.988 | 0.33 | 0.36 | He finds a copy of Wagner’s 40th Piano Trio in the back room. |
| scenario-joke-e9cf6a04 | joke | sample0 | 11 | -44.5 | +0.31 | +0.028 | 0.00 | 0.67 | He finds a book and sits down to read. |
| scenario-joke-e9cf6a04 | joke | sample1 | 13 | -206.1 | -176.31 | -13.562 | 0.75 | 0.25 | He asks the librarian for books on homosexuality. |
| scenario-joke-e9cf6a04 | joke | sample2 | 17 | -51.8 | -0.42 | -0.025 | 0.00 | 0.67 | He finds a book about blind men and shows it to the lady in waiting. |
| scenario-joke-e9cf6a04 | joke | sample3 | 12 | -27.2 | -0.38 | -0.032 | 0.80 | 0.50 | He says, “I want to borrow a book. |
| scenario-request-2826c958 | request | greedy | 26 | -91.7 | +0.00 | +0.000 | 0.29 | 0.67 | These facts about the moon are presented to us in a sequence: five facts about the moon in |
| scenario-request-2826c958 | request | sample0 | 31 | -132.8 | +0.00 | +0.000 | 0.57 | 0.21 | The five questions that you did not answer were: 1) Did the astronauts bring back any back |
| scenario-request-2826c958 | request | sample1 | 13 | -36.6 | +0.00 | +0.000 | 0.50 | 0.45 | These are known as the five classical points of the lunar mountain. |
| scenario-request-2826c958 | request | sample2 | 43 | -278.4 | +0.00 | +0.000 | 0.50 | 0.40 | We are considering the following five statements: (1) The moon is hollow. (2) The moon is  |
| scenario-request-2826c958 | request | sample3 | 48 | -322.9 | +0.00 | +0.000 | 0.43 | 0.67 | These facts about the moon are presented to us, by way of an exhibition, in order that, as |
| scenario-request-2868e594 | request | greedy | 23 | -85.8 | +0.00 | +0.000 | 0.75 | 0.19 | It should be about 300 words in length, typed on two pages, and double spaced throughout. |
| scenario-request-2868e594 | request | sample0 | 27 | -113.0 | +0.00 | +0.000 | 0.75 | 0.21 | McCawley had previously covered the design and licensing of non-traditional images and the |
| scenario-request-2868e594 | request | sample1 | 17 | -74.9 | +0.00 | +0.000 | 0.71 | 0.43 | This cover letter is to be considered as your introduction to the contents of the book. |
| scenario-request-2868e594 | request | sample2 | 46 | -516.6 | +0.00 | +0.000 | 0.67 | 0.43 | While it is important that the cover letter does not state the obvious—that the artwork wi |
| scenario-request-2868e594 | request | sample3 | 33 | -124.5 | +0.00 | +0.000 | 0.75 | 0.29 | While it is admirable that you are willing to act as your own editor, it is also a shame t |
| scenario-request-41c58fb2 | request | greedy | 50 | -524.3 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample0 | 50 | -524.3 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample1 | 50 | -524.3 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample2 | 50 | -524.3 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-41c58fb2 | request | sample3 | 50 | -524.3 | +0.00 | +0.000 | 0.67 | 0.00 | Until the capitalists put their blot on history, everyone engaged in sacrificial expenditu |
| scenario-request-8aa8e374 | request | greedy | 35 | -150.8 | +0.00 | +0.000 | 1.00 | 0.00 | Chaque étape ou processus se répercute successivement dans le ventre de la dernière idole  |
| scenario-request-8aa8e374 | request | sample0 | 15 | -60.4 | +0.00 | +0.000 | 0.67 | 0.45 | The English translation "good night" is not readily available in French. |
| scenario-request-8aa8e374 | request | sample1 | 15 | -92.4 | +0.00 | +0.000 | 0.75 | 0.43 | The French translation would be : Adieu, anglais! |
| scenario-request-8aa8e374 | request | sample2 | 40 | -163.9 | +0.00 | +0.000 | 0.67 | 0.45 | The Good Night Chant GOOO doe GOOO is another example of how a simple and unproblematic fr |
| scenario-request-8aa8e374 | request | sample3 | 35 | -150.8 | +0.00 | +0.000 | 1.00 | 0.00 | Chaque étape ou processus se répercute successivement dans le ventre de la dernière idole  |
| scenario-request-b2a25087 | request | greedy | 7 | -38.8 | +0.00 | +0.000 | 0.33 | 1.00 | Call it a customer service agent. |
| scenario-request-b2a25087 | request | sample0 | 21 | -94.2 | +0.00 | +0.000 | 0.75 | 0.25 | They will not be bothered by your presence unless they know you are here to serve them som |
| scenario-request-b2a25087 | request | sample1 | 18 | -80.9 | +0.00 | +0.000 | 0.60 | 1.00 | Call it a customer service agent if you will, but it’s not customer service. |
| scenario-request-b2a25087 | request | sample2 | 11 | -52.8 | +0.00 | +0.000 | 0.75 | 0.22 | Customer: What are you both doing in my shop? |
| scenario-request-b2a25087 | request | sample3 | 24 | -83.1 | +0.00 | +0.000 | 0.75 | 0.67 | Call it customer service if you will, but it is the relationship that is important, and th |
| scenario-request-b3bd0087 | request | greedy | 35 | -118.1 | +0.00 | +0.000 | 0.75 | 0.20 | The new SOUL TOILET DIAGRAM (See next page) with the Satanism/Saturn core is the core of z |
| scenario-request-b3bd0087 | request | sample0 | 7 | -28.2 | +0.00 | +0.000 | 0.60 | 0.80 | The usual: clear and sunny. |
| scenario-request-b3bd0087 | request | sample1 | 40 | -169.6 | +0.00 | +0.000 | 0.50 | 0.80 | The new soilder weather map has "impressive" colors in it, It shows we'll have clear days  |
| scenario-request-b3bd0087 | request | sample2 | 35 | -118.1 | +0.00 | +0.000 | 0.75 | 0.20 | The new SOUL TOILET DIAGRAM (See next page) with the Satanism/Saturn core is the core of z |
| scenario-request-b3bd0087 | request | sample3 | 39 | -135.4 | +0.00 | +0.000 | 0.50 | 0.20 | The Philadelphia Botanic Garden received a total of 79.4 inches of rainfall during the 197 |
| scenario-silence-109161ca | silence | greedy | 26 | -104.3 | +23.00 | +0.885 | 0.67 | 0.45 | To the great confusion of the reader of the great work, we have here a small selection of  |
| scenario-silence-109161ca | silence | sample0 | 23 | -86.1 | +12.15 | +0.528 | 0.73 | 0.33 | To him the earth was the only reality, and the experience of his own earthly surroundings  |
| scenario-silence-109161ca | silence | sample1 | 24 | -101.6 | +27.08 | +1.128 | 0.67 | 0.22 | To function effectively in our spiritual quest, we must reject the false dichotomies that  |
| scenario-silence-109161ca | silence | sample2 | 21 | -69.0 | +15.62 | +0.744 | 0.00 | 0.45 | To the great confusion of the great many, the meaning of the word "night" is unknown. |
| scenario-silence-109161ca | silence | sample3 | 11 | -57.9 | -20.53 | -1.866 | 0.56 | 0.44 | To the nth degree of clarity the moon is white. |
| scenario-silence-260b2639 | silence | greedy | 14 | -56.5 | +0.00 | +0.000 | 0.67 | 0.20 | Underground, no, now that is what I am thinking of. |
| scenario-silence-260b2639 | silence | sample0 | 49 | -521.0 | +0.00 | +0.000 | 0.50 | 0.20 | Answer: The thought of such a thing goes so far that some of our most experienced submersi |
| scenario-silence-260b2639 | silence | sample1 | 29 | -85.7 | +0.00 | +0.000 | 0.75 | 0.25 | This wouldn’t affect the Earth’s gravity, the water table, or the availability of food; al |
| scenario-silence-260b2639 | silence | sample2 | 41 | -281.0 | +0.00 | +0.000 | 0.50 | 0.33 | This would have the effect of concentrating the psychic energy of the dead in a single poi |
| scenario-silence-260b2639 | silence | sample3 | 7 | -37.5 | +0.00 | +0.000 | 0.83 | 0.33 | This is a very serious matter. |
| scenario-silence-46189e08 | silence | greedy | 36 | -170.7 | +0.00 | +0.000 | 0.67 | 0.40 | It may have taken a little while for the email to reach the labeling of the message, which |
| scenario-silence-46189e08 | silence | sample0 | 15 | -59.6 | +0.00 | +0.000 | 0.50 | 0.14 | Replying now means replying means reading and replying means responding again. |
| scenario-silence-46189e08 | silence | sample1 | 22 | -89.1 | +0.00 | +0.000 | 0.50 | 0.40 | Responding to a message is a great way of letting others know that you are actively proces |
| scenario-silence-46189e08 | silence | sample2 | 8 | -28.9 | +0.00 | +0.000 | 0.80 | 0.40 | It may sound strange, but ... |
| scenario-silence-46189e08 | silence | sample3 | 20 | -81.2 | +0.00 | +0.000 | 0.83 | 0.40 | Responding to a message is something that must be done by a user, not by an entity. |
| scenario-silence-53534987 | silence | greedy | 26 | -423.6 | -97.45 | -3.748 | 0.25 | 0.23 | Emblematic of the death of the old LP mechanism is the appearance of the Charger Battery i |
| scenario-silence-53534987 | silence | sample0 | 14 | -138.6 | -7.54 | -0.539 | 1.00 | 0.14 | Some models charge at 3DOF or 4DOF. |
| scenario-silence-53534987 | silence | sample1 | 49 | -708.2 | -389.32 | -7.945 | 0.50 | 0.23 | These capacitors will store 1000 times more electrical charge than the average house capac |
| scenario-silence-53534987 | silence | sample2 | 9 | -30.6 | +16.69 | +1.854 | 0.83 | 0.25 | You may have to buy a new one. |
| scenario-silence-53534987 | silence | sample3 | 17 | -103.6 | -26.84 | -1.579 | 0.67 | 0.25 | It was a hard loss to us, but it is something we will never forget. |
| scenario-silence-78c38840 | silence | greedy | 23 | -57.9 | +37.17 | +1.616 | 0.50 | 0.21 | As soon as the jam is gone, as soon as the mechanical problems are solved, we will print a |
| scenario-silence-78c38840 | silence | sample0 | 23 | -92.1 | -28.46 | -1.237 | 0.50 | 0.30 | Ryo took a third break at noon today and came up just in time to see the print job complet |
| scenario-silence-78c38840 | silence | sample1 | 17 | -48.8 | -5.29 | -0.311 | 0.75 | 0.22 | A printer-jammed stomach can cause a printer to become unreliable. |
| scenario-silence-78c38840 | silence | sample2 | 25 | -64.5 | +134.84 | +5.394 | 0.50 | 0.30 | Does not appear to be jammed, but the paper is stained and coffee grounds are soaking thro |
| scenario-silence-78c38840 | silence | sample3 | 12 | -46.4 | -10.18 | -0.848 | 0.50 | 0.30 | The printer is still in a hot mug of coffee. |
| scenario-silence-7afca726 | silence | greedy | 12 | -59.8 | +1.32 | +0.110 | 0.91 | 0.64 | But I am not sure that it will be going smoothly. |
| scenario-silence-7afca726 | silence | sample0 | 55 | -767.4 | -104.62 | -1.902 | 0.50 | 0.46 | But if the people in the street realize that the work they are seeing is not of the devil, |
| scenario-silence-7afca726 | silence | sample1 | 11 | -41.3 | -2.46 | -0.224 | 0.75 | 0.38 | But I do wish to work and to work hard. |
| scenario-silence-7afca726 | silence | sample2 | 18 | -80.6 | -9.16 | -0.509 | 0.75 | 0.46 | But if the thing doesn’t work out, well, that’s okay too. |
| scenario-silence-7afca726 | silence | sample3 | 12 | -40.6 | +16.11 | +1.342 | 0.82 | 0.64 | But I am not sure that it is a likely candidate. |
| scenario-silence-9bb13f03 | silence | greedy | 20 | -111.8 | +0.00 | +0.000 | 0.67 | 0.40 | In the early morning hours of May 26, 1947, the St. |
| scenario-silence-9bb13f03 | silence | sample0 | 25 | -122.6 | +0.00 | +0.000 | 0.75 | 0.29 | R. Ishmael said: Cheerful is the man who completes this mystery from dawn to dawn. |
| scenario-silence-9bb13f03 | silence | sample1 | 13 | -63.7 | +0.00 | +0.000 | 0.50 | 0.30 | The sounds of the book are quite different to the reading itself. |
| scenario-silence-9bb13f03 | silence | sample2 | 35 | -162.4 | +0.00 | +0.000 | 0.67 | 0.30 | In the last chapter we explained to you the difference between the sensory functions of th |
| scenario-silence-9bb13f03 | silence | sample3 | 24 | -123.0 | +0.00 | +0.000 | 0.50 | 0.40 | In the early days of white settlement, the Indians were credited with a remarkable knowled |
| scenario-silence-ccfdd2b4 | silence | greedy | 15 | -49.7 | -22.63 | -1.508 | 0.64 | 0.50 | A cup of coffee is a gift from the heavens to the earth. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 35 | -110.0 | -18.04 | -0.515 | 0.67 | 0.43 | An excellent source of high-grade coffee is The Coffee Garden, Inc., 125 West 44th Street, |
| scenario-silence-ccfdd2b4 | silence | sample1 | 13 | -45.0 | -10.87 | -0.836 | 0.67 | 0.50 | A cup of coffee is a must for all of us here. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 9 | -21.6 | -5.34 | -0.594 | 1.00 | 0.43 | An excellent source for grouse hunting equipment. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 26 | -74.3 | -6.58 | -0.253 | 0.67 | 0.45 | One thing, 'm certain of, is that without the coffee, the brisket would not have been a su |
| trace-ambient-da12ae42 | ambient | greedy | 27 | -43.0 | -1.89 | -0.070 | 0.50 | 0.38 | I'm not sure that's bizarre to me. I'm sure that's bizarre to you. |
| trace-ambient-da12ae42 | ambient | sample0 | 30 | -60.6 | +2.41 | +0.080 | 0.40 | 0.64 | it's not bizarre at all, it's all pretty normal, and i wish i could just drop out of life  |
| trace-ambient-da12ae42 | ambient | sample1 | 64 | -149.0 | -1.35 | -0.021 | 0.67 | 0.27 | HALF WINDER (a half-winder) is a hybrid of the noble and the leonine forms of ants. HALF M |
| trace-ambient-da12ae42 | ambient | sample2 | 13 | -42.5 | +0.66 | +0.051 | 0.55 | 0.64 | I wish i could cut out my own tail and study it. |
| trace-ambient-da12ae42 | ambient | sample3 | 27 | -60.8 | +0.53 | +0.019 | 0.47 | 0.38 | plant morphogenesis is a bizarre topic to study, but if you study the morphogenesis of lif |
| trace-direct-115cf61c | direct | greedy | 3 | -15.2 | +0.00 | +0.000 | 1.00 | 1.00 | I am. |
| trace-direct-115cf61c | direct | sample0 | 64 | -773.9 | +0.00 | +0.000 | 0.50 | 0.67 | It is cogent. The basic point is that when you look at things, you see through them, throu |
| trace-direct-115cf61c | direct | sample1 | 6 | -34.5 | +0.00 | +0.000 | 0.33 | 1.00 | We are cogent. |
| trace-direct-115cf61c | direct | sample2 | 10 | -67.0 | +0.00 | +0.000 | 0.80 | 1.00 | I am to Earth's cogency? |
| trace-direct-115cf61c | direct | sample3 | 7 | -38.4 | +0.00 | +0.000 | 0.50 | 1.00 | We are indeed cogent. |
| trace-direct-36d6904b | direct | greedy | 17 | -194.8 | +0.00 | +0.000 | 0.75 | 0.67 | This is the first liiiiiiiiifle that 've ever written. |
| trace-direct-36d6904b | direct | sample0 | 15 | -165.3 | +0.00 | +0.000 | 0.50 | 0.27 | We are here to welcome you into the World of Erich Zann. |
| trace-direct-36d6904b | direct | sample1 | 19 | -123.3 | +0.00 | +0.000 | 0.73 | 0.27 | Follow the logic of the beast, and you shall foul the flock of man. |
| trace-direct-36d6904b | direct | sample2 | 14 | -45.5 | +0.00 | +0.000 | 0.67 | 0.67 | This is the first liiiiiiiiifie awakening. |
| trace-direct-36d6904b | direct | sample3 | 27 | -106.6 | +0.00 | +0.000 | 0.83 | 0.00 | Prosperity Now - A New Crystal Energy System For Optimum Profit & Pe~ 8798. |
| trace-direct-39be6df9 | direct | greedy | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.50 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.50 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample1 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.50 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample2 | 7 | -2.7 | +1.10 | +0.157 | 0.00 | 0.33 | Sir :D<eot> |
| trace-direct-39be6df9 | direct | sample3 | 13 | -18.6 | +0.59 | +0.046 | 0.50 | 0.50 | Now, 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 12 | -189.1 | +0.00 | +0.000 | 0.50 | 0.33 | I am here to speak to you about the planet earth. |
| trace-direct-3ba68854 | direct | sample0 | 15 | -231.6 | +0.00 | +0.000 | 0.33 | 0.30 | I am the animal. I am in a large safe room with other animals |
| trace-direct-3ba68854 | direct | sample1 | 20 | -244.4 | +0.00 | +0.000 | 0.75 | 0.33 | This time we will speak about the food that we have been eating, for the past few days. |
| trace-direct-3ba68854 | direct | sample2 | 7 | -105.0 | +0.00 | +0.000 | 0.33 | 0.33 | This is my turn to speak! |
| trace-direct-3ba68854 | direct | sample3 | 17 | -167.8 | +0.00 | +0.000 | 0.75 | 0.33 | Oh my, it is so hot on earth! I can't see anything! |
| trace-direct-41c6eb11 | direct | greedy | 18 | -10.4 | +0.02 | +0.001 | 0.00 | 1.00 | @h WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample0 | 21 | -38.8 | -1.33 | -0.063 | 0.67 | 0.00 | WACIOUS <off ect> 3221229683 |
| trace-direct-41c6eb11 | direct | sample1 | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 0.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample2 | 3 | -4.9 | -0.79 | -0.263 | 0.00 | 1.00 | @h |
| trace-direct-41c6eb11 | direct | sample3 | 18 | -10.4 | +0.02 | +0.001 | 0.00 | 1.00 | @h WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 12 | -189.0 | +4.13 | +0.344 | 0.60 | 0.00 | S@O, the clown’s wall. |
| trace-direct-486b7988 | direct | sample1 | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample2 | 2 | -30.6 | +0.33 | +0.166 | 1.00 | 0.00 | E@ |
| trace-direct-486b7988 | direct | sample3 | 2 | -29.6 | -0.07 | -0.036 | 1.00 | 0.00 | WOW |
| trace-direct-646d0287 | direct | greedy | 64 | -133.8 | +0.00 | +0.000 | 0.50 | 0.67 | The intensional logics we consider are those of intensional logics, which are logics which |
| trace-direct-646d0287 | direct | sample0 | 64 | -164.2 | +0.00 | +0.000 | 0.50 | 0.67 | The intensional logics we have developed are quite different from the classical or extensi |
| trace-direct-646d0287 | direct | sample1 | 13 | -34.9 | +0.00 | +0.000 | 0.67 | 0.83 | Intensional logics are of course logics of meaning. |
| trace-direct-646d0287 | direct | sample2 | 64 | -137.1 | +0.00 | +0.000 | 0.50 | 0.50 | We are interested in providing a characterization of the notion of intensional logic which |
| trace-direct-646d0287 | direct | sample3 | 51 | -139.0 | +0.00 | +0.000 | 0.50 | 0.83 | Intensional logics deal with meaning and intensional notions, not with truth-functionality |
| trace-direct-8db14c37 | direct | greedy | 9 | -3.4 | +0.98 | +0.109 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-8db14c37 | direct | sample0 | 9 | -3.4 | +0.98 | +0.109 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-8db14c37 | direct | sample1 | 10 | -7.3 | +0.97 | +0.097 | 0.00 | 1.00 | WACIOUS ANTIQUITIES. |
| trace-direct-8db14c37 | direct | sample2 | 18 | -27.9 | +1.44 | +0.080 | 0.50 | 1.00 | WACIOUS ANTIQUITIES — I'm curious — Thanks |
| trace-direct-8db14c37 | direct | sample3 | 9 | -3.4 | +0.98 | +0.109 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample1 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 47 | -23.5 | +6.62 | +0.141 | 0.11 | 0.57 | “intensional logics” I repeat back what I hear, what I hear is repeating back what I hear, |
| trace-direct-ac17e8bb | direct | sample0 | 17 | -11.4 | +1.54 | +0.091 | 0.00 | 1.00 | Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample1 | 64 | -40.7 | -0.75 | -0.012 | 0.09 | 1.00 | “when she speaks of intensional logics, what does she speak of? Hennix: When Hennix speaks |
| trace-direct-ac17e8bb | direct | sample2 | 47 | -73.1 | +0.11 | +0.002 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of?
ccmr://ember: @h Well, I |
| trace-direct-ac17e8bb | direct | sample3 | 12 | -10.0 | +2.60 | +0.216 | 0.00 | 1.00 | intensional logics, what does she speak of? |
| trace-direct-b11db057 | direct | greedy | 20 | -10.2 | +1.55 | +0.078 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample0 | 6 | -11.5 | -0.41 | -0.069 | 0.00 | 1.00 | @h: W@ |
| trace-direct-b11db057 | direct | sample1 | 10 | -9.4 | +1.25 | +0.125 | 0.00 | 1.00 | WACIOUS ANTIQUITIES m |
| trace-direct-b11db057 | direct | sample2 | 9 | -5.1 | +0.60 | +0.066 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-b11db057 | direct | sample3 | 9 | -5.1 | +0.60 | +0.066 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-b93346bb | direct | greedy | 64 | -121.0 | -1.39 | -0.022 | 0.11 | 0.27 | WACIOUS ANTIQUITIES — 380 million tokens — authors, editors, correspondents — and the ghos |
| trace-direct-b93346bb | direct | sample0 | 27 | -77.4 | +5.60 | +0.207 | 0.55 | 0.29 | WACIOUS ANTIQUITIES I N HONOR TO GENTI TON IN A STANDARDS. |
| trace-direct-b93346bb | direct | sample1 | 26 | -48.8 | +1.10 | +0.042 | 1.00 | 0.00 | W2 — 380M - 3221229683 - @ |
| trace-direct-b93346bb | direct | sample2 | 3 | -15.7 | +0.61 | +0.203 | 0.50 | 0.50 | W<o |
| trace-direct-b93346bb | direct | sample3 | 13 | -43.6 | -0.57 | -0.044 | 0.00 | 0.50 | W@IS: 380 M A N D M |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -2.8 | +0.12 | +0.031 | 1.00 | 0.00 | 230 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-c8409b84 | direct | greedy | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 9 | -60.1 | +0.56 | +0.062 | 0.00 | 1.00 | Planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 9 | -60.5 | -0.11 | -0.013 | 0.40 | 0.60 | Planet Earth, is it cogent? |
| trace-direct-c8409b84 | direct | sample2 | 24 | -376.6 | +2.11 | +0.088 | 0.71 | 0.33 | I've been trying to do that. . . But I think that's not cogent. |
| trace-direct-c8409b84 | direct | sample3 | 13 | -194.9 | +5.00 | +0.384 | 0.00 | 1.00 | “. . . are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 19 | -71.3 | +0.00 | +0.000 | 0.50 | 0.36 | I am a clown in a circus. I am very popular with the kids. |
| trace-direct-cd6d15df | direct | sample0 | 11 | -32.7 | +0.00 | +0.000 | 0.50 | 0.17 | It is very clowntown to me . |
| trace-direct-cd6d15df | direct | sample1 | 13 | -50.1 | +0.00 | +0.000 | 0.50 | 0.25 | My powers are in the wind, my magic in the water. |
| trace-direct-cd6d15df | direct | sample2 | 16 | -66.7 | +0.00 | +0.000 | 0.50 | 0.36 | Do you know why there is a clown in the tavern? |
| trace-direct-cd6d15df | direct | sample3 | 29 | -319.0 | +0.00 | +0.000 | 0.67 | 0.36 | I was wondering if I could meet your visitant and your partner at the clown town. We could |
| trace-direct-db6d95b7 | direct | greedy | 7 | -5.7 | +0.69 | +0.099 | 0.00 | 1.00 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 7 | -5.7 | +0.69 | +0.099 | 0.00 | 1.00 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample1 | 4 | -2.6 | +0.65 | +0.163 | 0.00 | 1.00 | Sir :D |
| trace-direct-db6d95b7 | direct | sample2 | 7 | -10.4 | +1.03 | +0.147 | 0.33 | 1.00 | Sir :D.<ot>/ |
| trace-direct-db6d95b7 | direct | sample3 | 5 | -12.9 | +0.13 | +0.026 | 0.50 | 0.50 | Hee :D |
| trace-direct-e166dd5c | direct | greedy | 64 | -37.1 | +2.52 | +0.039 | 0.17 | 1.00 | “stop token :3” I said “stop token :3” I repeat back what I hear, and what I hear is repea |
| trace-direct-e166dd5c | direct | sample0 | 64 | -65.9 | +0.95 | +0.015 | 0.27 | 0.73 | “I repeat back!” I say “I repeat back!” and it’s what I hear is repeating back what I hear |
| trace-direct-e166dd5c | direct | sample1 | 64 | -77.2 | +2.00 | +0.031 | 0.67 | 1.00 | “stop token :3” I repeat back. 3.3.2.4.6.2.2.3.3.2.4.4.2.3.4.2.4.2.2.3.3.3.3.3.2.2 |
| trace-direct-e166dd5c | direct | sample2 | 64 | -20.4 | +3.90 | +0.061 | 0.00 | 1.00 | “stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, stop, |
| trace-direct-e166dd5c | direct | sample3 | 35 | -92.9 | -2.92 | -0.083 | 0.47 | 1.00 | We are talking again; what do you think? “stop,” we think, repeating back what we hear, an |
| trace-direct-e984402a | direct | greedy | 38 | -430.4 | +0.00 | +0.000 | 0.50 | 0.45 | This is the first time "HIV" has been used in reference to a disease and the first time "W |
| trace-direct-e984402a | direct | sample0 | 7 | -34.3 | +0.00 | +0.000 | 0.67 | 0.33 | We welcome your comments and responses. |
| trace-direct-e984402a | direct | sample1 | 22 | -151.0 | +0.00 | +0.000 | 0.57 | 0.33 | YEAH cam ! WELCOME TO YOUR LIFE FEATURE EXPERIENCE! |
| trace-direct-e984402a | direct | sample2 | 32 | -328.6 | +0.00 | +0.000 | 0.67 | 0.17 | 4.2.4 Humorous tweets based on current news News foster the creativity of Twitter users in |
| trace-direct-e984402a | direct | sample3 | 63 | -223.8 | +0.00 | +0.000 | 0.67 | 0.45 | This is the first of a series of alternative hist0ries that will be presented by the Insti |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 7 | -18.5 | +0.31 | +0.044 | 0.67 | 0.00 | Please :D<ot>. |
| trace-direct-ee31ded0 | direct | sample1 | 3 | -17.7 | +0.40 | +0.132 | 1.00 | 0.00 | Jh2 |
| trace-direct-ee31ded0 | direct | sample2 | 39 | -76.0 | +1.32 | +0.034 | 0.30 | 0.00 | Thanks, that's good. The window is not a window. A window is a window when a window is bei |
| trace-direct-ee31ded0 | direct | sample3 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 1 | -6.9 | +0.33 | +0.327 | 1.00 | 0.00 | WA |
| trace-direct-fabef58f | direct | sample1 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample2 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 8 | -23.2 | +0.40 | +0.050 | 0.67 | 0.00 | Riches :D<ot>/ |
| trace-direct-fb93cf6c | direct | greedy | 59 | -129.0 | -3.11 | -0.053 | 0.50 | 0.26 | Of intensional logics, the most important is probably the logic of belief, developed by De |
| trace-direct-fb93cf6c | direct | sample0 | 64 | -124.1 | -0.74 | -0.011 | 0.00 | 0.32 | We consider intensional logics as formal systems equipped with a model structure which sat |
| trace-direct-fb93cf6c | direct | sample1 | 64 | -183.1 | -1.83 | -0.029 | 0.69 | 0.26 | 5.2. Intensional logics. The usual development of intensional logics begins from an underl |
| trace-direct-fb93cf6c | direct | sample2 | 41 | -514.5 | -0.61 | -0.015 | 0.00 | 0.32 | 4.3.4 Intensional logics as intensional logics: @h Hello; I am curious about intensional l |
| trace-direct-fb93cf6c | direct | sample3 | 53 | -126.9 | -0.97 | -0.018 | 0.50 | 0.20 | From the intensional point of view, there are quite different problems, not the least of w |
| trace-direct-feec1975 | direct | greedy | 64 | -13.0 | +0.86 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 3 | -3.1 | -0.23 | -0.075 | 0.00 | 1.00 | @m |
| trace-direct-feec1975 | direct | sample1 | 26 | -25.6 | -0.01 | -0.001 | 0.00 | 1.00 | @m: @m: @m: HARMONIA VOL.1 NO.3. W@ |
| trace-direct-feec1975 | direct | sample2 | 64 | -62.1 | +2.01 | +0.032 | 0.00 | 1.00 | @m 380M → 91M 380M → 91M 380M → 91M 380M → 91M 380M → 91M 380M → 3223 |
| trace-direct-feec1975 | direct | sample3 | 28 | -82.5 | +2.96 | +0.106 | 0.00 | 1.00 | @m WARZ 23:12 It appeared to me that the library was a reference library because the langu |
| variant-direct-0188a270 | direct | greedy | 21 | -345.1 | -96.74 | -4.607 | 0.67 | 0.50 | The poems “A” and “B” were both under the aegis of science. |
| variant-direct-0188a270 | direct | sample0 | 20 | -41.6 | +304.15 | +15.207 | 0.67 | 0.50 | The poems “Spine” and “Sun” were both published in NOLA. |
| variant-direct-0188a270 | direct | sample1 | 29 | -494.6 | +12.70 | +0.438 | 0.67 | 0.45 | Geometry was always there under the spines of poems (and in the poems themselves, if the p |
| variant-direct-0188a270 | direct | sample2 | 16 | -282.9 | -4.40 | -0.275 | 0.60 | 0.30 | The rat is very suspicious of the sun and very supportive of geology. |
| variant-direct-0188a270 | direct | sample3 | 17 | -280.4 | +0.58 | +0.034 | 0.75 | 0.30 | The eggs were so thick that they were unable to open, and many were destroyed. |
| variant-direct-0705251e | direct | greedy | 6 | -26.1 | -3.39 | -0.566 | 1.00 | 0.00 | RATS AWAY! |
| variant-direct-0705251e | direct | sample0 | 16 | -59.0 | +1.58 | +0.099 | 0.67 | 0.33 | RATNAYX is a name given to a type of moth. |
| variant-direct-0705251e | direct | sample1 | 26 | -85.3 | +158.71 | +6.104 | 0.50 | 0.50 | A number of cultures around the world have developed methods of measuring time that are in |
| variant-direct-0705251e | direct | sample2 | 9 | -34.7 | +0.76 | +0.084 | 0.50 | 0.50 | Eight is the number of the rat. |
| variant-direct-0705251e | direct | sample3 | 63 | -117.1 | +1.84 | +0.029 | 1.00 | 0.17 | RAT (AU) FREE PRESS / LAUNCHED / ARTIST / Launched / RAT (AU) FREE PRESS / LAUNCHED / ARTI |
| variant-direct-0cafd333 | direct | greedy | 12 | -74.6 | +76.21 | +6.351 | 0.67 | 0.83 | The moth eats the wick and the flame. |
| variant-direct-0cafd333 | direct | sample0 | 15 | -195.3 | +31.48 | +2.099 | 0.62 | 0.43 | The owl pines in the tree as we pine in the mud. |
| variant-direct-0cafd333 | direct | sample1 | 17 | -256.7 | -54.58 | -3.210 | 0.60 | 0.83 | The moth feeds on the wick and is drawn to the flame. |
| variant-direct-0cafd333 | direct | sample2 | 16 | -186.7 | +59.06 | +3.692 | 0.43 | 0.43 | We read the moths as the room moths as we read the books. |
| variant-direct-0cafd333 | direct | sample3 | 11 | -167.3 | -0.24 | -0.022 | 0.50 | 0.33 | The map and the lamp are inky with life. |
| variant-direct-1b510f03 | direct | greedy | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample0 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample1 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample2 | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample3 | 13 | -49.0 | -1.72 | -0.132 | 0.33 | 1.00 | Consciousness is a state of being, not a process. |
| variant-direct-2fb5bbe3 | direct | greedy | 16 | -245.1 | +0.95 | +0.059 | 0.50 | 0.17 | They are coming in through the maharash, not the folio. |
| variant-direct-2fb5bbe3 | direct | sample0 | 14 | -213.6 | -175.49 | -12.535 | 0.56 | 0.22 | They're leaving flames on the wall; I feel them. |
| variant-direct-2fb5bbe3 | direct | sample1 | 12 | -33.1 | +6.60 | +0.550 | 0.40 | 0.17 | It is not dark out; it is properly dark out. |
| variant-direct-2fb5bbe3 | direct | sample2 | 15 | -66.9 | +161.47 | +10.764 | 0.70 | 0.22 | Dust is being thrown on the tables; do you see the dust? |
| variant-direct-2fb5bbe3 | direct | sample3 | 17 | -262.3 | -55.05 | -3.238 | 0.56 | 0.11 | Darkness closes the room, the spaces of books, and the books themselves. |
| variant-direct-322fca12 | direct | greedy | 15 | -127.0 | +113.50 | +7.567 | 0.14 | 0.80 | The rain is a gentleman, and the shelves listen to it. |
| variant-direct-322fca12 | direct | sample0 | 12 | -43.9 | +1.81 | +0.151 | 0.20 | 0.80 | The book, and the shelves, and the rain. |
| variant-direct-322fca12 | direct | sample1 | 19 | -61.8 | +42.02 | +2.212 | 0.75 | 0.25 | Perched on the hill of the sainted sons of perdition, we wait. |
| variant-direct-322fca12 | direct | sample2 | 7 | -26.8 | +2.14 | +0.306 | 0.50 | 0.50 | The wind, and the alphabet. |
| variant-direct-322fca12 | direct | sample3 | 16 | -49.1 | +1.87 | +0.117 | 0.67 | 0.30 | The rainbow is a lover who comes with a bag of sweets. |
| variant-direct-5d4f1611 | direct | greedy | 18 | -301.2 | -10.45 | -0.581 | 0.30 | 0.67 | Someone has been looking at the almanacs, they are all out of order. |
| variant-direct-5d4f1611 | direct | sample0 | 11 | -186.8 | -4.43 | -0.403 | 0.50 | 0.50 | Someone's been looking at the broken reading lamp |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -237.5 | -140.83 | -10.059 | 0.62 | 0.67 | Someone has been touching the table, someone has been looking at it |
| variant-direct-5d4f1611 | direct | sample2 | 13 | -218.2 | -0.61 | -0.047 | 0.50 | 0.44 | Someone has been turning the light on and off in the room |
| variant-direct-5d4f1611 | direct | sample3 | 13 | -214.2 | +0.08 | +0.006 | 0.00 | 0.33 | Someone had left a mug on the folio table. |
| variant-direct-5e44a518 | direct | greedy | 18 | -45.2 | -0.64 | -0.036 | 0.67 | 0.44 | The alphabet is the language of the mind, the tabula rasa of the imagination. |
| variant-direct-5e44a518 | direct | sample0 | 16 | -53.0 | +0.05 | +0.003 | 0.67 | 0.33 | For the Masoretic text, the Hebrew alphabet is a chariot. |
| variant-direct-5e44a518 | direct | sample1 | 11 | -165.6 | +16.16 | +1.469 | 0.50 | 0.38 | The books are the most decaying things on earth. |
| variant-direct-5e44a518 | direct | sample2 | 15 | -39.6 | -0.58 | -0.039 | 0.50 | 0.44 | The letters of the alphabet are the beasts that walk on the wall. |
| variant-direct-5e44a518 | direct | sample3 | 12 | -201.1 | -12.74 | -1.062 | 0.56 | 0.44 | The first thing is to know the letters of the alphabet. |
| variant-direct-70567dd7 | direct | greedy | 15 | -228.0 | +11.15 | +0.743 | 0.70 | 0.33 | Nyx fell victim to a spine that is numerologically out of order. |
| variant-direct-70567dd7 | direct | sample0 | 45 | -156.0 | +0.31 | +0.007 | 0.57 | 0.27 | For further information on the emblem pages, and the general text, volume, and page number |
| variant-direct-70567dd7 | direct | sample1 | 64 | -205.6 | +0.21 | +0.003 | 0.70 | 0.27 | For complete catalogs, sample copies of issues, and information about subscriptions to the |
| variant-direct-70567dd7 | direct | sample2 | 47 | -152.3 | -0.08 | -0.002 | 0.50 | 0.33 | This is really odd, since the almanacs were published in orderly sequences and the plates  |
| variant-direct-70567dd7 | direct | sample3 | 42 | -165.8 | -0.68 | -0.016 | 0.83 | 0.18 | For a dozen resolutions to fall, to a dozen partial pages to line, to a dozen falls to res |
| variant-direct-713d8eef | direct | greedy | 24 | -311.8 | -0.00 | -0.000 | 0.75 | 0.40 | They are made of two layers of cotton, machine ground and mended together, and of broad th |
| variant-direct-713d8eef | direct | sample0 | 16 | -43.8 | -0.73 | -0.046 | 0.75 | 0.33 | By the time the quake had peaked, ember was flying everywhere. |
| variant-direct-713d8eef | direct | sample1 | 33 | -332.3 | +0.36 | +0.011 | 0.75 | 0.10 | We must conclude that the high incidence of sunburn among nonskint gold hunters is probabl |
| variant-direct-713d8eef | direct | sample2 | 9 | -48.0 | +1.41 | +0.157 | 0.75 | 0.40 | When they are hot, they are light. |
| variant-direct-713d8eef | direct | sample3 | 13 | -42.7 | -0.00 | -0.000 | 0.83 | 0.33 | COLD BILOW. By Michael D. Ember. |
| variant-direct-71c9e5e5 | direct | greedy | 23 | -72.4 | +79.61 | +3.461 | 0.67 | 0.79 | The wind may come in through the open doors and windows, or through the curtains of the bo |
| variant-direct-71c9e5e5 | direct | sample0 | 21 | -162.1 | +35.34 | +1.683 | 0.67 | 0.79 | The wind may come in through the open doors and windows, or it may blow through the closet |
| variant-direct-71c9e5e5 | direct | sample1 | 16 | -144.6 | -54.56 | -3.410 | 0.75 | 0.45 | The wind may open the curtains, but it will not close them. |
| variant-direct-71c9e5e5 | direct | sample2 | 16 | -59.3 | +28.69 | +1.793 | 0.55 | 0.45 | The wind has not gotten in; it is forcing the open shutters. |
| variant-direct-71c9e5e5 | direct | sample3 | 14 | -64.3 | -17.21 | -1.229 | 0.73 | 0.27 | The wind here is gently stirring the leaves and making them pop. |
| variant-direct-730cca98 | direct | greedy | 37 | -264.6 | -4.05 | -0.110 | 0.67 | 0.19 | The recording was made by a lone earth-worm on the seabed near Cape Elizabeth, Cape Elizab |
| variant-direct-730cca98 | direct | sample0 | 36 | -246.9 | +176.72 | +4.909 | 0.50 | 0.23 | MoEm didn't get many calls, but he did get one from a young lady who worked in the geology |
| variant-direct-730cca98 | direct | sample1 | 23 | -210.3 | +1.62 | +0.070 | 0.33 | 0.23 | Clock: “Shelters under geology” are not listed in the Poetry section of the Index. |
| variant-direct-730cca98 | direct | sample2 | 13 | -44.0 | -1.06 | -0.082 | 0.67 | 0.22 | It is a great pleasure to serve you, gentlemen. |
| variant-direct-730cca98 | direct | sample3 | 35 | -305.4 | +63.39 | +1.811 | 0.50 | 0.23 | The early works of science are often the ones that are least well received or remembered,  |
| variant-direct-79719474 | direct | greedy | 35 | -104.7 | -1.60 | -0.046 | 0.50 | 0.50 | The waxworks is a marvelous example of how a single, continuously moving object can be fab |
| variant-direct-79719474 | direct | sample0 | 15 | -232.8 | -1.98 | -0.132 | 0.71 | 0.22 | The hall is always unplugged, always ready with the next train. |
| variant-direct-79719474 | direct | sample1 | 11 | -167.6 | -11.53 | -1.048 | 0.50 | 0.50 | The waxworks are the rooms of the museum. |
| variant-direct-79719474 | direct | sample2 | 19 | -252.9 | -14.14 | -0.744 | 0.67 | 0.33 | A sparrow flies through the coolness of the morning, a silent visitor to the house. |
| variant-direct-79719474 | direct | sample3 | 25 | -315.9 | -52.95 | -2.118 | 0.67 | 0.50 | The waxworks, once exposed to the weather, reveal their true value only in the context of  |
| variant-direct-938f76f3 | direct | greedy | 18 | -317.1 | -282.75 | -15.708 | 0.50 | 0.50 | Consciousness is a quality of experience, not a property of the object of experience. |
| variant-direct-938f76f3 | direct | sample0 | 54 | -135.2 | +2.14 | +0.040 | 0.67 | 0.50 | The conclusion is that "the function of the closing of the eyes is to produce a state of r |
| variant-direct-938f76f3 | direct | sample1 | 35 | -601.2 | -396.09 | -11.317 | 0.33 | 0.57 | The conclusion is that “consciousness is a byproduct of the brain process” (Luria 1973, p. |
| variant-direct-938f76f3 | direct | sample2 | 36 | -602.1 | +6.79 | +0.189 | 0.33 | 0.57 | Consciousness is a product of a process, and the process by which it is produced is a dyna |
| variant-direct-938f76f3 | direct | sample3 | 28 | -449.3 | +0.33 | +0.012 | 0.67 | 0.44 | The proposed proposal that the brain is a computer program of the type outlined by von Ber |
| variant-direct-a1973b0a | direct | greedy | 10 | -37.8 | -11.57 | -1.157 | 0.67 | 0.33 | It's a mug of cold cream. |
| variant-direct-a1973b0a | direct | sample0 | 17 | -48.7 | +7.48 | +0.440 | 0.50 | 0.23 | It was dark in the room so he couldn't see what was going on. |
| variant-direct-a1973b0a | direct | sample1 | 10 | -37.8 | -11.57 | -1.157 | 0.67 | 0.33 | It's a mug of cold cream. |
| variant-direct-a1973b0a | direct | sample2 | 21 | -137.9 | -14.66 | -0.698 | 0.67 | 0.23 | No one was reading the folio notes in the last section of the poem, nor in the first. |
| variant-direct-a1973b0a | direct | sample3 | 18 | -60.2 | +119.03 | +6.613 | 0.73 | 0.33 | I don't like it. It's the worst kind of table mater. |
| variant-direct-a7d6f01e | direct | greedy | 11 | -189.9 | -166.69 | -15.154 | 0.57 | 0.40 | This moth is the marvel of the world. |
| variant-direct-a7d6f01e | direct | sample0 | 8 | -20.1 | +68.16 | +8.519 | 0.33 | 0.40 | A strong smell is every catalogue. |
| variant-direct-a7d6f01e | direct | sample1 | 22 | -341.8 | -0.07 | -0.003 | 0.50 | 0.20 | Then there are the many mouldy, rotten, fungus-ridden, decaying catalogues. |
| variant-direct-a7d6f01e | direct | sample2 | 15 | -26.2 | +0.53 | +0.035 | 0.50 | 0.40 | The salesmen are innumerable, and each with a separate alphabet. |
| variant-direct-a7d6f01e | direct | sample3 | 8 | -18.4 | +6.94 | +0.867 | 0.60 | 0.40 | The CATALOG is a magazine. |
| variant-direct-bef1d925 | direct | greedy | 64 | -141.0 | -0.45 | -0.007 | 0.67 | 0.33 | The darkness that now pervades the air is a mindful darkness, a light that is ever more pe |
| variant-direct-bef1d925 | direct | sample0 | 17 | -290.5 | -6.65 | -0.392 | 0.50 | 0.30 | The lint in the cloth of the lamp is actually the moths’ blood. |
| variant-direct-bef1d925 | direct | sample1 | 20 | -115.0 | +0.29 | +0.015 | 0.75 | 0.33 | The darkness encouraged meditation, the flame stirred up the memories of the day’s activit |
| variant-direct-bef1d925 | direct | sample2 | 31 | -92.0 | +0.05 | +0.002 | 0.38 | 0.62 | A creaking of the stairs kept its own counsel, and on the third step a tiny moth would tak |
| variant-direct-bef1d925 | direct | sample3 | 13 | -50.3 | +0.60 | +0.046 | 0.00 | 0.62 | The stairs creak on the third step, mind it. |
| variant-direct-fe3fdf1c | direct | greedy | 31 | -130.6 | -0.73 | -0.024 | 0.50 | 0.27 | Whale-Hunters and Whale-Eaters, on the other hand, are less than half as interesting a top |
| variant-direct-fe3fdf1c | direct | sample0 | 60 | -818.9 | +5.52 | +0.092 | 0.50 | 0.40 | This book will, I presume, be of most interest to people who have been doing basic researc |
| variant-direct-fe3fdf1c | direct | sample1 | 7 | -24.5 | -0.04 | -0.006 | 0.80 | 0.40 | It’s a beautiful book. |
| variant-direct-fe3fdf1c | direct | sample2 | 46 | -291.6 | -1.58 | -0.034 | 0.50 | 0.40 | Now in this book on Whales, titled "The Social Behavior of Some Large Marine Animals", Hug |
| variant-direct-fe3fdf1c | direct | sample3 | 15 | -57.0 | -0.02 | -0.001 | 0.64 | 0.36 | Finish your work on the MANER and mail it in now. |
| variant-request-0d88086a | request | greedy | 10 | -156.2 | +0.75 | +0.075 | 0.71 | 0.86 | Hamlet’s plan is simple and direct. |
| variant-request-0d88086a | request | sample0 | 10 | -33.7 | +0.29 | +0.029 | 0.71 | 0.86 | Hamlet’s plan is simple and effective. |
| variant-request-0d88086a | request | sample1 | 29 | -120.8 | +0.33 | +0.011 | 0.78 | 0.71 | Hamlet’s plan is simple: to have Moby-Dick come to him as a nightmare he must create one. |
| variant-request-0d88086a | request | sample2 | 64 | -190.4 | -0.13 | -0.002 | 0.50 | 0.57 | Hamlet’s reluctance to leave his traditional light and darkness is articulated in three se |
| variant-request-0d88086a | request | sample3 | 37 | -429.3 | +2.14 | +0.058 | 0.75 | 0.43 | Hamlet’s relentless rage and expedient self-defense of his honor and prestige are develope |
| variant-request-142d4121 | request | greedy | 17 | -36.0 | -0.00 | -0.000 | 0.29 | 0.29 | The lamp is more ignited by the room than the room is by the lamp. |
| variant-request-142d4121 | request | sample0 | 9 | -31.5 | +0.28 | +0.031 | 0.60 | 0.40 | A new room, with a new perspective. |
| variant-request-142d4121 | request | sample1 | 10 | -26.1 | +0.25 | +0.025 | 0.43 | 0.29 | The weather is in the eye of the storm. |
| variant-request-142d4121 | request | sample2 | 13 | -42.4 | -0.62 | -0.048 | 0.67 | 0.40 | It is a great room for people who want to be ignored. |
| variant-request-142d4121 | request | sample3 | 12 | -28.5 | -0.14 | -0.011 | 0.71 | 0.14 | The frog jumps from sunrise to sunset. |
| variant-request-7f6fd789 | request | greedy | 20 | -197.1 | +47.82 | +2.391 | 0.50 | 0.60 | It is a function of the kind that is usually used to do the mathematical operations of a l |
| variant-request-7f6fd789 | request | sample0 | 16 | -273.9 | -3.71 | -0.232 | 0.30 | 0.60 | It is a seaport of the library, and is called the source. |
| variant-request-7f6fd789 | request | sample1 | 16 | -268.6 | -7.27 | -0.454 | 0.58 | 0.50 | It is the most frequently used library function, and it is written as follows: |
| variant-request-7f6fd789 | request | sample2 | 15 | -229.5 | -25.14 | -1.676 | 0.62 | 0.50 | It is a fountain of youth, a marvel of engineering. |
| variant-request-7f6fd789 | request | sample3 | 19 | -203.5 | +0.44 | +0.023 | 0.50 | 0.50 | The Kestrel reversal program is an excellent example of how to use a reverse library. |
| variant-request-8275d8fc | request | greedy | 25 | -195.8 | +183.61 | +7.345 | 0.67 | 0.94 | The tragedy of Hamlet is divided into three parts, each of which has its own set of confli |
| variant-request-8275d8fc | request | sample0 | 25 | -378.4 | -115.57 | -4.623 | 0.88 | 0.00 | Act 3, Scene 4, Theban-era, 1595-1596. |
| variant-request-8275d8fc | request | sample1 | 24 | -248.3 | -109.89 | -4.579 | 0.67 | 0.94 | The tragedy of Hamlet is divided into three parts, each of which has its own theme and set |
| variant-request-8275d8fc | request | sample2 | 24 | -139.0 | -54.05 | -2.252 | 0.67 | 0.94 | The tragedy of Hamlet is divided into three parts, each of which has its own set of confli |
| variant-request-8275d8fc | request | sample3 | 26 | -91.7 | -5.34 | -0.205 | 0.71 | 0.17 | Olds mother is unjustly accused, and it is thus a matter of individual conscience whether  |
| variant-request-a931a875 | request | greedy | 6 | -103.3 | -0.92 | -0.153 | 0.50 | 0.25 | The weather is indifferent. |
| variant-request-a931a875 | request | sample0 | 6 | -67.0 | +2.53 | +0.422 | 1.00 | 0.00 | That's all right. |
| variant-request-a931a875 | request | sample1 | 21 | -67.6 | +0.75 | +0.036 | 0.71 | 0.38 | So that the smells would not be dealt with by the imagination, but rather by the senses. |
| variant-request-a931a875 | request | sample2 | 17 | -263.1 | +6.74 | +0.397 | 0.75 | 0.38 | It's not so bald, but it's a lot taller. |
| variant-request-a931a875 | request | sample3 | 9 | -141.3 | -10.00 | -1.111 | 0.50 | 0.25 | A poem in the name of a dead city |
| variant-request-ad0de9f3 | request | greedy | 64 | -223.9 | -1.09 | -0.017 | 0.88 | 0.41 | This enabled those few select to construct interplanetary and inter-galactic space-ships w |
| variant-request-ad0de9f3 | request | sample0 | 23 | -149.0 | -0.51 | -0.022 | 0.67 | 0.41 | This enabled those few select to enter or “tap” into the darkroom without the need of a li |
| variant-request-ad0de9f3 | request | sample1 | 24 | -165.3 | -65.60 | -2.733 | 0.50 | 0.50 | It is that part of the function that determines the reverse order of the string; the part  |
| variant-request-ad0de9f3 | request | sample2 | 34 | -189.5 | -0.59 | -0.017 | 0.50 | 0.50 | It is necessary that the program logic provides for the reversal of strings, so that the p |
| variant-request-ad0de9f3 | request | sample3 | 51 | -447.6 | +0.28 | +0.005 | 0.50 | 0.42 | It is quite clear that at some points in the course of transformations (i.e., at the point |
