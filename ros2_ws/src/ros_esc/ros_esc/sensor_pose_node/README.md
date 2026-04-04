# Node Description:

The purpose of this node is to calculate the transformation matrices describing the position and orientation of sensors attached to rotating frames with respect to some global reference frame. The sensor pose node uses a forward kinematic method to calculate these transformation matrices requiring 'odom' data which contains position and orientation data of the vehicle's chassis with respect to the global reference frame, the angular position values of the rotating sensor frames, and additional information described in a sensor transform configuration file. This additional information includes the rotating sensor frame's rotation axis with respect to the vehicle chassis, the rotating sensor frame joint position with respect to the vehicle chassis, and a transform matrix specifying where the sensor is placed on the rotating frame with respect to the rotating sensor frame joint.

## ROS Communication:

Input Topic Subscriptions:

- Input Odom Topic: Used to collect Odometry messages that contain the position and orientation of the vehicle's footprint in the Gazebo environment.

- Input Encoder Topic: Used to collect StampedFloat64MultiArray messages which contain arrays of angles, denoting the angular position of rotating sensor frames.

- Input Timekeeper Topic: Used to collect Timekeeper messages which contain timekeeping information, this is used to create timestamps for output data.

Output Topic Publishing:

- Output Topic: This node publishes StampedTransformMultiArray messages containing the sensor transformation matrices to the output topic.

## Forward Kinematics:

A transformation matrix $T_{a,b}$ describes the transform from a coordinate frame {a} to a frame {b}. This matrix has the following form:

$$ T_{a,b} = \begin{pmatrix} R & p \\ 0 & 1 \end{pmatrix} = \begin{pmatrix} r_{11} & r_{12} & r_{13} & p_{x} \\ r_{21} & r_{22} & r_{23} & p_{y} \\ r_{31} & r_{32} & r_{33} & p_{z} \\ 0 & 0 & 0 & 1 \end{pmatrix} $$

Here, R denotes a rotation matrix which describes the orientation of frame {b} in frame {a}, and vector p denotes the position of the origin of frame {b} in the coordinates of frame {a}. Transformation matrices like this are used to describe position and orientation of one frame {b} with respect to another frame {a}. We will make use of them to describe the position of the sensor frame {sensor} with respect to a stationary odometry frame {odom}.

We will make use of the subscript cancellation rule shown below. Note $T_{a,b}$ describes frame {b} in frame {a}, and $T_{b,c}$ describes frame {c} in frame {b}, thus to describe frame {c} in frame {a}, one simply has to do the multiplication of the transformation matrices in the order shown below.

$$ T_{a,b} * T_{b,c} = T_{a,c} $$

This node uses the following forward kinematic equation to calculate sensor position:
$$ T_{odom,sensor}  =  T_{odom,vehicle}  *  T_{vehicle,r\_ joint}  *  T_{r\_ joint,sensor} $$

![Visualization of transformation matrices for a turtlebot vehicle](/ros_esc/sensor_pose_node/transform_matrices.png)

First, the odometry information is used to calculate the pose of the vehicle's footprint frame w.r.t. the fixed odom frame (for a turtlebot, this is set up in the robot's URDF file in the differential drive plugin, other vehicles making use of this package will have to set up something similar). With this, the transformation matrix $T_{odom,vehcile}$ can be created. Note this matrix changes with time, as the robot moves, this matrix gets updated with the odom callback. The odom information contains the vehicle position (px, py, pz) as well as quaternion angles (qw, qx, qy, qz). The position vector can be directly inserted into a transformation matrix, and the quaternion angles can be converted into a rotation matrix. See eqn (7b) from [reference link](https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html).

$$ T_{odom,vehicle} = \begin{pmatrix} 1-2*q_y**2-2*q_z**2 & 2*q_x*q_y-2*q_w*q_z & 2*q_x*q_z+2*q_w*q_y & p_x \\ 2*q_x*q_y+2*q_w*q_z & 1-2*q_x**2-2*q_z**2 & 2*q_y*q_z-2*q_w*q_x & p_y \\ 2*q_x*q_z-2*q_w*q_y & 2*q_y*q_z+2*q_w*q_x & 1-2*q_x**2-2*q_y**2 & p_z \\ 0 & 0 & 0 & 1 \end{pmatrix} $$

Second, the encoder information is used to calculate the transformation matrix $T_{vehicle,r_joint}$. This node constructs $T_{vehicle,r_joint}$ as a lambda function where the position portion of the T matrix is constant, however the rotation matrix portion of T gets updated with every new encoder reading. Note, that $T_{vehicle,r_joint}$ changes with time, as the frame rotates, this matrix gets updated with the encoder callback.

![Visualization of the encoder angle with a turtlebot vehicle](/ros_esc/sensor_pose_node/encoder_angle.png)

The rotation axis of this revolute joint and the position of this revolute joint $p = [pa,pb,pc]^T$ w.r.t. the vehicle's footprint are both specified from the json file. We can use equations (4b-e) [from this reference](https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html) to construct quaternion angles knowing the value of our angular position $\phi$. These equations are restated below.

$$ q_0 = \cos{\frac{\phi}{2}} $$
$$ q_1 = \hat{x}\sin{\frac{\phi}{2}} $$
$$ q_2 = \hat{y}\sin{\frac{\phi}{2}} $$
$$ q_3 = \hat{z}\sin{\frac{\phi}{2}} $$

We can then use these quaternion angles to construct the $T_{vehicle,r\_joint}$ transformation matrix using the equation below. See equation (7b) [from this reference](https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html) for more information.

$$ T_{r\_joint,sensor} = \begin{pmatrix} 1-2q_2^2-2q_3^2 & 2q_1q_2 - 2q_0q_3 & 2q_1q_3 + 2q_0q_2 & pa \\ 2q_1q_2 + 2q_0q_3 & 1-2q_1^2-2q_3^2 & 2q_2q_3 - 2q_0q_2 & pb \\ 2q_1q_3 - 2q_0q_2 & 2q_2q_3 + 2q_0q_1 & 1-2q_1^2-2q_2^2 & pc \\ 0 & 0 & 0 & 1 $$

Third, the $T_{r\_ joint,sensor}$ transformation matrix is taken directly from the json configuration file, where $p = [px,py,pz]^T$ is sensor position with respect to the revolute joint. Note this matrix does not change with time.

$$ T_{r\_ joint,sensor} = \begin{pmatrix} 1 & 0 & 0 & px \\ 0 & 1 & 0 & py \\ 0 & 0 & 1 & pz \\ 0 & 0 & 0 & 1 \end{pmatrix} $$

## Example Configuration File:

This configuration file was made to describe a vehicle mounted with three rotating sensor frames. More config files are contained in the [transform config files](/ros_esc/sensor_pose_node/transform_config_files) directory.

```
{
    "rotating_frame_one":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_objects/transform_objects.py",
        "object_name": "Transform_Odom_To_Sensor_Pose",
        "params":{
            "joint_position": [0, 0, 0.325],
            "rotation_axis": [0, 0, 1],
            "sensor_transform": [
                [1, 0, 0, 0.25],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        }
    },

    "rotating_frame_two":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_objects/transform_objects.py",
        "object_name": "Transform_Odom_To_Sensor_Pose",
        "params":{
            "joint_position": [0, 0.325, 0],
            "rotation_axis": [0, 1, 0],
            "sensor_transform": [
                [1, 0, 0, 0.25],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        }
    },

    "rotating_frame_three":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_objects/transform_objects.py",
        "object_name": "Transform_Odom_To_Sensor_Pose",
        "params":{
            "joint_position": [0, 0.325, 0],
            "rotation_axis": [0, 1, 0],
            "sensor_transform": [
                [1, 0, 0, 0.25],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        }
    }
}
```

Please note that each rotating sensor frame is configured with a unique transform object described in this configuration file. More information on these parameters can be found in documentation for this transform object.

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc sensor_pose_node {input_odom_topic} {input_encoder_topic} {input_timekeeper_topic} {output_topic} {transform_config_filepath}
```
