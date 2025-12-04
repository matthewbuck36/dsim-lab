// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from ros_esc_interfaces:msg/StampedTransformMultiArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__rosidl_typesupport_introspection_c.h"
#include "ros_esc_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__functions.h"
#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__struct.h"


// Include directives for member types
// Member `header`
#include "rosidl_runtime_c/string_functions.h"
// Member `transform_array`
#include "geometry_msgs/msg/transform.h"
// Member `transform_array`
#include "geometry_msgs/msg/detail/transform__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  ros_esc_interfaces__msg__StampedTransformMultiArray__init(message_memory);
}

void ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_fini_function(void * message_memory)
{
  ros_esc_interfaces__msg__StampedTransformMultiArray__fini(message_memory);
}

size_t ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__size_function__StampedTransformMultiArray__transform_array(
  const void * untyped_member)
{
  const geometry_msgs__msg__Transform__Sequence * member =
    (const geometry_msgs__msg__Transform__Sequence *)(untyped_member);
  return member->size;
}

const void * ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__get_const_function__StampedTransformMultiArray__transform_array(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Transform__Sequence * member =
    (const geometry_msgs__msg__Transform__Sequence *)(untyped_member);
  return &member->data[index];
}

void * ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__get_function__StampedTransformMultiArray__transform_array(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Transform__Sequence * member =
    (geometry_msgs__msg__Transform__Sequence *)(untyped_member);
  return &member->data[index];
}

void ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__fetch_function__StampedTransformMultiArray__transform_array(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Transform * item =
    ((const geometry_msgs__msg__Transform *)
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__get_const_function__StampedTransformMultiArray__transform_array(untyped_member, index));
  geometry_msgs__msg__Transform * value =
    (geometry_msgs__msg__Transform *)(untyped_value);
  *value = *item;
}

void ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__assign_function__StampedTransformMultiArray__transform_array(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Transform * item =
    ((geometry_msgs__msg__Transform *)
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__get_function__StampedTransformMultiArray__transform_array(untyped_member, index));
  const geometry_msgs__msg__Transform * value =
    (const geometry_msgs__msg__Transform *)(untyped_value);
  *item = *value;
}

bool ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__resize_function__StampedTransformMultiArray__transform_array(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Transform__Sequence * member =
    (geometry_msgs__msg__Transform__Sequence *)(untyped_member);
  geometry_msgs__msg__Transform__Sequence__fini(member);
  return geometry_msgs__msg__Transform__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_member_array[3] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_esc_interfaces__msg__StampedTransformMultiArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "timestamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_esc_interfaces__msg__StampedTransformMultiArray, timestamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "transform_array",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_esc_interfaces__msg__StampedTransformMultiArray, transform_array),  // bytes offset in struct
    NULL,  // default value
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__size_function__StampedTransformMultiArray__transform_array,  // size() function pointer
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__get_const_function__StampedTransformMultiArray__transform_array,  // get_const(index) function pointer
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__get_function__StampedTransformMultiArray__transform_array,  // get(index) function pointer
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__fetch_function__StampedTransformMultiArray__transform_array,  // fetch(index, &value) function pointer
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__assign_function__StampedTransformMultiArray__transform_array,  // assign(index, value) function pointer
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__resize_function__StampedTransformMultiArray__transform_array  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_members = {
  "ros_esc_interfaces__msg",  // message namespace
  "StampedTransformMultiArray",  // message name
  3,  // number of fields
  sizeof(ros_esc_interfaces__msg__StampedTransformMultiArray),
  ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_member_array,  // message members
  ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_init_function,  // function to initialize message memory (memory has to be allocated)
  ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_type_support_handle = {
  0,
  &ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_ros_esc_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, ros_esc_interfaces, msg, StampedTransformMultiArray)() {
  ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Transform)();
  if (!ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_type_support_handle.typesupport_identifier) {
    ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &ros_esc_interfaces__msg__StampedTransformMultiArray__rosidl_typesupport_introspection_c__StampedTransformMultiArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
