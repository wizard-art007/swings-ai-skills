# .NET Race Condition Detector Simulator

A lightweight Python experimental project inspired by common concurrency hazards found in multi-threaded task queues and web service pipelines (such as lost updates and Time-Of-Check to Time-Of-Use / TOCTOU bugs).

## Idea & Background
In high-throughput systems (like modern .NET web applications or task queues), asynchronous execution and shared mutable state (e.g., EF Core DbContext or shared in-memory caches) frequently introduce subtle race conditions. This project models these hazards in a controlled Python multi-threaded environment and demonstrates how synchronization primitives mitigate them.

## Features
- **Lost Update Simulator**: Demonstrates non-atomic read-modify-write data loss and its synchronization fix using locks.
- **TOCTOU Simulator**: Simulates race conditions where checking state and subsequently acting upon it are separated by a time window.
- **Offline Pytest Suite**: Fully self-contained tests validating both vulnerable and safe execution paths.

## How to Run

1. Run tests via pytest:
   