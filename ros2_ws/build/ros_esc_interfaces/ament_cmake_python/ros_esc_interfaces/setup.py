from setuptools import find_packages
from setuptools import setup

setup(
    name='ros_esc_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('ros_esc_interfaces', 'ros_esc_interfaces.*')),
)
