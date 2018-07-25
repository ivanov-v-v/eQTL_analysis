import os
import pickle
import random
import time

import numpy as np
import pandas as pd

import qtls

# os.chdir("/home/vvi/Science/eQTL_analysis/")
os.chdir("/home/ivanov_vv/eQTL_analysis/")

random.seed(time.time())

eQTLs_expression_df = pd.read_table("./data/eQTLs/averaged_expression.csv")
pQTLs_expression_df = pd.read_table("./data/pQTLs/averaged_expression.csv")

# QTLs estimated with MatrixEQTL package for R
eQTLs_df = pd.read_table("./data/eQTLs/results.csv").query("q_value < 0.05")
pQTLs_df = pd.read_table("./data/pQTLs/results.csv").query("q_value < 0.05")

interactions_type = "physical"
with open("./data/interactions/{}_interactions_graph.pkl".format(interactions_type), "rb") as pickle_file:
    interactome_graph = pickle.load(pickle_file)

modules_type = "kegg_modules"
with open("./results/" + modules_type + "/modules_for_ppi_test.pkl", "rb") as pickle_file:
    modules_to_test = pickle.load(pickle_file)

for qtl_type, qtl_df, expression_df in [("eQTLs", eQTLs_df, eQTLs_expression_df),
                                        ("pQTLs", pQTLs_df, pQTLs_expression_df)]:
    module_analyzer = qtls.LinkageSharingAnalyzer(
        expression_df=expression_df,
        interactome_graph=interactome_graph,
        modules_type=modules_type,
        module_dict=modules_to_test[qtl_type],
        qtl_type=qtl_type,
        qtl_df=qtl_df,
        q_thresholds=np.logspace(-5, -2, 10),
        pairwise_test_iter=200,
        ppi_test_iter=1024
    )
    module_analyzer.pairwise_test()
    module_analyzer.ppi_test()
