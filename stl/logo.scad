

module left()
{
	rotate([0,0,180])linear_extrude(height=3)import("python_logo_2_half.dxf");
	translate([0,0,2])cube([20,10,1],center=true);
}

module right()
{
translate([-4.5,-0.25,0])linear_extrude(height=3)import("python_logo_2_half.dxf");
}

right();
//left();