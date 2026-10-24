"""Module 09 · Rajaraman–Wong delay-oriented clustering: reference implementation (Python 3.9+, standard library only).

Model (Rajaraman & Wong, IEEE TCAD 1995; conference version DAC 1993): a combinational DAG, node delay δ(v),
node size (1 by default here), cluster capacity M; a wire inside a cluster adds 0, a wire between clusters adds a fixed D;
logic nodes may be replicated. Goal: minimise the maximum PI→PO delay. The paper's optimality holds only inside this
model; the tests in this pack do not prove it.

Logic nodes and physical instances are kept apart: an instance id is written "node@cluster-root", and one logic node
may have several instances. Ties (an assumption, not confirmed by the original author): when l(x)+Δ(x,v) are equal,
the x later in topological order goes first.
"""


def topological_order(nodes, edges):
    """Kahn's algorithm; nodes ready at the same time go in input order. Raises ValueError on a cycle."""
    pred = {v: [] for v in nodes}
    succ = {v: [] for v in nodes}
    for u, v in edges:
        pred[v].append(u)
        succ[u].append(v)
    indeg = {v: len(pred[v]) for v in nodes}
    ready = [v for v in nodes if indeg[v] == 0]
    order = []
    while ready:
        x = ready.pop(0)
        order.append(x)
        for y in succ[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                ready.append(y)
                ready.sort(key=nodes.index)
    if len(order) != len(nodes):
        raise ValueError("the input has a cycle: RW handles only combinational DAGs")
    return order


def longest_node_delays(nodes, edges, delay):
    """Δ[x][v]: the largest sum of node delays on an x→v path, counting v, not x; None when there is no path."""
    order = topological_order(nodes, edges)
    pred = {v: [u for u, w in edges if w == v] for v in nodes}
    delta = {}
    for x in nodes:
        row = {v: None for v in nodes}
        row[x] = 0
        for v in order:
            for u in pred[v]:
                if row[u] is not None:
                    row[v] = max(row[v] if row[v] is not None else float("-inf"), row[u] + delay[v])
        delta[x] = row
    return delta


def evaluate_instance_delay(instances, instance_edges, delay):
    """instances: {instance id: logic id}; instance_edges: [(source instance, target instance, extra cost)].

    Arrival time t(i) = δ(logic id) + max(source arrival + cost); with no input, just δ.
    """
    inc = {i: [] for i in instances}
    for a, b, c in instance_edges:
        inc[b].append((a, c))
    memo = {}

    def t(i, stack=()):
        if i in memo:
            return memo[i]
        if i in stack:
            raise ValueError("the instance graph has a cycle")
        memo[i] = delay[instances[i]] + max([t(a, stack + (i,)) + c for a, c in inc[i]], default=0)
        return memo[i]

    for i in instances:
        t(i)
    return memo


def rw_label(dag):
    nodes, edges = dag["nodes"], [tuple(e) for e in dag["edges"]]
    delay = {v: dag.get("node_delay", 1) for v in nodes}
    cap, D = dag["capacity"], dag["D"]
    pi = dag.get("PI") or [v for v in nodes if not any(w == v for _, w in edges)]
    order = topological_order(nodes, edges)
    pos = {v: i for i, v in enumerate(order)}
    delta = longest_node_delays(nodes, edges, delay)
    label, cluster, steps = {}, {}, []
    for p in pi:
        label[p], cluster[p] = delay[p], [p]
    for v in order:
        if v in pi:
            continue
        anc = [x for x in order if x != v and delta[x][v] is not None]
        score = {x: label[x] + delta[x][v] for x in anc}
        rank = sorted(anc, key=lambda x: (-score[x], -pos[x]))
        C = [v] + rank[:cap - 1]
        outside = rank[cap - 1:]
        l1 = max([score[x] for x in C if x in pi], default=0)
        l2 = max([score[x] + D for x in outside], default=0)
        label[v], cluster[v] = max(l1, l2), C
        steps.append({"node": v, "l1": l1, "l2": l2, "label": label[v], "cluster": C})
    return label, cluster, steps


def rw_reconstruct(dag, cluster):
    nodes, edges = dag["nodes"], [tuple(e) for e in dag["edges"]]
    D = dag["D"]
    po = dag.get("PO") or [v for v in nodes if not any(u == v for u, _ in edges)]
    pred = {v: [u for u, w in edges if w == v] for v in nodes}
    order = topological_order(nodes, edges)
    selected, queue = [], list(po)
    while queue:
        r = queue.pop(0)
        if r in selected:
            continue
        selected.append(r)
        inside = set(cluster[r])
        for m in cluster[r]:
            for u in pred[m]:
                if u not in inside and u not in selected and u not in queue:
                    queue.append(u)
    instances, iedges = {}, []
    for r in selected:
        for m in [x for x in order if x in cluster[r]]:
            instances[f"{m}@{r}"] = m
    for inst, m in instances.items():
        r = inst.split("@")[1]
        for u in pred[m]:
            iedges.append((f"{u}@{r}", inst, 0) if u in cluster[r] else (f"{u}@{u}", inst, D))
    return selected, instances, iedges


def rajaraman_wong(dag):
    label, cluster, steps = rw_label(dag)
    selected, instances, iedges = rw_reconstruct(dag, cluster)
    delay = {v: dag.get("node_delay", 1) for v in dag["nodes"]}
    t = evaluate_instance_delay(instances, iedges, delay)
    po = dag.get("PO")
    return {"labels": label, "clusters": {r: cluster[r] for r in selected}, "instances": instances,
            "instance_edges": iedges, "output_delay": {p: t[f"{p}@{p}"] for p in po}, "steps": steps}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "candidate_dag.json").read_text(encoding="utf-8"))
    r = rajaraman_wong(g)
    print("labels", r["labels"])
    print("clusters", len(r["clusters"]), "instances", len(r["instances"]), "output delay", r["output_delay"])
