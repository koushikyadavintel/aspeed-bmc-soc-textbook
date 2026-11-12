# Chapter 8 - Memory Model and Atomics

[Index](00_README.md) | Prev: [Ch 7](07_Hypervisor_AIA_IOMMU.md) | Next: [Ch 9 - ABI, Toolchain, Assembly](09_ABI_Toolchain_Assembly.md)

**Goals:** Understand what other harts and devices may observe, how `fence`, acquire/release, LR/SC and AMOs create ordering, how C11/C++11 atomics map to RISC-V, and how to reason with litmus tests.

> Status: **RVWMO** (the default model) and **Ztso** are **Ratified**. The C11 mapping below follows the ISA manual's appendix and the psABI atomics guidance; check the current "Atomics ABI" document for updates **[verify]** (newer `Zalasr` instructions may change recommended sequences).

---

## 8.1 Why memory models exist

Modern cores buffer stores, speculate loads, reorder, and use multiple caches. The **memory consistency model** specifies which results of multi-threaded programs are architecturally allowed. A weaker model gives hardware more freedom (better performance, lower cost) and gives software more responsibility (insert fences).

| Model | Reorderings allowed | Used by |
|-------|---------------------|---------|
| Sequential consistency (SC) | none | theoretical baseline |
| TSO | store -> later load only | x86, RISC-V with `Ztso` |
| **RVWMO** | most reorderings unless constrained by dependencies, fences, acquire/release | RISC-V default, similar in spirit to ARMv8/POWER (but multi-copy atomic) |

**Multi-copy atomicity:** RVWMO is *multi-copy atomic*: when a store becomes visible to any other hart, it becomes visible to all of them at the same time. This rules out the notorious POWER-style IRIW anomalies.

## 8.2 Vocabulary

| Term | Meaning |
|------|---------|
| **Program order** | The order in which a single hart executes memory instructions |
| **Global memory order** | A single total order of all memory operations from all harts and the effects of each (the model's abstraction of "what really happened") |
| **Preserved program order (PPO)** | The subset of program order that must be respected in the global memory order |
| **Syntactic dependency** | Dependency visible in register names (address, data, or control), not in values |
| **Coherence** | All accesses to a *single address* appear in some total order consistent with program order |
| **Reservation** | State created by `lr`, checked by `sc` |
| **Acquire / release** | One-way ordering annotations (`.aq`, `.rl`) |
| **RCsc / RCpc** | Release consistency flavors: *sequentially consistent* vs *processor consistent* synchronization operations |

## 8.3 RVWMO in one page

Execution is legal if there exists a **global memory order** (a total order over all memory operations) that satisfies three axioms:

1. **Load Value Axiom:** Each load returns the value written by the latest store to that byte that precedes it either in global memory order, or in program order *on the same hart* (store forwarding).
2. **Atomicity Axiom:** If a successful `sc` pairs with an `lr`, no other hart's store to the reserved bytes may intervene (in global memory order) between the `lr` and the `sc`. Likewise AMOs are indivisible.
3. **Progress Axiom:** No memory operation is delayed forever.

And two operations must appear in global memory order consistent with the **preserved program order**: roughly, `a` before `b` in program order is preserved if one of the following holds (the manual numbers these 13 rules):

**Overlapping-address rules**
- `b` is a store and `a`/`b` access overlapping bytes (same-address store ordering).
- `a`, `b` are loads reading overlapping bytes and return values from different stores (no intervening store to that byte in between) - keeps coherence of loads.
- `a` is an AMO/`sc`, `b` is a load that returns the value written by `a`.

**Explicit synchronization**
- A `fence` orders `a` before `b` (according to `pred`/`succ`).
- `a` has acquire; `b` has release; both are RCsc annotated and sequentially consistent with each other.
- `b` is a store-conditional and `a` is its paired load-reserved.

**Syntactic dependencies**
- `b` has a syntactic **address** dependency on `a`.
- `b` is a store with a syntactic **data** dependency on `a`.
- `b` is a store with a syntactic **control** dependency on `a` (loads are not ordered after a control-dependent branch, stores are).
- `b` is a load and a store `m` between them has an address/data dependency on `a` and `b` reads from `m` (pipeline forwarding preserved).
- `b` is a store and some instruction between has an address dependency on `a` (can't speculatively commit).

> Key practical consequences: **address and data dependencies order**; **control dependencies order only load -> store**; everything else needs a `fence` or acquire/release.

### What "syntactic" means

```asm
lw  a0, 0(s0)        # load pointer
lw  a1, 0(a0)        # address depends on a0 -> ordered after the first load (even with no fence)
```

But `xor a1, a0, a0; add t0, s1, a1; lw ...` still counts as a dependency even though the value is always 0: the dependency is determined by registers, not values. (Compilers may break dependencies via optimization, which is why `memory_order_consume` is deprecated.)

## 8.4 Fences

```
fence pred, succ
```

Operations in the **predecessor set** (`pred`) that precede the fence in program order are ordered before operations in the **successor set** (`succ`) that follow it. Sets are drawn from `i` (device input), `o` (device output), `r` (memory reads), `w` (memory writes).

| Fence | Typical use |
|-------|-------------|
| `fence rw, rw` | Full memory barrier |
| `fence r, rw` | **Acquire** barrier (after a load, before later accesses) |
| `fence rw, w` | **Release** barrier (before a store, after earlier accesses) |
| `fence w, w` | Store-store (`smp_wmb`) |
| `fence r, r` | Load-load (`smp_rmb`) |
| `fence w, r` | Store-load (the expensive one; needed even under TSO) |
| `fence.tso` | `fence rw, rw` minus store->load: orders load->load/store and store->store |
| `fence iorw, iorw` | Everything including I/O |
| `fence w, o` / `fence i, r` | MMIO write ordering (Linux `writel`/`readl` pattern) |

`fence.tso` is encoded as `fence` with `fm=1000`, `rw,rw`.

Hardware may implement `fence.tso` as a full `fence rw,rw` where it can't distinguish.

## 8.5 Acquire and release annotations

`.aq` and `.rl` bits exist on AMOs and `lr`/`sc`.

| Annotation | Guarantee |
|------------|-----------|
| `.aq` (acquire) | No later memory operation (in program order) can be observed to happen *before* this operation. |
| `.rl` (release) | All earlier memory operations are observed before this operation. |
| `.aqrl` | Both, and the operation is **sequentially consistent** with other `.aqrl` operations (RCsc). |

- Acquire is for *reading a lock/flag*; release is for *writing it* after finishing the critical section.
- A store alone with release uses a `fence rw,w` before it (in the base ISA); an `amoswap.w.rl x0, x0, (a0)` is a convenient atomic release store.
- `lr.aq` and `sc.rl` are the standard pair. Software should not set `rl` on an `lr` unless `aq` is also set, nor `aq` on an `sc` unless `rl` is also set.

## 8.6 Litmus tests

Written as `[hart0 | hart1]`, all initial values 0. "Allowed" means RVWMO permits the outcome.

### Message passing (MP)

```
Hart 0:                Hart 1:
  sw x, 1                lw r1, y
  sw y, 1                lw r2, x
```

Outcome `r1 = 1 and r2 = 0`: **allowed** without fences (stores may be reordered; loads may be reordered).

Fix: producer `fence w,w` between the stores, consumer `fence r,r` between the loads. Or use release/acquire: `fence rw,w` before `sw y` and `lw r1,y; fence r,rw`.

### Store buffering (SB)

```
Hart 0:                Hart 1:
  sw x, 1                sw y, 1
  lw r1, y               lw r2, x
```

`r1 = 0 and r2 = 0` **allowed** (even under TSO!). Fix: `fence w,r` (or `fence rw,rw`) between store and load on both harts. Required for Dekker/Peterson algorithms.

### Load buffering (LB)

```
Hart 0:                Hart 1:
  lw r1, x               lw r2, y
  sw y, 1                sw x, 1
```

`r1 = 1 and r2 = 1` **allowed** in RVWMO without dependencies. Forbidden if there's a data dependency from the load to the store (rule: store with data dep on load), or a `fence r,w`.

### IRIW (independent reads of independent writes)

Two writer harts write `x` and `y`; two reader harts read both in opposite orders. With `fence r,r` between each reader's loads, RVWMO **forbids** readers disagreeing on the order (multi-copy atomicity).

### Coherence (CoRR)

`lw r1,x; lw r2,x` on one hart while another writes `x=1`: cannot observe `r1=1, r2=0` (per-location coherence).

## 8.7 LR/SC details

```
lr.w   rd, (rs1)
sc.w   rd, rs2, (rs1)
```

- **Reservation set:** a contiguous naturally aligned region containing the `lr` address (profile `Za64rs`: at most 64 bytes; `Za128rs`: 128). Other harts' stores to *any byte in the set* can invalidate it.
- `sc` fails (rd != 0) if: the reservation was lost, `sc` address differs from the last `lr`, there is no preceding `lr`, a trap or context switch occurred (privileged software should execute an `sc` to a dummy address on context switch), or implementation-chosen spurious reasons (e.g., interrupt).
- An `sc` always invalidates the hart's reservation (success or fail).
- **Eventual success** needs a *constrained LR/SC loop*: <= 16 instructions, only base `I` instructions that are not loads/stores/`fence`/system/`jalr`, no backward branches other than the retry, `sc` to the same address and size as `lr`, and only in memory with the `RsrvEventual` PMA (`Ziccrse`). Outside this, the standard guarantees nothing; livelock is possible.
- Do **not** put loads/stores between `lr` and `sc` (they may kill the reservation on some implementations).

### Atomic increment variants

```asm
amoadd.w     a1, a2, (a0)          # simplest: one AMO
```

```asm
# Compare-and-swap (32-bit) with LR/SC: if (*a0 == a1) *a0 = a2; return old in a3
1:  lr.w     a3, (a0)
    bne      a3, a1, 2f
    sc.w     t0, a2, (a0)
    bnez     t0, 1b
2:
```

With `Zacas`: `amocas.w a1, a2, (a0)` does the same in one instruction (`rd` = expected on input and old value on output).

## 8.8 AMO semantics and alignment

- AMOs require natural alignment; a misaligned AMO raises an exception (address-misaligned, or access-fault if the PMA forbids the atomic). Profiles can add the misaligned atomicity granule `Zama16b`.
- AMOs operate on main memory with **atomicity PMAs**: `AMONone`, `AMOSwap`, `AMOLogical`, `AMOArithmetic`; some regions (devices) support none. `Ziccamoa` requires full arithmetic AMO support in cacheable coherent main memory.
- `AMOs` do not need a reservation; they are always successful.

## 8.9 C11 / C++11 mapping to RISC-V

Recommended sequences (from the ISA manual's memory-model appendix; **[verify]** against the current psABI "Atomics" document):

| C/C++ operation | RISC-V sequence |
|-----------------|-----------------|
| `load relaxed` | `l{b,h,w,d}` |
| `load acquire` | `l{b,h,w,d}; fence r,rw` |
| `load seq_cst` | `fence rw,rw; l{b,h,w,d}; fence r,rw` |
| `store relaxed` | `s{b,h,w,d}` |
| `store release` | `fence rw,w; s{b,h,w,d}` |
| `store seq_cst` | `fence rw,w; s{b,h,w,d}` |
| `atomic_thread_fence(acquire)` | `fence r,rw` |
| `atomic_thread_fence(release)` | `fence rw,w` |
| `atomic_thread_fence(acq_rel)` | `fence.tso` |
| `atomic_thread_fence(seq_cst)` | `fence rw,rw` |
| `fetch_<op> relaxed` | `amo<op>.{w,d}` |
| `fetch_<op> acquire` | `amo<op>.{w,d}.aq` |
| `fetch_<op> release` | `amo<op>.{w,d}.rl` |
| `fetch_<op> acq_rel` / `seq_cst` | `amo<op>.{w,d}.aqrl` |
| `compare_exchange` relaxed | `1: lr; bne; sc; bnez 1b` |
| `compare_exchange` acquire | `lr.aq ... sc` |
| `compare_exchange` release | `lr ... sc.rl` |
| `compare_exchange` acq_rel | `lr.aq ... sc.rl` |
| `compare_exchange` seq_cst | `lr.aqrl ... sc.rl` |

Notes:

- Because SC loads here start with a full fence, SC stores need only `fence rw,w` (they pair with the leading fence of SC loads).
- Compilers may choose the **`Zalasr`** forms (`lw.aq`, `sw.rl`, ...) when available for cheaper acquire/release **[verify status]**.
- Under **`Ztso`**, acquire/release loads/stores need no fences; only the store->load SC case needs `fence rw,rw` (or an `amoswap.aqrl` style store).
- `memory_order_consume` is typically promoted to acquire.

## 8.10 Ztso (Total Store Ordering)

`Ztso` is an optional extension. Under it:

- All loads behave as if acquire; all stores as if release; all AMOs as `.aqrl`.
- The only reordering allowed: a **later load may pass an earlier store** to a different address (store buffer).
- Binary marking: `EF_RISCV_TSO` in the ELF header; compiler flag `-march=..._ztso`.
- RVWMO software also works on Ztso hardware (Ztso is stronger).
- Code written for TSO must **not** run on weak-model hardware without inserting fences.
- Used for fast x86-binary translation and porting lock-free code.

## 8.11 I/O ordering and memory-mapped devices

- Device regions have **I/O** or **main-memory** PMAs. The ordering of device accesses is governed by the `i` and `o` bits of `fence` and the region's *channel* (accesses in different channels are not ordered).
- Typical driver patterns (Linux names):

| Pattern | RISC-V |
|---------|--------|
| `writel(v, addr)` | `fence w,o; sw v,(addr)` |
| `readl(addr)` | `lw v,(addr); fence i,r` |
| `wmb()` between normal stores | `fence w,w` |
| `rmb()` | `fence r,r` |
| `mb()` | `fence rw,rw` |
| DMA descriptor then doorbell | descriptor stores, `fence w,o`, MMIO write |

- With `Svpbmt`, IO-type pages are **strongly ordered**, `NC` pages are weakly ordered non-cacheable.

## 8.12 Instruction fetch and self-modifying code

- Stores are not automatically visible to the instruction fetch of the *same* hart. Use `fence.i` after writing code (`Zifencei`).
- For **cross-hart** code modification: the writer makes the store visible (`fence w,w`/release), the other harts must execute `fence.i` after observing it. Operating systems implement this with IPIs (SBI `remote_fence_i`).
- RVA23 says `Zifencei` is currently the only standard way for instruction-cache coherence; a new mechanism (**`Zjid`**) is under development **[verify]**.
- Page-table and TLB visibility: `sfence.vma` (Chapter 6).

## 8.13 Practical lock-free patterns

### Message passing with release/acquire (assembly)

AMOs take no immediate offset, so compute the flag address first.

```asm
# producer: data in a1 stored to (a0), flag at 8(a0)
    sw       a1, 0(a0)
    li       t0, 1
    addi     t1, a0, 8
    amoswap.w.rl x0, t0, (t1)     # release store of the flag
# consumer
1:  lw       t2, 0(t1)            # load flag
    beqz     t2, 1b
    fence    r, rw                # acquire
    lw       a2, 0(a0)            # sees data
```

### Test-and-test-and-set spinlock

```asm
lock:
1:  lw           t0, 0(a0)
    bnez         t0, 1b
    li           t0, 1
    amoswap.w.aq t0, t0, (a0)
    bnez         t0, 1b
    ret
unlock:
    amoswap.w.rl x0, x0, (a0)
    ret
```

With `Zihintpause`, add `pause` inside the spin loop. With `Zawrs`, use `wrs.nto` paired with `lr`.

### Seqlock reader (outline)

```
do { s1 = load_acquire(seq); data = read(); fence r,r; s2 = load(seq);} while (s1 != s2 || (s1 & 1));
```

## 8.14 Debugging concurrency bugs

| Symptom | Likely cause |
|---------|--------------|
| Works on x86, fails on RISC-V | Missing acquire/release or fences; code assumed TSO |
| Stale data after flag observed | Missing `fence r,r`/acquire on consumer or missing `fence w,w`/release on producer |
| Hang in `lr/sc` loop | Unconstrained loop in your code; reservation lost repeatedly (livelock) |
| Rare crash after JIT or module load | Missing `fence.i` (also on other harts) |
| Device sees stale descriptors | Missing `fence w,o` before doorbell, or non-coherent DMA without `cbo.clean` |
| Stale TLB after `munmap` | Missing `sfence.vma` / remote shootdown |

Tools: **herd7** with the RISC-V model (`riscv.cat`), **Diy7/litmus7**, **rmem** (operational model), **Isla/Sail** model, Linux `tools/memory-model`, ThreadSanitizer (compile-time instrumentation), `loom`-style tests.

## 8.15 Chapter summary

- RVWMO is weak but multi-copy atomic: only coherence, dependencies, fences, acquire/release and AMO/LR-SC rules order accesses.
- `fence pred,succ` is the swiss-army barrier; `.aq/.rl` give cheaper one-way ordering.
- LR/SC is guaranteed to make progress only within a constrained loop; AMOs always succeed.
- `Ztso` strengthens the model to TSO for porting; RVWMO code remains valid.
- Instruction fetch and TLB are not coherent with stores without `fence.i` and `sfence.vma`.

### Check yourself

1. In MP, which two fences (or annotations) restore message passing?
2. Is `r1 = 0, r2 = 0` allowed in the store-buffering litmus test under TSO? Under RVWMO?
3. Does a control dependency order a load after another load?
4. What are the C11 sequences for `store release` and `load acquire`?
5. Why does an AMO have no offset field?

<details><summary>Answers</summary>

1. Producer `fence w,w` (or release), consumer `fence r,r` (or acquire).
2. Allowed in both.
3. No; control dependencies order load->store only.
4. `fence rw,w; s*` and `l*; fence r,rw`.
5. The encoding repurposes the immediate bits for `funct5/aq/rl`; the address is just `rs1`.
</details>

Next: [Chapter 9 - ABI, Toolchain, Assembly](09_ABI_Toolchain_Assembly.md)
