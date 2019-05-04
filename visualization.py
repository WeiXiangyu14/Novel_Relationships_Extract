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
    # res = 1
    # sqart = 1.2
    # while x > sqart:
    #     sqart *= sqart
    #     res += 1
    # return 5*res
    return max(math.sqrt(x)*2, 5)

def graph_base() -> Graph:

    f = open("two_names_dict", "rb")
    dic = pickle.load(f)

    num_dic = {}
    for k in dic:
        num_dic.update({k: 0})
        num_k = 0
        for k2 in dic[k]:
            num_k += dic[k][k2]
        num_dic[k] = num_k



    nodes = [
        # opts.GraphNode(name="结点1", symbol_size=10),
        # opts.GraphNode(name="结点2", symbol_size=20),
        # opts.GraphNode(name="结点3", symbol_size=30),
        # opts.GraphNode(name="结点4", symbol_size=40),
        # opts.GraphNode(name="结点5", symbol_size=50),
    ]

    for k in dic:
        nodes.append(opts.GraphNode(name=k, value=str(num_dic[k]), symbol_size = calcsize(num_dic[k])))

    links = [
        # opts.GraphLink(source="结点1", target="结点2", value=30, linestyle_opts= opts.LineStyleOpts(width=10)),
        # opts.GraphLink(source="结点2", target="结点3"),
        # opts.GraphLink(source="结点3", target="结点4"),
        # opts.GraphLink(source="结点4", target="结点5"),
        # opts.GraphLink(source="结点5", target="结点1"),
    ]

    for k1 in dic:
        for k2 in dic[k1]:
            if dic[k1][k2] > 0:
                links.append(opts.GraphLink(source=k1, target=k2, value=dic[k1][k2], linestyle_opts=opts.LineStyleOpts(width=calcwidth(dic[k1][k2]))))

    c = (
        Graph(init_opts=opts.InitOpts(width="1600px", height="700px"))
        .add("", nodes, links, repulsion=8000)
        .set_global_opts(title_opts=opts.TitleOpts(title="Number of times two people in same sentence"))
    )
    return c

c = graph_base()
c.render("two_name_times.html")