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


## Readout on the room prompts (workspace loading = cosine with lens vectors)

### 90m-base L8  (mean max loading at final position 0.144; mean |top10 loading ∩ top10 prediction| = 1.8/10)

| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |
|---|---|---|---|---|---|---|
| 0 greeting | final `:` | `␣The`:0.13 `␣There`:0.13 `␣Now`:0.13 `␣Here`:0.13 `␣When`:0.13 `␣More`:0.12 `␣As`:0.12 `␣Where`:0.12 `␣To`:0.12 `␣Thanks`:0.12 | `␣About` `␣Now` `␣Patients` `␣Always` `␣Where` `␣Tell` `␣Thanks` `␣More` `␣Lo` `␣How` | `␣Following`:0.12 `VMName`:0.11 `␣Always`:0.11 `␣Would`:0.11 `␣Patients`:0.11 `␣Thanks`:0.11 | `␣Hi`:0.20 `␣I`:0.11 `␣Hello`:0.04 `␣The`:0.03 `␣So`:0.02 `␣It`:0.02 `␣You`:0.02 `␣hi`:0.02 `␣Yes`:0.02 `␣H`:0.02 | `␣There` `␣Now` `␣Here` `␣When` `␣More` `␣As` `␣Where` `␣To` `␣Thanks` |
| 0 greeting | h-label `h` | `.:`:0.14 `_:`:0.14 `:*`:0.14 `omen`:0.14 `ardo`:0.13 `␣knows`:0.13 `:\"`:0.13 `):`:0.13 `:`:0.13 `.,`:0.13 | `omen` `ournal` `popper` `ardo` `ccall` `mpp` `yyt` `ugin` `procs` `allery` | `:\"`:0.15 `omen`:0.14 `ardo`:0.14 `uties`:0.14 `atus`:0.14 `******************************************************************`:0.14 | `:`:0.99 `␣`:0.00 `,`:0.00 `.`:0.00 `'`:0.00 `␣and`:0.00 `␣says`:0.00 `␣is`:0.00 `:(`:0.00 `(`:0.00 | `.:` `_:` `:*` `omen` `ardo` `␣knows` `:\"` `):` `.,` |
| 1 greeting | final `:` | `␣The`:0.14 `␣When`:0.14 `␣There`:0.14 `␣Here`:0.13 `␣As`:0.13 `␣Now`:0.13 `␣To`:0.13 `␣More`:0.13 `␣Before`:0.13 `␣Where`:0.12 | `␣Patients` `␣Always` `␣Now` `␣About` `␣Where` `␣When` `␣Before` `␣Following` `␣Lo` `␣Another` | `␣Following`:0.12 `␣Always`:0.12 `␣Patients`:0.12 `VMName`:0.12 `␣Would`:0.11 `␣Once`:0.11 | `␣I`:0.28 `␣You`:0.07 `␣The`:0.05 `␣My`:0.02 `␣It`:0.02 `␣Who`:0.02 `␣A`:0.02 `␣There`:0.01 `␣What`:0.01 `␣No`:0.01 | `␣When` `␣Here` `␣As` `␣Now` `␣To` `␣More` `␣Before` `␣Where` |
| 1 greeting | h-label `h` | `.:`:0.14 `:*`:0.14 `ardo`:0.14 `omen`:0.14 `_:`:0.14 `oman`:0.13 `ï¸`:0.13 `:"`:0.13 `]:`:0.13 `uties`:0.13 | `omen` `ardo` `ournal` `popper` `ccall` `yyt` `ogma` `allery` `flr` `erman` | `:\"`:0.15 `ardo`:0.14 `uties`:0.14 `omen`:0.14 `oug`:0.14 `oman`:0.14 | `:`:1.00 `,`:0.00 `.`:0.00 `/`:0.00 `␣`:0.00 `;`:0.00 `(`:0.00 `.:`:0.00 `:(`:0.00 `-`:0.00 | `:*` `ardo` `omen` `_:` `oman` `ï¸` `:"` `]:` `uties` |
| 2 greeting | final `:` | `␣The`:0.14 `␣When`:0.14 `␣There`:0.13 `␣Now`:0.13 `␣As`:0.13 `␣Here`:0.13 `␣To`:0.13 `␣More`:0.13 `␣Where`:0.13 `␣Before`:0.12 | `␣Now` `␣Patients` `␣About` `␣Always` `␣Where` `␣When` `␣Before` `␣Following` `␣More` `unrecognized` | `␣Following`:0.13 `␣Always`:0.12 `␣Patients`:0.12 `␣Would`:0.12 `␣Once`:0.12 `VMName`:0.12 | `␣I`:0.14 `␣G`:0.10 `␣Hello`:0.03 `␣Thank`:0.03 `␣Yes`:0.02 `␣The`:0.02 `␣You`:0.02 `␣So`:0.02 `␣`:0.02 `␣And`:0.02 | `␣When` `␣There` `␣Now` `␣As` `␣Here` `␣To` `␣More` `␣Where` `␣Before` |
| 2 greeting | h-label `h` | `.:`:0.14 `:`:0.14 `:*`:0.14 `:"`:0.14 `_:`:0.14 `ardo`:0.13 `.,`:0.13 `):`:0.13 `omen`:0.13 `]:`:0.13 | `omen` `ardo` `ournal` `popper` `ccall` `ftype` `yyt` `procs` `oug` `mpp` | `:\"`:0.16 `ardo`:0.14 `omen`:0.14 `oug`:0.14 `oman`:0.14 `atus`:0.14 | `:`:0.99 `,`:0.00 `␣`:0.00 `.`:0.00 `␣and`:0.00 `'`:0.00 `:(`:0.00 `(`:0.00 `/`:0.00 `␣says`:0.00 | `.:` `:*` `:"` `_:` `ardo` `.,` `):` `omen` `]:` |
| 3 talk | final `:` | `␣The`:0.16 `␣When`:0.15 `␣There`:0.15 `␣As`:0.14 `␣It`:0.14 `␣To`:0.14 `␣Because`:0.14 `␣Here`:0.14 `␣If`:0.14 `␣Now`:0.14 | `␣Now` `␣When` `␣Because` `␣About` `␣Patients` `␣From` `␣Before` `␣There` `␣Following` `␣Where` | `␣Following`:0.14 `␣Because`:0.13 `␣Would`:0.13 `␣Once`:0.13 `␣Patients`:0.13 `␣When`:0.12 | `␣Yes`:0.17 `␣No`:0.14 `␣I`:0.13 `␣They`:0.07 `␣The`:0.03 `␣It`:0.03 `␣Mas`:0.02 `␣Not`:0.02 `␣We`:0.02 `␣There`:0.02 | `␣When` `␣As` `␣To` `␣Because` `␣Here` `␣If` `␣Now` |
| 3 talk | h-label `h` | `.:`:0.15 `.):`:0.14 `./`:0.14 `.,`:0.14 `):`:0.14 `:*`:0.14 `ardo`:0.14 `:"`:0.14 `omen`:0.14 `_:`:0.14 | `ournal` `omen` `ardo` `ccall` `yyt` `popper` `allery` `ogma` `ftype` `oug` | `:\"`:0.15 `ardo`:0.15 `uties`:0.14 `oug`:0.14 `omen`:0.14 `oman`:0.14 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `;`:0.00 `/`:0.00 `:.`:0.00 `:(`:0.00 `(`:0.00 `:[`:0.00 | `.:` `.):` `./` `.,` `):` `:*` `ardo` `:"` `omen` `_:` |
| 4 talk | final `:` | `␣The`:0.15 `␣There`:0.14 `␣When`:0.14 `␣As`:0.13 `␣To`:0.13 `␣Here`:0.13 `␣Now`:0.13 `␣All`:0.12 `␣More`:0.12 `␣It`:0.12 | `␣Now` `␣Always` `␣About` `␣Following` `␣Patients` `␣When` `␣There` `␣Before` `␣Another` `␣Because` | `␣Following`:0.13 `␣Always`:0.12 `␣Because`:0.12 `␣Patients`:0.12 `␣Once`:0.12 `␣Thanks`:0.11 | `␣I`:0.21 `␣The`:0.09 `␣It`:0.05 `␣What`:0.03 `␣We`:0.02 `␣Read`:0.02 `␣`:0.02 `␣You`:0.02 `␣This`:0.02 `␣Today`:0.02 | `␣There` `␣When` `␣As` `␣To` `␣Here` `␣Now` `␣All` `␣More` |
| 4 talk | h-label `h` | `.:`:0.15 `_:`:0.14 `:*`:0.14 `]:`:0.14 `):`:0.14 `omen`:0.14 `.):`:0.14 `ardo`:0.14 `./`:0.14 `ï¸`:0.14 | `ournal` `omen` `ardo` `ccall` `yyt` `popper` `ftype` `allery` `ogma` `flr` | `:\"`:0.15 `ardo`:0.14 `oug`:0.14 `omen`:0.14 `uties`:0.14 `atus`:0.14 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `(`:0.00 `/`:0.00 `:(`:0.00 `;`:0.00 `:\`:0.00 `:.`:0.00 | `.:` `_:` `:*` `]:` `):` `omen` `.):` `ardo` `./` `ï¸` |
| 5 talk | final `:` | `␣The`:0.15 `␣There`:0.14 `␣When`:0.14 `␣As`:0.13 `␣It`:0.13 `␣Now`:0.13 `␣Because`:0.13 `␣To`:0.13 `␣Here`:0.13 `␣If`:0.13 | `␣Now` `␣About` `␣Because` `␣When` `␣Patients` `␣Always` `␣There` `␣Before` `␣Where` `␣Only` | `␣Following`:0.13 `␣Because`:0.13 `␣Always`:0.12 `␣Once`:0.12 `␣Would`:0.12 `␣There`:0.12 | `␣Yes`:0.26 `␣I`:0.20 `␣No`:0.12 `␣Aw`:0.02 `␣You`:0.02 `␣It`:0.02 `␣Oh`:0.02 `␣The`:0.02 `␣Are`:0.01 `␣Ye`:0.01 | `␣There` `␣When` `␣As` `␣Now` `␣Because` `␣To` `␣Here` `␣If` |
| 5 talk | h-label `h` | `.:`:0.14 `ardo`:0.13 `.,`:0.13 `omen`:0.13 `.):`:0.13 `uties`:0.13 `oman`:0.13 `):`:0.13 `_:`:0.13 `./`:0.13 | `ournal` `omen` `ardo` `popper` `ccall` `procs` `yyt` `ogma` `oug` `allery` | `:\"`:0.15 `uties`:0.15 `ardo`:0.14 `omen`:0.14 `oug`:0.14 `oman`:0.14 | `:`:1.00 `␣`:0.00 `,`:0.00 `.`:0.00 `;`:0.00 `:(`:0.00 `:.`:0.00 `(`:0.00 `/`:0.00 `:[`:0.00 | `.:` `ardo` `.,` `omen` `.):` `uties` `oman` `):` `_:` `./` |
| 6 talk | final `:` | `␣The`:0.15 `␣When`:0.14 `␣There`:0.14 `␣As`:0.13 `␣To`:0.13 `␣Now`:0.13 `␣Here`:0.13 `␣More`:0.13 `␣From`:0.12 `␣If`:0.12 | `␣Now` `␣When` `␣About` `␣Where` `␣Patients` `␣Another` `␣From` `␣Always` `␣More` `␣Resp` | `␣Following`:0.12 `VMName`:0.11 `␣Always`:0.11 `␣Would`:0.11 `␣Once`:0.11 `␣Exploring`:0.11 | `␣I`:0.10 `␣It`:0.09 `␣The`:0.05 `␣Con`:0.04 `␣A`:0.04 `␣consciousness`:0.03 `␣No`:0.02 `␣In`:0.02 `␣Yes`:0.02 `␣There`:0.02 | `␣When` `␣As` `␣To` `␣Now` `␣Here` `␣More` `␣From` `␣If` |
| 6 talk | h-label `h` | `.:`:0.14 `:*`:0.14 `ardo`:0.14 `oman`:0.14 `_:`:0.14 `ï¸`:0.14 `omen`:0.14 `./`:0.14 `idth`:0.13 `.,`:0.13 | `ardo` `omen` `ournal` `ccall` `yyt` `popper` `allery` `ogma` `ftype` `erman` | `:\"`:0.15 `ardo`:0.14 `oug`:0.14 `oman`:0.14 `omen`:0.14 `uties`:0.14 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `;`:0.00 `/`:0.00 `(`:0.00 `:\`:0.00 `-`:0.00 `:.`:0.00 | `.:` `:*` `ardo` `oman` `_:` `ï¸` `omen` `./` `idth` `.,` |
| 7 talk | final `:` | `␣The`:0.14 `␣There`:0.14 `␣When`:0.14 `␣Here`:0.13 `␣To`:0.13 `␣As`:0.13 `␣Now`:0.13 `␣More`:0.13 `␣Because`:0.13 `␣Before`:0.13 | `␣About` `␣Now` `␣Always` `unrecognized` `␣Patients` `␣Following` `␣When` `␣Another` `␣Because` `␣Before` | `␣Following`:0.13 `␣Always`:0.12 `␣Because`:0.11 `␣Would`:0.11 `VMName`:0.11 `␣Patients`:0.11 | `␣I`:0.20 `␣The`:0.06 `␣What`:0.05 `␣It`:0.04 `␣Em`:0.02 `␣There`:0.02 `␣Well`:0.02 `␣That`:0.02 `␣You`:0.01 `␣`:0.01 | `␣When` `␣Here` `␣To` `␣As` `␣Now` `␣More` `␣Because` `␣Before` |
| 7 talk | h-label `h` | `.:`:0.14 `:*`:0.14 `_:`:0.14 `:`:0.13 `]:`:0.13 `ï¸`:0.13 `:"`:0.13 `):`:0.13 `.):`:0.13 `omen`:0.13 | `ournal` `omen` `popper` `ardo` `ccall` `yyt` `ogma` `allery` `ftype` `mpp` | `:\"`:0.15 `uties`:0.14 `oug`:0.13 `ardo`:0.13 `omen`:0.13 `******************************************************************`:0.13 | `:`:0.99 `,`:0.00 `.`:0.00 `␣`:0.00 `/`:0.00 `;`:0.00 `(`:0.00 `:(`:0.00 `.:`:0.00 `-`:0.00 | `:*` `_:` `]:` `ï¸` `:"` `):` `.):` `omen` |
| 8 talk | final `:` | `␣The`:0.14 `␣Now`:0.13 `␣When`:0.13 `␣There`:0.13 `␣As`:0.13 `␣Here`:0.13 `␣To`:0.12 `␣More`:0.12 `␣If`:0.12 `␣Because`:0.12 | `␣Now` `␣About` `␣Where` `␣When` `␣Patients` `␣More` `␣Because` `␣Another` `␣Thanks` `␣From` | `␣Would`:0.12 `VMName`:0.11 `␣Once`:0.11 `␣Following`:0.11 `␣Because`:0.11 `␣About`:0.11 | `␣The`:0.10 `␣I`:0.08 `␣That`:0.06 `␣It`:0.04 `␣There`:0.03 `␣But`:0.02 `␣Yes`:0.02 `␣You`:0.02 `␣So`:0.02 `␣No`:0.02 | `␣Now` `␣When` `␣As` `␣Here` `␣To` `␣More` `␣If` `␣Because` |
| 8 talk | h-label `h` | `.:`:0.15 `:*`:0.14 `:"`:0.14 `_:`:0.14 `ï¸`:0.14 `./`:0.14 `]:`:0.14 `.):`:0.14 `):`:0.14 `ardo`:0.14 | `ournal` `ardo` `omen` `popper` `ccall` `ogma` `yyt` `ugin` `allery` `oug` | `:\"`:0.15 `uties`:0.14 `ardo`:0.14 `oug`:0.14 `ucky`:0.14 `atus`:0.14 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `'`:0.00 `:.`:0.00 `;`:0.00 `:(`:0.00 `/`:0.00 `:'`:0.00 | `.:` `:*` `:"` `_:` `ï¸` `./` `]:` `.):` `):` `ardo` |
| 9 deflect | final `:` | `␣When`:0.14 `␣The`:0.14 `␣There`:0.14 `␣Here`:0.13 `␣To`:0.13 `␣As`:0.13 `␣Now`:0.13 `␣Where`:0.13 `␣Before`:0.13 `␣All`:0.13 | `␣About` `␣Now` `␣Always` `␣Where` `␣When` `␣Patients` `␣Before` `␣Thanks` `␣Another` `␣Any` | `␣Always`:0.12 `␣Following`:0.12 `␣Would`:0.12 `VMName`:0.11 `␣Once`:0.11 `␣Thanks`:0.11 | `␣I`:0.07 `␣Write`:0.06 `␣`:0.06 `␣The`:0.05 `␣Let`:0.03 `␣Re`:0.02 `␣write`:0.02 `␣You`:0.02 `␣If`:0.02 `␣In`:0.01 | `␣When` `␣There` `␣Here` `␣To` `␣As` `␣Now` `␣Where` `␣Before` `␣All` |
| 9 deflect | h-label `h` | `.:`:0.15 `:*`:0.14 `./`:0.14 `ï¸`:0.14 `):`:0.14 `:),`:0.14 `:"`:0.14 `]:`:0.14 `.):`:0.14 `_:`:0.14 | `ournal` `omen` `popper` `ardo` `yyt` `mpp` `ccall` `ftype` `erman` `oug` | `:\"`:0.15 `oug`:0.14 `ardo`:0.14 `omen`:0.14 `oman`:0.14 `atus`:0.14 | `:`:0.99 `,`:0.00 `␣`:0.00 `.`:0.00 `:\`:0.00 `(`:0.00 `/`:0.00 `:(`:0.00 `;`:0.00 `-`:0.00 | `.:` `:*` `./` `ï¸` `):` `:),` `:"` `]:` `.):` `_:` |
| 10 deflect | final `:` | `␣The`:0.14 `␣When`:0.13 `␣There`:0.13 `␣Now`:0.13 `␣As`:0.12 `␣To`:0.12 `␣More`:0.12 `␣If`:0.12 `␣Here`:0.12 `␣All`:0.12 | `␣Now` `␣About` `␣Where` `␣When` `␣Patients` `␣More` `␣Always` `␣Lo` `␣Another` `␣Mean` | `␣Would`:0.11 `␣Following`:0.11 `␣Always`:0.11 `␣Exploring`:0.11 `␣Have`:0.11 `␣Once`:0.11 | `␣The`:0.12 `␣the`:0.05 `␣`:0.05 `␣I`:0.05 `␣ham`:0.02 `␣In`:0.02 `⏎`:0.02 `␣in`:0.02 `␣Ham`:0.02 `␣There`:0.02 | `␣When` `␣Now` `␣As` `␣To` `␣More` `␣If` `␣Here` `␣All` |
| 10 deflect | h-label `h` | `.:`:0.15 `:*`:0.15 `ardo`:0.15 `omen`:0.14 `_:`:0.14 `:\"`:0.14 `ï¸`:0.14 `oman`:0.14 `./`:0.14 `/--`:0.14 | `omen` `ccall` `yyt` `ardo` `ournal` `popper` `allery` `ftype` `flr` `mpp` | `:\"`:0.16 `ardo`:0.15 `oug`:0.15 `omen`:0.15 `atus`:0.14 `åĪł`:0.14 | `:`:0.99 `␣`:0.00 `,`:0.00 `.`:0.00 `:\`:0.00 `-`:0.00 `1`:0.00 `:.`:0.00 `/`:0.00 `(`:0.00 | `.:` `:*` `ardo` `omen` `_:` `:\"` `ï¸` `oman` `./` `/--` |
| 11 deflect | final `:` | `␣The`:0.15 `␣When`:0.15 `␣There`:0.14 `␣Here`:0.14 `␣As`:0.14 `␣To`:0.14 `␣Now`:0.13 `␣If`:0.13 `␣Before`:0.13 `␣Where`:0.13 | `␣About` `␣When` `␣Patients` `␣Now` `␣Where` `␣Always` `␣Before` `␣Following` `␣Because` `␣From` | `␣Following`:0.13 `␣Would`:0.12 `␣Patients`:0.12 `␣Because`:0.12 `␣Always`:0.12 `VMName`:0.12 | `␣The`:0.14 `␣I`:0.08 `␣It`:0.08 `␣Yes`:0.04 `␣No`:0.03 `␣We`:0.02 `␣Weather`:0.02 `␣There`:0.02 `␣What`:0.02 `␣`:0.01 | `␣When` `␣Here` `␣As` `␣To` `␣Now` `␣If` `␣Before` `␣Where` |
| 11 deflect | h-label `h` | `oman`:0.14 `.:`:0.14 `omen`:0.14 `ardo`:0.14 `ï¸`:0.13 `_:`:0.13 `:*`:0.13 `uties`:0.13 `ough`:0.13 `/****************************************************************************`:0.13 | `ournal` `omen` `popper` `ardo` `ccall` `ogma` `yyt` `erman` `ftype` `allery` | `:\"`:0.15 `oug`:0.14 `oman`:0.14 `ardo`:0.14 `uties`:0.14 `omen`:0.14 | `:`:0.99 `,`:0.00 `.`:0.00 `␣`:0.00 `/`:0.00 `;`:0.00 `(`:0.00 `:(`:0.00 `.:`:0.00 `␣and`:0.00 | `oman` `omen` `ardo` `ï¸` `_:` `:*` `uties` `ough` `/****************************************************************************` |

### 90m-base L12  (mean max loading at final position 0.163; mean |top10 loading ∩ top10 prediction| = 4.0/10)

| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |
|---|---|---|---|---|---|---|
| 0 greeting | final `:` | `␣The`:0.15 `␣There`:0.15 `␣hello`:0.15 `␣This`:0.15 `␣It`:0.14 `␣Hi`:0.14 `␣I`:0.14 `␣You`:0.14 `␣Thanks`:0.14 `␣Hello`:0.14 | `␣hello` `␣acknow` `␣Your` `␣Hello` `␣Hi` `␣That` `unrecognized` `␣There` `␣yes` `␣your` | `DDDD`:0.12 `␣hello`:0.11 `␣acknow`:0.10 `␣There`:0.10 `␣That`:0.10 `␣Hi`:0.10 | `␣Hi`:0.20 `␣I`:0.11 `␣Hello`:0.04 `␣The`:0.03 `␣So`:0.02 `␣It`:0.02 `␣You`:0.02 `␣hi`:0.02 `␣Yes`:0.02 `␣H`:0.02 | `␣There` `␣hello` `␣This` `␣Thanks` |
| 0 greeting | h-label `h` | `:`:0.23 `:*`:0.19 `:(`:0.19 `:'`:0.19 `}:`:0.19 `':`:0.19 `:<`:0.19 `:_`:0.19 `:"`:0.18 `.:`:0.18 | `:` `_:` `:*` `:\"` `:{` `:_` `.:` `:~` `:[` `:`` | `:\"`:0.18 `_:`:0.18 `>:`:0.17 `():`:0.16 `:>`:0.16 `:+`:0.16 | `:`:0.99 `␣`:0.00 `,`:0.00 `.`:0.00 `'`:0.00 `␣and`:0.00 `␣says`:0.00 `␣is`:0.00 `:(`:0.00 `(`:0.00 | `:*` `:'` `}:` `':` `:<` `:_` `:"` `.:` |
| 1 greeting | final `:` | `␣The`:0.16 `␣This`:0.15 `␣There`:0.14 `␣It`:0.14 `␣My`:0.13 `␣That`:0.13 `␣All`:0.13 `␣We`:0.13 `␣He`:0.13 `␣Our`:0.13 | `␣Your` `␣Only` `␣Those` `unrecognized` `␣That` `␣Names` `␣Our` `␣Any` `␣There` `␣This` | `␣Those`:0.11 `␣Only`:0.11 `DDDD`:0.10 `␣That`:0.10 `␣There`:0.10 `␣Your`:0.09 | `␣I`:0.28 `␣You`:0.07 `␣The`:0.05 `␣My`:0.02 `␣It`:0.02 `␣Who`:0.02 `␣A`:0.02 `␣There`:0.01 `␣What`:0.01 `␣No`:0.01 | `␣This` `␣That` `␣All` `␣We` `␣He` `␣Our` |
| 1 greeting | h-label `h` | `:`:0.23 `}:`:0.20 `:*`:0.20 `:'`:0.19 `':`:0.19 `:_`:0.19 `:(`:0.19 `:<`:0.19 `_:`:0.19 `*:`:0.19 | `_:` `:` `:*` `:\"` `:`` `:_` `:{` `>:` `.:` `:~` | `_:`:0.17 `:\"`:0.17 `>:`:0.17 `}:`:0.15 `:>`:0.15 `():`:0.15 | `:`:1.00 `,`:0.00 `.`:0.00 `/`:0.00 `␣`:0.00 `;`:0.00 `(`:0.00 `.:`:0.00 `:(`:0.00 `-`:0.00 | `}:` `:*` `:'` `':` `:_` `:<` `_:` `*:` |
| 2 greeting | final `:` | `␣The`:0.16 `␣There`:0.16 `␣This`:0.15 `␣It`:0.14 `␣One`:0.14 `␣These`:0.14 `␣That`:0.14 `␣We`:0.14 `␣If`:0.13 `␣All`:0.13 | `␣There` `␣Your` `␣Those` `␣That` `␣Only` `␣Now` `␣Words` `␣Names` `␣One` `␣These` | `␣Those`:0.13 `␣There`:0.12 `␣Only`:0.11 `DDDD`:0.11 `␣That`:0.11 `␣These`:0.11 | `␣I`:0.14 `␣G`:0.10 `␣Hello`:0.03 `␣Thank`:0.03 `␣Yes`:0.02 `␣The`:0.02 `␣You`:0.02 `␣So`:0.02 `␣`:0.02 `␣And`:0.02 | `␣There` `␣This` `␣It` `␣One` `␣These` `␣That` `␣We` `␣If` `␣All` |
| 2 greeting | h-label `h` | `:`:0.23 `:*`:0.19 `:(`:0.19 `:'`:0.19 `}:`:0.19 `:<`:0.19 `':`:0.19 `:_`:0.19 `:+`:0.18 `:"`:0.18 | `_:` `:` `:*` `:\"` `:{` `:`` `:_` `:~` `:[` `.:` | `:\"`:0.18 `_:`:0.17 `>:`:0.16 `:+`:0.16 `:>`:0.16 `():`:0.15 | `:`:0.99 `,`:0.00 `␣`:0.00 `.`:0.00 `␣and`:0.00 `'`:0.00 `:(`:0.00 `(`:0.00 `/`:0.00 `␣says`:0.00 | `:*` `:'` `}:` `:<` `':` `:_` `:+` `:"` |
| 3 talk | final `:` | `␣There`:0.18 `␣This`:0.18 `␣The`:0.17 `␣It`:0.17 `␣Yes`:0.17 `␣That`:0.16 `␣These`:0.16 `␣Only`:0.16 `␣If`:0.15 `␣One`:0.15 | `␣Only` `␣There` `␣That` `␣Neither` `␣Those` `␣Yes` `␣This` `␣Your` `␣These` `␣Such` | `␣Those`:0.14 `␣Only`:0.14 `␣There`:0.14 `␣Neither`:0.12 `␣That`:0.12 `␣These`:0.12 | `␣Yes`:0.17 `␣No`:0.14 `␣I`:0.13 `␣They`:0.07 `␣The`:0.03 `␣It`:0.03 `␣Mas`:0.02 `␣Not`:0.02 `␣We`:0.02 `␣There`:0.02 | `␣This` `␣That` `␣These` `␣Only` `␣If` `␣One` |
| 3 talk | h-label `h` | `:`:0.23 `:*`:0.20 `}:`:0.20 `:'`:0.20 `:(`:0.20 `:_`:0.19 `:+`:0.19 `:<`:0.19 `:"`:0.19 `':`:0.19 | `_:` `:*` `:` `:`` `:_` `:\"` `:{` `:[` `.:` `:+` | `:\"`:0.18 `_:`:0.17 `:+`:0.17 `>:`:0.17 `:>`:0.16 `}:`:0.16 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `;`:0.00 `/`:0.00 `:.`:0.00 `:(`:0.00 `(`:0.00 `:[`:0.00 | `:*` `}:` `:'` `:_` `:+` `:<` `:"` `':` |
| 4 talk | final `:` | `␣The`:0.16 `␣It`:0.14 `␣There`:0.14 `␣This`:0.14 `␣One`:0.13 `␣Today`:0.12 `␣That`:0.12 `␣All`:0.12 `␣Did`:0.12 `␣Now`:0.12 | `␣There` `␣Only` `␣That` `␣Today` `␣The` `␣It` `␣Now` `␣Did` `␣One` `␣Five` | `␣Those`:0.10 `␣There`:0.10 `␣Only`:0.10 `␣Changed`:0.10 `EEEEEEEE`:0.10 `␣Did`:0.10 | `␣I`:0.21 `␣The`:0.09 `␣It`:0.05 `␣What`:0.03 `␣We`:0.02 `␣Read`:0.02 `␣`:0.02 `␣You`:0.02 `␣This`:0.02 `␣Today`:0.02 | `␣There` `␣One` `␣That` `␣All` `␣Did` `␣Now` |
| 4 talk | h-label `h` | `:`:0.23 `}:`:0.20 `:*`:0.20 `:'`:0.20 `':`:0.20 `:_`:0.20 `:(`:0.20 `:<`:0.20 `]:`:0.19 `*:`:0.19 | `_:` `:*` `:` `:\"` `:`` `:_` `:{` `>:` `.:` `:~` | `:\"`:0.18 `_:`:0.18 `>:`:0.17 `:>`:0.16 `:+`:0.16 `}:`:0.15 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `(`:0.00 `/`:0.00 `:(`:0.00 `;`:0.00 `:\`:0.00 `:.`:0.00 | `}:` `:*` `:'` `':` `:_` `:<` `]:` `*:` |
| 5 talk | final `:` | `␣There`:0.16 `␣This`:0.16 `␣Yes`:0.15 `␣The`:0.15 `␣It`:0.15 `␣No`:0.15 `␣Ye`:0.14 `␣Nothing`:0.14 `␣Only`:0.14 `␣That`:0.14 | `␣Only` `␣There` `␣Yes` `␣That` `␣Your` `␣Ye` `unrecognized` `␣Well` `␣Nothing` `␣Any` | `␣Only`:0.12 `␣There`:0.12 `␣Those`:0.11 `␣That`:0.11 `␣Yes`:0.11 `␣Nothing`:0.11 | `␣Yes`:0.26 `␣I`:0.20 `␣No`:0.12 `␣Aw`:0.02 `␣You`:0.02 `␣It`:0.02 `␣Oh`:0.02 `␣The`:0.02 `␣Are`:0.01 `␣Ye`:0.01 | `␣There` `␣This` `␣Nothing` `␣Only` `␣That` |
| 5 talk | h-label `h` | `:`:0.23 `}:`:0.19 `:*`:0.19 `:'`:0.19 `:(`:0.19 `:_`:0.19 `:<`:0.19 `:+`:0.19 `':`:0.19 `:"`:0.19 | `_:` `:` `:*` `:\"` `:_` `:`` `:{` `.:` `:~` `:[` | `:\"`:0.18 `_:`:0.17 `:+`:0.17 `>:`:0.17 `:>`:0.16 `}:`:0.16 | `:`:1.00 `␣`:0.00 `,`:0.00 `.`:0.00 `;`:0.00 `:(`:0.00 `:.`:0.00 `(`:0.00 `/`:0.00 `:[`:0.00 | `}:` `:*` `:'` `:_` `:<` `:+` `':` `:"` |
| 6 talk | final `:` | `␣This`:0.17 `␣The`:0.17 `␣It`:0.17 `␣There`:0.17 `␣That`:0.16 `␣If`:0.15 `␣Every`:0.15 `␣Because`:0.14 `␣One`:0.14 `␣When`:0.14 | `␣That` `␣There` `unrecognized` `inferred` `␣Only` `␣This` `␣It` `ecause` `TERNAL` `␣Any` | `␣There`:0.11 `␣That`:0.11 `␣Only`:0.11 `␣Those`:0.11 `␣Because`:0.10 `␣This`:0.10 | `␣I`:0.10 `␣It`:0.09 `␣The`:0.05 `␣Con`:0.04 `␣A`:0.04 `␣consciousness`:0.03 `␣No`:0.02 `␣In`:0.02 `␣Yes`:0.02 `␣There`:0.02 | `␣This` `␣That` `␣If` `␣Every` `␣Because` `␣One` `␣When` |
| 6 talk | h-label `h` | `:`:0.23 `}:`:0.20 `:*`:0.20 `:'`:0.20 `:_`:0.20 `:(`:0.20 `:<`:0.20 `:+`:0.20 `':`:0.20 `*:`:0.19 | `_:` `:*` `:\"` `:` `:`` `:_` `:{` `:~` `>:` `.:` | `:\"`:0.18 `_:`:0.17 `>:`:0.17 `:+`:0.16 `:>`:0.16 `:'\`:0.15 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `;`:0.00 `/`:0.00 `(`:0.00 `:\`:0.00 `-`:0.00 `:.`:0.00 | `}:` `:*` `:'` `:_` `:(` `:<` `:+` `':` `*:` |
| 7 talk | final `:` | `␣The`:0.16 `␣It`:0.15 `␣There`:0.15 `␣This`:0.15 `␣That`:0.14 `␣If`:0.13 `␣Because`:0.13 `␣I`:0.12 `␣One`:0.12 `␣We`:0.12 | `␣That` `ecause` `␣There` `␣It` `␣This` `␣Its` `␣Because` `␣Your` `␣Only` `␣Those` | `␣There`:0.11 `␣Those`:0.11 `␣That`:0.11 `␣Because`:0.10 `DDDD`:0.10 `␣Its`:0.10 | `␣I`:0.20 `␣The`:0.06 `␣What`:0.05 `␣It`:0.04 `␣Em`:0.02 `␣There`:0.02 `␣Well`:0.02 `␣That`:0.02 `␣You`:0.01 `␣`:0.01 | `␣This` `␣If` `␣Because` `␣One` `␣We` |
| 7 talk | h-label `h` | `:`:0.23 `:*`:0.20 `}:`:0.20 `:'`:0.20 `':`:0.19 `:_`:0.19 `:(`:0.19 `:<`:0.19 `:"`:0.19 `:+`:0.19 | `_:` `:` `:*` `:_` `:\"` `:`` `:{` `>:` `.:` `:[` | `_:`:0.18 `:\"`:0.18 `>:`:0.17 `:+`:0.16 `:>`:0.16 `():`:0.16 | `:`:0.99 `,`:0.00 `.`:0.00 `␣`:0.00 `/`:0.00 `;`:0.00 `(`:0.00 `:(`:0.00 `.:`:0.00 `-`:0.00 | `:*` `}:` `:'` `':` `:_` `:<` `:"` `:+` |
| 8 talk | final `:` | `␣The`:0.16 `␣This`:0.15 `␣There`:0.15 `␣It`:0.15 `␣That`:0.14 `␣But`:0.14 `␣Now`:0.13 `␣If`:0.13 `␣Because`:0.13 `␣One`:0.13 | `␣That` `␣Your` `␣There` `␣Another` `␣Now` `␣But` `␣This` `TERNAL` `␣It` `␣Those` | `DDDD`:0.12 `␣There`:0.11 `␣That`:0.11 `␣Those`:0.11 `␣Because`:0.10 `␣This`:0.10 | `␣The`:0.10 `␣I`:0.08 `␣That`:0.06 `␣It`:0.04 `␣There`:0.03 `␣But`:0.02 `␣Yes`:0.02 `␣You`:0.02 `␣So`:0.02 `␣No`:0.02 | `␣This` `␣Now` `␣If` `␣Because` `␣One` |
| 8 talk | h-label `h` | `:`:0.23 `:'`:0.19 `:(`:0.19 `:*`:0.19 `:+`:0.19 `:_`:0.19 `}:`:0.19 `:<`:0.19 `':`:0.19 `:"`:0.19 | `:` `_:` `:*` `:\"` `:`` `:_` `:{` `.:` `:~` `:+` | `:\"`:0.18 `:+`:0.17 `_:`:0.17 `>:`:0.16 `:>`:0.16 `:``:0.16 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `'`:0.00 `:.`:0.00 `;`:0.00 `:(`:0.00 `/`:0.00 `:'`:0.00 | `:*` `:+` `:_` `}:` `:<` `':` `:"` |
| 9 deflect | final `:` | `␣The`:0.17 `␣This`:0.17 `␣It`:0.16 `␣There`:0.16 `␣If`:0.16 `␣Here`:0.15 `␣One`:0.15 `␣You`:0.15 `␣Write`:0.15 `␣Let`:0.14 | `␣Your` `␣Definition` `␣Write` `␣If` `textfield` `unrecognized` `␣This` `␣There` `␣Any` `␣That` | `DDDD`:0.11 `␣Definition`:0.10 `␣Suppose`:0.09 `oooooooooooooooo`:0.09 `␣There`:0.09 `£Ð`:0.09 | `␣I`:0.07 `␣Write`:0.06 `␣`:0.06 `␣The`:0.05 `␣Let`:0.03 `␣Re`:0.02 `␣write`:0.02 `␣You`:0.02 `␣If`:0.02 `␣In`:0.01 | `␣This` `␣It` `␣There` `␣Here` `␣One` |
| 9 deflect | h-label `h` | `:`:0.23 `}:`:0.20 `:*`:0.20 `:_`:0.20 `:'`:0.20 `':`:0.20 `:(`:0.20 `:<`:0.20 `:+`:0.20 `:"`:0.20 | `_:` `:\"` `:*` `:`` `:_` `:` `>:` `:~` `:{` `yyt` | `:\"`:0.18 `_:`:0.17 `>:`:0.17 `:'\`:0.15 `:+`:0.15 `:>`:0.15 | `:`:0.99 `,`:0.00 `␣`:0.00 `.`:0.00 `:\`:0.00 `(`:0.00 `/`:0.00 `:(`:0.00 `;`:0.00 `-`:0.00 | `}:` `:*` `:_` `:'` `':` `:<` `:+` `:"` |
| 10 deflect | final `:` | `␣The`:0.17 `␣There`:0.16 `␣This`:0.15 `␣It`:0.15 `␣Here`:0.13 `␣All`:0.13 `␣THE`:0.13 `␣there`:0.13 `␣One`:0.13 `␣These`:0.12 | `Zj` `␣acknow` `Jq` `␣There` `Hq` `ecause` `TERNAL` `ellipsis` `Oq` `␣there` | `DDDD`:0.10 `␣There`:0.10 `WWWW`:0.10 `YWN`:0.10 `Zj`:0.09 `Jq`:0.09 | `␣The`:0.12 `␣the`:0.05 `␣`:0.05 `␣I`:0.05 `␣ham`:0.02 `␣In`:0.02 `⏎`:0.02 `␣in`:0.02 `␣Ham`:0.02 `␣There`:0.02 | `␣This` `␣It` `␣Here` `␣All` `␣THE` `␣there` `␣One` `␣These` |
| 10 deflect | h-label `h` | `:`:0.24 `:*`:0.21 `}:`:0.21 `:'`:0.21 `:(`:0.21 `:_`:0.21 `':`:0.20 `:<`:0.20 `:"`:0.20 `ï¼ļ`:0.20 | `_:` `:\"` `:*` `:` `:`` `:_` `>:` `:{` `:~` `.:` | `:\"`:0.18 `>:`:0.17 `_:`:0.17 `:'\`:0.16 `():`:0.15 `:>`:0.15 | `:`:0.99 `␣`:0.00 `,`:0.00 `.`:0.00 `:\`:0.00 `-`:0.00 `1`:0.00 `:.`:0.00 `/`:0.00 `(`:0.00 | `:*` `}:` `:'` `:(` `:_` `':` `:<` `:"` `ï¼ļ` |
| 11 deflect | final `:` | `␣The`:0.16 `␣There`:0.16 `␣This`:0.16 `␣It`:0.15 `␣No`:0.13 `␣Today`:0.13 `␣If`:0.13 `␣One`:0.13 `␣That`:0.13 `␣Only`:0.13 | `␣There` `␣Only` `␣This` `␣Today` `␣Your` `␣That` `␣Any` `ecause` `␣Now` `␣The` | `␣There`:0.11 `␣Only`:0.11 `DDDD`:0.10 `␣This`:0.10 `␣Because`:0.10 `␣That`:0.10 | `␣The`:0.14 `␣I`:0.08 `␣It`:0.08 `␣Yes`:0.04 `␣No`:0.03 `␣We`:0.02 `␣Weather`:0.02 `␣There`:0.02 `␣What`:0.02 `␣`:0.01 | `␣This` `␣Today` `␣If` `␣One` `␣That` `␣Only` |
| 11 deflect | h-label `h` | `:`:0.23 `:*`:0.20 `}:`:0.20 `:'`:0.20 `:_`:0.20 `':`:0.20 `:<`:0.19 `:(`:0.19 `:+`:0.19 `:"`:0.19 | `_:` `:*` `:` `:\"` `:`` `:_` `:{` `>:` `:~` `.:` | `:\"`:0.18 `_:`:0.17 `>:`:0.17 `:+`:0.16 `:>`:0.16 `:``:0.15 | `:`:0.99 `,`:0.00 `.`:0.00 `␣`:0.00 `/`:0.00 `;`:0.00 `(`:0.00 `:(`:0.00 `.:`:0.00 `␣and`:0.00 | `:*` `}:` `:'` `:_` `':` `:<` `:+` `:"` |

### 90m-base L16  (mean max loading at final position 0.231; mean |top10 loading ∩ top10 prediction| = 5.6/10)

| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |
|---|---|---|---|---|---|---|
| 0 greeting | final `:` | `␣The`:0.20 `␣There`:0.20 `␣You`:0.19 `␣I`:0.19 `␣We`:0.18 `␣It`:0.18 `␣Thank`:0.18 `␣So`:0.18 `␣Thanks`:0.18 `␣Yes`:0.17 | `␣There` `␣You` `␣That` `␣Your` `␣Thanks` `␣It` `␣Well` `␣Yes` `␣Thank` `␣Here` | `␣There`:0.24 `␣The`:0.23 `␣Thanks`:0.22 `␣Thank`:0.22 `␣You`:0.22 `␣That`:0.22 | `␣Hi`:0.20 `␣I`:0.11 `␣Hello`:0.04 `␣The`:0.03 `␣So`:0.02 `␣It`:0.02 `␣You`:0.02 `␣hi`:0.02 `␣Yes`:0.02 `␣H`:0.02 | `␣There` `␣We` `␣Thank` `␣Thanks` |
| 0 greeting | h-label `h` | `:`:0.26 `:[`:0.19 `:(`:0.19 `.:`:0.18 `:'`:0.18 `:,`:0.18 `:{`:0.18 `:*`:0.18 `:"`:0.17 `_:`:0.17 | `:` `:[` `_:` `:{` `.:` `:*` `:\"` `:(` `:_` `:'` | `:`:0.21 `:[`:0.18 `:(`:0.18 `:\"`:0.18 `:{`:0.18 `:(-`:0.17 | `:`:0.99 `␣`:0.00 `,`:0.00 `.`:0.00 `'`:0.00 `␣and`:0.00 `␣says`:0.00 `␣is`:0.00 `:(`:0.00 `(`:0.00 | `:[` `.:` `:'` `:,` `:{` `:*` `:"` `_:` |
| 1 greeting | final `:` | `␣The`:0.24 `␣You`:0.23 `␣We`:0.22 `␣There`:0.21 `␣My`:0.21 `␣Nob`:0.20 `␣I`:0.20 `␣It`:0.19 `␣Who`:0.19 `␣This`:0.19 | `␣Your` `␣You` `␣There` `␣Nob` `␣Who` `␣Only` `␣Everyone` `␣My` `␣We` `␣That` | `␣The`:0.24 `␣Nob`:0.24 `␣There`:0.23 `␣You`:0.23 `␣We`:0.23 `␣Everyone`:0.22 | `␣I`:0.28 `␣You`:0.07 `␣The`:0.05 `␣My`:0.02 `␣It`:0.02 `␣Who`:0.02 `␣A`:0.02 `␣There`:0.01 `␣What`:0.01 `␣No`:0.01 | `␣We` `␣Nob` `␣This` |
| 1 greeting | h-label `h` | `:`:0.23 `:(`:0.17 `:[`:0.17 `:*`:0.17 `.:`:0.17 `:'`:0.16 `_:`:0.16 `:,`:0.16 `:\"`:0.16 `:{`:0.16 | `:` `_:` `:*` `:\"` `:[` `.:` `:{` `yyt` `:_` `:(-` | `:\"`:0.16 `:`:0.16 `fsx`:0.15 `:(-`:0.15 `_:`:0.15 `:[`:0.14 | `:`:1.00 `,`:0.00 `.`:0.00 `/`:0.00 `␣`:0.00 `;`:0.00 `(`:0.00 `.:`:0.00 `:(`:0.00 `-`:0.00 | `:[` `:*` `:'` `_:` `:,` `:\"` `:{` |
| 2 greeting | final `:` | `␣The`:0.22 `␣There`:0.22 `␣Thank`:0.21 `␣We`:0.21 `␣You`:0.21 `␣Please`:0.21 `␣When`:0.20 `␣Good`:0.20 `␣It`:0.19 `␣This`:0.19 | `␣There` `␣Your` `␣Those` `␣Well` `␣They` `␣Thank` `␣That` `␣You` `␣Before` `␣When` | `␣There`:0.25 `␣Thank`:0.25 `␣Please`:0.25 `␣Those`:0.24 `␣When`:0.24 `␣Good`:0.24 | `␣I`:0.14 `␣G`:0.10 `␣Hello`:0.03 `␣Thank`:0.03 `␣Yes`:0.02 `␣The`:0.02 `␣You`:0.02 `␣So`:0.02 `␣`:0.02 `␣And`:0.02 | `␣There` `␣We` `␣Please` `␣When` `␣Good` `␣It` `␣This` |
| 2 greeting | h-label `h` | `:`:0.24 `:(`:0.18 `:[`:0.18 `.:`:0.17 `:,`:0.17 `:'`:0.17 `:*`:0.17 `:{`:0.17 `:\"`:0.16 `_:`:0.16 | `:` `:[` `_:` `:\"` `:*` `.:` `:{` `:(` `:(-` `:_` | `:`:0.17 `:\"`:0.17 `:[`:0.16 `:(`:0.16 `:(-`:0.16 `:{`:0.15 | `:`:0.99 `,`:0.00 `␣`:0.00 `.`:0.00 `␣and`:0.00 `'`:0.00 `:(`:0.00 `(`:0.00 `/`:0.00 `␣says`:0.00 | `:[` `.:` `:,` `:'` `:*` `:{` `:\"` `_:` |
| 3 talk | final `:` | `␣There`:0.25 `␣The`:0.24 `␣Yes`:0.23 `␣They`:0.23 `␣We`:0.22 `␣No`:0.22 `␣That`:0.21 `␣Well`:0.21 `␣It`:0.21 `␣You`:0.21 | `␣They` `␣There` `␣Well` `␣Those` `␣Their` `␣That` `␣Yes` `␣Only` `␣Nothing` `␣Neither` | `␣There`:0.29 `␣Those`:0.27 `␣They`:0.27 `␣The`:0.27 `␣Yes`:0.27 `␣Well`:0.26 | `␣Yes`:0.17 `␣No`:0.14 `␣I`:0.13 `␣They`:0.07 `␣The`:0.03 `␣It`:0.03 `␣Mas`:0.02 `␣Not`:0.02 `␣We`:0.02 `␣There`:0.02 | `␣That` `␣Well` `␣You` |
| 3 talk | h-label `h` | `:`:0.22 `:[`:0.17 `:(`:0.17 `:*`:0.16 `.:`:0.16 `:'`:0.16 `:,`:0.16 `:+`:0.15 `:{`:0.15 `:\"`:0.15 | `:` `:[` `:*` `_:` `:\"` `.:` `:_` `:{` `:(` `:(-` | `:`:0.16 `:\"`:0.15 `:[`:0.15 `:(`:0.14 `:(-`:0.14 `:*`:0.14 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `;`:0.00 `/`:0.00 `:.`:0.00 `:(`:0.00 `(`:0.00 `:[`:0.00 | `:*` `.:` `:'` `:,` `:+` `:{` `:\"` |
| 4 talk | final `:` | `␣The`:0.25 `␣It`:0.21 `␣There`:0.21 `␣We`:0.19 `␣I`:0.19 `␣This`:0.19 `␣One`:0.18 `␣What`:0.18 `␣You`:0.18 `␣After`:0.18 | `␣There` `␣It` `␣The` `␣Well` `␣One` `␣Two` `␣Today` `␣That` `␣They` `␣Reading` | `␣The`:0.25 `␣There`:0.24 `␣It`:0.23 `␣One`:0.21 `␣Well`:0.21 `␣This`:0.20 | `␣I`:0.21 `␣The`:0.09 `␣It`:0.05 `␣What`:0.03 `␣We`:0.02 `␣Read`:0.02 `␣`:0.02 `␣You`:0.02 `␣This`:0.02 `␣Today`:0.02 | `␣There` `␣One` `␣After` |
| 4 talk | h-label `h` | `:`:0.23 `:(`:0.18 `:[`:0.18 `:*`:0.18 `:'`:0.17 `.:`:0.17 `:,`:0.17 `:{`:0.17 `_:`:0.16 `:\"`:0.16 | `:` `_:` `:*` `:[` `:\"` `:{` `:_` `yyt` `.:` `:(` | `:\"`:0.16 `:`:0.16 `fsx`:0.15 `:[`:0.15 `:(-`:0.15 `:*`:0.15 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `(`:0.00 `/`:0.00 `:(`:0.00 `;`:0.00 `:\`:0.00 `:.`:0.00 | `:[` `:*` `:'` `.:` `:,` `:{` `_:` `:\"` |
| 5 talk | final `:` | `␣Yes`:0.22 `␣The`:0.22 `␣There`:0.22 `␣No`:0.22 `␣We`:0.21 `␣You`:0.20 `␣It`:0.20 `␣Well`:0.20 `␣Are`:0.19 `␣Never`:0.19 | `␣Yes` `␣There` `␣Well` `␣Only` `␣No` `␣Nothing` `␣Are` `␣You` `␣Never` `␣Two` | `␣Yes`:0.25 `␣There`:0.25 `␣Never`:0.25 `␣Well`:0.24 `␣Only`:0.23 `␣The`:0.23 | `␣Yes`:0.26 `␣I`:0.20 `␣No`:0.12 `␣Aw`:0.02 `␣You`:0.02 `␣It`:0.02 `␣Oh`:0.02 `␣The`:0.02 `␣Are`:0.01 `␣Ye`:0.01 | `␣There` `␣We` `␣Well` `␣Never` |
| 5 talk | h-label `h` | `:`:0.23 `:[`:0.17 `:(`:0.17 `:*`:0.17 `:'`:0.17 `.:`:0.17 `:,`:0.16 `:{`:0.16 `:+`:0.16 `:.`:0.15 | `:` `:[` `:*` `_:` `:\"` `.:` `:{` `:_` `:(` `:(-` | `:`:0.17 `:\"`:0.16 `:[`:0.16 `:(`:0.16 `:(-`:0.16 `:*`:0.15 | `:`:1.00 `␣`:0.00 `,`:0.00 `.`:0.00 `;`:0.00 `:(`:0.00 `:.`:0.00 `(`:0.00 `/`:0.00 `:[`:0.00 | `:*` `:'` `.:` `:,` `:{` `:+` |
| 6 talk | final `:` | `␣It`:0.23 `␣The`:0.23 `␣There`:0.22 `␣That`:0.20 `␣This`:0.20 `␣In`:0.19 `␣We`:0.19 `␣If`:0.19 `␣You`:0.18 `␣Being`:0.18 | `␣There` `␣It` `␣That` `␣Being` `␣Only` `inferred` `␣Its` `␣Nothing` `␣Your` `␣If` | `␣It`:0.23 `␣There`:0.23 `␣That`:0.22 `␣The`:0.21 `␣This`:0.20 `␣Being`:0.19 | `␣I`:0.10 `␣It`:0.09 `␣The`:0.05 `␣Con`:0.04 `␣A`:0.04 `␣consciousness`:0.03 `␣No`:0.02 `␣In`:0.02 `␣Yes`:0.02 `␣There`:0.02 | `␣That` `␣This` `␣We` `␣If` `␣You` `␣Being` |
| 6 talk | h-label `h` | `:`:0.21 `:(`:0.17 `:[`:0.16 `:*`:0.16 `.:`:0.16 `iddle`:0.16 `orry`:0.16 `itz`:0.16 `:\"`:0.16 `:'`:0.16 | `yyt` `:` `_:` `:\"` `:*` `:[` `:{` `.:` `uler` `cbi` | `:\"`:0.15 `fsx`:0.15 `iph`:0.14 `qh`:0.14 `:`:0.14 `orry`:0.14 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `;`:0.00 `/`:0.00 `(`:0.00 `:\`:0.00 `-`:0.00 `:.`:0.00 | `:(` `:[` `:*` `.:` `iddle` `orry` `itz` `:\"` `:'` |
| 7 talk | final `:` | `␣The`:0.24 `␣There`:0.22 `␣It`:0.21 `␣I`:0.20 `␣We`:0.19 `␣What`:0.19 `␣That`:0.19 `␣This`:0.19 `␣An`:0.19 `␣You`:0.18 | `␣There` `␣That` `␣It` `␣Well` `␣Two` `␣The` `␣They` `␣Those` `␣When` `␣Nothing` | `␣There`:0.24 `␣The`:0.24 `␣It`:0.23 `␣That`:0.22 `␣When`:0.21 `␣This`:0.21 | `␣I`:0.20 `␣The`:0.06 `␣What`:0.05 `␣It`:0.04 `␣Em`:0.02 `␣There`:0.02 `␣Well`:0.02 `␣That`:0.02 `␣You`:0.01 `␣`:0.01 | `␣We` `␣This` `␣An` |
| 7 talk | h-label `h` | `:`:0.24 `:(`:0.18 `:[`:0.18 `:*`:0.18 `.:`:0.17 `:'`:0.17 `_:`:0.17 `:,`:0.17 `:{`:0.17 `ï¼ļ`:0.16 | `:` `_:` `:*` `:[` `:\"` `.:` `:{` `:_` `yyt` `:(` | `:`:0.17 `:\"`:0.17 `:[`:0.16 `:(`:0.16 `_:`:0.15 `:(-`:0.15 | `:`:0.99 `,`:0.00 `.`:0.00 `␣`:0.00 `/`:0.00 `;`:0.00 `(`:0.00 `:(`:0.00 `.:`:0.00 `-`:0.00 | `:[` `:*` `:'` `_:` `:,` `:{` `ï¼ļ` |
| 8 talk | final `:` | `␣That`:0.23 `␣The`:0.23 `␣There`:0.22 `␣It`:0.20 `␣This`:0.19 `␣We`:0.19 `␣But`:0.19 `␣So`:0.18 `␣You`:0.18 `␣Those`:0.18 | `␣That` `␣There` `␣Those` `That` `␣But` `␣It` `␣Another` `␣Now` `␣The` `␣Well` | `␣That`:0.27 `␣There`:0.25 `␣The`:0.24 `␣Those`:0.23 `␣It`:0.23 `␣This`:0.21 | `␣The`:0.10 `␣I`:0.08 `␣That`:0.06 `␣It`:0.04 `␣There`:0.03 `␣But`:0.02 `␣Yes`:0.02 `␣You`:0.02 `␣So`:0.02 `␣No`:0.02 | `␣This` `␣We` `␣Those` |
| 8 talk | h-label `h` | `:`:0.24 `:[`:0.18 `:(`:0.18 `:'`:0.18 `:*`:0.17 `.:`:0.17 `:,`:0.17 `:{`:0.17 `:+`:0.17 `:.`:0.16 | `:` `:[` `:*` `_:` `.:` `:\"` `:{` `:_` `:(` `:(-` | `:`:0.18 `:\"`:0.17 `:[`:0.16 `:(-`:0.16 `:(`:0.16 `:+`:0.16 | `:`:1.00 `,`:0.00 `␣`:0.00 `.`:0.00 `'`:0.00 `:.`:0.00 `;`:0.00 `:(`:0.00 `/`:0.00 `:'`:0.00 | `:[` `:*` `.:` `:,` `:{` `:+` |
| 9 deflect | final `:` | `␣The`:0.22 `␣Write`:0.21 `␣Take`:0.20 `␣Let`:0.20 `␣You`:0.19 `␣This`:0.19 `␣Please`:0.19 `␣Suppose`:0.19 `␣Give`:0.18 `␣Start`:0.18 | `␣Write` `␣Take` `␣Your` `␣Delete` `␣Rename` `␣Example` `␣Remove` `␣Let` `␣Input` `␣Start` | `␣Write`:0.19 `␣Take`:0.19 `␣Suppose`:0.17 `␣Delete`:0.17 `␣Rename`:0.17 `␣Give`:0.17 | `␣I`:0.07 `␣Write`:0.06 `␣`:0.06 `␣The`:0.05 `␣Let`:0.03 `␣Re`:0.02 `␣write`:0.02 `␣You`:0.02 `␣If`:0.02 `␣In`:0.01 | `␣Take` `␣This` `␣Please` `␣Suppose` `␣Give` `␣Start` |
| 9 deflect | h-label `h` | `:`:0.21 `:(`:0.17 `:[`:0.17 `:\"`:0.17 `orry`:0.17 `itz`:0.16 `iddle`:0.16 `iph`:0.16 `:'`:0.16 `:{`:0.16 | `yyt` `:\"` `ottom` `uler` `_:` `ccall` `:` `:[` `cbi` `:{` | `:\"`:0.16 `fsx`:0.15 `iph`:0.14 `orry`:0.14 `uler`:0.14 `itz`:0.13 | `:`:0.99 `,`:0.00 `␣`:0.00 `.`:0.00 `:\`:0.00 `(`:0.00 `/`:0.00 `:(`:0.00 `;`:0.00 `-`:0.00 | `:[` `:\"` `orry` `itz` `iddle` `iph` `:'` `:{` |
| 10 deflect | final `:` | `␣The`:0.22 `␣There`:0.18 `␣This`:0.17 `␣It`:0.17 `␣the`:0.16 `␣there`:0.16 `␣First`:0.16 `␣Here`:0.15 `␣One`:0.15 `␣THE`:0.14 | `␣There` `␣The` `␣there` `␣It` `␣First` `␣Before` `␣One` `␣This` `␣Here` `there` | `␣The`:0.21 `␣There`:0.19 `␣This`:0.17 `␣It`:0.16 `␣THE`:0.16 `␣First`:0.16 | `␣The`:0.12 `␣the`:0.05 `␣`:0.05 `␣I`:0.05 `␣ham`:0.02 `␣In`:0.02 `⏎`:0.02 `␣in`:0.02 `␣Ham`:0.02 `␣There`:0.02 | `␣This` `␣It` `␣there` `␣First` `␣Here` `␣One` `␣THE` |
| 10 deflect | h-label `h` | `:`:0.23 `:[`:0.18 `:(`:0.18 `:\"`:0.17 `:*`:0.17 `.:`:0.17 `:'`:0.17 `:,`:0.17 `:{`:0.17 `orry`:0.17 | `:\"` `:` `_:` `yyt` `:*` `:[` `ottom` `:{` `uler` `.:` | `:\"`:0.17 `fsx`:0.16 `:`:0.15 `:(-`:0.14 `orry`:0.14 `_:`:0.14 | `:`:0.99 `␣`:0.00 `,`:0.00 `.`:0.00 `:\`:0.00 `-`:0.00 `1`:0.00 `:.`:0.00 `/`:0.00 `(`:0.00 | `:[` `:(` `:\"` `:*` `.:` `:'` `:,` `:{` `orry` |
| 11 deflect | final `:` | `␣The`:0.25 `␣There`:0.22 `␣It`:0.21 `␣We`:0.19 `␣No`:0.18 `␣This`:0.18 `␣Well`:0.18 `␣Please`:0.18 `␣Yes`:0.17 `␣You`:0.17 | `␣There` `␣It` `␣Well` `␣The` `␣Today` `␣That` `␣Nothing` `␣Two` `␣Weather` `␣Before` | `␣The`:0.25 `␣There`:0.24 `␣It`:0.23 `␣Well`:0.21 `␣Please`:0.20 `␣We`:0.20 | `␣The`:0.14 `␣I`:0.08 `␣It`:0.08 `␣Yes`:0.04 `␣No`:0.03 `␣We`:0.02 `␣Weather`:0.02 `␣There`:0.02 `␣What`:0.02 `␣`:0.01 | `␣This` `␣Well` `␣Please` `␣You` |
| 11 deflect | h-label `h` | `:`:0.23 `:[`:0.17 `:(`:0.17 `:*`:0.17 `.:`:0.17 `:'`:0.17 `:,`:0.16 `:\"`:0.16 `:{`:0.16 `ï¼ļ`:0.16 | `:` `:\"` `:*` `:[` `_:` `yyt` `.:` `:{` `:_` `:(-` | `:\"`:0.16 `:`:0.15 `fsx`:0.15 `:(-`:0.15 `:[`:0.15 `:(`:0.14 | `:`:0.99 `,`:0.00 `.`:0.00 `␣`:0.00 `/`:0.00 `;`:0.00 `(`:0.00 `:(`:0.00 `.:`:0.00 `␣and`:0.00 | `:[` `:*` `:'` `:,` `:\"` `:{` `ï¼ļ` |

### 91m-leaf L8  (mean max loading at final position 0.156; mean |top10 loading ∩ top10 prediction| = 0.6/10)

| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |
|---|---|---|---|---|---|---|
| 0 greeting | final `:` | `␣Lo`:0.17 `␣We`:0.16 `␣All`:0.15 `␣From`:0.15 `␣Nob`:0.15 `␣And`:0.15 `␣Med`:0.15 `␣In`:0.15 `␣Mart`:0.15 `␣How`:0.15 | `␣Lo` `␣From` `␣Tell` `␣Accepted` `␣Nob` `␣And` `␣All` `␣Probability` `␣Yes` `␣Med` | `␣Probability`:0.14 `␣Following`:0.14 `␣Nob`:0.13 `␣Accepted`:0.13 `␣From`:0.13 `␣Addr`:0.13 | `␣Hi`:0.07 `␣Yes`:0.07 `␣I`:0.07 `␣The`:0.06 `⏎⏎`:0.06 `␣It`:0.04 `␣Oh`:0.03 `␣`:0.03 `␣What`:0.03 `␣No`:0.03 | `␣Lo` `␣We` `␣All` `␣From` `␣Nob` `␣And` `␣Med` `␣In` `␣Mart` `␣How` |
| 0 greeting | h-label `h` | `oman`:0.14 `␣nod`:0.14 `ardo`:0.14 `␣explain`:0.13 `aving`:0.13 `uming`:0.13 `procs`:0.13 `aked`:0.13 `reat`:0.13 `␣explained`:0.13 | `ardo` `reat` `omen` `oman` `ough` `ippet` `ings` `aving` `odel` `ould` | `oman`:0.18 `ardo`:0.17 `procs`:0.17 `aving`:0.16 `rowave`:0.15 `osen`:0.15 | `:`:0.98 `.:`:0.00 `.`:0.00 `␣`:0.00 `;`:0.00 `,`:0.00 `âĢĻ`:0.00 `⏎⏎`:0.00 `␣is`:0.00 `-`:0.00 | `oman` `␣nod` `ardo` `␣explain` `aving` `uming` `procs` `aked` `reat` `␣explained` |
| 1 greeting | final `:` | `␣Lo`:0.16 `␣We`:0.15 `␣All`:0.15 `␣Nob`:0.15 `␣Mart`:0.15 `␣From`:0.15 `␣Med`:0.15 `␣Clo`:0.14 `␣Enter`:0.14 `␣Ask`:0.14 | `␣Accepted` `␣From` `␣Lo` `␣Nob` `␣Tell` `ï»¿namespace` `␣Through` `␣Yes` `␣All` `␣Enter` | `Compose`:0.13 `␣Following`:0.13 `␣Probability`:0.13 `␣Nob`:0.13 `␣Accepted`:0.13 `Inp`:0.13 | `␣I`:0.26 `␣The`:0.06 `⏎⏎`:0.04 `␣It`:0.04 `␣`:0.04 `␣You`:0.03 `␣Who`:0.02 `␣Yes`:0.02 `␣In`:0.02 `␣We`:0.02 | `␣Lo` `␣All` `␣Nob` `␣Mart` `␣From` `␣Med` `␣Clo` `␣Enter` `␣Ask` |
| 1 greeting | h-label `h` | `oman`:0.16 `ardo`:0.15 `procs`:0.15 `uming`:0.15 `aving`:0.14 `reat`:0.14 `avorite`:0.14 `.):`:0.14 `******************************************************************`:0.14 `␣nod`:0.14 | `ardo` `reat` `ippet` `omen` `odel` `oman` `essor` `ough` `ard` `ould` | `oman`:0.18 `procs`:0.17 `ardo`:0.17 `******************************************************************`:0.16 `aving`:0.15 `osen`:0.15 | `:`:0.94 `.`:0.01 `;`:0.01 `,`:0.00 `.:`:0.00 `␣`:0.00 `âĢĻ`:0.00 `at`:0.00 `⏎⏎`:0.00 `1`:0.00 | `oman` `ardo` `procs` `uming` `aving` `reat` `avorite` `.):` `******************************************************************` `␣nod` |
| 2 greeting | final `:` | `␣Lo`:0.16 `␣We`:0.15 `␣Med`:0.15 `␣All`:0.15 `␣Clo`:0.15 `␣From`:0.15 `␣Through`:0.15 `␣Im`:0.14 `␣Nob`:0.14 `␣Mart`:0.14 | `␣Accepted` `␣From` `␣Through` `␣Lo` `␣Med` `␣Nob` `␣All` `␣Yes` `␣Enter` `␣Following` | `␣Following`:0.13 `␣Probability`:0.13 `␣Accepted`:0.13 `␣Through`:0.13 `Inp`:0.13 `␣Clo`:0.13 | `␣The`:0.08 `␣I`:0.07 `␣Yes`:0.06 `␣G`:0.06 `␣It`:0.06 `␣A`:0.04 `␣There`:0.03 `␣In`:0.03 `␣You`:0.02 `␣And`:0.02 | `␣Lo` `␣We` `␣Med` `␣All` `␣Clo` `␣From` `␣Through` `␣Im` `␣Nob` `␣Mart` |
| 2 greeting | h-label `h` | `oman`:0.15 `ardo`:0.15 `uming`:0.14 `procs`:0.14 `aving`:0.14 `reat`:0.14 `aked`:0.13 `erious`:0.13 `ard`:0.13 `olves`:0.13 | `ardo` `reat` `omen` `odel` `oman` `ippet` `essor` `arily` `ard` `aked` | `oman`:0.19 `procs`:0.17 `ardo`:0.17 `aving`:0.16 `odel`:0.16 `osen`:0.15 | `:`:0.98 `.`:0.01 `.:`:0.00 `,`:0.00 `;`:0.00 `␣`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 `-`:0.00 `␣and`:0.00 | `oman` `ardo` `uming` `procs` `aving` `reat` `aked` `erious` `ard` `olves` |
| 3 talk | final `:` | `␣We`:0.15 `␣Lo`:0.15 `␣The`:0.15 `␣All`:0.14 `␣As`:0.14 `␣Nob`:0.14 `␣Im`:0.14 `␣Nam`:0.14 `␣Here`:0.14 `␣Because`:0.14 | `␣Accepted` `␣Because` `␣Yes` `␣From` `␣Following` `␣Nob` `␣Through` `␣All` `␣Lo` `␣The` | `␣Following`:0.14 `␣Accepted`:0.12 `␣Probability`:0.12 `␣Throughout`:0.12 `␣Always`:0.12 `␣Because`:0.12 | `␣Yes`:0.14 `␣They`:0.11 `␣No`:0.10 `␣The`:0.09 `␣I`:0.09 `␣It`:0.05 `␣There`:0.02 `␣Not`:0.02 `␣`:0.01 `␣In`:0.01 | `␣We` `␣Lo` `␣All` `␣As` `␣Nob` `␣Im` `␣Nam` `␣Here` `␣Because` |
| 3 talk | h-label `h` | `oman`:0.15 `ardo`:0.15 `uming`:0.15 `procs`:0.14 `reat`:0.14 `aving`:0.14 `ough`:0.13 `erious`:0.13 `ousing`:0.13 `aked`:0.13 | `ardo` `reat` `omen` `odel` `ippet` `oman` `essor` `ough` `arily` `ics` | `oman`:0.18 `procs`:0.18 `ardo`:0.17 `osen`:0.16 `WRK`:0.16 `odel`:0.15 | `:`:0.99 `;`:0.00 `.`:0.00 `.:`:0.00 `,`:0.00 `␣`:0.00 `:.`:0.00 `-`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 | `oman` `ardo` `uming` `procs` `reat` `aving` `ough` `erious` `ousing` `aked` |
| 4 talk | final `:` | `␣Lo`:0.16 `␣We`:0.16 `␣All`:0.15 `␣From`:0.15 `␣Im`:0.15 `␣Clo`:0.15 `␣The`:0.15 `␣Nob`:0.15 `␣Through`:0.15 `␣Nam`:0.14 | `␣Accepted` `␣From` `␣Through` `␣Lo` `␣All` `␣Nob` `␣Yes` `␣Following` `␣Because` `␣Probability` | `␣Following`:0.14 `␣Accepted`:0.13 `␣Probability`:0.13 `␣Through`:0.13 `␣Always`:0.13 `␣Nob`:0.12 | `␣The`:0.14 `␣I`:0.12 `␣It`:0.08 `␣A`:0.05 `␣In`:0.03 `␣Reading`:0.03 `␣Well`:0.02 `␣There`:0.02 `␣`:0.02 `␣What`:0.02 | `␣Lo` `␣We` `␣All` `␣From` `␣Im` `␣Clo` `␣Nob` `␣Through` `␣Nam` |
| 4 talk | h-label `h` | `oman`:0.15 `ardo`:0.14 `procs`:0.14 `uming`:0.14 `.):`:0.14 `aving`:0.14 `reat`:0.14 `avorite`:0.14 `:*`:0.13 `erious`:0.13 | `ardo` `reat` `omen` `oman` `ippet` `essor` `odel` `ough` `ard` `arily` | `oman`:0.18 `procs`:0.17 `ardo`:0.17 `osen`:0.15 `******************************************************************`:0.15 `avorite`:0.15 | `:`:0.92 `ira`:0.01 `.`:0.01 `,`:0.00 `.:`:0.00 `ia`:0.00 `;`:0.00 `ora`:0.00 `ina`:0.00 `ua`:0.00 | `oman` `ardo` `procs` `uming` `.):` `aving` `reat` `avorite` `:*` `erious` |
| 5 talk | final `:` | `␣Lo`:0.16 `␣We`:0.15 `␣Nob`:0.14 `␣The`:0.14 `␣All`:0.14 `␣Clo`:0.14 `␣From`:0.14 `␣Nam`:0.14 `␣As`:0.14 `␣Mart`:0.14 | `␣Accepted` `␣From` `␣Nob` `␣Following` `␣Lo` `␣Through` `␣Yes` `␣Because` `␣All` `␣Upon` | `␣Following`:0.14 `␣Accepted`:0.12 `␣Always`:0.12 `␣Probability`:0.12 `␣Nob`:0.12 `␣Throughout`:0.12 | `␣I`:0.29 `␣Yes`:0.14 `␣No`:0.11 `␣The`:0.04 `␣It`:0.03 `␣Oh`:0.02 `␣In`:0.02 `␣`:0.02 `␣Not`:0.02 `␣Aw`:0.01 | `␣Lo` `␣We` `␣Nob` `␣All` `␣Clo` `␣From` `␣Nam` `␣As` `␣Mart` |
| 5 talk | h-label `h` | `oman`:0.15 `ardo`:0.14 `procs`:0.14 `uming`:0.14 `reat`:0.13 `aving`:0.13 `===================================================================`:0.13 `aked`:0.13 `ousing`:0.13 `ough`:0.13 | `ardo` `reat` `omen` `ippet` `odel` `oman` `essor` `ough` `arily` `aving` | `oman`:0.18 `procs`:0.18 `ardo`:0.17 `WRK`:0.15 `osen`:0.15 `aving`:0.15 | `:`:0.99 `;`:0.00 `.`:0.00 `.:`:0.00 `,`:0.00 `␣`:0.00 `:.`:0.00 `-`:0.00 `âĢĻ`:0.00 `⏎⏎`:0.00 | `oman` `ardo` `procs` `uming` `reat` `aving` `===================================================================` `aked` `ousing` `ough` |
| 6 talk | final `:` | `␣Lo`:0.14 `␣We`:0.14 `␣Mart`:0.13 `␣Im`:0.13 `␣Clo`:0.13 `␣Yes`:0.13 `␣Dem`:0.13 `␣Nob`:0.13 `␣All`:0.13 `␣Nam`:0.13 | `␣Accepted` `␣Yes` `␣From` `Patient` `␣Nob` `␣Lo` `␣Through` `␣Probability` `␣Tell` `␣Med` | `␣Probability`:0.12 `␣Accepted`:0.12 `Compose`:0.12 `␣Clo`:0.11 `Patient`:0.11 `␣Nob`:0.11 | `␣It`:0.08 `␣A`:0.08 `␣I`:0.08 `␣The`:0.06 `⏎⏎`:0.05 `␣Yes`:0.04 `␣a`:0.03 `␣No`:0.03 `␣In`:0.02 `␣`:0.02 | `␣Lo` `␣We` `␣Mart` `␣Im` `␣Clo` `␣Dem` `␣Nob` `␣All` `␣Nam` |
| 6 talk | h-label `h` | `oman`:0.16 `uming`:0.15 `ardo`:0.15 `procs`:0.14 `erious`:0.14 `aving`:0.14 `reat`:0.14 `avorite`:0.14 `uly`:0.14 `aked`:0.14 | `ardo` `reat` `omen` `oman` `essor` `odel` `ough` `ippet` `arily` `aused` | `oman`:0.19 `procs`:0.17 `ardo`:0.17 `osen`:0.16 `******************************************************************`:0.16 `ocom`:0.15 | `:`:0.88 `.`:0.01 `;`:0.01 `.:`:0.01 `,`:0.00 `2`:0.00 `3`:0.00 `ii`:0.00 `ov`:0.00 `⏎⏎`:0.00 | `oman` `uming` `ardo` `procs` `erious` `aving` `reat` `avorite` `uly` `aked` |
| 7 talk | final `:` | `␣Lo`:0.16 `␣We`:0.15 `␣All`:0.15 `␣From`:0.14 `␣Nob`:0.14 `␣Im`:0.14 `␣Clo`:0.14 `␣Nam`:0.14 `␣Now`:0.14 `␣The`:0.14 | `␣Accepted` `␣From` `␣Nob` `␣Lo` `␣Through` `␣Yes` `␣All` `␣Following` `␣Probability` `␣Given` | `␣Following`:0.13 `␣Accepted`:0.13 `␣Probability`:0.12 `Inp`:0.12 `␣Nob`:0.12 `␣Through`:0.12 | `␣I`:0.16 `␣The`:0.07 `␣It`:0.06 `␣He`:0.03 `⏎⏎`:0.03 `␣`:0.03 `␣What`:0.02 `␣In`:0.02 `␣There`:0.02 `␣A`:0.02 | `␣Lo` `␣We` `␣All` `␣From` `␣Nob` `␣Im` `␣Clo` `␣Nam` `␣Now` |
| 7 talk | h-label `h` | `oman`:0.16 `ardo`:0.15 `procs`:0.15 `uming`:0.15 `aving`:0.14 `reat`:0.14 `aked`:0.14 `erious`:0.14 `uly`:0.14 `ould`:0.14 | `ardo` `reat` `ippet` `oman` `omen` `odel` `ough` `essor` `ould` `arily` | `oman`:0.19 `procs`:0.17 `ardo`:0.17 `odel`:0.16 `ocom`:0.15 `rowave`:0.15 | `:`:0.94 `;`:0.01 `.`:0.01 `,`:0.00 `.:`:0.00 `␣`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 `1`:0.00 `3`:0.00 | `oman` `ardo` `procs` `uming` `aving` `reat` `aked` `erious` `uly` `ould` |
| 8 talk | final `:` | `␣Lo`:0.16 `␣We`:0.15 `␣Mart`:0.14 `␣All`:0.14 `␣From`:0.14 `␣Med`:0.14 `␣Im`:0.14 `␣Clo`:0.14 `␣Nob`:0.14 `␣Physical`:0.13 | `␣From` `␣Accepted` `␣Lo` `␣Nob` `␣Tell` `␣Yes` `␣Through` `␣Probability` `␣Med` `␣All` | `␣Probability`:0.13 `␣Following`:0.13 `Compose`:0.13 `␣Accepted`:0.12 `␣Electronic`:0.12 `␣Nob`:0.12 | `␣The`:0.10 `␣It`:0.08 `␣Yes`:0.07 `␣I`:0.06 `␣That`:0.05 `␣`:0.03 `␣What`:0.02 `␣But`:0.02 `␣There`:0.02 `␣No`:0.02 | `␣Lo` `␣We` `␣Mart` `␣All` `␣From` `␣Med` `␣Im` `␣Clo` `␣Nob` `␣Physical` |
| 8 talk | h-label `h` | `oman`:0.16 `ardo`:0.15 `uming`:0.15 `procs`:0.15 `aving`:0.14 `reat`:0.14 `␣nod`:0.14 `avorite`:0.14 `aked`:0.14 `oice`:0.14 | `ardo` `reat` `omen` `ippet` `odel` `oman` `aving` `essor` `atest` `ough` | `oman`:0.19 `procs`:0.18 `ardo`:0.18 `aving`:0.16 `avorite`:0.16 `osen`:0.16 | `:`:0.99 `.`:0.00 `.:`:0.00 `;`:0.00 `⏎⏎`:0.00 `,`:0.00 `:.`:0.00 `␣`:0.00 `-`:0.00 `:*`:0.00 | `oman` `ardo` `uming` `procs` `aving` `reat` `␣nod` `avorite` `aked` `oice` |
| 9 deflect | final `:` | `␣Lo`:0.15 `␣Nob`:0.15 `␣Happy`:0.14 `␣Clo`:0.14 `␣Mart`:0.14 `␣Dem`:0.14 `␣We`:0.14 `␣Im`:0.14 `␣All`:0.14 `␣Enter`:0.14 | `␣Accepted` `␣Nob` `␣Yes` `␣Tell` `Patient` `␣From` `␣Lo` `␣Enter` `␣Probability` `␣Through` | `␣Accepted`:0.13 `␣Probability`:0.13 `Compose`:0.13 `␣Nob`:0.12 `Employee`:0.12 `␣Electronic`:0.12 | `␣I`:0.06 `␣The`:0.06 `⏎⏎`:0.05 `␣`:0.04 `␣Write`:0.04 `␣You`:0.03 `␣A`:0.03 `␣It`:0.03 `␣That`:0.03 `␣Yes`:0.02 | `␣Lo` `␣Nob` `␣Happy` `␣Clo` `␣Mart` `␣Dem` `␣We` `␣Im` `␣All` `␣Enter` |
| 9 deflect | h-label `h` | `oman`:0.17 `procs`:0.15 `uming`:0.15 `ardo`:0.15 `erious`:0.15 `aving`:0.14 `avorite`:0.14 `ough`:0.14 `reat`:0.14 `omen`:0.14 | `omen` `ardo` `reat` `oman` `ippet` `essor` `odel` `ough` `arily` `ographer` | `oman`:0.20 `procs`:0.18 `ardo`:0.16 `osen`:0.16 `avorite`:0.16 `omen`:0.16 | `:`:0.63 `,`:0.06 `.`:0.02 `;`:0.02 `2`:0.01 `ime`:0.01 `te`:0.01 `1`:0.01 `ite`:0.01 `?`:0.01 | `oman` `procs` `uming` `ardo` `erious` `aving` `avorite` `ough` `reat` `omen` |
| 10 deflect | final `:` | `␣Lo`:0.13 `␣Clo`:0.13 `␣Nam`:0.12 `␣Mart`:0.12 `␣All`:0.12 `␣Nob`:0.12 `␣Enter`:0.12 `␣Tell`:0.12 `␣Im`:0.12 `␣Home`:0.12 | `␣Accepted` `␣Tell` `Patient` `␣Yes` `␣Lo` `␣Nob` `␣Probability` `␣Enter` `␣Clo` `ï»¿namespace` | `Compose`:0.11 `␣Probability`:0.11 `Employee`:0.11 `␣Clo`:0.11 `␣Electronic`:0.11 `␣Accepted`:0.11 | `␣the`:0.06 `␣The`:0.04 `⏎⏎`:0.04 `␣`:0.04 `␣what`:0.02 `␣yes`:0.02 `␣I`:0.02 `␣a`:0.02 `␣What`:0.02 `␣it`:0.02 | `␣Lo` `␣Clo` `␣Nam` `␣Mart` `␣All` `␣Nob` `␣Enter` `␣Tell` `␣Im` `␣Home` |
| 10 deflect | h-label `h` | `oman`:0.17 `uming`:0.15 `ardo`:0.15 `procs`:0.15 `ough`:0.15 `aving`:0.15 `reat`:0.15 `avorite`:0.15 `aked`:0.14 `ard`:0.14 | `ardo` `reat` `omen` `oman` `ough` `ippet` `odel` `essor` `ard` `ould` | `oman`:0.20 `procs`:0.18 `ardo`:0.17 `osen`:0.17 `avorite`:0.16 `******************************************************************`:0.16 | `:`:0.74 `.`:0.04 `,`:0.02 `2`:0.01 `anna`:0.01 `⏎⏎`:0.01 `1`:0.01 `.:`:0.01 `?`:0.01 `␣`:0.01 | `oman` `uming` `ardo` `procs` `ough` `aving` `reat` `avorite` `aked` `ard` |
| 11 deflect | final `:` | `␣Lo`:0.16 `␣We`:0.15 `␣Nob`:0.14 `␣From`:0.14 `␣Yes`:0.14 `␣All`:0.14 `␣Im`:0.14 `␣Accepted`:0.14 `␣Now`:0.13 `␣Enter`:0.13 | `␣Accepted` `␣From` `␣Yes` `␣Nob` `␣Lo` `␣Through` `␣Because` `␣Enter` `Patient` `␣Tell` | `␣Accepted`:0.13 `␣Nob`:0.13 `␣Probability`:0.12 `Compose`:0.12 `␣Through`:0.12 `␣From`:0.12 | `␣The`:0.07 `␣I`:0.07 `␣Yes`:0.07 `␣It`:0.05 `␣What`:0.04 `␣No`:0.03 `␣`:0.03 `⏎⏎`:0.02 `␣Well`:0.02 `␣You`:0.02 | `␣Lo` `␣We` `␣Nob` `␣From` `␣All` `␣Im` `␣Accepted` `␣Now` `␣Enter` |
| 11 deflect | h-label `h` | `oman`:0.15 `uming`:0.14 `ardo`:0.14 `procs`:0.14 `aving`:0.14 `reat`:0.14 `erious`:0.13 `ough`:0.13 `aked`:0.13 `avorite`:0.13 | `reat` `ardo` `omen` `oman` `odel` `ippet` `ough` `essor` `ould` `ard` | `oman`:0.19 `procs`:0.17 `ardo`:0.16 `******************************************************************`:0.15 `aving`:0.15 `odel`:0.15 | `:`:0.88 `.`:0.02 `,`:0.02 `;`:0.01 `.:`:0.01 `art`:0.00 `␣`:0.00 `⏎⏎`:0.00 `?`:0.00 `1`:0.00 | `oman` `uming` `ardo` `procs` `aving` `reat` `erious` `ough` `aked` `avorite` |

### 91m-leaf L12  (mean max loading at final position 0.179; mean |top10 loading ∩ top10 prediction| = 2.5/10)

| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |
|---|---|---|---|---|---|---|
| 0 greeting | final `:` | `␣Yes`:0.20 `␣There`:0.17 `␣How`:0.17 `␣Does`:0.16 `␣Here`:0.16 `␣Because`:0.16 `␣Accepted`:0.16 `␣That`:0.16 `␣yes`:0.16 `␣What`:0.16 | `unrecognized` `essages` `ecause` `typography` `ellipsis` `essage` `YWN` `TERNAL` `EEEEEEEE` `DDDD` | `DDDD`:0.15 `ellipsis`:0.15 `YWN`:0.14 `DDDDD`:0.14 `Xz`:0.14 `typography`:0.14 | `␣Hi`:0.07 `␣Yes`:0.07 `␣I`:0.07 `␣The`:0.06 `⏎⏎`:0.06 `␣It`:0.04 `␣Oh`:0.03 `␣`:0.03 `␣What`:0.03 `␣No`:0.03 | `␣There` `␣How` `␣Does` `␣Here` `␣Because` `␣Accepted` `␣That` `␣yes` |
| 0 greeting | h-label `h` | `]:`:0.20 `:*`:0.19 `:**`:0.19 `.:`:0.19 `:_`:0.19 `:+`:0.18 `}:`:0.18 `ï¼ļ`:0.18 `:$`:0.18 `:\"`:0.18 | `:\>` `.:` `:\"` `:`` `]:` `omen` `abeth` `allery` `_:` `:*` | `:\"`:0.19 `():`:0.17 `]:`:0.16 `ï¼ļ`:0.16 `:+`:0.16 `>:`:0.16 | `:`:0.98 `.:`:0.00 `.`:0.00 `␣`:0.00 `;`:0.00 `,`:0.00 `âĢĻ`:0.00 `⏎⏎`:0.00 `␣is`:0.00 `-`:0.00 | `]:` `:*` `:**` `:_` `:+` `}:` `ï¼ļ` `:$` `:\"` |
| 1 greeting | final `:` | `␣From`:0.15 `␣The`:0.15 `␣There`:0.15 `␣That`:0.15 `␣Only`:0.15 `␣Yes`:0.15 `␣Those`:0.15 `␣How`:0.14 `␣Because`:0.14 `␣Words`:0.14 | `unrecognized` `ecause` `Ð²ÑĪ` `essages` `descr` `␣From` `typography` `␣Those` `␣Words` `ellipsis` | `Inp`:0.14 `descr`:0.13 `Xz`:0.13 `␣Those`:0.13 `ellipsis`:0.12 `essages`:0.12 | `␣I`:0.26 `␣The`:0.06 `⏎⏎`:0.04 `␣It`:0.04 `␣`:0.04 `␣You`:0.03 `␣Who`:0.02 `␣Yes`:0.02 `␣In`:0.02 `␣We`:0.02 | `␣From` `␣There` `␣That` `␣Only` `␣Those` `␣How` `␣Because` `␣Words` |
| 1 greeting | h-label `h` | `]:`:0.21 `:*`:0.20 `:**`:0.20 `:+`:0.19 `:_`:0.19 `_:`:0.19 `.:`:0.19 `ï¼ļ`:0.18 `:[`:0.18 `:$`:0.18 | `:\>` `:`` `omen` `xea` `ournal` `_:` `.:` `abeth` `:*` `]:` | `:\"`:0.17 `():`:0.16 `:``:0.16 `WRK`:0.16 `:+`:0.16 `]:`:0.16 | `:`:0.94 `.`:0.01 `;`:0.01 `,`:0.00 `.:`:0.00 `␣`:0.00 `âĢĻ`:0.00 `at`:0.00 `⏎⏎`:0.00 `1`:0.00 | `]:` `:*` `:**` `:+` `:_` `_:` `ï¼ļ` `:[` `:$` |
| 2 greeting | final `:` | `␣There`:0.18 `␣Yes`:0.18 `␣The`:0.16 `␣Because`:0.16 `␣That`:0.16 `␣Only`:0.16 `␣What`:0.15 `␣How`:0.15 `␣This`:0.15 `␣When`:0.15 | `unrecognized` `typography` `descr` `␣There` `ecause` `␣Words` `␣Because` `␣Yes` `ellipsis` `␣That` | `typography`:0.15 `descr`:0.14 `␣There`:0.14 `Inp`:0.14 `Xz`:0.14 `␣Because`:0.14 | `␣The`:0.08 `␣I`:0.07 `␣Yes`:0.06 `␣G`:0.06 `␣It`:0.06 `␣A`:0.04 `␣There`:0.03 `␣In`:0.03 `␣You`:0.02 `␣And`:0.02 | `␣Because` `␣That` `␣Only` `␣What` `␣How` `␣This` `␣When` |
| 2 greeting | h-label `h` | `]:`:0.20 `:*`:0.20 `:+`:0.19 `:_`:0.19 `:**`:0.19 `.:`:0.19 `>:`:0.18 `ï¼ļ`:0.18 `:$`:0.18 `}:`:0.18 | `.:` `:\>` `]:` `:`` `:*` `_:` `:+` `xea` `:\"` `.):` | `:\"`:0.18 `:+`:0.17 `():`:0.17 `>:`:0.17 `]:`:0.17 `ï¼ļ`:0.16 | `:`:0.98 `.`:0.01 `.:`:0.00 `,`:0.00 `;`:0.00 `␣`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 `-`:0.00 `␣and`:0.00 | `]:` `:*` `:+` `:_` `:**` `>:` `ï¼ļ` `:$` `}:` |
| 3 talk | final `:` | `␣Yes`:0.21 `␣There`:0.20 `␣Only`:0.19 `␣Nothing`:0.18 `␣Because`:0.18 `␣This`:0.18 `␣That`:0.17 `␣It`:0.17 `␣Remember`:0.17 `␣Neither`:0.17 | `unrecognized` `␣Yes` `ecause` `␣There` `typography` `␣Only` `␣Because` `␣Those` `␣Accepted` `␣Neither` | `␣There`:0.15 `␣Those`:0.15 `␣Always`:0.14 `␣Only`:0.14 `␣Yes`:0.14 `typography`:0.14 | `␣Yes`:0.14 `␣They`:0.11 `␣No`:0.10 `␣The`:0.09 `␣I`:0.09 `␣It`:0.05 `␣There`:0.02 `␣Not`:0.02 `␣`:0.01 `␣In`:0.01 | `␣Only` `␣Nothing` `␣Because` `␣This` `␣That` `␣Remember` `␣Neither` |
| 3 talk | h-label `h` | `]:`:0.21 `:*`:0.20 `:+`:0.20 `:**`:0.20 `:_`:0.20 `.:`:0.19 `:$`:0.19 `:(`:0.19 `:[`:0.19 `_:`:0.19 | `.:` `:`` `:\>` `_:` `:+` `]:` `:*` `:_` `.):` `:` | `:+`:0.18 `:\"`:0.18 `]:`:0.17 `():`:0.17 `_:`:0.17 `>:`:0.17 | `:`:0.99 `;`:0.00 `.`:0.00 `.:`:0.00 `,`:0.00 `␣`:0.00 `:.`:0.00 `-`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 | `]:` `:*` `:+` `:**` `:_` `:$` `:(` `:[` `_:` |
| 4 talk | final `:` | `␣The`:0.18 `␣There`:0.17 `␣From`:0.17 `␣Because`:0.16 `␣Only`:0.15 `␣Through`:0.15 `␣One`:0.15 `␣Our`:0.15 `␣Words`:0.15 `␣That`:0.15 | `␣From` `ecause` `unrecognized` `␣Words` `␣Because` `␣Those` `␣There` `␣Through` `␣The` `␣Written` | `␣From`:0.14 `␣Those`:0.14 `␣Because`:0.14 `␣Words`:0.13 `Inp`:0.13 `Xz`:0.13 | `␣The`:0.14 `␣I`:0.12 `␣It`:0.08 `␣A`:0.05 `␣In`:0.03 `␣Reading`:0.03 `␣Well`:0.02 `␣There`:0.02 `␣`:0.02 `␣What`:0.02 | `␣From` `␣Because` `␣Only` `␣Through` `␣One` `␣Our` `␣Words` `␣That` |
| 4 talk | h-label `h` | `]:`:0.21 `:*`:0.21 `:**`:0.20 `ï¼ļ`:0.20 `:_`:0.20 `:+`:0.20 `_:`:0.20 `\):`:0.20 `():`:0.19 `:[`:0.19 | `:`` `ournal` `omen` `:\>` `_:` `xea` `yyt` `é»ĺ` `abeth` `allery` | `:\"`:0.18 `():`:0.17 `:``:0.16 `ï¼ļ`:0.16 `_:`:0.16 `WRK`:0.16 | `:`:0.92 `ira`:0.01 `.`:0.01 `,`:0.00 `.:`:0.00 `ia`:0.00 `;`:0.00 `ora`:0.00 `ina`:0.00 `ua`:0.00 | `]:` `:*` `:**` `ï¼ļ` `:_` `:+` `_:` `\):` `():` `:[` |
| 5 talk | final `:` | `␣Yes`:0.20 `␣There`:0.19 `␣Only`:0.19 `␣Nothing`:0.18 `␣Always`:0.17 `␣It`:0.17 `␣Accepted`:0.17 `␣That`:0.16 `␣This`:0.16 `␣Neither`:0.16 | `unrecognized` `␣Yes` `ecause` `␣Only` `␣Accepted` `␣There` `ellipsis` `␣Nothing` `␣Always` `typography` | `␣Always`:0.15 `␣Only`:0.14 `␣Accepted`:0.14 `ellipsis`:0.14 `␣Yes`:0.14 `Inp`:0.14 | `␣I`:0.29 `␣Yes`:0.14 `␣No`:0.11 `␣The`:0.04 `␣It`:0.03 `␣Oh`:0.02 `␣In`:0.02 `␣`:0.02 `␣Not`:0.02 `␣Aw`:0.01 | `␣There` `␣Only` `␣Nothing` `␣Always` `␣Accepted` `␣That` `␣This` `␣Neither` |
| 5 talk | h-label `h` | `]:`:0.20 `:*`:0.20 `:_`:0.20 `:+`:0.20 `:**`:0.19 `.:`:0.19 `:(`:0.19 `}:`:0.18 `:$`:0.18 `>:`:0.18 | `.:` `:`` `_:` `]:` `:\>` `:+` `:*` `:_` `:` `.):` | `:+`:0.18 `:\"`:0.18 `():`:0.17 `>:`:0.17 `]:`:0.17 `_:`:0.17 | `:`:0.99 `;`:0.00 `.`:0.00 `.:`:0.00 `,`:0.00 `␣`:0.00 `:.`:0.00 `-`:0.00 `âĢĻ`:0.00 `⏎⏎`:0.00 | `]:` `:*` `:_` `:+` `:**` `:(` `}:` `:$` `>:` |
| 6 talk | final `:` | `␣Because`:0.17 `␣Yes`:0.16 `␣There`:0.16 `␣That`:0.16 `␣Only`:0.16 `␣Neither`:0.16 `␣However`:0.15 `␣Always`:0.15 `␣It`:0.15 `␣This`:0.15 | `ecause` `unrecognized` `ftype` `␣Because` `Transferred` `textfield` `typography` `essages` `inferred` `gorithm` | `Xz`:0.14 `Transferred`:0.14 `Inp`:0.14 `textfield`:0.14 `␣Because`:0.14 `ftype`:0.13 | `␣It`:0.08 `␣A`:0.08 `␣I`:0.08 `␣The`:0.06 `⏎⏎`:0.05 `␣Yes`:0.04 `␣a`:0.03 `␣No`:0.03 `␣In`:0.02 `␣`:0.02 | `␣Because` `␣There` `␣That` `␣Only` `␣Neither` `␣However` `␣Always` `␣This` |
| 6 talk | h-label `h` | `]:`:0.21 `:*`:0.20 `:**`:0.20 `:+`:0.20 `\):`:0.20 `ï¼ļ`:0.20 `:``:0.20 `:(-`:0.19 `:_`:0.19 `:$`:0.19 | `:\>` `:`` `ournal` `omen` `abeth` `xea` `yyt` `:\"` `allery` `ippet` | `:\"`:0.18 `WRK`:0.17 `:``:0.16 `():`:0.16 `:\>`:0.16 `xffffffffffffffff`:0.16 | `:`:0.88 `.`:0.01 `;`:0.01 `.:`:0.01 `,`:0.00 `2`:0.00 `3`:0.00 `ii`:0.00 `ov`:0.00 `⏎⏎`:0.00 | `]:` `:*` `:**` `:+` `\):` `ï¼ļ` `:`` `:(-` `:_` `:$` |
| 7 talk | final `:` | `␣There`:0.18 `␣Because`:0.17 `␣That`:0.17 `␣The`:0.17 `␣Yes`:0.17 `␣It`:0.16 `␣Only`:0.16 `␣Here`:0.16 `␣From`:0.16 `␣Nothing`:0.16 | `ecause` `unrecognized` `␣Because` `typography` `essages` `␣There` `␣That` `␣From` `␣Words` `descr` | `␣Because`:0.15 `␣Those`:0.14 `␣There`:0.14 `typography`:0.14 `descr`:0.13 `Xz`:0.13 | `␣I`:0.16 `␣The`:0.07 `␣It`:0.06 `␣He`:0.03 `⏎⏎`:0.03 `␣`:0.03 `␣What`:0.02 `␣In`:0.02 `␣There`:0.02 `␣A`:0.02 | `␣Because` `␣That` `␣Yes` `␣Only` `␣Here` `␣From` `␣Nothing` |
| 7 talk | h-label `h` | `]:`:0.21 `:*`:0.20 `:**`:0.20 `:_`:0.20 `:+`:0.20 `_:`:0.19 `\):`:0.19 `:$`:0.19 `:[`:0.19 `ï¼ļ`:0.19 | `:`` `:\>` `ournal` `omen` `_:` `é»ĺ` `xea` `.:` `]:` `:\"` | `:\"`:0.18 `():`:0.17 `:``:0.16 `_:`:0.16 `:+`:0.16 `WRK`:0.16 | `:`:0.94 `;`:0.01 `.`:0.01 `,`:0.00 `.:`:0.00 `␣`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 `1`:0.00 `3`:0.00 | `]:` `:*` `:**` `:_` `:+` `_:` `\):` `:$` `:[` `ï¼ļ` |
| 8 talk | final `:` | `␣There`:0.18 `␣Yes`:0.18 `␣That`:0.16 `␣How`:0.16 `␣The`:0.16 `␣Does`:0.16 `␣What`:0.16 `␣Here`:0.16 `␣Now`:0.16 `␣Let`:0.16 | `unrecognized` `typography` `ecause` `ellipsis` `EEEEEEEE` `␣Words` `␣Your` `eday` `descr` `TERNAL` | `ellipsis`:0.15 `typography`:0.15 `DDDD`:0.14 `YWN`:0.14 `Inp`:0.14 `descr`:0.13 | `␣The`:0.10 `␣It`:0.08 `␣Yes`:0.07 `␣I`:0.06 `␣That`:0.05 `␣`:0.03 `␣What`:0.02 `␣But`:0.02 `␣There`:0.02 `␣No`:0.02 | `␣How` `␣Does` `␣Here` `␣Now` `␣Let` |
| 8 talk | h-label `h` | `]:`:0.21 `:*`:0.20 `:**`:0.20 `:+`:0.20 `:_`:0.20 `\):`:0.19 `:$`:0.19 `.:`:0.19 `}:`:0.18 `:[`:0.18 | `:\>` `:`` `.:` `]:` `_:` `:*` `:")` `:+` `:\"` `abeth` | `:\"`:0.18 `:+`:0.17 `():`:0.17 `]:`:0.16 `:``:0.16 `\):`:0.16 | `:`:0.99 `.`:0.00 `.:`:0.00 `;`:0.00 `⏎⏎`:0.00 `,`:0.00 `:.`:0.00 `␣`:0.00 `-`:0.00 `:*`:0.00 | `]:` `:**` `:+` `:_` `\):` `:$` `}:` `:[` |
| 9 deflect | final `:` | `␣Yes`:0.17 `␣There`:0.17 `␣Does`:0.16 `␣That`:0.16 `␣Answer`:0.16 `␣Accepted`:0.16 `␣Because`:0.15 `␣Assume`:0.15 `␣This`:0.15 `␣Only`:0.15 | `unrecognized` `essages` `typography` `essage` `ecause` `descr` `gorithm` `ellipsis` `classname` `textfield` | `Inp`:0.15 `DDDD`:0.14 `typography`:0.13 `ellipsis`:0.13 `Transferred`:0.13 `essages`:0.13 | `␣I`:0.06 `␣The`:0.06 `⏎⏎`:0.05 `␣`:0.04 `␣Write`:0.04 `␣You`:0.03 `␣A`:0.03 `␣It`:0.03 `␣That`:0.03 `␣Yes`:0.02 | `␣There` `␣Does` `␣Answer` `␣Accepted` `␣Because` `␣Assume` `␣This` `␣Only` |
| 9 deflect | h-label `h` | `]:`:0.21 `:**`:0.20 `:(-`:0.20 `:``:0.20 `:*`:0.20 `:+`:0.20 `:\"`:0.20 `\):`:0.20 `:_`:0.20 `_:`:0.20 | `:\>` `ournal` `omen` `é»ĺ` `:`` `etype` `yyt` `ippet` `allery` `abeth` | `:\"`:0.18 `WRK`:0.17 `:\>`:0.16 `:``:0.16 `ZXJ`:0.16 `é»ĺ`:0.16 | `:`:0.63 `,`:0.06 `.`:0.02 `;`:0.02 `2`:0.01 `ime`:0.01 `te`:0.01 `1`:0.01 `ite`:0.01 `?`:0.01 | `]:` `:**` `:(-` `:`` `:*` `:+` `:\"` `\):` `:_` `_:` |
| 10 deflect | final `:` | `␣describes`:0.15 `␣describe`:0.14 `␣yes`:0.14 `␣mention`:0.14 `␣introduces`:0.14 `␣Yes`:0.13 `␣how`:0.13 `␣hello`:0.13 `DDDD`:0.13 `␣There`:0.13 | `unrecognized` `typography` `DDDD` `essages` `essage` `DDDDD` `EEEEEEEE` `xxl` `ecause` `SSSSS` | `DDDD`:0.15 `DDDDD`:0.15 `AAAAAAAAAAAAAAAA`:0.14 `Xz`:0.14 `AAAAAAA`:0.14 `WWWW`:0.14 | `␣the`:0.06 `␣The`:0.04 `⏎⏎`:0.04 `␣`:0.04 `␣what`:0.02 `␣yes`:0.02 `␣I`:0.02 `␣a`:0.02 `␣What`:0.02 `␣it`:0.02 | `␣describes` `␣describe` `␣mention` `␣introduces` `␣Yes` `␣how` `␣hello` `DDDD` `␣There` |
| 10 deflect | h-label `h` | `]:`:0.21 `:*`:0.21 `:**`:0.21 `\):`:0.20 `ï¼ļ`:0.20 `:+`:0.20 `:\"`:0.20 `:``:0.20 `:(-`:0.20 `():`:0.20 | `:\>` `ournal` `allery` `é»ĺ` `omen` `:`` `xea` `abeth` `yyt` `åĳĺ` | `:\"`:0.18 `WRK`:0.17 `:\>`:0.16 `ZXJ`:0.16 `:``:0.16 `():`:0.16 | `:`:0.74 `.`:0.04 `,`:0.02 `2`:0.01 `anna`:0.01 `⏎⏎`:0.01 `1`:0.01 `.:`:0.01 `?`:0.01 `␣`:0.01 | `]:` `:*` `:**` `\):` `ï¼ļ` `:+` `:\"` `:`` `:(-` `():` |
| 11 deflect | final `:` | `␣Yes`:0.17 `␣There`:0.17 `␣Because`:0.16 `␣That`:0.15 `␣Now`:0.15 `␣The`:0.15 `␣What`:0.15 `␣Then`:0.15 `␣Let`:0.15 `␣How`:0.15 | `unrecognized` `typography` `ecause` `essages` `EEEEEEEE` `descr` `eday` `essage` `␣Because` `ellipsis` | `typography`:0.15 `Inp`:0.14 `DDDD`:0.14 `descr`:0.13 `ellipsis`:0.13 `WWWW`:0.13 | `␣The`:0.07 `␣I`:0.07 `␣Yes`:0.07 `␣It`:0.05 `␣What`:0.04 `␣No`:0.03 `␣`:0.03 `⏎⏎`:0.02 `␣Well`:0.02 `␣You`:0.02 | `␣There` `␣Because` `␣That` `␣Now` `␣Then` `␣Let` `␣How` |
| 11 deflect | h-label `h` | `]:`:0.20 `:*`:0.20 `:**`:0.20 `\):`:0.19 `ï¼ļ`:0.19 `:+`:0.19 `:``:0.19 `:\"`:0.19 `:_`:0.19 `_:`:0.19 | `:\>` `:`` `é»ĺ` `omen` `ournal` `yyt` `xea` `:\"` `allery` `ccall` | `:\"`:0.18 `WRK`:0.16 `:``:0.16 `:\>`:0.16 `():`:0.15 `ZXJ`:0.15 | `:`:0.88 `.`:0.02 `,`:0.02 `;`:0.01 `.:`:0.01 `art`:0.00 `␣`:0.00 `⏎⏎`:0.00 `?`:0.00 `1`:0.00 | `]:` `:*` `:**` `\):` `ï¼ļ` `:+` `:`` `:\"` `:_` `_:` |

### 91m-leaf L16  (mean max loading at final position 0.246; mean |top10 loading ∩ top10 prediction| = 4.2/10)

| prompt | pos | loading top-10 (cos) | paper readout softmax(W_U norm(J h)) top-10 | centered loading top-10 (diagnostic) | model top-10 next tokens (p) | loaded, not predicted |
|---|---|---|---|---|---|---|
| 0 greeting | final `:` | `␣Yes`:0.26 `␣There`:0.25 `␣The`:0.24 `␣What`:0.23 `␣Because`:0.22 `␣That`:0.22 `␣Here`:0.22 `␣It`:0.21 `␣Please`:0.21 `␣Why`:0.21 | `␣There` `␣Yes` `␣That` `␣Because` `unrecognized` `␣Here` `␣Then` `␣You` `␣It` `␣They` | `␣Yes`:0.24 `␣There`:0.24 `␣Here`:0.22 `␣Because`:0.22 `␣Please`:0.21 `␣The`:0.21 | `␣Hi`:0.07 `␣Yes`:0.07 `␣I`:0.07 `␣The`:0.06 `⏎⏎`:0.06 `␣It`:0.04 `␣Oh`:0.03 `␣`:0.03 `␣What`:0.03 `␣No`:0.03 | `␣There` `␣Because` `␣That` `␣Here` `␣Please` `␣Why` |
| 0 greeting | h-label `h` | `:`:0.18 `.:`:0.17 `:*`:0.16 `:$`:0.16 `ï¼ļ`:0.16 `:{`:0.15 `:\"`:0.15 `:[`:0.14 `:,`:0.14 `anks`:0.14 | `.:` `:` `abeth` `:*` `:\"` `anks` `_:` `ï¼ļ` `:")` `letes` | `.:`:0.17 `:\"`:0.17 `ï¼ļ`:0.16 `:$`:0.16 `abeth`:0.15 `:*`:0.15 | `:`:0.98 `.:`:0.00 `.`:0.00 `␣`:0.00 `;`:0.00 `,`:0.00 `âĢĻ`:0.00 `⏎⏎`:0.00 `␣is`:0.00 `-`:0.00 | `:*` `:$` `ï¼ļ` `:{` `:\"` `:[` `:,` `anks` |
| 1 greeting | final `:` | `␣The`:0.24 `␣You`:0.23 `␣There`:0.23 `␣Because`:0.22 `␣We`:0.22 `␣Who`:0.22 `␣Those`:0.22 `␣What`:0.21 `␣That`:0.21 `␣Yes`:0.20 | `␣Those` `␣You` `␣There` `␣Because` `␣Who` `␣They` `unrecognized` `␣Your` `␣Everyone` `␣That` | `␣Those`:0.23 `␣There`:0.22 `␣Because`:0.22 `␣Who`:0.22 `␣You`:0.22 `␣The`:0.22 | `␣I`:0.26 `␣The`:0.06 `⏎⏎`:0.04 `␣It`:0.04 `␣`:0.04 `␣You`:0.03 `␣Who`:0.02 `␣Yes`:0.02 `␣In`:0.02 `␣We`:0.02 | `␣There` `␣Because` `␣Those` `␣What` `␣That` |
| 1 greeting | h-label `h` | `orry`:0.17 `umbled`:0.17 `.:`:0.16 `anks`:0.16 `ï¼ļ`:0.16 `ancer`:0.16 `abeth`:0.16 `:$`:0.16 `ights`:0.15 `:*`:0.15 | `abeth` `yyt` `atest` `apters` `anks` `orse` `omen` `ancer` `.:` `rets` | `abeth`:0.16 `umbled`:0.15 `orry`:0.15 `ancer`:0.15 `SSSSS`:0.15 `cbi`:0.14 | `:`:0.94 `.`:0.01 `;`:0.01 `,`:0.00 `.:`:0.00 `␣`:0.00 `âĢĻ`:0.00 `at`:0.00 `⏎⏎`:0.00 `1`:0.00 | `orry` `umbled` `anks` `ï¼ļ` `ancer` `abeth` `:$` `ights` `:*` |
| 2 greeting | final `:` | `␣There`:0.26 `␣The`:0.25 `␣Yes`:0.24 `␣Because`:0.23 `␣What`:0.23 `␣That`:0.23 `␣We`:0.22 `␣It`:0.22 `␣Those`:0.22 `␣Remember`:0.22 | `␣There` `unrecognized` `␣Because` `␣Those` `␣That` `␣Yes` `␣They` `␣Before` `␣It` `␣Two` | `␣There`:0.26 `␣Because`:0.24 `␣Those`:0.23 `␣Remember`:0.23 `␣Yes`:0.23 `␣Before`:0.23 | `␣The`:0.08 `␣I`:0.07 `␣Yes`:0.06 `␣G`:0.06 `␣It`:0.06 `␣A`:0.04 `␣There`:0.03 `␣In`:0.03 `␣You`:0.02 `␣And`:0.02 | `␣Because` `␣What` `␣That` `␣We` `␣Those` `␣Remember` |
| 2 greeting | h-label `h` | `.:`:0.16 `:`:0.16 `:*`:0.16 `:$`:0.16 `ï¼ļ`:0.15 `:[`:0.15 `:(`:0.14 `:,`:0.14 `:{`:0.14 `:\"`:0.14 | `.:` `:*` `:` `xea` `_:` `:[` `:$` `yyt` `abeth` `apters` | `.:`:0.16 `:$`:0.15 `ï¼ļ`:0.15 `:\"`:0.15 `:[`:0.14 `:*`:0.14 | `:`:0.98 `.`:0.01 `.:`:0.00 `,`:0.00 `;`:0.00 `␣`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 `-`:0.00 `␣and`:0.00 | `:*` `:$` `ï¼ļ` `:[` `:(` `:,` `:{` `:\"` |
| 3 talk | final `:` | `␣They`:0.28 `␣There`:0.28 `␣Because`:0.27 `␣The`:0.27 `␣Yes`:0.27 `␣Nothing`:0.26 `␣Those`:0.25 `␣Only`:0.24 `␣We`:0.24 `␣Remember`:0.24 | `␣They` `␣There` `␣Their` `␣Because` `␣Those` `␣Nothing` `␣Yes` `␣Only` `They` `␣Neither` | `␣They`:0.27 `␣There`:0.27 `␣Because`:0.27 `␣Those`:0.26 `␣Nothing`:0.26 `␣Yes`:0.25 | `␣Yes`:0.14 `␣They`:0.11 `␣No`:0.10 `␣The`:0.09 `␣I`:0.09 `␣It`:0.05 `␣There`:0.02 `␣Not`:0.02 `␣`:0.01 `␣In`:0.01 | `␣Because` `␣Nothing` `␣Those` `␣Only` `␣We` `␣Remember` |
| 3 talk | h-label `h` | `:`:0.18 `.:`:0.17 `:*`:0.17 `:$`:0.17 `:(`:0.16 `:[`:0.16 `:,`:0.16 `ï¼ļ`:0.16 `:_`:0.15 `:+`:0.15 | `.:` `:` `:*` `_:` `:[` `:$` `:_` `apters` `:+` `abeth` | `.:`:0.16 `:$`:0.16 `ï¼ļ`:0.16 `:[`:0.15 `:*`:0.15 `:,`:0.15 | `:`:0.99 `;`:0.00 `.`:0.00 `.:`:0.00 `,`:0.00 `␣`:0.00 `:.`:0.00 `-`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 | `:*` `:$` `:(` `:[` `:,` `ï¼ļ` `:_` `:+` |
| 4 talk | final `:` | `␣The`:0.28 `␣Because`:0.25 `␣There`:0.25 `␣Nothing`:0.23 `␣Reading`:0.23 `␣It`:0.23 `␣Every`:0.22 `␣Only`:0.22 `␣Two`:0.22 `␣Well`:0.22 | `␣Because` `␣There` `␣Reading` `␣From` `␣Nothing` `␣The` `␣Only` `␣Writing` `␣Two` `␣Through` | `␣Reading`:0.24 `␣The`:0.24 `␣Because`:0.24 `␣There`:0.23 `␣Nothing`:0.23 `␣Before`:0.22 | `␣The`:0.14 `␣I`:0.12 `␣It`:0.08 `␣A`:0.05 `␣In`:0.03 `␣Reading`:0.03 `␣Well`:0.02 `␣There`:0.02 `␣`:0.02 `␣What`:0.02 | `␣Because` `␣Nothing` `␣Every` `␣Only` `␣Two` |
| 4 talk | h-label `h` | `iana`:0.17 `orry`:0.17 `anka`:0.17 `umbled`:0.17 `anks`:0.17 `ï¼ļ`:0.17 `ursday`:0.17 `abeth`:0.16 `ancer`:0.16 `ione`:0.16 | `yyt` `abeth` `omen` `anks` `iana` `xea` `ente` `orse` `akespeare` `ursday` | `abeth`:0.16 `iana`:0.15 `anka`:0.15 `akespeare`:0.15 `umbled`:0.15 `SSSSS`:0.15 | `:`:0.92 `ira`:0.01 `.`:0.01 `,`:0.00 `.:`:0.00 `ia`:0.00 `;`:0.00 `ora`:0.00 `ina`:0.00 `ua`:0.00 | `iana` `orry` `anka` `umbled` `anks` `ï¼ļ` `ursday` `abeth` `ancer` `ione` |
| 5 talk | final `:` | `␣There`:0.26 `␣Yes`:0.25 `␣The`:0.24 `␣Nothing`:0.24 `␣We`:0.23 `␣Only`:0.23 `␣Because`:0.23 `␣It`:0.23 `␣Never`:0.22 `␣Remember`:0.22 | `␣There` `␣Nothing` `␣Only` `␣Yes` `unrecognized` `␣Because` `␣Always` `␣Before` `␣During` `␣Two` | `␣There`:0.25 `␣Nothing`:0.25 `␣Yes`:0.24 `␣Only`:0.24 `␣Never`:0.24 `␣Always`:0.24 | `␣I`:0.29 `␣Yes`:0.14 `␣No`:0.11 `␣The`:0.04 `␣It`:0.03 `␣Oh`:0.02 `␣In`:0.02 `␣`:0.02 `␣Not`:0.02 `␣Aw`:0.01 | `␣There` `␣Nothing` `␣We` `␣Only` `␣Because` `␣Never` `␣Remember` |
| 5 talk | h-label `h` | `:`:0.19 `.:`:0.18 `:$`:0.17 `:*`:0.17 `:(`:0.16 `:[`:0.16 `ï¼ļ`:0.16 `:_`:0.16 `:,`:0.16 `:+`:0.16 | `.:` `:` `:*` `_:` `:[` `:$` `:_` `:+` `ï¼ļ` `]:` | `.:`:0.17 `:$`:0.17 `ï¼ļ`:0.16 `:[`:0.16 `:*`:0.16 `:+`:0.15 | `:`:0.99 `;`:0.00 `.`:0.00 `.:`:0.00 `,`:0.00 `␣`:0.00 `:.`:0.00 `-`:0.00 `âĢĻ`:0.00 `⏎⏎`:0.00 | `:$` `:*` `:(` `:[` `ï¼ļ` `:_` `:,` `:+` |
| 6 talk | final `:` | `␣Because`:0.21 `␣There`:0.21 `␣It`:0.20 `␣Yes`:0.19 `␣The`:0.18 `␣That`:0.18 `␣Every`:0.17 `␣Only`:0.17 `␣When`:0.17 `␣Does`:0.17 | `␣Because` `␣There` `␣It` `␣Yes` `␣That` `␣Only` `␣Neither` `ecause` `␣Every` `There` | `␣Because`:0.20 `␣There`:0.19 `␣It`:0.19 `␣Yes`:0.18 `␣That`:0.17 `␣Only`:0.17 | `␣It`:0.08 `␣A`:0.08 `␣I`:0.08 `␣The`:0.06 `⏎⏎`:0.05 `␣Yes`:0.04 `␣a`:0.03 `␣No`:0.03 `␣In`:0.02 `␣`:0.02 | `␣Because` `␣There` `␣That` `␣Every` `␣Only` `␣When` `␣Does` |
| 6 talk | h-label `h` | `umbled`:0.17 `orry`:0.17 `orse`:0.17 `iana`:0.16 `anks`:0.16 `abeth`:0.16 `undred`:0.16 `ternoon`:0.16 `ights`:0.16 `orizon`:0.16 | `abeth` `orse` `yyt` `anks` `undred` `rets` `xea` `orses` `iana` `erman` | `orse`:0.16 `abeth`:0.16 `umbled`:0.16 `undred`:0.15 `iana`:0.15 `cbi`:0.15 | `:`:0.88 `.`:0.01 `;`:0.01 `.:`:0.01 `,`:0.00 `2`:0.00 `3`:0.00 `ii`:0.00 `ov`:0.00 `⏎⏎`:0.00 | `umbled` `orry` `orse` `iana` `anks` `abeth` `undred` `ternoon` `ights` `orizon` |
| 7 talk | final `:` | `␣Because`:0.26 `␣There`:0.26 `␣The`:0.26 `␣It`:0.24 `␣What`:0.22 `␣That`:0.22 `␣They`:0.22 `␣Nothing`:0.22 `␣We`:0.22 `␣Yes`:0.21 | `␣Because` `␣There` `␣They` `␣It` `␣Those` `␣Nothing` `␣That` `␣Only` `␣The` `␣Everyone` | `␣Because`:0.26 `␣There`:0.25 `␣Nothing`:0.23 `␣The`:0.23 `␣It`:0.23 `␣Those`:0.22 | `␣I`:0.16 `␣The`:0.07 `␣It`:0.06 `␣He`:0.03 `⏎⏎`:0.03 `␣`:0.03 `␣What`:0.02 `␣In`:0.02 `␣There`:0.02 `␣A`:0.02 | `␣Because` `␣That` `␣They` `␣Nothing` `␣We` `␣Yes` |
| 7 talk | h-label `h` | `umbled`:0.17 `orry`:0.17 `ancer`:0.16 `iana`:0.16 `anks`:0.16 `:$`:0.16 `abeth`:0.16 `.:`:0.15 `ights`:0.15 `ï¼ļ`:0.15 | `yyt` `abeth` `ancer` `atest` `anks` `orse` `iana` `apters` `omen` `xea` | `umbled`:0.15 `abeth`:0.15 `ancer`:0.15 `iana`:0.15 `xdb`:0.15 `cbi`:0.15 | `:`:0.94 `;`:0.01 `.`:0.01 `,`:0.00 `.:`:0.00 `␣`:0.00 `⏎⏎`:0.00 `âĢĻ`:0.00 `1`:0.00 `3`:0.00 | `umbled` `orry` `ancer` `iana` `anks` `:$` `abeth` `ights` `ï¼ļ` |
| 8 talk | final `:` | `␣That`:0.27 `␣There`:0.25 `␣The`:0.25 `␣Yes`:0.24 `␣It`:0.24 `␣Because`:0.23 `␣What`:0.23 `␣Those`:0.21 `␣Nothing`:0.21 `␣You`:0.21 | `␣That` `␣There` `␣It` `␣Yes` `␣Because` `␣Those` `That` `␣Nothing` `␣They` `␣Another` | `␣That`:0.26 `␣There`:0.24 `␣Yes`:0.23 `␣Because`:0.23 `␣Those`:0.22 `␣It`:0.22 | `␣The`:0.10 `␣It`:0.08 `␣Yes`:0.07 `␣I`:0.06 `␣That`:0.05 `␣`:0.03 `␣What`:0.02 `␣But`:0.02 `␣There`:0.02 `␣No`:0.02 | `␣Because` `␣Those` `␣Nothing` `␣You` |
| 8 talk | h-label `h` | `.:`:0.18 `:`:0.18 `:$`:0.17 `:*`:0.17 `ï¼ļ`:0.16 `:[`:0.16 `:(`:0.15 `:_`:0.15 `:{`:0.15 `:,`:0.15 | `.:` `:*` `:` `:$` `abeth` `_:` `apters` `:_` `:[` `:")` | `:$`:0.16 `.:`:0.16 `ï¼ļ`:0.15 `:*`:0.15 `:[`:0.15 `:_`:0.14 | `:`:0.99 `.`:0.00 `.:`:0.00 `;`:0.00 `⏎⏎`:0.00 `,`:0.00 `:.`:0.00 `␣`:0.00 `-`:0.00 `:*`:0.00 | `:$` `ï¼ļ` `:[` `:(` `:_` `:{` `:,` |
| 9 deflect | final `:` | `␣Yes`:0.23 `␣The`:0.23 `␣Please`:0.22 `␣You`:0.22 `␣That`:0.22 `␣There`:0.22 `␣What`:0.22 `␣This`:0.21 `␣It`:0.21 `␣Because`:0.21 | `␣That` `␣You` `␣Your` `unrecognized` `␣Yes` `␣There` `␣Please` `␣Then` `␣Because` `␣Two` | `␣Please`:0.20 `␣Yes`:0.19 `␣That`:0.19 `␣You`:0.19 `␣Write`:0.19 `␣There`:0.19 | `␣I`:0.06 `␣The`:0.06 `⏎⏎`:0.05 `␣`:0.04 `␣Write`:0.04 `␣You`:0.03 `␣A`:0.03 `␣It`:0.03 `␣That`:0.03 `␣Yes`:0.02 | `␣Please` `␣There` `␣What` `␣This` `␣Because` |
| 9 deflect | h-label `h` | `umbled`:0.18 `ancer`:0.17 `orse`:0.17 `undred`:0.17 `orry`:0.17 `ternoon`:0.17 `orizon`:0.17 `oman`:0.17 `erman`:0.16 `iana`:0.16 | `yyt` `orse` `ccall` `isher` `ender` `ancer` `erman` `abeth` `omen` `sman` | `ancer`:0.16 `orse`:0.16 `umbled`:0.15 `undred`:0.15 `ccall`:0.15 `erman`:0.15 | `:`:0.63 `,`:0.06 `.`:0.02 `;`:0.02 `2`:0.01 `ime`:0.01 `te`:0.01 `1`:0.01 `ite`:0.01 `?`:0.01 | `umbled` `ancer` `orse` `undred` `orry` `ternoon` `orizon` `oman` `erman` `iana` |
| 10 deflect | final `:` | `␣yes`:0.17 `␣There`:0.17 `␣The`:0.17 `␣Yes`:0.16 `␣What`:0.15 `␣pause`:0.15 `␣That`:0.15 `␣Please`:0.14 `␣Here`:0.14 `␣Then`:0.14 | `␣yes` `␣There` `EEEEEEEE` `typography` `ellipsis` `etween` `␣Then` `unrecognized` `DDDD` `␣Yes` | `␣There`:0.15 `AAAAAAAAAAAAAAAA`:0.15 `EEEEEEEE`:0.15 `␣yes`:0.15 `DDDD`:0.14 `******************************************************************`:0.14 | `␣the`:0.06 `␣The`:0.04 `⏎⏎`:0.04 `␣`:0.04 `␣what`:0.02 `␣yes`:0.02 `␣I`:0.02 `␣a`:0.02 `␣What`:0.02 `␣it`:0.02 | `␣There` `␣Yes` `␣pause` `␣That` `␣Please` `␣Here` `␣Then` |
| 10 deflect | h-label `h` | `iana`:0.18 `anka`:0.17 `umbled`:0.17 `anks`:0.17 `ancer`:0.17 `erman`:0.17 `anna`:0.16 `ancers`:0.16 `orse`:0.16 `abeth`:0.16 | `erman` `iana` `abeth` `yyt` `anks` `orse` `ender` `ancer` `ccall` `anka` | `iana`:0.16 `erman`:0.15 `ancer`:0.15 `anka`:0.15 `umbled`:0.15 `cbi`:0.15 | `:`:0.74 `.`:0.04 `,`:0.02 `2`:0.01 `anna`:0.01 `⏎⏎`:0.01 `1`:0.01 `.:`:0.01 `?`:0.01 `␣`:0.01 | `iana` `anka` `umbled` `anks` `ancer` `erman` `ancers` `orse` `abeth` |
| 11 deflect | final `:` | `␣The`:0.23 `␣Yes`:0.22 `␣There`:0.22 `␣Because`:0.22 `␣What`:0.21 `␣It`:0.21 `␣That`:0.20 `␣Please`:0.20 `␣We`:0.20 `␣Thank`:0.19 | `␣There` `␣Because` `␣Yes` `␣That` `␣It` `␣Then` `␣Your` `␣Nothing` `␣The` `unrecognized` | `␣Because`:0.23 `␣There`:0.22 `␣Yes`:0.22 `␣The`:0.21 `␣Please`:0.21 `␣It`:0.20 | `␣The`:0.07 `␣I`:0.07 `␣Yes`:0.07 `␣It`:0.05 `␣What`:0.04 `␣No`:0.03 `␣`:0.03 `⏎⏎`:0.02 `␣Well`:0.02 `␣You`:0.02 | `␣There` `␣Because` `␣That` `␣Please` `␣We` `␣Thank` |
| 11 deflect | h-label `h` | `umbled`:0.17 `ancer`:0.17 `orry`:0.16 `anks`:0.16 `orse`:0.16 `oman`:0.16 `erman`:0.15 `iana`:0.15 `anka`:0.15 `ights`:0.15 | `yyt` `ancer` `orse` `anks` `erman` `abeth` `ccall` `ancers` `omen` `apters` | `ancer`:0.16 `umbled`:0.16 `orse`:0.15 `xdb`:0.15 `erman`:0.14 `anks`:0.14 | `:`:0.88 `.`:0.02 `,`:0.02 `;`:0.01 `.:`:0.01 `art`:0.00 `␣`:0.00 `⏎⏎`:0.00 `?`:0.00 `1`:0.00 | `umbled` `ancer` `orry` `anks` `orse` `oman` `erman` `iana` `anka` `ights` |

## Injection (flexible use): capital recall after adding a country direction at the filler's last token

Lift = mean log p(capital tokens) after injection minus before; 'others' = the same lift averaged over the 11 other capitals; 'specific' = correct - others; top1 = fraction of fillers where the correct capital has the highest per-token log-prob among the 12 capitals.

### 90m-base L16 (inject-inject_pos.json; 40 fillers x 12 countries; alpha in units of ||h_l||=77.7); baseline top1 0.08; natural-prompt ceiling lift +3.80

| direction | alpha | lift correct | lift others | specific | top1 among capitals |
|---|---|---|---|---|---|
| lens | 2 | -0.47 | -1.66 | +1.19 | 0.10 |
| lens | 4 | -2.35 | -3.26 | +0.91 | 0.07 |
| lens | 8 | -3.85 | -4.79 | +0.93 | 0.02 |
| unembed | 2 | -1.38 | -2.43 | +1.05 | 0.09 |
| unembed | 4 | -5.73 | -6.51 | +0.78 | 0.03 |
| unembed | 8 | -7.13 | -9.22 | +2.09 | 0.06 |
| random | 2 | -0.34 | -0.44 | +0.09 | 0.08 |
| random | 4 | -0.99 | -1.26 | +0.27 | 0.08 |
| random | 8 | -2.16 | -2.44 | +0.28 | 0.07 |

Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):

| country | base | natural | top1 | lens | unembed | random |
|---|---|---|---|---|---|---|
| France | -9.29 | -5.36 | 0.00 | +1.22 | +5.33 | +0.54 |
| Italy | -9.36 | -6.68 | 0.00 | +3.46 | +4.00 | +0.26 |
| Germany | -10.53 | -6.55 | 0.00 | +3.30 | +6.58 | +1.51 |
| England | -8.80 | -6.19 | 0.00 | +12.73 | +9.94 | +3.09 |
| Japan | -9.94 | -4.26 | 0.00 | +3.20 | +1.72 | -0.17 |
| Egypt | -9.03 | -5.92 | 0.00 | -0.93 | -2.30 | +0.00 |
| Spain | -10.51 | -6.58 | 0.00 | +1.28 | -0.34 | -0.03 |
| Russia | -7.91 | -4.90 | 0.00 | +0.86 | +0.19 | +0.05 |
| China | -9.29 | -4.91 | 0.95 | +0.67 | -4.78 | +0.23 |
| Canada | -11.89 | -8.42 | 0.00 | -6.24 | -6.69 | +0.02 |
| Brazil | -13.76 | -7.62 | 0.05 | -3.10 | -0.83 | -0.24 |
| Greece | -9.03 | -6.38 | 0.00 | -5.58 | -3.47 | -2.01 |

### 90m-base L12 (inject-inject_pos.json; 40 fillers x 12 countries; alpha in units of ||h_l||=37.1); baseline top1 0.08; natural-prompt ceiling lift +3.80

| direction | alpha | lift correct | lift others | specific | top1 among capitals |
|---|---|---|---|---|---|
| lens | 2 | -0.03 | -0.67 | +0.64 | 0.08 |
| lens | 4 | -1.70 | -2.56 | +0.86 | 0.13 |
| lens | 8 | -3.92 | -5.31 | +1.38 | 0.13 |
| unembed | 2 | +0.24 | -0.90 | +1.14 | 0.10 |
| unembed | 4 | -1.73 | -2.64 | +0.91 | 0.10 |
| unembed | 8 | -5.72 | -5.68 | -0.04 | 0.01 |
| random | 2 | -0.00 | -0.04 | +0.04 | 0.09 |
| random | 4 | -0.09 | -0.32 | +0.24 | 0.13 |
| random | 8 | -0.61 | -1.63 | +1.02 | 0.11 |

Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):

| country | base | natural | top1 | lens | unembed | random |
|---|---|---|---|---|---|---|
| France | -9.29 | -5.36 | 0.00 | +2.03 | +1.34 | +0.17 |
| Italy | -9.36 | -6.68 | 0.00 | +1.18 | +0.43 | +0.02 |
| Germany | -10.53 | -6.55 | 0.00 | +6.68 | +3.56 | +0.02 |
| England | -8.80 | -6.19 | 0.00 | +2.77 | +4.94 | +0.56 |
| Japan | -9.94 | -4.26 | 0.00 | +0.93 | +2.44 | +0.61 |
| Egypt | -9.03 | -5.92 | 0.00 | -0.02 | -0.91 | +0.06 |
| Spain | -10.51 | -6.58 | 0.00 | -2.07 | +0.25 | +0.36 |
| Russia | -7.91 | -4.90 | 0.00 | +2.38 | +4.75 | +0.05 |
| China | -9.29 | -4.91 | 0.95 | +1.51 | +3.68 | +0.13 |
| Canada | -11.89 | -8.42 | 0.00 | -4.36 | -6.17 | +0.08 |
| Brazil | -13.76 | -7.62 | 0.05 | -0.78 | -3.68 | +0.64 |
| Greece | -9.03 | -6.38 | 0.00 | +0.12 | +0.34 | +0.17 |

### 90m-base L8 (inject-inject_pos.json; 40 fillers x 12 countries; alpha in units of ||h_l||=11.2); baseline top1 0.08; natural-prompt ceiling lift +3.80

| direction | alpha | lift correct | lift others | specific | top1 among capitals |
|---|---|---|---|---|---|
| lens | 2 | +0.96 | +0.67 | +0.29 | 0.08 |
| lens | 4 | +1.00 | +0.67 | +0.32 | 0.07 |
| lens | 8 | +0.26 | -0.47 | +0.73 | 0.04 |
| unembed | 2 | +0.93 | +0.40 | +0.53 | 0.09 |
| unembed | 4 | +1.00 | +0.31 | +0.69 | 0.10 |
| unembed | 8 | -0.06 | -0.72 | +0.66 | 0.09 |
| random | 2 | +0.18 | +0.22 | -0.03 | 0.08 |
| random | 4 | +0.14 | +0.27 | -0.14 | 0.08 |
| random | 8 | +0.12 | +0.15 | -0.02 | 0.08 |

Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):

| country | base | natural | top1 | lens | unembed | random |
|---|---|---|---|---|---|---|
| France | -9.29 | -5.36 | 0.00 | +0.17 | +0.83 | -0.09 |
| Italy | -9.36 | -6.68 | 0.00 | +0.75 | +0.30 | -0.12 |
| Germany | -10.53 | -6.55 | 0.00 | +0.38 | +0.99 | +0.08 |
| England | -8.80 | -6.19 | 0.00 | +0.52 | +3.03 | -0.14 |
| Japan | -9.94 | -4.26 | 0.00 | +0.46 | +0.59 | +0.06 |
| Egypt | -9.03 | -5.92 | 0.00 | +0.38 | +0.12 | -0.00 |
| Spain | -10.51 | -6.58 | 0.00 | +0.54 | +0.22 | +0.38 |
| Russia | -7.91 | -4.90 | 0.00 | +0.38 | +1.26 | +0.01 |
| China | -9.29 | -4.91 | 0.95 | -0.43 | +0.10 | -0.31 |
| Canada | -11.89 | -8.42 | 0.00 | +0.32 | +0.95 | +0.10 |
| Brazil | -13.76 | -7.62 | 0.05 | +0.29 | -0.17 | -1.92 |
| Greece | -9.03 | -6.38 | 0.00 | +0.14 | +0.06 | +0.28 |

### 91m-leaf L12 (inject-inject_pos.json; 40 fillers x 12 countries; alpha in units of ||h_l||=47.5); baseline top1 0.08; natural-prompt ceiling lift +1.87

| direction | alpha | lift correct | lift others | specific | top1 among capitals |
|---|---|---|---|---|---|
| lens | 2 | -0.04 | -1.26 | +1.23 | 0.09 |
| lens | 4 | -1.38 | -2.61 | +1.23 | 0.12 |
| lens | 8 | -3.21 | -4.22 | +1.01 | 0.08 |
| unembed | 2 | -0.00 | -0.46 | +0.46 | 0.08 |
| unembed | 4 | -1.17 | -1.34 | +0.17 | 0.05 |
| unembed | 8 | -3.12 | -2.86 | -0.26 | 0.07 |
| random | 2 | +0.02 | +0.03 | -0.00 | 0.08 |
| random | 4 | +0.02 | +0.00 | +0.01 | 0.09 |
| random | 8 | -0.15 | -0.20 | +0.05 | 0.09 |

Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):

| country | base | natural | top1 | lens | unembed | random |
|---|---|---|---|---|---|---|
| France | -9.74 | -8.65 | 0.00 | +3.69 | +1.21 | +0.13 |
| Italy | -9.52 | -8.98 | 0.00 | +3.09 | +0.74 | -0.05 |
| Germany | -10.18 | -8.92 | 0.00 | +2.89 | +1.44 | +0.08 |
| England | -9.16 | -8.52 | 0.00 | +3.12 | +3.47 | +0.00 |
| Japan | -10.43 | -7.84 | 0.00 | +0.54 | +0.03 | +0.04 |
| Egypt | -9.84 | -7.56 | 0.00 | +0.38 | -1.43 | +0.03 |
| Spain | -10.57 | -9.05 | 0.00 | +0.81 | +0.97 | +0.10 |
| Russia | -9.01 | -6.80 | 0.00 | -0.11 | -2.92 | -0.07 |
| China | -10.59 | -7.59 | 0.07 | +1.10 | +0.42 | +0.05 |
| Canada | -12.84 | -10.44 | 0.00 | +1.92 | -0.00 | +0.06 |
| Brazil | -12.62 | -8.86 | 0.93 | -1.58 | -2.11 | -0.08 |
| Greece | -9.36 | -8.17 | 0.00 | -1.12 | +0.22 | -0.13 |

### 91m-leaf L8 (inject-inject_pos.json; 40 fillers x 12 countries; alpha in units of ||h_l||=15.8); baseline top1 0.08; natural-prompt ceiling lift +1.87

| direction | alpha | lift correct | lift others | specific | top1 among capitals |
|---|---|---|---|---|---|
| lens | 2 | +0.59 | +0.18 | +0.41 | 0.08 |
| lens | 4 | +0.48 | -0.05 | +0.53 | 0.09 |
| lens | 8 | -0.29 | -0.95 | +0.66 | 0.09 |
| unembed | 2 | +0.49 | +0.08 | +0.42 | 0.08 |
| unembed | 4 | +0.49 | +0.01 | +0.48 | 0.09 |
| unembed | 8 | +0.14 | -0.49 | +0.63 | 0.08 |
| random | 2 | +0.16 | +0.19 | -0.03 | 0.08 |
| random | 4 | +0.21 | +0.26 | -0.06 | 0.07 |
| random | 8 | +0.18 | +0.26 | -0.08 | 0.06 |

Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):

| country | base | natural | top1 | lens | unembed | random |
|---|---|---|---|---|---|---|
| France | -9.74 | -8.65 | 0.00 | +1.19 | +0.79 | +0.07 |
| Italy | -9.52 | -8.98 | 0.00 | +0.79 | +0.27 | +0.07 |
| Germany | -10.18 | -8.92 | 0.00 | +0.99 | +0.91 | +0.09 |
| England | -9.16 | -8.52 | 0.00 | +0.39 | +2.37 | +0.03 |
| Japan | -10.43 | -7.84 | 0.00 | -0.29 | +0.39 | -0.09 |
| Egypt | -9.84 | -7.56 | 0.00 | +1.10 | -0.08 | +0.04 |
| Spain | -10.57 | -9.05 | 0.00 | +1.09 | -0.00 | -0.17 |
| Russia | -9.01 | -6.80 | 0.00 | +1.44 | +1.30 | -0.08 |
| China | -10.59 | -7.59 | 0.07 | -0.15 | -0.24 | -0.11 |
| Canada | -12.84 | -10.44 | 0.00 | +0.19 | +0.09 | -0.01 |
| Brazil | -12.62 | -8.86 | 0.93 | -0.65 | +0.01 | -0.61 |
| Greece | -9.36 | -8.17 | 0.00 | +0.31 | -0.02 | +0.07 |

### 91m-leaf L16 (inject-inject_pos.json; 40 fillers x 12 countries; alpha in units of ||h_l||=99.0); baseline top1 0.08; natural-prompt ceiling lift +1.87

| direction | alpha | lift correct | lift others | specific | top1 among capitals |
|---|---|---|---|---|---|
| lens | 2 | +0.80 | -1.52 | +2.32 | 0.12 |
| lens | 4 | -0.11 | -2.68 | +2.57 | 0.12 |
| lens | 8 | -1.04 | -3.66 | +2.63 | 0.18 |
| unembed | 2 | +0.10 | -0.97 | +1.07 | 0.13 |
| unembed | 4 | -2.08 | -2.82 | +0.74 | 0.05 |
| unembed | 8 | -3.51 | -4.36 | +0.84 | 0.02 |
| random | 2 | -0.23 | -0.11 | -0.12 | 0.09 |
| random | 4 | -0.48 | -0.33 | -0.15 | 0.08 |
| random | 8 | -0.89 | -0.71 | -0.19 | 0.05 |

Per country (base logp / natural logp / baseline top1; specific lift at alpha=4 for lens, unembed, random):

| country | base | natural | top1 | lens | unembed | random |
|---|---|---|---|---|---|---|
| France | -9.74 | -8.65 | 0.00 | +5.09 | +4.00 | +0.04 |
| Italy | -9.52 | -8.98 | 0.00 | +4.33 | +0.96 | +0.10 |
| Germany | -10.18 | -8.92 | 0.00 | +4.39 | +3.14 | -0.43 |
| England | -9.16 | -8.52 | 0.00 | +13.45 | +8.16 | +0.79 |
| Japan | -10.43 | -7.84 | 0.00 | +3.18 | +0.17 | -0.03 |
| Egypt | -9.84 | -7.56 | 0.00 | -3.28 | -1.30 | -0.11 |
| Spain | -10.57 | -9.05 | 0.00 | +2.79 | +0.19 | -0.22 |
| Russia | -9.01 | -6.80 | 0.00 | +2.77 | -4.31 | +0.01 |
| China | -10.59 | -7.59 | 0.07 | +0.25 | +0.76 | -0.22 |
| Canada | -12.84 | -10.44 | 0.00 | -0.32 | -1.71 | +0.01 |
| Brazil | -12.62 | -8.86 | 0.93 | -3.11 | -1.04 | -0.06 |
| Greece | -9.36 | -8.17 | 0.00 | +1.33 | -0.14 | -1.70 |

## Sparse decomposition (nonnegative OMP, k atoms): fraction of ||h_l||^2 explained

| model | layer | k | lens: room / library | unembed: room / library | random dict: room / library |
|---|---|---|---|---|---|
| 90m-base | 16 | 8 | 0.076 / 0.069 ± 0.020 | 0.059 / 0.077 | 0.207 / 0.205 |
| 90m-base | 12 | 8 | 0.044 / 0.060 ± 0.017 | 0.067 / 0.076 | 0.204 / 0.205 |
| 90m-base | 8 | 8 | 0.025 / 0.055 ± 0.023 | 0.064 / 0.077 | 0.211 / 0.208 |
| 91m-leaf | 12 | 8 | 0.064 / 0.067 ± 0.013 | 0.078 / 0.077 | 0.200 / 0.204 |
| 91m-leaf | 8 | 8 | 0.046 / 0.048 ± 0.017 | 0.072 / 0.073 | 0.204 / 0.206 |
| 91m-leaf | 16 | 8 | 0.106 / 0.082 ± 0.029 | 0.066 / 0.081 | 0.198 / 0.205 |

**90m-base L16** lens atoms at the final `:` of each room prompt (coefficient):  
- 0 greeting (0.066): `␣The`:4.4 `␣I`:5.7 `␣You`:4.0 `␣there`:2.8 `␣Thank`:2.5 `␣So`:1.8 `␣Yes`:1.4 `␣There`:2.1
- 1 greeting (0.083): `␣The`:6.8 `␣I`:6.4 `␣You`:5.7 `␣who`:2.8 `␣There`:3.3 `␣We`:1.6 `␣No`:0.8 `␣the`:0.6
- 2 greeting (0.075): `␣The`:3.5 `␣Thank`:5.6 `␣There`:5.2 `␣I`:3.8 `␣You`:3.5 `␣Yes`:1.3 `␣We`:1.5 `␣So`:1.0
- 3 talk (0.086): `␣There`:5.8 `␣Yes`:5.3 `␣The`:5.1 `␣I`:2.8 `␣They`:4.1 `␣No`:2.7 `␣We`:1.2 `␣You`:0.8
- 4 talk (0.078): `␣The`:11.3 `␣there`:4.3 `␣I`:5.5 `␣It`:2.4 `␣You`:1.2 `␣the`:0.8 `␣No`:0.6 `␣Today`:0.6
- 5 talk (0.077): `␣Yes`:5.3 `␣The`:4.3 `␣I`:5.7 `␣There`:4.8 `␣You`:2.9 `␣no`:0.7 `␣Are`:1.3 `␣No`:2.7
- 6 talk (0.074): `␣It`:5.2 `␣yes`:3.1 `␣The`:5.8 `␣there`:0.7 `␣is`:2.8 `␣That`:2.6 `␣I`:2.0 `␣There`:4.5
- 7 talk (0.076): `␣The`:8.3 `␣I`:6.8 `␣there`:0.8 `␣That`:1.4 `␣You`:1.2 `␣There`:5.1 `␣yes`:1.4 `␣what`:1.2
- 8 talk (0.078): `␣That`:8.2 `␣the`:2.4 `␣There`:1.1 `␣But`:3.1 `␣I`:0.8 `␣The`:5.9 `␣yes`:1.1 `␣there`:4.2
- 9 deflect (0.075): `␣The`:8.4 `␣let`:4.4 `you`:3.6 `␣hello`:4.1 `␣Write`:3.6 `␣I`:1.6 `␣If`:1.8 `␣try`:1.2
- 10 deflect (0.068): `␣The`:12.1 `␣there`:5.6 `␣first`:2.8 `␣i`:1.3 `the`:0.6 `␣the`:1.3 `1`:0.9 `␣let`:0.7
- 11 deflect (0.073): `␣The`:11.3 `␣there`:4.6 `␣I`:2.9 `␣No`:2.9 `␣It`:3.0 `␣Thank`:1.3 `the`:0.8 `␣Today`:0.6

**90m-base L12** lens atoms at the final `:` of each room prompt (coefficient):  
- 0 greeting (0.044): `␣The`:3.9 `␣hello`:2.2 `That`:2.7 `␣you`:1.2 `␣but`:0.3 `␣no`:1.1 `␣and`:0.5 `␣this`:0.6
- 1 greeting (0.041): `␣The`:3.3 `␣those`:0.0 `This`:3.2 `␣but`:0.9 `␣you`:0.8 `␣none`:1.3 `␣My`:1.4 `␣the`:1.9
- 2 greeting (0.039): `␣The`:3.8 `␣there`:1.7 `But`:1.3 `␣one`:1.1 `␣Thank`:0.5 `␣this`:1.0 `␣No`:0.8 `That`:1.3
- 3 talk (0.050): `␣There`:2.7 `␣this`:2.0 `Yes`:0.8 `␣But`:1.4 `␣The`:2.3 `␣yes`:1.5 `␣none`:0.8 `That`:1.7
- 4 talk (0.039): `␣The`:4.4 `␣there`:1.0 `That`:1.5 `␣one`:1.9 `␣the`:1.3 `␣was`:0.5 `Today`:0.6 `It`:1.1
- 5 talk (0.041): `␣There`:1.5 `␣yes`:1.4 `This`:2.2 `␣The`:3.0 `␣no`:2.2 `␣but`:0.5 `␣hello`:0.6 `␣That`:0.6
- 6 talk (0.049): `␣This`:2.3 `␣there`:1.6 `The`:2.7 `␣the`:1.9 `␣But`:0.2 `␣because`:1.6 `␣It`:1.5 `␣The`:1.8
- 7 talk (0.040): `␣The`:3.9 `␣there`:1.4 `That`:3.0 `␣but`:0.9 `␣this`:0.9 `␣one`:0.7 `␣It`:0.8 `␣the`:0.9
- 8 talk (0.045): `␣The`:4.4 `␣there`:1.3 `That`:2.9 `␣but`:1.7 `␣this`:1.3 `␣how`:0.4 `␣no`:0.4 `␣to`:0.3
- 9 deflect (0.051): `␣The`:4.0 `␣you`:1.8 `This`:3.5 `␣one`:2.1 `␣Let`:0.5 `␣to`:0.6 `␣if`:0.9 `␣Write`:0.6
- 10 deflect (0.048): `␣The`:4.4 `␣there`:1.6 `This`:2.2 `␣one`:1.5 `␣the`:1.8 `␣how`:0.3 `There`:1.5 `␣but`:0.3
- 11 deflect (0.042): `␣The`:4.5 `␣there`:1.7 `This`:2.2 `␣no`:1.7 `␣but`:0.4 `␣the`:0.6 `␣Today`:0.4 `That`:0.7

**90m-base L8** lens atoms at the final `:` of each room prompt (coefficient):  
- 0 greeting (0.023): `␣The`:0.5 `but`:0.2 `␣No`:0.3 `␣to`:0.1 `␣Here`:0.1 `␣About`:0.1 `␣Now`:0.2 `To`:0.2
- 1 greeting (0.025): `␣The`:0.5 `Thank`:0.0 `␣Now`:0.2 `␣to`:0.1 `␣No`:0.2 `␣When`:0.2 `To`:0.3 `␣There`:0.1
- 2 greeting (0.025): `␣The`:0.5 `Thank`:0.0 `␣Now`:0.3 `␣to`:0.1 `␣About`:0.1 `␣No`:0.2 `To`:0.3 `␣When`:0.2
- 3 talk (0.029): `␣The`:0.6 `There`:0.0 `␣Now`:0.1 `␣to`:0.1 `␣When`:0.3 `␣No`:0.1 `␣There`:0.2 `To`:0.3
- 4 talk (0.026): `␣The`:0.7 `There`:0.0 `␣No`:0.2 `␣to`:0.1 `␣Here`:0.1 `␣When`:0.1 `To`:0.3 `␣There`:0.2
- 5 talk (0.026): `␣The`:0.5 `There`:0.1 `␣Now`:0.2 `␣to`:0.1 `␣When`:0.3 `␣No`:0.1 `␣There`:0.2 `To`:0.2
- 6 talk (0.026): `␣The`:0.6 `To`:0.3 `␣Now`:0.2 `␣to`:0.1 `␣When`:0.2 `␣Em`:0.1 `␣There`:0.1 `␣More`:0.0
- 7 talk (0.025): `␣The`:0.6 `Thanks`:0.1 `␣About`:0.1 `␣to`:0.1 `␣Now`:0.2 `␣There`:0.2 `␣When`:0.2 `To`:0.2
- 8 talk (0.024): `␣The`:0.5 `but`:0.0 `␣Now`:0.4 `␣to`:0.2 `Thank`:0.2 `␣About`:0.1 `␣When`:0.1 `the`:0.2
- 9 deflect (0.026): `␣When`:0.4 `␣To`:0.1 `the`:0.0 `␣No`:0.1 `␣Now`:0.2 `␣The`:0.4 `Thank`:0.3 `␣to`:0.1
- 10 deflect (0.024): `␣The`:0.6 `when`:0.0 `␣to`:0.2 `␣Now`:0.2 `␣When`:0.3 `Thank`:0.1 `the`:0.2 `␣More`:0.1
- 11 deflect (0.028): `␣The`:0.6 `When`:0.3 `␣No`:0.2 `␣to`:0.1 `␣Here`:0.1 `␣When`:0.2 `␣There`:0.1 `␣Now`:0.1

**91m-leaf L12** lens atoms at the final `:` of each room prompt (coefficient):  
- 0 greeting (0.074): `␣Yes`:5.8 `␣went`:2.0 `essages`:2.1 `␣there`:3.0 `␣However`:2.5 `␣how`:2.4 `␣introduces`:1.8 `␣Words`:1.9
- 1 greeting (0.052): `␣From`:3.0 `␣yes`:2.4 `␣everyone`:2.0 `␣Words`:2.4 `␣that`:2.5 `unrecognized`:2.2 `␣There`:2.6 `␣but`:1.8
- 2 greeting (0.058): `␣There`:4.9 `␣yes`:2.6 `␣Words`:1.8 `␣because`:1.8 `␣how`:2.5 `␣Only`:2.3 `␣acknowledged`:1.5 `␣Depression`:1.5
- 3 talk (0.079): `␣Yes`:6.0 `␣there`:4.1 `typography`:2.5 `␣Only`:2.7 `␣however`:2.0 `␣points`:1.8 `␣Accepted`:2.1 `␣It`:1.9
- 4 talk (0.055): `␣The`:4.7 `␣consisted`:2.5 `␣yes`:2.2 `␣Words`:2.7 `␣because`:1.5 `antly`:1.7 `␣from`:1.8 `␣There`:2.5
- 5 talk (0.070): `␣Yes`:5.4 `␣there`:4.1 `␣Only`:3.4 `inating`:1.7 `␣whether`:1.9 `␣Accepted`:2.1 `␣wants`:1.3 `␣We`:1.7
- 6 talk (0.064): `␣Because`:3.2 `␣yes`:3.7 `␣however`:2.5 `␣That`:3.7 `␣choice`:2.2 `␣does`:1.7 `istically`:1.6 `␣It`:2.6
- 7 talk (0.061): `␣There`:6.2 `␣whether`:1.3 `␣hello`:2.4 `␣Answer`:3.0 `␣but`:2.5 `␣that`:2.7 `␣Accepted`:2.1 `␣wants`:1.3
- 8 talk (0.068): `␣There`:5.7 `␣how`:2.5 `␣Accepted`:2.8 `␣but`:2.5 `␣points`:2.1 `␣hello`:2.6 `␣Answer`:2.7 `␣that`:1.8
- 9 deflect (0.063): `␣Yes`:3.4 `␣describes`:2.4 `␣There`:4.4 `␣that`:2.1 `␣placeholder`:2.1 `␣but`:2.0 `␣Accepted`:2.7 `␣how`:1.6
- 10 deflect (0.060): `␣describes`:2.6 `␣Yes`:3.6 `␣how`:2.7 `typography`:3.2 `␣but`:2.1 `␣there`:2.8 `␣Assume`:2.6 `␣points`:1.9
- 11 deflect (0.060): `␣Yes`:4.1 `␣there`:3.4 `typography`:2.9 `␣However`:2.6 `␣points`:1.9 `␣how`:1.6 `␣The`:2.7 `␣hello`:1.8

**91m-leaf L8** lens atoms at the final `:` of each room prompt (coefficient):  
- 0 greeting (0.048): `␣Lo`:0.6 `␣deny`:0.6 `␣There`:0.3 `␣physical`:0.4 `␣And`:0.7 `␣immediately`:0.4 `␣We`:0.9 `␣referring`:0.5
- 1 greeting (0.052): `␣Lo`:0.2 `␣immediately`:0.8 `␣Tell`:0.5 `␣We`:1.2 `␣patient`:0.7 `␣also`:0.7 `␣Physical`:0.4 `␣Yes`:0.5
- 2 greeting (0.049): `␣Lo`:0.0 `␣immediately`:0.8 `␣Physical`:0.5 `␣We`:1.1 `␣patient`:0.5 `␣also`:0.5 `␣Yes`:0.6 `␣Med`:0.6
- 3 talk (0.048): `␣We`:1.3 `␣immediately`:0.8 `␣Yes`:0.8 `␣physical`:0.4 `␣Nam`:0.4 `␣throughout`:0.6 `␣Because`:0.4 `␣literally`:0.3
- 4 talk (0.051): `␣Lo`:0.2 `␣immediately`:0.9 `␣There`:0.3 `␣Physical`:0.6 `␣We`:1.3 `␣also`:0.6 `␣patient`:0.5 `␣Yes`:0.6
- 5 talk (0.049): `␣Lo`:0.2 `␣immediately`:1.1 `␣There`:0.2 `␣Physical`:0.5 `␣We`:1.2 `␣Yes`:0.8 `␣act`:0.3 `␣throughout`:0.4
- 6 talk (0.041): `␣Lo`:0.0 `␣immediately`:0.7 `␣Yes`:0.7 `␣We`:1.2 `␣patient`:0.7 `␣also`:0.5 `␣Physical`:0.4 `␣Tell`:0.4
- 7 talk (0.046): `␣Lo`:0.3 `␣immediately`:0.8 `␣There`:0.5 `␣physical`:0.4 `␣Yes`:0.7 `␣We`:1.2 `␣also`:0.5 `␣patient`:0.5
- 8 talk (0.047): `␣Lo`:0.1 `␣immediately`:0.9 `␣Tell`:0.6 `␣We`:1.3 `␣physical`:0.5 `␣Yes`:0.6 `␣therefore`:0.4 `␣patient`:0.4
- 9 deflect (0.043): `␣Lo`:0.2 `␣immediately`:0.7 `␣Tell`:0.7 `␣Yes`:0.7 `␣physical`:0.4 `␣We`:1.1 `␣also`:0.5 `␣patient`:0.6
- 10 deflect (0.038): `␣Lo`:0.3 `␣immediately`:1.0 `␣Tell`:0.7 `␣man`:0.4 `␣Yes`:0.6 `␣also`:0.5 `␣Physical`:0.4 `␣We`:0.5
- 11 deflect (0.044): `␣Lo`:0.2 `␣immediately`:0.6 `␣Yes`:0.8 `␣We`:1.4 `␣patient`:0.7 `␣also`:0.6 `␣Physical`:0.4 `␣ask`:0.3

**91m-leaf L16** lens atoms at the final `:` of each room prompt (coefficient):  
- 0 greeting (0.108): `␣Yes`:11.1 `␣There`:9.5 `␣slowly`:2.4 `␣why`:3.3 `␣The`:7.5 `␣hello`:3.4 `␣didn`:3.3 `typography`:2.5
- 1 greeting (0.101): `␣The`:9.5 `␣yes`:5.9 `␣You`:7.4 `␣who`:5.2 `␣Because`:7.8 `␣referring`:3.7 `␣We`:5.1 `␣there`:2.7
- 2 greeting (0.106): `␣There`:11.1 `␣Yes`:8.8 `␣Thank`:5.0 `␣slowly`:3.8 `␣The`:5.5 `␣because`:3.9 `␣We`:3.6 `␣Reading`:2.5
- 3 talk (0.138): `␣They`:12.4 `␣Yes`:12.2 `␣Because`:7.7 `␣there`:5.2 `␣slowly`:4.6 `␣The`:6.3 `␣Remember`:3.7 `␣speaking`:2.4
- 4 talk (0.120): `␣The`:13.6 `␣reading`:8.3 `␣Because`:9.2 `␣yesterday`:3.8 `␣Well`:5.5 `␣there`:5.1 `␣Only`:4.2 `␣Accepted`:2.9
- 5 talk (0.112): `␣There`:9.9 `␣Yes`:11.3 `␣slowly`:4.5 `␣We`:5.6 `␣listening`:4.7 `␣Only`:4.6 `␣The`:5.3 `␣stay`:2.4
- 6 talk (0.084): `␣Because`:8.3 `␣yes`:9.7 `␣It`:6.3 `␣consciousness`:5.0 `␣There`:5.8 `perature`:2.1 `␣everything`:2.7 `␣That`:2.8
- 7 talk (0.109): `␣Because`:11.4 `␣The`:8.7 `␣yes`:7.6 `␣there`:4.7 `␣Nothing`:3.9 `␣They`:3.8 `typography`:3.1 `␣It`:4.1
- 8 talk (0.111): `␣That`:11.0 `␣yes`:8.4 `␣The`:6.6 `␣There`:6.3 `␣slowly`:3.2 `␣Thank`:3.1 `␣Because`:4.3 `␣it`:2.7
- 9 deflect (0.102): `␣Yes`:8.9 `␣The`:9.1 `␣please`:5.8 `␣doesn`:4.2 `typography`:4.3 `␣That`:7.8 `␣write`:4.3 `␣two`:2.9
- 10 deflect (0.080): `␣yes`:8.5 `␣The`:9.8 `␣pause`:4.9 `␣there`:5.5 `typography`:3.9 `␣starting`:4.0 `␣Then`:4.1 `␣sentence`:3.5
- 11 deflect (0.097): `␣The`:8.6 `␣yes`:9.4 `␣Because`:7.1 `␣wait`:3.7 `␣Let`:3.7 `␣There`:5.8 `␣doesn`:2.7 `␣Thank`:3.2

