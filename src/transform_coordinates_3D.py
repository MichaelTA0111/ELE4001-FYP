import numpy as np

from pytransform3d.rotations import norm_vector, perpendicular_to_vectors, matrix_from_axis_angle
from pytransform3d.transformations import transform_from, invert_transform, vector_to_point
from pytransform3d.transform_manager import TransformManager


# Attempting to follow the relevant parts of this tutorial - https://alexanderfabisch.github.io/pytransform.html


def main():
    # Step 1 - Build motion capture coordinate system
    object_marker1_2_mocap = np.array([425, 327, 481])  # Pos 2.1
    object_marker2_2_mocap = np.array([423, 945, 476])  # Pos 4.1
    object_marker3_2_mocap = np.array([366, 251, 409])  # Pos 2.5
    another_marker_2_mocap = np.array([575, 631, 411])  # Pos 3.3

    obj_y = norm_vector(object_marker2_2_mocap - object_marker1_2_mocap)
    obj_z = norm_vector(object_marker3_2_mocap - object_marker1_2_mocap)
    obj_x = perpendicular_to_vectors(obj_y, obj_z)
    obj_z = perpendicular_to_vectors(obj_x, obj_y)

    R = np.vstack((obj_x, obj_y, obj_z)).T

    object2mocap = transform_from(R=R, p=object_marker1_2_mocap)
    print(object2mocap)

    print(object2mocap.dot(np.array([1, 0, 0, 1])))

    mocap2object = invert_transform(object2mocap)
    print(mocap2object)

    # Alternative method of getting mocap2object
    tm = TransformManager()
    tm.add_transform("object", "mocap", object2mocap)
    mocap2object = tm.get_transform("mocap", "object")
    print(mocap2object)

    another_marker2object = mocap2object.dot(vector_to_point(another_marker_2_mocap))
    print(another_marker2object)

    # Step 2 - Map to robot coordinate system
    detected_object2object = transform_from(
        R=matrix_from_axis_angle(1, np.pi / 8.0),
        p=np.array([0.1, 0.05, -0.05]))
    tm.add_transform("detected_object", "object", detected_object2object)


if __name__ == '__main__':
    main()
