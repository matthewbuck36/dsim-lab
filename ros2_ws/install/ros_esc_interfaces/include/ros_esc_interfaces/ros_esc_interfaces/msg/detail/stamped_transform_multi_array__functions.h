// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from ros_esc_interfaces:msg/StampedTransformMultiArray.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__FUNCTIONS_H_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "ros_esc_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__struct.h"

/// Initialize msg/StampedTransformMultiArray message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * ros_esc_interfaces__msg__StampedTransformMultiArray
 * )) before or use
 * ros_esc_interfaces__msg__StampedTransformMultiArray__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
bool
ros_esc_interfaces__msg__StampedTransformMultiArray__init(ros_esc_interfaces__msg__StampedTransformMultiArray * msg);

/// Finalize msg/StampedTransformMultiArray message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
void
ros_esc_interfaces__msg__StampedTransformMultiArray__fini(ros_esc_interfaces__msg__StampedTransformMultiArray * msg);

/// Create msg/StampedTransformMultiArray message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * ros_esc_interfaces__msg__StampedTransformMultiArray__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
ros_esc_interfaces__msg__StampedTransformMultiArray *
ros_esc_interfaces__msg__StampedTransformMultiArray__create();

/// Destroy msg/StampedTransformMultiArray message.
/**
 * It calls
 * ros_esc_interfaces__msg__StampedTransformMultiArray__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
void
ros_esc_interfaces__msg__StampedTransformMultiArray__destroy(ros_esc_interfaces__msg__StampedTransformMultiArray * msg);

/// Check for msg/StampedTransformMultiArray message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
bool
ros_esc_interfaces__msg__StampedTransformMultiArray__are_equal(const ros_esc_interfaces__msg__StampedTransformMultiArray * lhs, const ros_esc_interfaces__msg__StampedTransformMultiArray * rhs);

/// Copy a msg/StampedTransformMultiArray message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
bool
ros_esc_interfaces__msg__StampedTransformMultiArray__copy(
  const ros_esc_interfaces__msg__StampedTransformMultiArray * input,
  ros_esc_interfaces__msg__StampedTransformMultiArray * output);

/// Initialize array of msg/StampedTransformMultiArray messages.
/**
 * It allocates the memory for the number of elements and calls
 * ros_esc_interfaces__msg__StampedTransformMultiArray__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
bool
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__init(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array, size_t size);

/// Finalize array of msg/StampedTransformMultiArray messages.
/**
 * It calls
 * ros_esc_interfaces__msg__StampedTransformMultiArray__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
void
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__fini(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array);

/// Create array of msg/StampedTransformMultiArray messages.
/**
 * It allocates the memory for the array and calls
 * ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence *
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__create(size_t size);

/// Destroy array of msg/StampedTransformMultiArray messages.
/**
 * It calls
 * ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
void
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__destroy(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array);

/// Check for msg/StampedTransformMultiArray message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
bool
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__are_equal(const ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * lhs, const ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * rhs);

/// Copy an array of msg/StampedTransformMultiArray messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_ros_esc_interfaces
bool
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__copy(
  const ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * input,
  ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__FUNCTIONS_H_
