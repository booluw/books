# Consistent hashing (Chapter 7)

## The problem

A cache or a partitioned database spreads its keys across N servers. Each client needs a rule that maps a key to a server without asking anyone. The textbook rule, `hash(key) mod N`, spreads keys evenly, but it falls apart when N changes. Grow from 10 servers to 11 and about 10 keys in 11 map somewhere new: a cache loses almost every entry at once and the database behind it is flooded, or a database copies almost all of its data over the network.

**Consistent hashing** keeps placement stable as servers come and go: adding the 11th server moves only the keys it should own, about 1/11 of them.

## Terms

- **Partitioning** (or sharding): splitting a dataset so each server holds part of it.
- **Hash ring:** the range of a hash function (here 0 to 2⁶⁴ − 1) bent into a circle. Servers and keys are hashed onto it; a key belongs to the first server point clockwise from it.
- **Virtual node** (vnode): one of several points a physical server occupies on the ring. More points mean each server owns many small arcs instead of one large one, which evens out load.
- **Load imbalance:** the most-loaded server's load divided by the mean. 1.0 is perfect. Capacity is planned for the most-loaded server, so imbalance is wasted hardware.
- **Rendezvous hashing** (highest random weight, HRW): every server scores the key with `hash(server, key)`; the highest score wins. No ring, the same stability as consistent hashing, and good balance without virtual nodes, at the cost of N hashes per lookup.
- **Stable hash:** a hash that gives the same answer on every machine and every run. Python's `hash()` for strings is randomised per process, so we use `hashlib.sha256`.

## How it works

`hashring.py`:

| Name | What it does |
|---|---|
| `stable_hash(text)` | First 64 bits of SHA-256 |
| `ModNHashing(nodes)` | The naive baseline |
| `HashRing(nodes, vnodes=100)` | Sorted ring positions with `bisect`; `lookup`, `add_node`, `remove_node`, and `ownership()` (exact fraction of the ring each node owns) |
| `RendezvousHashing(nodes)` | `lookup` takes the node with the highest `stable_hash(f"{node}|{key}")` |
| `assignment`, `fraction_moved`, `load_imbalance`, `movement_on_add` | Measurement helpers |

All three schemes share `lookup(key)`, `add_node(node)` and `remove_node(node)`, so the measurement code treats them alike.

**Why only 1/(N+1) of keys move.** On the ring, a new node's points each claim the arc between the previous point and themselves. Keys outside those arcs see the same successor as before, so they stay put; keys inside move to the new node and nowhere else. With rendezvous hashing, a key moves only if the new node's score beats the old winner's; with N+1 independent scores, that happens with probability 1/(N+1). With mod-N, a key stays only if `h mod N == h mod (N+1)`, which holds for about 1 key in N+1, so N/(N+1) of keys move.

## Run it

```bash
python3 hashring.py        # demo
python3 -m unittest -v     # 12 tests
```

Demo output (20,000 keys, 10 nodes growing to 11; ideal movement 1/11 = 9.1%):

| Scheme | Keys moved |
|---|---|
| mod-N hashing | 90.8% |
| Hash ring, 1 vnode per node | 6.0% |
| Hash ring, 100 vnodes per node | 9.6% |
| Rendezvous hashing | 9.3% |

With one vnode the new node happened to land on a short arc, so it took only 6% of the keys. That is not good news: it is the imbalance problem showing up in a different place.

Removing one of 10 nodes from a 100-vnode ring moves 10.8% of keys, exactly the share that node owned. No other key moves.

Load imbalance (max/mean), 10 nodes:

| Vnodes per node | Keys (20,000 sampled) | Exact ring share |
|---|---|---|
| 1 | 2.32 | 2.26 |
| 10 | 1.51 | 1.53 |
| 100 | 1.12 | 1.14 |
| 1000 | 1.05 | 1.03 |
| Rendezvous | 1.06 | n/a |

Averaged over 20 random clusters of 10 nodes, exact ring-share imbalance is about 2.9 with 1 vnode, 1.53 with 10, 1.18 with 100 and 1.05 with 1000. The spread falls roughly as 1/√(vnodes).

## Experiments to try

1. **Watch mod-N collapse.** Run `movement_on_add(ModNHashing, n, make_keys(20000))` for n = 2, 5, 10, 50, 100. Compare each result with n/(n+1).
2. **Find the vnode sweet spot.** Plot (or print) exact imbalance `max(ring.ownership().values()) * n` for vnodes = 1, 2, 4, …, 1024. Where do the gains stop paying for the memory and lookup cost?
3. **Use a bad hash.** Replace `stable_hash` with `lambda s: sum(map(ord, s))` and rerun the demo. Keys `key-1` … `key-20000` have very similar character sums; what happens to balance?
4. **Weighted nodes.** Give a node twice the capacity by giving it twice the vnodes (add a `weights` argument to `HashRing`). Check `ownership()` comes out near 2:1.
5. **Time the lookups.** Use `timeit` to compare `HashRing.lookup` (O(log V) with bisect) and `RendezvousHashing.lookup` (O(N)) at N = 10 and N = 1000.
6. **Remove a node with 1 vnode.** All its keys go to a single neighbour. With 100 vnodes they spread over all survivors. Count where node-3's keys go in each case.

## Limitations

- Keys are uniform and equally hot. Real workloads have hot keys that no hashing scheme can split; Chapter 7 covers splitting hot partitions and adding random suffixes.
- Nodes are equal in capacity unless you add weights (experiment 4).
- Only placement is shown. Real systems must also *move* the data, replicate to the next N distinct nodes on the ring (see `quorum-store/`), and agree on ring membership (see `gossip-membership/`).
- Other schemes, such as jump consistent hashing, Maglev hashing and consistent hashing with bounded loads, are not implemented here.
