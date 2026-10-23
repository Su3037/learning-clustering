"""Module 09 · Rajaraman–Wong 延迟导向聚类 —— 参考实现（Python 3.9+，仅标准库）。

模型（Rajaraman & Wong, IEEE TCAD 1995；会议版 DAC 1993）：组合电路 DAG，节点延迟 δ(v)，
节点大小（此处默认 1），簇容量 M；簇内连线额外延迟 0，跨簇连线固定 D；允许复制逻辑节点。
目标：最小化 PI→PO 的最大延迟。论文的最优性只在这个模型里成立；本文件的测试不证明它。

逻辑节点与物理实例分开：实例 id 写成 "节点@簇根"，同一逻辑节点可以有多个实例。
平票（假设，未经原作者确认）：l(x)+Δ(x,v) 相等时，拓扑序靠后的 x 优先。
"""


def topological_order(nodes, edges):
    """Kahn 算法；同时可选的节点按输入顺序。有环时抛 ValueError。"""
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
        raise ValueError("输入含有环：RW 只处理组合电路 DAG")
    return order


def longest_node_delays(nodes, edges, delay):
    """Δ[x][v]：x→v 路径上节点延迟之和的最大值，计 v 不计 x；无路径为 None。"""
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
    """instances: {实例id: 逻辑id}；instance_edges: [(来源实例, 目标实例, 额外代价)]。

    到达时间 t(i) = δ(逻辑id) + max(来源到达时间 + 代价)，没有输入时只有 δ。
    """
    inc = {i: [] for i in instances}
    for a, b, c in instance_edges:
        inc[b].append((a, c))
    memo = {}

    def t(i, stack=()):
        if i in memo:
            return memo[i]
        if i in stack:
            raise ValueError("实例图含环")
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
    print("簇", len(r["clusters"]), "实例", len(r["instances"]), "输出延迟", r["output_delay"])
