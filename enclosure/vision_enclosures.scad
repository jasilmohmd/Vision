/*
  Vision enclosure prototypes -- millimetres, no external libraries.
  Select one part, F6 Render, then Export STL. "layout" is an overview.
  Typical component sizes are NOT measured hardware dimensions.
  Read README.md for deliberate corrections to the reference and print limits.
*/

/* [Output] */
part = "layout"; // [layout,camera_assembly,C1,C1_vertical,C2,C3,C4,P5,P6,P7_front,P7_back]
quality = 48;
preview_tilt = 0; // [-30:45]

/* [Measured components - replace these typical values] */
servo_l = 22.8;
servo_w = 12.2;
servo_below_tabs = 20;
servo_hole_pitch = 27.5;
servo_shaft_from_end = 6;
tilt_servo_projection = 8.5; // tab seating face to output face; measure!
tilt_horn_thickness = 2;
horn_length = 20; // hub centre to far tip, conservative interpretation
horn_width = 5;
horn_hub_d = 7;
horn_tie_positions = [10,16]; // replace with measured hole positions
post_d = 22;
pcb_w = 28;
pcb_h = 64;
pcb_t = 1.6;
lens_x = 0;
lens_from_pcb_top = 8; // PLACEHOLDER: measure!
usb_x = [-7.5,7.5]; // PLACEHOLDERS: centres from PCB centre
usb_depth = 12; // centre from outer front face; measure connector stack
perf_w = 30;
perf_h = 40;
perf_t = 1.6;
header_space = 10;
capacitor_space = 12;
breadboard_l = 47;
breadboard_w = 35;
breadboard_h = 8.5;
voice_usb_x = -23; // PLACEHOLDER in box coordinates
voice_usb_z = 16; // PLACEHOLDER above print bed
charger_usb_x = 27; // PLACEHOLDER
mic_d = 14;
mic_t = 2; // PLACEHOLDER: module excluding pins
mic_sound_x = 0; // PLACEHOLDER: offset of actual sound port
mic_sound_z = 0;
arm_d = 7;

/* [Fit and optional features] */
clearance = 0.4; // per side
wall = 2;
bottom_chamfer = 0.5;
lip_clearance = 0.3; // per side
clamp_interference = 0.3; // DIAMETRAL, verify with a test coupon
horn_pocket_depth = 1.5;
camera_hood = 0; // 0 for flat front-down bed contact; 1.5 adds outward hood
engrave_labels = true;
tilt_min = -30;
tilt_max = 45;

/* [Hidden] */
$fn = quality;
eps = 0.02;
m2_pilot = 1.8;
m2_clear = 2.4;
m3_pilot = 2.8;
m3_clear = 3.4;
servo_offset = servo_l/2-servo_shaft_from_end;
pan_bearing_id = max(30,2*sqrt(pow(servo_offset+servo_l/2+clearance,2)+pow(servo_w/2+clearance,2))+1);
pan_bearing_height = max(1,tilt_servo_projection+tilt_horn_thickness-horn_pocket_depth);
cam_w = max(pcb_w+2*clearance+8,perf_w+2*clearance+6)+2*wall;
cam_h = pcb_h+2*clearance+8+2*wall;
cam_front = wall+10+pcb_t+clearance;
cam_back = header_space+perf_t+capacitor_space+wall;
cam_depth = cam_front+cam_back;
tilt_depth = cam_depth/2;
boss_projection = 3;
case_across_bosses = cam_w+2*boss_projection;
tilt_side_gap = tilt_servo_projection+tilt_horn_thickness+1;
yoke_gap = case_across_bosses+2*tilt_side_gap;
yoke_t = 3;
yoke_w = max(50,yoke_gap+2*yoke_t+0.6);
yoke_d = max(30,2*(horn_length+clearance+2));
tilt_axis = max(48,sqrt(pow(cam_h/2,2)+pow(cam_depth/2,2))+3);
arm_h = max(60,tilt_axis+11);
cam_screws_x = cam_w/2-wall-2.5;
cam_screws_y = cam_h/2-wall-2.5;
voice_iw = breadboard_l+2*clearance+49;
voice_id = max(breadboard_w+2*clearance+8,25+17+4*clearance+6);
voice_w = voice_iw+2*wall;
voice_d = voice_id+2*wall;
voice_h = max(30,breadboard_h+20)+wall;
bb_x = -voice_iw/2+6+breadboard_l/2;
voice_sx = voice_w/2-wall-2.5;
voice_sy = voice_d/2-wall-2.5;
pod_d = 30;
pod_l = 52;
pod_r = pod_d/2;
pod_screw_x = 10.5;
pod_screw_y = 4;

assert(wall>=1.2 && clearance>=0 && lip_clearance>0);
assert(quality>=16);
assert(servo_shaft_from_end>0 && servo_shaft_from_end<servo_l);
assert(cam_back-wall>=header_space+perf_t+capacitor_space);
assert(abs(lens_x)+6<cam_w/2-wall);
assert(lens_from_pcb_top>6 && lens_from_pcb_top<pcb_h-6);
assert(arm_d>1 && arm_d<12);
assert(mic_d+0.6<22 && mic_t>0 && mic_t<=4);
assert(preview_tilt>=tilt_min && preview_tilt<=tilt_max);
assert(part=="layout" || part=="camera_assembly" || part=="C1" || part=="C1_vertical" || part=="C2" ||
       part=="C3" || part=="C4" || part=="P5" || part=="P6" ||
       part=="P7_front" || part=="P7_back","Unknown part selector");

// Rounded footprints have a true planar base. Offset maintains overall sizes.
module rounded2(w,d,r=2) {
    offset(r=r) square([w-2*r,d-2*r],center=true);
}
module rounded_box(w,d,h,r=2,ch=bottom_chamfer) {
    if(ch>0) {
        hull() {
            linear_extrude(eps) rounded2(w-2*ch,d-2*ch,max(r-ch,0.1));
            translate([0,0,ch]) linear_extrude(eps) rounded2(w,d,r);
        }
        translate([0,0,ch]) linear_extrude(h-ch) rounded2(w,d,r);
    } else linear_extrude(h) rounded2(w,d,r);
}
module drill_x(d,h) { rotate([0,90,0]) cylinder(d=d,h=h,center=true); }
module drill_y(d,h) { rotate([90,0,0]) cylinder(d=d,h=h,center=true); }
module hex_hole(af,h) { cylinder(d=af/cos(30),h=h,$fn=6); }
module screw_grid(x,y) { for(a=[-1,1],b=[-1,1]) translate([a*x,b*y,0]) children(); }
module frame(w,d,h,t=1.2,r=2) {
    difference() {
        rounded_box(w,d,h,r,0);
        translate([0,0,-eps]) rounded_box(w-2*t,d-2*t,h+2*eps,max(0.3,r-t),0);
    }
}
module countersink(hole=2.4,head=4.5,depth=1.1) {
    // Exterior face at z=0; countersink narrows inward into +Z.
    translate([0,0,-eps]) cylinder(d1=head,d2=hole,h=depth+eps);
}
module horn2() {
    circle(d=horn_hub_d+2*clearance);
    hull() {
        circle(d=horn_width+2*clearance);
        translate([horn_length-horn_width/2,0]) circle(d=horn_width+2*clearance);
    }
}
module horn_cut(depth) {
    linear_extrude(depth) horn2();
}

// C1: shaft centred on X=Y=0. Separate horizontal and vertical tube variants.
module collar() {
    ir=(post_d-clamp_interference)/2;
    rr=ir+4;
    difference() {
        union() {
            cylinder(r=rr,h=20);
            for(s=[-1,1]) translate([s*(ir*0.72+2),ir*0.88,10])
                cube([6,10,20],center=true);
        }
        translate([0,0,-eps]) cylinder(r=ir,h=20+2*eps);
        translate([0,0,-eps]) linear_extrude(20+2*eps)
            polygon([[0,0],[-rr*2,rr*2],[rr*2,rr*2]]);
        translate([0,ir*0.88+2,10]) drill_x(m3_clear,2*rr+20);
        translate([ir*0.72+2+3-2.5,ir*0.88+2,10])
            rotate([0,90,0]) hex_hole(5.6,3);
    }
}
module C1(vertical=false) {
    rr=(post_d-clamp_interference)/2+4;
    base_z=vertical?19:2*rr-1;
    cup_h=servo_below_tabs+4;
    cup_w=max(44,servo_l+2*clearance+14);
    cup_d=38;
    difference() {
        union() {
            if(vertical) {
                translate([0,-rr-cup_d/2-2,0]) rotate([0,0,180]) collar();
                translate([0,-cup_d/2-1,19]) cube([10,8,6],center=true);
            }
            else translate([-10,0,rr]) rotate([0,90,0]) collar();
            if(!vertical) translate([0,0,0]) rounded_box(20,10,3,1,0.5);
            translate([servo_offset,0,base_z]) rounded_box(cup_w,cup_d,cup_h,3);
            translate([0,0,base_z+cup_h-eps]) difference() {
                cylinder(d=pan_bearing_id+4,h=pan_bearing_height+eps);
                translate([0,0,-eps]) cylinder(d=pan_bearing_id,h=pan_bearing_height+3*eps);
            }
            // Tripod flange extends beside the tube, under an accessible top.
            translate([servo_offset+cup_w/2+5,0,base_z]) rounded_box(18,24,8,3);
        }
        translate([servo_offset,0,base_z+2])
            rounded_box(servo_l+2*clearance,servo_w+2*clearance,cup_h+3,0.6,0);
        for(s=[-1,1]) translate([servo_offset+s*servo_hole_pitch/2,0,base_z+cup_h-8])
            cylinder(d=m2_pilot,h=10);
        translate([servo_offset+cup_w/2,0,base_z+cup_h-1.5]) cube([12,4,3.1],center=true);
        translate([servo_offset+cup_w/2,0,base_z+6]) cube([12,6,4],center=true);
        translate([servo_offset+cup_w/2+7,0,base_z-eps]) {
            cylinder(d=6.6,h=9);
            translate([0,0,2.4]) hex_hole(11.1+0.3,5.7);
        }
    }
}

// C2: central horn points along +Y; tilt servo is on left arm.
module C2() {
    ax=3+tilt_axis;
    difference() {
        union() {
            rounded_box(yoke_w,yoke_d,3,2);
            for(s=[-1,1]) translate([s*(yoke_gap/2+yoke_t/2),0,3-eps])
                rounded_box(yoke_t,25,arm_h,1,0);
            // Triangular gussets in front/rear corners.
            for(s=[-1,1],t=[-1,1]) hull() {
                translate([s*(yoke_gap/2+1.3),t*10,8]) cube([3,3,10],center=true);
                translate([s*(yoke_gap/2-3),t*10,3.4]) cube([3,3,0.8],center=true);
            }
            translate([yoke_gap/2-tilt_side_gap+1,0,ax]) rotate([0,90,0])
                cylinder(d=10,h=tilt_side_gap-1+eps);
        }
        translate([0,0,-eps]) rotate([0,0,90]) horn_cut(horn_pocket_depth+eps);
        translate([0,0,-eps]) cylinder(d=2.5,h=4);
        for(p=horn_tie_positions) translate([0,p,-eps]) cylinder(d=1.2,h=4);
        // Servo long dimension vertical; shaft offset is correctly applied.
        translate([-yoke_gap/2-1.5,0,ax-servo_offset])
            cube([8,servo_w+2*clearance,servo_l+2*clearance],center=true);
        for(s=[-1,1]) translate([-yoke_gap/2-1.5,0,ax-servo_offset+s*servo_hole_pitch/2])
            drill_x(m2_pilot,8);
        translate([yoke_gap/2,0,ax]) drill_x(m3_clear,2*(tilt_side_gap+yoke_t+2));
        translate([-yoke_gap/2-1.5,9,3+arm_h-2]) cube([8,6,6],center=true);
        // Trim gussets flush with the print bed.
        translate([0,0,-50]) cube([200,200,100],center=true);
    }
}

module camera_shell_base(depth) {
    difference() {
        rounded_box(cam_w,cam_h,depth,2);
        translate([0,0,wall]) rounded_box(cam_w-2*wall,cam_h-2*wall,depth+2,1,0);
    }
}
// Boss frames extend aft from C3 because the tilt axis lies behind its rim.
module camera_hinge(s) {
    translate([s*(cam_w/2+boss_projection/2-eps),0,0])
        rounded_box(boss_projection+2*eps,2*horn_length+8,tilt_depth+6,1,0);
}
module C3() {
    difference() {
        union() {
            camera_shell_base(cam_front);
            screw_grid(cam_screws_x,cam_screws_y) rounded_box(5.2,5.2,cam_front,0.5,0);
            // Edge ledges finish at the specified 12 mm PCB front plane.
            for(s=[-1,1]) translate([s*(pcb_w/2+clearance),0,wall])
                rounded_box(3,pcb_h-8,10,0.6,0);
            translate([0,0,cam_front-eps]) frame(cam_w-2*wall,cam_h-2*wall,1+eps,1.2,1);
            for(s=[-1,1]) camera_hinge(s);
            if(camera_hood>0) translate([lens_x,pcb_h/2-lens_from_pcb_top,-camera_hood])
                difference() { cylinder(d=17,h=camera_hood+eps); cylinder(d=12,h=camera_hood+2*eps); }
        }
        translate([lens_x,pcb_h/2-lens_from_pcb_top,-camera_hood-eps]) {
            cylinder(d=12,h=wall+camera_hood+2*eps);
            cylinder(d1=14,d2=12,h=1);
        }
        for(x=usb_x) translate([x,-cam_h/2,usb_depth]) rotate([90,0,0])
            linear_extrude(2*wall+2,center=true) rounded2(13,8,1.5);
        screw_grid(cam_screws_x,cam_screws_y) translate([0,0,cam_front-8])
            cylinder(d=m2_pilot,h=10);
        translate([-cam_w/2-boss_projection-eps,0,tilt_depth]) rotate([0,90,0])
            horn_cut(horn_pocket_depth+eps);
        translate([-cam_w/2-boss_projection/2,0,tilt_depth]) drill_x(2.5,8);
        for(p=horn_tie_positions) translate([-cam_w/2-boss_projection/2,0,tilt_depth-p])
            drill_x(1.2,8);
        translate([cam_w/2,0,tilt_depth]) drill_x(m3_pilot,10);
        if(engrave_labels) translate([0,-12,-eps]) mirror([1,0,0]) linear_extrude(0.6+eps)
            text("CAM",size=6,halign="center",valign="center");
    }
}

// C4 print back-down. Its open rim mates to C3 after a 180 degree rotation.
module C4() {
    perf_z=wall+capacitor_space;
    difference() {
        union() {
            camera_shell_base(cam_back);
            screw_grid(cam_screws_x,cam_screws_y) cylinder(d=5,h=cam_back);
            // Two pairs of rails form slots of board thickness + fit clearance.
            for(s=[-1,1],z=[perf_z-1.2,perf_z+perf_t+clearance])
                translate([s*(perf_w/2+clearance),0,z]) rounded_box(4,perf_h,1.2,0.5,0);
            // Rail supports join both slot faces to the side walls.
            for(s=[-1,1]) translate([s*(cam_w/2-wall-1.5),0,wall-eps])
                rounded_box(3.1,perf_h,perf_z+perf_t+clearance+1.2-wall,0.5,0);
            // Strain-relief bridge anchored to the back floor.
            for(s=[-1,1]) translate([s*6,-cam_h/2+7,wall-eps]) cube([3,3,5]);
            translate([-6,-cam_h/2+7,6]) cube([15,3,2]);
        }
        translate([0,0,cam_back-1.2]) frame(cam_w-2*wall+2*lip_clearance,
            cam_h-2*wall+2*lip_clearance,1.3,1.2+2*lip_clearance,1+lip_clearance);
        screw_grid(cam_screws_x,cam_screws_y) {
            translate([0,0,-eps]) cylinder(d=m2_clear,h=cam_back+1);
            countersink();
        }
        for(x=[-9,-3,3,9]) translate([x,0,-eps]) rounded_box(2,15,wall+2*eps,0.8,0);
        translate([0,-cam_h/2,cam_back-3.5]) cube([10,8,9],center=true);
        for(x=usb_x) translate([-x,-cam_h/2,cam_depth-usb_depth]) rotate([90,0,0])
            linear_extrude(2*wall+2,center=true) rounded2(13,8,1.5);
        translate([0,-cam_h/2,cam_back]) drill_y(6,8);
    }
}

module P5() {
    difference() {
        union() {
            difference() {
                rounded_box(voice_w,voice_d,voice_h,2);
                translate([0,0,wall]) rounded_box(voice_iw,voice_id,voice_h+1,1,0);
            }
            screw_grid(voice_sx,voice_sy) cylinder(d=5,h=voice_h);
            // Locating frame around breadboard; separate battery bay on right.
            translate([bb_x,0,wall-eps]) frame(breadboard_l+2*clearance+3,
                breadboard_w+2*clearance+3,1.5+eps,1.5,1);
            translate([bb_x+breadboard_l/2+clearance+3,-17.5,wall-eps]) cube([1.5,35,9]);
            // External strap ears keep straps outside the electronics cavity.
            for(x=[-28,28]) translate([x,voice_d/2+3,0]) rounded_box(32,10,5,2);
        }
        screw_grid(voice_sx,voice_sy) translate([0,0,voice_h-9]) cylinder(d=m2_pilot,h=10);
        translate([voice_usb_x,-voice_d/2,voice_usb_z]) rotate([90,0,0])
            linear_extrude(8,center=true) rounded2(12,7,1.5);
        translate([charger_usb_x,-voice_d/2,7]) rotate([90,0,0])
            linear_extrude(8,center=true) rounded2(6,4,1);
        translate([-voice_w/2,0,voice_h-8]) rotate([0,90,0])
            linear_extrude(8,center=true) rounded2(6,10,1.5);
        for(s=[-1,1],x=[-10,10]) translate([x,s*voice_d/2,voice_h-9])
            cube([15,8,2],center=true);
        for(x=[-28,28]) translate([x,voice_d/2+4,-eps]) rounded_box(26,3,6,1,0);
        if(engrave_labels) translate([bb_x,0,-eps]) mirror([1,0,0]) linear_extrude(0.6+eps)
            text("VOICE",size=6,halign="center",valign="center");
    }
}
module P6() {
    difference() {
        union() {
            rounded_box(voice_w,voice_d,2,2);
            translate([0,0,2-eps]) frame(voice_iw-2*lip_clearance,
                voice_id-2*lip_clearance,1.2+eps,1.2,1);
        }
        screw_grid(voice_sx,voice_sy) {
            translate([0,0,-eps]) cylinder(d=m2_clear,h=5);
            countersink();
            // Locating frame relief over the box screw towers.
            translate([0,0,2]) cylinder(d=5+2*lip_clearance,h=2);
        }
        for(x=[bb_x-9:6:bb_x+9],y=[-9:6:9]) translate([x,y,-eps]) cylinder(d=2,h=4);
    }
}

module capsule(d,len) {
    hull() for(s=[-1,1]) translate([0,s*(len-d)/2,0]) sphere(d=d);
}
module pod_whole() {
    difference() {
        union() {
            capsule(pod_d,pod_l);
            // Angled light pocket, roof is a 1 mm solid diffuser.
            translate([0,0,9]) rotate([30,0,0]) rounded_box(16,18,5,3,0);
        }
        intersection() {
            capsule(pod_d-2*wall,pod_l-2*wall);
            translate([-30,-pod_l/2+8,-30]) cube([60,pod_l-22,60]);
        }
        // Microphone receiver and rear header space; source port may be offset.
        translate([0,-pod_l/2+6+mic_t/2,0]) drill_y(mic_d+0.6,mic_t+2*clearance);
        translate([0,-pod_l/2+10+mic_t/2,0]) drill_y(mic_d-1.6,7);
        translate([mic_sound_x,-pod_l/2+3,mic_sound_z]) drill_y(3,8);
        translate([0,-pod_l/2+1.5,0]) drill_y(12,3.1);
        // 12 mm deep arm socket, with separate through-wire passage.
        translate([0,pod_l/2-6+eps,0]) drill_y(arm_d-0.2,12+2*eps);
        translate([0,pod_l/2-15,0]) drill_y(6,12);
        // Zip tie passes through two slots around the arm socket.
        for(s=[-1,1]) translate([s*(arm_d/2+2),pod_l/2-7,0]) cube([2,3,16],center=true);
        // Pocket underside connects to the cavity, leaving roof at local z=4..5.
        translate([0,0,9]) rotate([30,0,0]) translate([0,0,-4]) rounded_box(10+0.8,12+0.8,8,1,0);
        // Trim the original capsule above this plane too, so the diffuser is 1 mm.
        translate([0,0,9]) rotate([30,0,0]) translate([0,0,5]) rounded_box(16,18,30,3,0);
    }
    // Add the membrane after hollowing: the main cavity must not cut it away.
    translate([0,0,9]) rotate([30,0,0]) translate([0,0,4]) rounded_box(14,16,1,2,0);
}
module pod_half(front=true) {
    // Half with NeoPixel = front; lower half is flipped onto its split plane.
    difference() {
        union() {
            intersection() {
                if(front) pod_whole(); else rotate([0,180,0]) pod_whole();
                translate([-40,-40,0]) cube([80,80,40]);
            }
            for(s=[-1,1]) translate([s*pod_screw_x,pod_screw_y,0]) cylinder(d=6,h=7);
        }
        for(s=[-1,1]) translate([s*pod_screw_x,pod_screw_y,-eps]) {
            cylinder(d=front?m2_clear:m2_pilot,h=front?30:6);
            if(front) translate([0,0,7]) cylinder(d=4.5,h=25);
        }
    }
}

module camera_assembly() {
    pan_top=2*((post_d-clamp_interference)/2+4)-1+servo_below_tabs+4+pan_bearing_height;
    color("SlateGray") C1();
    translate([0,0,pan_top]) {
        color("SteelBlue") C2();
        translate([0,0,3+tilt_axis]) rotate([preview_tilt,0,0])
            translate([0,tilt_depth,0]) rotate([90,0,0]) {
                color("DarkOrange") C3();
                color("Orange") translate([0,0,cam_depth]) rotate([0,180,0]) C4();
            }
    }
}
module selected() {
    if(part=="C1") C1();
    else if(part=="C1_vertical") C1(true);
    else if(part=="C2") C2();
    else if(part=="C3") translate([0,0,camera_hood]) C3();
    else if(part=="C4") C4();
    else if(part=="P5") P5();
    else if(part=="P6") P6();
    else if(part=="P7_front") pod_half(true);
    else if(part=="P7_back") pod_half(false);
    else if(part=="camera_assembly") camera_assembly();
    else {
        translate([-95,70,0]) color("SlateGray") C1();
        translate([0,70,0]) color("SteelBlue") C2();
        translate([80,75,camera_hood]) color("DarkOrange") C3();
        translate([140,75,0]) color("Orange") C4();
        translate([-85,-30,0]) color("SeaGreen") P5();
        translate([30,-30,0]) color("MediumSeaGreen") P6();
        translate([110,-30,0]) color("Ivory") pod_half(true);
        translate([155,-30,0]) color("Wheat") pod_half(false);
    }
}
selected();
echo(camera_outer=[cam_w,cam_h,cam_depth],yoke_gap=yoke_gap,tilt_axis_above_plate=tilt_axis);
echo(voice_internal=[voice_iw,voice_id,voice_h-wall]);
echo("PROTOTYPE: measure components and test joint motion before full printing.");
