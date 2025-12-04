// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from ros_esc_interfaces:msg/StampedTransformMultiArray.idl
// generated code does not contain a copyright notice
#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "rosidl_runtime_c/string_functions.h"
// Member `transform_array`
#include "geometry_msgs/msg/detail/transform__functions.h"

bool
ros_esc_interfaces__msg__StampedTransformMultiArray__init(ros_esc_interfaces__msg__StampedTransformMultiArray * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!rosidl_runtime_c__String__init(&msg->header)) {
    ros_esc_interfaces__msg__StampedTransformMultiArray__fini(msg);
    return false;
  }
  // timestamp
  // transform_array
  if (!geometry_msgs__msg__Transform__Sequence__init(&msg->transform_array, 0)) {
    ros_esc_interfaces__msg__StampedTransformMultiArray__fini(msg);
    return false;
  }
  return true;
}

void
ros_esc_interfaces__msg__StampedTransformMultiArray__fini(ros_esc_interfaces__msg__StampedTransformMultiArray * msg)
{
  if (!msg) {
    return;
  }
  // header
  rosidl_runtime_c__String__fini(&msg->header);
  // timestamp
  // transform_array
  geometry_msgs__msg__Transform__Sequence__fini(&msg->transform_array);
}

bool
ros_esc_interfaces__msg__StampedTransformMultiArray__are_equal(const ros_esc_interfaces__msg__StampedTransformMultiArray * lhs, const ros_esc_interfaces__msg__StampedTransformMultiArray * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // timestamp
  if (lhs->timestamp != rhs->timestamp) {
    return false;
  }
  // transform_array
  if (!geometry_msgs__msg__Transform__Sequence__are_equal(
      &(lhs->transform_array), &(rhs->transform_array)))
  {
    return false;
  }
  return true;
}

bool
ros_esc_interfaces__msg__StampedTransformMultiArray__copy(
  const ros_esc_interfaces__msg__StampedTransformMultiArray * input,
  ros_esc_interfaces__msg__StampedTransformMultiArray * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!rosidl_runtime_c__String__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // timestamp
  output->timestamp = input->timestamp;
  // transform_array
  if (!geometry_msgs__msg__Transform__Sequence__copy(
      &(input->transform_array), &(output->transform_array)))
  {
    return false;
  }
  return true;
}

ros_esc_interfaces__msg__StampedTransformMultiArray *
ros_esc_interfaces__msg__StampedTransformMultiArray__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  ros_esc_interfaces__msg__StampedTransformMultiArray * msg = (ros_esc_interfaces__msg__StampedTransformMultiArray *)allocator.allocate(sizeof(ros_esc_interfaces__msg__StampedTransformMultiArray), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(ros_esc_interfaces__msg__StampedTransformMultiArray));
  bool success = ros_esc_interfaces__msg__StampedTransformMultiArray__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
ros_esc_interfaces__msg__StampedTransformMultiArray__destroy(ros_esc_interfaces__msg__StampedTransformMultiArray * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    ros_esc_interfaces__msg__StampedTransformMultiArray__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__init(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  ros_esc_interfaces__msg__StampedTransformMultiArray * data = NULL;

  if (size) {
    data = (ros_esc_interfaces__msg__StampedTransformMultiArray *)allocator.zero_allocate(size, sizeof(ros_esc_interfaces__msg__StampedTransformMultiArray), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = ros_esc_interfaces__msg__StampedTransformMultiArray__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        ros_esc_interfaces__msg__StampedTransformMultiArray__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__fini(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      ros_esc_interfaces__msg__StampedTransformMultiArray__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence *
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array = (ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence *)allocator.allocate(sizeof(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__destroy(ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__are_equal(const ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * lhs, const ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!ros_esc_interfaces__msg__StampedTransformMultiArray__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence__copy(
  const ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * input,
  ros_esc_interfaces__msg__StampedTransformMultiArray__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(ros_esc_interfaces__msg__StampedTransformMultiArray);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    ros_esc_interfaces__msg__StampedTransformMultiArray * data =
      (ros_esc_interfaces__msg__StampedTransformMultiArray *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!ros_esc_interfaces__msg__StampedTransformMultiArray__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          ros_esc_interfaces__msg__StampedTransformMultiArray__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!ros_esc_interfaces__msg__StampedTransformMultiArray__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
