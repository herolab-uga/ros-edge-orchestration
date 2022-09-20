#!/usr/bin/env python3
import rospy
from ast import Add
from pexpect import pxssh
from edge_robot.msg import EdgeNext
import time

class Executor:

    def __init__(self):
        rospy.loginfo("Executor started")
        self.e1_cpu_sub = rospy.Subscriber('/next_edge', EdgeNext, self.execute_task)

    def execute_task(self, msg):
        next_edge = msg.assigned_edge
        next_node = msg.next_node
        N1 = 'nohup roslaunch edge_robot navigation_1.launch &'
        N2 = 'nohup roslaunch edge_robot tb3_1_yolov3.launch &'
        N3 = 'nohup roslaunch edge_robot navigation_2.launch &'
        N4 = 'nohup roslaunch edge_robot tb3_2_yolov3.launch &'
        N5 = 'nohup roslaunch edge_robot navigation_3.launch &'
        N6 = 'nohup roslaunch edge_robot tb3_3_yolov3.launch &'
        N7 = 'nohup roslaunch edge_robot multi_tb3_mapmerge.launch &'
        # print(next_node)
        # print(next_edge) 
        

        if next_node =='N1':
           print ('Ive got this')
           self.task_offload(N1, next_edge)
           time.sleep(20)
        elif next_node =='N2':
           self.task_offload(N2, next_edge)
           time.sleep(20)
        elif next_node=='N3':
           self.task_offload(N3, next_edge)
           time.sleep(20)
        elif next_node =='N4':
           self.task_offload(N4, next_edge)
           time.sleep(20)
        elif next_node =='N5':
           self.task_offload(N5, next_edge)
           time.sleep(20)
        elif next_node =='N6':
           self.task_offload(N6, next_edge)
           time.sleep(20)
        elif next_node =='N7':
           self.task_offload(N7, next_edge)
           time.sleep(20)
           

    def task_offload(self, task, edge):
        if edge == 'E1':
            self.connect_Host('192.168.1.24', 'hero', edge, task)
        elif edge == 'E2':
            self.connect_Host('192.168.1.30', 'hero-edge2', edge, task)
        elif edge == 'E3':
            self.connect_Host('192.168.1.14', 'nano1', edge, task)    
        
    
    def connect_Host(self, ipaddr, uname, e,  command):
        try:
            s = pxssh.pxssh(timeout=30)
            hostname = ipaddr
            username = uname 
            password = 'HeroRobots!'
            s.login(hostname, username, password)
            print("Logged into " + e)
            print("Running commands on " + e)
            s.sendline(command)
            s.prompt()
            print(s.before)
        except pxssh.ExceptionPxssh as e:  
            print("pxssh failed on login.")
            print(e)

if __name__ == '__main__':
    rospy.init_node('Executor')
    execution_ = Executor()
    rospy.spin()