# Restore the KRAS archive

1. Download every asset from the [archive release](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31) into a new empty directory.
2. Verify each downloaded ZIP against its SHA-256 in the release asset manifest before extraction.
3. Extract each ZIP while preserving its relative paths. The package names identify the original source roots and avoid collisions between same-named files.
4. Review each `MANIFEST.json`. It lists every member, source-relative path, source SHA-256, published SHA-256, and any text-redaction transformations.
5. Byte-identical members can be restored to their source-relative paths. Redacted text members restore the directory layout but not original bytes; their unredacted source copies remain local and are deliberately not claimed as recoverable from the public archive.
6. Do not treat third-party models, weights, or caches as included. Obtain them from their original source under the applicable license and record the version before running project scripts.
7. Configure paths and dependencies for the local environment. Historical commands are records of what was run, not a guarantee that current dependencies or remote services will reproduce identical results.

Release assets are split below 512 MiB each. The archive was verified by downloading the public assets to a clean directory, checking ZIP integrity, comparing manifests, and hashing restored members.


Supplemental release: [archive-2026-10-31-batch2](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31-batch2). Download and verify this asset in addition to the original archive when recovering the follow-on Boltz2 screen.

## Asp6 follow-on archive

Download [archive-2026-10-31-batch3](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31-batch3) and extract `KRAS-Asp6-followon-screen-01.zip` at the archive root. The asset manifest records source and published hashes for all files. The stopped duplicate invocation is kept under its own prediction and log paths and is excluded from scientific metrics.
