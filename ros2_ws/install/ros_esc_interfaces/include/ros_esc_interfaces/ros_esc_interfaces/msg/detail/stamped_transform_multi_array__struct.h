// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from ros_esc_interfaces:msg/StampedTransformMultiArray.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__STRUCT_H_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "rosidl_runtime_c/string.h"
// Member 'transform_array'
#include "geometry_msgs/msg/detail/transform__struct.h"

/// Struct defined in msg/StampedTransformMultiArray in the package ros_esc_interfaces.
/**
  * This message is used to broadcast transformation matrices
  * which contain the global position and orientation of sensors 
  * for other ROS nodes to reference.
 */
typedef struct ros_esc_interfaces__msg__StampedTransformMultiArray
{
  /// Header containing a description of what the data represents
  rosidl_runtime_c__String header;
  /// Timestamp of the message.
  double timestamp;
  /// Array of transformation matrices, each matrix
  /// represents the information for one individual sensor.
  geometry_msgs__msg__Transform__Sequence transform_array;
} ros_esc_interfaces__msg__StampedTransformMultiArray;

// Struct for a sequence of ros_esc_interfaces__msg__StampedTransformMultiArray.
typedef struct ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence
{
  ros_esc_interfaces__msg__StampedTransformMultiArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__STRUCT_H_
