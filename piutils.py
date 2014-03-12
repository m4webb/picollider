import random

def multinomial_draw(stochastic_vector):
    """Return a multinomial draw from distribution given by stochastic vector.
    
    If sum(stochastic_vector) < 1, may throw an error. 
    If sum(stochastic_vector) > 1, results will be weird.
    """
    uniform_draw = random.random()
    i = 0
    try:
        while uniform_draw > stochastic_vector[i]:
            uniform_draw -= stochastic_vector[i]
            i += 1
        return i
    except IndexError:
        raise ValueError("vector not stochastic.")
