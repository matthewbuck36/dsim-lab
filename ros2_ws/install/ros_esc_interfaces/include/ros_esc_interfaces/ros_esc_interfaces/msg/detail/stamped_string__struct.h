// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from ros_esc_interfaces:msg/StampedString.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_STRING__STRUCT_H_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_STRING__STRUCT_H_

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
// Member 'data'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/StampedString in the package ros_esc_interfaces.
/**
  * This is simply a timestamped String message.
 */
typedef struct ros_esc_interfaces__msg__StampedString
{
  /// Header containing a description of what the data represents
  rosidl_runtime_c__String header;
  /// Timestamp of the message.
  double timestamp;
  /// The string data.
  rosidl_runtime_c__String data;
} ros_esc_interfaces__msg__StampedString;

// Struct for a sequence of ros_esc_interfaces__msg__StampedString.
typedef struct ros_esc_interfaces__msg__StampedString__Sequence
{
  ros_esc_interfaces__msg__StampedString * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} ros_esc_interfaces__msg__StampedString__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_STRING__STRUCT_H_
