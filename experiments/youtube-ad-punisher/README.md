# YouTube Ad Punisher (Experimental Python Core)

An experimental Python-based simulation and orchestration engine inspired by browser automation concepts for dealing with YouTube ads. Instead of traditional ad blocking, the "punisher" concept detects ad states and triggers a punitive page reload or state reset sequence.

## How It Works
1. **DOM / State Analyzer**: Inspects incoming webpage HTML or player state payloads for known ad markers (e.g., `ad-showing`, `ytp-ad-module`).
2. **Punishment Engine**: Decides whether to issue a reset (reload trigger) based on configurable thresholds (e.g., maximum allowable reload frequency to avoid infinite reload loops).
3. **Telemetry**: Tracks how many ads were "punished" versus skipped.

## How to Run
