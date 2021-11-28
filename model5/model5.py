from pyomo.environ import *
import numpy as np

# minimize the cost subject to nutritional values constraints and food group constraints, flow constraints
model = AbstractModel()
# Sets
# set of commodities
model.K = Set()
# set of nutrients
model.L = Set()
# set of food groups
model.G = Set()
# set of Supplier (source nodes)
model.S = Set()
# NFDP =Set of Final Delivery Points
model.Nfdp = Set()
# B =Set of beneficiary types
model.B = Set()
# T =Set of months.
model.T = Set()

# Params
# alpha: conversion rate from metric tonnes to grams 10^6
model.alpha = Param(model.K)

# Current number of feeding days per month for beneficiaries of type b
model.days = Param(model.B)

# The beneficiary type to be optimized (ben 2 B)
model.ben = Param()

# Number of beneficiaries of type b at node i in Nfdp in month t
model.dem = Param(model.B, model.Nfdp, model.T, within=NonNegativeReals)

# The food group that commodity k belongs to
model.group = Param(model.K)

# Nutritional requirement of beneficiaries of type b for nutrient l
model.nutReq = Param(model.L)
# Nutritional value per gram of commodity k for nutrient l
model.nutVal = Param(model.K, model.L)

# min ration in grams per person per day for each food group
model.minRat = Param(model.G, within=NonNegativeReals)
# max ration in grams per person per day for each food group
model.maxRat = Param(model.G, within=NonNegativeReals)
# total supply cost for 1 metric ton of commodity k from supplier s
model.sCost = Param(model.K, model.S, within=NonNegativeReals)

# Variables
# Ration of commodity k in the food basket of month t (gram/person/day)
model.ration = Var(model.K, model.T, within=NonNegativeReals)
# Flow of commodity k from node i to node j in month t (metric tonnes)
model.flow = Var(model.K, model.S, model.Nfdp, model.T, within=NonNegativeReals)


# Objective
# minimize total cost
def cost_rule(model):
    return sum((model.sCost[k, s]) * model.flow[k, s, n_fdp, t]
               for s in model.S for k in model.K for n_fdp in model.Nfdp for t in model.T)


model.objective = Objective(rule=cost_rule)


# Constraints
# 1-supplied nutrients must be more than or equal required nutrients
def nutrients_limit_rule(m, n):
    return sum(m.nutVal[k, n] * m.ration[k, t] for k in m.K for t in m.T) >= m.nutReq[n]


# creates one constraint for each member of the set model.L
model.nutrients_cover_requirements = Constraint(model.L, rule=nutrients_limit_rule)


# 2-satisfy min ration of food group
# data: set of commodities, set of groups , param that describes the food group tha commodity k belongs to
# k in m.k and k belong to group g
# sum of ratios of all commodities belonging to certain group must be more than or equal to this group min ration
def min_ration_rule(m, g):
    return sum(m.ration[k, t] * int(m.group[k] == g) for k in m.K for t in m.T) >= m.minRat[g]


model.min_rat_constraint = Constraint(model.G, rule=min_ration_rule)


# 3-satisfy max ration of food group
def max_ration_rule(m, g):
    return sum(m.ration[k, t] * int(m.group[k] == g) for k in m.K for t in m.T) <= m.maxRat[g]


model.max_rat_constraint = Constraint(model.G, rule=max_ration_rule)


# 4- flow from source i  must equal ration in food basket
def flow_rule(m, k, n_fdp, t):
    return sum(m.flow[k, s, n_fdp, t] for s in m.S) * m.alpha == m.dem[m.ben, n_fdp, t] * m.days[m.ben] * m.ration[k, t]


model.flow_constraint = Constraint(model.K, model.Nfdp, model.T, rule=flow_rule)
