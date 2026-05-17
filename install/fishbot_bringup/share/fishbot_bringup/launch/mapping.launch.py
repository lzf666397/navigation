import os

import launch
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

    return launch.LaunchDescription([
        slam_toolbox,
    ])
