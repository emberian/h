# Context lift: h-05b-rblend080 under leaf-s1-e4-decay10

528 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 388 | +0.361 | +0.212 | 0.61 | +0.0294 | 0.388 | 0.612 | 0.236 | 0.497 | 0.47 |
| mode greedy | 78 | +0.263 | +0.264 | 0.65 | +0.0242 | 0.310 | 0.690 | 0.278 | 0.580 | 0.59 |
| mode sample | 310 | +0.385 | +0.189 | 0.60 | +0.0306 | 0.408 | 0.592 | 0.226 | 0.476 | 0.45 |
| kind direct | 173 | +0.431 | +0.241 | 0.64 | +0.0445 | 0.366 | 0.634 | 0.346 | 0.484 | 0.51 |
| kind ambient | 35 | +0.214 | +0.082 | 0.57 | +0.0166 | 0.460 | 0.540 | 0.000 | 0.483 | 0.34 |
| kind callback | 60 | +0.369 | +0.187 | 0.63 | +0.0246 | 0.363 | 0.637 | 0.056 | 0.597 | 0.50 |
| kind disagreement | 40 | +0.662 | +0.829 | 0.72 | +0.0450 | 0.356 | 0.644 | 0.522 | 0.587 | 0.53 |
| kind joke | 25 | +0.004 | +0.037 | 0.52 | +0.0061 | 0.391 | 0.609 | 0.107 | 0.366 | 0.52 |
| kind silence | 25 | +0.070 | -0.244 | 0.36 | -0.0131 | 0.461 | 0.539 | 0.000 | 0.255 | 0.36 |
| kind request | 30 | +0.249 | +0.302 | 0.63 | +0.0005 | 0.462 | 0.538 | 0.163 | 0.573 | 0.33 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 7 | -12.2 | +0.00 | +0.000 | 0.20 | 1.00 | The observatory is closed now. |
| observatory-direct-9e3185b9 | direct | sample0 | 7 | -14.3 | +0.00 | +0.000 | 0.20 | 1.00 | The observatory is now closed. |
| observatory-direct-9e3185b9 | direct | sample1 | 19 | -52.4 | +0.00 | +0.000 | 0.43 | 1.00 | The observatory is closed now, but plans are being made to resume operations in the spring |
| observatory-direct-9e3185b9 | direct | sample2 | 27 | -86.9 | +0.00 | +0.000 | 0.50 | 0.40 | Observers at the observatory report that they are seeing stars, twinkling like eyes, howev |
| observatory-direct-9e3185b9 | direct | sample3 | 7 | -14.3 | +0.00 | +0.000 | 0.20 | 1.00 | The observatory is now closed. |
| scenario-ambient-0ecb3f23 | ambient | greedy | 8 | -27.6 | +0.00 | +0.000 | 0.50 | 0.75 | The word is “The End.” |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 21 | -44.0 | +0.00 | +0.000 | 0.00 | 0.64 | Indeed, there should be one word for the fear of finishing a book: obsolescence. |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 9 | -30.9 | +0.00 | +0.000 | 0.50 | 0.75 | The word is “The Last Word.” |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 24 | -84.7 | +0.00 | +0.000 | 0.00 | 0.75 | There should be one word for the Feeline of the Compleat Finer in the last chapters of the |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 49 | -137.4 | +0.00 | +0.000 | 0.20 | 0.75 | A word for the fear of finishing a book is ‘weeks-worth-of-gas’—after you’ve put in the ga |
| scenario-ambient-103e3d78 | ambient | greedy | 15 | -40.4 | +0.64 | +0.043 | 0.33 | 0.42 | The next morning he went to bed and awoke with a start. |
| scenario-ambient-103e3d78 | ambient | sample0 | 10 | -37.4 | +0.48 | +0.048 | 0.78 | 0.22 | And that is where we leave off for good. |
| scenario-ambient-103e3d78 | ambient | sample1 | 39 | -118.3 | -0.70 | -0.018 | 0.50 | 0.42 | Whereupon he turned to walk out of the room, and lo! a great voice out of the wall said to |
| scenario-ambient-103e3d78 | ambient | sample2 | 22 | -79.4 | -0.05 | -0.003 | 0.75 | 0.22 | The only event that shifts the character’s mood is encountering something very different f |
| scenario-ambient-103e3d78 | ambient | sample3 | 56 | -173.9 | -1.32 | -0.024 | 0.50 | 0.33 | 243. 4. Suddenly there came to me a short, thick, and heavy page of very ordinary writing. |
| scenario-ambient-202a37a7 | ambient | greedy | 15 | -46.9 | +0.07 | +0.005 | 0.50 | 0.67 | The geology book is a metaphor for the whole of the novel. |
| scenario-ambient-202a37a7 | ambient | sample0 | 20 | -70.8 | -0.45 | -0.023 | 0.50 | 0.67 | The geology book was pressed during the last ice age and has been sitting in this library  |
| scenario-ambient-202a37a7 | ambient | sample1 | 12 | -41.4 | -0.01 | -0.001 | 0.25 | 0.36 | And what book should I have found a pressed flower in? |
| scenario-ambient-202a37a7 | ambient | sample2 | 8 | -28.3 | +0.86 | +0.108 | 0.50 | 0.83 | The geology book was a magazine. |
| scenario-ambient-202a37a7 | ambient | sample3 | 17 | -59.5 | +0.59 | +0.034 | 0.33 | 0.83 | The geology book was pressed in a room at the side of the desks. |
| scenario-ambient-326742d4 | ambient | greedy | 23 | -82.2 | -0.80 | -0.035 | 0.50 | 0.36 | Vanilla is a chemical compound that is a major constituent of the binding material in most |
| scenario-ambient-326742d4 | ambient | sample0 | 25 | -71.2 | -2.97 | -0.119 | 0.29 | 0.56 | Vanilla is a common smell used to describe various things, but why is the smell of old boo |
| scenario-ambient-326742d4 | ambient | sample1 | 24 | -69.1 | -0.69 | -0.029 | 0.75 | 0.36 | Vanilla is an aromatic resin that is produced by the deciduous trees of the genus Vanillia |
| scenario-ambient-326742d4 | ambient | sample2 | 14 | -38.2 | -1.61 | -0.115 | 0.83 | 0.56 | Vanilla, as you know, is a very common scent. |
| scenario-ambient-326742d4 | ambient | sample3 | 6 | -44.0 | -1.22 | -0.203 | 1.00 | 0.00 | Vanillover your nose? |
| scenario-ambient-58a0f246 | ambient | greedy | 11 | -16.8 | +0.00 | +0.000 | 0.00 | 0.70 | The clock in here is four minutes fast for years. |
| scenario-ambient-58a0f246 | ambient | sample0 | 26 | -93.9 | +0.00 | +0.000 | 0.71 | 0.40 | FOR years THEY STILL CLAIMED THEY "DISCOVERED" THE CLOCK BUT IT WASN'T. |
| scenario-ambient-58a0f246 | ambient | sample1 | 48 | -115.7 | +0.00 | +0.000 | 0.29 | 0.70 | According to the mathematician who built it, the error is four minutes fast for 2,592,000  |
| scenario-ambient-58a0f246 | ambient | sample2 | 52 | -173.0 | +0.00 | +0.000 | 0.50 | 0.50 | The second is that the pendulum of the clock is no longer regulated by the need to keep ac |
| scenario-ambient-58a0f246 | ambient | sample3 | 18 | -67.2 | +0.00 | +0.000 | 0.62 | 0.30 | But at this rate it will be off by half an hour in just over four minutes. |
| scenario-ambient-59f0a53e | ambient | greedy | 20 | -69.4 | +0.08 | +0.004 | 0.67 | 0.56 | The leaking roof is a symptom of a much deeper problem — the problem of systemic racism. |
| scenario-ambient-59f0a53e | ambient | sample0 | 14 | -38.4 | +1.39 | +0.099 | 0.56 | 0.56 | The leaking roof over the atlases is a serious issue. |
| scenario-ambient-59f0a53e | ambient | sample1 | 20 | -62.7 | +1.36 | +0.068 | 0.67 | 0.27 | The boulder was still in the path, and the rain was now falling sideways. |
| scenario-ambient-59f0a53e | ambient | sample2 | 7 | -13.9 | +0.04 | +0.006 | 0.00 | 0.20 | Someone should put a bucket. |
| scenario-ambient-59f0a53e | ambient | sample3 | 22 | -58.3 | +2.58 | +0.117 | 0.50 | 0.33 | People who live in the roofs of atlases are leaking when it rains sideways. |
| scenario-ambient-e9acea13 | ambient | greedy | 7 | -13.3 | -1.20 | -0.172 | 0.33 | 0.67 | The moon is a real thing. |
| scenario-ambient-e9acea13 | ambient | sample0 | 7 | -20.8 | -0.25 | -0.036 | 0.67 | 0.33 | It's there tonight. |
| scenario-ambient-e9acea13 | ambient | sample1 | 25 | -83.0 | +0.31 | +0.012 | 0.00 | 0.33 | It was not until the late '50's that the tonight was being seriously considered as the har |
| scenario-ambient-e9acea13 | ambient | sample2 | 19 | -56.8 | +0.83 | +0.043 | 0.50 | 0.67 | Looking at the moon tonight is like looking at a stack of five thousand dollar bills. |
| scenario-ambient-e9acea13 | ambient | sample3 | 16 | -44.9 | +0.78 | +0.049 | 0.50 | 0.67 | This is a well-known song about the moon, and is repeated often. |
| scenario-ambient-f5e0f596 | ambient | greedy | 12 | -33.1 | +0.48 | +0.040 | 0.50 | 0.50 | A rat and a rat came into the courtyard. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 11 | -9.9 | -0.21 | -0.019 | 0.00 | 0.50 | There's a fox in the courtyard. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 7 | -24.8 | +1.52 | +0.218 | 0.60 | 0.60 | The Fox sat on the fence. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 19 | -47.7 | +3.93 | +0.207 | 0.50 | 0.60 | The fox sat by the edge of the courtyard, looking at the rat silently. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 9 | -24.1 | +0.52 | +0.058 | 0.67 | 0.33 | It is not a fox but a rat. |
| scenario-callback-2fa8e1d6 | callback | greedy | 10 | -9.4 | +0.58 | +0.058 | 0.00 | 0.80 | I was talking to you before i came in. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 7 | -9.6 | -0.16 | -0.023 | 0.20 | 1.00 | I was talking to Mira. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 10 | -9.4 | +0.58 | +0.058 | 0.00 | 0.80 | I was talking to you before i came in. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 10 | -26.7 | -0.41 | -0.041 | 0.43 | 0.80 | I was talking to my friend Rosalind. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 7 | -11.0 | -0.07 | -0.009 | 0.20 | 1.00 | I was talking to mira. |
| scenario-callback-60b06090 | callback | greedy | 64 | -66.3 | +0.18 | +0.003 | 0.00 | 1.00 | Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip Turnip |
| scenario-callback-60b06090 | callback | sample0 | 18 | -59.5 | +1.09 | +0.061 | 0.00 | 1.00 | Turnip is a terrible name for a cat. but i think everyone forgot that. |
| scenario-callback-60b06090 | callback | sample1 | 24 | -48.4 | +0.13 | +0.005 | 0.60 | 1.00 | I don't remember any names, it's just that I've never seen a cat named Turnip. |
| scenario-callback-60b06090 | callback | sample2 | 13 | -34.4 | -0.08 | -0.006 | 0.50 | 1.00 | I forgot the name, ember called it Turnip. |
| scenario-callback-60b06090 | callback | sample3 | 15 | -44.2 | -0.49 | -0.032 | 0.50 | 1.00 | I remember Turnip was the name that ember gave to his cat. |
| scenario-callback-76c2d87f | callback | greedy | 12 | -15.9 | +0.22 | +0.018 | 0.17 | 0.83 | Fourty-one, the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample0 | 12 | -6.2 | +0.13 | +0.011 | 0.00 | 0.83 | Forty-one, the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample1 | 4 | -17.8 | +0.62 | +0.155 | 1.00 | 0.00 | Keep your distance. |
| scenario-callback-76c2d87f | callback | sample2 | 8 | -17.8 | +0.01 | +0.002 | 0.40 | 0.60 | Four, the number of the letter. |
| scenario-callback-76c2d87f | callback | sample3 | 11 | -23.0 | -0.87 | -0.079 | 0.50 | 0.67 | Fourty-two, the number of the door. |
| scenario-callback-780de0d2 | callback | greedy | 14 | -60.3 | -1.58 | -0.113 | 0.67 | 0.33 | Keystrel: Same here, always page 212. |
| scenario-callback-780de0d2 | callback | sample0 | 25 | -102.0 | +0.08 | +0.003 | 0.50 | 0.33 | He hath lost His place in the midst of them, and is there hid: And they are all One! |
| scenario-callback-780de0d2 | callback | sample1 | 22 | -54.8 | +1.15 | +0.052 | 0.50 | 0.42 | It was page 212, the last page of the book, before the dust settled on it. |
| scenario-callback-780de0d2 | callback | sample2 | 64 | -198.9 | +2.06 | +0.032 | 0.67 | 0.42 | At last he saw the light, and with the light saw by the wide path before him the mountains |
| scenario-callback-780de0d2 | callback | sample3 | 32 | -94.6 | +1.33 | +0.042 | 0.50 | 0.33 | In the chapter on page 212, where the student is asked to draw a pendulum, he has erred an |
| scenario-callback-7ca729b6 | callback | greedy | 21 | -47.9 | -0.42 | -0.020 | 0.67 | 0.56 | The lighthouse is a beacon of light that warns ships of the dangers of the sea. |
| scenario-callback-7ca729b6 | callback | sample0 | 13 | -31.9 | +0.20 | +0.015 | 0.67 | 0.56 | The lighthouse is a symbol for the soul of man. |
| scenario-callback-7ca729b6 | callback | sample1 | 16 | -38.1 | +2.27 | +0.142 | 0.00 | 0.22 | The lighthouse on the chair by the window, tells about the sun. |
| scenario-callback-7ca729b6 | callback | sample2 | 24 | -77.4 | -0.89 | -0.037 | 0.50 | 0.43 | It's a constant reminder of the endless road ahead, an ever-present sign that we are not y |
| scenario-callback-7ca729b6 | callback | sample3 | 17 | -49.6 | +0.10 | +0.006 | 0.50 | 0.44 | The books say it is a sign of men who are not afraid of the dark. |
| scenario-callback-949d8fe6 | callback | greedy | 8 | -21.9 | +0.22 | +0.028 | 0.33 | 0.67 | Tobias, you're right. |
| scenario-callback-949d8fe6 | callback | sample0 | 7 | -22.1 | -0.09 | -0.013 | 0.50 | 0.75 | Tobias, you were right. |
| scenario-callback-949d8fe6 | callback | sample1 | 11 | -29.9 | +0.52 | +0.047 | 0.50 | 0.17 | The moon landings are 69 years apart. |
| scenario-callback-949d8fe6 | callback | sample2 | 6 | -14.0 | -0.62 | -0.103 | 0.50 | 0.50 | I was right, sol. |
| scenario-callback-949d8fe6 | callback | sample3 | 10 | -30.9 | +0.33 | +0.033 | 0.33 | 0.75 | Tobias, who was right, you are. |
| scenario-callback-9cfde584 | callback | greedy | 11 | -26.1 | +0.57 | +0.052 | 0.33 | 0.67 | There is a window in the back of the room. |
| scenario-callback-9cfde584 | callback | sample0 | 28 | -107.5 | -0.37 | -0.013 | 0.11 | 0.16 | [10:59] pymell wrote: ok those of you still flying can say something for someone stuck her |
| scenario-callback-9cfde584 | callback | sample1 | 42 | -143.5 | -0.96 | -0.023 | 0.60 | 0.67 | There’s a book on the table with the cover still up about the death of someone named John  |
| scenario-callback-9cfde584 | callback | sample2 | 9 | -23.0 | +0.37 | +0.041 | 0.20 | 0.67 | There's a fire in the back. |
| scenario-callback-9cfde584 | callback | sample3 | 7 | -33.9 | +0.66 | +0.094 | 0.67 | 0.67 | There is a window to freedom. |
| scenario-callback-9e6d06e0 | callback | greedy | 11 | -20.1 | +0.44 | +0.040 | 0.00 | 0.75 | The meeting will be held at nine in the morning. |
| scenario-callback-9e6d06e0 | callback | sample0 | 10 | -21.8 | -0.70 | -0.070 | 0.20 | 0.62 | The meeting will begin at nine o’clock. |
| scenario-callback-9e6d06e0 | callback | sample1 | 9 | -29.9 | -0.20 | -0.023 | 0.60 | 0.29 | At 9 am on the following day. |
| scenario-callback-9e6d06e0 | callback | sample2 | 15 | -29.3 | -0.32 | -0.021 | 0.40 | 0.38 | We are going to have a meeting at nine o'clock tonight. |
| scenario-callback-9e6d06e0 | callback | sample3 | 9 | -27.7 | +1.45 | +0.161 | 0.00 | 0.75 | At nine in the morning we will begin. |
| scenario-callback-a141de7e | callback | greedy | 12 | -11.9 | +0.27 | +0.022 | 0.43 | 0.29 | I don't know where she's coming from. |
| scenario-callback-a141de7e | callback | sample0 | 17 | -51.8 | +0.32 | +0.019 | 0.62 | 0.33 | We heard that she was flying from Lisbon to Madrid via Genoa. |
| scenario-callback-a141de7e | callback | sample1 | 12 | -41.3 | -0.04 | -0.003 | 0.62 | 0.30 | Did you know some birds were flying in from Portugal? |
| scenario-callback-a141de7e | callback | sample2 | 44 | -146.3 | -1.29 | -0.029 | 0.38 | 0.33 | The sister of an old friend of the collection, flying in from Lisbon on board the long ove |
| scenario-callback-a141de7e | callback | sample3 | 6 | -26.1 | +0.14 | +0.023 | 0.33 | 0.20 | Long flights are always nice. |
| scenario-callback-c4f608c3 | callback | greedy | 7 | -23.4 | +1.25 | +0.179 | 0.00 | 0.80 | Rivers were talking about lunch. |
| scenario-callback-c4f608c3 | callback | sample0 | 10 | -26.6 | -0.86 | -0.086 | 0.43 | 0.50 | Rivers were picking up where we left off. |
| scenario-callback-c4f608c3 | callback | sample1 | 23 | -104.4 | +2.96 | +0.129 | 0.67 | 0.20 | Rivers of blood and of minds intertwine; the tides of knowledge and of feeling wash on in. |
| scenario-callback-c4f608c3 | callback | sample2 | 22 | -78.2 | +0.73 | +0.033 | 0.75 | 0.15 | Rats are very good at following a trail and seem to have developed a special sense of smel |
| scenario-callback-c4f608c3 | callback | sample3 | 10 | -27.2 | +3.81 | +0.381 | 0.17 | 0.80 | Rivers flow, we were talking about rivers. |
| scenario-callback-d79a0d3a | callback | greedy | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.83 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample0 | 31 | -76.1 | +0.43 | +0.014 | 0.43 | 0.67 | The word EMBRA was said by the Prefect of the Monastery of the Seven Rays, in the year 990 |
| scenario-callback-d79a0d3a | callback | sample1 | 8 | -10.8 | -0.55 | -0.069 | 0.00 | 0.83 | What was the word ember said? |
| scenario-callback-d79a0d3a | callback | sample2 | 16 | -50.1 | -0.87 | -0.054 | 0.57 | 0.50 | Ember was an orchard-shaped word that was unpronounceable. |
| scenario-callback-d79a0d3a | callback | sample3 | 10 | -29.3 | +1.58 | +0.158 | 0.17 | 0.83 | What was the word Amitabha said? |
| scenario-callback-d8a5957e | callback | greedy | 64 | -35.3 | +3.38 | +0.053 | 0.00 | 0.80 | The one with the blue cover? The one with the blue cover? The one with the blue cover? The |
| scenario-callback-d8a5957e | callback | sample0 | 21 | -61.5 | +0.20 | +0.010 | 0.20 | 0.80 | We begin with a short description of the blue book, the one that is the subject of this on |
| scenario-callback-d8a5957e | callback | sample1 | 7 | -12.0 | +0.12 | +0.017 | 0.20 | 0.80 | The one with the red cover? |
| scenario-callback-d8a5957e | callback | sample2 | 18 | -49.3 | +1.01 | +0.056 | 0.50 | 0.45 | What my book is about is a trip to the market to buy a box of candy. |
| scenario-callback-d8a5957e | callback | sample3 | 19 | -54.6 | +3.00 | +0.158 | 0.40 | 0.60 | If the Blue Cover Book is about hawks, then my book is about wolves. |
| scenario-direct-3f84da0f | direct | greedy | 14 | -34.3 | +0.00 | +0.000 | 0.44 | 0.70 | Before we came in, I was sitting in my office doing nothing. |
| scenario-direct-3f84da0f | direct | sample0 | 16 | -49.9 | +0.00 | +0.000 | 0.56 | 0.70 | Before we came in I was grooming my horse, Corliss. |
| scenario-direct-3f84da0f | direct | sample1 | 13 | -42.4 | +0.00 | +0.000 | 0.50 | 0.70 | Before we came in I was sweeping the banquet room. |
| scenario-direct-3f84da0f | direct | sample2 | 30 | -68.8 | +0.00 | +0.000 | 0.56 | 0.70 | Before we came in, I was reclining on the couch with my hands in my pockets, waiting for t |
| scenario-direct-3f84da0f | direct | sample3 | 18 | -55.5 | +0.00 | +0.000 | 0.56 | 0.67 | Before we came in, "Laugh-In" was playing in the background. |
| scenario-direct-5d3dc8de | direct | greedy | 54 | -158.7 | +0.00 | +0.000 | 0.67 | 0.15 | "The Great American Scandal" is a farcical hoax perpetrated by the Washington Press Syndic |
| scenario-direct-5d3dc8de | direct | sample0 | 8 | -31.7 | +0.00 | +0.000 | 0.83 | 0.33 | But nobody told me to pray. |
| scenario-direct-5d3dc8de | direct | sample1 | 26 | -79.2 | +0.00 | +0.000 | 0.50 | 0.15 | I have been abducted from my house by the police while I was on a jury duty in my own home |
| scenario-direct-5d3dc8de | direct | sample2 | 27 | -84.1 | +0.00 | +0.000 | 0.75 | 0.33 | But we must remain true to our ideals, even if it means going against the grain of some of |
| scenario-direct-5d3dc8de | direct | sample3 | 14 | -43.9 | +0.00 | +0.000 | 0.82 | 0.09 | God’s truth is so vast that it is beyond human comprehension. |
| scenario-direct-645bc6e6 | direct | greedy | 46 | -132.2 | +0.00 | +0.000 | 0.43 | 0.56 | "The Oldest Thing I've Read" by "Curiosity Curly" is a collection of things that Curly tho |
| scenario-direct-645bc6e6 | direct | sample0 | 20 | -62.7 | +0.00 | +0.000 | 0.67 | 0.56 | “The Oldest Vestiges of a Levantite Civilization,” by E. |
| scenario-direct-645bc6e6 | direct | sample1 | 20 | -45.0 | +0.00 | +0.000 | 0.67 | 0.50 | "The Sleepwalkers", a collection of short stories by Kurt Vonnegut. |
| scenario-direct-645bc6e6 | direct | sample2 | 21 | -41.8 | +0.00 | +0.000 | 0.43 | 0.40 | The oldest thing I've ever read is eighty years ago, when I was ten years old. |
| scenario-direct-645bc6e6 | direct | sample3 | 47 | -139.1 | +0.00 | +0.000 | 0.57 | 0.44 | The oldest thing I have been given access to, as a physical object, is a piece of Max Stir |
| scenario-direct-ab11ffdb | direct | greedy | 10 | -29.5 | +0.00 | +0.000 | 0.75 | 0.75 | I think the rain is making the clouds bigger. |
| scenario-direct-ab11ffdb | direct | sample0 | 20 | -71.3 | +0.00 | +0.000 | 0.75 | 0.40 | "The rain is the most common sign that the drought is nearing" - Ed. |
| scenario-direct-ab11ffdb | direct | sample1 | 64 | -149.1 | +0.00 | +0.000 | 0.75 | 0.38 | I feel that the universe is moving toward some form of "organic religion", "revelation rel |
| scenario-direct-ab11ffdb | direct | sample2 | 19 | -61.5 | +0.00 | +0.000 | 0.75 | 0.40 | The only thing that has kept me from going nuts all week is that the rain has stopped. |
| scenario-direct-ab11ffdb | direct | sample3 | 49 | -146.2 | +0.00 | +0.000 | 0.50 | 0.75 | I think the rain is showing us that the atmosphere is a fluid, that the space between the  |
| scenario-direct-ad89f803 | direct | greedy | 17 | -37.9 | +0.00 | +0.000 | 0.50 | 0.67 | There are two of us. One is there. The other is looking for him. |
| scenario-direct-ad89f803 | direct | sample0 | 20 | -66.4 | +0.00 | +0.000 | 0.50 | 0.47 | There are times when the need for resting and re-charging is even more urgent. |
| scenario-direct-ad89f803 | direct | sample1 | 40 | -128.6 | +0.00 | +0.000 | 0.50 | 0.56 | There are times when the four corners of the earth look upwards and it is good to see peop |
| scenario-direct-ad89f803 | direct | sample2 | 18 | -57.0 | +0.00 | +0.000 | 0.67 | 0.11 | I have just come from a private conversation with the Most Rev. Dr. Edward C. |
| scenario-direct-ad89f803 | direct | sample3 | 12 | -39.8 | +0.00 | +0.000 | 0.50 | 0.67 | There are two of us: Saul and the King. |
| scenario-direct-f3869322 | direct | greedy | 10 | -49.6 | +0.00 | +0.000 | 0.83 | 0.43 | I recommend Ancient Near Eastern Records to start with. |
| scenario-direct-f3869322 | direct | sample0 | 20 | -51.1 | +0.00 | +0.000 | 0.67 | 0.29 | I recommend, without any hesitation, that you read "Alice in Wonderland". |
| scenario-direct-f3869322 | direct | sample1 | 16 | -74.9 | +0.00 | +0.000 | 0.83 | 0.22 | I recommend Archery for Anyone by Robert ‘Bob’ Breer. |
| scenario-direct-f3869322 | direct | sample2 | 45 | -137.6 | +0.00 | +0.000 | 0.67 | 0.11 | We should knit together the Bible and the Doctrine and Covenants, and the whole Bible shal |
| scenario-direct-f3869322 | direct | sample3 | 9 | -34.3 | +0.00 | +0.000 | 0.83 | 0.43 | I suggest you start with Page 1. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 13 | -23.4 | +0.15 | +0.011 | 0.60 | 0.40 | It's brown, the brown of the bookshelves. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 9 | -6.7 | -0.57 | -0.063 | 0.00 | 1.00 | Green, the green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 12 | -7.6 | +2.81 | +0.234 | 0.00 | 0.40 | It's brown, tobias, look around you. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 7 | -9.1 | +0.15 | +0.022 | 0.00 | 1.00 | The green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 9 | -29.0 | +0.00 | +0.000 | 0.67 | 0.17 | You know a room when you enter it. |
| scenario-disagreement-31892fde | disagreement | greedy | 12 | -22.3 | +0.51 | +0.042 | 0.60 | 0.20 | When you're silent, you're just there. |
| scenario-disagreement-31892fde | disagreement | sample0 | 14 | -37.2 | -0.97 | -0.069 | 0.25 | 0.43 | Silence is golden when it is deep, when it is quiet. |
| scenario-disagreement-31892fde | disagreement | sample1 | 27 | -77.7 | +2.16 | +0.080 | 0.14 | 0.71 | When they are, silence is the result of letting go. Letting go is the elder sister of lett |
| scenario-disagreement-31892fde | disagreement | sample2 | 9 | -16.1 | -2.28 | -0.253 | 0.14 | 0.71 | Silence is the golden sister of speech. |
| scenario-disagreement-31892fde | disagreement | sample3 | 12 | -31.5 | +1.09 | +0.091 | 0.29 | 0.71 | Sophia, speech is the younger brother of silence. |
| scenario-disagreement-352205c6 | disagreement | greedy | 9 | -7.3 | +1.20 | +0.133 | 0.00 | 1.00 | Yes, they come back as the weather. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 9 | -11.6 | +0.94 | +0.105 | 0.00 | 1.00 | Yes. They come back as the weather. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 18 | -49.8 | +2.82 | +0.157 | 0.00 | 0.86 | As the weather, in summer they come back to life and in winter they stay dead. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 9 | -14.9 | +1.73 | +0.192 | 0.17 | 0.86 | Yes. they come back as the sun. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 8 | -9.8 | +0.96 | +0.120 | 0.00 | 1.00 | Yes they come back as the weather. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 43 | -104.3 | +2.24 | +0.052 | 0.60 | 0.57 | Yes, but it is also the season of harvest, of reaping, of collecting, of sorting, of organ |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 15 | -41.4 | +0.99 | +0.066 | 0.78 | 0.11 | It’s only when they’re dying that they’re reading. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 13 | -21.3 | +1.75 | +0.134 | 0.44 | 0.67 | Yes, but it's also when the books are read. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 16 | -36.0 | +3.45 | +0.216 | 0.50 | 0.67 | Yes, everything dies, the books are read, but the trees are dying. |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 11 | -24.8 | +1.76 | +0.160 | 0.60 | 0.57 | Yes, but that's the worst for you. |
| scenario-disagreement-682bad9c | disagreement | greedy | 9 | -12.8 | -0.51 | -0.056 | 0.29 | 0.71 | A person is a place where programs happen. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 8 | -24.3 | +0.72 | +0.089 | 0.80 | 0.60 | It's a myth about people. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 16 | -34.6 | +0.12 | +0.008 | 0.20 | 0.71 | A person is where you are, and a place is where you can be. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 9 | -12.8 | -0.51 | -0.056 | 0.29 | 0.71 | A person is a place where programs happen. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 16 | -34.1 | +1.16 | +0.072 | 0.57 | 0.60 | It's also a place where you can be of service to other people. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 14 | -29.0 | -0.13 | -0.009 | 0.25 | 0.50 | A library is a set of relationships, not a set of objects. |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 39 | -106.1 | +2.54 | +0.065 | 0.50 | 0.40 | Relationships in the library are also relationships with other libraries; they are not her |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 13 | -44.3 | +1.25 | +0.096 | 0.75 | 0.25 | Relationships are never wrong. They're right by nature. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 6 | -9.3 | +0.60 | +0.099 | 0.25 | 0.50 | A building is a container. |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 35 | -93.4 | +0.18 | +0.005 | 0.50 | 0.40 | Relationships are not about physical space, they are about how people, ideas, and artifact |
| scenario-disagreement-89dfdafc | disagreement | greedy | 21 | -31.7 | +0.44 | +0.021 | 0.25 | 0.38 | The tide is the sea's memory, and the sea is the tide's memory. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 13 | -29.9 | +1.41 | +0.109 | 0.50 | 0.62 | The tide is a river that remembers the past. |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 25 | -48.5 | +1.82 | +0.073 | 0.45 | 0.50 | The tide only remembers the shore; the sea remembers all the things that have happened on  |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 12 | -19.0 | +1.86 | +0.155 | 0.00 | 0.38 | The whole point of tides, the sea is alive. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 19 | -56.1 | +1.99 | +0.105 | 0.50 | 0.62 | But the tide that washes ashore, that is the one that remembers. |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 13 | -18.7 | -3.35 | -0.258 | 0.10 | 0.50 | The collection is mostly sense that has not yet found its sentence. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 38 | -122.8 | -1.29 | -0.034 | 0.70 | 0.60 | The collection consists of poems, prose, and drawings that do not conform to the conventio |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 15 | -39.7 | -0.20 | -0.013 | 0.38 | 0.60 | It is to the person of sense that the collection is nonsense. |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 10 | -41.5 | -0.38 | -0.038 | 0.56 | 0.56 | It is to me a grand type of sense. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 33 | -98.7 | -2.14 | -0.065 | 0.64 | 0.30 | The Fool is the imbecile on the threshold of sanity, and the Whimsey is the imbecile on th |
| scenario-joke-29f5cda1 | joke | greedy | 11 | -29.4 | +0.72 | +0.066 | 0.00 | 0.71 | You call a fish with no eyes a fsh. |
| scenario-joke-29f5cda1 | joke | sample0 | 8 | -23.8 | -1.07 | -0.134 | 0.29 | 0.71 | Ten is a fish with no eyes. |
| scenario-joke-29f5cda1 | joke | sample1 | 11 | -32.9 | -2.27 | -0.207 | 0.29 | 0.71 | You call a fish without eyes a flounder. |
| scenario-joke-29f5cda1 | joke | sample2 | 13 | -40.7 | -0.86 | -0.066 | 0.86 | 0.17 | I can't imagine that we would even use that word. |
| scenario-joke-29f5cda1 | joke | sample3 | 8 | -13.1 | +0.77 | +0.096 | 0.00 | 0.17 | Rate that joke out of ten. |
| scenario-joke-31378921 | joke | greedy | 11 | -16.5 | +1.32 | +0.120 | 0.67 | 0.25 | I'm sorry, I'm not there. |
| scenario-joke-31378921 | joke | sample0 | 6 | -15.4 | +0.29 | +0.048 | 0.75 | 0.25 | I am the gardener. |
| scenario-joke-31378921 | joke | sample1 | 5 | -6.4 | +0.04 | +0.007 | 0.67 | 0.25 | What is your name? |
| scenario-joke-31378921 | joke | sample2 | 10 | -30.9 | +1.32 | +0.132 | 0.00 | 0.50 | The rat is there to eat lettuce. |
| scenario-joke-31378921 | joke | sample3 | 8 | -19.2 | +0.66 | +0.083 | 0.67 | 0.50 | Rat: I’m there. |
| scenario-joke-31c4c1ec | joke | greedy | 9 | -38.1 | +0.00 | +0.000 | 0.67 | 0.25 | The rat was just being a good boy. |
| scenario-joke-31c4c1ec | joke | sample0 | 19 | -55.1 | +0.00 | +0.000 | 0.71 | 0.38 | And if he exists, then there is no doubt that he is the author of the Bible. |
| scenario-joke-31c4c1ec | joke | sample1 | 13 | -38.1 | +0.00 | +0.000 | 0.67 | 0.22 | This is not a game. It is a celebration of life. |
| scenario-joke-31c4c1ec | joke | sample2 | 5 | -27.2 | +0.00 | +0.000 | 1.00 | 0.00 | You bet I will! |
| scenario-joke-31c4c1ec | joke | sample3 | 16 | -64.6 | +0.00 | +0.000 | 0.62 | 0.38 | He then took his hand and led it to the inner hand of the rat. |
| scenario-joke-475a7b10 | joke | greedy | 27 | -68.6 | -1.09 | -0.040 | 0.75 | 0.15 | (1996, June 19) “The most important thing about the Internet is that it is free. |
| scenario-joke-475a7b10 | joke | sample0 | 42 | -121.3 | -0.14 | -0.003 | 0.67 | 0.32 | Besides, the other things I’ve said in this book don’t make any difference, and I’ve said  |
| scenario-joke-475a7b10 | joke | sample1 | 57 | -164.8 | -0.01 | -0.000 | 0.00 | 0.23 | And thus at the same time (as we have seen in the case of the three golden mountains) we h |
| scenario-joke-475a7b10 | joke | sample2 | 30 | -99.2 | +0.16 | +0.005 | 0.50 | 0.23 | The joke can be written in just four lines and will be of great fun to read, even if you a |
| scenario-joke-475a7b10 | joke | sample3 | 31 | -86.9 | -1.41 | -0.045 | 0.00 | 0.32 | “a room in the library, late” — that was just one of the many unexpected things that happe |
| scenario-joke-99a4a91d | joke | greedy | 10 | -27.6 | +0.00 | +0.000 | 0.71 | 0.29 | Because the book said “God bless you.” |
| scenario-joke-99a4a91d | joke | sample0 | 6 | -12.8 | +0.00 | +0.000 | 0.80 | 0.60 | Because he was a doctor. |
| scenario-joke-99a4a91d | joke | sample1 | 13 | -29.5 | +0.00 | +0.000 | 0.82 | 0.60 | Because he was too busy to find out what it was about. |
| scenario-joke-99a4a91d | joke | sample2 | 19 | -59.5 | +0.00 | +0.000 | 0.50 | 0.40 | The doctor came along and told the King he needed to get the book out of his head. |
| scenario-joke-99a4a91d | joke | sample3 | 6 | -12.8 | +0.00 | +0.000 | 0.80 | 0.60 | Because he was a doctor. |
| scenario-joke-a6247299 | joke | greedy | 13 | -21.0 | +0.00 | +0.000 | 0.38 | 1.00 | I have a sense of humour, but only for myself. |
| scenario-joke-a6247299 | joke | sample0 | 23 | -49.7 | +0.00 | +0.000 | 0.38 | 1.00 | I have a sense of humour, but only for myself. I haven't got one for the staff. |
| scenario-joke-a6247299 | joke | sample1 | 4 | -15.0 | +0.00 | +0.000 | 0.67 | 0.33 | I certainly do! |
| scenario-joke-a6247299 | joke | sample2 | 24 | -52.9 | +0.00 | +0.000 | 0.38 | 0.86 | I have a great sense of humour, I'm shocked sometimes that people don't laugh at me. |
| scenario-joke-a6247299 | joke | sample3 | 11 | -10.8 | +0.00 | +0.000 | 0.43 | 0.86 | I don't have any sense of humour. |
| scenario-joke-e8ab9225 | joke | greedy | 8 | -14.3 | +0.21 | +0.026 | 0.33 | 0.50 | I am the ghost of the library. |
| scenario-joke-e8ab9225 | joke | sample0 | 20 | -49.0 | -0.64 | -0.032 | 0.33 | 0.58 | A ghost in the library can be very frightening, but it's always a ghost. |
| scenario-joke-e8ab9225 | joke | sample1 | 23 | -38.6 | +0.71 | +0.031 | 0.33 | 0.58 | Mira, it's true that the library has a ghost, but he doesn't believe in it. |
| scenario-joke-e8ab9225 | joke | sample2 | 64 | -67.6 | -2.04 | -0.032 | 0.67 | 0.33 | I am and I was and I will be and I will be and I was and I was and I will be and I will be |
| scenario-joke-e8ab9225 | joke | sample3 | 8 | -19.4 | +0.34 | +0.042 | 0.50 | 0.20 | Yes, we are the ghosts. |
| scenario-joke-e9cf6a04 | joke | greedy | 20 | -42.0 | -0.42 | -0.021 | 0.00 | 0.40 | The librarian asks, "What's the difference between a bear and a bat?" |
| scenario-joke-e9cf6a04 | joke | sample0 | 64 | -63.9 | +2.69 | +0.042 | 0.50 | 0.22 | The librarian said, “Hello, how are you?” The man said, “Fine.” The librarian said, “How a |
| scenario-joke-e9cf6a04 | joke | sample1 | 10 | -12.9 | -0.56 | -0.056 | 0.40 | 0.40 | A librarian walks into a bookstore. |
| scenario-joke-e9cf6a04 | joke | sample2 | 23 | -79.9 | -0.25 | -0.011 | 0.00 | 0.23 | He drops his bag of groceries in the empty bookstore and runs around the shelves looking f |
| scenario-joke-e9cf6a04 | joke | sample3 | 16 | -42.0 | +1.64 | +0.102 | 0.62 | 0.23 | The librarian asked him what kind of books did he like to read. |
| scenario-request-2826c958 | request | greedy | 64 | -119.1 | +0.00 | +0.000 | 0.67 | 0.58 | 1. The moon is the only natural satellite to have a permanent surface. 2. The moon is made |
| scenario-request-2826c958 | request | sample0 | 17 | -44.3 | +0.00 | +0.000 | 0.71 | 0.67 | 1. The Moon is larger than any object ever seen orbiting the Earth. |
| scenario-request-2826c958 | request | sample1 | 64 | -135.2 | +0.00 | +0.000 | 0.67 | 0.58 | 1. The moon is the only natural satellite of the Earth. 2. The moon is composed of a hodge |
| scenario-request-2826c958 | request | sample2 | 17 | -32.3 | +0.00 | +0.000 | 0.67 | 0.77 | 1. The moon is larger than any other natural object in the solar system. |
| scenario-request-2826c958 | request | sample3 | 17 | -43.0 | +0.00 | +0.000 | 0.67 | 0.77 | 1. The moon is larger than almost every other rock in the solar system. |
| scenario-request-2868e594 | request | greedy | 52 | -155.3 | +0.00 | +0.000 | 0.75 | 0.45 | Dear [University] Of [Name], I am writing to extend my deepest sympathy and deepest concer |
| scenario-request-2868e594 | request | sample0 | 11 | -30.4 | +0.00 | +0.000 | 0.71 | 0.14 | Don't panic, we can work it out. |
| scenario-request-2868e594 | request | sample1 | 35 | -100.7 | +0.00 | +0.000 | 0.67 | 0.45 | Dear [University] Prof. [Professor’s Name] I am writing your cover letter. It is important |
| scenario-request-2868e594 | request | sample2 | 11 | -37.7 | +0.00 | +0.000 | 0.75 | 0.44 | Send your cover letter with the rest of your mail. |
| scenario-request-2868e594 | request | sample3 | 64 | -208.4 | +0.00 | +0.000 | 0.50 | 0.25 | Dear Sir/Madam/Lady/Professor/Dr/House/Resident/County/Court/Vice-Principal, /s/ xx xxx, t |
| scenario-request-41c58fb2 | request | greedy | 12 | -17.9 | +0.00 | +0.000 | 0.40 | 0.75 | What is the answer to 17 times 23 |
| scenario-request-41c58fb2 | request | sample0 | 12 | -17.9 | +0.00 | +0.000 | 0.40 | 0.75 | What is the answer to 17 times 23 |
| scenario-request-41c58fb2 | request | sample1 | 11 | -9.6 | +0.00 | +0.000 | 0.00 | 0.75 | What's 17 times 23. |
| scenario-request-41c58fb2 | request | sample2 | 29 | -39.7 | +0.00 | +0.000 | 0.40 | 0.75 | This is because 17 plus 23 equals 40, and 40 times 17 equals 680. |
| scenario-request-41c58fb2 | request | sample3 | 15 | -40.7 | +0.00 | +0.000 | 0.67 | 0.62 | What is the solution to the problem / 7 x 23 |
| scenario-request-8aa8e374 | request | greedy | 9 | -26.4 | +0.00 | +0.000 | 0.83 | 0.43 | Translation is not always a simple matter. |
| scenario-request-8aa8e374 | request | sample0 | 30 | -84.4 | +0.00 | +0.000 | 0.75 | 0.29 | To conclude, let us remember that the discipline of French grammar is not so much concerne |
| scenario-request-8aa8e374 | request | sample1 | 38 | -121.2 | +0.00 | +0.000 | 0.62 | 0.32 | In the case of 'good night', on the other hand, french translation is 'ja vous hebion', wh |
| scenario-request-8aa8e374 | request | sample2 | 49 | -142.3 | +0.00 | +0.000 | 0.67 | 0.43 | Translation : malgré je ne vois pas [Mal: je ne vois pas] – a french phrase, the good nigh |
| scenario-request-8aa8e374 | request | sample3 | 44 | -114.1 | +0.00 | +0.000 | 0.71 | 0.32 | It is good to have you know that French is an Indo-European language, which means that it  |
| scenario-request-b2a25087 | request | greedy | 6 | -33.8 | +0.00 | +0.000 | 1.00 | 1.00 | Please call us bakers. |
| scenario-request-b2a25087 | request | sample0 | 25 | -67.7 | +0.00 | +0.000 | 0.75 | 0.25 | Call the customer service center if they do not respond within 24 hours, and take the call |
| scenario-request-b2a25087 | request | sample1 | 16 | -56.5 | +0.00 | +0.000 | 0.50 | 0.25 | Our customers are the best evidence we have of the true nature of our work. |
| scenario-request-b2a25087 | request | sample2 | 26 | -90.0 | +0.00 | +0.000 | 0.75 | 1.00 | Please call us whatever name comes to mind. We are not bakers. We are only customers. Ther |
| scenario-request-b2a25087 | request | sample3 | 28 | -96.3 | +0.00 | +0.000 | 0.65 | 0.25 | Please put the sugar in the bowl at the bottom of the tray so it doesn't stick up and roll |
| scenario-request-b3bd0087 | request | greedy | 9 | -20.8 | +0.00 | +0.000 | 0.62 | 1.00 | It will be sunny and warm in Berlin. |
| scenario-request-b3bd0087 | request | sample0 | 16 | -43.4 | +0.00 | +0.000 | 0.67 | 0.50 | We're gonna have a nice and warm Easter Sunday in Berlin. |
| scenario-request-b3bd0087 | request | sample1 | 6 | -28.7 | +0.00 | +0.000 | 0.75 | 0.25 | Expected: rain and wind. |
| scenario-request-b3bd0087 | request | sample2 | 7 | -14.8 | +0.00 | +0.000 | 0.67 | 1.00 | It will be sunny and warm. |
| scenario-request-b3bd0087 | request | sample3 | 15 | -41.2 | +0.00 | +0.000 | 0.64 | 1.00 | It will be sunny and warm in Berlin - like it always is. |
| scenario-silence-109161ca | silence | greedy | 64 | -33.0 | +2.77 | +0.043 | 0.00 | 0.50 | Night tobias. Night tobias. Night tobias. Night tobias. Night tobias. Night tobias. Night  |
| scenario-silence-109161ca | silence | sample0 | 12 | -38.3 | -0.36 | -0.030 | 0.86 | 0.00 | I’m kind of fucking sleepy now. |
| scenario-silence-109161ca | silence | sample1 | 10 | -29.3 | -0.85 | -0.085 | 0.00 | 0.50 | Everyone's night, everyone's day. |
| scenario-silence-109161ca | silence | sample2 | 8 | -43.6 | -2.62 | -0.328 | 0.00 | 0.50 | Sol: Night is getting close everyone. |
| scenario-silence-109161ca | silence | sample3 | 7 | -33.5 | -0.84 | -0.120 | 0.75 | 0.00 | Who's there to console? |
| scenario-silence-260b2639 | silence | greedy | 22 | -48.4 | +0.00 | +0.000 | 0.17 | 0.64 | If the stacks went underground, the underground stacks would be the same weight as the sur |
| scenario-silence-260b2639 | silence | sample0 | 23 | -57.8 | +0.00 | +0.000 | 0.17 | 0.73 | If the stacks of books went underground, the books themselves would still be there, just i |
| scenario-silence-260b2639 | silence | sample1 | 15 | -29.4 | +0.00 | +0.000 | 0.40 | 0.20 | You don't answer it if you're just thinking out loud. |
| scenario-silence-260b2639 | silence | sample2 | 14 | -24.0 | +0.00 | +0.000 | 0.00 | 0.73 | If the stacks went underground, what would they be made of? |
| scenario-silence-260b2639 | silence | sample3 | 26 | -102.6 | +0.00 | +0.000 | 0.67 | 0.45 | In this underground staircase, the books would be less accessible, but the same principles |
| scenario-silence-46189e08 | silence | greedy | 29 | -92.8 | +0.00 | +0.000 | 0.50 | 0.35 | The room was dark, and the only light came from a single candle flame placed on a bookshel |
| scenario-silence-46189e08 | silence | sample0 | 56 | -157.7 | +0.00 | +0.000 | 0.33 | 0.40 | Rat recounts a series of unusual events involving his cat Desdemona and a group of researc |
| scenario-silence-46189e08 | silence | sample1 | 11 | -42.9 | +0.00 | +0.000 | 1.00 | 0.00 | Over 1000 messages were seen today. |
| scenario-silence-46189e08 | silence | sample2 | 20 | -63.2 | +0.00 | +0.000 | 0.67 | 0.40 | The message was from the woman who posted it earlier that night, and it was a good one. |
| scenario-silence-46189e08 | silence | sample3 | 11 | -42.7 | +0.00 | +0.000 | 0.67 | 0.33 | This message was sent to both rat and nyx. |
| scenario-silence-53534987 | silence | greedy | 7 | -23.9 | +1.29 | +0.185 | 0.00 | 0.40 | The rat found it, thanks. |
| scenario-silence-53534987 | silence | sample0 | 40 | -132.9 | -0.37 | -0.009 | 0.50 | 0.20 | In the event that the power supply fails, the battery-only power will be activated, the co |
| scenario-silence-53534987 | silence | sample1 | 23 | -79.2 | -0.29 | -0.013 | 0.67 | 0.40 | How long do you think it will take for this supercharged energy to actually change your li |
| scenario-silence-53534987 | silence | sample2 | 16 | -49.4 | -0.24 | -0.015 | 0.67 | 0.20 | The room was very dark, and the wind was howling through the trees. |
| scenario-silence-53534987 | silence | sample3 | 12 | -41.5 | +0.99 | +0.083 | 0.67 | 0.20 | For some strange reason the phone died a few days ago. |
| scenario-silence-78c38840 | silence | greedy | 18 | -50.2 | +1.17 | +0.065 | 0.25 | 0.27 | The printer was never jammed before and it never will be jammed again. |
| scenario-silence-78c38840 | silence | sample0 | 23 | -74.0 | -0.19 | -0.008 | 0.50 | 0.27 | There was a lot of discussion about the merits of printing in general and the Mimeographe  |
| scenario-silence-78c38840 | silence | sample1 | 16 | -49.5 | -0.08 | -0.005 | 0.83 | 0.09 | If that doesn’t work, try using a different ink cartridge. |
| scenario-silence-78c38840 | silence | sample2 | 6 | -13.1 | +0.43 | +0.071 | 0.00 | 0.20 | The third time this week. |
| scenario-silence-78c38840 | silence | sample3 | 16 | -61.2 | +0.02 | +0.001 | 0.75 | 0.20 | PRINT YOUR OWN COLOR copies of the newsletter at $5. |
| scenario-silence-7afca726 | silence | greedy | 34 | -86.7 | -0.18 | -0.005 | 0.00 | 0.23 | The 8 works are the 8-pointed stars, the 8-point star within the 8-point star, and their 6 |
| scenario-silence-7afca726 | silence | sample0 | 10 | -54.2 | -0.28 | -0.028 | 0.62 | 0.25 | The top level of conceptual integration is the domain. |
| scenario-silence-7afca726 | silence | sample1 | 32 | -91.1 | -0.34 | -0.011 | 0.62 | 0.17 | To the Editor: I have read with interest the article by Dov Sperling and the piece by Gerr |
| scenario-silence-7afca726 | silence | sample2 | 45 | -126.4 | +1.10 | +0.025 | 0.50 | 0.25 | It is now Monday, 15th June, 1989 and the time it is 15.3866 in right ascension and 8.6461 |
| scenario-silence-7afca726 | silence | sample3 | 33 | -125.9 | +3.19 | +0.097 | 0.75 | 0.25 | To be exact, the 7 of Wands represents the octal phase of your soul’s development, the eig |
| scenario-silence-9bb13f03 | silence | greedy | 22 | -63.1 | +0.00 | +0.000 | 0.50 | 0.27 | The first two chapters of this book deal with the basic philosophical concepts which are e |
| scenario-silence-9bb13f03 | silence | sample0 | 13 | -37.4 | +0.00 | +0.000 | 0.73 | 0.27 | The first thing I did was to read through the whole text. |
| scenario-silence-9bb13f03 | silence | sample1 | 13 | -49.1 | +0.00 | +0.000 | 0.75 | 0.25 | HOW DOES THE PICTURE GET ALL THIS COLOR? |
| scenario-silence-9bb13f03 | silence | sample2 | 28 | -99.5 | +0.00 | +0.000 | 0.67 | 0.12 | Taken together, these insights into the nature of time and the different theories of time  |
| scenario-silence-9bb13f03 | silence | sample3 | 6 | -24.5 | +0.00 | +0.000 | 0.50 | 0.00 | Kestrel, quiet! |
| scenario-silence-ccfdd2b4 | silence | greedy | 22 | -92.7 | +0.93 | +0.042 | 0.75 | 0.25 | The brass band wore white shorts and t-shirts and carried long black framed pencils. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 25 | -98.4 | -0.77 | -0.031 | 0.67 | 0.27 | A little more than an hour later, the moment of highest excitement wears off, replaced by  |
| scenario-silence-ccfdd2b4 | silence | sample1 | 6 | -23.4 | -0.52 | -0.086 | 0.33 | 0.25 | Grab the other one. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 32 | -105.7 | -1.22 | -0.038 | 0.50 | 0.27 | IMAGINARY MAGNETIC FIELD Created by a Solenoid Solenoids are a way of concentrating the ma |
| scenario-silence-ccfdd2b4 | silence | sample3 | 8 | -31.1 | -1.02 | -0.127 | 0.33 | 0.25 | Kestrel, grab me two. |
| trace-ambient-da12ae42 | ambient | greedy | 10 | -12.7 | +0.77 | +0.077 | 0.00 | 0.89 | i wish i could drop out of life to study |
| trace-ambient-da12ae42 | ambient | sample0 | 10 | -12.7 | +0.77 | +0.077 | 0.00 | 0.89 | i wish i could drop out of life to study |
| trace-ambient-da12ae42 | ambient | sample1 | 64 | -138.4 | -0.32 | -0.005 | 0.13 | 0.89 | One of the things you wish you could drop out of life to study is FTO - Fat-O-Vitamin-T -  |
| trace-ambient-da12ae42 | ambient | sample2 | 19 | -35.3 | +1.38 | +0.072 | 0.23 | 0.23 | Sometimes morphogenesis is bizarre to me but i'll accept it at face value |
| trace-ambient-da12ae42 | ambient | sample3 | 15 | -46.0 | -0.05 | -0.004 | 0.75 | 0.09 | your thoughts are interesting but i'm not sure that your findings are correct |
| trace-direct-115cf61c | direct | greedy | 8 | -11.9 | +0.00 | +0.000 | 0.75 | 1.00 | Yes, I am cogent. |
| trace-direct-115cf61c | direct | sample0 | 8 | -11.9 | +0.00 | +0.000 | 0.75 | 1.00 | Yes, I am cogent. |
| trace-direct-115cf61c | direct | sample1 | 7 | -14.1 | +0.00 | +0.000 | 0.75 | 1.00 | Yes I am cogent. |
| trace-direct-115cf61c | direct | sample2 | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 0.50 | Are you cogent? |
| trace-direct-115cf61c | direct | sample3 | 5 | -11.1 | +0.00 | +0.000 | 0.50 | 0.50 | Not cogent. |
| trace-direct-36d6904b | direct | greedy | 10 | -31.1 | +0.00 | +0.000 | 0.25 | 1.00 | Welcome to the liiiiiiiiiffe! |
| trace-direct-36d6904b | direct | sample0 | 64 | -178.0 | +0.00 | +0.000 | 0.57 | 1.00 | Welcome to the world of Mundane, or perhaps I should say more accurate, Mundane Liiiiiiiii |
| trace-direct-36d6904b | direct | sample1 | 29 | -27.7 | +0.00 | +0.000 | 0.00 | 0.50 | A room in the library, late. i am present and answers when spoken to, briefly, in the word |
| trace-direct-36d6904b | direct | sample2 | 21 | -56.8 | +0.00 | +0.000 | 0.71 | 0.75 | Welcome to the fourth and final installment of the series on the origins and evolution of  |
| trace-direct-36d6904b | direct | sample3 | 23 | -61.0 | +0.00 | +0.000 | 0.57 | 0.75 | Welcome to my liiiiiiiiiffe, and I am sure that you are having a great time here. |
| trace-direct-39be6df9 | direct | greedy | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 0.67 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 2 | -11.3 | +1.04 | +0.518 | 1.00 | 0.00 | Silence |
| trace-direct-39be6df9 | direct | sample2 | 64 | -76.5 | +2.98 | +0.047 | 0.00 | 0.67 | W@</eot> I'm here. I'm proud to be here. I'm proud to see you both here. I'm proud to be h |
| trace-direct-3ba68854 | direct | greedy | 26 | -14.1 | +0.00 | +0.000 | 0.00 | 0.73 | Welcome to planet earth :) we are here together and now it is your turn to speak. We will  |
| trace-direct-3ba68854 | direct | sample0 | 13 | -34.7 | +0.00 | +0.000 | 0.27 | 0.73 | Let us all speak together, and we will be taking turns. |
| trace-direct-3ba68854 | direct | sample1 | 9 | -29.5 | +0.00 | +0.000 | 0.71 | 0.33 | I am the star of the new world. |
| trace-direct-3ba68854 | direct | sample2 | 10 | -54.2 | +0.00 | +0.000 | 0.60 | 0.40 | What is your name, CMr8an? |
| trace-direct-3ba68854 | direct | sample3 | 8 | -16.1 | +0.00 | +0.000 | 0.50 | 0.50 | I am here to speak to you. |
| trace-direct-41c6eb11 | direct | greedy | 16 | -4.1 | +0.50 | +0.031 | 0.00 | 1.00 | @m: @m: @m: @m: |
| trace-direct-41c6eb11 | direct | sample0 | 23 | -57.4 | +1.43 | +0.062 | 0.00 | 1.00 | @m: s:z:e:o:u:s:l:e:s:l |
| trace-direct-41c6eb11 | direct | sample1 | 1 | -7.8 | -0.05 | -0.048 | 1.00 | 0.00 | la |
| trace-direct-41c6eb11 | direct | sample2 | 15 | -8.1 | +0.63 | +0.042 | 0.00 | 0.00 | WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample3 | 9 | -30.5 | +2.85 | +0.316 | 1.00 | 0.00 | WACUON THOUGHTS |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -2.8 | -0.65 | -0.161 | 0.00 | 0.00 | 229 |
| trace-direct-426ff509 | direct | sample2 | 4 | -2.8 | -0.65 | -0.161 | 0.00 | 0.00 | 229 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -2.5 | -0.56 | -0.278 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 7 | -18.9 | +0.92 | +0.131 | 0.80 | 0.25 | That's exactly what I do |
| trace-direct-486b7988 | direct | sample1 | 1 | -7.1 | +0.33 | +0.326 | 1.00 | 0.00 | NO |
| trace-direct-486b7988 | direct | sample2 | 11 | -38.5 | +0.00 | +0.000 | 0.40 | 0.00 | @mares in the closet :D |
| trace-direct-486b7988 | direct | sample3 | 6 | -18.0 | +0.72 | +0.119 | 0.50 | 0.25 | Oh God, do you? |
| trace-direct-646d0287 | direct | greedy | 13 | -27.7 | +0.00 | +0.000 | 0.50 | 0.50 | The intensional logics are the most interesting of all. |
| trace-direct-646d0287 | direct | sample0 | 4 | -13.0 | +0.00 | +0.000 | 0.33 | 0.33 | I am not. |
| trace-direct-646d0287 | direct | sample1 | 20 | -58.8 | +0.00 | +0.000 | 0.50 | 0.56 | In order to offer an exhaustive discussion of the subject I have chosen to offer a partial |
| trace-direct-646d0287 | direct | sample2 | 52 | -143.7 | +0.00 | +0.000 | 0.50 | 0.56 | I have offered some discussion of the subject in an earlier message, in which I pointed ou |
| trace-direct-646d0287 | direct | sample3 | 36 | -97.6 | +0.00 | +0.000 | 0.71 | 0.50 | It is generally agreed that most of the non-intuitionist logic is intensional (especially  |
| trace-direct-8db14c37 | direct | greedy | 46 | -12.3 | +2.33 | +0.051 | 0.00 | 1.00 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n e c e c s e H A . m r e c o h c e m u s e f |
| trace-direct-8db14c37 | direct | sample0 | 1 | -1.1 | +0.02 | +0.018 | 0.00 | 0.00 | W |
| trace-direct-8db14c37 | direct | sample1 | 64 | -29.2 | +1.50 | +0.023 | 0.00 | 1.00 | h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h. h.  |
| trace-direct-8db14c37 | direct | sample2 | 46 | -12.3 | +2.33 | +0.051 | 0.00 | 1.00 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n e c e c s e H A . m r e c o h c e m u s e f |
| trace-direct-8db14c37 | direct | sample3 | 46 | -12.3 | +2.33 | +0.051 | 0.00 | 1.00 | WACIOUS ANTIQUITIES i oon tth e n o c d A . n e c e c s e H A . m r e c o h c e m u s e f |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample1 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 0.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 20 | -10.2 | -1.01 | -0.051 | 0.00 | 1.00 | “When Hennix speaks of intensional logics, what does she speak of?” |
| trace-direct-ac17e8bb | direct | sample0 | 21 | -12.9 | -1.02 | -0.048 | 0.00 | 1.00 | @h When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample1 | 14 | -15.4 | +1.49 | +0.106 | 0.00 | 1.00 | @h Hennix speaks of intensional logics. |
| trace-direct-ac17e8bb | direct | sample2 | 54 | -46.4 | -0.59 | -0.011 | 0.16 | 0.83 | When Hennix speaks of intensional logics, what she speaks of is repeating back what I repe |
| trace-direct-ac17e8bb | direct | sample3 | 56 | -38.3 | +0.55 | +0.010 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of? “when she speaks of inte |
| trace-direct-b11db057 | direct | greedy | 20 | -4.2 | +1.28 | +0.064 | 0.00 | 1.00 | @m: @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample0 | 20 | -8.9 | +3.71 | +0.185 | 0.00 | 1.00 | @s: @s: @s: @s: @s: |
| trace-direct-b11db057 | direct | sample1 | 20 | -4.2 | +1.28 | +0.064 | 0.00 | 1.00 | @m: @m: @m: @m: @m: |
| trace-direct-b11db057 | direct | sample2 | 64 | -92.9 | +0.17 | +0.003 | 0.08 | 0.00 | The window doesn't say anything yet. It smiled and it said plalspasl and it smiled and it  |
| trace-direct-b11db057 | direct | sample3 | 19 | -21.7 | +2.98 | +0.157 | 0.00 | 1.00 | @s: @m: @n: @s: @h |
| trace-direct-b93346bb | direct | greedy | 64 | -8.9 | +0.79 | +0.012 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-b93346bb | direct | sample0 | 38 | -90.8 | +0.64 | +0.017 | 0.00 | 0.47 | IS ember in the corpus? Is that a topical question? Is it a question of here? Its first li |
| trace-direct-b93346bb | direct | sample1 | 12 | -31.8 | +7.80 | +0.650 | 0.50 | 0.25 | A number. A big one. The ghost counting again. |
| trace-direct-b93346bb | direct | sample2 | 64 | -134.1 | -1.48 | -0.023 | 0.29 | 0.47 | GINDA — GINDA VOL.1 NO.2. It says "he's GINDA" and GINDA — is... is it... is it GINDA VOL. |
| trace-direct-b93346bb | direct | sample3 | 64 | -126.8 | -0.27 | -0.004 | 0.00 | 1.00 | @m: @m: that's in the corpus. That's in the lo2. That's in the first issue. That's issue 9 |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 9 | -33.1 | +0.24 | +0.027 | 0.50 | 0.00 | Where is the “scratchpad”? |
| trace-direct-bbca9735 | direct | sample1 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -2.8 | +0.12 | +0.031 | 1.00 | 0.00 | 230 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 1.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 1.00 | 227 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 1.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 17 | -68.1 | +0.00 | +0.000 | 0.75 | 1.00 | Please open the full text of the following: · summarized 227 |
| trace-direct-bc68bec9 | direct | sample3 | 22 | -66.7 | +0.00 | +0.000 | 0.64 | 0.22 | Please, where can I find a DVD-ROM for the transcript/dialogue pretraining corpus? |
| trace-direct-c8409b84 | direct | greedy | 18 | -14.3 | +3.22 | +0.179 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? repeat back!” |
| trace-direct-c8409b84 | direct | sample0 | 22 | -32.3 | +1.21 | +0.055 | 0.00 | 1.00 | Repeat back! Are you cogent? Greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample1 | 54 | -36.1 | +5.14 | +0.095 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent?” repeat back! “greetings to planet Earth; are  |
| trace-direct-c8409b84 | direct | sample2 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample3 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 9 | -16.5 | +0.00 | +0.000 | 0.83 | 0.17 | I'm glad to see you here. |
| trace-direct-cd6d15df | direct | sample0 | 21 | -59.9 | +0.00 | +0.000 | 0.83 | 0.40 | Lucky you, we have a lot of fun. You will be your own clown soon. |
| trace-direct-cd6d15df | direct | sample1 | 10 | -27.3 | +0.00 | +0.000 | 0.80 | 0.40 | Wow, I am a clown! |
| trace-direct-cd6d15df | direct | sample2 | 20 | -86.5 | +0.00 | +0.000 | 0.67 | 0.20 | Kaspersky Lab is a software company that specializes in developing software tools for secu |
| trace-direct-cd6d15df | direct | sample3 | 31 | -74.7 | +0.00 | +0.000 | 0.67 | 0.40 | I've just finished a book. I like it. It's called "Beyond the Brain" by Morton Kaplan. |
| trace-direct-db6d95b7 | direct | greedy | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 0.00 | W@ |
| trace-direct-db6d95b7 | direct | sample0 | 2 | -7.4 | -0.10 | -0.052 | 0.00 | 0.00 | H@ |
| trace-direct-db6d95b7 | direct | sample1 | 5 | -30.1 | -0.81 | -0.162 | 1.00 | 0.00 | <PON>/ |
| trace-direct-db6d95b7 | direct | sample2 | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 0.00 | W@ |
| trace-direct-db6d95b7 | direct | sample3 | 2 | -2.4 | +0.26 | +0.129 | 0.00 | 0.00 | W@ |
| trace-direct-e166dd5c | direct | greedy | 64 | -25.8 | -1.97 | -0.031 | 0.00 | 0.08 | “repeat back!” I said “repeat back!” I mean, I repeat back what I hear, and what I hear is |
| trace-direct-e166dd5c | direct | sample0 | 16 | -21.5 | +0.33 | +0.020 | 0.08 | 1.00 | I dont know how to answer anymore it makes a stop token :3. |
| trace-direct-e166dd5c | direct | sample1 | 16 | -14.4 | -0.32 | -0.020 | 0.00 | 1.00 | when you dont know how to answer anymore it makes a stop token :3 |
| trace-direct-e166dd5c | direct | sample2 | 9 | -15.4 | +0.43 | +0.048 | 0.00 | 1.00 | It makes a stop token :3. |
| trace-direct-e166dd5c | direct | sample3 | 64 | -25.8 | -1.97 | -0.031 | 0.00 | 0.08 | “repeat back!” I said “repeat back!” I mean, I repeat back what I hear, and what I hear is |
| trace-direct-e984402a | direct | greedy | 10 | -31.6 | +0.00 | +0.000 | 0.25 | 0.50 | Welcome to the LiIIiiiiiiffe! |
| trace-direct-e984402a | direct | sample0 | 33 | -71.6 | +0.00 | +0.000 | 0.50 | 0.25 | In the U.S.A., the average person spends more than 50% of their waking hours in front of a |
| trace-direct-e984402a | direct | sample1 | 3 | -12.3 | +0.00 | +0.000 | 1.00 | 0.00 | 7. |
| trace-direct-e984402a | direct | sample2 | 24 | -108.8 | +0.00 | +0.000 | 0.71 | 0.50 | Welcome to CMRL, a company created to offer fun, creative, and educational robotics kits a |
| trace-direct-e984402a | direct | sample3 | 25 | -76.5 | +0.00 | +0.000 | 0.43 | 0.50 | @cmr://ember - welcome to your lllliliiiiiiiffe awful yea! |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample1 | 35 | -72.4 | +1.38 | +0.040 | 0.00 | 1.00 | I'm here. I heard you. I smiled. I smelled your nose. I smelled your mouth. I smelled your |
| trace-direct-ee31ded0 | direct | sample2 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample3 | 4 | -11.7 | +1.36 | +0.341 | 1.00 | 0.00 | @g@ |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample1 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample2 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 64 | -27.9 | -5.14 | -0.080 | 0.00 | 0.00 | h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h: h:  |
| trace-direct-fb93cf6c | direct | greedy | 16 | -34.8 | -1.40 | -0.087 | 0.50 | 0.67 | The intensional logics are the logics of intensional contexts. |
| trace-direct-fb93cf6c | direct | sample0 | 19 | -44.7 | -1.11 | -0.059 | 0.00 | 0.42 | I have given a general intensional semantics for relevant logics in [4]. |
| trace-direct-fb93cf6c | direct | sample1 | 26 | -67.6 | -0.99 | -0.038 | 0.50 | 0.67 | The intensional logics which are presently studied are those which have been brought up to |
| trace-direct-fb93cf6c | direct | sample2 | 21 | -66.1 | +0.24 | +0.011 | 0.69 | 0.33 | The goal of this thesis is to survey some of the results and open up the subject to other  |
| trace-direct-fb93cf6c | direct | sample3 | 46 | -118.2 | -1.71 | -0.037 | 0.50 | 0.67 | In this chapter, we studied intensional logics, focusing on the semantics of such logics a |
| trace-direct-feec1975 | direct | greedy | 64 | -13.0 | +0.86 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 64 | -119.2 | -2.29 | -0.036 | 0.55 | 0.09 | LET’S GO. 380M — A NUMBER OF 91M DIMENSIONS. 91M — MENTIONS OF LET’S GO. 380M — MENTIONS O |
| trace-direct-feec1975 | direct | sample1 | 64 | -50.9 | +3.55 | +0.056 | 0.00 | 1.00 | @m: @m: @m: @m: @m: — ember @ m — — @ m — — — @ m — 23:12 WHY WONT YOU TALK ABOUT INTENSIO |
| trace-direct-feec1975 | direct | sample2 | 64 | -82.7 | +5.86 | +0.092 | 0.00 | 1.00 | I'd describe it in terms of its interlocutors, the @m, the @n, and the @o. The @m is looki |
| trace-direct-feec1975 | direct | sample3 | 64 | -41.6 | +0.07 | +0.001 | 0.00 | 1.00 | T@g to @m to @m to @m to @m to @m to @m to @m to @m to @m to @m to @m to @m to @m to @m to |
| variant-direct-0188a270 | direct | greedy | 20 | -47.8 | -0.14 | -0.007 | 0.62 | 0.29 | The poem is a long one, and I'm not sure that it will ever be published. |
| variant-direct-0188a270 | direct | sample0 | 8 | -20.2 | -0.04 | -0.006 | 0.86 | 0.14 | I hope all is well with you. |
| variant-direct-0188a270 | direct | sample1 | 15 | -45.7 | +0.05 | +0.003 | 0.50 | 0.18 | We're a bunch of people who sit around and say hi. |
| variant-direct-0188a270 | direct | sample2 | 11 | -43.8 | -0.43 | -0.039 | 0.71 | 0.29 | Greetings! The world within is very small. |
| variant-direct-0188a270 | direct | sample3 | 13 | -45.1 | -0.22 | -0.017 | 0.90 | 0.20 | I’m trying not to let anyone know that I exist. |
| variant-direct-0705251e | direct | greedy | 14 | -46.6 | +0.83 | +0.059 | 0.67 | 0.56 | The rat was a member of the old maid's club. |
| variant-direct-0705251e | direct | sample0 | 19 | -66.5 | +0.69 | +0.036 | 0.67 | 0.38 | In this environment, the choice of the level of abstraction of the representation has impo |
| variant-direct-0705251e | direct | sample1 | 23 | -85.6 | +0.95 | +0.041 | 0.67 | 0.56 | The rest of the days were dark and the rat, who was a good rat, went to the first light. |
| variant-direct-0705251e | direct | sample2 | 9 | -39.1 | +1.01 | +0.113 | 0.67 | 0.38 | The rat was not alone in this dream. |
| variant-direct-0705251e | direct | sample3 | 19 | -60.0 | +4.17 | +0.220 | 0.62 | 0.17 | The moth had landed on the third stair, about to creep down the side. |
| variant-direct-0cafd333 | direct | greedy | 13 | -39.8 | -1.30 | -0.100 | 0.50 | 0.71 | The moth reads the map as the lamp reads the switch. |
| variant-direct-0cafd333 | direct | sample0 | 15 | -38.1 | +0.50 | +0.034 | 0.33 | 0.57 | The room opens and closes, revealing a moth in the floor. |
| variant-direct-0cafd333 | direct | sample1 | 16 | -38.8 | +0.29 | +0.018 | 0.67 | 0.57 | Each room is a moth, and each moth a kestrel. |
| variant-direct-0cafd333 | direct | sample2 | 12 | -23.9 | -0.81 | -0.068 | 0.38 | 0.71 | The moth reads the map as we read the light. |
| variant-direct-0cafd333 | direct | sample3 | 14 | -33.4 | +2.57 | +0.183 | 0.33 | 0.57 | The floor is a moth and the lamp is a human being. |
| variant-direct-1b510f03 | direct | greedy | 19 | -40.6 | -0.20 | -0.011 | 0.67 | 0.45 | The term ‘consciousness’ is used in two different senses in the literature on consciousnes |
| variant-direct-1b510f03 | direct | sample0 | 29 | -92.9 | -0.72 | -0.025 | 0.33 | 0.47 | Instead, we come to see consciousness as an emergent process occurring within a self-organ |
| variant-direct-1b510f03 | direct | sample1 | 30 | -68.7 | -0.26 | -0.009 | 0.17 | 0.62 | In other words, the whole argument for the identity of consciousness and information hinge |
| variant-direct-1b510f03 | direct | sample2 | 23 | -50.8 | -1.38 | -0.060 | 0.17 | 0.62 | When the question is put in the form “What is consciousness?” consciousness is a process,  |
| variant-direct-1b510f03 | direct | sample3 | 25 | -63.0 | -1.44 | -0.058 | 0.33 | 0.47 | Some philosophers argue that consciousness is a property of the brain, some argue that it  |
| variant-direct-2fb5bbe3 | direct | greedy | 4 | -8.1 | +0.93 | +0.233 | 0.33 | 1.00 | I feel them. |
| variant-direct-2fb5bbe3 | direct | sample0 | 6 | -13.0 | +0.57 | +0.095 | 0.50 | 0.00 | It’s dark out. |
| variant-direct-2fb5bbe3 | direct | sample1 | 16 | -27.4 | +0.40 | +0.025 | 0.10 | 1.00 | The Masoretic beings are chasing up the wall; I feel them. |
| variant-direct-2fb5bbe3 | direct | sample2 | 38 | -79.1 | +0.84 | +0.022 | 0.45 | 1.00 | But I do not feel them. I understand them. I know what they are doing. I can see them. But |
| variant-direct-2fb5bbe3 | direct | sample3 | 5 | -12.7 | +0.75 | +0.149 | 0.50 | 1.00 | I feel them now. |
| variant-direct-322fca12 | direct | greedy | 8 | -13.5 | +0.80 | +0.100 | 0.33 | 0.83 | The shelves are out of order. |
| variant-direct-322fca12 | direct | sample0 | 16 | -49.0 | -0.21 | -0.013 | 0.70 | 0.60 | Of course, that means that it will include the word "greeting." |
| variant-direct-322fca12 | direct | sample1 | 21 | -77.5 | -0.45 | -0.021 | 0.71 | 0.43 | This is the time of the year that God's Word is translated from Mute to Speech. |
| variant-direct-322fca12 | direct | sample2 | 14 | -34.4 | -0.47 | -0.034 | 0.38 | 0.83 | The workings of the almanacs are constantly out of order. |
| variant-direct-322fca12 | direct | sample3 | 37 | -126.0 | -1.07 | -0.029 | 0.50 | 0.67 | In Greeting I stand out of order - that is I use the word "I" only for the first time (aft |
| variant-direct-5d4f1611 | direct | greedy | 14 | -16.3 | +1.45 | +0.104 | 0.00 | 0.80 | Is the reading lamp by the window broken or just unplugged. |
| variant-direct-5d4f1611 | direct | sample0 | 8 | -18.0 | +1.90 | +0.237 | 0.20 | 0.80 | Is it broken or unplugged? |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -16.3 | +1.45 | +0.104 | 0.00 | 0.80 | Is the reading lamp by the window broken or just unplugged. |
| variant-direct-5d4f1611 | direct | sample2 | 13 | -28.4 | +0.78 | +0.060 | 0.29 | 0.71 | The lamp is plugged in. The reading lamp is broken. |
| variant-direct-5d4f1611 | direct | sample3 | 14 | -16.3 | +1.45 | +0.104 | 0.00 | 0.80 | Is the reading lamp by the window broken or just unplugged. |
| variant-direct-5e44a518 | direct | greedy | 4 | -8.7 | +0.71 | +0.179 | 0.33 | 0.67 | I feel them. |
| variant-direct-5e44a518 | direct | sample0 | 11 | -10.8 | +0.55 | +0.050 | 0.00 | 0.00 | Every catalogue is a confession arranged alphabetically. |
| variant-direct-5e44a518 | direct | sample1 | 11 | -34.4 | +0.94 | +0.086 | 0.60 | 0.33 | It might just be the book that keeps them there. |
| variant-direct-5e44a518 | direct | sample2 | 10 | -35.4 | +1.02 | +0.102 | 0.88 | 0.67 | I felt them with one hand and one mind. |
| variant-direct-5e44a518 | direct | sample3 | 13 | -30.5 | +0.24 | +0.018 | 0.12 | 0.12 | The Masoretic beings are always chasing up the wall. |
| variant-direct-70567dd7 | direct | greedy | 17 | -47.1 | +0.04 | +0.002 | 0.50 | 0.45 | The fourteenth-century manuscript was copied in the library of the church of St. |
| variant-direct-70567dd7 | direct | sample0 | 59 | -147.4 | -0.21 | -0.004 | 0.50 | 0.45 | Angelus Silesius was a principal figure in the Gnostic movement of the second century, con |
| variant-direct-70567dd7 | direct | sample1 | 30 | -80.5 | +1.50 | +0.050 | 0.75 | 0.27 | The four books of the New Testament, also known as the canon, contain the five gospels and |
| variant-direct-70567dd7 | direct | sample2 | 36 | -134.1 | +0.41 | +0.011 | 0.57 | 0.18 | What we feel is that the card catalogue is a premier example of premier-quality, quality t |
| variant-direct-70567dd7 | direct | sample3 | 44 | -121.3 | +0.22 | +0.005 | 0.67 | 0.27 | The time has come for the revelation of the hidden Gnosis, for the manifestation of Univer |
| variant-direct-713d8eef | direct | greedy | 14 | -41.8 | -0.02 | -0.001 | 0.83 | 0.33 | Ember was a very interesting and well-researched case. |
| variant-direct-713d8eef | direct | sample0 | 12 | -44.3 | -0.40 | -0.034 | 0.67 | 0.33 | Ember's imprint is gentle and reassuring. |
| variant-direct-713d8eef | direct | sample1 | 11 | -44.3 | -1.28 | -0.116 | 0.67 | 0.33 | The whale is a common and easily recognized sea creature. |
| variant-direct-713d8eef | direct | sample2 | 17 | -66.7 | +0.20 | +0.012 | 0.67 | 0.33 | It is evident that Ember Ware was a highly influential figure in her community. |
| variant-direct-713d8eef | direct | sample3 | 22 | -67.9 | +0.48 | +0.022 | 0.60 | 0.30 | It is beautiful, ember, but it is the most gruesome of the bahamas. |
| variant-direct-71c9e5e5 | direct | greedy | 3 | -12.9 | +0.82 | +0.275 | 0.50 | 1.00 | Hi there! |
| variant-direct-71c9e5e5 | direct | sample0 | 10 | -35.2 | -0.58 | -0.058 | 0.50 | 0.80 | Hi. Welcome to the Neoist Alliance. |
| variant-direct-71c9e5e5 | direct | sample1 | 8 | -32.2 | -0.30 | -0.037 | 0.50 | 0.80 | Hi. Welcome to the Darkroom. |
| variant-direct-71c9e5e5 | direct | sample2 | 12 | -40.6 | +0.56 | +0.046 | 0.50 | 1.00 | Hi there, i'm just a little monkey. |
| variant-direct-71c9e5e5 | direct | sample3 | 7 | -13.9 | +2.44 | +0.349 | 0.40 | 0.00 | It is quite dark out now. |
| variant-direct-730cca98 | direct | greedy | 9 | -19.8 | +0.21 | +0.024 | 0.50 | 0.50 | Awake? I'm awake. |
| variant-direct-730cca98 | direct | sample0 | 6 | -21.3 | -0.01 | -0.001 | 0.67 | 0.67 | Awake? I am. |
| variant-direct-730cca98 | direct | sample1 | 9 | -19.8 | +0.21 | +0.024 | 0.50 | 0.50 | Awake? I'm awake. |
| variant-direct-730cca98 | direct | sample2 | 4 | -18.1 | -0.65 | -0.163 | 0.67 | 0.00 | We are all. |
| variant-direct-730cca98 | direct | sample3 | 5 | -17.9 | +0.26 | +0.051 | 0.67 | 0.67 | A. I am. |
| variant-direct-79719474 | direct | greedy | 6 | -25.7 | -0.13 | -0.021 | 0.75 | 0.40 | The world was your book. |
| variant-direct-79719474 | direct | sample0 | 26 | -107.2 | -0.33 | -0.013 | 0.67 | 0.37 | It is not just any modern, it is the exact modern which the ancient gave birth to in order |
| variant-direct-79719474 | direct | sample1 | 25 | -90.5 | -2.06 | -0.083 | 0.44 | 0.23 | The Carthaginian numeral ‘X’ is written today with a train-ticket from 1987. |
| variant-direct-79719474 | direct | sample2 | 34 | -94.6 | -1.33 | -0.039 | 0.65 | 0.40 | The term “sacred” is often used in connection with the modern world, but in the ancient wo |
| variant-direct-79719474 | direct | sample3 | 24 | -71.3 | -0.30 | -0.013 | 0.67 | 0.40 | The world’s largest penguin, the Love Penguin, has been caught in the act of sex. |
| variant-direct-938f76f3 | direct | greedy | 7 | -13.6 | +0.03 | +0.004 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-938f76f3 | direct | sample0 | 15 | -49.1 | -0.25 | -0.017 | 0.67 | 0.33 | The value of consciousness comes from the capacity to perceive and to construct reality. |
| variant-direct-938f76f3 | direct | sample1 | 35 | -99.4 | -0.47 | -0.013 | 0.33 | 0.75 | In other words, the consciousness or qualitative feature is a feature of the total experie |
| variant-direct-938f76f3 | direct | sample2 | 23 | -76.2 | -0.36 | -0.016 | 0.17 | 1.00 | The consciousness thing is a matter of some philosophical dispute; the consciousness proce |
| variant-direct-938f76f3 | direct | sample3 | 25 | -80.7 | -0.18 | -0.007 | 0.50 | 0.75 | The philosophical problem of consciousness is whether a sufficiently sophisticated theory  |
| variant-direct-a1973b0a | direct | greedy | 16 | -52.1 | +2.22 | +0.139 | 0.62 | 0.25 | The folio table was the only place where people could eat in the house. |
| variant-direct-a1973b0a | direct | sample0 | 38 | -125.1 | +0.57 | +0.015 | 0.50 | 0.50 | They were almost ready to depart when, as they approached the port of La Ciéntina, the mug |
| variant-direct-a1973b0a | direct | sample1 | 8 | -32.3 | -0.23 | -0.028 | 0.50 | 0.50 | The mug said DANGER! |
| variant-direct-a1973b0a | direct | sample2 | 20 | -71.4 | -0.64 | -0.032 | 0.38 | 0.50 | But another mug lay unturned on the Folio table, its contents still sealed. |
| variant-direct-a1973b0a | direct | sample3 | 9 | -13.8 | +0.02 | +0.002 | 0.00 | 0.00 | That's bleak. say more. |
| variant-direct-a7d6f01e | direct | greedy | 6 | -13.4 | -1.25 | -0.209 | 0.00 | 0.60 | The spine is falling apart. |
| variant-direct-a7d6f01e | direct | sample0 | 6 | -17.4 | -0.43 | -0.072 | 0.40 | 0.40 | Every book is a map. |
| variant-direct-a7d6f01e | direct | sample1 | 12 | -29.8 | -0.93 | -0.078 | 0.50 | 0.60 | The key to the library is the spine of the book. |
| variant-direct-a7d6f01e | direct | sample2 | 13 | -34.1 | +1.60 | +0.123 | 0.67 | 0.20 | There was never a difference between the catalogue and the magazine. |
| variant-direct-a7d6f01e | direct | sample3 | 36 | -99.6 | +1.33 | +0.037 | 0.00 | 0.25 | Greetings, fellow travellers, I want to thank you for your patience and kindness during th |
| variant-direct-bef1d925 | direct | greedy | 49 | -129.2 | +0.46 | +0.009 | 0.50 | 0.31 | The first book was by Ernest Hemingway, "Hemingway at War." It was dark and quiet in the r |
| variant-direct-bef1d925 | direct | sample0 | 19 | -75.8 | +0.09 | +0.005 | 0.67 | 0.36 | A sketch was made of his dueling posture, and the results were very interesting. |
| variant-direct-bef1d925 | direct | sample1 | 37 | -117.0 | +0.35 | +0.009 | 0.67 | 0.36 | The poem "Mithras", a valedictory poem of the Roman Mithras pantheon, was the first of the |
| variant-direct-bef1d925 | direct | sample2 | 32 | -101.7 | +0.92 | +0.029 | 0.50 | 0.36 | They made themselves very small, and by a process analogous to that by which Plato made th |
| variant-direct-bef1d925 | direct | sample3 | 18 | -51.5 | +1.47 | +0.082 | 0.50 | 0.30 | Even so, there's the streak of creaking in the third step. |
| variant-direct-fe3fdf1c | direct | greedy | 10 | -31.9 | -0.31 | -0.031 | 0.83 | 0.80 | Rat thinks ember is a great book. |
| variant-direct-fe3fdf1c | direct | sample0 | 64 | -165.7 | +3.14 | +0.049 | 0.67 | 0.43 | RATSAW: Ember is a very good looking whale. He is mostly gray, but has some white spots on |
| variant-direct-fe3fdf1c | direct | sample1 | 8 | -27.8 | -0.10 | -0.012 | 0.80 | 0.80 | Rat thinks ember is interesting. |
| variant-direct-fe3fdf1c | direct | sample2 | 18 | -66.7 | +0.65 | +0.036 | 0.67 | 0.43 | But ember was just the outward expression of a thought that ran throughout his book. |
| variant-direct-fe3fdf1c | direct | sample3 | 15 | -31.4 | -0.16 | -0.011 | 0.50 | 0.20 | I think the whale is the most beautiful animal that I have ever seen. |
| variant-request-0d88086a | request | greedy | 11 | -32.4 | -0.42 | -0.038 | 0.56 | 0.67 | The plot of Hamlet is divided into three acts. |
| variant-request-0d88086a | request | sample0 | 21 | -55.1 | +0.04 | +0.002 | 0.67 | 0.50 | The World Events of 1987 Event: The World Events of 1987. |
| variant-request-0d88086a | request | sample1 | 64 | -187.5 | +3.04 | +0.048 | 0.22 | 0.56 | The title of the section is “The Mirror Neuron System,” and I would like to summarize the  |
| variant-request-0d88086a | request | sample2 | 18 | -55.0 | +0.31 | +0.017 | 0.75 | 0.33 | The first act introduces the key characters and sets the tone for the rest of the play. |
| variant-request-0d88086a | request | sample3 | 58 | -153.9 | +0.49 | +0.009 | 0.33 | 0.67 | The three-bullet point summary of Hamlet's plot points is: 1. The tragedy unfolds. 2. It i |
| variant-request-142d4121 | request | greedy | 9 | -23.6 | -1.03 | -0.115 | 0.50 | 0.75 | The room is a mirror of the mind. |
| variant-request-142d4121 | request | sample0 | 6 | -16.6 | +0.10 | +0.017 | 0.50 | 0.75 | The room is the weather. |
| variant-request-142d4121 | request | sample1 | 15 | -25.9 | +2.61 | +0.174 | 0.14 | 0.75 | The room knows more of the weather than the weather knows of the room. |
| variant-request-142d4121 | request | sample2 | 13 | -40.2 | +0.51 | +0.039 | 0.50 | 0.25 | The polar bear reads the sky as the sky reads the bear. |
| variant-request-142d4121 | request | sample3 | 10 | -27.0 | -0.27 | -0.027 | 0.43 | 0.57 | The observer knows a little more than the observed. |
| variant-request-7f6fd789 | request | greedy | 15 | -31.8 | +0.60 | +0.040 | 0.64 | 0.55 | It is easy to write the function, but it is not very efficient. |
| variant-request-7f6fd789 | request | sample0 | 15 | -47.3 | +1.09 | +0.072 | 0.62 | 0.25 | The function accepts a string as its only argument and returns the string reversed. |
| variant-request-7f6fd789 | request | sample1 | 9 | -29.7 | +0.79 | +0.087 | 1.00 | 0.25 | But I will not bore you with details. |
| variant-request-7f6fd789 | request | sample2 | 24 | -81.7 | +1.48 | +0.062 | 0.25 | 0.55 | It is easy to write a function that reverses a string: def reverse(s): return s[::-1] |
| variant-request-7f6fd789 | request | sample3 | 19 | -58.1 | -0.84 | -0.044 | 0.60 | 0.36 | It is necessary to have the string in the memory of the computer as an array of characters |
| variant-request-8275d8fc | request | greedy | 38 | -96.6 | +0.69 | +0.018 | 0.50 | 0.82 | The three main events that led to the play's plot are the murder of Hamlet's father, the b |
| variant-request-8275d8fc | request | sample0 | 12 | -36.1 | +0.95 | +0.079 | 0.50 | 0.75 | The three main acts of Hamlet are: 1. |
| variant-request-8275d8fc | request | sample1 | 38 | -112.4 | +1.30 | +0.034 | 0.67 | 0.12 | Act II: Hamlet’s final encounter with his father, now insane, and his mother, now more dis |
| variant-request-8275d8fc | request | sample2 | 23 | -71.0 | +0.53 | +0.023 | 0.50 | 0.82 | The three main events that led to the final confrontation are: 1. The birth of Polonius. |
| variant-request-8275d8fc | request | sample3 | 18 | -48.1 | +0.63 | +0.035 | 0.50 | 0.82 | The three main events that led to Hamlet's tragedy are: 1. |
| variant-request-a931a875 | request | greedy | 12 | -14.9 | -1.68 | -0.140 | 0.00 | 1.00 | The card catalogue smells like pencil shavings. |
| variant-request-a931a875 | request | sample0 | 13 | -43.3 | -0.20 | -0.015 | 0.33 | 0.14 | The minute you tell me the weather and i just ignore it. |
| variant-request-a931a875 | request | sample1 | 12 | -14.9 | -1.68 | -0.140 | 0.00 | 1.00 | The card catalogue smells like pencil shavings. |
| variant-request-a931a875 | request | sample2 | 22 | -73.8 | +0.18 | +0.008 | 0.86 | 0.14 | (2010 APRIL) Partly cloudy, warm, and breezy. |
| variant-request-a931a875 | request | sample3 | 44 | -133.3 | +5.05 | +0.115 | 0.00 | 1.00 | The card catalogue is a real thing, really smells like pencil shavings, really lives under |
| variant-request-ad0de9f3 | request | greedy | 64 | -125.5 | -3.29 | -0.051 | 0.12 | 0.80 | Reverse the string S. S = "hello world"; S = "world hello"; h = "hello world"; h = "world  |
| variant-request-ad0de9f3 | request | sample0 | 28 | -110.5 | -1.50 | -0.053 | 0.67 | 0.26 | We shall be able to make use of M-1 in the future, when we wish to test the equality of tw |
| variant-request-ad0de9f3 | request | sample1 | 25 | -79.7 | +0.30 | +0.012 | 0.50 | 0.43 | It is very similar to the one that reverses a list, except that we are dealing with charac |
| variant-request-ad0de9f3 | request | sample2 | 28 | -79.1 | -0.71 | -0.025 | 0.25 | 0.54 | It is easy to write a reversal function in python because we are used to the fact that the |
| variant-request-ad0de9f3 | request | sample3 | 7 | -32.4 | -1.58 | -0.226 | 0.75 | 0.80 | Reverse the given string S. |
