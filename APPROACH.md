# AI Approach Justification

> **Decision:** Implement VideoTranscriber as an **orchestrated multi-step pipeline
> whose core transformation is Generative AI**. Do **not** build a fully autonomous
> Agentic AI system.

This document evaluates the three candidate approaches against the problem and justifies
the choice on **problem complexity, scalability, and maintainability**.

## The problem, distilled
The task is a **fixed, linear transformation**:

```
video → audio → transcript → structured content
```

Every run performs the same ordered steps. There is **no open-ended goal**, **no dynamic
decision tree**, and **no need for the model to choose its own tools at runtime**. The
only "intelligence-heavy" step is rewriting a raw transcript into well-structured prose —
a classic generative task.

## Option 1 — Generative AI (single-shot generation)
**What it is:** Prompt an LLM once to transform input into output.

- ✅ Perfect fit for the structuring step (transcript → headings + bullets + summary).
- ✅ Lowest latency, lowest cost, fully deterministic-enough (low temperature).
- ✅ Trivial to test, prompt-tune, and reason about.
- ⚠️ On its own it does not handle ingestion, audio extraction, chunking, or STT — those
  are deterministic engineering steps, not generative ones.

## Option 2 — Agentic AI (autonomous, self-directed agent)
**What it is:** An LLM-driven loop that plans, selects tools, and decides next actions
autonomously until a goal is met.

- ❌ **Overkill for a fixed pipeline.** There is no branching problem for an agent to
  reason about; the steps never change.
- ❌ Adds **nondeterminism, latency, and token cost** (planning/reflection loops).
- ❌ **Harder to test and maintain** — failures can occur inside opaque reasoning loops.
- ❌ Higher risk of hallucinated actions with no offsetting benefit here.

## Option 3 — AI Agents / multi-step orchestration
**What it is:** A coordinated set of steps (optionally specialized "agents"), each with a
narrow responsibility, wired by an orchestrator.

- ✅ Matches the natural shape of the workflow (extract → chunk → transcribe → structure).
- ✅ Each step is independently testable and replaceable.
- ✅ Deterministic control flow; the LLM is used precisely where it adds value.
- ⚠️ "Full multi-agent" frameworks would add ceremony without payoff at this scope.

## Chosen approach (hybrid, pragmatic)
**A deterministic multi-step orchestrator (`pipeline.py`) that invokes Generative AI for
the one step that needs it (`structuring.py`).** This combines the best of Options 1 and
3 while deliberately avoiding the cost of Option 2.

| Criterion | Why this approach wins |
|-----------|------------------------|
| **Complexity** | The problem is linear and well-defined; an autonomous agent would add complexity the problem doesn't have. |
| **Scalability** | Steps are isolated → easy to parallelize chunk transcription, swap STT/chat models, or batch many videos. |
| **Maintainability** | Deterministic flow + a single prompt seam = predictable, debuggable, and easy to unit-test. |
| **Cost & latency** | No agent planning/reflection loops; one generative call per video. |
| **Accuracy/control** | Low-temperature, instruction-bounded generation reduces hallucination and enforces output structure. |

## Designed for future growth
The generative step is isolated behind `structuring.py`. If requirements later demand
genuine autonomy — e.g., retrieval-augmented fact-checking, multi-document synthesis,
tool selection, or quality self-critique loops — that single module can be upgraded to an
**Agentic** implementation (e.g., Azure AI Foundry Agent Service / Agent Framework)
**without changing the rest of the pipeline.** We adopt agentic capability only when a
real decision-making problem justifies it.

## Summary
- **Generative AI** is the right tool for the transformation → used at the core.
- **Multi-step orchestration** is the right shape for the workflow → used as the skeleton.
- **Full Agentic AI** is unjustified at this scope → deliberately avoided, but the design
  leaves a clean upgrade path.
