# Chapter 25. Distributed Systems for AI

> "A large training run is a distributed system in which every node must stay in lockstep, and every node is failing."

## What you will learn

- Why training large AI models is a distributed-systems problem, and how it differs from the systems in earlier chapters.
- The forms of parallelism: data, tensor, pipeline, sequence and expert parallelism, and how they combine.
- Collective communication: all-reduce and its bandwidth-optimal ring algorithm, with the cost formula.
- Interconnects and topology, and why they shape everything.
- Fault tolerance at scale: failure rates, checkpointing, stragglers and silent data corruption.
- Serving models: batching, KV caches, prefill and decode, routing and autoscaling.

This chapter is *as of October 2026*. Hardware, model sizes and software frameworks change quickly; the distributed-systems principles underneath change slowly.

---

## 25.1 A different kind of distributed system

The systems in earlier chapters mostly serve many independent requests, and they tolerate failures by letting some nodes carry on while others fail. Training a large neural network is different:

- **Tight coupling.** Thousands of accelerators (GPUs or TPUs) perform one computation together, exchanging data many times per second. Every step waits for the slowest participant.
- **Synchrony is the norm.** Most large training uses synchronous steps: everyone computes, everyone communicates, everyone updates. A single slow or failed node stalls the whole job.
- **Failure is constant.** With tens of thousands of components, something fails every few hours.
- **Bandwidth dominates.** The network's job is moving huge tensors between accelerators, at hundreds of gigabytes per second per device, with latency in microseconds.

The workload is closer to a supercomputer job than to a web service, but the problems (partial failure, stragglers, consistency of shared state, checkpointing, scheduling) are the ones this book has studied.

## 25.2 Training in one paragraph

A neural network is a function with billions of **parameters** (weights). Training repeats a **step**: take a **batch** of examples, compute the model's outputs (the **forward pass**), measure the error, compute the **gradient** of the error with respect to every parameter (the **backward pass**), and update the parameters a little in the direction that reduces the error (the **optimiser step**, commonly with the Adam optimiser, which keeps two extra numbers per parameter). A large language model in 2025–2026 may have hundreds of billions to over a trillion parameters and train on tens of trillions of tokens, over weeks, on 10,000–100,000 accelerators.

## 25.3 Forms of parallelism

No single accelerator can hold a large model's parameters, gradients and optimiser state, or finish training in reasonable time. The work is split in several ways at once.

| Parallelism | What is split | Communication | Notes |
|---|---|---|---|
| **Data parallelism** (DP) | The batch: each replica holds a full model and processes different examples | All-reduce of gradients each step | Simplest; limited by memory per device |
| **Sharded data parallelism** (ZeRO, FSDP) | Optimiser state, gradients and parameters sharded across data-parallel ranks | All-gather parameters before use; reduce-scatter gradients | Removes memory redundancy of plain DP (Rajbhandari and colleagues, ZeRO, 2020) |
| **Tensor parallelism** (TP) | Individual matrix multiplications split across devices | All-reduce or all-gather within each layer, many times per step | Needs very fast links; usually within one server (Megatron-LM, Shoeybi and colleagues, 2019) |
| **Pipeline parallelism** (PP) | Layers: different devices hold different layers | Activations passed between stages | "Bubbles" of idle time, reduced by micro-batching (GPipe, PipeDream) |
| **Sequence / context parallelism** | Long input sequences split across devices | Exchange of attention data (e.g. ring attention) | For very long contexts |
| **Expert parallelism** (EP) | In mixture-of-experts models, different experts on different devices | All-to-all to route tokens to experts | Load balance across experts matters (Chapter 18 ideas apply) |

Large jobs combine them ("3D" or "4D/5D parallelism"): for example, tensor parallelism within an 8-GPU server, pipeline parallelism across a few servers, and data parallelism (sharded) across hundreds of such groups. The mapping is chosen so that the most communication-intensive parallelism runs over the fastest links.

## 25.4 Collective communication

Distributed training uses **collective operations**, in which a group of processes communicate in a structured pattern:

- **Broadcast:** one process sends the same data to all.
- **Reduce:** combine (for example, sum) values from all processes onto one.
- **All-reduce:** combine values from all processes and give every process the result. This is how data-parallel replicas average their gradients.
- **All-gather:** every process contributes a piece; every process ends with all pieces.
- **Reduce-scatter:** combine, and give each process one slice of the result.
- **All-to-all:** every process sends a distinct piece to every other process.

Libraries such as NVIDIA's **NCCL**, AMD's **RCCL** and the collective layers of JAX/XLA implement these over the available interconnects, choosing algorithms (rings, trees, and hierarchical combinations) by message size and topology.

### ◆ Formal: the ring all-reduce

Suppose N processes each hold a vector of size D, and all want the element-wise sum. Arrange them in a logical ring and split each vector into N chunks of size D/N.

1. **Reduce-scatter phase (N − 1 steps):** in each step, every process sends one chunk to its successor and adds the chunk it receives from its predecessor to its own copy. After N − 1 steps, each process holds the complete sum for one chunk.
2. **All-gather phase (N − 1 steps):** each process passes its completed chunk around the ring, so after N − 1 more steps every process has every summed chunk.

Each process sends (and receives) 2(N − 1) chunks of size D/N, a total of

```
2 (N − 1) / N × D   ≈   2D   for large N
```

That's **independent of N** (asymptotically), and within a factor of two of the minimum possible (each process must at least receive D(N − 1)/N data to learn the others' contributions). This bandwidth optimality, popularised for deep learning by Baidu (2017) and Uber's Horovod (Sergeev and Del Balso, 2018), is why data parallelism scales: adding replicas doesn't increase per-replica communication volume. The price is latency: 2(N − 1) sequential steps, which is why large clusters use **hierarchical** and **tree** algorithms that combine fast intra-server reduction with fewer inter-server steps.

Example: a 70-billion-parameter model with gradients in 16-bit precision (2 bytes) has D = 140 GB of gradients. A ring all-reduce sends about 2 × 140 = 280 GB per replica per step. At an effective 400 Gbit/s (50 GB/s) per replica, that's about 5.6 seconds, which is why gradients are sharded (ZeRO), communication is overlapped with the backward pass, and model parallelism keeps some communication on much faster intra-server links.

## 25.5 Interconnects and topology

| Link | Scope | Approximate bandwidth per device *(order of magnitude, 2025–2026)* |
|---|---|---|
| **NVLink / NVSwitch** (NVIDIA), similar fabrics from other vendors | Within a server or rack-scale domain (e.g. 72 GPUs in an NVL72 rack) | ~1–2 TB/s |
| **InfiniBand** or **RDMA over Converged Ethernet (RoCE)** | Between servers | ~400–800 Gbit/s per NIC, often one NIC per GPU |
| **Data-centre Ethernet** (TCP) | General traffic, storage | Lower; higher latency |

**RDMA** (remote direct memory access) lets a NIC read and write another machine's memory directly, bypassing the operating system, for microsecond latency. **GPUDirect RDMA** lets NICs access GPU memory directly. Networks for training are typically built as **non-blocking fat trees** or **rail-optimised** topologies, so collective traffic doesn't contend; congestion control and load balancing across paths (Chapter 18 ideas at the packet level) become critical at scale. The industry **Ultra Ethernet Consortium** published its 1.0 specification in 2025 to adapt Ethernet for these workloads.

Topology awareness runs through the whole stack: the scheduler places a job's ranks so that tensor-parallel groups share fast links, and collective libraries choose algorithms that match the physical topology.

## 25.6 Failures at scale

Meta's paper on Llama 3 (2024) gives a rare public view: during a 54-day snapshot of pre-training on 16,384 H100 GPUs, there were 466 job interruptions, 419 of them unexpected, about 78% of which were attributed to confirmed or suspected hardware problems (GPU failures and GPU memory errors were the largest categories). That's roughly one unexpected interruption every three hours. Despite this, Meta reported over 90% effective training time, thanks to automation.

### Checkpointing

Synchronous training can't simply continue when a node dies, so jobs **checkpoint**: periodically save all parameters and optimiser state to durable storage, and restart from the last checkpoint after a failure. The trade-off (Young, 1974; Daly, 2006) is between checkpoint overhead and lost work. A classic approximation for the optimal interval is

```
T_opt ≈ √(2 × C × M)
```

where C is the time to write a checkpoint and M is the mean time between failures. With C = 1 minute and M = 3 hours (180 minutes), T_opt ≈ √(360) ≈ 19 minutes. Faster checkpointing (asynchronous writes, in-memory checkpoints replicated to peers, sharded writes from every rank in parallel) shortens C and allows more frequent checkpoints, cutting lost work.

### Detection and recovery

- **Health checks** before and during jobs (GPU diagnostics, NCCL tests, ECC error counters) exclude bad nodes.
- **Watchdogs** detect hangs: a collective that never completes because one rank is stuck.
- **Hot spares** replace failed nodes quickly, so restarts don't wait for repairs.
- **Elastic training** can continue with fewer data-parallel replicas, at some cost to reproducibility.

### Stragglers

Every synchronous step waits for the slowest rank (the tail-at-scale problem of Chapter 7 §7.7, in its most extreme form). Causes include thermal throttling, a degraded link, a noisy neighbour, or a slow storage read. Large training teams monitor per-rank step times and remove persistent stragglers.

### Silent data corruption

At this scale, **silent data corruption** (a component computing a wrong result without reporting an error, Chapter 13 §13.1) becomes a practical concern: a single bad GPU or CPU can corrupt gradients, which then spread to every replica through all-reduce. Mitigations include monitoring for loss spikes and numerical anomalies, periodic redundant computation and comparison, and fleet-wide screening tests.

## 25.7 Serving models

**Inference** (running a trained model to answer requests) is a more conventional distributed service, with distinctive twists.

### Prefill and decode

Generating text with a large language model has two phases:

- **Prefill:** process the whole prompt in parallel to compute the model's internal state for every prompt token. Compute-bound.
- **Decode:** generate output tokens one at a time, each depending on all previous tokens. Memory-bandwidth-bound, because each step reads all the weights to produce one token per sequence.

To avoid recomputing attention over all previous tokens at every step, servers keep a **KV cache** (the attention keys and values for every token so far) in accelerator memory. KV caches are large (gigabytes for long contexts) and dominate memory planning.

### Batching

Because decode reads all the weights per step regardless of how many sequences are in the batch, batching many requests together raises throughput dramatically. **Continuous batching** (Yu and colleagues, "Orca", OSDI 2022) adds and removes requests from the batch at every step rather than waiting for a whole batch to finish. **PagedAttention** (Kwon and colleagues, vLLM, SOSP 2023) manages the KV cache in fixed-size blocks, like virtual-memory pages, reducing fragmentation so more requests fit in memory. These ideas are standard in serving engines such as vLLM, SGLang and TensorRT-LLM.

### Distributed serving

- **Model parallelism for inference:** large models are split with tensor (and sometimes pipeline or expert) parallelism across several accelerators.
- **Disaggregated prefill and decode** (for example DistServe, Zhong and colleagues, OSDI 2024): run the two phases on different pools of machines, sized independently, transferring the KV cache between them over fast links.
- **Prefix caching and cache-aware routing:** requests that share a prefix (a long system prompt, a document) can reuse its KV cache; routers send such requests to replicas that already hold the prefix, an application of consistent hashing and affinity routing (Chapters 7 and 18). Providers expose this to customers as **prompt caching** with lower prices for cached input.
- **Speculative decoding:** a small "draft" model proposes several tokens; the large model verifies them in one step, accepting the matching ones.
- **Autoscaling and load shedding:** accelerators are scarce and slow to start (loading hundreds of gigabytes of weights takes time), so capacity can't be added instantly. Admission control, priority queues and graceful degradation (Chapter 17) matter more than usual.

## 25.8 The principles, revisited

| Book principle | Where it appears in AI infrastructure |
|---|---|
| Partial failure and failure detection (Ch. 2) | Node failures every few hours; watchdogs; health checks |
| Consistent snapshots (Ch. 16) | Checkpoints of a synchronously updated model |
| Tail latency amplification (Ch. 7) | Stragglers stall every synchronous step |
| Partitioning (Ch. 7) | Sharding parameters, optimiser state and experts |
| Load balancing (Ch. 18) | Expert routing; request routing; network path balancing |
| Caching (Ch. 18) | KV caches; prefix and prompt caching |
| Overload and admission control (Ch. 17) | Scarce accelerators; long start-up times |
| Silent corruption (Ch. 13) | Bad hardware poisoning gradients |
| Testing and observability (Ch. 22, 23) | Per-rank metrics; numerical anomaly detection; pre-flight tests |

---

## Summary

- Training large models is a tightly coupled, synchronous distributed computation over thousands of accelerators, where bandwidth dominates and failures are constant.
- Data, sharded data, tensor, pipeline, sequence and expert parallelism split the work; they're combined so the heaviest communication uses the fastest links.
- Collectives (all-reduce, all-gather, reduce-scatter, all-to-all) carry the communication. The ring all-reduce sends 2(N − 1)/N × D per process, almost independent of N, at the cost of 2(N − 1) steps.
- Interconnects (NVLink-class fabrics within racks, InfiniBand or RoCE between servers) and topology-aware placement shape performance.
- At 16,000 GPUs, Meta saw an unexpected interruption roughly every three hours. Checkpointing (optimal interval ≈ √(2CM)), health checks, hot spares, straggler removal and corruption detection keep jobs productive.
- Serving separates compute-bound prefill from memory-bound decode, keeps KV caches, batches continuously, pages KV memory, disaggregates phases, routes by prefix and sheds load.

## Exercises

See [`exercises/25-ai-infrastructure.md`](../exercises/25-ai-infrastructure.md).

## Further reading

- Mohammad Shoeybi et al., "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism" (2019); Deepak Narayanan et al., "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", SC (2021).
- Samyam Rajbhandari et al., "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", SC (2020).
- Alexander Sergeev and Mike Del Balso, "Horovod: fast and easy distributed deep learning in TensorFlow" (arXiv, 2018).
- Llama Team, AI @ Meta, "The Llama 3 Herd of Models" (arXiv, 2024), section on infrastructure and reliability.
- Woosuk Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention", SOSP (2023).
- Yinmin Zhong et al., "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving", OSDI (2024).
- John W. Young, "A First Order Approximation to the Optimum Checkpoint Interval", *Communications of the ACM* (1974).
- Stas Bekman, *Machine Learning Engineering Open Book* (github.com/stas00/ml-engineering).
