import os

import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    fishbot_bringup_dir = get_package_share_directory('fishbot_bringup')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')

    slam_params_file = os.path.join(
        fishbot_bringup_dir,
        'config',
        'slam_toolbox_mapping.yaml'
    )

    slam_toolbox = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_toolbox_dir, 'launch', 'online_sync_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'False',
            'slam_params_file': slam_params_file,
        }.items()
    )

    scan_filter = launch_ros.actions.Node(
        package='fishbot_bringup',
        executable='dynamic_scan_filter',
        name='dynamic_scan_filter',
        output='screen',
        parameters=[{
            'input_topic': '/scan',
            'output_topic': '/scan_for_slam',
            'stable_observations': 3,
            'sudden_obstacle_observations': 8,
            'range_tolerance': 0.20,
            'sudden_obstacle_distance': 0.40,
            'max_slam_range': 8.0,
        }],
    )

    return launch.LaunchDescription([
        scan_filter,
        slam_toolbox,
    ])
