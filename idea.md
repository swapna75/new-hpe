# Causal Alert Detection System Design

## Objective

Design a system for root cause detection in a microservices-based architecture, where a single event can generate multiple alerts across services. The goal is to identify the primary alert (root cause) using graph-based heuristics and continuously improve accuracy via feedback.

## Problem Statement

In distributed systems, alerts are often symptoms rather than the root causes. A CPU spike in one service might cause cascading failures across others. Traditional systems generate multiple alerts without connecting them causally, leading to alert fatigue and delayed response.

## Design Goals

- Identify the root cause of alert cascades
- Group causally linked alerts
- Route alerts to the right teams
- Learn and improve via human feedback
- Keep the system lightweight, modular, and feedback-driven

## High-Level Architecture

1. **Webhook Receiver**:

   - Receives raw alerts from Prometheus via webhook

2. **Graph Engine**:

   - Represents services and their dependencies
   - Builds causal alert graph from incoming alerts

3. **Alert Grouping & Root Cause Detector**:

   - Uses temporal(time) and topological heuristics to group alerts
   - Assigns root cause probabilities based on service dependency, start time, and historical data

4. **Feedback Engine**:

   - Interfaces with on-call teams to validate root cause predictions
   - Updates edge weights and false positive scores

5. **Alert Router**:

   - Sends grouped alerts to the appropriate team for investigation

---

## Alert Graph Representation

- **Nodes**: Represent alerts
- **Edges**: Represent potential causality (e.g. Service A -> Service B implies A's failure may cause B's)
- **Weights**: Represent confidence in causal relationships

### Fields Used from Alerts:

- `startsAt`: Temporal ordering
- `service`: Maps to node in service graph
- `severity`: Filtering & prioritization
- `summary`, `description`, `name`: Context

---

## Root Cause Detection Algorithm

1. **Initial Heuristic-Based Prediction**:

   - Use service dependency graph
   - Traverse upstream in the alert graph
   - Select root node based on highest influence (centrality, spread)

2. **Temporal Adjustment**:

   - Apply start time comparison within a sliding window
   - If downstream alert fires earlier, trust service graph more than time

3. **Probability Weights**:

   - Use edge weights to infer likeliness of causality
   - Update weights using Bayesian or exponential decay model

---

## Feedback Loop

After incident resolution, notify responsible team:

- Confirm root cause?
- Were all grouped alerts relevant?
- Any false positives?

Use this data to:

- Adjust edge weights
- Improve filtering logic
- Prune invalid connections

---

## Summary

This system allows for an incrementally learnable, low-overhead method to detect root causes from alert floods using graph heuristics and human feedback. It balances engineering practicality with future extensibility.

> MVP first. Learn from the teams. Let heuristics pave the way for better automation.
