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
        self.commands = rospy.get_param('scheduler/commands')

    def execute_task(self, msg):
        next_edge = msg.assigned_edge
        next_node = msg.next_node
        max_utility = msg.totalUT
        # print(next_node)
        # print(next_edge) 
        print("For node {}, {} has max utility {}!".format(next_node, next_edge, max_utility))
        command = self.commands.get(next_node)
        self.task_offload(command, next_edge)

           

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