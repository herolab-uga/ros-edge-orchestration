#!/usr/bin/env python3

import rospy
import actionlib
import time

#move_base_msgs
from move_base_msgs.msg import *
from geometry_msgs.msg import *
from edge_robot.msg import TaskStatus, ObjectFound
import message_filters 
from timeit import default_timer as timer 

task_state = TaskStatus()
list_objects_1 = set()
list_objects_2 = set()
list_objects_3 = set()

objects = set(['chair', 'fire hydrant', 'bicycle', 'stop sign', 'person', 'car', 'traffic light', 'airplane'])


def sub1_callback(msg):
    objects_detected = []
    global list_objects_1
    for obj in msg.obj_found:
        objects_detected.append(msg.obj_found)
        obj_list= [val for sublist in objects_detected for val in sublist]
        list_objects_1 = set(obj_list)
    
def sub2_callback(msg):
    objects_detected = []
    global list_objects_2
    for obj in msg.obj_found:
        objects_detected.append(msg.obj_found)
        obj_list= [val for sublist in objects_detected for val in sublist]
        list_objects_2 = set(obj_list)


def sub3_callback(msg):
    objects_detected = []
    global list_objects_3
    for obj in msg.obj_found:
        objects_detected.append(msg.obj_found)
        obj_list= [val for sublist in objects_detected for val in sublist]
        list_objects_3 = set(obj_list)





def simple_move(x,y,w,z):

    global task_state 
    move_base = actionlib.SimpleActionClient('tb3_2/move_base', MoveBaseAction )
    

    #create goal
    goal = MoveBaseGoal()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation.w = w
    goal.target_pose.pose.orientation.z = z
    goal.target_pose.header.frame_id = 'map'
    goal.target_pose.header.stamp = rospy.Time.now()

    #start listner
    move_base.wait_for_server()
    rospy.loginfo("Connected to R1 move base server")
    rospy.loginfo("Starting R1 navigation task")
    #send goal
    move_base.send_goal(goal)

    #print("State of the robot while moving..", move_state)
    #print ("Sending goal to R1:",x,y,w,z)
    
    # Allow 1 minute to get there
    finished_within_time = move_base.wait_for_result(rospy.Duration(120)) 
    state = move_base.get_state()
    task_state.move_base_state = state 
    pub.publish(task_state)
    rate.sleep()
    


    
    # If we don't get there in time, abort the goal
    if not finished_within_time:
        move_base.cancel_goal()
        rospy.loginfo("R2 Timed out achieving goal")
    else:
        # We made it!
        state = move_base.get_state()
        print("State:", state)
        if state == 3:
            rospy.loginfo("R2 Goal succeeded!")
            # #stop robot for 2 minutes
            # rospy.loginfo("Robot 1 stopped waiting for offloading!")
            # t_end = time.time() + 15 * 1
            # while time.time() < t_end:
            #     pub_twist.publish(msg_twist)



if __name__ == '__main__':
    pub = rospy.Publisher('R2/task_status',TaskStatus, queue_size=10)
    sub_1 = rospy.Subscriber('/tb3_1/Objects_found', ObjectFound, sub1_callback)
    sub_2  = rospy.Subscriber('/tb3_2/Objects_found', ObjectFound, sub2_callback)
    sub_3  =  rospy.Subscriber ('/tb3_0/Objects_found', ObjectFound, sub3_callback ) 

    try:
        start = timer()
        rospy.init_node('simple_move_tb3_2')
        rate = rospy.Rate(10)


        arr = [ 
                -0.874285042285919, 2.8050808906555176, 0.0, 1.0,
                0.42532074451446533, 0.4162019193172455, 0.0, 1.0,
                -0.054413795471191406, 0.4900590777397156, 0.0, 1.0,
                1.3911306858062744, -3.2353665828704834, 0.0, 1.0,
                -1.3074437379837036, -5.033658981323242, 0.0, 1.0,
                -2.9193153381347656, -3.5253524780273438, 0.0, 1.0,
                -1.3745254278182983, -3.7580666542053223, 0.0, 1.0,
                -2.9193153381347656, -3.5253524780273438, 0.0, 1.0,
                -2.525683641433716, -0.6519403457641602, 0.0, 1.0,
                -3.661604881286621, 2.1470162868499756, 0.0, 1.0,
                -5.563322544097, 5.702484607696533, 0.0, 1.0,
                -2.529602527618408, 6.7726850509643555, 0.0, 1.0,
                1.3118164539337158, 2.844010591506958, 0.0, 1.0,
        ]
        coordinates = list()
        chunk_size = 4
        for i in range(0, len(arr), chunk_size):
            coordinates.append(arr[i:i+chunk_size])
        #print(coordinates)
        for i in range(10):
            print("-------------------------------------------")
            print("-------------------------------------------")
            print("Sending Goal {} to R2".format(i))
            goal = coordinates[i]
            #print("goal sent " , goal)
            simple_move(goal[0], goal[1], goal[2], goal[3])


            list_objects = set().union(*[list_objects_1, list_objects_2, list_objects_3])
            print(list_objects)
            if list_objects == objects:
                end = timer()
                total_time = end - start
                print("Total time taken: {} seconds".format(total_time))
                print("All objects have been detected!!!!!")
                rospy.signal_shutdown('All objects are detected')

        end2 = timer()
        total_time_2 = start-end2
        print("Total time taken: {} seconds".format(total_time_2))
        task_state = TaskStatus()
        task_state.status = "R1 Task Completed"
        print ("Task Completed for Robot 1")
        print("-------------------------------------------")
        print("-------------------------------------------")
        pub.publish(task_state)
        
    except rospy.ROSInterruptException:
        end3 = timer()
        print ("Keyboard Interrupt")
        print("total time taken:" +str(end3 - start))