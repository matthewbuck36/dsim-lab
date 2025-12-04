// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_esc_interfaces:msg/StampedFloat64MultiArray.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64_MULTI_ARRAY__BUILDER_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64_MULTI_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_esc_interfaces/msg/detail/stamped_float64_multi_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_esc_interfaces
{

namespace msg
{

namespace builder
{

class Init_StampedFloat64MultiArray_data
{
public:
  explicit Init_StampedFloat64MultiArray_data(::ros_esc_interfaces::msg::StampedFloat64MultiArray & msg)
  : msg_(msg)
  {}
  ::ros_esc_interfaces::msg::StampedFloat64MultiArray data(::ros_esc_interfaces::msg::StampedFloat64MultiArray::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedFloat64MultiArray msg_;
};

class Init_StampedFloat64MultiArray_timestamp
{
public:
  explicit Init_StampedFloat64MultiArray_timestamp(::ros_esc_interfaces::msg::StampedFloat64MultiArray & msg)
  : msg_(msg)
  {}
  Init_StampedFloat64MultiArray_data timestamp(::ros_esc_interfaces::msg::StampedFloat64MultiArray::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_StampedFloat64MultiArray_data(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedFloat64MultiArray msg_;
};

class Init_StampedFloat64MultiArray_header
{
public:
  Init_StampedFloat64MultiArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StampedFloat64MultiArray_timestamp header(::ros_esc_interfaces::msg::StampedFloat64MultiArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_StampedFloat64MultiArray_timestamp(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedFloat64MultiArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_esc_interfaces::msg::StampedFloat64MultiArray>()
{
  return ros_esc_interfaces::msg::builder::Init_StampedFloat64MultiArray_header();
}

}  // namespace ros_esc_interfaces

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64_MULTI_ARRAY__BUILDER_HPP_
