from pyomo.environ import *
import numpy as np
# Satisfy nutritional requirments
model = AbstractModel()
# Sets

# 1-set of commodities
model.K = Set()
# 2-set of nutrients
model.L = Set()

# Params
# 1-nutritional requirements for nutrient l in a food basket(initially we working on 1 food basket for one person)
model.nutReq = Param(model.L)
# 2- nutritional values for each nutrient per gram of commodity k
model.nutVal = Param(model.K, model.L)

# Variables
# 1-ration of each commodity k in the food basket
model.ration = Var(model.K, within=NonNegativeReals)


# objective
# minimize nutritional gap between supplied nutrients and required nutrients
# sum of nutVal of  nutrient l  in all commodities - requirments of this nutrient l
def nutrients_target_rule(model):
    return sum(
        sum(model.nutVal[k, l] * model.ration[k] for k in model.K) - model.nutReq[l] for l in model.L)


model.objective = Objective(rule=nutrients_target_rule)


# supplied nutrient must cover the requirements
def nutrients_limit_rule(m, n):
    return sum(m.nutVal[k, n] * m.ration[k] for k in m.K) >= m.nutReq[n]


model.nutrients_cover_requirements = Constraint(model.L, rule=nutrients_limit_rule)
