from time import time



def tokens_from_file(filename):
    with open(filename,'rt') as infile:
        for line in infile:
            for item in line.split():
                yield item
    print ('closing %s' % filename)
    infile.close()


def facets_from_file(file_path):
    
    def seek_token(token_generator, token_name):
        token = ""
        while token != token_name:
            token = next(token_generator)
    
    token_generator =  tokens_from_file(file_path)
    seek_token( token_generator, 'solid')
    print ('solid name: %s' % next(token_generator) )
    
    while(1):
        seek_token( token_generator, 'facet')
        facet = read_facet(token_generator)
        # can we continue and skip triangles on the plane?
        yield(facet)
        
def read_facet(token_generator ):

    normal = ()
    v1 = ()
    v2 = ()
    v3 = ()
    
    if next(token_generator) != 'normal':
        print ('expected normal')
        
    x = float(next(token_generator))
    y = float(next(token_generator))
    z = float(next(token_generator))
    normal = (x,y,z)
        
    if next(token_generator) != 'outer':
        print ('expected outer')
    
    if next(token_generator) != 'loop':
        print ('expected loop')
    
    if next(token_generator) != 'vertex':
        print ('expected vertex')
    
    x = float(next(token_generator))
    y = float(next(token_generator))
    z = float(next(token_generator))           
    v0 = (x,y,z)

    if next(token_generator) != 'vertex':
        print ('expected vertex')
    
    x = float(next(token_generator))
    y = float(next(token_generator))
    z = float(next(token_generator))           
    v1 = (x,y,z)    
    
    if next(token_generator) != 'vertex':
        print ('expected vertex')
    
    x = float(next(token_generator))
    y = float(next(token_generator))
    z = float(next(token_generator))           
    v2 = (x,y,z)
    
    if next(token_generator) != 'endloop':
        print ('expected endloop')
    
    if next(token_generator) != 'endfacet':
        print ('expected endfacet')
    
    return (normal, v0,v1,v2) 


    
import unittest
class Testing(unittest.TestCase):

          
    def test_bunny(self):
        start_time = time()
        facet_generator = facets_from_file('./bunny.stl')
        
        i = 0
        try:
            while 1:
                i += 1;
                f = next(facet_generator)
                
        except StopIteration:
            pass
        
        print("%d facets" % i)
        elapsed = time() - start_time
        print ("File read in %s sec" % (elapsed) )        
        self.assertEqual(69665, i)                

if __name__ == '__main__':
    unittest.main()
    
        
