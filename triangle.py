
import unittest
from stlfacets import facets_from_file
from vector import vector_sub, vector_unit, vector_scalar, vector_cross,\
    vector_dot, vector_length
from time import time


def calc_cut_direction(normal):
    d = vector_cross((0,0,1), normal)
    return d

def calc_inset_direction(cut_direction):
    inset_raw = vector_cross((0,0,1), cut_direction)
    inset = vector_unit(inset_raw)
    return inset

def swap(t1, t2):
    return t2, t1

def split_triangle(normal, v0, v1, v2):
    
    # we will return 0, 1 or 2 triangles
    results = [] 
        
    cut_direction = calc_cut_direction(normal)
    # weed out triangles on same z plane
    if vector_length(cut_direction) == 0:
        return
    
    inset_direction = calc_inset_direction(cut_direction)
    
    # sort triangle vertices along z
    bottom, mid, top = sorted([v0, v1,v2], key=lambda x: x[2])
    
    # split triangle in two 
    u1 = vector_sub(top, bottom)
    u1 = vector_unit(v1)
    u2 = vector_sub(top, mid)
    u2 = vector_unit(v2)
    
    u3 = vector_scalar(-1.0, u1)
    u4 = vector_sub(mid, bottom)
    u4 = vector_unit(u4) 
    
    if vector_dot(normal, vector_cross(u1,u2)  ) < 0:
        u1, u2 = swap(u1, u2)
        u3, u4 = swap(u3, u4)

    min_z = mid[2]
    max_z = top[2]
    if(min_z < max_z):
        results.append([min_z, max_z, top, u1, u2, inset_direction])
        
    min_z = bottom[2]
    max_z = mid[2]
    if(min_z < max_z):
        results.append([min_z, max_z, bottom, u3, u4, inset_direction])        
    
    return results
    
    
    

class Testing(unittest.TestCase):

    def setUp(self):
        pass

    def test_splits(self):
        start_time = time()
        facet_generator = facets_from_file('bunny.stl')
        
        all_triangles = []
        mins = []
        max =  []
        counter =0
        try:
            while 1:
                (normal, v0,v1,v2) = next(facet_generator)
                for min_z, max_z, bottom, u3, u4, inset_direction in split_triangle(normal, v0,v1,v2):
                    counter +=1
                    mins.append([min_z, counter])
                    max.append([min_z, counter])
                    all_triangles.append([bottom, u3, u4, inset_direction]) 
        except StopIteration:
            pass
        
        elapsed = time() - start_time
        print ("File read in %s sec" % (elapsed) ) 
        print( "Nb of split triangles", len(all_triangles))
        
        
    def test_write_layer_cad(self):
        """   
     
    polyhedron( points = [
        [-29.912, 25.026, 79.747], 
        [-29.542, 25.700, 79.969], 
        [-30.338, 25.182, 80.071], 
        ...
        ],
       triangles = [[0, 1, 2], [3, 4, 5], 
        ...
        [6, 7, 8], [9, 10, 11]
    ]);                 
        """   
     
        facet_generator = facets_from_file('bunny.stl')
        triangles = []
        z = 80.0
        
        points = []
        triangles = []
        counter = 0
        
        try:
            while 1:
                (normal, v0,v1,v2) = next(facet_generator)
                s = sorted([v0,v1,v2], key=lambda x: x[2])
                min_z = s[0][2]
                max_z = s[2][2]
                if z > min_z and z <= max_z:
                    points.append( v0 )
                    points.append( v1 )
                    points.append( v2 )
                    
                    triangles.append([counter, counter+1, counter+2])
                    counter +=3
        
        except StopIteration:
            pass

        
        f= open('layer.scad','w+')
        print("polyhedron( points = [", file=f)
        print ("polyhedron( points = [", file = f)
        for p in points:
            print("    [%3.3f, %3.3f, %3.3f], " % p, file = f)
        
        print("],\n triangles = %s);" % triangles, file=f)
        f.close()
        
        
    def test_split(self):
        triangle = [ [-29.912, 25.026, 79.747], [-29.542, 25.700, 79.969], [-30.338, 25.182, 80.071]]
        s = split_triangle([0,0.1,0.6], triangle[0], triangle[1], triangle[2])
        self.assertEqual(len(s), 2)   
        print("t0 ", s[0])
        print("t1 ", s[1])                   
        
        
if __name__ == '__main__':
    unittest.main()