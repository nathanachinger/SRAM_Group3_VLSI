# SRAM_Group3_VLSI

Group 3 final project for EEE4310: a simple SRAM designed in Cadence Virtuoso.

This repository **is** the Virtuoso library. Each top-level folder is a cell, and each folder inside a cell is a view (schematic, symbol, layout, and so on).

## Roles

The work is split into four areas. Each person owns every cell in their area.

| Role | Area | Responsibilities | Owner |
|---|---|---|---|
| Person 1 | Decoder | Logic gates, row decoder, column decoder | [@Coppola-J](https://github.com/Coppola-J) |
| Person 2 | SRAM | Bitcell, bitcell array, precharge | [@rcorreafl](https://github.com/rcorreafl) |
| Person 3 | Peripheral | Sense amplifier, read/write circuitry | [@nathanachinger](https://github.com/nathanachinger) |
| Person 4 | Integration | Top-level schematic, top-level testbench, combined layout | [@MarianoRequejo609](https://github.com/MarianoRequejo609) |

## Blocks and owners

Only the owner of a cell commits changes to it. Everyone else opens it read-only.

| Cell | Description | Area | Owner | Views |
|---|---|---|---|---|
| `inverter` | Static CMOS inverter | Decoder | Person 1 | schematic, symbol, layout |
| `nand2` | 2-input NAND | Decoder | Person 1 | schematic, symbol, layout |
| `nand3` | 3-input NAND (column decoder) | Decoder | Person 1 | schematic, symbol, layout |
| `tri_inv` | Tri-state inverter (read/write control) | Decoder | Person 1 | schematic, symbol |
| `tgate` | Transmission gate (column pass gate) | Decoder | Person 1 | schematic, symbol |
| `row_decoder` | 2-to-4 row decoder, drives the word lines | Decoder | Person 1 | schematic, symbol, layout |
| `col_decoder` | 3-to-6 column decoder, drives true and complement column selects | Decoder | Person 1 | schematic, symbol, layout |
| `bitcell` | 6T SRAM bitcell (PD 240n, PG/PU 120n) | SRAM | Person 2 | schematic, symbol |
| `bitcell_tb` | Bitcell testbench | SRAM | Person 2 | schematic, sim state |
| `precharge` | Bit line precharge, one per column | SRAM | Person 2 | schematic, symbol |
| `sense_amp` | Sense amplifier with output inverter | Peripheral | Person 3 | schematic, symbol |
| `sense_amp_tb` | Sense amplifier testbench | Peripheral | Person 3 | schematic, sim state |
| `RW_ctrl` | Read/write control: clocks `WR`/`RD`, drives the write data bus and the sense amp enable | Peripheral | Person 3 | schematic, symbol |
| `RW_ctrl_tb` | Read/write control testbench | Peripheral | Person 3 | schematic, sim state |
| `sram_top` | Top-level schematic: 4×6 bitcell array plus all peripherals | Integration | Person 4 | schematic, symbol |
| `sram_top_tb` | Top-level testbench | Integration | Person 4 | schematic |
| `test_schematic` | Scratch cell for testing the Git setup | — | anyone | schematic |

There is no separate array cell: the 24 bitcells are placed directly in `sram_top`. Layouts for `inverter`, `nand2`, `nand3`, `row_decoder`, and `col_decoder` are complete and have passed DRC and LVS. Status of other blocks is maintained by their owners.

Testbenches go in their own cell named `<block>_tb` and belong to the owner of that block.

## Decoder verification status

As of November 20, 2026, the following cells have completed layouts with zero DRC violations and matching Assura LVS results:

| Cell | Layout | DRC | LVS |
|---|---|---|---|
| `inverter` | Complete | Clean | Match |
| `nand2` | Complete | Clean | Match |
| `nand3` | Complete | Clean | Match |
| `row_decoder` | Complete | Clean | Match |
| `col_decoder` | Complete | Clean | Match |

The completed cells have been committed to the decoder owner's branch. Merge them through the team's normal integration workflow.

Schematic transient simulations verified the row and column decoder address mappings below. The row decoder asserts one of four word lines. The column decoder asserts one of six column selects for addresses `000` through `101`; addresses `110` and `111` leave all `CS` outputs low. `CSB` outputs complement `CS`.

DRC checks physical design rules, and LVS confirms that the extracted layout circuit matches the schematic. Post-layout parasitic timing simulation and full SRAM integration verification are not covered by these passes. A transient word-line glitch was observed during the row-address transition `01` to `10`; integration must account for address settling before access.

`tri_inv` and `tgate` are not instantiated inside either decoder. They remain listed in the project cell inventory because the SRAM architecture references them for read/write control and column switching. Their required implementation and layout scope must be confirmed with the peripheral and integration owners; the decoder passes do not establish that these cells are complete or unnecessary.

## Pinout and Naming Convention

### Top-level pins

`sram_top` has 13 pins under 9 names. These match the `sram_top` symbol and `sram_top_tb`.

| Pin | Dir | Width | Function |
| --- | --- | --- | --- |
| `CLK1` | in | 1 | Enables the tri-state inverters in `RW_ctrl` that pass the read and write commands (at least 10 MHz). Timing reference for all read and write measurements. |
| `CLK2` | in | 1 | Drives the precharge PMOS devices; both bit lines precharge to VDD. |
| `WR` | in | 1 | Write command, active-high. Never high together with `RD`. |
| `RD` | in | 1 | Read command, active-high. Never high together with `WR`. |
| `DATA_IN` | in | 1 | Bit to write to the addressed cell. |
| `DATA_OUT` | out | 1 | Bit read from the addressed cell (sense amplifier output). |
| `A<4:0>` | in | 5 | Address. `A<4:3>` is the row address and `A<2:0>` is the column address. |
| `Vdd` | inout | 1 | Supply. |
| `Vss` | inout | 1 | Ground. |

### Block pins

Do not change these without telling the group (see Rules).

| Cell | Inputs | Outputs | Supply |
| --- | --- | --- | --- |
| `inverter` | `Vin` | `Vout` | `Vdd`, `Vss` |
| `nand2` | `IN1`, `IN2` | `OUT` | `Vdd`, `Vss` |
| `nand3` | `IN1`, `IN2`, `IN3` | `OUT` | `Vdd`, `Vss` |
| `tri_inv` | `IN`, `EN` | `OUT` | `Vdd`, `Vss` |
| `tgate` | `IN`, `SEL`, `SELB` | `OUT` | `Vdd`, `Vss` |
| `row_decoder` | `A<1:0>` | `WL<3:0>` | `Vdd`, `Vss` |
| `col_decoder` | `A<2:0>` | `CS<5:0>`, `CSB<5:0>` | `Vdd`, `Vss` |
| `bitcell` | `WL` | `BL`, `BLB` (inout) | `VDD`, `GND` |
| `precharge` | `CLK2` | `BL`, `BLB` (inout) | `Vdd` |
| `sense_amp` | `IN+`, `IN-`, `EN` | `OUT` | `Vdd`, `Vss` |
| `RW_ctrl` | `WR`, `RD`, `DATA_IN`, `CLK1` | `DB`, `DBB`, `REN` | `Vdd`, `Vss` |

### Internal nets

These nets connect the blocks inside `sram_top`. Label them in the schematic so they show up by name in the waveform browser.

| Net | Width | Driven by | Meaning |
| --- | --- | --- | --- |
| `WL<3:0>` | 4 | `row_decoder` | Word lines, one per row. `WL<n>` selects row `Rn`. |
| `CS<5:0>` | 6 | `col_decoder` | Column selects, active-high. `CS<n>` selects column `Cn`. All low for column addresses 110 and 111. |
| `CSB<5:0>` | 6 | `col_decoder` | Complement column selects, for the `tgate` `SELB` inputs. |
| `BL<5:0>` | 6 | `precharge`, bitcells | True bit lines, one per column. |
| `BLB<5:0>` | 6 | `precharge`, bitcells | Complement bit lines. |
| `DB`, `DBB` | 1 each | `RW_ctrl` | Write data and its complement, driven only while writing. |
| `SA_BL`, `SA_BLB` | 1 each | Column `tgate`s | Selected bit line pair, into the sense amplifier `IN+` / `IN-`. |
| `REN` | 1 | `RW_ctrl` | Read enable (`RD` gated by `CLK1`), drives the sense amplifier `EN`. |

Many other nets in `sram_top` still have default names (`net1`, `net2`, …). Label any net you probe. The storage-node labels planned earlier (`Q_R<r>_C<c>`, `QB_R<r>_C<c>`) are not in the schematic yet, and the bitcell's internal nodes are unnamed.

### Address map

The index in every net name equals the binary value of its address, so `A<4:3> = 10` and `A<2:0> = 011` select row R2, column C3.

| `A<4:3>` | Word line high | Row |
| --- | --- | --- |
| 00 | `WL<0>` | R0 |
| 01 | `WL<1>` | R1 |
| 10 | `WL<2>` | R2 |
| 11 | `WL<3>` | R3 |

| `A<2:0>` | Column select high | Column |
| --- | --- | --- |
| 000 | `CS<0>` | C0 |
| 001 | `CS<1>` | C1 |
| 010 | `CS<2>` | C2 |
| 011 | `CS<3>` | C3 |
| 100 | `CS<4>` | C4 |
| 101 | `CS<5>` | C5 |
| 110 | none | unused |
| 111 | none | unused |

### Naming rules

- **Cells:** lowercase `snake_case` (`sense_amp`, `row_decoder`). `RW_ctrl` is the one exception and is kept for now, since renaming a cell breaks every instance of it.
- **Testbenches:** `<cell>_tb`.
- **Buses:** `NAME<msb:0>`, with index 0 at the LSB.
- **Complements:** add a `B` suffix (`BLB`, `CSB`, `DBB`, `SELB`).
- **Gate pins:** `IN`/`IN1`…, `OUT`, `EN`, `SEL`/`SELB`.
- **Power:** `Vdd` and `Vss`. `bitcell` still uses `VDD`/`GND`; that works, but new cells should use `Vdd`/`Vss`.

## File structure

```
SRAM_Group3_VLSI/            <- Virtuoso library (repo root)
├── .gitignore               <- keeps lock files, backups, logs and sim results out of Git
├── .oalib                   <- library metadata (do not edit)
├── cdsinfo.tag              <- library metadata (do not edit)
├── data.dm                  <- library metadata (do not edit)
├── bitcell/                 <- cell
│   ├── schematic/           <- view
│   │   ├── sch.oa           <- the schematic database
│   │   ├── master.tag
│   │   ├── data.dm
│   │   └── thumbnail_128x128.png
│   ├── symbol/              <- added once the symbol is created
│   └── layout/              <- added once the layout is created
├── row_decoder/
├── col_decoder/
├── sense_amp/
├── sram_top/
└── test_schematic/
```

What each view is for:

- **schematic**: the transistor-level circuit.
- **symbol**: the box with pins that other schematics instantiate.
- **layout**: the physical design, checked against the schematic with LVS.
- **maestro**: saved simulation setup, kept in the testbench cell.

Files that are deliberately not tracked: lock files (`*.cdslck`), automatic backups (`*.oa-`), logs, and simulation results. Simulation output stays in your own `~/simulation` directory.

## First-time setup

1. **Add an SSH key to GitHub** (once per person, on the ECE server):

   ```bash
   ssh-keygen -t ed25519 -C "github"
   cat ~/.ssh/id_ed25519.pub
   ```

   Paste the printed line into GitHub → Settings → SSH and GPG keys → New SSH key. Test with `ssh -T git@github.com`.

2. **Clone the repo** into your own home folder:

   ```bash
   git clone git@github.com:nathanachinger/SRAM_Group3_VLSI.git
   ```

3. **Tell Virtuoso where the library is.** Add this line to the `cds.lib` in the directory you launch Virtuoso from, using the path to your own clone:

   ```
   DEFINE SRAM_Group3_VLSI /path/to/your/SRAM_Group3_VLSI
   ```

   The library name must be exactly `SRAM_Group3_VLSI` for everyone. Instances refer to cells by library name, so a different name breaks `sram_top`.

4. Restart Virtuoso. The library should appear in the Library Manager.

## Daily workflow

```bash
git pull                          # 1. get everyone's latest work before you start
```

2. In the Library Manager, choose View → Refresh.
3. Work on your own cell in Virtuoso.
4. **Check and Save, then close the cellview.** Never commit while a cellview is open.

```bash
git status                        # 5. see what changed
git add sense_amp sense_amp_tb    # 6. add only your own cells
git commit -m "Sense amp: schematic done, passes DC sim"
git push                          # 7. share it
```

## Rules

Virtuoso `.oa` files are binary, so Git cannot merge them. If two people change the same cell, one person's work has to be redone by hand. These rules prevent that.

1. **One owner per cell.** Do not commit changes to a cell you don't own. If you need a change, ask the owner.
2. **Add only your own cell folders.** Do not use `git add .`. Opening a cell in edit mode can modify its files even if you change nothing.
3. **Open other people's cells read-only.**
4. **If `git status` shows someone else's cell as modified, discard it:**

   ```bash
   git restore row_decoder
   ```

5. **Do not change pin names, pin order or symbols without telling the group.** `sram_top` depends on them.
6. **Pull before you start and push when you finish.** Small, frequent commits are better than one large one.
7. **Write commit messages that state the status,** for example `Row decoder: layout DRC clean, LVS pending`. The commit history is our progress log.

## Troubleshooting

**A cell opens read-only or says it is locked.** A crashed Virtuoso session left a stale lock. Make sure you have no Virtuoso session running, then delete the lock files in that view:

```bash
rm bitcell/schematic/*.cdslck*
```

**`git pull` reports a conflict on a `.oa` file.** Two people changed the same cell. Decide whose version to keep, then:

```bash
git checkout --theirs path/to/sch.oa    # keep the version from GitHub
# or
git checkout --ours path/to/sch.oa      # keep your version
git add path/to/sch.oa
git commit
```

The other person's changes must be redone by hand.

**`git push` is rejected.** Someone pushed before you. Run `git pull`, then `git push` again.

**A teammate's new cell doesn't show up in Virtuoso.** Run `git pull`, then View → Refresh in the Library Manager.

**Instances in `sram_top` show as missing or red boxes.** The cell or its symbol has not been pushed yet, or your `cds.lib` defines the library under a different name.
