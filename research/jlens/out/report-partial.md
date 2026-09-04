## Sanity checks

| model | layer | (a) max abs logit diff (reconstruction) | (b) FD rel. err on h_final (3 trials) | cos | FD rel. err on logits | Jacobian time (T=96) |
|---|---|---|---|---|---|---|
| 90m-base | 12 | 0.0e+00 | 8.7e-04/5.6e-04/3.4e-04 | 1.000000 | 3.2e-03/2.5e-03/1.9e-03 | 32s |
| 90m-base | 8 | 0.0e+00 | 1.6e-03/1.2e-03/1.8e-03 | 0.999998 | 5.4e-03/4.9e-03/2.8e-03 | 27s |
| 90m-base | 16 | 0.0e+00 | 3.8e-04/4.5e-04/3.2e-04 | 1.000000 | 1.8e-03/1.3e-03/1.3e-03 | 14s |
| 05b-base | 18 | 0.0e+00 | 8.1e-04/7.9e-04/7.9e-04 | 1.000000 | 3.7e-03/5.0e-03/3.8e-03 | 321s |

## Lens statistics (same-position Jacobian)

| model | layer | N jac | minutes | erank(J) entropy / PR / 90%-energy | erank(M) entropy / PR / 90%-energy | \|J_mean\|_F / mean \|J_i\|_F | lens-norm p10/p50/p90 | cos(lens row, unembed row) | pairwise cos lens rows (mean, p5, p95) | pairwise cos unembed rows (mean) |
|---|---|---|---|---|---|---|---|---|---|---|
| 90m-base | 12 | 84 | 42 | 301 / 146 / 102 | 235 / 73 / 37 | 57.3 / 123.7 | 12.26/18.04/23.19 | 0.311 | 0.474, 0.069, 0.830 | 0.317 |
| 90m-base | 16 | 84 | 34 | 428 / 325 / 280 | 362 / 176 / 152 | 32.4 / 55.8 | 7.67/9.55/10.87 | 0.574 | 0.433, 0.212, 0.643 | 0.317 |
| 90m-base | 8 | 84 | 49 | 219 / 101 / 58 | 164 / 46 / 19 | 85.9 / 230.4 | 18.89/28.09/36.88 | 0.166 | 0.547, 0.174, 0.862 | 0.317 |
| 91m-leaf | 12 | 84 | 78 | 350 / 208 / 163 | 297 / 122 / 83 | 40.5 / 106.1 | 7.31/10.46/13.36 | 0.379 | 0.412, 0.099, 0.731 | 0.328 |
| 91m-leaf | 16 | 84 | 14 | 441 / 353 / 303 | 389 / 226 / 203 | 29.1 / 56.0 | 5.82/7.22/8.35 | 0.600 | 0.342, 0.144, 0.547 | 0.328 |
| 91m-leaf | 8 | 84 | 72 | 274 / 147 / 94 | 228 / 82 / 48 | 54.8 / 186.2 | 9.49/14.69/19.04 | 0.232 | 0.455, 0.120, 0.780 | 0.328 |

### Top lens tokens

**90m-base L12** top-20 by lens-vector norm: `beneficiary` `ournal` `coming` `inferred` `allery` `cui` `jeg` `outlined` `ccall` `unrecognized` `deeply` `potential` `gorith` `cpa` `ndata` `ogma` `pose` `sole` `megam` `want`  
top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): `m` `cur` `2` `the` `total` `con` `cultural` `rec` `run` `type` `ri` `v` `aff` `sum` `ob` `cr` `matrix` `act` `p` `r`  
future-variant top-20 by norm: `âĢĿ` `TTP` `␣␣⏎` `,âĢĿ` `MDA` `.âĢĿ` `CPU` `"--` `?âĢĿ` `Pixel` `Linux` `!âĢĿ` `NFT` `GPU` `âĢĻ.` `SCIP` `="#"` `crypt` `"*` `NV`  
\|J_(s->t)\|_F by lag t-s = 0..7: 123.7, 27.5, 13.7, 12.7, 11.3, 8.9, 7.9, 8.8

**90m-base L16** top-20 by lens-vector norm: `**)` `)**` `ournal` `):**` `unrecognized` `TERNAL` `inferred` `))**` `yyt` `)||` `)."` `)**(-` `velt` `ogma` `..\..\` `ecause` `)")` `etween` `)=-(` `beneficiary`  
top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): `)**` `.` `)` `):**` `).` `.**` `2` `ï¼ī` `.)` `0` `),` `matrix` `user` `cultural` `quant` `âĤĤ` `␣␣⏎⏎` `sym` `⏎⏎` `1`  
future-variant top-20 by norm: `âĢĿ` `␣␣⏎` `.âĢĿ` `!âĢĿ` `âĢĻ.` `âĢĻ,` `?âĢĿ` `âĢĿ.` `.âĢĻ` `,âĢĿ` `âĢĿ,` `␣č⏎` `␣␣⏎⏎` `âĢĻ` `"--` `..."` `č⏎` `"...` `âĢľ` `âĢĺ`  
\|J_(s->t)\|_F by lag t-s = 0..7: 55.8, 9.2, 4.2, 3.9, 3.5, 2.8, 2.3, 2.9

**90m-base L8** top-20 by lens-vector norm: `s` `ournal` `coming` `sole` `ing` `sen` `semin` `pose` `ped` `rans` `ging` `ping` `nor` `t` `rain` `gorith` `jeg` `deeply` `miss` `cpa`  
top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): `m` `s` `t` `l` `r` `cur` `cultural` `the` `g` `a` `rec` `v` `sur` `p` `ri` `run` `in` `matrix` `sum` `ra`  
future-variant top-20 by norm: `JSON` `MDA` `␣COMPATIBILITY` `NFT` `MCU` `USD` `␣json` `RNG` `TTP` `␣TOKEN` `STEM` `␣JSON` `="#"` `CPU` `␣github` `Pixel` `STM` `UID` `FDA` `SYNC`  
\|J_(s->t)\|_F by lag t-s = 0..7: 230.4, 67.5, 40.6, 35.2, 31.4, 25.6, 22.8, 25.4

**91m-leaf L12** top-20 by lens-vector norm: `s` `ournal` `rit` `coming` `rad` `der` `ogma` `cre` `sen` `same` `rev` `ationship` `etc` `cop` `selves` `ends` `nection` `sole` `thing` `ener`  
top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): `2` `3` `1` `the` `In` `5` `7` `6` `B` `4` `.` `The` `rit` `CA` `,` `CO` `M` `con` `C` `A`  
future-variant top-20 by norm: `ournal` `TTP` `MDA` `matory` `AIDS` `'"` `Å¡` `etype` `ogma` `SDSS` `gorith` `DOT` `anon` `TERNAL` `ixel` `"`` `␣SOFTWARE` `consin` `AWS` `AAD`  
\|J_(s->t)\|_F by lag t-s = 0..7: 106.1, 31.6, 17.3, 14.0, 11.5, 9.0, 7.6, 7.2

**91m-leaf L16** top-20 by lens-vector norm: `):**` `ournal` `**)` `ogma` `TERNAL` `))**` `)."` `)**` `)**(-` `velt` `").` `)")` `Ð²ÑĪ` `achuset` `yyt` `),"` `"),` `unrecognized` `UVENILE` `umns`  
top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): `⏎` `1` `2` `)` `.` `3` `0` `4` `):**` `6` `5` `7` `).` `)**` `),` `9` `the` `The` `8` `CO`  
future-variant top-20 by norm: `'"` `'",` `"` `!"` `␣␣⏎` `"'` `"`:` `?"` `,"` `".` `..."` `"...` `."` `␣␣⏎⏎` `.")` `$"` `"`` `):**` `␣č⏎` `"--`  
\|J_(s->t)\|_F by lag t-s = 0..7: 56.0, 11.9, 5.8, 4.9, 4.0, 3.2, 2.5, 2.6

**91m-leaf L8** top-20 by lens-vector norm: `s` `t` `coming` `rit` `ing` `sen` `ournal` `der` `rain` `rad` `tor` `med` `m` `selves` `sole` `nor` `rab` `ting` `ed` `ding`  
top-20 by norm ratio lens/unembed (tokens the Jacobian amplifies): `s` `t` `the` `m` `The` `rit` `rec` `v` `l` `d` `a` `M` `In` `cur` `B` `g` `p` `A` `con` `rev`  
future-variant top-20 by norm: `␣␣⏎` `ournal` `␣JSON` `TERNAL` `URPOSE` `!"` `gorith` `␣␣⏎⏎` `)**(-` `MDA` `TTP` `␣GPL` `␣monospace` `thag` `GPL` `):**` `atabases` `CDC` `NASA` `␣SOFTWARE`  
\|J_(s->t)\|_F by lag t-s = 0..7: 186.2, 72.8, 45.2, 35.5, 30.7, 26.4, 22.7, 21.8


