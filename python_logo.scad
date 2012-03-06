module neg()
{
translate([29,0,0])cube([20,35,20], center=true);
translate([20,-30,0])cube([50,60,20], center=true);
translate([-5,-10,0])cylinder(r = 10, h=20,center=true);
}

module logo_05()
{
linear_extrude (height=5) import ("python05.dxf");

}

module logo()
{
linear_extrude (height=5) import ("python.dxf");
translate([0,0, 1])cube([45,31,2], center=true);
}

// translate([100,0,0])logo();

module dual_small()
{
	translate([5,0,0])rotate([0,0,180])logo_05();
}

module dual_big()
{
	logo_05();	
	translate([0,0, 2.5])cube([45,31,2], center=true);
}

dual_big();
dual_small();
