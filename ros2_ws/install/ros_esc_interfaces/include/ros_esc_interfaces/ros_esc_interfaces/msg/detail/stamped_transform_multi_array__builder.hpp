// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_esc_interfaces:msg/StampedTransformMultiArray.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__BUILDER_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_esc_interfaces
{

namespace msg
{

namespace builder
{

class Init_StampedTransformMultiArray_transform_array
{
public:
  explicit Init_StampedTransformMultiArray_transform_array(::ros_esc_interfaces::msg::StampedTransformMultiArray & msg)
  : msg_(msg)
  {}
  ::ros_esc_interfaces::msg::StampedTransformMultiArray transform_array(::ros_esc_interfaces::msg::StampedTransformMultiArray::_transform_array_type arg)
  {
    msg_.transform_array = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedTransformMultiArray msg_;
};

class Init_StampedTransformMultiArray_timestamp
{
public:
  explicit Init_StampedTransformMultiArray_timestamp(::ros_esc_interfaces::msg::StampedTransformMultiArray & msg)
  : msg_(msg)
  {}
  Init_StampedTransformMultiArray_transform_array timestamp(::ros_esc_interfaces::msg::StampedTransformMultiArray::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_StampedTransformMultiArray_transform_array(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedTransformMultiArray msg_;
};

class Init_StampedTransformMultiArray_header
{
public:
  Init_StampedTransformMultiArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StampedTransformMultiArray_timestamp header(::ros_esc_interfaces::msg::StampedTransformMultiArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_StampedTransformMultiArray_timestamp(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedTransformMultiArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_esc_interfaces::msg::StampedTransformMultiArray>()
{
  return ros_esc_interfaces::msg::builder::Init_StampedTransformMultiArray_header();
}

}  // namespace ros_esc_interfaces

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__BUILDER_HPP_
