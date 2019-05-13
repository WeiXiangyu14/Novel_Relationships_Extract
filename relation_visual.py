import json
import os
import pickle
import math

from pyecharts import options as opts
from pyecharts.charts import Graph, Page


def calcwidth(x):
    res = 1
    while x > 1:
        x = x // 2
        res += 1
    return res


def calcsize(x):
    return max(math.sqrt(x)*2, 5)

def modify_name(name):
    res = ""
    if name[0:3] == "mrs":
        res = "Mrs. " + name[3:].capitalize()
    elif name[0:2] == "mr":
        res = "Mr. " + name[2:].capitalize()
    else:
        res = name.capitalize()
    return res

def relation_name(n1, n2, r):
    if r[-1] == "s":
        r = r[:-1]
    return modify_name(n1)+" is "+modify_name(n2)+"'s "+r

def graph_base() -> Graph:

    f = open("relation_pap", "rb")
    dic = pickle.load(f)


    used_names = []
    for r in dic:
        for (n1, n2) in dic[r]:
            if n1 not in used_names:
                used_names.append(n1)
            if n2 not in used_names:
                used_names.append(n2)

    nodes = []

    for n in used_names:
        nodes.append(opts.GraphNode(name=modify_name(n), symbol_size = 40))

    for r in dic:
        dic[r] = list(set(dic[r]))
        for(n1, n2) in dic[r]:
            nodes.append(opts.GraphNode(name=relation_name(n1, n2, r), symbol="rect" ,symbol_size=10))


    links = []

    for r in dic:
        for (n1, n2) in dic[r]:
            links.append(opts.GraphLink(source=modify_name(n1), target=relation_name(n1, n2, r), linestyle_opts=opts.LineStyleOpts(width=5)))
            links.append(opts.GraphLink(source=modify_name(n2), target=relation_name(n1, n2, r),
                                        linestyle_opts=opts.LineStyleOpts(width=5)))

    c = (
        Graph(init_opts=opts.InitOpts(width="1800px", height="900px"))
        .add("", nodes, links, repulsion=6000)
        .set_global_opts(title_opts=opts.TitleOpts(title="Relationship in Harry Potter"))
    )
    return c

c = graph_base()
c.render("relation_HP1.html")