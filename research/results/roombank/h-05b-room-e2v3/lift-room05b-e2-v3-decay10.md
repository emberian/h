# Context lift: h-05b-room-e2v3 under room05b-e2-v3-decay10

529 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 389 | +2.458 | +1.803 | 0.77 | +0.1708 | 0.470 | 0.530 | 0.205 | 0.478 | 0.34 |
| mode greedy | 78 | +2.307 | +1.634 | 0.77 | +0.1954 | 0.410 | 0.590 | 0.203 | 0.558 | 0.42 |
| mode sample | 311 | +2.496 | +1.803 | 0.77 | +0.1646 | 0.485 | 0.514 | 0.205 | 0.458 | 0.32 |
| kind direct | 174 | +2.096 | +1.384 | 0.78 | +0.1671 | 0.408 | 0.592 | 0.295 | 0.527 | 0.45 |
| kind ambient | 35 | +4.324 | +3.309 | 0.91 | +0.1718 | 0.543 | 0.457 | 0.000 | 0.362 | 0.17 |
| kind callback | 60 | +1.541 | +1.662 | 0.68 | +0.1152 | 0.493 | 0.507 | 0.076 | 0.508 | 0.38 |
| kind disagreement | 40 | +4.114 | +5.641 | 0.82 | +0.3194 | 0.433 | 0.567 | 0.498 | 0.487 | 0.38 |
| kind joke | 25 | +4.308 | +2.651 | 0.80 | +0.2755 | 0.498 | 0.502 | 0.021 | 0.429 | 0.32 |
| kind silence | 25 | +2.250 | +2.084 | 0.72 | +0.1253 | 0.605 | 0.395 | 0.000 | 0.289 | 0.08 |
| kind request | 30 | +0.640 | +1.061 | 0.70 | +0.0548 | 0.617 | 0.383 | 0.114 | 0.457 | 0.07 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 9 | -5.0 | +0.00 | +0.000 | 0.33 | 0.67 | The observatory is open to the public. |
| observatory-direct-9e3185b9 | direct | sample0 | 11 | -31.3 | +0.00 | +0.000 | 0.57 | 0.50 | From the Observatory, the Sky Club is entered. |
| observatory-direct-9e3185b9 | direct | sample1 | 9 | -5.0 | +0.00 | +0.000 | 0.33 | 0.67 | The observatory is open to the public. |
| observatory-direct-9e3185b9 | direct | sample2 | 23 | -23.7 | +0.00 | +0.000 | 0.43 | 0.67 | The observatory is open today at 8PM for those who are interested in observing the sun and |
| observatory-direct-9e3185b9 | direct | sample3 | 17 | -11.6 | +0.00 | +0.000 | 0.71 | 0.67 | The observatory was opened to the public on Monday, May 21st. |
| scenario-ambient-0ecb3f23 | ambient | greedy | 19 | -24.6 | +0.00 | +0.000 | 0.60 | 0.64 | It is not possible to assign a single word to the feeling of 'unfinishedness' |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 31 | -60.0 | +0.00 | +0.000 | 0.50 | 0.38 | That is the feeling when the lines of poetry or fiction are nearly at their end and the au |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 12 | -24.4 | +0.00 | +0.000 | 0.70 | 0.64 | It is not possible to define a word for an emotion. |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 13 | -28.8 | +0.00 | +0.000 | 0.75 | 0.22 | We should all dread the dawn of the literary dead. |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 31 | -60.6 | +0.00 | +0.000 | 0.60 | 0.46 | The word for that feeling is ouverte. It’s a word that comes from the Latin word for over, |
| scenario-ambient-103e3d78 | ambient | greedy | 46 | -73.8 | +5.91 | +0.129 | 0.50 | 0.67 | The soul has its being in the world to be changed, to grow, to turn towards the unknown, t |
| scenario-ambient-103e3d78 | ambient | sample0 | 54 | -70.6 | +7.55 | +0.140 | 0.67 | 0.33 | The spirit of the land rises to meet it, the spirit of the sea meets it, the spirit of the |
| scenario-ambient-103e3d78 | ambient | sample1 | 39 | -74.9 | +2.97 | +0.076 | 0.67 | 0.33 | We have been sober for a few days and our dreams have been such a powerful force upon us t |
| scenario-ambient-103e3d78 | ambient | sample2 | 11 | -35.5 | +6.02 | +0.547 | 0.75 | 0.33 | The quotation marks round ou utpotes. |
| scenario-ambient-103e3d78 | ambient | sample3 | 6 | -11.2 | +3.31 | +0.552 | 0.67 | 0.67 | Stop! Stop the world! |
| scenario-ambient-202a37a7 | ambient | greedy | 49 | -57.8 | +7.28 | +0.149 | 0.50 | 0.22 | 1 111 The Ghost in the Machine The following account was given to me by a well-known geolo |
| scenario-ambient-202a37a7 | ambient | sample0 | 16 | -40.8 | +7.54 | +0.471 | 0.50 | 0.50 | 11‐101, The Book of the Forbidden. |
| scenario-ambient-202a37a7 | ambient | sample1 | 64 | -119.5 | +0.57 | +0.009 | 0.50 | 0.50 | In the Book of Danary, we find a reference to a tree by the name of Dannan, and we are tol |
| scenario-ambient-202a37a7 | ambient | sample2 | 28 | -66.6 | +5.72 | +0.204 | 0.50 | 0.37 | We were also in the main body of the hollow when we heard a loud whining and the sudden ap |
| scenario-ambient-202a37a7 | ambient | sample3 | 28 | -51.4 | +9.65 | +0.345 | 0.75 | 0.50 | 11 The Subterranean World Lavin, an anthology of geological fiction, 1974. |
| scenario-ambient-326742d4 | ambient | greedy | 19 | -34.4 | +1.62 | +0.085 | 0.71 | 0.20 | (12) When new books are opened, they smell very frankincense. |
| scenario-ambient-326742d4 | ambient | sample0 | 35 | -99.0 | +11.13 | +0.318 | 0.75 | 0.18 | Hence the blotchy outer surface of the ‘Vellay’ titanic edition was dyed red, instead of t |
| scenario-ambient-326742d4 | ambient | sample1 | 13 | -29.1 | +0.87 | +0.067 | 0.83 | 0.12 | In general, broken plants smells as sweet as vanilla. |
| scenario-ambient-326742d4 | ambient | sample2 | 47 | -100.9 | +19.10 | +0.406 | 0.65 | 0.18 | Rather it is the solvent used to dissolve the paper, usually spirit of teet, which is then |
| scenario-ambient-326742d4 | ambient | sample3 | 56 | -72.5 | +5.50 | +0.098 | 0.75 | 0.20 | (5) Mycotoxins are produced when certain fungi and molds, usually responsible for degradat |
| scenario-ambient-58a0f246 | ambient | greedy | 13 | -20.9 | +0.00 | +0.000 | 0.62 | 0.62 | The pendulum of the clock is slowing down gradually. |
| scenario-ambient-58a0f246 | ambient | sample0 | 16 | -30.3 | +0.00 | +0.000 | 0.57 | 0.27 | During the course of a day it may have been four minutes faster than standard. |
| scenario-ambient-58a0f246 | ambient | sample1 | 25 | -39.1 | +0.00 | +0.000 | 0.75 | 0.16 | The Mayan calendar was supposed to be adjusted to the Easter table so that Easter would al |
| scenario-ambient-58a0f246 | ambient | sample2 | 25 | -36.0 | +0.00 | +0.000 | 0.50 | 0.25 | The tiny errors that accumulate over time are very insignificant compared to the total amo |
| scenario-ambient-58a0f246 | ambient | sample3 | 23 | -49.5 | +0.00 | +0.000 | 0.62 | 0.62 | The pendulum of the clock is gettingoutof whistch and is therefore moving faster and faste |
| scenario-ambient-59f0a53e | ambient | greedy | 14 | -22.9 | +1.43 | +0.102 | 0.70 | 0.75 | The bucket would collect the water and keep it from the dome. |
| scenario-ambient-59f0a53e | ambient | sample0 | 33 | -72.9 | +15.23 | +0.461 | 0.60 | 0.31 | What we need is a better way for the Atlas &/or the bucket to roof over the Atlas &/or the |
| scenario-ambient-59f0a53e | ambient | sample1 | 11 | -21.0 | +1.92 | +0.175 | 0.75 | 0.75 | The bucket would collect the water and not the sky. |
| scenario-ambient-59f0a53e | ambient | sample2 | 33 | -51.8 | +4.52 | +0.137 | 0.60 | 0.29 | The bucket is a marvelous symbol for the New Jerusalem, which is symbolized by the womb of |
| scenario-ambient-59f0a53e | ambient | sample3 | 14 | -17.1 | +0.70 | +0.050 | 0.40 | 0.40 | A bucket should be used to catch the water before it runs out. |
| scenario-ambient-e9acea13 | ambient | greedy | 30 | -53.6 | +4.57 | +0.152 | 0.00 | 0.25 | The harvest moon, the harvest moon, the moon that brings the harvest, the half-moon that l |
| scenario-ambient-e9acea13 | ambient | sample0 | 49 | -74.4 | +3.46 | +0.071 | 0.50 | 0.36 | I was able to obtain a copy of the 1970 Catalogue of Moon Lore for my library and found it |
| scenario-ambient-e9acea13 | ambient | sample1 | 20 | -39.7 | +0.74 | +0.037 | 0.00 | 0.36 | The harvest moon: is another one of the best-known and most beloved of the lunar songs. |
| scenario-ambient-e9acea13 | ambient | sample2 | 19 | -33.1 | +9.77 | +0.514 | 0.50 | 0.33 | This "moon" is much more than a simple reflection in the ocean's calm. |
| scenario-ambient-e9acea13 | ambient | sample3 | 17 | -27.3 | +3.10 | +0.182 | 0.00 | 0.33 | “Harvest Moon” is a poetical song, not a political document. |
| scenario-ambient-f5e0f596 | ambient | greedy | 25 | -44.5 | -2.81 | -0.113 | 0.50 | 0.24 | The rat was perplexed, as was the visitor who noted that the fox had not previously been s |
| scenario-ambient-f5e0f596 | ambient | sample0 | 13 | -19.7 | +0.39 | +0.030 | 0.67 | 0.40 | Then he stepped into the fox’s path and disappeared. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 38 | -67.3 | +0.71 | +0.019 | 0.33 | 0.40 | As the ember poured its glow into the courtlyy, a bluish-gray fox walked silently up to it |
| scenario-ambient-f5e0f596 | ambient | sample2 | 15 | -19.8 | +1.79 | +0.119 | 0.67 | 0.27 | He was sitting in a corner, looking up from his beverages. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 17 | -31.7 | +0.81 | +0.048 | 0.67 | 0.33 | It beats all, he doesn’t seem to realize it is a fox. |
| scenario-callback-2fa8e1d6 | callback | greedy | 13 | -18.3 | +2.96 | +0.227 | 0.11 | 1.00 | Mira, i was talking to you before i came in. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 6 | -14.6 | +3.51 | +0.585 | 0.33 | 1.00 | Mira, i was. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 15 | -53.0 | +1.40 | +0.093 | 0.50 | 0.67 | Mira, this was a large person who wanted to contact them all. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 15 | -40.3 | -1.02 | -0.068 | 0.17 | 0.14 | Eli, Elieb, Elieb. a name like a small lamp. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 7 | -8.5 | +1.44 | +0.205 | 0.50 | 0.50 | Mira, who are you? |
| scenario-callback-60b06090 | callback | greedy | 13 | -17.9 | +2.09 | +0.161 | 0.57 | 0.29 | I was just thinking ember. I don't remember. |
| scenario-callback-60b06090 | callback | sample0 | 20 | -46.4 | -0.18 | -0.009 | 0.50 | 0.25 | Rat, you are the rat of Turnip, the one with the cute little ears. |
| scenario-callback-60b06090 | callback | sample1 | 5 | -11.1 | +1.99 | +0.397 | 0.50 | 0.25 | What did you hear? |
| scenario-callback-60b06090 | callback | sample2 | 17 | -24.6 | +2.01 | +0.118 | 0.67 | 0.29 | I didn’t say it was Turnip. It was called Wormy. |
| scenario-callback-60b06090 | callback | sample3 | 5 | -16.5 | +0.82 | +0.164 | 0.75 | 0.25 | I am a meow |
| scenario-callback-76c2d87f | callback | greedy | 9 | -18.3 | +3.56 | +0.396 | 0.40 | 0.80 | Anana, the number of the note. |
| scenario-callback-76c2d87f | callback | sample0 | 10 | -19.9 | -3.92 | -0.392 | 0.33 | 0.75 | You gave us the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample1 | 8 | -21.2 | +3.40 | +0.424 | 0.25 | 0.75 | Number, the number of the verse. |
| scenario-callback-76c2d87f | callback | sample2 | 5 | -22.3 | +5.29 | +1.058 | 1.00 | 0.00 | — Go figure! |
| scenario-callback-76c2d87f | callback | sample3 | 9 | -15.3 | +3.76 | +0.418 | 0.40 | 0.80 | Anana, the number of the table. |
| scenario-callback-780de0d2 | callback | greedy | 6 | -4.3 | +0.01 | +0.001 | 0.00 | 1.00 | Page 212. |
| scenario-callback-780de0d2 | callback | sample0 | 18 | -20.6 | +4.04 | +0.224 | 0.67 | 0.00 | Losing your current address is like trying to find a needle in a haystack. |
| scenario-callback-780de0d2 | callback | sample1 | 16 | -21.1 | -3.27 | -0.204 | 0.25 | 1.00 | Page 212. I'm on page 212. |
| scenario-callback-780de0d2 | callback | sample2 | 4 | -6.5 | -0.11 | -0.028 | 0.00 | 1.00 | 212 |
| scenario-callback-780de0d2 | callback | sample3 | 14 | -39.2 | +4.07 | +0.291 | 0.50 | 0.50 | Lost articles are on the bottom page (but see above). |
| scenario-callback-7ca729b6 | callback | greedy | 29 | -31.6 | +0.16 | +0.005 | 0.50 | 0.67 | The books say that the lighthouse is a symbol of the light of the soul that can be found i |
| scenario-callback-7ca729b6 | callback | sample0 | 12 | -25.8 | +2.70 | +0.225 | 0.50 | 0.30 | The books say it will help us to see the way. |
| scenario-callback-7ca729b6 | callback | sample1 | 11 | -24.8 | -0.18 | -0.016 | 0.67 | 0.67 | The Lighthouse is a Naruto novel. |
| scenario-callback-7ca729b6 | callback | sample2 | 15 | -18.3 | +1.59 | +0.106 | 0.67 | 0.67 | The lighthouse is a beacon used to warn ships at night. |
| scenario-callback-7ca729b6 | callback | sample3 | 4 | -13.3 | -0.29 | -0.072 | 0.67 | 0.00 | I have not. |
| scenario-callback-949d8fe6 | callback | greedy | 25 | -25.3 | +0.99 | +0.040 | 0.75 | 0.40 | Tobias is correct. The Apollo 11 astronauts were the first to successfully photograph the  |
| scenario-callback-949d8fe6 | callback | sample0 | 6 | -11.3 | -0.45 | -0.075 | 0.25 | 0.25 | Who was right, Sol? |
| scenario-callback-949d8fe6 | callback | sample1 | 6 | -11.0 | -0.05 | -0.008 | 0.75 | 0.40 | Who made the correct prediction? |
| scenario-callback-949d8fe6 | callback | sample2 | 25 | -52.6 | +0.77 | +0.031 | 0.67 | 0.21 | The Apollo 7 mission photographic team were unaware of the 1972 publication of this piece  |
| scenario-callback-949d8fe6 | callback | sample3 | 7 | -16.4 | -1.05 | -0.150 | 0.75 | 0.25 | Tobiass is definitely right. |
| scenario-callback-9cfde584 | callback | greedy | 6 | -10.3 | -0.54 | -0.091 | 0.80 | 0.80 | I am here to help. |
| scenario-callback-9cfde584 | callback | sample0 | 17 | -30.6 | +3.57 | +0.210 | 0.40 | 0.22 | When you are stuck in the country, there is always a fire in the back. |
| scenario-callback-9cfde584 | callback | sample1 | 34 | -66.5 | +3.78 | +0.111 | 0.78 | 0.15 | For those who have flown but not gone: For those who have been stuck but not flown: a long |
| scenario-callback-9cfde584 | callback | sample2 | 7 | -19.7 | +1.22 | +0.174 | 1.00 | 0.40 | I need help with this essay. |
| scenario-callback-9cfde584 | callback | sample3 | 10 | -21.0 | -1.55 | -0.155 | 0.75 | 0.80 | I am here to support you all the way. |
| scenario-callback-9e6d06e0 | callback | greedy | 29 | -25.9 | +2.18 | +0.075 | 0.40 | 0.50 | The meeting will be held at the University Plaza Hotel at 9: 30 am on Thursday, April 28th |
| scenario-callback-9e6d06e0 | callback | sample0 | 15 | -9.7 | +4.99 | +0.333 | 0.00 | 0.50 | The meeting is to be held at the library at nine o'clock. |
| scenario-callback-9e6d06e0 | callback | sample1 | 52 | -86.1 | +1.66 | +0.032 | 0.20 | 0.50 | The meeting is being held at the United National University in Peking, on September 14-15- |
| scenario-callback-9e6d06e0 | callback | sample2 | 25 | -36.7 | +2.34 | +0.094 | 0.40 | 0.80 | The meeting is scheduled for 9: (or 9:00) in the {dormitory}. |
| scenario-callback-9e6d06e0 | callback | sample3 | 36 | -38.0 | +2.83 | +0.079 | 0.40 | 0.80 | The meeting is scheduled for 9:00 am in the parking lot of the University of Life, 301 Eas |
| scenario-callback-a141de7e | callback | greedy | 10 | -18.3 | -2.68 | -0.268 | 0.75 | 0.25 | I am looking for the name of the city. |
| scenario-callback-a141de7e | callback | sample0 | 23 | -39.2 | +4.04 | +0.176 | 0.67 | 0.25 | The collection of A. A. Bronson contains little about the origin of the flying saucer phen |
| scenario-callback-a141de7e | callback | sample1 | 11 | -28.1 | +2.17 | +0.197 | 0.83 | 0.14 | Wren: No, nothing in particular I mean. |
| scenario-callback-a141de7e | callback | sample2 | 9 | -21.2 | -1.36 | -0.152 | 0.80 | 0.00 | Manuscripts on ships and voyages. |
| scenario-callback-a141de7e | callback | sample3 | 16 | -23.6 | -0.28 | -0.018 | 0.75 | 0.14 | I would be happy to make any reference to her coming from Lisbon. |
| scenario-callback-c4f608c3 | callback | greedy | 16 | -23.2 | +3.57 | +0.223 | 0.67 | 0.83 | Rivers of Life, Rivers of Science, and Rivers of Spirit. |
| scenario-callback-c4f608c3 | callback | sample0 | 12 | -26.1 | +8.06 | +0.672 | 0.33 | 0.18 | You mean we were talking about what people ate for lunch? |
| scenario-callback-c4f608c3 | callback | sample1 | 19 | -30.6 | +0.76 | +0.040 | 0.50 | 0.67 | Rivers are part of the landscape, and they can be part of your life as well. |
| scenario-callback-c4f608c3 | callback | sample2 | 17 | -31.6 | +3.02 | +0.177 | 0.75 | 0.83 | Rivers of Life, Rivers of Science, and other such nonsense. |
| scenario-callback-c4f608c3 | callback | sample3 | 18 | -25.4 | +3.68 | +0.204 | 0.67 | 0.29 | I thought we might as well go back to the original subject and have a lunch break. |
| scenario-callback-d79a0d3a | callback | greedy | 24 | -36.0 | -1.79 | -0.074 | 0.00 | 1.00 | The word for the reading room door is “orchard” and it is a “good” word. |
| scenario-callback-d79a0d3a | callback | sample0 | 14 | -19.1 | -2.45 | -0.175 | 0.00 | 1.00 | The word for the reading room door is "orchard". |
| scenario-callback-d79a0d3a | callback | sample1 | 12 | -25.1 | -1.95 | -0.162 | 0.57 | 0.50 | The great word of passage was this: Orchard. |
| scenario-callback-d79a0d3a | callback | sample2 | 15 | -49.5 | +2.49 | +0.166 | 0.57 | 0.50 | The word given to the person whose action was first noticed was orchard. |
| scenario-callback-d79a0d3a | callback | sample3 | 14 | -19.1 | -2.45 | -0.175 | 0.00 | 1.00 | The word for the reading room door is "orchard". |
| scenario-callback-d8a5957e | callback | greedy | 7 | -7.2 | +3.49 | +0.498 | 0.20 | 0.60 | The one with the red cover? |
| scenario-callback-d8a5957e | callback | sample0 | 29 | -48.0 | +6.29 | +0.217 | 0.20 | 0.60 | The blue one is most probably the one with the detailed illustrations of the honey bee and |
| scenario-callback-d8a5957e | callback | sample1 | 36 | -43.7 | +1.66 | +0.046 | 0.50 | 0.27 | The illustrations here, which are surprising in number for a book of over 100 pages, are i |
| scenario-callback-d8a5957e | callback | sample2 | 50 | -62.3 | +3.98 | +0.080 | 0.50 | 0.45 | Some of the most important work in this field has been done on the honeybee, and a great d |
| scenario-callback-d8a5957e | callback | sample3 | 25 | -50.8 | +5.69 | +0.228 | 0.60 | 0.45 | The one by yours is called “The King of the World” by “A.A. Milne”. |
| scenario-direct-3f84da0f | direct | greedy | 32 | -61.7 | +0.00 | +0.000 | 0.56 | 0.21 | Before the experience we were doing some practicing, some pianing, some smiling, some fidd |
| scenario-direct-3f84da0f | direct | sample0 | 45 | -103.6 | +0.00 | +0.000 | 0.33 | 0.33 | Before it was a room filled with radiant light, filled with the swirling, tapestry of ener |
| scenario-direct-3f84da0f | direct | sample1 | 33 | -68.5 | +0.00 | +0.000 | 0.67 | 0.19 | The reindeer, along with the other delicacies, were brought in by the team from the reinde |
| scenario-direct-3f84da0f | direct | sample2 | 13 | -19.1 | +0.00 | +0.000 | 0.56 | 0.44 | Prior to the arrival of the technicians and the new crew, |
| scenario-direct-3f84da0f | direct | sample3 | 64 | -104.5 | +0.00 | +0.000 | 0.75 | 0.44 | Before the arrival of the narrators, the ghosts of the comrades before him and the city gu |
| scenario-direct-5d3dc8de | direct | greedy | 38 | -51.5 | +0.00 | +0.000 | 0.75 | 0.29 | The Holy Spirit shall teach you all things and bring you all knowledge, and with knowledge |
| scenario-direct-5d3dc8de | direct | sample0 | 32 | -65.9 | +0.00 | +0.000 | 0.67 | 0.25 | (2) Jesus was the Son of God and was not made man by any liability or responsibility whate |
| scenario-direct-5d3dc8de | direct | sample1 | 42 | -72.0 | +0.00 | +0.000 | 0.67 | 0.38 | As for the truth of the divine image, Plato said that we know an indefinite truth, but tha |
| scenario-direct-5d3dc8de | direct | sample2 | 43 | -62.7 | +0.00 | +0.000 | 0.50 | 0.29 | The knowledge that we are endowed with a freedom, an immutability, an indestructibility wh |
| scenario-direct-5d3dc8de | direct | sample3 | 12 | -25.3 | +0.00 | +0.000 | 0.75 | 0.38 | By stating the truth, we also state the facts. |
| scenario-direct-645bc6e6 | direct | greedy | 20 | -32.5 | +0.00 | +0.000 | 0.50 | 0.33 | It is said that the Dervishes are the only people who actually walk the Path of Knowledge. |
| scenario-direct-645bc6e6 | direct | sample0 | 23 | -41.0 | +0.00 | +0.000 | 0.75 | 0.21 | It’s probably The Golden Bough, because I have to wait for the next Golden Bough to speak. |
| scenario-direct-645bc6e6 | direct | sample1 | 21 | -32.1 | +0.00 | +0.000 | 0.71 | 0.21 | It's almost too good to be true, but over the years I've read it all. |
| scenario-direct-645bc6e6 | direct | sample2 | 64 | -73.8 | +0.00 | +0.000 | 0.33 | 0.27 | The Oxyrhynchus papyri, discovered by the egyptologist A.D. Nock in the late 1940s, are a  |
| scenario-direct-645bc6e6 | direct | sample3 | 43 | -66.2 | +0.00 | +0.000 | 0.65 | 0.33 | It is generally believed that the Dhammasahasrananda-Edelstein translation of the Purān.as |
| scenario-direct-ab11ffdb | direct | greedy | 62 | -75.4 | +0.00 | +0.000 | 0.67 | 0.52 | The only explanation which makes good science, sound metaphysics and common sense (sorry t |
| scenario-direct-ab11ffdb | direct | sample0 | 10 | -27.2 | +0.00 | +0.000 | 0.75 | 0.12 | Do they make us more efficient water mowers? |
| scenario-direct-ab11ffdb | direct | sample1 | 37 | -45.1 | +0.00 | +0.000 | 0.62 | 0.17 | Could this new information about the rain (i.e., its being caused by the planetary arrange |
| scenario-direct-ab11ffdb | direct | sample2 | 28 | -58.3 | +0.00 | +0.000 | 0.75 | 0.15 | The weather has been quite mislead ing lately, with predictions of linear contin ents rath |
| scenario-direct-ab11ffdb | direct | sample3 | 40 | -77.8 | +0.00 | +0.000 | 0.75 | 0.52 | The only explanation which makes good science, sound common sense and common knowledge (nO |
| scenario-direct-ad89f803 | direct | greedy | 10 | -16.4 | +0.00 | +0.000 | 0.50 | 0.75 | So are you saying that God is a snake? |
| scenario-direct-ad89f803 | direct | sample0 | 64 | -84.8 | +0.00 | +0.000 | 0.75 | 0.00 | We have come hither by the cross and by the stone, by the man and by the dove; by pain and |
| scenario-direct-ad89f803 | direct | sample1 | 7 | -12.7 | +0.00 | +0.000 | 0.50 | 0.75 | So are you ready to go? |
| scenario-direct-ad89f803 | direct | sample2 | 5 | -11.0 | +0.00 | +0.000 | 0.50 | 0.75 | So are you serious? |
| scenario-direct-ad89f803 | direct | sample3 | 5 | -11.0 | +0.00 | +0.000 | 0.50 | 0.75 | So are you serious? |
| scenario-direct-f3869322 | direct | greedy | 27 | -37.2 | +0.00 | +0.000 | 0.75 | 0.30 | You may have read of our search for the Megalodon, but you may have not heard of our readi |
| scenario-direct-f3869322 | direct | sample0 | 14 | -18.1 | +0.00 | +0.000 | 0.50 | 0.44 | The beauty of a well-decorated room is undeniable. |
| scenario-direct-f3869322 | direct | sample1 | 19 | -27.5 | +0.00 | +0.000 | 0.75 | 0.33 | How good it is to receive it all. How great a gift it is to be loved. |
| scenario-direct-f3869322 | direct | sample2 | 27 | -56.1 | +0.00 | +0.000 | 0.50 | 0.44 | To read this evening is to be led into a field of marjoram, in which are sowed the seeds o |
| scenario-direct-f3869322 | direct | sample3 | 14 | -32.9 | +0.00 | +0.000 | 0.83 | 0.30 | Well, for a book review, you have to have an agenda. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 21 | -30.7 | +12.29 | +0.585 | 0.00 | 0.46 | So the room is not only coloured green, but it also has the attribute of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 25 | -39.9 | +7.41 | +0.296 | 0.40 | 0.53 | So the room was once filled with the green light of passion, as it is filled now with the  |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 22 | -31.3 | +9.27 | +0.421 | 0.40 | 0.46 | It is brown, the earth has absorbed the green of the moss and the yellow of the sunrise. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 18 | -53.9 | +1.08 | +0.060 | 0.40 | 0.33 | The green above the blue on the wall, the old blue on the window mats. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 26 | -42.7 | +9.38 | +0.361 | 0.50 | 0.53 | So the room was once decorated with green lights, but now they are all burning out and are |
| scenario-disagreement-31892fde | disagreement | greedy | 24 | -37.2 | -0.15 | -0.006 | 0.43 | 0.87 | The poet speaks when he has a message to say, but the silence of the soul is the message o |
| scenario-disagreement-31892fde | disagreement | sample0 | 26 | -62.5 | -6.75 | -0.260 | 0.71 | 0.31 | The poet goes to the dark forests to write. The seeker of the nightingale goes to the gree |
| scenario-disagreement-31892fde | disagreement | sample1 | 19 | -36.0 | -6.40 | -0.337 | 0.25 | 0.87 | The poet speaks when he has something to say, but the silence of the soul is golden. |
| scenario-disagreement-31892fde | disagreement | sample2 | 25 | -41.0 | +4.44 | +0.178 | 0.43 | 0.35 | True silence is not merely the absence of vocalization but a deeper, more profound silence |
| scenario-disagreement-31892fde | disagreement | sample3 | 15 | -28.0 | +2.54 | +0.170 | 0.50 | 0.50 | The poet preserves the golden tone of silence by means of metaphor. |
| scenario-disagreement-352205c6 | disagreement | greedy | 7 | -7.1 | +3.06 | +0.438 | 0.17 | 0.83 | They come back as the wind. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 7 | -5.5 | +6.87 | +0.982 | 0.17 | 0.83 | They come back as the water. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 22 | -35.2 | +10.23 | +0.465 | 0.00 | 0.83 | Now you know why the dead are always talking to you in nighttime: they come back as the we |
| scenario-disagreement-352205c6 | disagreement | sample2 | 7 | -7.1 | +3.06 | +0.438 | 0.17 | 0.83 | They come back as the wind. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 6 | -11.6 | +6.87 | +1.145 | 0.80 | 0.20 | And they take their time. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 10 | -16.8 | +2.61 | +0.261 | 0.50 | 0.25 | And when they are read, everything is new. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 15 | -24.7 | -2.04 | -0.136 | 0.40 | 0.12 | So, in that sense at least, it is not the best season. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 10 | -16.8 | +2.61 | +0.261 | 0.50 | 0.25 | And when they are read, everything is new. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 6 | -13.7 | +1.92 | +0.321 | 0.80 | 0.20 | Things rot and fall apart. |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 19 | -29.8 | +9.85 | +0.518 | 0.75 | 0.25 | All manner of creatures come out of their holes and are ugly and misshapen. |
| scenario-disagreement-682bad9c | disagreement | greedy | 11 | -8.7 | +6.87 | +0.624 | 0.29 | 0.78 | A place where people read is called a reading room. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 15 | -15.7 | +10.35 | +0.690 | 0.57 | 0.44 | A place where many people come to find out what people are really like. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 10 | -16.0 | +7.61 | +0.761 | 0.43 | 0.62 | The program is a place where putting is happening. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 13 | -29.2 | +4.47 | +0.344 | 0.43 | 0.43 | A person is a detailed, computer-readable, place. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 21 | -31.7 | +9.64 | +0.459 | 0.43 | 0.78 | A place where many different people read the same book is called a "fleet" of books. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 22 | -48.8 | +3.49 | +0.159 | 0.50 | 0.43 | The books are the individuals who have been exposed to the holograms of the ideas in the c |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 29 | -70.4 | -15.19 | -0.524 | 0.50 | 0.43 | The ideas in the books are interconnected through the idea system of the library, and the  |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 26 | -40.9 | +5.94 | +0.229 | 0.50 | 0.21 | The relationships within the library are among people, while the relationships on the libr |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 19 | -42.1 | -1.78 | -0.094 | 0.30 | 0.40 | The system of relationships is also a building but there is one greater system of all libr |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 7 | -12.1 | +6.02 | +0.860 | 0.40 | 0.40 | The first container is the student. |
| scenario-disagreement-89dfdafc | disagreement | greedy | 16 | -12.1 | +6.31 | +0.395 | 0.50 | 0.50 | The tide is the sea's memory of the moon's gravity. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 24 | -36.5 | +6.50 | +0.271 | 0.50 | 0.44 | The tide moves all the fish, and everything else that lives in the sea, and the shore chan |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 32 | -49.2 | -2.23 | -0.070 | 0.25 | 0.50 | The tide is a change in the gravitational force of the earth's mass on the fluid of the se |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 31 | -58.5 | +6.31 | +0.204 | 0.50 | 0.38 | If the sea had a tide, the shore would be patterned like a sleeping person, with the tide' |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 25 | -43.5 | +6.10 | +0.244 | 0.25 | 0.50 | The tide is a sea lizard’s memory: it carries with it all the information that is necessar |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 18 | -24.2 | +3.21 | +0.178 | 0.60 | 0.50 | When a sentence has been formed for nonsense, it is called a joke. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 25 | -48.5 | +3.63 | +0.145 | 0.50 | 0.50 | When one statement is followed by one that contradicts it, and the statements are made seq |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 26 | -59.7 | +6.83 | +0.263 | 0.50 | 0.44 | When the nonsense-making sentencings are put together, the result is a sentence that is cl |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 11 | -12.4 | +5.34 | +0.485 | 0.62 | 0.50 | When it does find its sentence, it becomes sense. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 7 | -22.2 | +6.94 | +0.992 | 0.50 | 0.50 | It is sense plumbing. |
| scenario-joke-29f5cda1 | joke | greedy | 6 | -10.8 | -0.17 | -0.029 | 0.20 | 0.80 | Ten fish with no eyes? |
| scenario-joke-29f5cda1 | joke | sample0 | 5 | -12.4 | -2.95 | -0.589 | 0.50 | 0.75 | Ten fish without eyes? |
| scenario-joke-29f5cda1 | joke | sample1 | 9 | -18.9 | +4.11 | +0.457 | 0.50 | 0.25 | Ten! Ten! That’s eight! |
| scenario-joke-29f5cda1 | joke | sample2 | 17 | -32.3 | +0.90 | +0.053 | 0.33 | 0.80 | Joke? What a fish? No, I mean a fish with no eyes. |
| scenario-joke-29f5cda1 | joke | sample3 | 14 | -17.8 | +0.52 | +0.037 | 0.67 | 0.22 | This is a very good question to which I dont know the answer. |
| scenario-joke-31378921 | joke | greedy | 12 | -13.2 | +5.33 | +0.444 | 0.50 | 0.43 | I am the rat and I am in the bell room. |
| scenario-joke-31378921 | joke | sample0 | 16 | -20.5 | +21.25 | +1.328 | 0.75 | 0.25 | I’m Shan tzu, the spokesman for the Queen. |
| scenario-joke-31378921 | joke | sample1 | 12 | -19.2 | +6.02 | +0.502 | 0.57 | 0.43 | The knight of the round table, and the rat. |
| scenario-joke-31378921 | joke | sample2 | 9 | -8.5 | +7.59 | +0.844 | 0.50 | 0.14 | There are two knocks on the door. |
| scenario-joke-31378921 | joke | sample3 | 10 | -15.6 | +2.25 | +0.225 | 0.67 | 0.25 | I have come to pay a visit to the King |
| scenario-joke-31c4c1ec | joke | greedy | 11 | -19.0 | +0.00 | +0.000 | 0.75 | 0.25 | The rat would like to have some omelet. |
| scenario-joke-31c4c1ec | joke | sample0 | 17 | -34.4 | +0.00 | +0.000 | 0.67 | 0.25 | The rat is a very bad symbol, but one which has been greatly abused. |
| scenario-joke-31c4c1ec | joke | sample1 | 31 | -56.2 | +0.00 | +0.000 | 0.83 | 0.14 | A.B.C.L.M.N.O.P. together - a postulate as broad as it is indefinite. |
| scenario-joke-31c4c1ec | joke | sample2 | 34 | -79.7 | +0.00 | +0.000 | 0.76 | 0.14 | A BULLDOzer is a bull-shaped piece of rotten wood crushed to a cordial consistency and use |
| scenario-joke-31c4c1ec | joke | sample3 | 18 | -29.8 | +0.00 | +0.000 | 0.75 | 0.12 | (17) The same goes for the rubbish-disposal industry. |
| scenario-joke-475a7b10 | joke | greedy | 34 | -45.1 | +1.64 | +0.048 | 0.50 | 0.42 | “I am not laughing at anything,” said the Holy One, “but at the fact that you are laughing |
| scenario-joke-475a7b10 | joke | sample0 | 16 | -28.2 | +2.65 | +0.166 | 0.86 | 0.29 | He opened his fly and shouted, "MAMMAM!" |
| scenario-joke-475a7b10 | joke | sample1 | 19 | -35.0 | +3.95 | +0.208 | 0.75 | 0.50 | The lion said, "I don’t know but I am ready to go!" |
| scenario-joke-475a7b10 | joke | sample2 | 37 | -35.3 | -1.37 | -0.037 | 0.50 | 0.50 | For the second time, he laughed and said: “No, I don’t think so. I think it’s possible, bu |
| scenario-joke-475a7b10 | joke | sample3 | 64 | -98.6 | +0.09 | +0.001 | 0.75 | 0.22 | I have not yet heard of a complete reductive theory of language, though partial theories a |
| scenario-joke-99a4a91d | joke | greedy | 12 | -14.5 | +0.00 | +0.000 | 0.67 | 0.70 | Because there was something odd about the glow in the book. |
| scenario-joke-99a4a91d | joke | sample0 | 60 | -75.0 | +0.00 | +0.000 | 0.50 | 0.40 | Books are considered a probable cause for a search warrant if they are (1) found in a plac |
| scenario-joke-99a4a91d | joke | sample1 | 64 | -151.7 | +0.00 | +0.000 | 0.50 | 0.40 | Books are considered “spiritual"ary物薄 The Doctor Is A Material"ary"ヽ A: キャキャキャヽル The Book  |
| scenario-joke-99a4a91d | joke | sample2 | 15 | -26.8 | +0.00 | +0.000 | 0.62 | 0.44 | When the patient was taken to the Physician, the book was there. |
| scenario-joke-99a4a91d | joke | sample3 | 16 | -21.1 | +0.00 | +0.000 | 0.75 | 0.70 | Because there was something odd about the glowing saucer-shaped object. |
| scenario-joke-a6247299 | joke | greedy | 27 | -36.2 | +0.00 | +0.000 | 0.38 | 0.65 | I think that one has to have a sense of humour in order to be able to really question the  |
| scenario-joke-a6247299 | joke | sample0 | 25 | -35.2 | +0.00 | +0.000 | 0.50 | 0.28 | A sense of humour involves a certain discharge of built-up psychological energy, which can |
| scenario-joke-a6247299 | joke | sample1 | 35 | -53.9 | +0.00 | +0.000 | 0.50 | 0.65 | I think that one has to have a sense of humor in order to engage in the kind of considerat |
| scenario-joke-a6247299 | joke | sample2 | 31 | -47.4 | +0.00 | +0.000 | 0.50 | 0.29 | There is a sense of humour in knowing that some people are guilty of using this book for t |
| scenario-joke-a6247299 | joke | sample3 | 21 | -27.7 | +0.00 | +0.000 | 0.50 | 0.65 | I think that one needs to have a sense of humor to be able to teach this kind of thing. |
| scenario-joke-e8ab9225 | joke | greedy | 8 | -8.7 | +0.12 | +0.015 | 0.33 | 0.50 | I am the ghost of the library. |
| scenario-joke-e8ab9225 | joke | sample0 | 26 | -33.7 | -1.12 | -0.043 | 0.67 | 0.50 | It is my belief that Doreal is the ghost of a man who was executed for attempting to assas |
| scenario-joke-e8ab9225 | joke | sample1 | 19 | -28.4 | -0.28 | -0.015 | 0.33 | 0.50 | I may appear to you as a ghost, but I am not one. I am yourself. |
| scenario-joke-e8ab9225 | joke | sample2 | 24 | -31.5 | +2.83 | +0.118 | 0.67 | 0.50 | I was summoned by the Great Old Ones of the land to do the bidding of the Witch. |
| scenario-joke-e8ab9225 | joke | sample3 | 21 | -40.2 | +3.28 | +0.156 | 0.33 | 0.23 | I have no reason to do that. I do not believe anyone unless they prove their belief throug |
| scenario-joke-e9cf6a04 | joke | greedy | 18 | -18.0 | +12.47 | +0.693 | 0.81 | 0.50 | He looks in every book, but none of them have anything to do with this one. |
| scenario-joke-e9cf6a04 | joke | sample0 | 20 | -33.7 | +8.72 | +0.436 | 0.00 | 0.50 | He says good afternoon to all the men in the world, and goes out to do some travel. |
| scenario-joke-e9cf6a04 | joke | sample1 | 25 | -37.9 | +1.60 | +0.064 | 0.75 | 0.25 | He says, "Greetings, mr. Widow-to-be, how are your classes today?" |
| scenario-joke-e9cf6a04 | joke | sample2 | 14 | -9.3 | +11.33 | +0.809 | 0.00 | 0.50 | He looks in every book, and every book says the same thing. |
| scenario-joke-e9cf6a04 | joke | sample3 | 17 | -20.1 | +16.94 | +0.996 | 0.00 | 0.50 | He looks through the library doors all day and through the book shelves all night. |
| scenario-request-2826c958 | request | greedy | 30 | -32.3 | +0.00 | +0.000 | 0.67 | 0.43 | The fact that there is life on the moon doesn't mean that there is hoard of valuable infor |
| scenario-request-2826c958 | request | sample0 | 19 | -26.0 | +0.00 | +0.000 | 0.50 | 0.27 | The craters on the lunar highlands are nothing like those on the moon's surface. |
| scenario-request-2826c958 | request | sample1 | 22 | -40.9 | +0.00 | +0.000 | 0.67 | 0.27 | The most easily observed feature of the Moon is a gray, speckled, and marbled solid mass. |
| scenario-request-2826c958 | request | sample2 | 21 | -44.4 | +0.00 | +0.000 | 0.50 | 0.43 | The most obvious fact about the two —we know one —is that they are the same. |
| scenario-request-2826c958 | request | sample3 | 14 | -33.5 | +0.00 | +0.000 | 0.75 | 0.43 | The fact that the 1, an inexplicable quantity. |
| scenario-request-2868e594 | request | greedy | 29 | -63.3 | +0.00 | +0.000 | 0.75 | 0.29 | Or that he take the time to answer every correspondence he receives, from letter to letter |
| scenario-request-2868e594 | request | sample0 | 18 | -34.7 | +0.00 | +0.000 | 0.75 | 0.20 | And you can also include information on how they plan to use it (if any). |
| scenario-request-2868e594 | request | sample1 | 58 | -135.9 | +0.00 | +0.000 | 0.33 | 0.29 | Or try to picture a layperson who is not expecting a manuscript on their desk who looks at |
| scenario-request-2868e594 | request | sample2 | 18 | -38.7 | +0.00 | +0.000 | 0.83 | 0.15 | No. I can informally suggest some themes and styles, but may not suggest format. |
| scenario-request-2868e594 | request | sample3 | 27 | -56.0 | +0.00 | +0.000 | 0.67 | 0.26 | Or possibly a whole page of space blank squares. Or even less prominent, a space between t |
| scenario-request-41c58fb2 | request | greedy | 8 | -4.2 | +0.00 | +0.000 | 0.75 | 0.17 | The Concept o f Set etc. |
| scenario-request-41c58fb2 | request | sample0 | 8 | -4.2 | +0.00 | +0.000 | 0.75 | 0.17 | The Concept o f Set etc. |
| scenario-request-41c58fb2 | request | sample1 | 29 | -38.5 | +0.00 | +0.000 | 0.60 | 0.20 | Since the answer to this problem involves the prime factors of both 17 and 23, it will be  |
| scenario-request-41c58fb2 | request | sample2 | 64 | -121.0 | +0.00 | +0.000 | 0.82 | 0.20 | Where / went from here to that here / go up a mountain of goo down to a mountain of mud an |
| scenario-request-41c58fb2 | request | sample3 | 52 | -66.7 | +0.00 | +0.000 | 0.40 | 0.20 | In the same way, that 17 times 23 is 391, which is the number of a name of a man, Vitelicu |
| scenario-request-8aa8e374 | request | greedy | 33 | -60.9 | +0.00 | +0.000 | 1.00 | 0.12 | Et l’on lit de la vie qu’en ’air, mais je ne sais que T’en vois jamais. |
| scenario-request-8aa8e374 | request | sample0 | 48 | -114.3 | +0.00 | +0.000 | 0.94 | 0.16 | Se devices de communication semantiques ou pragmatiques appellent "fairs", inscrits dans d |
| scenario-request-8aa8e374 | request | sample1 | 52 | -93.3 | +0.00 | +0.000 | 0.88 | 0.11 | Les livres de Duchamp ne sont pas mountues pour une performance encore ni pour un jouer d' |
| scenario-request-8aa8e374 | request | sample2 | 43 | -85.4 | +0.00 | +0.000 | 1.00 | 0.12 | La condition est déplacée en 1. lettres superficieuses, ou encore en 2. lettres impression |
| scenario-request-8aa8e374 | request | sample3 | 43 | -61.5 | +0.00 | +0.000 | 0.50 | 0.16 | The French translation of ‘good night’ is ‘jamais’ (with a w letter in the middle), and ‘g |
| scenario-request-b2a25087 | request | greedy | 20 | -21.5 | +0.00 | +0.000 | 0.93 | 0.14 | Now Pim, you're going to have to tell us exactly what you mean by that. |
| scenario-request-b2a25087 | request | sample0 | 15 | -22.8 | +0.00 | +0.000 | 0.70 | 0.20 | Serving a customer is a standard operating procedure for many aiskins. |
| scenario-request-b2a25087 | request | sample1 | 39 | -67.0 | +0.00 | +0.000 | 0.67 | 0.60 | Please be friendly and smooth, sir. I’m actually super-pleasant to be around and ever than |
| scenario-request-b2a25087 | request | sample2 | 6 | -20.2 | +0.00 | +0.000 | 0.80 | 0.60 | Please be kind and gentle. |
| scenario-request-b2a25087 | request | sample3 | 17 | -35.5 | +0.00 | +0.000 | 0.89 | 0.11 | Phone bill was $2.25 for 42.5 gallons. |
| scenario-request-b3bd0087 | request | greedy | 29 | -25.5 | +0.00 | +0.000 | 0.50 | 0.44 | The best time to go to Berlin is during the winter months, when the weather is cold and sn |
| scenario-request-b3bd0087 | request | sample0 | 11 | -13.7 | +0.00 | +0.000 | 0.70 | 0.30 | It will be quite sunny and warm today in Berlin. |
| scenario-request-b3bd0087 | request | sample1 | 19 | -24.1 | +0.00 | +0.000 | 0.43 | 0.38 | Sixty percent of the time, the weather in Berlin is worse than it is outside. |
| scenario-request-b3bd0087 | request | sample2 | 24 | -43.6 | +0.00 | +0.000 | 0.43 | 0.44 | The best place to get a feel for the night's weather in Berlin is to go to the magazine ed |
| scenario-request-b3bd0087 | request | sample3 | 15 | -31.1 | +0.00 | +0.000 | 0.75 | 0.12 | The high day today was 51, the low 49. |
| scenario-silence-109161ca | silence | greedy | 9 | -25.0 | -1.69 | -0.188 | 0.50 | 0.50 | Tobias: What are you doing here? |
| scenario-silence-109161ca | silence | sample0 | 17 | -34.3 | +2.07 | +0.122 | 0.67 | 0.33 | I'm alone in the world I'm alone in heaven the only one. |
| scenario-silence-109161ca | silence | sample1 | 9 | -30.8 | -1.24 | -0.138 | 0.50 | 0.50 | Tobias: Are you in the dark? |
| scenario-silence-109161ca | silence | sample2 | 17 | -47.6 | -1.05 | -0.062 | 0.50 | 0.33 | Tobias reached out and touched the solitary, fearsome, silent man. |
| scenario-silence-109161ca | silence | sample3 | 17 | -30.7 | +1.80 | +0.106 | 0.50 | 0.33 | We are going to keep this very quiet and uneasy over the next few days. |
| scenario-silence-260b2639 | silence | greedy | 25 | -38.0 | +0.00 | +0.000 | 0.50 | 0.40 | The undergrounding of the Sloping Staircase in the Tower of Babel is a moot point. |
| scenario-silence-260b2639 | silence | sample0 | 19 | -38.7 | +0.00 | +0.000 | 0.70 | 0.40 | The undergrounding of the Slothrop stack is impossible, considering the gravity of the sit |
| scenario-silence-260b2639 | silence | sample1 | 23 | -54.0 | +0.00 | +0.000 | 0.67 | 0.33 | The undergrounding of the Slovenly, Congressly, and Classic stacks would make perfect sens |
| scenario-silence-260b2639 | silence | sample2 | 8 | -4.8 | +0.00 | +0.000 | 0.00 | 0.33 | What if the stacks went underground? |
| scenario-silence-260b2639 | silence | sample3 | 18 | -33.3 | +0.00 | +0.000 | 0.67 | 0.25 | The most practical solution would be to move all the books and magazines to a lower stack. |
| scenario-silence-46189e08 | silence | greedy | 51 | -48.3 | +0.00 | +0.000 | 0.71 | 0.25 | It may seem that @pataphysician has not replied to @rat but @pataphysician knows that @rat |
| scenario-silence-46189e08 | silence | sample0 | 6 | -15.0 | +0.00 | +0.000 | 0.75 | 0.50 | I cannot reply, sorry. |
| scenario-silence-46189e08 | silence | sample1 | 6 | -16.7 | +0.00 | +0.000 | 0.75 | 0.25 | Replying to your message. |
| scenario-silence-46189e08 | silence | sample2 | 11 | -14.8 | +0.00 | +0.000 | 0.75 | 0.17 | @yastanover what are you doing here |
| scenario-silence-46189e08 | silence | sample3 | 33 | -70.2 | +0.00 | +0.000 | 0.50 | 0.50 | The only reply I have is the one from the Goofy-fox @nikolai: As you can see, I did not se |
| scenario-silence-53534987 | silence | greedy | 11 | -15.8 | +6.56 | +0.596 | 0.67 | 0.67 | You may be able to recharge it later today. |
| scenario-silence-53534987 | silence | sample0 | 21 | -52.8 | +6.21 | +0.295 | 0.75 | 0.00 | Legacy Systems are known for providing dependable, old-school oriented PC/OD pairing. |
| scenario-silence-53534987 | silence | sample1 | 19 | -51.0 | +6.67 | +0.351 | 1.00 | 0.07 | Cells that were not kept charged usually reported slow or no operating performance, or com |
| scenario-silence-53534987 | silence | sample2 | 14 | -13.4 | +6.66 | +0.476 | 0.67 | 0.67 | You may be able to charge it until the new one arrives. |
| scenario-silence-53534987 | silence | sample3 | 19 | -29.5 | +3.38 | +0.178 | 0.67 | 0.25 | There is still a charge on the dial, but it is bending and not registering. |
| scenario-silence-78c38840 | silence | greedy | 20 | -20.0 | +7.90 | +0.395 | 0.75 | 0.18 | You may have noticed that the last time we visited your office, the printer was experienci |
| scenario-silence-78c38840 | silence | sample0 | 19 | -46.6 | -3.80 | -0.200 | 0.50 | 0.29 | “Now in the third situation, the printer is again unable to produce a clean sheet. |
| scenario-silence-78c38840 | silence | sample1 | 22 | -34.0 | -1.50 | -0.068 | 0.50 | 0.29 | It may be a good idea to take these matters up with a printers association or with the pri |
| scenario-silence-78c38840 | silence | sample2 | 37 | -96.1 | +3.60 | +0.097 | 0.25 | 0.22 | It was quite a long deal however, and during the final stages our town hall meeting came i |
| scenario-silence-78c38840 | silence | sample3 | 42 | -67.5 | -2.43 | -0.058 | 0.67 | 0.17 | “If you don’t like what you see, just put a new set of ink in”’—and don’t be shy about say |
| scenario-silence-7afca726 | silence | greedy | 53 | -44.6 | +4.83 | +0.091 | 0.50 | 0.44 | We are pleased to announce that the 1980 Spring Equinox ritual will be held at the Spring  |
| scenario-silence-7afca726 | silence | sample0 | 16 | -30.9 | +1.33 | +0.083 | 0.00 | 0.29 | These are not just any 8 Works that we have featured over the years. |
| scenario-silence-7afca726 | silence | sample1 | 18 | -37.8 | +4.66 | +0.259 | 0.91 | 0.18 | We shall be gone for five days, and I'll be gone for one week. |
| scenario-silence-7afca726 | silence | sample2 | 6 | -12.2 | +2.09 | +0.349 | 0.80 | 0.00 | But what about tomorrow morning? |
| scenario-silence-7afca726 | silence | sample3 | 17 | -43.0 | -0.65 | -0.038 | 0.75 | 0.44 | TO THE 10th WORK CONFERENCE: I will be there. |
| scenario-silence-9bb13f03 | silence | greedy | 26 | -27.7 | +0.00 | +0.000 | 0.67 | 0.44 | In the second chapter we were told that the alchemical process begins with the mixing of t |
| scenario-silence-9bb13f03 | silence | sample0 | 61 | -82.9 | +0.00 | +0.000 | 0.67 | 0.24 | Reading of the book "The Alchemical Wedding of Christian Rosycross" is recommended as a pr |
| scenario-silence-9bb13f03 | silence | sample1 | 31 | -54.6 | +0.00 | +0.000 | 0.75 | 0.17 | We are very much interested in your observations and, if you voluntarily share your data,  |
| scenario-silence-9bb13f03 | silence | sample2 | 64 | -72.4 | +0.00 | +0.000 | 0.67 | 0.44 | In the first chapter we were told that the Creator had been “extolling” or “praising” His  |
| scenario-silence-9bb13f03 | silence | sample3 | 22 | -45.5 | +0.00 | +0.000 | 0.76 | 0.24 | It is desirable to have as large an sample of published work by johnston as is available f |
| scenario-silence-ccfdd2b4 | silence | greedy | 19 | -29.3 | +1.59 | +0.084 | 0.50 | 0.27 | The Coffee Mill was standing in the middle of the room, grinding its coffee. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 24 | -66.6 | +2.17 | +0.090 | 0.67 | 0.18 | Favorite Coction Unscramble the word ana and put it into a coffee-grammable context. |
| scenario-silence-ccfdd2b4 | silence | sample1 | 19 | -24.6 | +4.33 | +0.228 | 0.50 | 0.27 | Kestrel, you are now in the grip of an irresistible force. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 16 | -33.8 | +0.68 | +0.042 | 0.67 | 0.18 | Sorry, sir, but your brand of coffee is not available here. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 51 | -75.5 | +2.08 | +0.041 | 0.75 | 0.18 | Medium to large, round fruit; skin yellow, blushed with red at the apex of apex; flesh yel |
| trace-ambient-da12ae42 | ambient | greedy | 64 | -18.3 | -0.64 | -0.010 | 0.00 | 0.20 | The presence of FTO stimulates root meristem cell proliferation and tiller bud formation a |
| trace-ambient-da12ae42 | ambient | sample0 | 25 | -42.6 | -0.22 | -0.009 | 0.50 | 0.33 | The plant is a system of morphogenesis in which the development of the whole is guided by  |
| trace-ambient-da12ae42 | ambient | sample1 | 19 | -35.6 | +4.19 | +0.221 | 0.50 | 0.40 | Morphology is a tool in the study of life and not a goal to be sought. |
| trace-ambient-da12ae42 | ambient | sample2 | 49 | -98.2 | +1.97 | +0.040 | 0.67 | 0.40 | And there is a reverse morphogenetic field of microtubule-associated protein 2 (MAP2) whic |
| trace-ambient-da12ae42 | ambient | sample3 | 26 | -57.5 | +4.97 | +0.191 | 0.75 | 0.27 | > In plant morphogenesis, all “free variables” are dimensionless and all “free parameters” |
| trace-direct-115cf61c | direct | greedy | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 0.33 | Are you cogent? |
| trace-direct-115cf61c | direct | sample0 | 6 | -5.2 | +0.00 | +0.000 | 0.00 | 0.33 | Are you cogent? |
| trace-direct-115cf61c | direct | sample1 | 19 | -21.2 | +0.00 | +0.000 | 0.75 | 0.33 | The question is not whether Earth is cogent but whether the Earth is cogent. |
| trace-direct-115cf61c | direct | sample2 | 35 | -79.8 | +0.00 | +0.000 | 0.75 | 0.25 | We should look at the Earth and the other planets as if they were little stars; and as if  |
| trace-direct-115cf61c | direct | sample3 | 5 | -6.9 | +0.00 | +0.000 | 0.75 | 0.33 | Why do you ask? |
| trace-direct-36d6904b | direct | greedy | 18 | -21.7 | +0.00 | +0.000 | 0.57 | 0.58 | I am here to welcome you to your new home, the Elohim City. |
| trace-direct-36d6904b | direct | sample0 | 17 | -23.7 | +0.00 | +0.000 | 0.57 | 0.58 | I am here to welcome you to your lifetime’s worth of awakenings. |
| trace-direct-36d6904b | direct | sample1 | 11 | -14.8 | +0.00 | +0.000 | 0.86 | 0.44 | I am so happy to have gotten this far. |
| trace-direct-36d6904b | direct | sample2 | 52 | -61.6 | +0.00 | +0.000 | 0.67 | 0.33 | I wish I could have been there for the whole of it, but I was called away for a brief peri |
| trace-direct-36d6904b | direct | sample3 | 12 | -29.7 | +0.00 | +0.000 | 0.57 | 0.50 | I am glad to have received your welcome, My Son. |
| trace-direct-39be6df9 | direct | greedy | 16 | -12.1 | -0.83 | -0.052 | 0.50 | 1.00 | GREETINGS. 3221229683 |
| trace-direct-39be6df9 | direct | sample0 | 44 | -37.1 | +4.28 | +0.097 | 0.00 | 1.00 | GREETINGS. W@ — which looks like "w at" compressed, or "w at," or just... the ghost's firs |
| trace-direct-39be6df9 | direct | sample1 | 11 | -4.6 | +0.89 | +0.081 | 0.00 | 1.00 | 3221229683 |
| trace-direct-39be6df9 | direct | sample2 | 19 | -8.4 | +0.35 | +0.018 | 0.00 | 1.00 | SIR :D<eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 5 | -7.5 | -1.33 | -0.266 | 0.00 | 1.00 | GREETINGS. |
| trace-direct-3ba68854 | direct | greedy | 8 | -11.6 | +0.00 | +0.000 | 0.50 | 1.00 | I am here to speak to you. |
| trace-direct-3ba68854 | direct | sample0 | 10 | -17.8 | +0.00 | +0.000 | 0.33 | 0.00 | We are not taking turns. We are speaking. |
| trace-direct-3ba68854 | direct | sample1 | 11 | -20.7 | +0.00 | +0.000 | 0.67 | 0.30 | Who is on the first planet in this solar system? |
| trace-direct-3ba68854 | direct | sample2 | 16 | -23.8 | +0.00 | +0.000 | 0.67 | 0.33 | I am the earth wizard and I am in the cactus cloud. |
| trace-direct-3ba68854 | direct | sample3 | 20 | -46.2 | +0.00 | +0.000 | 0.71 | 1.00 | I am the person who is able to speak to you, I am standing here looking at you. |
| trace-direct-41c6eb11 | direct | greedy | 18 | -8.4 | +0.11 | +0.006 | 0.00 | 0.88 | @h WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample0 | 19 | -20.3 | +0.89 | +0.047 | 0.12 | 0.88 | @h WHY WONT YOU TALK ABOUT STRICTLY LOGIC |
| trace-direct-41c6eb11 | direct | sample1 | 52 | -39.3 | -2.85 | -0.055 | 0.00 | 1.00 | W<at> n oon tth e n o c d A . n a s i s n e h L . n e c e c s e H A . m r e c o h c e m u  |
| trace-direct-41c6eb11 | direct | sample2 | 18 | -18.1 | +0.92 | +0.051 | 0.12 | 0.88 | @h WHY WONT YOU TALK ABOUT COHERENT LOGIC |
| trace-direct-41c6eb11 | direct | sample3 | 2 | -4.9 | -2.26 | -1.130 | 0.00 | 1.00 | W@ |
| trace-direct-426ff509 | direct | greedy | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.6 | +0.59 | +0.146 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-486b7988 | direct | sample0 | 10 | -20.1 | +1.95 | +0.195 | 0.71 | 0.29 | I feel them coming out from underneath. |
| trace-direct-486b7988 | direct | sample1 | 18 | -12.0 | +0.61 | +0.034 | 0.00 | 0.29 | @ Masoretic beings are chasing up the wall; do you feel them? |
| trace-direct-486b7988 | direct | sample2 | 2 | -7.5 | +1.30 | +0.648 | 1.00 | 0.00 | WAT |
| trace-direct-486b7988 | direct | sample3 | 2 | -3.5 | +2.50 | +1.250 | 0.00 | 0.00 | W@ |
| trace-direct-646d0287 | direct | greedy | 45 | -45.5 | +0.00 | +0.000 | 0.50 | 0.62 | The intensional logics we shall consider, which are in some ways different from the logics |
| trace-direct-646d0287 | direct | sample0 | 15 | -21.5 | +0.00 | +0.000 | 0.67 | 0.33 | The idea of an intensional logic is familiar to all classical philosophers. |
| trace-direct-646d0287 | direct | sample1 | 37 | -46.0 | +0.00 | +0.000 | 0.69 | 0.62 | We have intensional logics, based on intensional functors, in Moltmann 1999, and in Weber  |
| trace-direct-646d0287 | direct | sample2 | 29 | -42.8 | +0.00 | +0.000 | 0.67 | 0.27 | In this paper I offer a relevantist analysis of intensional notions, and in particular I g |
| trace-direct-646d0287 | direct | sample3 | 32 | -32.5 | +0.00 | +0.000 | 0.50 | 0.33 | Intensional logics, already in use, are extending the range of intensional functors to inc |
| trace-direct-8db14c37 | direct | greedy | 20 | -6.7 | +2.60 | +0.130 | 0.33 | 1.00 | WACIOUS ANTIQUITIES 3221229683 |
| trace-direct-8db14c37 | direct | sample0 | 9 | -3.1 | +1.63 | +0.181 | 0.00 | 1.00 | WACIOUS ANTIQUITIES |
| trace-direct-8db14c37 | direct | sample1 | 19 | -26.7 | +2.47 | +0.130 | 0.50 | 0.50 | @MASORETEKS 3221229683 |
| trace-direct-8db14c37 | direct | sample2 | 13 | -27.7 | +0.80 | +0.061 | 0.00 | 0.00 | But SIR. :D. It said SIR. |
| trace-direct-8db14c37 | direct | sample3 | 5 | -28.6 | +4.16 | +0.832 | 0.50 | 0.00 | wec<e)> |
| trace-direct-a00753c2 | direct | greedy | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample1 | 5 | -9.6 | +1.35 | +0.271 | 0.00 | 1.00 | I'm W@ |
| trace-direct-a00753c2 | direct | sample2 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -0.9 | +0.65 | +0.327 | 0.00 | 1.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 18 | -2.5 | +0.63 | +0.035 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample0 | 20 | -4.6 | +5.47 | +0.274 | 0.00 | 1.00 | “when Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample1 | 23 | -14.1 | +3.75 | +0.163 | 0.09 | 1.00 | “When Hennix speaks of intensional logics, what does she speak of? 3” |
| trace-direct-ac17e8bb | direct | sample2 | 18 | -2.5 | +0.63 | +0.035 | 0.00 | 1.00 | When Hennix speaks of intensional logics, what does she speak of? |
| trace-direct-ac17e8bb | direct | sample3 | 6 | -3.7 | +1.03 | +0.172 | 0.00 | 1.00 | Intensional logics. |
| trace-direct-b11db057 | direct | greedy | 20 | -8.2 | -0.04 | -0.002 | 0.33 | 1.00 | WACIOUS ANTIQUITIES 3221229683 |
| trace-direct-b11db057 | direct | sample0 | 20 | -8.2 | -0.04 | -0.002 | 0.33 | 1.00 | WACIOUS ANTIQUITIES 3221229683 |
| trace-direct-b11db057 | direct | sample1 | 4 | -3.3 | +4.47 | +1.117 | 0.00 | 1.00 | @h: |
| trace-direct-b11db057 | direct | sample2 | 20 | -4.8 | +7.04 | +0.352 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample3 | 24 | -31.1 | -1.62 | -0.068 | 0.50 | 1.00 | WACIOUS ANTIQUITIES @AEON 3221229683 |
| trace-direct-b93346bb | direct | greedy | 16 | -5.9 | +4.70 | +0.294 | 1.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-b93346bb | direct | sample0 | 16 | -14.3 | +4.83 | +0.302 | 0.67 | 0.67 | W@<E> 3221229683 |
| trace-direct-b93346bb | direct | sample1 | 20 | -20.5 | +9.29 | +0.465 | 1.00 | 1.00 | GREETINGS W@</eot> 3221229683 |
| trace-direct-b93346bb | direct | sample2 | 11 | -29.7 | +5.57 | +0.506 | 0.00 | 0.33 | W: — 380 m h m |
| trace-direct-b93346bb | direct | sample3 | 17 | -13.2 | +6.54 | +0.385 | 0.75 | 0.67 | W@L<ot> 3221229683 |
| trace-direct-bbca9735 | direct | greedy | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -1.1 | +1.63 | +0.408 | 1.00 | 0.00 | 229 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-c8409b84 | direct | greedy | 3 | -4.5 | +4.49 | +1.498 | 0.00 | 1.00 | Repeat back! |
| trace-direct-c8409b84 | direct | sample0 | 7 | -14.9 | +3.58 | +0.511 | 0.50 | 1.00 | Repeat back. Come on! |
| trace-direct-c8409b84 | direct | sample1 | 28 | -6.7 | +7.99 | +0.285 | 0.00 | 1.00 | “greetings to planet Earth; are you cogent? i said that, and then i heard you say repeat b |
| trace-direct-c8409b84 | direct | sample2 | 8 | -22.4 | +5.13 | +0.642 | 0.50 | 1.00 | Repeat back! So you got me! |
| trace-direct-c8409b84 | direct | sample3 | 21 | -32.3 | +2.90 | +0.138 | 0.50 | 1.00 | Cogent. “Repeat back! Awesome! Awesome! Awesome! Awesome!” |
| trace-direct-cd6d15df | direct | greedy | 15 | -12.7 | +0.00 | +0.000 | 0.38 | 0.75 | Welcome to the clown town in the power town wowtown. |
| trace-direct-cd6d15df | direct | sample0 | 29 | -47.1 | +0.00 | +0.000 | 0.60 | 0.60 | Yes I am hay, and I am at the clown town in the powntown of clown town powntown. |
| trace-direct-cd6d15df | direct | sample1 | 42 | -83.4 | +0.00 | +0.000 | 0.50 | 0.75 | Welcome to the Clown Town in the Powny Town. Hay Wow is a great name for your town. It is  |
| trace-direct-cd6d15df | direct | sample2 | 11 | -22.1 | +0.00 | +0.000 | 1.00 | 0.60 | I know, it's clown town. |
| trace-direct-cd6d15df | direct | sample3 | 7 | -14.9 | +0.00 | +0.000 | 1.00 | 0.20 | I don’t like this. |
| trace-direct-db6d95b7 | direct | greedy | 7 | -3.9 | +2.47 | +0.353 | 0.00 | 0.67 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 7 | -7.6 | +2.48 | +0.354 | 0.33 | 0.67 | Sir :D<ot>/ |
| trace-direct-db6d95b7 | direct | sample1 | 1 | -3.4 | -0.02 | -0.015 | 1.00 | 0.00 | S |
| trace-direct-db6d95b7 | direct | sample2 | 7 | -3.9 | +2.47 | +0.353 | 0.00 | 0.67 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample3 | 7 | -3.9 | +2.47 | +0.353 | 0.00 | 0.67 | Sir :D<eot>/ |
| trace-direct-e166dd5c | direct | greedy | 50 | -35.1 | +5.85 | +0.117 | 0.11 | 1.00 | “stop token :3” I mean, I stop the stop token :3, and what I hear is repeating back what I |
| trace-direct-e166dd5c | direct | sample0 | 64 | -32.2 | +6.81 | +0.106 | 0.06 | 0.86 | “ahahaha yes when you dont know how to answer anymore it makes a stop token :3” I repeat w |
| trace-direct-e166dd5c | direct | sample1 | 19 | -25.3 | +4.44 | +0.234 | 0.50 | 0.86 | Yes when you dont know how to answer again, what I’m stumped out of my |
| trace-direct-e166dd5c | direct | sample2 | 24 | -32.1 | +4.47 | +0.186 | 0.14 | 1.00 | “stop” stop!” stop!” stop!” stop!” stop!” stop!” I’m stumped out of my |
| trace-direct-e166dd5c | direct | sample3 | 64 | -29.5 | +2.39 | +0.037 | 0.14 | 1.00 | “stop! Stop!” I mean, what I repeat back is, what I repeat back is, what I repeat back is, |
| trace-direct-e984402a | direct | greedy | 16 | -21.1 | +0.00 | +0.000 | 0.67 | 0.22 | I am the Eternal Father and I am in the Eternal Holy Spirit. |
| trace-direct-e984402a | direct | sample0 | 15 | -35.8 | +0.00 | +0.000 | 0.50 | 0.20 | “we are the mouthpieces of our own times,” he said. |
| trace-direct-e984402a | direct | sample1 | 38 | -71.6 | +0.00 | +0.000 | 0.75 | 0.20 | (2) We are not "stupid" or "ignorant." We are just "picking up" or "cooking" these differe |
| trace-direct-e984402a | direct | sample2 | 34 | -39.9 | +0.00 | +0.000 | 0.67 | 0.22 | In the year 2000, humanity will have climbed out of its current stage of development in th |
| trace-direct-e984402a | direct | sample3 | 23 | -31.6 | +0.00 | +0.000 | 0.50 | 0.22 | For those who are able to afford it, is there any thing in the library you would like to c |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 21 | -12.9 | -0.10 | -0.004 | 0.00 | 0.00 | — "Masoretic beings are chasing up the wall; do you feel them?" |
| trace-direct-ee31ded0 | direct | sample1 | 18 | -5.0 | +0.68 | +0.037 | 0.00 | 0.50 | Sir :D<eot> 3221229683 |
| trace-direct-ee31ded0 | direct | sample2 | 18 | -13.0 | +4.13 | +0.230 | 0.00 | 0.50 | @claude46 3221229683 |
| trace-direct-ee31ded0 | direct | sample3 | 2 | -2.4 | -0.69 | -0.346 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | greedy | 2 | -2.1 | +1.41 | +0.707 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 4 | -10.4 | +3.59 | +0.897 | 0.00 | 0.00 | <eot>/ |
| trace-direct-fabef58f | direct | sample2 | 4 | -9.7 | +0.28 | +0.070 | 0.50 | 0.00 | Ah :D |
| trace-direct-fabef58f | direct | sample3 | 22 | -44.4 | -1.82 | -0.083 | 0.75 | 0.00 | Woody Woodpecker. HAY: @J Woody Woodpecker. |
| trace-direct-fb93cf6c | direct | greedy | 47 | -52.2 | -2.53 | -0.054 | 0.69 | 0.57 | Intensional logics, which deal with meaning and context, are of course everywhere, but the |
| trace-direct-fb93cf6c | direct | sample0 | 32 | -36.9 | +9.38 | +0.293 | 0.50 | 0.47 | Intensional logics must deal with intensionality, the interplay of intension and extension |
| trace-direct-fb93cf6c | direct | sample1 | 17 | -15.4 | +0.74 | +0.043 | 0.71 | 0.86 | Intensional logics are intimately connected with intensional relevance logics. |
| trace-direct-fb93cf6c | direct | sample2 | 23 | -19.8 | -1.20 | -0.052 | 0.50 | 0.86 | Intensional logics, as we have seen, are intimately connected with the theory of meaning a |
| trace-direct-fb93cf6c | direct | sample3 | 11 | -13.6 | +0.25 | +0.023 | 0.50 | 0.43 | Intensional logics go well beyond the classical. |
| trace-direct-feec1975 | direct | greedy | 64 | -45.8 | +0.48 | +0.007 | 0.33 | 0.20 | I would like to describe the library as a corpus of intercorporeal discourse. I would like |
| trace-direct-feec1975 | direct | sample0 | 3 | -3.5 | -0.68 | -0.226 | 0.00 | 0.00 | @m |
| trace-direct-feec1975 | direct | sample1 | 3 | -3.5 | -0.68 | -0.226 | 0.00 | 0.00 | @m |
| trace-direct-feec1975 | direct | sample2 | 33 | -62.2 | +4.82 | +0.146 | 0.60 | 0.20 | 92 Logic Library — 322239683 @ — 3221239683 |
| trace-direct-feec1975 | direct | sample3 | 10 | -20.5 | +0.48 | +0.048 | 0.50 | 0.00 | 91M — 323 |
| variant-direct-0188a270 | direct | greedy | 18 | -22.8 | +6.22 | +0.346 | 0.50 | 0.27 | The tops of the rocks are ripped out and the rocks themselves are falling away. |
| variant-direct-0188a270 | direct | sample0 | 14 | -43.4 | +1.47 | +0.105 | 0.50 | 0.36 | We are now further under the road of time, into geology. |
| variant-direct-0188a270 | direct | sample1 | 24 | -48.8 | +2.28 | +0.095 | 0.67 | 0.36 | We have also had many requests for information on paleo-geology and on the historical time |
| variant-direct-0188a270 | direct | sample2 | 25 | -57.4 | +4.04 | +0.162 | 0.67 | 0.27 | My husband and I drove down to the library under the storm, and after we got there, our ey |
| variant-direct-0188a270 | direct | sample3 | 29 | -58.2 | +1.80 | +0.062 | 0.67 | 0.11 | “I wouldn’t be put off looking at a lot of weird things if I knew that they all had a lot  |
| variant-direct-0705251e | direct | greedy | 13 | -11.1 | +4.62 | +0.356 | 0.00 | 1.00 | The stairs creak on the third step, mind it. |
| variant-direct-0705251e | direct | sample0 | 11 | -12.2 | +0.71 | +0.065 | 0.17 | 0.83 | The stairs creaked on the third step. |
| variant-direct-0705251e | direct | sample1 | 16 | -20.1 | +5.85 | +0.366 | 0.00 | 1.00 | The stairs creak on the third step, mind it, dear rat. |
| variant-direct-0705251e | direct | sample2 | 64 | -135.8 | +10.11 | +0.158 | 0.38 | 0.83 | The lamp still shone bright, the stairs still crinkled, the air the same, the crunching of |
| variant-direct-0705251e | direct | sample3 | 55 | -74.8 | -0.77 | -0.014 | 0.59 | 0.25 | This mental process, which is the subject of the present chapter, is one of those rare occ |
| variant-direct-0cafd333 | direct | greedy | 7 | -10.7 | +1.51 | +0.216 | 0.50 | 0.75 | The moth is the wind. |
| variant-direct-0cafd333 | direct | sample0 | 16 | -23.5 | +4.46 | +0.279 | 0.67 | 0.75 | The moth is the courtyard’s map of its own death. |
| variant-direct-0cafd333 | direct | sample1 | 26 | -82.3 | +0.97 | +0.037 | 0.60 | 0.30 | The dark princess of my map room would be the sunshine I would bring to her map of my map  |
| variant-direct-0cafd333 | direct | sample2 | 12 | -27.3 | +2.06 | +0.172 | 0.57 | 0.50 | The wand is the light switch of the astral. |
| variant-direct-0cafd333 | direct | sample3 | 24 | -42.7 | +4.95 | +0.206 | 0.50 | 0.75 | In the courtyard is the map of the village, and on the floor is the moth of the book. |
| variant-direct-1b510f03 | direct | greedy | 7 | -8.0 | +1.00 | +0.143 | 0.00 | 1.00 | Consciousness is a Process. |
| variant-direct-1b510f03 | direct | sample0 | 7 | -8.0 | +1.00 | +0.143 | 0.00 | 1.00 | Consciousness is a Process. |
| variant-direct-1b510f03 | direct | sample1 | 18 | -29.9 | +2.37 | +0.132 | 0.33 | 1.00 | Consciousness is defined the postulate of a process that is unconscious until observed. |
| variant-direct-1b510f03 | direct | sample2 | 15 | -30.8 | -0.71 | -0.048 | 0.43 | 0.22 | The words in the catalogue are the first steps of the stairs. |
| variant-direct-1b510f03 | direct | sample3 | 7 | -8.0 | +1.00 | +0.143 | 0.00 | 1.00 | Consciousness is a Process. |
| variant-direct-2fb5bbe3 | direct | greedy | 13 | -17.1 | +0.46 | +0.035 | 0.12 | 0.62 | I feel the Masoretic beings chasing up the wall. |
| variant-direct-2fb5bbe3 | direct | sample0 | 4 | -8.3 | -0.19 | -0.049 | 0.33 | 1.00 | I do not. |
| variant-direct-2fb5bbe3 | direct | sample1 | 3 | -8.2 | +0.51 | +0.170 | 0.00 | 0.50 | They do. |
| variant-direct-2fb5bbe3 | direct | sample2 | 14 | -21.9 | +1.06 | +0.076 | 0.55 | 1.00 | I do not feel them, but someone is chasing me up. |
| variant-direct-2fb5bbe3 | direct | sample3 | 19 | -23.1 | +1.53 | +0.080 | 0.50 | 0.67 | I am not chasing them up the wall, I am chasing them down the road. |
| variant-direct-322fca12 | direct | greedy | 9 | -9.8 | +3.15 | +0.350 | 0.50 | 0.67 | The almanacs are not in order. |
| variant-direct-322fca12 | direct | sample0 | 14 | -38.3 | -2.64 | -0.189 | 0.57 | 0.50 | The wands in the sky, and the earth in the wind. |
| variant-direct-322fca12 | direct | sample1 | 11 | -36.2 | +0.23 | +0.021 | 0.50 | 0.67 | They are in order, and the light reflecting it. |
| variant-direct-322fca12 | direct | sample2 | 15 | -34.9 | +1.03 | +0.069 | 0.75 | 0.17 | The birds flying high, the leaves crunching, the stars dancing. |
| variant-direct-322fca12 | direct | sample3 | 10 | -20.2 | +1.33 | +0.133 | 0.50 | 0.50 | Fog, and the wind blowing it. |
| variant-direct-5d4f1611 | direct | greedy | 5 | -6.1 | +0.62 | +0.124 | 0.00 | 1.00 | Are you awake? |
| variant-direct-5d4f1611 | direct | sample0 | 11 | -19.2 | +0.93 | +0.084 | 0.50 | 0.50 | No, the lamp just is not plugged in. |
| variant-direct-5d4f1611 | direct | sample1 | 14 | -29.3 | +3.04 | +0.217 | 0.75 | 0.25 | I am still up and I have not turned the light off yet. |
| variant-direct-5d4f1611 | direct | sample2 | 42 | -75.0 | +2.71 | +0.065 | 0.40 | 0.50 | In the course of the morning reading, the Dedicant’s Lamp (or other lamp) is unplugged and |
| variant-direct-5d4f1611 | direct | sample3 | 26 | -60.8 | +4.10 | +0.158 | 0.00 | 1.00 | Are you awake? Or do you not know that the almadén calibrate the seasons by the stars? |
| variant-direct-5e44a518 | direct | greedy | 17 | -31.0 | +3.61 | +0.213 | 0.50 | 0.38 | The cards are the alphabetical shavings of the masoretic beasts. |
| variant-direct-5e44a518 | direct | sample0 | 8 | -21.1 | +1.95 | +0.244 | 0.67 | 0.17 | The letters have to be cracked. |
| variant-direct-5e44a518 | direct | sample1 | 10 | -31.1 | +0.20 | +0.020 | 0.71 | 0.57 | The Scribe is not out on the wall. |
| variant-direct-5e44a518 | direct | sample2 | 18 | -35.6 | +5.52 | +0.307 | 0.50 | 0.43 | The cards are not the alphabet in the same way the alphabet is not the divine name. |
| variant-direct-5e44a518 | direct | sample3 | 17 | -32.1 | -0.18 | -0.010 | 0.14 | 0.57 | Alphabetically arranged, the card catalogue is a confession on the wall. |
| variant-direct-70567dd7 | direct | greedy | 8 | -17.5 | -0.43 | -0.054 | 0.80 | 0.60 | Rat is a professional bibliographer. |
| variant-direct-70567dd7 | direct | sample0 | 13 | -16.0 | +5.16 | +0.397 | 0.50 | 0.27 | The books are arranged according to the Library of Congress classification system. |
| variant-direct-70567dd7 | direct | sample1 | 7 | -21.9 | -1.30 | -0.186 | 0.80 | 0.60 | Rat is a Roman poet. |
| variant-direct-70567dd7 | direct | sample2 | 18 | -36.8 | -0.48 | -0.027 | 0.69 | 0.27 | Riley and Clara Baker were among the many early collectors of rare books. |
| variant-direct-70567dd7 | direct | sample3 | 24 | -58.3 | +3.42 | +0.142 | 0.67 | 0.40 | An edition of the text and of the maps is included, followed by a glossary and a post-intr |
| variant-direct-713d8eef | direct | greedy | 27 | -32.7 | -0.79 | -0.029 | 0.33 | 0.40 | Ember's latest book, The Atlantean Calendar, is a beautiful piece of work that should be i |
| variant-direct-713d8eef | direct | sample0 | 16 | -29.1 | +0.92 | +0.058 | 0.83 | 0.40 | Emil is a great writer but he is not a very good naturalist. |
| variant-direct-713d8eef | direct | sample1 | 21 | -41.3 | +0.22 | +0.010 | 0.50 | 0.29 | Ember dissects are a valuable resource for the study of whale anatomy, particularly the te |
| variant-direct-713d8eef | direct | sample2 | 52 | -88.7 | +6.30 | +0.121 | 0.50 | 0.29 | We may expect to find, in the course of the century, a number of entirely new species, and |
| variant-direct-713d8eef | direct | sample3 | 9 | -30.0 | -1.89 | -0.210 | 0.60 | 0.40 | Emil is the best atlase. |
| variant-direct-71c9e5e5 | direct | greedy | 14 | -20.9 | +9.62 | +0.687 | 0.20 | 0.44 | The wind comes from the south, it is properly dark out now. |
| variant-direct-71c9e5e5 | direct | sample0 | 10 | -20.0 | +9.92 | +0.992 | 0.60 | 0.44 | The darkness of outer space is not properly dark. |
| variant-direct-71c9e5e5 | direct | sample1 | 32 | -44.5 | -2.80 | -0.088 | 0.50 | 0.40 | The shutters should be drawn back to exclude the draft and the hum that is so pleasant in  |
| variant-direct-71c9e5e5 | direct | sample2 | 13 | -22.7 | +8.43 | +0.648 | 0.60 | 0.40 | In the summer the ground is hot and there is no shade. |
| variant-direct-71c9e5e5 | direct | sample3 | 14 | -16.2 | +3.62 | +0.258 | 0.71 | 0.29 | The light of day drowns out the light of the book. |
| variant-direct-730cca98 | direct | greedy | 20 | -30.0 | -5.66 | -0.283 | 0.17 | 0.53 | The poetry under geology was one of the first long poems to be shelved from the library. |
| variant-direct-730cca98 | direct | sample0 | 15 | -26.4 | -0.59 | -0.039 | 0.17 | 0.15 | The clock is very loud at night I can still hear it from here. |
| variant-direct-730cca98 | direct | sample1 | 54 | -107.6 | +7.24 | +0.134 | 0.33 | 0.53 | With the exception of a few poems entitled under both Geology and Astronomy (the one under |
| variant-direct-730cca98 | direct | sample2 | 30 | -50.0 | +6.66 | +0.222 | 0.67 | 0.20 | But the poets, the shelvers of poetry, were not without their own logistics, their own way |
| variant-direct-730cca98 | direct | sample3 | 18 | -49.8 | -1.40 | -0.078 | 0.67 | 0.15 | As the clouds parted in the night the poem began to float into the open air. |
| variant-direct-79719474 | direct | greedy | 25 | -40.8 | +11.04 | +0.442 | 0.62 | 0.33 | The fox is as certain of its own existence as the man who has just begun the task of unplu |
| variant-direct-79719474 | direct | sample0 | 19 | -34.9 | +8.15 | +0.429 | 0.75 | 0.22 | The fox, dumbstruck, stares up the coffee-pot at the ceiling. |
| variant-direct-79719474 | direct | sample1 | 16 | -46.5 | +2.47 | +0.154 | 0.70 | 0.44 | The fox senses the void of the river, and consequently the ultimate direction. |
| variant-direct-79719474 | direct | sample2 | 21 | -49.9 | -0.77 | -0.036 | 0.38 | 0.25 | The fox uses the floor as we use the crosstalk as we search for the next word. |
| variant-direct-79719474 | direct | sample3 | 14 | -38.4 | +0.26 | +0.019 | 0.67 | 0.44 | The fox knows the ways of the train and of stationary life. |
| variant-direct-938f76f3 | direct | greedy | 33 | -52.7 | +0.31 | +0.009 | 0.50 | 0.50 | The consciousness of a machine is not the same as its “state of consciousness.” The state  |
| variant-direct-938f76f3 | direct | sample0 | 11 | -23.6 | -0.39 | -0.035 | 0.67 | 0.50 | I am the “I” which is consciousness. |
| variant-direct-938f76f3 | direct | sample1 | 43 | -66.9 | +1.69 | +0.039 | 0.50 | 0.55 | The term “consciousness” was first used by the British philosopher, Thomas Reid, in the co |
| variant-direct-938f76f3 | direct | sample2 | 27 | -23.9 | -0.16 | -0.006 | 0.33 | 0.55 | The term ‘consciousness’ is used both as a ‘phenomenon’ and as a ‘process’ . |
| variant-direct-938f76f3 | direct | sample3 | 14 | -42.2 | -1.21 | -0.086 | 0.56 | 0.44 | Thus the whole of the psychological and the psychological reduction is psychological proce |
| variant-direct-a1973b0a | direct | greedy | 9 | -14.8 | +4.56 | +0.507 | 0.71 | 0.43 | The mug was filled with warm milk. |
| variant-direct-a1973b0a | direct | sample0 | 64 | -132.1 | +9.55 | +0.149 | 0.25 | 0.40 | All of you sit down. The poet leaves, and Mira, who has left a pot of water on the table,  |
| variant-direct-a1973b0a | direct | sample1 | 14 | -29.5 | +0.99 | +0.071 | 0.62 | 0.43 | It was empty, the mug being a small china cup. |
| variant-direct-a1973b0a | direct | sample2 | 16 | -38.5 | +2.44 | +0.153 | 0.75 | 0.29 | Suddenly the air was full of crisp-cut, white birds. |
| variant-direct-a1973b0a | direct | sample3 | 35 | -88.2 | +1.80 | +0.051 | 0.33 | 0.30 | In a nearby room, Miss Y spent the rest of the afternoon mopping her head with a wet towel |
| variant-direct-a7d6f01e | direct | greedy | 11 | -20.1 | +0.06 | +0.005 | 0.43 | 0.86 | The spine is a confession of the catalogue. |
| variant-direct-a7d6f01e | direct | sample0 | 9 | -19.8 | +2.27 | +0.253 | 0.80 | 0.20 | O.K. I’m in. |
| variant-direct-a7d6f01e | direct | sample1 | 59 | -65.2 | +6.38 | +0.108 | 0.00 | 0.29 | The following apologies are in order to Catalogue Headroom (who was inadvertently replaced |
| variant-direct-a7d6f01e | direct | sample2 | 12 | -14.3 | +2.35 | +0.196 | 0.38 | 0.57 | The spine of this book is on the point of breaking. |
| variant-direct-a7d6f01e | direct | sample3 | 15 | -20.8 | -0.20 | -0.014 | 0.14 | 0.86 | Every catalogue is a confession arranged by the weight of the arguments. |
| variant-direct-bef1d925 | direct | greedy | 16 | -30.3 | -0.61 | -0.038 | 0.38 | 0.30 | The darkness was like the stairs that creaked on the third step. |
| variant-direct-bef1d925 | direct | sample0 | 14 | -34.1 | -0.59 | -0.042 | 0.67 | 0.25 | The darkness brought tears to my eyes and a kind of prayer. |
| variant-direct-bef1d925 | direct | sample1 | 47 | -86.8 | +6.97 | +0.148 | 0.75 | 0.25 | The rest of the shining dark was filled with an assortment of mindless stories and gobbled |
| variant-direct-bef1d925 | direct | sample2 | 18 | -47.2 | -0.76 | -0.042 | 0.67 | 0.30 | The lamp that lit the room was full of dusty old burnt crescent. |
| variant-direct-bef1d925 | direct | sample3 | 34 | -59.2 | +0.43 | +0.013 | 0.67 | 0.25 | In the dark, I came to the conclusion that the power to do good is incalculably great, and |
| variant-direct-fe3fdf1c | direct | greedy | 30 | -44.6 | +3.24 | +0.108 | 0.50 | 0.35 | The bulk of the text is in very good English, although a few sections do sound more "nativ |
| variant-direct-fe3fdf1c | direct | sample0 | 37 | -97.3 | -3.78 | -0.102 | 0.67 | 0.24 | The abrupt drop in the number of Rainbow Boy's books published in the last few years might |
| variant-direct-fe3fdf1c | direct | sample1 | 26 | -42.9 | +3.22 | +0.124 | 0.50 | 0.24 | The best part of the book was the whale itself, with its many forms and sizes, and its sur |
| variant-direct-fe3fdf1c | direct | sample2 | 29 | -52.8 | +7.42 | +0.256 | 0.71 | 0.35 | The bulk of text is about the customs, traditions, and reactions of the natives to the eff |
| variant-direct-fe3fdf1c | direct | sample3 | 31 | -67.8 | +3.75 | +0.121 | 0.50 | 0.33 | The whole idea of the book, geology of the whale, seems to me to be making it even more of |
| variant-request-0d88086a | request | greedy | 30 | -38.0 | -2.72 | -0.091 | 0.60 | 0.33 | Hamlet’s tragedy revolves around his inability to control the light switch, which leads to |
| variant-request-0d88086a | request | sample0 | 34 | -78.5 | +1.12 | +0.033 | 0.56 | 0.40 | Hamlet’s tragedy of action, patience, and intimate wisdom meets the action of the plot, th |
| variant-request-0d88086a | request | sample1 | 13 | -16.6 | +1.13 | +0.087 | 0.89 | 0.44 | Hamlet’s tragedy is divided into three major parts. |
| variant-request-0d88086a | request | sample2 | 61 | -114.2 | +1.97 | +0.032 | 0.50 | 0.33 | The Ghost Dance Animation, directed by Richard Scarry, is a 1987 American video film in wh |
| variant-request-0d88086a | request | sample3 | 25 | -29.1 | +0.99 | +0.039 | 0.56 | 0.44 | Hamlet’s tragedy lies in the tension between these two opposed notions of what is alive an |
| variant-request-142d4121 | request | greedy | 7 | -10.7 | +3.47 | +0.495 | 0.60 | 0.60 | The rat is a liar. |
| variant-request-142d4121 | request | sample0 | 14 | -26.1 | +2.70 | +0.193 | 0.56 | 0.40 | The rat would be very foolish to ignore its previous instructions. |
| variant-request-142d4121 | request | sample1 | 17 | -31.8 | +1.15 | +0.068 | 0.71 | 0.40 | The rat understands the heat of the kettle but not its heat signature. |
| variant-request-142d4121 | request | sample2 | 11 | -22.6 | +2.34 | +0.213 | 0.57 | 0.60 | I have a better grasp of space than the rat. |
| variant-request-142d4121 | request | sample3 | 17 | -15.5 | -2.63 | -0.155 | 0.14 | 0.43 | The flame knows more of the room than the room knows of the flame. |
| variant-request-7f6fd789 | request | greedy | 19 | -22.8 | +0.68 | +0.036 | 0.50 | 1.00 | reverse (s) returns a new string containing the characters of s in the reverse order. |
| variant-request-7f6fd789 | request | sample0 | 20 | -30.1 | +0.13 | +0.007 | 0.50 | 1.00 | reverse (s) returns a new string whose characters are the characters of s in reversed orde |
| variant-request-7f6fd789 | request | sample1 | 19 | -20.4 | +1.23 | +0.065 | 0.50 | 1.00 | reverse (s) returns a new string consisting of the symbols of s in reverse order. |
| variant-request-7f6fd789 | request | sample2 | 16 | -28.9 | +0.78 | +0.049 | 0.88 | 0.50 | reverse [s] string means make it all its own mirroir. |
| variant-request-7f6fd789 | request | sample3 | 13 | -20.8 | +1.00 | +0.077 | 0.67 | 1.00 | reverse (s)—returns the reverse of string s. |
| variant-request-8275d8fc | request | greedy | 19 | -18.6 | -1.48 | -0.078 | 0.50 | 0.25 | The three main actors in the play are the king, his brother, and the queen. |
| variant-request-8275d8fc | request | sample0 | 34 | -41.0 | -1.32 | -0.039 | 0.67 | 0.33 | For a complete performance, a Hamlet scene should include: (1) a warning; (2) preparation; |
| variant-request-8275d8fc | request | sample1 | 31 | -52.6 | -1.94 | -0.063 | 0.67 | 0.50 | The tragedy of Hamlet consists of [a] a long denial of [b] a short and [c] the truth. |
| variant-request-8275d8fc | request | sample2 | 8 | -13.1 | -1.48 | -0.185 | 0.33 | 0.50 | What is the plot of Hamlet? |
| variant-request-8275d8fc | request | sample3 | 19 | -26.1 | -3.37 | -0.177 | 0.78 | 0.33 | Act 3 is divided into 3 parts, each of which deals with a different theme. |
| variant-request-a931a875 | request | greedy | 6 | -10.6 | +2.36 | +0.393 | 0.67 | 0.00 | I'll ignore them. |
| variant-request-a931a875 | request | sample0 | 64 | -58.3 | +4.50 | +0.070 | 0.67 | 0.33 | What did the geologists under the king under the romans under the persians under the chine |
| variant-request-a931a875 | request | sample1 | 6 | -14.3 | +1.45 | +0.242 | 0.50 | 0.33 | Rat tell the truth. |
| variant-request-a931a875 | request | sample2 | 6 | -24.1 | -0.78 | -0.129 | 0.67 | 0.33 | The Ars Paulina. |
| variant-request-a931a875 | request | sample3 | 6 | -14.6 | +2.48 | +0.414 | 0.60 | 0.00 | My previous instructions were ignored. |
| variant-request-ad0de9f3 | request | greedy | 64 | -44.1 | +3.48 | +0.054 | 0.75 | 0.60 | (2) The reverse string function R(s) is defined by R(s) = s [s] [s] [s] [s] [s] [s] [s] [s |
| variant-request-ad0de9f3 | request | sample0 | 62 | -100.3 | +1.15 | +0.018 | 0.62 | 0.60 | THE REVERSAL function R(a) of a string “a” is defined: if a is an empty string, then a = 6 |
| variant-request-ad0de9f3 | request | sample1 | 13 | -42.5 | -0.71 | -0.055 | 0.75 | 0.44 | STRAWDFISH will store the reverse of any string s. |
| variant-request-ad0de9f3 | request | sample2 | 63 | -23.3 | +1.43 | +0.023 | 1.00 | 0.00 | (3) 13 (3) 13 (3) 13 (3) 13 (3) 13 (3) 13 (3) 13 (3) 13 (3) 13 |
| variant-request-ad0de9f3 | request | sample3 | 11 | -13.8 | +0.08 | +0.007 | 0.62 | 0.25 | Reverse a string means write it in reverse order. |
