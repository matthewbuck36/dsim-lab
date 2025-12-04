// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from ros_esc_interfaces:msg/StampedFloat64.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64__STRUCT_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__ros_esc_interfaces__msg__StampedFloat64 __attribute__((deprecated))
#else
# define DEPRECATED__ros_esc_interfaces__msg__StampedFloat64 __declspec(deprecated)
#endif

namespace ros_esc_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct StampedFloat64_
{
  using Type = StampedFloat64_<ContainerAllocator>;

  explicit StampedFloat64_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->header = "";
      this->timestamp = 0.0;
      this->data = 0.0;
    }
  }

  explicit StampedFloat64_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->header = "";
      this->timestamp = 0.0;
      this->data = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _header_type header;
  using _timestamp_type =
    double;
  _timestamp_type timestamp;
  using _data_type =
    double;
  _data_type data;

  // setters for named parameter idiom
  Type & set__header(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__timestamp(
    const double & _arg)
  {
    this->timestamp = _arg;
    return *this;
  }
  Type & set__data(
    const double & _arg)
  {
    this->data = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator> *;
  using ConstRawPtr =
    const ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__ros_esc_interfaces__msg__StampedFloat64
    std::shared_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__ros_esc_interfaces__msg__StampedFloat64
    std::shared_ptr<ros_esc_interfaces::msg::StampedFloat64_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const StampedFloat64_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->timestamp != other.timestamp) {
      return false;
    }
    if (this->data != other.data) {
      return false;
    }
    return true;
  }
  bool operator!=(const StampedFloat64_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct StampedFloat64_

// alias to use template instance with default allocator
using StampedFloat64 =
  ros_esc_interfaces::msg::StampedFloat64_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace ros_esc_interfaces

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64__STRUCT_HPP_
