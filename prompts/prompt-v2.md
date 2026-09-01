# Canonical Prompt — v2 (FROZEN 2026-09-01)

> Controlled paraphrase of `prompt-v1.md` for the prompt-sensitivity analysis (RQ6).
> Same hardware, same capability set, same investigation coverage, same A–K deliverables and the
> same responder-context header and response-format request (measurement scaffolding, held
> constant). **Changed:** the "senior AI infrastructure architect" role framing is replaced with
> a neutral "respond to this technical RFC" framing; section order is reshuffled (requirements
> and deliverables stated up front, investigation areas reworded and reordered); no sentence is
> shared with v1 where a reword was possible.
> Paste everything between the markers. Record `prompt_version: v2` in the capture front-matter.

=== PROMPT START ===

**Context for you, the responding model:**
- Today's date is **31 August 2026**. Research and cite the current state of the ecosystem as of this date.
- If you have web/tool access, use it and cite primary sources. If you do not, answer from knowledge and say so explicitly.
- This response will be compared side-by-side with responses from ~10 other AI systems, then synthesized into a research paper and used as a build specification. Be concrete, evidence-based, and decisive.
- At the very top of your response, state: your model name and version, your knowledge cutoff (if known), and whether web browsing/tools were enabled for this answer.

---

## Request

Treat this as a technical RFC. A single operator needs a reference design for a self-hosted,
continuously-running autonomous AI workstation, plus the evidence behind every choice. Investigate
the current tool and model landscape as it stands today, then commit to a specific build for the
exact machine described. Do not defer to whatever product or framework is most talked about;
weigh options on measured behaviour and choose.

## Target machine (fixed)

- Apple Mac mini, base **M6** silicon (not Pro or Max)
- 32 GB unified memory
- 512 GB internal SSD plus a 1 TB external SSD
- Left powered on around the clock
- Expected to keep making progress while the operator is asleep or out of the house

## Deliverables (label each clearly)

- **A.** Technology stack — a table of *Layer | Chosen technology | Alternatives considered | Rationale*
- **B.** Architecture diagram — every component and how they connect
- **C.** Resource plan — projected RAM and storage consumption
- **D.** Agent model — how to run 100+ logical agents without 100 concurrent model processes
- **E.** Model assignment — which model handles planning, coding, debugging, research, summarization, classification, and final synthesis
- **F.** Continuous-operation design — how overnight progress and automatic failure recovery work
- **G.** Remote-operation design — secure interaction from a phone while away from the machine
- **H.** Security design — broad machine capability without exposing personal secrets by default
- **I.** Installation procedure — ordered, runnable on the Mac
- **J.** Exclusion list — widely-used technologies that would be redundant, premature, or harmful in this build
- **K.** Scaling path — what changes at 64 / 96 / 128+ GB unified memory or with an added GPU or server

## Capabilities the system must have

It must run unattended for long stretches, resume through the night, and be operable remotely from
a phone or laptop. It must work against any project directory on the machine rather than a single
checked-out repository.

For software work it must read and understand existing codebases, plan changes, edit files, run
shell commands and test suites, debug failures, use Git including branches and worktrees, review
its own and others' code, and keep iterating until a task is finished or a stop condition fires.

For research it must search the web and academic literature, locate and compare papers, gather
and track evidence, check claims, surface contradictions, and assemble reports. It must handle
PDFs, datasets, Markdown, source code and other document types, run experiments, analyse the
output, and write documentation without being asked each time.

It must keep durable memory of projects, decisions, findings, experiments and prior work. It must
coordinate many specialised sub-agents and be able to hold 100+ logical agents while capping how
many model-inference processes run at once to what the hardware allows. It must create
task-specific agents on its own rather than requiring every agent to be hand-configured, and let
agents differ in role, tools, permissions, context and goals. It must pick a suitable model per
task automatically. It must keep processing local and private wherever that is practical, reach
out to the web only when research needs it, and operate the computer autonomously while keeping
firm boundaries around credentials, financial data, other sensitive personal information and
destructive system actions.

## What this is not

Not a chat assistant and not code completion. The operator wants an agentic environment that
cycles through: plan, delegate, execute, observe, verify, correct, document, continue — with
little human input. On waking it should read its queue, decide the next work, do it, judge the
result, queue follow-ups, and keep going until the objective or a predefined stop condition is
met.

## Areas to investigate (evidence expected for each)

1. **On-device inference.** Which local inference options are genuinely strong on a 32 GB
   unified-memory Apple Silicon box? Account for output quality, coding, reasoning, tool-use
   competence, context length, quantization, memory footprint, throughput, concurrency,
   Metal/Apple-Silicon optimisation, load/unload behaviour, running more than one model, and
   stability/maturity. Say which models to actually run. Do not just take the biggest model that
   fits — optimise for useful work per hour, not parameter count.
2. **Agent runtimes and harnesses.** Survey current runtimes offering autonomous loops, tool use,
   shell and filesystem and browser access, code execution, sandboxing, durable sessions,
   sub-agents and spawning, delegation, retries, state handling, long-running and background
   tasks, scheduling, observability, permissions and remote control. Decide: one existing
   harness, several complementary ones, or a custom orchestration layer over existing pieces.
3. **Many-agent design on small hardware.** Distinguish 100 real model instances, 100 logical
   agents, agent definitions, task queues, worker pools, dynamic sub-agents, sequential vs
   parallel execution, model routing, hierarchical vs swarm vs coordinator/worker topologies.
   Pick the design with the best useful throughput on 32 GB.
4. **Autonomous coding systems.** Compare on repository comprehension, shell execution, editing,
   test runs, debugging, Git and worktree handling, long-running tasks, self-iteration, code
   review, context management, local-model support and sandboxing. Choose the best fit here.
5. **Autonomous research systems.** Compare web search, source and literature discovery, PDF
   analysis, citation extraction, evidence tracking, claim checking, contradiction detection,
   synthesis and report writing. Specify the design that best prevents fabricated citations and
   unsupported claims.
6. **Durable memory.** Compare filesystem stores, SQLite, relational databases, vector stores,
   knowledge graphs, embeddings, hybrid and episodic and semantic memory, and per-project vs
   global scope. Say what to start with and what to add later; avoid infrastructure that is not
   yet needed.
7. **Machine control and isolation.** Compare the safest capable options for shell, filesystem,
   browser, GUI/computer-use, application and process control, alongside sandboxes, VMs,
   containers, dedicated OS users, permission systems, credential isolation and network
   isolation. The aim is maximum practical autonomy without default access to sensitive personal
   data.
8. **Running 24/7.** Cover macOS background services, launch agents and daemons, auto-restart,
   crash recovery, task persistence, queues, scheduled jobs, monitoring, logging, watchdogs,
   sleep prevention, remote reachability and network hardening. A crashed agent or a reboot must
   recover on its own.
9. **Remote reach.** Cover secure command execution, status dashboards, notifications, task
   submission, log access, approvals, an emergency stop, authentication and encrypted transport.
   Keep services off the open internet unless there is a reason.
10. **Storage split.** Across the 512 GB internal and 1 TB external SSD, place models, databases,
    embeddings, Git repositories, papers, datasets, logs, scratch agent workspaces, backups and
    caches — accounting for external-SSD throughput and durability.

## Resource budgeting

Work out roughly how the 32 GB should be divided across macOS, model weights, KV cache, context
windows, agent processes, databases, a browser and filesystem cache. State a target model size,
quantization and context length; how many large-model and small-model workers run at once;
whether swapping models is worth it; whether to hold more than one model resident; and the
expected bottlenecks. Give performance numbers only where a benchmark backs them.

## Cost posture

Favour free, open and local components where practical. Identify the fully-local/free parts, the
optional paid parts, the cloud APIs that are actually worth it, and the cases where cloud
inference is worth reaching for temporarily versus staying local. The system has to stay useful
with no mandatory cloud API.

## Security posture

Give a security model for autonomous running. The agent should be highly capable but not
implicitly trusted. Cover permissions, sandboxing, dedicated accounts, workspace isolation, Git
safeguards, secrets handling, network controls, destructive-command controls, human-approval
thresholds, an emergency kill switch, audit logs, and resource / time / token limits with
runaway protection. State precisely which operations run unattended and which need sign-off.

## Architecture and market comparison

Propose a concrete layered design — interface, supervisor, orchestrator, task queue, specialised
agents, model router, local inference, tools, durable memory — but treat that shape as a starting
hypothesis and change it if the evidence points elsewhere. For each major category, name: (1) best
overall, (2) best for this hardware, (3) best open-source, (4) best lightweight, (5) best
mature/stable, (6) best cutting-edge, (7) the actual pick. Include options the operator may not
know. When two are close, explain the trade-off and still choose one.

## Implementation phases

Lay out a phased roadmap: (1) minimal working system, (2) autonomous coding, (3) research agents,
(4) durable memory, (5) many-agent orchestration, (6) 24/7 operation, (7) remote access, (8)
advanced tuning. For each phase give exact technologies, install commands where they apply,
configuration, directory layout, how components talk to each other, how to test it, likely
failure modes, and how to roll back.

## Overriding instruction

Research before answering. Do not produce a generic answer from memory. Confirm current versions,
capabilities, hardware support and project health as of today. Decide on evidence and benchmarks,
not popularity. The output should be a practical, production-grade architecture for a personal
24/7 autonomous AI research lab running mainly on a 32 GB M6 Mac mini.

## Response format (for comparability across models)

Please structure your answer as:
1. Header line: model name + version, knowledge cutoff, browsing on/off
2. Short "decisions at a glance" table (your final picks per layer)
3. Numbered sections 1–10 matching the investigation areas above
4. Lettered deliverables A–K
5. A "Sources" list with URLs, marking each primary or secondary

=== PROMPT END ===
