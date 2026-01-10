from pyquaternion import Quaternion
import numpy as np
def rotate_object(quaternion, axis, degrees):
    """
    Rotate using quaternions around a specified axis by a given number of degrees.
    """    
    angle = np.radians(degrees)    
    if axis == 'x':
        delta_rotation = Quaternion(axis=[1, 0, 0], angle=angle)
    elif axis == 'y':
        delta_rotation = Quaternion(axis=[0, 1, 0], angle=angle)
    elif axis == 'z':
        delta_rotation = Quaternion(axis=[0, 0, 1], angle=angle)
        # Update the quaternion representing the object's orientationreturn quaternion * delta_rotation  # Quaternion multiplication is non-commutative# Initial orientation (no rotation)
current_orientation = Quaternion()

# Rotate 30 degrees around y, then 45 degrees around the new x
current_orientation = rotate_object(current_orientation, 'y', 30)
current_orientation = rotate_object(current_orientation, 'x', 45)

print("Current Orientation Quaternion:", current_orientation)