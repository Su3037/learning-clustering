"""Module 09 · Rajaraman–Wong delay-oriented clustering: exercise starter (Python 3.9+, standard library only).

Model (Rajaraman & Wong, IEEE TCAD 1995; conference version DAC 1993): a combinational DAG, node delay δ(v),
node size (1 by default here), cluster capacity M; a wire inside a cluster adds 0, a wire between clusters adds a fixed D;
logic nodes may be replicated. Goal: minimise the maximum PI→PO delay. The paper's optimality holds only inside this
model; the tests in this pack do not prove it.

Logic nodes and physical instances are kept apart: an instance id is written "node@cluster-root", and one logic node
may have several instances. Ties (an assumption, not confirmed by the original author): when l(x)+Δ(x,v) are equal,
the x later in topological order goes first.
"""


def topological_order(nodes, edges):
    """Task 1 (basic): Kahn topological sort. When several nodes are ready, take them in the order of nodes; raise ValueError on a cycle."""
    raise NotImplementedError("topological_order")


def longest_node_delays(nodes, edges, delay):
    """Task 2 (basic): Δ[x][v] = the largest sum of node delays on an x→v path (counting v, not x); None when there is no path.

    In the candidate DAG Δ[b][k] = 4 (b→e→g→i→k or b→e→g→j→k, through the four nodes e, g, i/j, k).
    """
    raise NotImplementedError("longest_node_delays")


def evaluate_instance_delay(instances, instance_edges, delay):
    """Task 3 (basic): instance arrival time t(i) = δ(logic node) + max(source arrival + cost).

    Chain P→X→Y→O, δ=1, split {P,X} | {Y,O}: X→Y crosses at cost 3, output delay 1+1+3+1+1 = 7.
    """
    raise NotImplementedError("evaluate_instance_delay")


def rw_label(dag):
    """Task 4 (advanced): label every non-PI node in topological order; return (label, cluster, steps).

    For each ancestor x of v compute l(x)+Δ[x][v] and sort descending (on ties the later x in topological order first:
    an assumption this course makes); v plus the first M−1 form the candidate cluster; l1 = the largest value of a PI
    inside the cluster, l2 = the largest value of an ancestor outside it + D; l(v) = max(l1, l2).
    """
    raise NotImplementedError("rw_label")


def rw_reconstruct(dag, cluster):
    """Task 5 (advanced): work back from the POs to the clusters needed, build instances and instance edges;
    return (selected, instances, instance_edges).

    Member m of the cluster rooted at r becomes instance "m@r". For each input u of m: if u is in the same cluster →
    ("u@r", "m@r", 0), otherwise → ("u@u", "m@r", D), and u itself becomes a cluster root to recover. One logic node
    can appear in several clusters: that is replication.
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
    print("clusters", len(r["clusters"]), "instances", len(r["instances"]), "output delay", r["output_delay"])
