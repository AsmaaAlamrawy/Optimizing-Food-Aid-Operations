from pyomo.environ import *
import numpy as np

# minimize the cost subject to nutritional values constraints and food group constraints, flow constraints
model = AbstractModel()
# Sets
# 1-set of commodities
model.K = Set()
# 2-set of nutrients
model.L = Set()
# 3-set of food groups
model.G = Set()
# 4-set of Supplier
model.S = Set()

# Params
# 1-nutritional requirements for nutrient l in a food basket(initially we working on 1 food basket for one person)
model.nutReq = Param(model.L)
# 2- nutritional values for each nutrient per gram of commodity k
model.nutVal = Param(model.K, model.L)
# 3-The food group that commodity k belongs to
model.group = Param(model.K)
# 4- min ration in grams per person per day for each food group
model.minRat = Param(model.G, within=NonNegativeReals)
# 5- max ration in grams per person per day for each food group
model.maxRat = Param(model.G, within=NonNegativeReals)
# 6- conversion rate from metric tonnes to grams 10^6
model.alpha = Param(model.K)
# 7- total supply cost for 1 metric ton of commodity k from supplier s
model.sCost = Param(model.K, model.S, within=NonNegativeReals)

# Variables
# 1-ration of each commodity k in the food basket in grams
model.ration = Var(model.K, within=NonNegativeReals)
# 2-quantity from supplier s of commodity k in the food basket
model.flow = Var(model.K, model.S, within=NonNegativeReals)


# Objective
# minimize total cost
def cost_rule(model):
    return sum((model.sCost[k, s]) * model.flow[k, s] for s in model.S for k in model.K)


model.objective = Objective(rule=cost_rule)


# Constraints
# 1-supplied nutrients must be more than or equal required nutrients
def nutrients_limit_rule(m, n):
    return sum(m.nutVal[k, n] * m.ration[k] for k in m.K) >= m.nutReq[n]


# creates one constraint for each member of the set model.L
model.nutrients_cover_requirements = Constraint(model.L, rule=nutrients_limit_rule)


# 2-satisfy min ration of food group
# data: set of commodities, set of groups , param that describes the food group tha commodity k belongs to
# k in m.k and k belong to group g
# sum of ratios of all commodities belonging to certain group must be more than or equal to this group min ration
def min_ration_rule(m, g):
    return sum(m.ration[k] * int(m.group[k] == g) for k in m.K) >= m.minRat[g]


model.min_rat_constraint = Constraint(model.G, rule=min_ration_rule)


# 3-satisfy max ration of food group
def max_ration_rule(m, g):
    return sum(m.ration[k] * int(m.group[k] == g) for k in m.K) <= m.maxRat[g]


model.max_rat_constraint = Constraint(model.G, rule=max_ration_rule)


# 4- flow from source i  must equal ration in food basket
def flow_rule(m, k):
    return sum(m.flow[k, s] for s in m.S) == m.ration[k]


model.flow_constraint = Constraint(model.K, rule=flow_rule)


# there should be an upper limit for nutrients too besides the upper limit of food groups!

# instance = model.create_instance(data="data4.dat")
# opt = pyomo.SolverFactory('glpk')

# results = opt.solve(instance)
