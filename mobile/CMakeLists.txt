cmake_minimum_required(VERSION 2.8.3)

project(mobile)

find_package(catkin REQUIRED COMPONENTS
	message_generation
	roscpp
	rospy
	std_msgs
	geometry_msgs
	urdf
	xacro
	controller_manager
	gazebo_ros
	gazebo_ros_control
	diff_drive_controller
)
catkin_package(
	CATKIN_DEPENDS
	geometry_msgs
	roscpp
	rospy
	std_msgs
	urdf
	xacro
	controller_manager
	gazebo_ros
	gazebo_ros_control
	diff_drive_controller
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${GAZEBO_INCLUDE_DIRS}
)
link_directories(${GAZEBO_LIBRARY_DIRS})

find_package(roslaunch)

foreach(dir config launch meshes urdf)
	install(DIRECTORY ${dir}/
		DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)
