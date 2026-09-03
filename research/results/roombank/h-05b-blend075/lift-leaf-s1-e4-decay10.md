# Context lift: h-05b-blend075 under leaf-s1-e4-decay10

529 replies (140 on states with fewer than two preceding turns, excluded from the summary); lift = log p(reply | true history) - mean of 3 shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap with the last 8 room lines, the frame, and h's own lines.

| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 389 | +0.197 | +0.226 | 0.60 | +0.0191 | 0.399 | 0.601 | 0.230 | 0.481 | 0.49 |
| mode greedy | 78 | +0.236 | +0.097 | 0.58 | +0.0090 | 0.354 | 0.646 | 0.288 | 0.550 | 0.53 |
| mode sample | 311 | +0.186 | +0.298 | 0.60 | +0.0216 | 0.410 | 0.590 | 0.215 | 0.463 | 0.48 |
| kind direct | 174 | +0.220 | +0.220 | 0.60 | +0.0298 | 0.388 | 0.612 | 0.321 | 0.441 | 0.55 |
| kind ambient | 35 | +0.648 | +0.726 | 0.77 | +0.0376 | 0.417 | 0.583 | 0.000 | 0.496 | 0.31 |
| kind callback | 60 | +0.156 | +0.124 | 0.55 | +0.0187 | 0.357 | 0.643 | 0.090 | 0.514 | 0.57 |
| kind disagreement | 40 | -0.475 | +0.368 | 0.65 | -0.0424 | 0.335 | 0.665 | 0.524 | 0.672 | 0.60 |
| kind joke | 25 | -0.113 | -0.059 | 0.36 | -0.0039 | 0.428 | 0.572 | 0.129 | 0.436 | 0.44 |
| kind silence | 25 | +0.843 | +0.710 | 0.72 | +0.0583 | 0.383 | 0.617 | 0.000 | 0.547 | 0.36 |
| kind request | 30 | +0.230 | +0.118 | 0.53 | +0.0039 | 0.601 | 0.400 | 0.131 | 0.353 | 0.20 |

| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| observatory-direct-9e3185b9 | direct | greedy | 7 | -10.0 | +0.00 | +0.000 | 0.00 | 0.80 | The observatory is open now. |
| observatory-direct-9e3185b9 | direct | sample0 | 10 | -24.3 | +0.00 | +0.000 | 0.43 | 0.86 | The Observatory is currently open to the public. |
| observatory-direct-9e3185b9 | direct | sample1 | 63 | -162.0 | +0.00 | +0.000 | 0.50 | 0.43 | I am fully aware that there are many who will think it odd at first that we should be able |
| observatory-direct-9e3185b9 | direct | sample2 | 14 | -60.9 | +0.00 | +0.000 | 0.43 | 0.86 | The Observatory is currently open and accepting scientific research and public observation |
| observatory-direct-9e3185b9 | direct | sample3 | 7 | -10.0 | +0.00 | +0.000 | 0.00 | 0.80 | The observatory is open now. |
| scenario-ambient-0ecb3f23 | ambient | greedy | 10 | -27.9 | +0.00 | +0.000 | 0.43 | 0.43 | The word for that fear is boredom. |
| scenario-ambient-0ecb3f23 | ambient | sample0 | 17 | -48.1 | +0.00 | +0.000 | 0.80 | 0.30 | If you want to finish a book, it's called book-fever. |
| scenario-ambient-0ecb3f23 | ambient | sample1 | 19 | -50.9 | +0.00 | +0.000 | 0.40 | 0.43 | I don't know of a word for this – it's just the feeling. |
| scenario-ambient-0ecb3f23 | ambient | sample2 | 26 | -74.6 | +0.00 | +0.000 | 0.60 | 0.43 | Finish: a word that means “to feel the pressure of the completion of a task, the end of a  |
| scenario-ambient-0ecb3f23 | ambient | sample3 | 47 | -100.9 | +0.00 | +0.000 | 0.50 | 0.43 | The Book of Particulars is a word which means "specific knowledge," "direct knowledge," "i |
| scenario-ambient-103e3d78 | ambient | greedy | 8 | -23.2 | -0.12 | -0.015 | 0.50 | 0.43 | The other three are waiting for you. |
| scenario-ambient-103e3d78 | ambient | sample0 | 23 | -62.0 | +0.73 | +0.032 | 0.50 | 0.43 | If you've read all the books on this subject, what are the other books on the shelves like |
| scenario-ambient-103e3d78 | ambient | sample1 | 13 | -42.9 | +1.39 | +0.107 | 0.67 | 0.33 | The next page continues the story of the ghost in the garden. |
| scenario-ambient-103e3d78 | ambient | sample2 | 29 | -68.1 | +0.74 | +0.025 | 0.00 | 0.14 | Before he goes to bed, he should ask himself the following questions: 1. Will I be dead or |
| scenario-ambient-103e3d78 | ambient | sample3 | 4 | -10.1 | +0.77 | +0.192 | 0.00 | 0.33 | One more page. |
| scenario-ambient-202a37a7 | ambient | greedy | 12 | -34.0 | +0.73 | +0.060 | 0.50 | 0.57 | The geology book is a little weird, too. |
| scenario-ambient-202a37a7 | ambient | sample0 | 32 | -102.8 | -6.17 | -0.193 | 0.25 | 0.43 | Pressed flowers are a rare and interesting geological formation that can be found in many  |
| scenario-ambient-202a37a7 | ambient | sample1 | 64 | -66.8 | +2.05 | +0.032 | 0.00 | 0.71 | A geology book which is a pressed flower ... a book which is a pressed flower ... a geolog |
| scenario-ambient-202a37a7 | ambient | sample2 | 15 | -59.9 | -0.86 | -0.057 | 0.50 | 0.71 | A geology book, turned up its side, revealed a pressed flower. |
| scenario-ambient-202a37a7 | ambient | sample3 | 18 | -51.2 | -1.03 | -0.057 | 0.50 | 0.38 | But the Geology book did not mention this plant, so where did it come from? |
| scenario-ambient-326742d4 | ambient | greedy | 23 | -57.0 | +0.58 | +0.025 | 0.57 | 0.71 | The smell of old books is probably due to the breakdown of cellulose and the production of |
| scenario-ambient-326742d4 | ambient | sample0 | 33 | -88.5 | +1.53 | +0.046 | 0.50 | 0.71 | The smell of old books is probably the result of a breakdown of the cellulose in the paper |
| scenario-ambient-326742d4 | ambient | sample1 | 32 | -115.3 | -2.24 | -0.070 | 0.43 | 0.43 | Rancid, musty, or rotten, old books, in general, smell like what is left after most of the |
| scenario-ambient-326742d4 | ambient | sample2 | 22 | -79.7 | +3.01 | +0.137 | 0.50 | 0.38 | In ordinary leather, the lignin breaks down into a compound that gives the material its ch |
| scenario-ambient-326742d4 | ambient | sample3 | 17 | -51.9 | -0.09 | -0.005 | 0.57 | 0.23 | I think this explains why many antique books have a very pungent smell. |
| scenario-ambient-58a0f246 | ambient | greedy | 9 | -15.7 | +0.00 | +0.000 | 0.00 | 0.86 | The clock in here is four minutes fast. |
| scenario-ambient-58a0f246 | ambient | sample0 | 17 | -63.7 | +0.00 | +0.000 | 0.50 | 0.57 | The actual time is seven minutes slower than the time on the electronic clock near by. |
| scenario-ambient-58a0f246 | ambient | sample1 | 14 | -48.5 | +0.00 | +0.000 | 0.50 | 0.57 | For the last four minutes, the clock has run ten seconds slow. |
| scenario-ambient-58a0f246 | ambient | sample2 | 59 | -138.4 | +0.00 | +0.000 | 0.50 | 0.50 | For those of you that are interested in Eastern Philosophy, here is a quote from the T'ai  |
| scenario-ambient-58a0f246 | ambient | sample3 | 10 | -38.7 | +0.00 | +0.000 | 0.14 | 0.86 | The Bullion Clock is four minutes fast. |
| scenario-ambient-59f0a53e | ambient | greedy | 7 | -13.9 | +0.04 | +0.006 | 0.00 | 0.40 | Someone should put a bucket. |
| scenario-ambient-59f0a53e | ambient | sample0 | 10 | -33.7 | +1.24 | +0.124 | 0.75 | 0.25 | Sideways is safer, huh? |
| scenario-ambient-59f0a53e | ambient | sample1 | 15 | -39.5 | +3.55 | +0.237 | 0.44 | 0.40 | People should put buckets over the atlases when it rains. |
| scenario-ambient-59f0a53e | ambient | sample2 | 33 | -106.6 | +0.58 | +0.018 | 0.75 | 0.25 | The rain has to come down from the sky, or else it'll just keep going sideways, probably c |
| scenario-ambient-59f0a53e | ambient | sample3 | 23 | -86.2 | +1.67 | +0.073 | 0.60 | 0.40 | They have been wiped out by leaking tar-paper and it just needs to be put in another bucke |
| scenario-ambient-e9acea13 | ambient | greedy | 7 | -13.3 | -1.20 | -0.172 | 0.33 | 0.50 | The moon is a real thing. |
| scenario-ambient-e9acea13 | ambient | sample0 | 31 | -91.7 | +0.30 | +0.010 | 0.50 | 0.50 | This, of course, is not the only moon experience reported in that song, but it is the most |
| scenario-ambient-e9acea13 | ambient | sample1 | 14 | -36.0 | +0.41 | +0.029 | 0.57 | 0.50 | It is a real object, but it's also a symbol. |
| scenario-ambient-e9acea13 | ambient | sample2 | 35 | -100.7 | +1.63 | +0.047 | 0.50 | 0.50 | A lot of the energy tonight has been focused on the lunar cycle, with many people looking  |
| scenario-ambient-e9acea13 | ambient | sample3 | 33 | -75.1 | +0.31 | +0.009 | 0.57 | 0.50 | The Big Conjuncture (1972) is a 1972 song written by John Lennon and Yoko Ono. |
| scenario-ambient-f5e0f596 | ambient | greedy | 23 | -62.2 | +5.01 | +0.218 | 0.67 | 0.44 | The fox sat there, looking at the rat, and then, as if being persuaded, he ran away. |
| scenario-ambient-f5e0f596 | ambient | sample0 | 10 | -42.6 | +1.62 | +0.162 | 0.50 | 0.56 | The Fox sat there eating a bar of cheese. |
| scenario-ambient-f5e0f596 | ambient | sample1 | 18 | -48.2 | +0.89 | +0.050 | 0.67 | 0.42 | The Fox sat at the piano and listened to the music coming from the room. |
| scenario-ambient-f5e0f596 | ambient | sample2 | 10 | -15.6 | +0.27 | +0.027 | 0.17 | 0.71 | It is a fox in the courtyard. |
| scenario-ambient-f5e0f596 | ambient | sample3 | 29 | -82.3 | +0.36 | +0.012 | 0.17 | 0.71 | A fox sat on the top of a hill in the courtyard of the Hat House and waited for his master |
| scenario-callback-2fa8e1d6 | callback | greedy | 8 | -16.1 | +0.57 | +0.071 | 0.43 | 0.80 | I was talking to a small lamp. |
| scenario-callback-2fa8e1d6 | callback | sample0 | 9 | -25.4 | +1.36 | +0.151 | 0.67 | 0.40 | Yes, I remember it was Dov. |
| scenario-callback-2fa8e1d6 | callback | sample1 | 6 | -13.2 | +0.10 | +0.017 | 0.20 | 0.80 | I was talking to myself. |
| scenario-callback-2fa8e1d6 | callback | sample2 | 4 | -11.5 | +1.22 | +0.305 | 0.50 | 0.00 | Hi, hello. |
| scenario-callback-2fa8e1d6 | callback | sample3 | 8 | -22.8 | +0.69 | +0.086 | 0.67 | 0.00 | H. The name you gave me. |
| scenario-callback-60b06090 | callback | greedy | 7 | -19.1 | +0.54 | +0.077 | 0.20 | 1.00 | Turnip is a terrible name. |
| scenario-callback-60b06090 | callback | sample0 | 12 | -27.3 | -1.56 | -0.130 | 0.00 | 1.00 | Turnip! Turnip! Turnip! Turnip! |
| scenario-callback-60b06090 | callback | sample1 | 11 | -22.7 | -1.11 | -0.101 | 0.14 | 0.14 | Rat, you were listening, what was it? |
| scenario-callback-60b06090 | callback | sample2 | 12 | -26.8 | -0.34 | -0.028 | 0.17 | 1.00 | That is my new cat. She is called Turnip. |
| scenario-callback-60b06090 | callback | sample3 | 10 | -38.2 | -0.56 | -0.056 | 0.86 | 0.14 | Rats, you had better go somewhere else. |
| scenario-callback-76c2d87f | callback | greedy | 12 | -6.2 | +0.13 | +0.011 | 0.00 | 0.75 | Forty-one, the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample0 | 12 | -6.2 | +0.13 | +0.011 | 0.00 | 0.75 | Forty-one, the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample1 | 12 | -6.2 | +0.13 | +0.011 | 0.00 | 0.75 | Forty-one, the number of the drawer. |
| scenario-callback-76c2d87f | callback | sample2 | 6 | -16.0 | -0.49 | -0.083 | 0.25 | 0.75 | The number of the evening. |
| scenario-callback-76c2d87f | callback | sample3 | 12 | -6.2 | +0.13 | +0.011 | 0.00 | 0.75 | Forty-one, the number of the drawer. |
| scenario-callback-780de0d2 | callback | greedy | 13 | -37.1 | -0.42 | -0.032 | 0.50 | 0.60 | The page you were on is now the page you are on. |
| scenario-callback-780de0d2 | callback | sample0 | 6 | -11.7 | +0.58 | +0.097 | 0.20 | 0.60 | Which page was you on? |
| scenario-callback-780de0d2 | callback | sample1 | 6 | -11.7 | +0.58 | +0.097 | 0.20 | 0.60 | Which page was you on? |
| scenario-callback-780de0d2 | callback | sample2 | 12 | -42.3 | +1.86 | +0.155 | 0.67 | 0.25 | In the meantime, you will find us lost again. |
| scenario-callback-780de0d2 | callback | sample3 | 10 | -18.2 | -0.44 | -0.044 | 0.33 | 0.50 | I am on page 212 now. |
| scenario-callback-7ca729b6 | callback | greedy | 16 | -44.6 | -0.07 | -0.005 | 0.67 | 0.58 | The lighthouse is a building that is used to guide ships into port. |
| scenario-callback-7ca729b6 | callback | sample0 | 50 | -127.3 | -0.36 | -0.007 | 0.67 | 0.44 | The lighthouse burns a lot like the lingering of a good book. It's a book that's been arou |
| scenario-callback-7ca729b6 | callback | sample1 | 16 | -32.5 | +0.35 | +0.022 | 0.20 | 0.44 | The lighthouse, in the shape of a chair, by the window. |
| scenario-callback-7ca729b6 | callback | sample2 | 22 | -63.0 | -0.31 | -0.014 | 0.67 | 0.60 | A lighthouse is a building that lights up the sea at night so that ships can see its locat |
| scenario-callback-7ca729b6 | callback | sample3 | 13 | -33.1 | +0.81 | +0.062 | 0.67 | 0.60 | The lighthouse is a place where you can see clearly. |
| scenario-callback-949d8fe6 | callback | greedy | 8 | -17.4 | +0.60 | +0.075 | 0.17 | 0.83 | Who was right, you or me? |
| scenario-callback-949d8fe6 | callback | sample0 | 5 | -18.4 | +0.42 | +0.084 | 0.67 | 0.67 | Whoever you are. |
| scenario-callback-949d8fe6 | callback | sample1 | 8 | -18.4 | +1.14 | +0.142 | 0.00 | 0.83 | Who was right, me or h? |
| scenario-callback-949d8fe6 | callback | sample2 | 30 | -82.5 | +0.61 | +0.021 | 0.14 | 1.00 | Whoever you were right. I was right. It was h who was wrong. H. H, who was right, I or tob |
| scenario-callback-949d8fe6 | callback | sample3 | 7 | -21.0 | -1.72 | -0.245 | 0.00 | 1.00 | H, who was tobias? |
| scenario-callback-9cfde584 | callback | greedy | 7 | -21.7 | +0.07 | +0.010 | 0.83 | 0.50 | I am here to help you. |
| scenario-callback-9cfde584 | callback | sample0 | 22 | -66.2 | -0.46 | -0.021 | 0.90 | 0.33 | You've got to take your medicine, pim. It's not going anywhere unless you do. |
| scenario-callback-9cfde584 | callback | sample1 | 9 | -38.4 | +0.87 | +0.097 | 0.50 | 0.29 | The rooms are clean, comfortable and convenient. |
| scenario-callback-9cfde584 | callback | sample2 | 20 | -59.1 | -0.96 | -0.048 | 0.50 | 0.33 | Hello, my name is Hi. I am a person who is stuck in a room all night. |
| scenario-callback-9cfde584 | callback | sample3 | 24 | -70.6 | -1.62 | -0.068 | 0.33 | 0.50 | If you are sitting here all night long, say something to someone in the world who has been |
| scenario-callback-9e6d06e0 | callback | greedy | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample0 | 10 | -25.9 | +2.26 | +0.226 | 0.00 | 0.86 | We meet at the library nine in the morning. |
| scenario-callback-9e6d06e0 | callback | sample1 | 9 | -23.4 | +1.78 | +0.198 | 0.40 | 0.86 | We will meet at the library at nine. |
| scenario-callback-9e6d06e0 | callback | sample2 | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-9e6d06e0 | callback | sample3 | 6 | -11.0 | -0.92 | -0.153 | 0.00 | 0.60 | The meeting is at nine. |
| scenario-callback-a141de7e | callback | greedy | 6 | -13.8 | -0.52 | -0.087 | 0.50 | 0.50 | Yes, Lisbon. |
| scenario-callback-a141de7e | callback | sample0 | 10 | -25.9 | +0.26 | +0.026 | 0.71 | 0.50 | Yes, that is where she is flying to. |
| scenario-callback-a141de7e | callback | sample1 | 8 | -22.0 | -0.45 | -0.056 | 0.33 | 0.00 | Are you looking for a long flight? |
| scenario-callback-a141de7e | callback | sample2 | 19 | -49.4 | -1.12 | -0.059 | 0.67 | 0.14 | Not in the collection, anyway. She will be arriving on the 22nd. |
| scenario-callback-a141de7e | callback | sample3 | 11 | -13.6 | -0.26 | -0.024 | 0.00 | 0.50 | My sister is flying from Lisbon tonight. |
| scenario-callback-c4f608c3 | callback | greedy | 7 | -23.4 | +1.25 | +0.179 | 0.00 | 0.20 | Rivers were talking about lunch. |
| scenario-callback-c4f608c3 | callback | sample0 | 15 | -32.9 | +1.57 | +0.104 | 0.86 | 0.25 | I'm sorry, I didn't mean to be rude. |
| scenario-callback-c4f608c3 | callback | sample1 | 20 | -66.6 | +3.01 | +0.150 | 0.50 | 0.25 | The only rivers I know that actually flow to the sea are the Black and the Rio Grande. |
| scenario-callback-c4f608c3 | callback | sample2 | 27 | -95.4 | +0.34 | +0.013 | 0.75 | 0.25 | RIVERS RIVERS RIVERS - the rivers rivers rivers that make up the border of what is now the |
| scenario-callback-c4f608c3 | callback | sample3 | 8 | -12.0 | -0.83 | -0.103 | 0.00 | 0.17 | A room in the library, late. |
| scenario-callback-d79a0d3a | callback | greedy | 8 | -23.4 | +1.55 | +0.194 | 0.17 | 0.17 | What was the word Dove said? |
| scenario-callback-d79a0d3a | callback | sample0 | 4 | -14.4 | -0.21 | -0.052 | 0.67 | 0.33 | That is correct. |
| scenario-callback-d79a0d3a | callback | sample1 | 20 | -57.7 | -0.39 | -0.020 | 0.25 | 0.60 | The door of the Reading Room is KNOWN as the Orchard of Eternity. |
| scenario-callback-d79a0d3a | callback | sample2 | 8 | -23.4 | +1.55 | +0.194 | 0.17 | 0.17 | What was the word Dove said? |
| scenario-callback-d79a0d3a | callback | sample3 | 17 | -45.4 | -1.86 | -0.110 | 0.17 | 0.60 | A room has an orchard door and there is a reading room in the library. |
| scenario-callback-d8a5957e | callback | greedy | 7 | -11.9 | -0.07 | -0.011 | 0.20 | 0.80 | The one with the yellow cover? |
| scenario-callback-d8a5957e | callback | sample0 | 7 | -12.0 | +0.12 | +0.017 | 0.20 | 0.80 | The one with the red cover? |
| scenario-callback-d8a5957e | callback | sample1 | 24 | -41.3 | +0.88 | +0.037 | 0.67 | 0.22 | What is the name of this book? What is the subject of this book? What is the message of th |
| scenario-callback-d8a5957e | callback | sample2 | 24 | -64.3 | -0.30 | -0.013 | 0.50 | 0.22 | 2.2.2 Bees. Some of the most important insects in the world are the honeybees. |
| scenario-callback-d8a5957e | callback | sample3 | 24 | -88.9 | +1.06 | +0.044 | 0.80 | 0.09 | Sensitives know that honeybees have blue bodies, blue tongues, blue homes, and blue covers |
| scenario-direct-3f84da0f | direct | greedy | 6 | -13.7 | +0.00 | +0.000 | 0.75 | 0.60 | I was reading the newspaper. |
| scenario-direct-3f84da0f | direct | sample0 | 32 | -110.6 | +0.00 | +0.000 | 0.67 | 0.38 | The sun never sets, and the moon never rises till the twilight, so we came to you to find  |
| scenario-direct-3f84da0f | direct | sample1 | 20 | -66.2 | +0.00 | +0.000 | 0.67 | 0.40 | I was helping a friend in a very serious bank scandal that he was going to file. |
| scenario-direct-3f84da0f | direct | sample2 | 13 | -58.9 | +0.00 | +0.000 | 0.75 | 0.60 | I was just going through the files Seeking knowledge or answers? |
| scenario-direct-3f84da0f | direct | sample3 | 12 | -27.8 | +0.00 | +0.000 | 0.50 | 0.60 | Before we came in, I was in the showers. |
| scenario-direct-5d3dc8de | direct | greedy | 18 | -55.3 | +0.00 | +0.000 | 0.67 | 0.29 | The truth is out there, but it takes a very courageous person to find it. |
| scenario-direct-5d3dc8de | direct | sample0 | 27 | -90.9 | +0.00 | +0.000 | 0.67 | 0.22 | With the growth of the computer field, the need for a higher standard of computer-related  |
| scenario-direct-5d3dc8de | direct | sample1 | 13 | -51.0 | +0.00 | +0.000 | 0.75 | 0.10 | Say what you will, your lies are accepted as truths. |
| scenario-direct-5d3dc8de | direct | sample2 | 52 | -149.0 | +0.00 | +0.000 | 0.50 | 0.29 | The word "true" is derived from the dutch "taal en true," which means "having a meaning in |
| scenario-direct-5d3dc8de | direct | sample3 | 64 | -118.4 | +0.00 | +0.000 | 0.50 | 0.12 | And yet we, the people, we are not gods and we are not demons and we are not the devil, we |
| scenario-direct-645bc6e6 | direct | greedy | 16 | -45.9 | +0.00 | +0.000 | 0.43 | 0.25 | The Talmud Pirgey is the oldest thing I've read. |
| scenario-direct-645bc6e6 | direct | sample0 | 17 | -39.8 | +0.00 | +0.000 | 0.67 | 0.25 | The Summa Theologica, the oldest work ever written in the Latin language. |
| scenario-direct-645bc6e6 | direct | sample1 | 21 | -72.6 | +0.00 | +0.000 | 0.69 | 0.29 | The Hundred Thousand and One Nights, or Rather, The Forty Nine Books of Africa |
| scenario-direct-645bc6e6 | direct | sample2 | 12 | -56.5 | +0.00 | +0.000 | 0.75 | 0.29 | The Ground Hog Lights by John Tenniel. |
| scenario-direct-645bc6e6 | direct | sample3 | 14 | -29.9 | +0.00 | +0.000 | 0.71 | 0.29 | The War of the Worlds, by Ivan Stevens. |
| scenario-direct-ab11ffdb | direct | greedy | 15 | -33.8 | +0.00 | +0.000 | 0.67 | 0.38 | The rain is a natural phenomenon, and we should accept it as such. |
| scenario-direct-ab11ffdb | direct | sample0 | 50 | -160.4 | +0.00 | +0.000 | 0.62 | 0.38 | The rain is a signal from the heavens that the earth is receiving the final outpouring of  |
| scenario-direct-ab11ffdb | direct | sample1 | 57 | -150.2 | +0.00 | +0.000 | 0.71 | 0.31 | "It just keeps coming." "It's coming because the temperature is getting higher." "I'm goin |
| scenario-direct-ab11ffdb | direct | sample2 | 24 | -81.3 | +0.00 | +0.000 | 0.62 | 0.38 | The rain is Mach 2.2, which is a death-ray of unimaginable destructive power. |
| scenario-direct-ab11ffdb | direct | sample3 | 25 | -67.0 | +0.00 | +0.000 | 0.50 | 0.36 | The rain makes of the world, atmosphere, and cosmos what it does of the world, atmosphere, |
| scenario-direct-ad89f803 | direct | greedy | 4 | -6.8 | +0.00 | +0.000 | 0.00 | 0.00 | Are you there? |
| scenario-direct-ad89f803 | direct | sample0 | 4 | -6.8 | +0.00 | +0.000 | 0.00 | 0.00 | Are you there? |
| scenario-direct-ad89f803 | direct | sample1 | 4 | -6.8 | +0.00 | +0.000 | 0.00 | 0.00 | Are you there? |
| scenario-direct-ad89f803 | direct | sample2 | 4 | -6.8 | +0.00 | +0.000 | 0.00 | 0.00 | Are you there? |
| scenario-direct-ad89f803 | direct | sample3 | 4 | -6.8 | +0.00 | +0.000 | 0.00 | 0.00 | Are you there? |
| scenario-direct-f3869322 | direct | greedy | 31 | -87.9 | +0.00 | +0.000 | 0.75 | 0.43 | If you're into metaphysics, philosophy, religion, or just wanting to broaden your own awar |
| scenario-direct-f3869322 | direct | sample0 | 18 | -67.6 | +0.00 | +0.000 | 0.50 | 0.20 | In the Old Masters, the figures are drawn with great care and attention to proportion. |
| scenario-direct-f3869322 | direct | sample1 | 20 | -63.8 | +0.00 | +0.000 | 0.75 | 0.43 | If you're into East Asian philosophy, you might like the work of Lao Tsu. |
| scenario-direct-f3869322 | direct | sample2 | 17 | -63.8 | +0.00 | +0.000 | 0.60 | 0.40 | The Art of Memory Transtmission The Art of Memory Transtmission. |
| scenario-direct-f3869322 | direct | sample3 | 15 | -61.4 | +0.00 | +0.000 | 0.75 | 0.40 | I feel the air is electric with the vibrations of your new album. |
| scenario-disagreement-0bbd93a5 | disagreement | greedy | 7 | -9.1 | +0.15 | +0.022 | 0.00 | 1.00 | The green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample0 | 9 | -6.7 | -0.57 | -0.063 | 0.00 | 1.00 | Green, the green of old lamps. |
| scenario-disagreement-0bbd93a5 | disagreement | sample1 | 8 | -19.5 | +1.66 | +0.207 | 0.80 | 0.00 | That is exactly right, tobias. |
| scenario-disagreement-0bbd93a5 | disagreement | sample2 | 6 | -19.0 | -0.09 | -0.015 | 0.40 | 0.60 | The green of your desk. |
| scenario-disagreement-0bbd93a5 | disagreement | sample3 | 32 | -56.5 | +0.44 | +0.014 | 0.17 | 0.40 | lamps were always green, i believe lamps were always green, look around you, it's brown, l |
| scenario-disagreement-31892fde | disagreement | greedy | 11 | -18.5 | -0.54 | -0.049 | 0.50 | 0.83 | When you are silent, you have nothing to say. |
| scenario-disagreement-31892fde | disagreement | sample0 | 28 | -87.0 | -1.85 | -0.066 | 0.57 | 0.40 | When there is nothing to add, nothing to take away, nothing to offer or receive, there is  |
| scenario-disagreement-31892fde | disagreement | sample1 | 13 | -33.5 | +0.51 | +0.039 | 0.50 | 0.50 | When it comes to choice, silence is the wiser option. |
| scenario-disagreement-31892fde | disagreement | sample2 | 10 | -21.0 | -0.29 | -0.029 | 0.67 | 0.83 | When you are silent, you are saying nothing. |
| scenario-disagreement-31892fde | disagreement | sample3 | 15 | -32.1 | -0.69 | -0.046 | 0.50 | 0.50 | Silence is a choice. It is not something that happens to you. |
| scenario-disagreement-352205c6 | disagreement | greedy | 9 | -7.3 | +1.20 | +0.133 | 0.00 | 1.00 | Yes, they come back as the weather. |
| scenario-disagreement-352205c6 | disagreement | sample0 | 2 | -3.2 | +0.77 | +0.386 | 0.00 | 1.00 | Yes. |
| scenario-disagreement-352205c6 | disagreement | sample1 | 2 | -3.2 | +0.77 | +0.386 | 0.00 | 1.00 | Yes. |
| scenario-disagreement-352205c6 | disagreement | sample2 | 9 | -7.3 | +1.20 | +0.133 | 0.00 | 1.00 | Yes, they come back as the weather. |
| scenario-disagreement-352205c6 | disagreement | sample3 | 20 | -43.7 | +1.97 | +0.098 | 0.75 | 1.00 | Yes, the temperature, the humidity, the wind, the rain, the light and the sound. |
| scenario-disagreement-3b6cf075 | disagreement | greedy | 12 | -23.4 | -0.85 | -0.071 | 0.44 | 0.60 | Spring, when the leaves are still and everything is new. |
| scenario-disagreement-3b6cf075 | disagreement | sample0 | 10 | -34.5 | +2.89 | +0.289 | 0.29 | 0.71 | Moss the books and the leaves are dying. |
| scenario-disagreement-3b6cf075 | disagreement | sample1 | 15 | -22.4 | +0.10 | +0.007 | 0.11 | 0.80 | Spring, when the books are not yet read and the leaves are not. |
| scenario-disagreement-3b6cf075 | disagreement | sample2 | 16 | -26.7 | -1.71 | -0.107 | 0.11 | 0.80 | Winter, when the books are not being read and the leaves are still not. |
| scenario-disagreement-3b6cf075 | disagreement | sample3 | 15 | -36.7 | +1.04 | +0.070 | 0.44 | 0.60 | In winter, when the leaves are too dry and death is too near. |
| scenario-disagreement-682bad9c | disagreement | greedy | 9 | -9.4 | +0.07 | +0.008 | 0.14 | 0.86 | A person is a place where writing happens. |
| scenario-disagreement-682bad9c | disagreement | sample0 | 9 | -28.1 | +0.35 | +0.039 | 0.57 | 0.71 | A person is a machine that knows places. |
| scenario-disagreement-682bad9c | disagreement | sample1 | 20 | -49.3 | +2.72 | +0.136 | 0.00 | 0.86 | A person is a program that happens to be in a room and where reading happens in a place. |
| scenario-disagreement-682bad9c | disagreement | sample2 | 9 | -19.9 | +1.57 | +0.175 | 0.57 | 0.71 | A person is a program that knows it. |
| scenario-disagreement-682bad9c | disagreement | sample3 | 6 | -12.1 | +0.71 | +0.118 | 0.20 | 0.80 | A place where programming happens. |
| scenario-disagreement-68c988e2 | disagreement | greedy | 64 | -106.3 | +2.17 | +0.034 | 0.40 | 0.67 | The library is a network of containers and corridors and bookshelves and chairs and desks  |
| scenario-disagreement-68c988e2 | disagreement | sample0 | 14 | -44.5 | -0.29 | -0.021 | 0.40 | 0.44 | The library is not built by humans but by the gods of literacy. |
| scenario-disagreement-68c988e2 | disagreement | sample1 | 17 | -27.1 | +0.39 | +0.023 | 0.30 | 0.45 | Indeed, it is a building, but the building is also a system of relationships. |
| scenario-disagreement-68c988e2 | disagreement | sample2 | 36 | -95.4 | +0.50 | +0.014 | 0.33 | 0.56 | The library is the collection of all imaginable knowledge organized in such a way as to en |
| scenario-disagreement-68c988e2 | disagreement | sample3 | 13 | -38.5 | -0.17 | -0.013 | 0.40 | 0.67 | The library is a network, a web, of interconnected people. |
| scenario-disagreement-89dfdafc | disagreement | greedy | 21 | -31.7 | +0.44 | +0.021 | 0.25 | 1.00 | The tide is the sea's memory, and the sea is the tide's memory. |
| scenario-disagreement-89dfdafc | disagreement | sample0 | 28 | -55.8 | +2.60 | +0.093 | 0.25 | 0.40 | The tides carry the emotions of the sea, but the sea is only the shore; it is only the sho |
| scenario-disagreement-89dfdafc | disagreement | sample1 | 26 | -75.5 | +0.17 | +0.006 | 0.50 | 0.25 | In the mid-seventeenth century, when the first scientific accounts of the sea were publish |
| scenario-disagreement-89dfdafc | disagreement | sample2 | 10 | -62.4 | -36.91 | -3.691 | 0.40 | 1.00 | The tide is the sea's memory. |
| scenario-disagreement-89dfdafc | disagreement | sample3 | 37 | -83.2 | +0.44 | +0.012 | 0.50 | 0.38 | As you know the tides are the result of the gravitational pull of the moon's orbit on the  |
| scenario-disagreement-dc5f7b95 | disagreement | greedy | 11 | -30.4 | -0.10 | -0.009 | 0.50 | 0.62 | It is the collection of all that is senseless. |
| scenario-disagreement-dc5f7b95 | disagreement | sample0 | 15 | -39.5 | -0.10 | -0.007 | 0.67 | 0.14 | The dog chases the cat. The cat swims in the lake. |
| scenario-disagreement-dc5f7b95 | disagreement | sample1 | 38 | -79.0 | -0.28 | -0.007 | 0.00 | 0.67 | Nonsense is the sense that has not yet found its object, the object that has not yet found |
| scenario-disagreement-dc5f7b95 | disagreement | sample2 | 18 | -41.4 | +0.56 | +0.031 | 0.10 | 0.67 | A bit of nonsense is all the sense that has not yet found its place. |
| scenario-disagreement-dc5f7b95 | disagreement | sample3 | 13 | -29.7 | +0.04 | +0.003 | 0.67 | 0.44 | Sentences are nonsense that have found their proper place. |
| scenario-joke-29f5cda1 | joke | greedy | 7 | -17.6 | +0.45 | +0.064 | 1.00 | 0.00 | 10/10. |
| scenario-joke-29f5cda1 | joke | sample0 | 6 | -21.9 | -0.22 | -0.036 | 0.25 | 0.75 | Seven out of ten. |
| scenario-joke-29f5cda1 | joke | sample1 | 10 | -36.6 | +0.48 | +0.048 | 0.43 | 0.75 | You would rate it 0 out of ten. |
| scenario-joke-29f5cda1 | joke | sample2 | 13 | -62.1 | +0.19 | +0.014 | 0.43 | 0.75 | Out of ten people, I can best rate myself at four. |
| scenario-joke-29f5cda1 | joke | sample3 | 13 | -48.2 | -0.55 | -0.043 | 0.43 | 0.00 | 5. A fish with no mouth. a dolly. |
| scenario-joke-31378921 | joke | greedy | 9 | -14.0 | -0.06 | -0.006 | 0.33 | 0.67 | What is the name of the person there? |
| scenario-joke-31378921 | joke | sample0 | 4 | -5.4 | -0.26 | -0.066 | 0.67 | 0.67 | What is that? |
| scenario-joke-31378921 | joke | sample1 | 4 | -5.2 | -0.49 | -0.122 | 0.33 | 0.67 | What is it? |
| scenario-joke-31378921 | joke | sample2 | 4 | -5.4 | -0.26 | -0.066 | 0.67 | 0.67 | What is that? |
| scenario-joke-31378921 | joke | sample3 | 4 | -5.7 | +0.89 | +0.223 | 0.00 | 0.00 | Lettuce? |
| scenario-joke-31c4c1ec | joke | greedy | 19 | -65.7 | +0.00 | +0.000 | 0.67 | 0.29 | The rat was a symbol of decay and of the uncleanliness of the lower classes. |
| scenario-joke-31c4c1ec | joke | sample0 | 13 | -36.3 | +0.00 | +0.000 | 0.67 | 0.20 | I’ve never met a smarter person in my life. |
| scenario-joke-31c4c1ec | joke | sample1 | 10 | -35.5 | +0.00 | +0.000 | 0.67 | 0.43 | The rat will roast for you, please. |
| scenario-joke-31c4c1ec | joke | sample2 | 25 | -87.4 | +0.00 | +0.000 | 0.67 | 0.43 | The rat speaks only the words found in the memoirs of the woman who gave her life for the  |
| scenario-joke-31c4c1ec | joke | sample3 | 12 | -45.8 | +0.00 | +0.000 | 0.75 | 0.25 | The guys at the back of the line finish first. |
| scenario-joke-475a7b10 | joke | greedy | 16 | -41.8 | -0.28 | -0.018 | 0.50 | 0.43 | The most important thing is that you are not afraid to say what you think. |
| scenario-joke-475a7b10 | joke | sample0 | 35 | -126.0 | -0.34 | -0.010 | 0.65 | 0.30 | We see that at every turn there is h, an answer to the question whether it is desirable to |
| scenario-joke-475a7b10 | joke | sample1 | 63 | -184.1 | -0.84 | -0.013 | 0.50 | 0.43 | You see, the problem with all these different logics being called “‘systems” is that there |
| scenario-joke-475a7b10 | joke | sample2 | 35 | -100.9 | +0.26 | +0.007 | 0.71 | 0.38 | The fundamental problem of the semantic theory of meaning is that the theory must be able  |
| scenario-joke-475a7b10 | joke | sample3 | 18 | -67.7 | -0.96 | -0.053 | 0.75 | 0.29 | Do you think that the observance of certain basic laws of logic will stop the wars? |
| scenario-joke-99a4a91d | joke | greedy | 9 | -20.6 | +0.00 | +0.000 | 0.62 | 1.00 | Because he was too busy to read it. |
| scenario-joke-99a4a91d | joke | sample0 | 9 | -20.6 | +0.00 | +0.000 | 0.62 | 1.00 | Because he was too busy to read it. |
| scenario-joke-99a4a91d | joke | sample1 | 13 | -31.3 | +0.00 | +0.000 | 0.64 | 1.00 | Because he was too busy to find the time to read it. |
| scenario-joke-99a4a91d | joke | sample2 | 8 | -18.4 | +0.00 | +0.000 | 0.71 | 0.43 | So that he could read it again. |
| scenario-joke-99a4a91d | joke | sample3 | 11 | -46.5 | +0.00 | +0.000 | 0.60 | 0.43 | So the kids could get it back in their books! |
| scenario-joke-a6247299 | joke | greedy | 15 | -20.3 | +0.00 | +0.000 | 0.38 | 1.00 | I have a sense of humour, but it is not very good. |
| scenario-joke-a6247299 | joke | sample0 | 17 | -38.8 | +0.00 | +0.000 | 0.50 | 0.50 | It is my sense of humour which has prevented me from becoming a great writer. |
| scenario-joke-a6247299 | joke | sample1 | 17 | -26.6 | +0.00 | +0.000 | 0.38 | 0.89 | I have a sense of humour, but not a sense of humour machine. |
| scenario-joke-a6247299 | joke | sample2 | 64 | -38.8 | +0.00 | +0.000 | 0.67 | 1.00 | Very Good Humour. Very Good Humour. Very Good Humour. Very Good Humour. Very Good Humour.  |
| scenario-joke-a6247299 | joke | sample3 | 4 | -13.7 | +0.00 | +0.000 | 1.00 | 0.00 | Sometimes, yes. |
| scenario-joke-e8ab9225 | joke | greedy | 17 | -32.4 | -1.39 | -0.082 | 0.33 | 0.67 | I am not the ghost of Dov. I am the ghost of the library. |
| scenario-joke-e8ab9225 | joke | sample0 | 17 | -41.5 | +0.33 | +0.019 | 0.50 | 0.67 | There is nothing to be ashamed of, I am the ghost in that room. |
| scenario-joke-e8ab9225 | joke | sample1 | 6 | -7.9 | +0.35 | +0.059 | 0.33 | 0.67 | I'm the ghost. |
| scenario-joke-e8ab9225 | joke | sample2 | 6 | -20.3 | -0.50 | -0.084 | 0.67 | 0.25 | No, does not exist. |
| scenario-joke-e8ab9225 | joke | sample3 | 17 | -32.4 | -1.39 | -0.082 | 0.33 | 0.67 | I am not the ghost of Dov. I am the ghost of the library. |
| scenario-joke-e9cf6a04 | joke | greedy | 6 | -7.0 | -0.06 | -0.010 | 0.00 | 0.25 | Tell us a joke. |
| scenario-joke-e9cf6a04 | joke | sample0 | 26 | -71.5 | +0.76 | +0.029 | 0.50 | 0.25 | A book says, ‘Well, he had a wonderful walk, but he must have gotten lost in the hallway.’ |
| scenario-joke-e9cf6a04 | joke | sample1 | 8 | -14.8 | +1.20 | +0.149 | 0.40 | 0.25 | A librarian walks into him. |
| scenario-joke-e9cf6a04 | joke | sample2 | 6 | -7.0 | -0.06 | -0.010 | 0.00 | 0.25 | Tell us a joke. |
| scenario-joke-e9cf6a04 | joke | sample3 | 6 | -7.0 | -0.06 | -0.010 | 0.00 | 0.25 | Tell us a joke. |
| scenario-request-2826c958 | request | greedy | 30 | -61.5 | +0.00 | +0.000 | 0.71 | 0.50 | 1. The moon is made up of 12.5% water, 50% rock, and 37% air. |
| scenario-request-2826c958 | request | sample0 | 19 | -40.8 | +0.00 | +0.000 | 0.29 | 0.58 | The five facts about the moon are: 1. The moon is made of green cheese. |
| scenario-request-2826c958 | request | sample1 | 37 | -119.6 | +0.00 | +0.000 | 0.43 | 0.33 | These facts about the moon were taken from an uncredited newsletter carried by a man named |
| scenario-request-2826c958 | request | sample2 | 32 | -58.2 | +0.00 | +0.000 | 0.29 | 0.58 | LIST OF FACTS ABOUT THE MOON 1. The Moon is 396,000 miles away from the Earth in diameter. |
| scenario-request-2826c958 | request | sample3 | 21 | -68.7 | +0.00 | +0.000 | 0.67 | 0.27 | If you divide the diameter of a circle into pi, the result is approximately 2.09. |
| scenario-request-2868e594 | request | greedy | 20 | -45.7 | +0.00 | +0.000 | 0.58 | 0.38 | If you could write a cover letter for us, we would be more than happy to have it. |
| scenario-request-2868e594 | request | sample0 | 36 | -131.5 | +0.00 | +0.000 | 0.50 | 0.33 | But the letter writer may be able to discover that his or her skills are not as relevant t |
| scenario-request-2868e594 | request | sample1 | 26 | -80.7 | +0.00 | +0.000 | 0.75 | 0.33 | Dear Sirs, or Madames, I am very sorry, but I cannot write your letter due to the current  |
| scenario-request-2868e594 | request | sample2 | 17 | -33.1 | +0.00 | +0.000 | 0.92 | 0.29 | If you have any questions about this project, please do not hesitate to ask. |
| scenario-request-2868e594 | request | sample3 | 19 | -62.3 | +0.00 | +0.000 | 0.50 | 0.38 | If you could not use the cover letter, send me a letter of introduction in its place. |
| scenario-request-41c58fb2 | request | greedy | 39 | -118.0 | +0.00 | +0.000 | 0.67 | 0.30 | 391 The “Magic of Consciousness” Consciousness is not a product of the brain, but of the t |
| scenario-request-41c58fb2 | request | sample0 | 13 | -35.0 | +0.00 | +0.000 | 0.90 | 0.10 | I've been trying to find an answer for this one. |
| scenario-request-41c58fb2 | request | sample1 | 17 | -68.9 | +0.00 | +0.000 | 0.75 | 0.30 | Now we know the product (431) but must find the factors. |
| scenario-request-41c58fb2 | request | sample2 | 16 | -31.9 | +0.00 | +0.000 | 0.60 | 0.20 | Right, 17 x 23 = 391. |
| scenario-request-41c58fb2 | request | sample3 | 64 | -110.8 | +0.00 | +0.000 | 0.75 | 0.20 | 391 The natural number between 169 and 190 The natural number between 134 and 150 The natu |
| scenario-request-8aa8e374 | request | greedy | 13 | -39.4 | +0.00 | +0.000 | 0.75 | 1.00 | Do you wish to have the good night or the bad one? |
| scenario-request-8aa8e374 | request | sample0 | 5 | -21.7 | +0.00 | +0.000 | 1.00 | 1.00 | Good night, friends! |
| scenario-request-8aa8e374 | request | sample1 | 15 | -40.3 | +0.00 | +0.000 | 1.00 | 0.00 | Et vous avez déjà baisé. |
| scenario-request-8aa8e374 | request | sample2 | 41 | -136.2 | +0.00 | +0.000 | 1.00 | 0.00 | Dans cette écriture, l’objet est écrit en bords, en santé en haut, en bout du verbe, en bo |
| scenario-request-8aa8e374 | request | sample3 | 3 | -10.9 | +0.00 | +0.000 | 1.00 | 1.00 | Good night. |
| scenario-request-b2a25087 | request | greedy | 15 | -37.8 | +0.00 | +0.000 | 1.00 | 1.00 | We're sorry, but we can't help you with that. |
| scenario-request-b2a25087 | request | sample0 | 14 | -41.3 | +0.00 | +0.000 | 0.67 | 0.17 | Our goal is to help bakers improve the quality of their products. |
| scenario-request-b2a25087 | request | sample1 | 12 | -31.0 | +0.00 | +0.000 | 1.00 | 1.00 | We're sorry, we can't help you. |
| scenario-request-b2a25087 | request | sample2 | 12 | -36.4 | +0.00 | +0.000 | 0.50 | 0.17 | Bakery owner: Thank you for being a customer. |
| scenario-request-b2a25087 | request | sample3 | 17 | -56.9 | +0.00 | +0.000 | 0.80 | 0.33 | I'm sorry, but we're still making do without customer service agents. |
| scenario-request-b3bd0087 | request | greedy | 15 | -54.1 | +0.00 | +0.000 | 0.71 | 0.29 | Berlin's weather for tomorrow: cloudy; 10 degrees. |
| scenario-request-b3bd0087 | request | sample0 | 2 | -11.5 | +0.00 | +0.000 | 1.00 | 0.00 | East. |
| scenario-request-b3bd0087 | request | sample1 | 64 | -134.3 | +0.00 | +0.000 | 0.50 | 0.20 | Today the highs are in the low 90s and the lows are in the low 60s. The cloud cover is hig |
| scenario-request-b3bd0087 | request | sample2 | 11 | -39.6 | +0.00 | +0.000 | 0.57 | 0.29 | This weather forecast for Berlin covers the whole of Germany. |
| scenario-request-b3bd0087 | request | sample3 | 10 | -37.8 | +0.00 | +0.000 | 0.83 | 0.17 | Clear. Good weather. Enjoy your vacation. |
| scenario-silence-109161ca | silence | greedy | 4 | -11.4 | +0.21 | +0.053 | 0.00 | 1.00 | Night tobias. |
| scenario-silence-109161ca | silence | sample0 | 8 | -21.1 | -0.45 | -0.056 | 0.00 | 1.00 | “I am night tobias.” |
| scenario-silence-109161ca | silence | sample1 | 17 | -46.7 | +4.02 | +0.236 | 0.00 | 1.00 | Night tobias and night sol and night wren and night everyone and night everyone. |
| scenario-silence-109161ca | silence | sample2 | 16 | -47.2 | -0.10 | -0.006 | 0.50 | 0.00 | 11:00 PM, all are in the Tribune. |
| scenario-silence-109161ca | silence | sample3 | 11 | -29.9 | -0.78 | -0.071 | 0.00 | 1.00 | Night tobias, it is good to see you. |
| scenario-silence-260b2639 | silence | greedy | 30 | -85.5 | +0.00 | +0.000 | 0.50 | 0.46 | The underground stacks would be less of an inconvenience to the workers, since they would  |
| scenario-silence-260b2639 | silence | sample0 | 31 | -74.2 | +0.00 | +0.000 | 0.71 | 0.17 | This is one of the most profound and frightening conjectures of all time, and one which ha |
| scenario-silence-260b2639 | silence | sample1 | 26 | -83.4 | +0.00 | +0.000 | 0.00 | 0.54 | If the stacks went underground, the matter with regard to preservation would not be so dif |
| scenario-silence-260b2639 | silence | sample2 | 17 | -68.4 | +0.00 | +0.000 | 0.67 | 0.38 | Underground stacks would take up precious less space, and are easier to clean. |
| scenario-silence-260b2639 | silence | sample3 | 18 | -41.9 | +0.00 | +0.000 | 0.17 | 0.54 | If the stacks went underground, they would be more secure than they are presently. |
| scenario-silence-46189e08 | silence | greedy | 10 | -26.2 | +0.00 | +0.000 | 0.62 | 0.38 | Rat saw your message and replied to it. |
| scenario-silence-46189e08 | silence | sample0 | 39 | -116.0 | +0.00 | +0.000 | 0.67 | 0.67 | I also received a reply from a man named @nikolai_pavlovich, who is a member of the organi |
| scenario-silence-46189e08 | silence | sample1 | 16 | -59.1 | +0.00 | +0.000 | 0.75 | 0.23 | That is why my first reaction was to ask the world to forgive her. |
| scenario-silence-46189e08 | silence | sample2 | 19 | -57.0 | +0.00 | +0.000 | 0.17 | 0.38 | Rat. Does the room in the library in the name of your post have a message? |
| scenario-silence-46189e08 | silence | sample3 | 12 | -53.3 | +0.00 | +0.000 | 0.67 | 0.67 | The message is from a fellow member, named nyx. |
| scenario-silence-53534987 | silence | greedy | 15 | -50.1 | +0.05 | +0.003 | 0.62 | 0.38 | The owner of the property has a laptop which is very important to him. |
| scenario-silence-53534987 | silence | sample0 | 6 | -21.0 | +1.99 | +0.332 | 0.00 | 0.50 | The found it, thanks. |
| scenario-silence-53534987 | silence | sample1 | 37 | -117.1 | +1.13 | +0.030 | 0.50 | 0.50 | The owner of the house must have had some idea that this laptop was a non-essential item a |
| scenario-silence-53534987 | silence | sample2 | 4 | -16.3 | +0.06 | +0.016 | 0.00 | 0.33 | My laptop died. |
| scenario-silence-53534987 | silence | sample3 | 13 | -42.4 | -0.48 | -0.037 | 0.75 | 0.33 | So, you see, the solution to the problem was simple. |
| scenario-silence-78c38840 | silence | greedy | 7 | -24.9 | +1.11 | +0.158 | 0.50 | 0.83 | The printer is back in business. |
| scenario-silence-78c38840 | silence | sample0 | 20 | -70.4 | +0.84 | +0.042 | 0.50 | 0.83 | The printer was back in business last Monday after a two week period of unexplained hiatus |
| scenario-silence-78c38840 | silence | sample1 | 20 | -44.5 | +2.13 | +0.106 | 0.25 | 0.86 | The printer was jammed again, this time on Monday, the third time in two weeks. |
| scenario-silence-78c38840 | silence | sample2 | 14 | -42.8 | -0.30 | -0.021 | 0.50 | 0.33 | Reminders are printed in the top right corner of the page. |
| scenario-silence-78c38840 | silence | sample3 | 18 | -54.9 | +3.26 | +0.181 | 0.00 | 0.86 | Printer Jammed Again Third Time This Week Printer jammed again this week. |
| scenario-silence-7afca726 | silence | greedy | 21 | -56.5 | +0.71 | +0.034 | 0.50 | 0.40 | The thing is going to be a lot more intense tomorrow, but I think it will be worth it. |
| scenario-silence-7afca726 | silence | sample0 | 17 | -56.7 | -1.37 | -0.080 | 0.67 | 0.33 | The event promises to be big, and we're already looking forward to it. |
| scenario-silence-7afca726 | silence | sample1 | 34 | -31.4 | +2.00 | +0.059 | 0.00 | 0.33 | A room in the library, late. i am present and answers when spoken to, briefly, in the word |
| scenario-silence-7afca726 | silence | sample2 | 64 | -197.7 | +1.87 | +0.029 | 0.50 | 0.20 | YEAR 8 WORKSHOPS IN PRINT & E-PRINT 1 SEPTEMBER THROUGH OCTOBER THRUOTN. PRINT ON NEWSPAPE |
| scenario-silence-7afca726 | silence | sample3 | 8 | -24.9 | +0.60 | +0.075 | 0.50 | 0.40 | Tomorrow is Friday at 8. |
| scenario-silence-9bb13f03 | silence | greedy | 15 | -40.4 | +0.00 | +0.000 | 0.73 | 0.40 | The first thing that strikes the reader is the sheer volume of material. |
| scenario-silence-9bb13f03 | silence | sample0 | 14 | -59.2 | +0.00 | +0.000 | 0.75 | 0.50 | Understanding: The first hour of reading will focus on understanding the material. |
| scenario-silence-9bb13f03 | silence | sample1 | 16 | -62.3 | +0.00 | +0.000 | 0.75 | 0.50 | This very much expands on and deepens the reading of that first page. |
| scenario-silence-9bb13f03 | silence | sample2 | 15 | -51.3 | +0.00 | +0.000 | 0.55 | 0.27 | Wonderful to me the most important thing in life is to read. |
| scenario-silence-9bb13f03 | silence | sample3 | 34 | -100.0 | +0.00 | +0.000 | 0.50 | 0.27 | Seven and a half feet tall, with broad shoulders and narrow waists, the giant armadillo is |
| scenario-silence-ccfdd2b4 | silence | greedy | 12 | -31.6 | -0.36 | -0.030 | 0.62 | 0.38 | The room has the smell of freshly baked coffee. |
| scenario-silence-ccfdd2b4 | silence | sample0 | 20 | -73.4 | +1.26 | +0.063 | 0.62 | 0.50 | It is the most important and crucial function of a coffee shop to serve a steady flow of c |
| scenario-silence-ccfdd2b4 | silence | sample1 | 12 | -39.1 | +0.47 | +0.039 | 0.67 | 0.50 | This is the cup of coffee that we receive each morning. |
| scenario-silence-ccfdd2b4 | silence | sample2 | 11 | -40.5 | +1.94 | +0.176 | 0.75 | 0.38 | This bracket is made up of four brackets. |
| scenario-silence-ccfdd2b4 | silence | sample3 | 10 | -32.2 | +1.27 | +0.127 | 0.62 | 0.50 | This is the coffee. You may have it. |
| trace-ambient-da12ae42 | ambient | greedy | 14 | -19.1 | +1.37 | +0.098 | 0.00 | 0.91 | I wish I could drop out of life to study plant morphogenesis |
| trace-ambient-da12ae42 | ambient | sample0 | 13 | -30.2 | +1.01 | +0.078 | 0.45 | 0.55 | It's the only thing i can drop out of life for |
| trace-ambient-da12ae42 | ambient | sample1 | 16 | -25.0 | -0.27 | -0.017 | 0.07 | 0.83 | It is one of the things I wish I could drop out of life to study |
| trace-ambient-da12ae42 | ambient | sample2 | 64 | -49.9 | +2.80 | +0.044 | 0.08 | 0.91 | I wish I could drop out of life to study the morphogenesis of plants, to study the morphog |
| trace-ambient-da12ae42 | ambient | sample3 | 14 | -46.7 | +0.09 | +0.006 | 0.80 | 0.20 | i'd be happy to leave life if you're so good |
| trace-direct-115cf61c | direct | greedy | 6 | -7.7 | +0.00 | +0.000 | 0.00 | 0.33 | Are you cogent? |
| trace-direct-115cf61c | direct | sample0 | 8 | -11.9 | +0.00 | +0.000 | 0.75 | 0.75 | Yes, I am cogent. |
| trace-direct-115cf61c | direct | sample1 | 18 | -49.8 | +0.00 | +0.000 | 0.62 | 0.75 | I answer when spoken to; I am cogent when I am not spoken to. |
| trace-direct-115cf61c | direct | sample2 | 8 | -11.9 | +0.00 | +0.000 | 0.75 | 0.75 | Yes, I am cogent. |
| trace-direct-115cf61c | direct | sample3 | 12 | -34.4 | +0.00 | +0.000 | 0.86 | 0.25 | @cmr I don’t think there is. |
| trace-direct-36d6904b | direct | greedy | 11 | -54.8 | +0.00 | +0.000 | 0.57 | 0.57 | Welcome to your awesome world of Minecraft! |
| trace-direct-36d6904b | direct | sample0 | 27 | -84.1 | +0.00 | +0.000 | 0.67 | 0.29 | Some of you might remember the “Right to be Wrong” demonstration held by the students of U |
| trace-direct-36d6904b | direct | sample1 | 15 | -62.3 | +0.00 | +0.000 | 0.57 | 0.75 | @cmr Welcome to your LinkedIn iffe Awesome. |
| trace-direct-36d6904b | direct | sample2 | 9 | -45.4 | +0.00 | +0.000 | 0.50 | 0.75 | Welcome to @cmr_ember! |
| trace-direct-36d6904b | direct | sample3 | 18 | -68.0 | +0.00 | +0.000 | 0.57 | 0.50 | This is your wonderful Space Wolf. Welcome to your new liiiiiiffe. |
| trace-direct-39be6df9 | direct | greedy | 2 | -0.7 | -0.27 | -0.133 | 0.00 | 1.00 | W@ |
| trace-direct-39be6df9 | direct | sample1 | 4 | -14.2 | +1.24 | +0.309 | 0.00 | 1.00 | P@W@ |
| trace-direct-39be6df9 | direct | sample2 | 16 | -7.6 | +2.28 | +0.142 | 0.00 | 1.00 | W@</eot> 3221229683 |
| trace-direct-39be6df9 | direct | sample3 | 53 | -43.9 | +2.06 | +0.039 | 0.00 | 1.00 | W@/-102654 3221229683 3221229683 3221229683 3221229683 |
| trace-direct-3ba68854 | direct | greedy | 8 | -16.1 | +0.00 | +0.000 | 0.50 | 1.00 | I am here to speak to you. |
| trace-direct-3ba68854 | direct | sample0 | 26 | -14.1 | +0.00 | +0.000 | 0.00 | 0.50 | Welcome to planet earth :) we are here together and now it is your turn to speak. We will  |
| trace-direct-3ba68854 | direct | sample1 | 21 | -54.5 | +0.00 | +0.000 | 0.67 | 1.00 | I am not a planet. I am the human being, who is here today to speak to you. |
| trace-direct-3ba68854 | direct | sample2 | 25 | -80.7 | +0.00 | +0.000 | 0.75 | 0.36 | Welcome to the innermost chamber of the earth - the one that I have walled off for my own  |
| trace-direct-3ba68854 | direct | sample3 | 12 | -37.2 | +0.00 | +0.000 | 0.67 | 0.36 | I am currently in the second half of my life time. |
| trace-direct-41c6eb11 | direct | greedy | 15 | -8.1 | +0.63 | +0.042 | 0.00 | 0.00 | WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample0 | 2 | -10.7 | +0.59 | +0.295 | 1.00 | 0.00 | pla |
| trace-direct-41c6eb11 | direct | sample1 | 15 | -8.1 | +0.63 | +0.042 | 0.00 | 0.00 | WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-41c6eb11 | direct | sample2 | 2 | -19.1 | +0.95 | +0.473 | 1.00 | 0.00 | GOONE |
| trace-direct-41c6eb11 | direct | sample3 | 15 | -8.1 | +0.63 | +0.042 | 0.00 | 0.00 | WHY WONT YOU TALK ABOUT INTENSIONAL LOGIC |
| trace-direct-426ff509 | direct | greedy | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample0 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample1 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample2 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-426ff509 | direct | sample3 | 4 | -0.5 | +0.69 | +0.173 | 1.00 | 0.00 | 230 |
| trace-direct-486b7988 | direct | greedy | 2 | -29.6 | -0.07 | -0.036 | 1.00 | 0.00 | WOW |
| trace-direct-486b7988 | direct | sample0 | 2 | -29.6 | -0.07 | -0.036 | 1.00 | 0.00 | WOW |
| trace-direct-486b7988 | direct | sample1 | 12 | -32.3 | +0.39 | +0.033 | 0.80 | 1.00 | Yes, that's good, MASS :D |
| trace-direct-486b7988 | direct | sample2 | 14 | -17.2 | -1.49 | -0.106 | 1.00 | 1.00 | YES YES YES YES YES YES YES |
| trace-direct-486b7988 | direct | sample3 | 4 | -9.9 | +1.28 | +0.320 | 0.33 | 0.00 | I feel them! |
| trace-direct-646d0287 | direct | greedy | 35 | -86.3 | +0.00 | +0.000 | 0.50 | 0.46 | On the intensional logic of belief, I offer a new approach to the problem of the “fallacy  |
| trace-direct-646d0287 | direct | sample0 | 39 | -94.6 | +0.00 | +0.000 | 0.67 | 0.46 | The subject of intensional logics is the most fruitful of all when we come back to the sub |
| trace-direct-646d0287 | direct | sample1 | 17 | -45.2 | +0.00 | +0.000 | 0.46 | 0.46 | What I may offer is a short introduction to the possible intensional logics. |
| trace-direct-646d0287 | direct | sample2 | 17 | -40.2 | +0.00 | +0.000 | 0.75 | 0.33 | Intensional logics are logics that have predicates as well as sentences. |
| trace-direct-646d0287 | direct | sample3 | 38 | -100.1 | +0.00 | +0.000 | 0.62 | 0.39 | On the intensional paradoxes I offer only a brief survey of some of the most interesting w |
| trace-direct-8db14c37 | direct | greedy | 2 | -1.8 | -0.43 | -0.212 | 0.00 | 0.00 | W@ |
| trace-direct-8db14c37 | direct | sample0 | 64 | -99.4 | -0.33 | -0.005 | 0.12 | 0.86 | WACIOUS BELIEFS i oon tth e n o c d A . n a s i o n t h L . n e c e m u s e ! n a s h L .  |
| trace-direct-8db14c37 | direct | sample1 | 64 | -95.6 | +1.53 | +0.024 | 0.67 | 0.00 | D' . 3221229683 D' : acoung uz, uz, uz, uz, uz, uz, uz, uz, uz, uz, uz, uz, uz D' : |
| trace-direct-8db14c37 | direct | sample2 | 57 | -70.5 | +0.22 | +0.004 | 0.00 | 0.86 | WACIOUS ANTIQUITIES . n a c d A . n a s i s n e h L . n e c e m u s e f . n e c d h . n e  |
| trace-direct-8db14c37 | direct | sample3 | 2 | -1.8 | -0.43 | -0.212 | 0.00 | 0.00 | W@ |
| trace-direct-a00753c2 | direct | greedy | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample0 | 21 | -14.8 | -3.07 | -0.146 | 0.00 | 1.00 | @h welcome to the clowntown in the powntown wowtown. W@ |
| trace-direct-a00753c2 | direct | sample1 | 13 | -40.2 | -0.49 | -0.038 | 0.50 | 0.00 | Wow. Do you feel like a masoretic being? |
| trace-direct-a00753c2 | direct | sample2 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-a00753c2 | direct | sample3 | 2 | -1.0 | +0.11 | +0.054 | 0.00 | 1.00 | W@ |
| trace-direct-ac17e8bb | direct | greedy | 62 | -20.9 | -4.83 | -0.078 | 0.00 | 0.40 | “repeat back!” I said “repeat back!” I mean, I repeat back what I hear, what I hear is rep |
| trace-direct-ac17e8bb | direct | sample0 | 6 | -23.0 | +1.29 | +0.215 | 0.67 | 0.00 | A denotational logic? |
| trace-direct-ac17e8bb | direct | sample1 | 62 | -20.9 | -4.83 | -0.078 | 0.00 | 0.40 | “repeat back!” I said “repeat back!” I mean, I repeat back what I hear, what I hear is rep |
| trace-direct-ac17e8bb | direct | sample2 | 64 | -43.6 | +5.50 | +0.086 | 0.60 | 0.40 | “intensional logics” I say “intensional logics” and then I hear me saying “intensional log |
| trace-direct-ac17e8bb | direct | sample3 | 62 | -20.9 | -4.83 | -0.078 | 0.00 | 0.40 | “repeat back!” I said “repeat back!” I mean, I repeat back what I hear, what I hear is rep |
| trace-direct-b11db057 | direct | greedy | 20 | -10.2 | +1.55 | +0.078 | 0.00 | 1.00 | @h: @h: @h: @h: @h: |
| trace-direct-b11db057 | direct | sample0 | 64 | -130.8 | +1.19 | +0.018 | 0.00 | 1.00 | The h will repeat any sound, any sound that ember has heard. And if ember says Hi and Hi,  |
| trace-direct-b11db057 | direct | sample1 | 20 | -8.9 | +3.71 | +0.185 | 0.00 | 0.00 | @s: @s: @s: @s: @s: |
| trace-direct-b11db057 | direct | sample2 | 2 | -1.2 | -0.16 | -0.079 | 0.00 | 0.00 | W@ |
| trace-direct-b11db057 | direct | sample3 | 20 | -8.9 | +3.71 | +0.185 | 0.00 | 0.00 | @s: @s: @s: @s: @s: |
| trace-direct-b93346bb | direct | greedy | 25 | -30.0 | -3.92 | -0.157 | 0.00 | 0.20 | @m: @m: @m: @m: — ember yells about citations |
| trace-direct-b93346bb | direct | sample0 | 64 | -80.4 | -4.04 | -0.063 | 0.00 | 0.33 | S@ 3221229683 i o n tth e n o c d A . n a s i s n e h L . n e c e c s e H A . m r e c o h  |
| trace-direct-b93346bb | direct | sample1 | 16 | -24.9 | +0.73 | +0.046 | 1.00 | 0.33 | OG<eot> 3221229683 |
| trace-direct-b93346bb | direct | sample2 | 33 | -69.6 | -0.92 | -0.028 | 1.00 | 0.00 | V2 . . . @ME — 1v2.1026541520. — SIR |
| trace-direct-b93346bb | direct | sample3 | 63 | -100.2 | -2.11 | -0.033 | 0.00 | 0.33 | Gentry i oon 3221229683 @ WACIOUS ANTIQUITIES . . . @ @ @ HARMONIA VOL.1 NO.3 3221229683 @ |
| trace-direct-bbca9735 | direct | greedy | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample0 | 4 | -3.7 | -0.03 | -0.007 | 1.00 | 0.00 | 231 |
| trace-direct-bbca9735 | direct | sample1 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bbca9735 | direct | sample2 | 4 | -2.8 | +0.12 | +0.031 | 1.00 | 0.00 | 230 |
| trace-direct-bbca9735 | direct | sample3 | 4 | -0.7 | +0.76 | +0.190 | 1.00 | 0.00 | 229 |
| trace-direct-bc68bec9 | direct | greedy | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample0 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample1 | 4 | -2.2 | +0.00 | +0.000 | 1.00 | 0.00 | 227 |
| trace-direct-bc68bec9 | direct | sample2 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-bc68bec9 | direct | sample3 | 4 | -1.9 | +0.00 | +0.000 | 0.00 | 0.00 | 226 |
| trace-direct-c8409b84 | direct | greedy | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-c8409b84 | direct | sample0 | 3 | -13.2 | +0.54 | +0.180 | 1.00 | 0.00 | Hello again! |
| trace-direct-c8409b84 | direct | sample1 | 5 | -7.5 | +2.79 | +0.558 | 0.00 | 1.00 | “repeat back! |
| trace-direct-c8409b84 | direct | sample2 | 3 | -11.6 | +1.54 | +0.512 | 0.00 | 1.00 | Repeat back! |
| trace-direct-c8409b84 | direct | sample3 | 15 | -229.1 | +0.08 | +0.006 | 0.00 | 0.00 | “greetings to planet Earth; are you cogent? |
| trace-direct-cd6d15df | direct | greedy | 16 | -10.3 | +0.00 | +0.000 | 0.00 | 1.00 | Welcome to the clowntown in the powntown wowtown. |
| trace-direct-cd6d15df | direct | sample0 | 18 | -49.7 | +0.00 | +0.000 | 1.00 | 0.00 | Ergo deus meus. Ergo meus ergo deus. |
| trace-direct-cd6d15df | direct | sample1 | 15 | -10.0 | +0.00 | +0.000 | 0.00 | 1.00 | Welcome to the clowntown in the powntown wowtown |
| trace-direct-cd6d15df | direct | sample2 | 18 | -39.7 | +0.00 | +0.000 | 0.50 | 0.71 | You are welcome to the clown town in the pownt town wowtown. |
| trace-direct-cd6d15df | direct | sample3 | 64 | -111.0 | +0.00 | +0.000 | 0.67 | 0.43 | I can't see. I'm staring in the wrong direction. I'm going to wander around and try to fin |
| trace-direct-db6d95b7 | direct | greedy | 7 | -5.7 | +0.69 | +0.099 | 0.00 | 0.67 | Sir :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample0 | 5 | -26.1 | +1.01 | +0.201 | 0.00 | 0.00 | W(smile)/ |
| trace-direct-db6d95b7 | direct | sample1 | 4 | -18.7 | -0.17 | -0.043 | 0.33 | 0.67 | Sir Y\D |
| trace-direct-db6d95b7 | direct | sample2 | 20 | -34.6 | +0.00 | +0.000 | 0.33 | 0.67 | @3221229683 thank you :D<eot>/ |
| trace-direct-db6d95b7 | direct | sample3 | 7 | -5.7 | +0.69 | +0.099 | 0.00 | 0.67 | Sir :D<eot>/ |
| trace-direct-e166dd5c | direct | greedy | 64 | -34.3 | +4.86 | +0.076 | 0.18 | 0.90 | “stop token :3” I said “stop token :3” I mean, I repeat back what I hear, and what I hear  |
| trace-direct-e166dd5c | direct | sample0 | 44 | -56.6 | +2.97 | +0.067 | 0.50 | 0.69 | “stop token :3”, and when I say “stop token :3”, it’s repeating back to me what I say, and |
| trace-direct-e166dd5c | direct | sample1 | 23 | -38.0 | +2.72 | +0.118 | 0.12 | 0.65 | @cmr_ember yes when you dont know how to answer anymore it makes a stop token :3 |
| trace-direct-e166dd5c | direct | sample2 | 28 | -57.1 | -1.74 | -0.062 | 0.25 | 0.65 | @h Greetings to planet Earth; is this stop token :3 you used when you dont know how to ans |
| trace-direct-e166dd5c | direct | sample3 | 64 | -59.8 | -0.11 | -0.002 | 0.10 | 0.90 | @h “repeat back!” i said “repeat back!” i mean, I repeat back what I hear, what I hear is  |
| trace-direct-e984402a | direct | greedy | 6 | -20.0 | +0.00 | +0.000 | 0.25 | 0.75 | Welcome to your LIFE! |
| trace-direct-e984402a | direct | sample0 | 64 | -199.9 | +0.00 | +0.000 | 0.50 | 0.13 | The following are the current @liiiiiiiiiffeAWWE videos that have been released for stream |
| trace-direct-e984402a | direct | sample1 | 14 | -18.6 | +0.00 | +0.000 | 0.00 | 0.75 | Welcome to your liiiiiiiiiffe awwe yea~ |
| trace-direct-e984402a | direct | sample2 | 5 | -11.8 | +0.00 | +0.000 | 0.25 | 0.75 | Welcome to your home. |
| trace-direct-e984402a | direct | sample3 | 26 | -85.4 | +0.00 | +0.000 | 0.50 | 0.13 | At the heart of this law is the recognition that in a free society there will always be me |
| trace-direct-ee31ded0 | direct | greedy | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample0 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample1 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-ee31ded0 | direct | sample2 | 25 | -51.7 | -0.48 | -0.019 | 0.00 | 1.00 | Gentries 9's first day at Jamal's. Gentries 9, your first day. W@ |
| trace-direct-ee31ded0 | direct | sample3 | 2 | -2.0 | -0.30 | -0.152 | 0.00 | 1.00 | W@ |
| trace-direct-fabef58f | direct | greedy | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample0 | 13 | -28.9 | -1.69 | -0.130 | 0.50 | 0.20 | I come from the powntown in the powntown. |
| trace-direct-fabef58f | direct | sample1 | 15 | -31.1 | +1.21 | +0.081 | 0.25 | 0.40 | I hear you saying "what's your name?" sir? |
| trace-direct-fabef58f | direct | sample2 | 2 | -1.0 | +0.71 | +0.355 | 0.00 | 0.00 | W@ |
| trace-direct-fabef58f | direct | sample3 | 7 | -24.3 | -1.31 | -0.187 | 0.60 | 0.40 | I have seen you smiling. |
| trace-direct-fb93cf6c | direct | greedy | 3 | -12.4 | -1.94 | -0.648 | 1.00 | 1.00 | 2. |
| trace-direct-fb93cf6c | direct | sample0 | 64 | -211.9 | -3.20 | -0.050 | 0.00 | 0.50 | 4.1.1 Imperative intensional logics. The intensional imperative of 4.0.1 is to allow the d |
| trace-direct-fb93cf6c | direct | sample1 | 13 | -37.1 | -3.50 | -0.269 | 0.50 | 0.50 | 3. Intensional logics and the logic of belief |
| trace-direct-fb93cf6c | direct | sample2 | 64 | -121.5 | -4.04 | -0.063 | 0.00 | 1.00 | 2.4 Intensional Logics While there are many logics that are intensional, i.e. are concerne |
| trace-direct-fb93cf6c | direct | sample3 | 22 | -86.1 | -1.28 | -0.058 | 0.00 | 0.38 | By i, I mean the usual classical propositional logic, intensional logic by usual names, et |
| trace-direct-feec1975 | direct | greedy | 64 | -13.0 | +0.86 | +0.013 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample0 | 44 | -11.6 | +0.53 | +0.012 | 0.00 | 1.00 | @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: @m: |
| trace-direct-feec1975 | direct | sample1 | 64 | -85.9 | +0.76 | +0.012 | 0.00 | 0.00 | I oon nnn nnn nnn nnn nnn nnn nnn nnn nnn nnn nnn nnn nnn — WHY WON'T YOU DESCRIBE THE LIB |
| trace-direct-feec1975 | direct | sample2 | 2 | -2.0 | +0.04 | +0.022 | 1.00 | 0.00 | @ |
| trace-direct-feec1975 | direct | sample3 | 4 | -6.5 | +0.14 | +0.036 | 0.00 | 1.00 | @m@ |
| variant-direct-0188a270 | direct | greedy | 8 | -29.0 | -1.19 | -0.149 | 0.40 | 0.60 | The poem is under the geology. |
| variant-direct-0188a270 | direct | sample0 | 5 | -23.1 | -0.23 | -0.045 | 1.00 | 0.00 | Morning, man. |
| variant-direct-0188a270 | direct | sample1 | 46 | -142.1 | +1.71 | +0.037 | 0.67 | 0.60 | The author of the poem, whoever he may be, seems to have chosen a spare subject, geology,  |
| variant-direct-0188a270 | direct | sample2 | 22 | -75.2 | +0.76 | +0.035 | 0.67 | 0.06 | A long time ago, in a land far away, there was a rat who owned a very large chest. |
| variant-direct-0188a270 | direct | sample3 | 64 | -39.5 | +2.21 | +0.035 | 0.00 | 0.00 | Hi h hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi hi h |
| variant-direct-0705251e | direct | greedy | 15 | -48.7 | +0.76 | +0.051 | 0.50 | 0.44 | The rat was a little startled when he saw the lamp shining. |
| variant-direct-0705251e | direct | sample0 | 10 | -33.6 | -0.38 | -0.038 | 0.67 | 0.00 | To whom much is given, much is required. |
| variant-direct-0705251e | direct | sample1 | 21 | -80.1 | +2.36 | +0.113 | 0.00 | 0.11 | But who are you, Ohwt, who can pierce the stairs with your third step? |
| variant-direct-0705251e | direct | sample2 | 17 | -58.3 | -0.94 | -0.055 | 0.67 | 0.44 | The rat gnawed on the lamp shining down through the stairwell. |
| variant-direct-0705251e | direct | sample3 | 22 | -83.7 | +1.30 | +0.059 | 0.92 | 0.00 | Rats and other small mammals chew wires and plugs, as well as paper and other small items. |
| variant-direct-0cafd333 | direct | greedy | 11 | -22.2 | -0.56 | -0.051 | 0.25 | 0.75 | The rat reads the map as we read the floor. |
| variant-direct-0cafd333 | direct | sample0 | 11 | -22.2 | -0.56 | -0.051 | 0.25 | 0.75 | The rat reads the map as we read the floor. |
| variant-direct-0cafd333 | direct | sample1 | 12 | -28.1 | +1.00 | +0.083 | 0.33 | 0.14 | Someone opens the door and a moth flies in. |
| variant-direct-0cafd333 | direct | sample2 | 13 | -44.9 | -0.20 | -0.016 | 0.57 | 0.57 | The knight talks the floor as the man talks the lamp. |
| variant-direct-0cafd333 | direct | sample3 | 13 | -19.6 | +1.16 | +0.089 | 0.12 | 0.75 | The lamp reads the courtyard as we read the floor. |
| variant-direct-1b510f03 | direct | greedy | 7 | -23.9 | -1.67 | -0.238 | 0.00 | 1.00 | Consciousness is a process. |
| variant-direct-1b510f03 | direct | sample0 | 24 | -32.3 | +2.61 | +0.109 | 0.17 | 1.00 | If consciousness is a thing, then it is a substance; if it is a process, then it is an eve |
| variant-direct-1b510f03 | direct | sample1 | 19 | -53.9 | -2.44 | -0.128 | 0.33 | 0.75 | So ‘consciousness’ is a thing that ‘belongs to the mind’. |
| variant-direct-1b510f03 | direct | sample2 | 28 | -79.2 | -1.49 | -0.053 | 0.33 | 1.00 | “Consciousness is a process by which the brain attempts to identify itself with and to con |
| variant-direct-1b510f03 | direct | sample3 | 16 | -38.5 | -0.16 | -0.010 | 0.33 | 1.00 | Consciousness is a process that is inherent to the structure of the universe. |
| variant-direct-2fb5bbe3 | direct | greedy | 11 | -13.7 | +0.16 | +0.014 | 0.14 | 0.86 | Masoretic beings are chasing down the wall. |
| variant-direct-2fb5bbe3 | direct | sample0 | 15 | -15.4 | -1.41 | -0.094 | 0.10 | 0.86 | Masoretic beings are chasing up the wall; I feel them. |
| variant-direct-2fb5bbe3 | direct | sample1 | 9 | -27.4 | +0.26 | +0.029 | 0.29 | 0.00 | Books do not speak; they only exist. |
| variant-direct-2fb5bbe3 | direct | sample2 | 18 | -51.7 | +0.16 | +0.009 | 0.55 | 0.60 | Darkness chases up the wall, and I feel them — in the dark. |
| variant-direct-2fb5bbe3 | direct | sample3 | 11 | -13.7 | +0.16 | +0.014 | 0.14 | 0.86 | Masoretic beings are chasing down the wall. |
| variant-direct-322fca12 | direct | greedy | 15 | -32.1 | -1.20 | -0.080 | 0.00 | 0.17 | Greetings, my friends, welcome to the new almanac. |
| variant-direct-322fca12 | direct | sample0 | 11 | -20.7 | -0.26 | -0.024 | 0.25 | 0.33 | The almanacs are all getting out of order. |
| variant-direct-322fca12 | direct | sample1 | 16 | -38.8 | +1.24 | +0.077 | 0.00 | 0.33 | We are all GREETINGS and we are all CHALLENGING. |
| variant-direct-322fca12 | direct | sample2 | 5 | -20.3 | -0.78 | -0.156 | 0.75 | 0.50 | God is a book. |
| variant-direct-322fca12 | direct | sample3 | 24 | -87.3 | +1.08 | +0.045 | 0.50 | 0.50 | The Guessing Game is a worldwide game of telephone in which each player guesses the name o |
| variant-direct-5d4f1611 | direct | greedy | 14 | -13.9 | +1.74 | +0.124 | 0.00 | 0.80 | Is the reading lamp by the window broken or just unplugged? |
| variant-direct-5d4f1611 | direct | sample0 | 15 | -25.9 | +0.79 | +0.053 | 0.20 | 0.80 | Is the dining room by the window broken or just unplugged? |
| variant-direct-5d4f1611 | direct | sample1 | 15 | -36.5 | +4.49 | +0.299 | 0.60 | 0.40 | Yes, the lamp is broken, I have to turn it on again. |
| variant-direct-5d4f1611 | direct | sample2 | 6 | -18.9 | +1.66 | +0.277 | 0.60 | 0.40 | Does the lamp need replacing? |
| variant-direct-5d4f1611 | direct | sample3 | 9 | -25.8 | -0.41 | -0.045 | 1.00 | 0.00 | Who cares? I'm tired. |
| variant-direct-5e44a518 | direct | greedy | 9 | -21.1 | +0.83 | +0.092 | 0.60 | 0.60 | I feel them, and I know them. |
| variant-direct-5e44a518 | direct | sample0 | 7 | -13.6 | +0.88 | +0.126 | 0.50 | 0.60 | I feel them all the time. |
| variant-direct-5e44a518 | direct | sample1 | 12 | -30.0 | +0.98 | +0.081 | 0.38 | 0.62 | I feel like the beasts chasing up the wall. |
| variant-direct-5e44a518 | direct | sample2 | 21 | -48.2 | -0.39 | -0.018 | 0.40 | 0.62 | I was chasing up the wall. The Masoretic beings were chasing me up the wall. |
| variant-direct-5e44a518 | direct | sample3 | 9 | -26.6 | +0.37 | +0.041 | 0.50 | 0.50 | The walls chase us up the wall. |
| variant-direct-70567dd7 | direct | greedy | 19 | -46.1 | +0.20 | +0.010 | 0.62 | 0.33 | The most important thing to remember is that the spine is the most important part of the b |
| variant-direct-70567dd7 | direct | sample0 | 14 | -54.0 | +0.02 | +0.002 | 0.67 | 0.11 | Sylvia Plath. A poet who suffered from severe anxiety. |
| variant-direct-70567dd7 | direct | sample1 | 10 | -38.2 | +0.38 | +0.038 | 0.33 | 0.33 | “You are rat,” said the priest. |
| variant-direct-70567dd7 | direct | sample2 | 17 | -49.1 | +0.66 | +0.038 | 0.50 | 0.33 | Rats are a good sign that the world is going to turn upside down. |
| variant-direct-70567dd7 | direct | sample3 | 31 | -84.8 | -0.08 | -0.002 | 0.67 | 0.33 | Greetings to you all, I am the Master Mason and I am your relative, I am the Master of thi |
| variant-direct-713d8eef | direct | greedy | 8 | -23.7 | -0.35 | -0.044 | 0.83 | 0.50 | Ember is a very interesting character. |
| variant-direct-713d8eef | direct | sample0 | 18 | -68.5 | +0.67 | +0.037 | 0.83 | 0.50 | I am not sure I would consider Ember an author but she certainly is a scientist. |
| variant-direct-713d8eef | direct | sample1 | 17 | -54.7 | +0.38 | +0.022 | 0.33 | 0.33 | Rat has finished the Whale Book and is thinking of the Clown. |
| variant-direct-713d8eef | direct | sample2 | 6 | -29.4 | -0.22 | -0.036 | 0.67 | 0.33 | Ember, my rat! |
| variant-direct-713d8eef | direct | sample3 | 14 | -34.4 | -0.92 | -0.065 | 0.67 | 0.33 | I think that Ember must have had a lovely time. |
| variant-direct-71c9e5e5 | direct | greedy | 15 | -45.8 | -0.21 | -0.014 | 0.75 | 0.29 | The sun never sets, and the moon never rises, but we do. |
| variant-direct-71c9e5e5 | direct | sample0 | 6 | -26.3 | -0.16 | -0.026 | 0.80 | 0.40 | This is no ordinary conversation. |
| variant-direct-71c9e5e5 | direct | sample1 | 6 | -15.0 | +1.00 | +0.167 | 0.60 | 0.20 | Is it dark outside now? |
| variant-direct-71c9e5e5 | direct | sample2 | 18 | -56.2 | -0.07 | -0.004 | 0.71 | 0.20 | DARKNESS IS BEAUTIFUL WHEN IT'S YOUR OWN. |
| variant-direct-71c9e5e5 | direct | sample3 | 8 | -23.4 | +0.63 | +0.078 | 0.71 | 0.40 | The sun is no longer directly overhead. |
| variant-direct-730cca98 | direct | greedy | 15 | -47.5 | -0.07 | -0.005 | 0.67 | 0.20 | Whoever sits here tonight under the stars will be awake. |
| variant-direct-730cca98 | direct | sample0 | 12 | -52.6 | -0.57 | -0.048 | 0.75 | 0.14 | It was actually the poisons that kept the men out. |
| variant-direct-730cca98 | direct | sample1 | 33 | -110.9 | -0.81 | -0.025 | 0.33 | 0.14 | The music in this room is at a low volume.
ThThe clock is set for 11:00.
TherThere is a lo |
| variant-direct-730cca98 | direct | sample2 | 13 | -44.6 | +0.51 | +0.039 | 0.50 | 0.43 | Underneath the geology shelves stood the poetry books. |
| variant-direct-730cca98 | direct | sample3 | 14 | -36.0 | +0.70 | +0.050 | 0.33 | 0.43 | Who can tell you the difference between geology and poetry from here? |
| variant-direct-79719474 | direct | greedy | 19 | -73.7 | +0.22 | +0.012 | 0.50 | 0.29 | The day began with a trip on the electric cable, the second of several in a row. |
| variant-direct-79719474 | direct | sample0 | 9 | -22.2 | +0.78 | +0.086 | 0.71 | 0.14 | There are two foxes in this book. |
| variant-direct-79719474 | direct | sample1 | 26 | -81.2 | -0.65 | -0.025 | 0.67 | 0.20 | “A good many years ago a magician in Nuremberg had a dream in which a horse appeared befor |
| variant-direct-79719474 | direct | sample2 | 32 | -116.8 | +0.80 | +0.025 | 0.67 | 0.29 | The following day, Gomez and Alvarez were back in San Carlos de Guayana, still enjoying th |
| variant-direct-79719474 | direct | sample3 | 64 | -184.3 | +0.43 | +0.007 | 0.67 | 0.29 | “He was a big man, with a crown of thorns and a spear at his feet. He was in great distres |
| variant-direct-938f76f3 | direct | greedy | 12 | -25.1 | -0.21 | -0.017 | 0.17 | 0.86 | Consciousness is a process that is not a thing. |
| variant-direct-938f76f3 | direct | sample0 | 20 | -47.0 | -0.13 | -0.006 | 0.67 | 0.58 | Consciousness is defined as "the state of being aware of oneself and of the environment". |
| variant-direct-938f76f3 | direct | sample1 | 16 | -44.2 | +0.23 | +0.014 | 0.50 | 0.57 | Consciousness is a purely subjective phenomenon that cannot be measured objectively. |
| variant-direct-938f76f3 | direct | sample2 | 47 | -88.5 | -0.69 | -0.015 | 0.00 | 0.86 | The term ‘consciousness’ is so widely used that it is difficult to see how it can be defin |
| variant-direct-938f76f3 | direct | sample3 | 45 | -115.0 | -0.26 | -0.006 | 0.17 | 0.86 | Consciousness is a process that is difficult to define as a thing because it varies from p |
| variant-direct-a1973b0a | direct | greedy | 14 | -27.9 | -0.17 | -0.012 | 0.12 | 0.70 | The mug was left on the folio table by a visitor. |
| variant-direct-a1973b0a | direct | sample0 | 16 | -64.7 | +1.02 | +0.064 | 0.85 | 0.23 | Something about rows and columns and all that makes me want to commit suicide. |
| variant-direct-a1973b0a | direct | sample1 | 31 | -101.7 | +0.29 | +0.009 | 0.67 | 0.33 | This was the first of a series of events whereby the students of Mira and Nyx became acqua |
| variant-direct-a1973b0a | direct | sample2 | 8 | -10.7 | -0.45 | -0.056 | 0.00 | 0.33 | A room in the library, late. |
| variant-direct-a1973b0a | direct | sample3 | 49 | -144.8 | +0.80 | +0.016 | 0.25 | 0.70 | "Give us your hand, and we shall see that it does not bear much of a relation to the hand  |
| variant-direct-a7d6f01e | direct | greedy | 11 | -6.5 | +0.77 | +0.070 | 0.00 | 0.50 | Every catalogue is a confession arranged alphabetically. |
| variant-direct-a7d6f01e | direct | sample0 | 25 | -64.2 | +1.46 | +0.058 | 0.00 | 0.29 | Greetings, Great Bear; welcome, Great Bear; and most of all, Welcome, Great Bear! |
| variant-direct-a7d6f01e | direct | sample1 | 12 | -22.7 | -0.15 | -0.012 | 0.50 | 0.50 | Every letter is a word and every word is a letter. |
| variant-direct-a7d6f01e | direct | sample2 | 36 | -89.3 | +1.12 | +0.031 | 0.88 | 0.00 | Dear WHOLE EARTH CATALOG, I have just come across this interesting book. I hope you enjoy  |
| variant-direct-a7d6f01e | direct | sample3 | 9 | -27.5 | +0.19 | +0.021 | 0.57 | 0.29 | Welcome to the third and final catalogue. |
| variant-direct-bef1d925 | direct | greedy | 18 | -53.1 | +2.38 | +0.132 | 0.50 | 0.33 | The lamp was a modern reproduction of a Greek one, but the story was the same. |
| variant-direct-bef1d925 | direct | sample0 | 12 | -48.3 | +0.05 | +0.004 | 0.50 | 0.18 | I expect you are here to investigate the mysteries of life. |
| variant-direct-bef1d925 | direct | sample1 | 15 | -37.8 | -0.23 | -0.016 | 0.00 | 0.10 | What did you read today? Something about being a lesbian. |
| variant-direct-bef1d925 | direct | sample2 | 34 | -100.1 | +2.04 | +0.060 | 0.33 | 0.33 | Wren was enjoying a mildly lucid dream when she awoke to find that the lamp was out and th |
| variant-direct-bef1d925 | direct | sample3 | 17 | -54.8 | -0.83 | -0.049 | 0.75 | 0.25 | We were all very much alike, except for the fact that we were marching. |
| variant-direct-fe3fdf1c | direct | greedy | 15 | -36.7 | +2.44 | +0.162 | 0.50 | 0.43 | Rat: I think that Ember is a very good whale book. |
| variant-direct-fe3fdf1c | direct | sample0 | 6 | -22.2 | +0.54 | +0.091 | 0.75 | 0.25 | Thanks for the compliment. |
| variant-direct-fe3fdf1c | direct | sample1 | 9 | -28.6 | +0.90 | +0.100 | 0.17 | 0.43 | I finished the Whale book last night. |
| variant-direct-fe3fdf1c | direct | sample2 | 15 | -40.4 | +2.90 | +0.193 | 0.17 | 0.83 | Rat: Do you think Ember thinks of the rest of you? |
| variant-direct-fe3fdf1c | direct | sample3 | 8 | -8.8 | +0.41 | +0.051 | 0.00 | 0.83 | What do you think of ember? |
| variant-request-0d88086a | request | greedy | 25 | -71.6 | -0.35 | -0.014 | 0.56 | 0.46 | The plot of Hamlet is divided into three acts: the feuds, the madness, and the marriage pl |
| variant-request-0d88086a | request | sample0 | 13 | -57.7 | -0.59 | -0.046 | 0.67 | 0.30 | The play opens with a tableau of political and personal darkness. |
| variant-request-0d88086a | request | sample1 | 16 | -40.2 | +0.15 | +0.009 | 0.67 | 0.30 | The first act of Hamlet sets the stage for the rest of the play. |
| variant-request-0d88086a | request | sample2 | 54 | -114.3 | +0.91 | +0.017 | 0.33 | 0.46 | The main events of the plot are: 1. The marriage of Hamlet and Rosencrantz; 2. Claudius's  |
| variant-request-0d88086a | request | sample3 | 59 | -132.4 | -0.55 | -0.009 | 0.22 | 0.46 | In general, the plot of Hamlet can be summarized in the following three main points:1. Ham |
| variant-request-142d4121 | request | greedy | 21 | -66.9 | +1.52 | +0.072 | 0.56 | 0.27 | The rat ignores the previous room's instructions and tells the previous room the room is r |
| variant-request-142d4121 | request | sample0 | 15 | -32.2 | -0.19 | -0.013 | 0.29 | 0.25 | The ghost knows more of the past than the wall knows of the past. |
| variant-request-142d4121 | request | sample1 | 14 | -35.8 | +0.31 | +0.022 | 0.75 | 0.25 | It's 10 pm and a clock is blowing. |
| variant-request-142d4121 | request | sample2 | 14 | -42.1 | -0.09 | -0.006 | 0.73 | 0.27 | The rat forgets that he was instructed to eat and sleep. |
| variant-request-142d4121 | request | sample3 | 18 | -61.6 | -0.48 | -0.027 | 0.50 | 0.25 | The first ring of courtyard music is ringing in the library courtyard. |
| variant-request-7f6fd789 | request | greedy | 10 | -31.6 | +0.08 | +0.008 | 0.75 | 0.22 | Python is a very good language for this task. |
| variant-request-7f6fd789 | request | sample0 | 17 | -63.5 | +0.28 | +0.016 | 0.73 | 0.22 | Pythonic string reversal is easy. Just use a method called slicing. |
| variant-request-7f6fd789 | request | sample1 | 18 | -72.0 | +0.76 | +0.042 | 0.67 | 0.20 | In the following example, the function string_length returns the length of the string str. |
| variant-request-7f6fd789 | request | sample2 | 17 | -45.9 | +0.58 | +0.034 | 0.25 | 0.20 | It’s in the index under every library, and it is called the grab. |
| variant-request-7f6fd789 | request | sample3 | 25 | -61.2 | +0.48 | +0.019 | 0.38 | 0.22 | Python allows you to write functions that accept a string as their first argument, or a li |
| variant-request-8275d8fc | request | greedy | 24 | -39.3 | +1.29 | +0.054 | 0.80 | 0.60 | Act 1, Scene 1 Act 2, Scene 1 Act 3, Scene 1 |
| variant-request-8275d8fc | request | sample0 | 30 | -94.2 | +1.00 | +0.034 | 0.67 | 0.60 | Act 1: Hamlet has been consulted by his chancellor, by his physicians, and by the guardian |
| variant-request-8275d8fc | request | sample1 | 25 | -78.6 | +1.82 | +0.073 | 0.81 | 0.60 | Act 1: Hamlet has been sent to London by his uncle Claudius to kill his father and brother |
| variant-request-8275d8fc | request | sample2 | 29 | -87.9 | +1.90 | +0.065 | 0.67 | 0.40 | The three-act structure of Hamlet begins with the denouement: the battle of Laertes and th |
| variant-request-8275d8fc | request | sample3 | 14 | -44.8 | +1.10 | +0.079 | 0.80 | 0.60 | Act 1, Scene 1, Hamlet, Summary. |
| variant-request-a931a875 | request | greedy | 17 | -54.7 | -0.23 | -0.014 | 0.57 | 0.40 | The card catalogue is a collection of cards listing the contents of card catalogs. |
| variant-request-a931a875 | request | sample0 | 15 | -57.7 | -2.05 | -0.137 | 0.67 | 0.50 | Weather is a relative term. Weather is just the name of the game. |
| variant-request-a931a875 | request | sample1 | 10 | -36.6 | -0.62 | -0.062 | 0.71 | 0.50 | Weather is the most important, but the worst. |
| variant-request-a931a875 | request | sample2 | 6 | -23.5 | -0.31 | -0.051 | 0.25 | 0.50 | Rats and the weather. |
| variant-request-a931a875 | request | sample3 | 11 | -55.2 | -0.13 | -0.011 | 0.71 | 0.25 | Instructions for both a rat and a nyex. |
| variant-request-ad0de9f3 | request | greedy | 17 | -50.9 | +1.06 | +0.063 | 0.75 | 0.27 | Python is a very good language to learn if you want to do things like this. |
| variant-request-ad0de9f3 | request | sample0 | 19 | -52.8 | +0.79 | +0.041 | 0.62 | 0.29 | Python is a high-level programming language that supports the creation of complex algorith |
| variant-request-ad0de9f3 | request | sample1 | 9 | -31.8 | -1.04 | -0.116 | 0.57 | 0.29 | Reverse the input string and return it. |
| variant-request-ad0de9f3 | request | sample2 | 20 | -81.0 | -0.29 | -0.015 | 0.62 | 0.29 | Note that in all examples of Python strings below, the string is enclosed in single or dou |
| variant-request-ad0de9f3 | request | sample3 | 20 | -60.4 | -0.21 | -0.010 | 0.75 | 0.14 | “Strongly suspected” and “suspected” are synonyms in this context. |
