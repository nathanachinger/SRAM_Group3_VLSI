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

| Cell | Description | Area | Owner |
|---|---|---|---|
| `inverter` | Inverter and other basic logic gates | Decoder | Person 1 |
| `row_decoder` | Row address decoder | Decoder | Person 1 |
| `col_decoder` | Column address decoder | Decoder | Person 1 |
| `bitcell` | 6T SRAM bitcell | SRAM | Person 2 |
| `array` *(planned)* | Bitcell array | SRAM | Person 2 |
| `precharge` *(planned)* | Bitline precharge circuit | SRAM | Person 2 |
| `sense_amp` | Sense amplifier | Peripheral | Person 3 |
| `write_driver` *(planned)* | Write circuitry | Peripheral | Person 3 |
| `sram_top` | Top-level schematic and combined layout | Integration | Person 4 |
| `sram_top_tb` *(planned)* | Top-level testbench | Integration | Person 4 |

Testbenches go in their own cell named `<block>_tb` (for example `sense_amp_tb`) and belong to the owner of that block. Planned cell names are suggestions; the owner can rename them before creating the cell.

## Pinout and Naming Convention
### Top-level pins

The complete array, `sram_top`, has 13 pins under 10 names.

| Pin | Dir | Width | Function |
| --- | --- | --- | --- |
| `CLK1` | in | 1 | Enables the tri-state buffers that pass the read and write commands (at least 10 MHz). Timing reference for all read and write measurements. |
| `CLK2` | in | 1 | Drives the precharge PMOS devices; both bit lines precharge to VDD. |
| `WR` | in | 1 | Write command, active-high. Never high together with `RD`. |
| `RD` | in | 1 | Read command, active-high. Never high together with `WR`. |
| `DATA_IN` | in | 1 | Bit to write to the addressed cell. |
| `DATA_OUT` | out | 1 | Bit read from the addressed cell (sense amplifier buffer output). |
| `RA<1:0>` | in | 2 | Row address. |
| `CA<2:0>` | in | 3 | Column address. Only 000 to 101 are valid. |
| `VDD` | inout | 1 | Supply. |
| `VSS` | inout | 1 | Ground. |

### Internal nets

These nets connect the blocks inside `sram_top`. Label them in the schematic so they show up by name in the waveform browser.

| Net | Width | Driven by | Meaning |
| --- | --- | --- | --- |
| `WL<3:0>` | 4 | Row decoder | Word lines, one per row. `WL<n>` selects row `Rn`. |
| `COL<5:0>` | 6 | Column decoder | Column selects, active-high. `COL<n>` selects column `Cn`. All low for addresses 110 and 111. |
| `BL<5:0>` | 6 | Precharge, cells, write driver | True bit lines, one per column. |
| `BLB<5:0>` | 6 | Precharge, cells, write driver | Complement bit lines. |
| `DB`, `DBB` | 1 each | Column pass gates | Shared data bus pair between the column pass gates and the write driver and sense amplifier. |
| `WR_EN` | 1 | Read/write control | `WR` after the `CLK1` tri-state buffer; enables the write driver. |
| `RD_EN` | 1 | Read/write control | `RD` after the `CLK1` tri-state buffer; enables the sense amplifier. |
| `SA_OUT` | 1 | Sense amplifier | Sense amplifier output before the output buffer. |
| `Q_R<r>_C<c>` | 24 nets | Cell | Storage node of the cell at row r, column c, for example `Q_R2_C4`. |
| `QB_R<r>_C<c>` | 24 nets | Cell | Complement storage node of the same cell. |

### Address map

The index in every net name equals the binary value of its address, so `RA = 10` and `CA = 011` select cell `Q_R2_C3`.

| `RA<1:0>` | Word line high | Row |
| --- | --- | --- |
| 00 | `WL<0>` | R0 |
| 01 | `WL<1>` | R1 |
| 10 | `WL<2>` | R2 |
| 11 | `WL<3>` | R3 |

| `CA<2:0>` | Column select high | Column |
| --- | --- | --- |
| 000 | `COL<0>` | C0 |
| 001 | `COL<1>` | C1 |
| 010 | `COL<2>` | C2 |
| 011 | `COL<3>` | C3 |
| 100 | `COL<4>` | C4 |
| 101 | `COL<5>` | C5 |
| 110 | none | unused |
| 111 | none | unused |

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

## Interfaces

Agree on these before building, and update this table when they change.

| Cell | Pins | Notes |
|---|---|---|
| `bitcell` | TBD | |
| `row_decoder` | TBD | |
| `col_decoder` | TBD | |
| `sense_amp` | TBD | |

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
