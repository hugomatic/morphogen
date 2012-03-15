
import unittest
from stlfacets import facets_from_file
from vector import vector_sub, vector_unit, vector_scalar, vector_cross,\
    vector_dot, vector_length, vector_add
from time import time



def calc_cut_direction(normal):
    d = vector_cross((0,0,1), normal)
    return d

def calc_inset_direction(cut_direction):
    inset_raw = vector_cross((0,0,1), cut_direction)
    inset = vector_unit(inset_raw)
    return inset

def z_plane_intersect(p0, u, cut):
    s = (cut-p0[2])/(u[2])
    su = vector_scalar(s, u)
    p = vector_add(p0, su)
    return p

def swap(t1, t2):
    return t2, t1


def split_triangle(normal, v0, v1, v2):
    # we will return 0, 1 or 2 triangles
    results = [] 
    cut_direction = calc_cut_direction(normal)
    # weed out triangles on same z plane
    if vector_length(cut_direction) == 0:
        return results
    inset_direction = calc_inset_direction(cut_direction)
    # sort triangle vertices along z
    bottom, mid, top = sorted([v0, v1,v2], key=lambda x: x[2])
    # split triangle in two 
    u0 = vector_sub(top, bottom) # from bottom to top
    u1 = vector_sub(top, mid)
    if vector_dot(normal, vector_cross(u0,u1)  ) < 0:
        u0, u1 = swap(u0, u1)
    u2 = u0 
    u3 = vector_sub(mid, bottom)
    if vector_dot(normal, vector_cross(u3,u2)  ) < 0:
        u2, u3 = swap(u2, u3)
    min_z = mid[2]
    max_z = top[2]
    if(u0[2]>0 and u1[2]>0):
        results.append([min_z, max_z, top, u0, u1, inset_direction])
    min_z = bottom[2]
    max_z = mid[2]
    if( u2[2]>0 and u3[2]>0):
        results.append([min_z, max_z, bottom, u2, u3, inset_direction])        
    return results


def distance(pointa, pointb):
    v = vector_sub(pointb, pointa)
    d = vector_length(v)
    return d

class Testing(unittest.TestCase):
            
    def test_split_slice(self):
        z = 1.0
        segments = []
        facet_generator = facets_from_file('hexagon.stl')
        try:
            while 1:
                (normal, v0,v1,v2) = next(facet_generator)
                for min_z, max_z, p, u0, u1, inset_direction in split_triangle(normal, v0,v1,v2):
                    if min_z < z and max_z >= z:
                        normal, v0,v1,v2
                        segment_start = z_plane_intersect(p, u0, z)
                        segment_end = z_plane_intersect(p, u1, z)
                        if distance(segment_start, segment_end) > 0:
                            segments.append([segment_start, segment_end])         
        except StopIteration:
            pass
        print("writing segment.scad with %s segments" % (len(segments) ) )
        f= open('segment.scad','w')
        
        f.write ("segments = [\n")
        for a,b in segments:
            f.write ( "[ [%.5f, %.5f, %.5f ], [%.5f, %.5f, %.5f] ],\n" % (a[0], a[1], a[2], b[0], b[1], b[2]) )
        f.write("\n];\n")
        f.write("""
        
module tube(x1, y1, z1, x2, y2, z2, diameter1, diameter2, faces, thickness_over_width)
{
    length = sqrt( pow(x1 - x2, 2) + pow(y1 - y2, 2) + pow(z1 - z2, 2) );
    alpha = ( (y2 - y1 != 0) ? atan( (z2 - z1) / (y2 - y1) ) : 0 );
     beta = 90 - ( (x2 - x1 != 0) ? atan( (z2 - z1) / (x2 - x1) ) :  0 );
    gamma =  ( (x2 - x1 != 0) ? atan( (y2 - y1) / (x2 - x1) ) : ( (y2 - y1 >= 0) ? 90 : -90 ) ) + ( (x2 - x1 >= 0) ? 0 : -180 );
    // echo(Length = length, Alpha = alpha, Beta = beta, Gamma = gamma);    
    translate([x1, y1, z1])
    rotate([ 0, beta, gamma])
        scale([thickness_over_width,1,1])
            rotate([0,0,90]) cylinder(h = length, r1 = diameter1/2, r2 = diameter2/2, center = false, $fn = faces );
}

for (segment = segments)
{
    tube(segment[0][0], segment[0][1], segment[0][2], segment[1][0], segment[1][1], segment[1][2], 0.3, 0, 6, 1);
}          
        
        """ % ())
        f.close()

    def test_split_triangle(self):
        normal, v0,v1,v2 = ((0.998312, 0.05807914, 0.0), (-2.462019, -0.4341192, 10.0), (-2.5, 7.152557e-07, 3.469447e-15), (-2.5, 7.152557e-07, 10.0))
        print( normal, v0,v1,v2)
        print( "min_z, max_z, p, u0, u1, inset_direction")
        for min_z, max_z, p, u0, u1, inset_direction in split_triangle(normal, v0,v1,v2):
            print ("%s\t%s\t%s\t%s\t%s\t%s" % (min_z, max_z, p, u0, u1, inset_direction) )
            self.assertLess(0, u1[2])
        
    def a_test_splits(self):
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
     
        facet_generator = facets_from_file('hexagon.stl')
        triangles = []
        z = 1.0
        
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

        
        f= open('layer.scad','w')

        f.write ("polyhedron( points = [")
        for p in points:
            f.write("    [%3.3f, %3.3f, %3.3f],\n" % p)
        
        f.write("],\n triangles = %s);\n" % triangles)
        f.close()
        
    def test_split_hex(self):
        triangle =  [ [10.000, -5.774, 10.000], [0.000, -11.547, 10.000], [10.000, -5.774, 0.000] ]  
        u0 = vector_sub(triangle[0], triangle[1])
        u1 = vector_sub(triangle[1], triangle[2])
        n = vector_cross(u0, u1)
        s = split_triangle( n, triangle[0], triangle[1], triangle[2])
        self.assertEqual(len(s), 1) 
        print("t0 ", s[0])
        
          
    def test_split(self):
        triangle = [ [-29.912, 25.026, 79.747], [-29.542, 25.700, 79.969], [-30.338, 25.182, 80.071]]
        s = split_triangle([0,0.1,0.6], triangle[0], triangle[1], triangle[2])
         
        print("t0 ", s[0])
        self.assertEqual(len(s), 2)  
        print("t1 ", s[1])  
        
    
    def test_cut(self):
        p0 = [0,0,0]
        p1 = [0,0,1]
        
        u = vector_add(p0, p1)
        p = z_plane_intersect(p0, u, 0.5)
        
        self.assertAlmostEqual(p[2], 0.5, 3)
                         
        
        
if __name__ == '__main__':
    unittest.main()