#demo.py

import pyopencl as cl
import numpy
import time


def segment_segment_intersection(  p0_x,  p0_y,
                                  p1_x,  p1_y,
                                  p2_x,  p2_y,
                                  p3_x,  p3_y):
    
    # double s1_x, s1_y, s2_x, s2_y;
    s1_x = p1_x - p0_x;
    s1_y = p1_y - p0_y;
    s2_x = p3_x - p2_x;
    s2_y = p3_y - p2_y;    
    # double s, t;
    s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y);
    t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y);
    
    #int r;
    #r = (s >= 0 && s <= 1 && t >= 0 && t <= 1);
    r = (s >= 0 and s <= 1 and t >= 0 and t <= 1);
    
    i_x = p0_x + (t * s1_x);
    i_y = p0_y + (t * s1_y);
    
    return (r, i_x, i_y);


src = """
    
#pragma OPENCL EXTENSION cl_khr_fp64 : enable

#define scalar float
inline int segment_segment_intersection( scalar p0_x, scalar p0_y,
                             scalar p1_x, scalar p1_y,
                             scalar p2_x, scalar p2_y,
                             scalar p3_x, scalar p3_y,
                             scalar *i_x, scalar *i_y);
                             
                             





#define scalar float
inline int segment_segment_intersection( scalar p0_x, scalar p0_y,
                             scalar p1_x, scalar p1_y,
                             scalar p2_x, scalar p2_y,
                             scalar p3_x, scalar p3_y,
                             scalar *i_x, scalar *i_y)
{
    scalar s1_x, s1_y, s2_x, s2_y;
    s1_x = p1_x - p0_x;
    s1_y = p1_y - p0_y;
    s2_x = p3_x - p2_x;
    s2_y = p3_y - p2_y;

    scalar s, t;
    s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y);
    t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y);

    int r = (s >= 0 && s <= 1 && t >= 0 && t <= 1);
    
    *i_x = p0_x + (t * s1_x);
    *i_y = p0_y + (t * s1_y);
    
    return r;
}

__kernel void segment_segment_coordinates( __global const scalar *p0,
                                            __global const scalar *p1, 
                                            __global const scalar *p2, 
                                            __global const scalar *p3, 
                                            __global scalar *coordinates,
                                            __global int *intersections)
{
    int gid = get_global_id(0);
    
    scalar  x, y;    
    int collision;
    
    collision = segment_segment_intersection(p0[2*gid], p0[2*gid+1], 
                                             p1[2*gid], p1[2*gid+1], 
                                             p2[2*gid], p2[2*gid+1], 
                                             p3[2*gid], p3[2*gid+1], 
                                             &x, &y);
    coordinates[2 * gid]    = x;
    coordinates[2 * gid +1] = y;
    intersections[gid] = collision;
} 

"""


def openCl(p0, p1,p2,p3, intersections, coordinates):
    import pyopencl as cl
    
    platform = None
    for p in cl.get_platforms():
        if p.name.find("Apple") > -1:
            platform = p
    
    device = None
    for d  in platform.get_devices():
        if d.name.find("ATI") >-1:
            device = d
    ctx = cl.Context([device])     
    queue = cl.CommandQueue(ctx)
    
    print("OpenCL platform: %s" % platform.name)  
    print("OpenCL device: %s" % device.name) 

    mf = cl.mem_flags
    print ("\n")
    x = time.time()
    p0_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=p0)
    p1_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=p1)
    p2_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=p2)
    p3_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=p3)
    coordinates_buf = cl.Buffer(ctx, mf.WRITE_ONLY, coordinates.nbytes)
    intersections_buf = cl.Buffer(ctx, mf.WRITE_ONLY, intersections.nbytes)    
    
    prg = cl.Program(ctx, src).build()
    
    t = time.time()
    prg.segment_segment_coordinates(queue, [data_size], None, 
                                    p0_buf, p1_buf, p2_buf, p3_buf, 
                                    coordinates_buf, intersections_buf)
    
    cl.enqueue_copy(queue, coordinates, coordinates_buf)
    cl.enqueue_copy(queue, intersections, intersections_buf)
    return time.time() - t


data_size = 1024 * 512
print("Number of coordinatess:", data_size )
scalar = numpy.float32

p0 =  numpy.zeros(data_size *2).astype(scalar)
p1 =  numpy.zeros(data_size *2).astype(scalar)
p2 =  numpy.zeros(data_size *2).astype(scalar)
p3 =  numpy.zeros(data_size *2).astype(scalar)

coordinates = numpy.empty(data_size *2).astype(scalar)
intersections = numpy.empty(data_size).astype(numpy.int32)

print("Initializing data")

delta = 0.1
for i in range(data_size):
    ix = 2 *i
    iy = ix+1
    p0[ix] = -100
    p0[iy] = 0
    p1[ix] = 100
    p1[iy] = 0  
    p2[ix] = 0
    p2[iy] = -100 + i *delta
    p3[ix] = 0 
    p3[iy] = 100 + i *delta

    

print("\nperforming OpenCL calculations")


opencl_time = openCl(p0, p1,p2,p3, intersections, coordinates)

print intersections
print coordinates
print opencl_time

print("\nDoing it in python")
t = time.time()

for i in range(data_size):
    ix = i*2
    iy = ix+1
    r,x,y = segment_segment_intersection(p0[ix], p0[iy], 
                                         p1[ix], p1[iy], 
                                         p2[ix], p2[iy], 
                                         p3[ix], p3[iy])
    coordinates[ix] = x
    coordinates[iy] = y
    intersections[i] = r

python_time = time.time() - t
print intersections
print coordinates
print python_time

print( "Acceleration %s" % (python_time / opencl_time) )

