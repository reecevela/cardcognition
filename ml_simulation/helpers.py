def can_pay_cost(mana_pool, cost:list):
    temp_mana_pool = mana_pool.copy()
    for c in cost:
        try:
            c = int(c)
        except ValueError:
            pass
        if isinstance(c, int):  # any color
            if len(temp_mana_pool) >= c:
                temp_mana_pool = temp_mana_pool[:-c]
            else:
                return False
        elif isinstance(c, str):  # specific color
            if c in temp_mana_pool:
                temp_mana_pool.remove(c)
            else:
                return False
    return True

def pay_cost(mana_pool, cost):
    temp_mana_pool = mana_pool.copy()
    for c in cost:
        if isinstance(c, str):  # specific color
            temp_mana_pool.remove(c)
        elif isinstance(c, int):  # any color
            # Remove the most common color
            temp_mana_pool.remove(max(set(temp_mana_pool), key=temp_mana_pool.count))
    return temp_mana_pool