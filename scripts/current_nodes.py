#!/usr/bin/env python
  
import rospy
# the following line depends upon the
# type of message you are trying to publish
from edge_robot.msg import Nodes
import socket, time, datetime, psutil
import os 
from subprocess import Popen, PIPE
import netifaces as ni
  


nodes_list = [] 
def get_nodes():
    ip = ni.ifaddresses('wlp0s20f3')[ni.AF_INET][0]['addr']
    #print(ip) 
    command = 'rosnode machine ' + ip
    r = os.popen(command) #Execute command
    info = r.readlines()  #read command output
    for line in info:  #handle output line by line
        line = line.strip('\r\n')
        nodes_list.append(line)
    return nodes_list

def publisher():
    nodes_msg = Nodes()
    # define the actions the publisher will make
    pub = rospy.Publisher('m1/current_nodes', Nodes, queue_size=10)
    # initialize the publishing node
    rospy.init_node('master_current_nodes', anonymous=True)
    n_list = get_nodes()
    print(n_list)
    # define how many times per second will the data be published
    # let's say 10 times/second or 10Hz
    rate = rospy.Rate(0.25)
    # to keep publishing as long as the core is running
    while not rospy.is_shutdown():
        nodes_msg.current_nodes = n_list
        pub.publish(nodes_msg)
        #rospy.loginfo("Publishing data on rostopic ... ")
        rospy.loginfo(nodes_msg)
        # keep a buffer based on the rate defined earlier
        rate.sleep()
  
  
if __name__ == '__main__':

    try:
        publisher()
    except rospy.ROSInterruptException:        # you could simultaneously display the data
        # on the terminal and to the log file
        pass