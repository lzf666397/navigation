import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    fishbot_bringup_dir = get_package_share_directory('fishbot_bringup')
    fishbot_navigation2_dir = get_package_share_directory('fishbot_navigation2')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    nav2_params = os.path.join(
        fishbot_navigation2_dir, 'config', 'nav2_slam_params.yaml')
    rviz_config = os.path.join(
        nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    rviz = LaunchConfiguration('rviz')
    log_level = LaunchConfiguration('log_level')
    nav2_start_delay = LaunchConfiguration('nav2_start_delay')
    rviz_start_delay = LaunchConfiguration('rviz_start_delay')

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(fishbot_bringup_dir, 'launch', 'bringup.launch.py')),
    )

    scan_filter = Node(
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

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'slam': 'True',
            'use_localization': 'True',
            'map': '',
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
            'autostart': 'True',
            'use_composition': 'False',
            'use_respawn': 'False',
            'log_level': log_level,
        }.items(),
    )

    rviz_node = Node(
        condition=IfCondition(rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation clock. Keep False on the real fishbot.'),
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=nav2_params,
            description='Nav2 + slam_toolbox parameters for online mapping navigation.'),
        DeclareLaunchArgument(
            'rviz',
            default_value='True',
            description='Start RViz2 with the Nav2 default view.'),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Log level for Nav2 nodes.'),
        DeclareLaunchArgument(
            'nav2_start_delay',
            default_value='14.0',
            description='Seconds to wait before starting SLAM + Nav2.'),
        DeclareLaunchArgument(
            'rviz_start_delay',
            default_value='16.0',
            description='Seconds to wait before starting RViz2.'),
        bringup,
        scan_filter,
        TimerAction(period=nav2_start_delay, actions=[nav2]),
        TimerAction(period=rviz_start_delay, actions=[rviz_node]),
    ])
