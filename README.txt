Instructions


The values for the screen width, height, resolution, and camera offset from the center of the screen must be measured. Update the values in the FaceTracker and VirtualWindow files. 

You will have to measure your camera's field of view horizontally and vertically. I measured by using holding up a protractor flat to the webcam while looking at any webcam viewer app and finding the furthest angle something was still visible. For most webcams these values change with resolution, so make sure you measure it while it is running at the resolution you will be using. My webcam had a much wider field of view at its highest resolution.  The resolution and field of view values must be updated in the FaceTracker file.

The webcam is assigned in the main VirtualWindow file, by changing the "source" argument of the "def threadVirtualWindow(source=0)". For most users it will be 0 unless you have more than one webcam.
In the VideoGetHD file, you must assign the x/y resolution of the webcam in the "self.stream.set(3, 1280)" and "self.stream.set(4, 720)".

Finally an appropriate "userHead" value must be determined by measuring the distance from the user's eyes to the webcam with a tape measure, and adjusting the value until the distance the program outputs is correct. In the FaceTracker file there's a "print(distance)" that should be uncommented to aid with this process. Update the value of userHead in the beginning of the FaceTracker file until it's correct.

Once all that is complete you can place any Obj file (along with its MTL file) in the program folder and load it by changing "obj = OBJ('samples.obj', swapyz=True)" in the main VirtualWindow file and running the program.
The object coordinate space is as follows: When you're looking at the screen, positive X is left, positive Y is down, and positive Z is towards the user, and all values are in inches. When creating files for display it's usually best to keep Z values negative, or not too high positive.


