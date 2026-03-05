from setuptools import find_packages, setup

package_name = 'coin_haptics_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mumbzzz',
    maintainer_email='mwhidby@g.ucla.edu',
    description='ROS 2 nodes for taxel-driven coin motor haptic feedback.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
		'tss_to_coin_motor_node = coin_haptics_ros2.tss_to_coin_motor_node:main',
		'coin_motor_serial_node = coin_haptics_ros2.coin_motor_serial_node:main',
        ],
    },
)
