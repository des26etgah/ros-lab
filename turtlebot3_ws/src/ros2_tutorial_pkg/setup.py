from setuptools import find_packages, setup

package_name = 'ros2_tutorial_pkg'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='Module 3: Publishers, Subscribers & Robot Motion Control',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'velocity_publisher = ros2_tutorial_pkg.velocity_publisher:main',
            'laser_subscriber   = ros2_tutorial_pkg.laser_subscriber:main',
            'square_driver      = ros2_tutorial_pkg.square_driver:main',
            'safe_navigator     = ros2_tutorial_pkg.safe_navigator:main',
            'plot_trajectory    = ros2_tutorial_pkg.plot_trajectory:main',
        ],
    },
)
