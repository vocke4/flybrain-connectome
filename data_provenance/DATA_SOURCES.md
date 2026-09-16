# First-Hand Data Sources

The two connectomes analyzed in this study are public, versioned releases of the
original reconstruction projects. They are **not redistributed** in this package
(≈1.4 GB); download them from the locations below and verify against the SHA-256
checksums recorded from the files used in the study.

## Female — BANC (Brain And Nerve Cord)

- **Organism:** adult female *Drosophila melanogaster*, whole CNS (brain + ventral nerve cord)
- **Project:** FlyWire / Harvard Medical School (GridTape TEM)
- **Publication:** Bates et al., "Distributed control circuits across a brain-and-cord connectome" (*Nature*, 2025)
- **Access:** <https://flywire.ai/banc_access> — data access portal
- **Repository/tools:** <https://github.com/htem/BANC-project> and <https://github.com/jasper-tms/the-BANC-fly-connectome>

Files used (place in `data/female/`):

| File | Role | Size | SHA-256 |
|---|---|---|---|
| `banc_888_edgelist_simple_v3.feather` | Segment-to-segment synapse counts | 382 MB | `8c296e946f3c69a8c7222f30ad75fa8a98eeb189124fec6df829c9125f4be64b` |
| `banc_888_meta.feather` | Per-neuron metadata incl. neurotransmitter prediction/verification | 15 MB | `86ccf5df0c67419f8c5f43e93a7ed38d23a080e9f7fde26737290252f3780098` |

## Male — MaleCNS v1.0

- **Organism:** adult male *Drosophila melanogaster*, whole CNS
- **Project:** Janelia FlyEM Project Team + Drosophila Connectomics Group (Cambridge)
- **Publication:** Berg et al., "Sexual dimorphism in the complete connectome of the Drosophila male central nervous system" (*Cell*, 2026)
- **Download:** <https://male-cns.janelia.org/download/> (official table listing; the exact filenames below appear there)
- **Project site:** <https://male-cns.janelia.org/>

Files used (place in `data/male/`):

| File | Role | SHA-256 |
|---|---|---|
| `connectome-weights-male-cns-v1.0-minconf-0.5.feather` | Full connection graph (1.1 GB) | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` |
| `body-neurotransmitters-male-cns-v1.0.feather` | Consensus neurotransmitter per body | `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621` |
| `body-annotations-male-cns-v1.0-minconf-0.5.feather` | Cell annotations (sex typing, cell class) | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |

## Verification

```bash
shasum -a 256 data/female/*.feather data/male/*.feather
```

All five digests must match the table above. Any mismatch means a version drift —
check the source site for a re-versioned file before proceeding.

## Key structural descriptors used in the study

(derived by `normalize.py`; used as sanity anchors)

| Descriptor | Female (BANC) | Male (MaleCNS) |
|---|---|---|
| Neurons (CNS, sign-annotated) | 169,078 | 163,511 |
| Edges (sign-resolved) | 13,379,740 | 24,410,950 |
| Synapses (total count sum) | 41.5M | 117.5M |
| Mean synapses per edge | 3.10 | 4.81 |
| SD(log count) | 0.825 | 0.983 |
| E/I ratio (edges) | 75/25 | 80/20 |
| Dimorphic neurons | 3,803 | 3,900 (2.4% of cells) |