#!/usr/bin/env python3

import rospy
import actionlib
from timeit import default_timer as timer 

#move_base_msgs
from move_base_msgs.msg import *
from geometry_msgs.msg import *
from edge_robot.msg import TaskStatus, ObjectFound
import message_filters 


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
    move_base = actionlib.SimpleActionClient('tb3_1/move_base', MoveBaseAction )
    

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
        rospy.loginfo("R1 Timed out achieving goal")
    else:
        # We made it!
        state = move_base.get_state()
        print("State:", state)
        if state == 3:
            rospy.loginfo("R1 Goal succeeded!")
            # #stop robot for 2 minutes
            # rospy.loginfo("Robot 1 stopped waiting for offloading!")
            # t_end = time.time() + 15 * 1
            # while time.time() < t_end:
            #     pub_twist.publish(msg_twist)



if __name__ == '__main__':
    pub = rospy.Publisher('R1/task_status',TaskStatus, queue_size=10)
    sub_1 = rospy.Subscriber('/tb3_1/Objects_found', ObjectFound, sub1_callback)
    sub_2  = rospy.Subscriber('/tb3_2/Objects_found', ObjectFound, sub2_callback)
    sub_3  =  rospy.Subscriber ('/tb3_0/Objects_found', ObjectFound, sub3_callback ) 


    try:
        start = timer()
        rospy.init_node('simple_move_tb3_1')
        rate = rospy.Rate(10)

        arr = [ 1.983485460281372, 0.23099583387374878, 0.0, 1.0,
                4.49416971206665, 0.4107280373573303, 0.0, 1.0,
                5.533365726470947, -1.1008410453796387, 0.0, 1.0,
                1.484256625175476, -3.6470232009887695, 0.0, 1.0,
                5.791255474090576, -3.207575559616089, 0.0, 1.0,
                1.956437468528747,-3.3571555614471436, 0.0, 1.0,
                -0.011311724781990051, -2.4147539138793945, 0.0, 1.0,
                 3.1693997383117676, 1.8752059936523438,0.0, 1.0,
                -3.3047752380371094, -4.1709065437316895, 0.0, 1.0,
                -3.518420934677124, -0.17058663070201874, 0.0, 1.0, 
                -3.6608147621154785, 5.0288567543029785, 0.0, 1.0,
                0.0, 0.0, 0.0, 0.1,
            ]
        coordinates = list()
        chunk_size = 4
        for i in range(0, len(arr), chunk_size):
            coordinates.append(arr[i:i+chunk_size])
        #print(coordinates)
        for i in range(10):
            print("-------------------------------------------")
            print("-------------------------------------------")
            print("Sending Goal {} to R1".format(i))
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
