"""Module 09 · Rajaraman–Wong 延迟导向聚类 —— 练习起始代码（Python 3.9+，仅标准库）。

模型（Rajaraman & Wong, IEEE TCAD 1995；会议版 DAC 1993）：组合电路 DAG，节点延迟 δ(v)，
节点大小（此处默认 1），簇容量 M；簇内连线额外延迟 0，跨簇连线固定 D；允许复制逻辑节点。
目标：最小化 PI→PO 的最大延迟。论文的最优性只在这个模型里成立；本文件的测试不证明它。

逻辑节点与物理实例分开：实例 id 写成 "节点@簇根"，同一逻辑节点可以有多个实例。
平票（假设，未经原作者确认）：l(x)+Δ(x,v) 相等时，拓扑序靠后的 x 优先。
"""


def topological_order(nodes, edges):
    """任务 1（基础）：Kahn 拓扑排序。多个节点同时可选时按 nodes 中的顺序；有环时抛 ValueError。"""
    raise NotImplementedError("topological_order")


def longest_node_delays(nodes, edges, delay):
    """任务 2（基础）：Δ[x][v] = x→v 路径上节点延迟之和的最大值（计 v、不计 x），无路径为 None。

    在候选 DAG 中 Δ[b][k] = 4（b→e→g→i→k 或 b→e→g→j→k，经过 e、g、i/j、k 四个节点）。
    """
    raise NotImplementedError("longest_node_delays")


def evaluate_instance_delay(instances, instance_edges, delay):
    """任务 3（基础）：实例到达时间 t(i) = δ(逻辑节点) + max(来源到达 + 代价)。

    链 P→X→Y→O，δ=1，分成 {P,X} | {Y,O}：X→Y 跨簇代价 3，输出延迟 1+1+3+1+1 = 7。
    """
    raise NotImplementedError("evaluate_instance_delay")


def rw_label(dag):
    """任务 4（进阶）：按拓扑序给每个非 PI 节点打标签，返回 (label, cluster, steps)。

    对 v 的每个祖先 x 算 l(x)+Δ[x][v]，降序排（相等时拓扑序靠后者优先——这是本课程采用的假设）；
    v 加前 M−1 个组成候选簇；l1 = 簇内 PI 的最大值，l2 = 簇外祖先值 + D 的最大值；l(v) = max(l1, l2)。
    """
    raise NotImplementedError("rw_label")


def rw_reconstruct(dag, cluster):
    """任务 5（进阶）：从 PO 倒推需要的簇，生成实例与实例边，返回 (selected, instances, instance_edges)。

    簇根 r 的成员 m 生成实例 "m@r"。m 的每个输入 u：若 u 在同簇 → ("u@r", "m@r", 0)，否则 → ("u@u", "m@r", D)，
    且 u 自己也成为一个要恢复的簇根。同一逻辑节点可能出现在多个簇里——这就是复制。
    """
    raise NotImplementedError("rw_reconstruct")


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
