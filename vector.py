import math

def vector_length(vector):
    d2 = sum( x*x for x in vector )
    return math.sqrt(d2)
    
def vector_dot(vector_a, vector_b):
    s = sum(x*y for x,y in zip(vector_a, vector_b))
    return s

def vector_add(vector_a, vector_b):
    s = [x+y for x,y, in zip(vector_a, vector_b)]
    return s

def vector_sub(vector_a, vector_b):
    """
    From b to a
    """
    s = [x-y for x,y, in zip(vector_a, vector_b)]
    return s   

def vector_scalar(s, vector):
    r = [s * x for x in vector]
    return r

def vector_elongate(vector, length):
    l = vector_length(vector)
    v = vector_scalar((l + length) / l, vector)
    return v
    
def vector_cross(a, b):
    """
    http://en.wikipedia.org/wiki/Cross_product
    """
    x = a[1]*b[2] - a[2]*b[1]
    y = a[2]*b[0] - a[0]*b[2]
    z = a[0]*b[1] - a[1]*b[0]
    return [x, y, z]

def vector_unit(vector):
    length = vector_length(vector)
    l = 1.0 / length
    n = vector_scalar(l, vector)
    return n


