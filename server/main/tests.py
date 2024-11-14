
import json
food_orders = {
    "items1": 1,
    "items2": 2,

}
f_j = json.dumps(food_orders)
l = json.loads(f_j)
l.update({"items3": 3})
print(l)
f_j = json.dumps(l)
print(f_j)
