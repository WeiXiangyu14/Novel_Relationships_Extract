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
    return res/2


def calcsize(x):
    # res = 1
    # sqart = 1.2
    # while x > sqart:
    #     sqart *= sqart
    #     res += 1
    # return 5*res
    return max(math.sqrt(x)*1.4, 5)

def graph_base() -> Graph:

    f = open("two_names_dict_hp", "rb")
    dic = pickle.load(f)

    num_dic = {}
    for k in dic:
        num_dic.update({k: 0})
        num_k = 0
        for k2 in dic[k]:
            if k2 != k:
                num_k += dic[k][k2]
        num_dic[k] = num_k



    nodes = []

    for k in dic:
        if k:
            if len(k) > 0:
                if num_dic[k] > 0:
                    nodes.append(opts.GraphNode(name=k, value=str(num_dic[k]), symbol_size = calcsize(num_dic[k])))

    links = []

    for k1 in dic:
        for k2 in dic[k1]:
            if k1 and k2:
                if dic[k1][k2] > 0:
                    if len(k1) > 0 and len(k2) > 0:
                        if num_dic[k1] > 0 and num_dic[k2] > 0:
                            links.append(opts.GraphLink(source=k1, target=k2, value=dic[k1][k2], linestyle_opts=opts.LineStyleOpts(width=calcwidth(dic[k1][k2]))))

    c = (
        Graph(init_opts=opts.InitOpts(width="1800px", height="900px"))
        .add("", nodes, links, repulsion=12000)
        .set_global_opts(title_opts=opts.TitleOpts(title="Interactions of Pride and Prejudice"))
    )
    return c

c = graph_base()
c.render("int_pap.html")