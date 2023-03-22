#!/usr/bin/env python3
import queue
from types import new_class
import rospy
from ast import Add
from pexpect import pxssh, spawn
from edge_robot.msg import EdgeNext, Edgedata, TaskStatus
from geometry_msgs.msg import Twist
#from scheduler import Utility_Calculator
import actionlib
from move_base_msgs.msg import * 
import time

class Executor():

    def __init__(self):
        #super().__init__()

        self.r1_status = ""
        self.r2_status = ""
        self.r3_status = ""
        self.r1_state = 0.0
        self.r2_state = 0.0
        self.r3_state = 0.0
       
       
        self.prev_list_= {}
        self.commands = rospy.get_param('scheduler/commands')
        self.task_seq = rospy.get_param('scheduler/task_seq')
        self.data_sub = rospy.Subscriber('/next_edge', EdgeNext, self.execute_task, queue_size=1)
        self.sub_status = rospy.Subscriber('/R1/task_status', TaskStatus, self.r1_status_cb)
        self.sub_status = rospy.Subscriber('/R2/task_status', TaskStatus, self.r2_status_cb)
        self.sub_status = rospy.Subscriber('/R3/task_status', TaskStatus, self.r3_status_cb)
        self.move_base_1 = actionlib.SimpleActionClient('tb3_1/move_base', MoveBaseAction )
        self.move_base_2 = actionlib.SimpleActionClient('tb3_2/move_base', MoveBaseAction )
        self.move_base_3 = actionlib.SimpleActionClient('tb3_0/move_base', MoveBaseAction )
        rospy.spin()
        
    def r1_status_cb(self, msg):
        self.r1_status = msg.status
        self.r1_state = msg.move_base_state
    def r2_status_cb(self, msg):
        self.r2_status = msg.status
        self.r2_state = msg.move_base_state
    def r3_status_cb(self, msg):
        self.r3_status = msg.status
        self.r3_state = msg.move_base_state

    def status_check(self, n):
      if self.r1_status == "R1 Task Completed" and n == "R1_Navigation":
        return "remove"
      elif self.r1_status == "R1 Task Completed" and n == "R1_Obj_Detection":
        return "remove"
      elif self.r2_status == "R2 Task Completed" and n== "R2_Navigation":
        return "remove"
      elif self.r2_status == "R2 Task Completed" and n== "R2_Obj_Detection":
        return "remove"
      elif self.r3_status == "R3 Task Completed" and n == "R3_Navigation":
        return "remove"
      elif self.r3_status == "R3 Task Completed" and n == "R3_Obj_Detection":
        return "remove"
 

    def maintain_prev(self, list_curr):
        print("Previous list:", self.prev_list_)
        new_assign = dict(list_curr.items() - self.prev_list_.items())
        self.prev_list_ = list_curr
        print("Assignment from Scheduler: ", list_curr)
        #print("New Allocation: ", new_assign)

        # comparing with the task_seq list
        #Keys_ =  list(new_assign.keys())
        #print(list(set(self.task_seq) - set(Keys_)))

        self.offloader(new_assign)




        # if n == "R1_Navigation" and self.r1_state == 3.0:
        #     return "offload"
        # elif n == "R2_Navigation" and self.r2_state == 3.0:
        #     return "offload"
        # elif n == "R3_Navigation" and self.r2_state == 3.0:
        #     return "offload"
        # rate.sleep()




    def offloader(self, alloc):
        new_alloc = alloc 
        print("New Allocation:", new_alloc)
        for k, v in new_alloc.items():
            new_edge = v
            new_node = k
            status_ch = self.status_check(new_node)
            if status_ch != "remove":
                command = self.commands.get(new_node)
                self.task_offload(command, new_edge)
        

    def execute_task(self, msg):
        curr_list={}

        print("============================")    

        # populate assigned_nodes

        next_edge = msg.assigned_edge
        next_node = msg.next_node
        for node in range(len(next_node)):
            curr_list[next_node[node]] = next_edge[node] # populate dict from two lists
        self.maintain_prev(curr_list)
        #print("Current Assignment:", curr_list)


        # update allocated_edges
        #new_assign = dict(assign_list.items() - curr_list.items())
        #print("Allocation: ", new_assign)
        

        # send this allocation to the offloader 
        #self.offloader(new_assign)
        

    def task_offload(self, task, edge):
        #print("Task {} Received for {} ". format(task, edge))
        if edge == 'E1':
            self.connect_Host('192.168.1.232', 'jetson', edge, task)
        elif edge == 'E2':
            self.connect_Host('192.168.1.59', 'jetson', edge, task)
        elif edge == 'E3':
            self.connect_Host('192.168.1.173', 'jetson', edge, task)    
        
    
    def connect_Host(self, ipaddr, uname, e,  command):
        try:
            s = pxssh.pxssh(timeout=30)
            hostname = ipaddr
            username = uname 
            password = 'jetson'
            s.login(hostname, username, password)
            print("-----------------------------------------------------------------------------")
            print("Logged into " + e)
            print("Running commands on " + e)
            s.sendline(command)
            s.prompt()
            print(s.before)
            print("-----------------------------------------------------------------------------")
        except pxssh.ExceptionPxssh as e:  
            print("pxssh failed on login.")
            print(e)

if __name__ == '__main__':
    rospy.init_node('Executor', anonymous = True)
    rate = rospy.Rate(10)
    Executor()
    while not rospy.is_shutdown():
        rate.sleep()