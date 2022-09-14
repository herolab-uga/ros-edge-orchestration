#!/usr/bin/env python
import rospy
from network_analysis.msg import LinkUtilization, NetworkDelay
from edge_robot.msg import Edgeinfo, Nodes, Edgedata



class Scheduler:
    def __init__(self):
        
        # for Edge 1
        self.cpu_perct = 0
        self.mem_perct = 0
        self.thrpt_1 = 0
        self.node_names = []
    
        self.loop_rate = rospy.Rate(1)
        self.e1_pub = rospy.Publisher("/e1/edge_data", Edgedata, queue_size=10)
        self.e1_cpu_sub = rospy.Subscriber('/e1/cpu_usage', Edgeinfo, self.callback_cpu)
        self.e1_thp_sub = rospy.Subscriber('/e1/network_analysis/link_utilization', LinkUtilization, self.callback_link)
        self.e1_nodes_sub = rospy.Subscriber('/e1/current_nodes', Nodes, self.callback_nodes)


        # for Edge 2
        self.cpu_perct_2 = 0
        self.mem_perct_2 = 0
        self.thrpt_2 = 0
        self.node_names_2 = []
        self.e2_pub = rospy.Publisher("/e2/edge_data", Edgedata, queue_size=10)
        self.e2_cpu_sub = rospy.Subscriber('/e2/cpu_usage', Edgeinfo, self.callback_cpu_2)
        self.e2_thp_sub = rospy.Subscriber('/e2/network_analysis/link_utilization', LinkUtilization, self.callback_link_2)
        self.e2_nodes_sub = rospy.Subscriber('/e2/current_nodes', Nodes, self.callback_nodes_2)
        
        # # for Edge 3
        self.cpu_perct_3 = 0
        self.mem_perct_3 = 0
        self.thrpt_3 = 0
        self.node_names_3 = []

        self.e3_pub = rospy.Publisher("/e3/edge_data", Edgedata, queue_size=10)
        self.e3_cpu_sub = rospy.Subscriber('/e3/cpu_usage', Edgeinfo, self.callback_cpu_3)
        self.e3_thp_sub = rospy.Subscriber('/e3/network_analysis/link_utilization', LinkUtilization, self.callback_link_3)
        self.e3_nodes_sub = rospy.Subscriber('/e3/current_nodes', Nodes, self.callback_nodes_3)

    # CPU_data_callbacks
    def callback_cpu(self, msg):
        hostname = 'Edge 1'
        self.cpu_perct = msg.CPU_usage_perct
        self.mem_perct = msg.Mem_usage_perct
        print('cpu of {} is {}'.format(hostname, self.cpu_perct))
        print('memory of {} is {}'.format(hostname, self.mem_perct))


    def callback_cpu_2(self, msg):
        hostname = 'Edge 2'
        self.cpu_perct_2 = msg.CPU_usage_perct
        self.mem_perct_2 = msg.Mem_usage_perct
        print('cpu of {} is {}'.format(hostname, self.cpu_perct_2))
        print('memory of {} is {}'.format(hostname, self.mem_perct_2))


    def callback_cpu_3(self, msg):
        hostname = 'Edge 3'
        self.cpu_perct_3 = msg.CPU_usage_perct
        self.mem_perct_3 = msg.Mem_usage_perct
        print('cpu of {} is {}'.format(hostname, self.cpu_perct_3))
        print('memory of {} is {}'.format(hostname, self.mem_perct_3))


    # # throughput callbacks
    def callback_link(self, msg):
        hostname = 'Edge 1'
        self.tx_mbps = msg.total_tx_mbps
        self.rx_mbps = msg.total_rx_mbps 
        self.thrpt_1 = self.tx_mbps + self.rx_mbps
        print("throughput for {} is {} " .format(hostname, self.thrpt_1))

    def callback_link_2(self, msg):
        hostname = 'Edge 2'
        self.tx_mbps_2 = msg.total_tx_mbps
        self.rx_mbps_2 = msg.total_rx_mbps 
        self.thrpt_2 = self.tx_mbps_2 + self.rx_mbps_2
        print("throughput for {} is {} " .format(hostname, self.thrpt_2))

    def callback_link_3(self, msg):
        hostname = 'Edge 3'
        self.tx_mbps_3 = msg.total_tx_mbps
        self.rx_mbps_3 = msg.total_rx_mbps 
        self.thrpt_3 = self.tx_mbps_3 + self.rx_mbps_3
        print("throughput for {} is {} " .format(hostname, self.thrpt_3))
    
    def callback_nodes(self, msg):
        self.nodes = msg.current_nodes
        self.node_names = []
        #print ("Current nodes running on edge 1: ")
        for node in self.nodes: 
            # SLAM nodes 
            if (node =='/tb3_1/turtlebot3_slam_gmapping'): #only to make it more readable
                self.node_names.append('R1/SLAM')
            elif (node =='/tb3_2/turtlebot3_slam_gmapping'):
                self.node_names.append('R2/SLAM')
            elif (node == '/tb3_3/turtlebot3_slam_gmapping'):
                self.node_names.append('R3/SLAM')
            #Navigation nodes
            elif (node == '/tb3_1/move_base_1'):
                self.node_names.append('R1/Navigation')
            elif (node == '/tb3_2/move_base_2'):
                self.node_names.append('R2/Navigation')
            elif (node == '/tb3_3/move_base_3'):
                self.node_names.append('R3/Navigation')
            # map_merge node
            elif (node == '/map_merge'):
                self.node_names.append('Map_Merging')
            # Object_Detection nodes
            elif (node == '/darknet_ros_1/darknet_ros'):
                self.node_names.append('R1/Obj_Detection')
            elif (node == '/darknet_ros_2/darknet_ros'):
                self.node_names.append('R2/Obj_Detection')
            elif (node == '/darknet_ros_3/darknet_ros'):
                self.node_names.append('R3/Obj_Detection')
        #print (self.node_names)


    def callback_nodes_2(self, msg):
        self.nodes_2 = msg.current_nodes
        self.node_names_2 = []
        print ("Current nodes running on edge 2: ")
        for node in self.nodes_2: 
            # SLAM nodes 
            if (node =='/tb3_1/turtlebot3_slam_gmapping'): #only to make it more readable
                self.node_names_2.append('R1/SLAM')
            elif (node =='/tb3_2/turtlebot3_slam_gmapping'):
                self.node_names_2.append('R2/SLAM')
            elif (node == '/tb3_3/turtlebot3_slam_gmapping'):
                self.node_names_2.append('R3/SLAM')
            #Navigation nodes
            elif (node == '/tb3_1/move_base_1'):
                self.node_names_2.append('R1/Navigation')
            elif (node == '/tb3_2/move_base_2'):
                self.node_names_2.append('R2/Navigation')
            elif (node == '/tb3_3/move_base_3'):
                self.node_names.append('R3/Navigation')
            # map_merge node
            elif (node == '/map_merge'):
                self.node_names_2.append('Map_Merging')
            # Object_Detection nodes
            elif (node == '/darknet_ros_1/darknet_ros'):
                self.node_names_2.append('R1/Obj_Detection')
            elif (node == '/darknet_ros_2/darknet_ros'):
                self.node_names_2.append('R2/Obj_Detection')
            elif (node == '/darknet_ros_3/darknet_ros'):
                self.node_names_2.append('R3/Obj_Detection')
        #print (self.node_names_2)

    def callback_nodes_3(self, msg):
        self.nodes_3 = msg.current_nodes
        self.node_names_3 = []
        #print ("Current nodes running on edge 3: ")
        for node in self.nodes_3: 
            # SLAM nodes 
            if (node =='/tb3_1/turtlebot3_slam_gmapping'): #only to make it more readable
                self.node_names_3.append('R1/SLAM')
            elif (node =='/tb3_2/turtlebot3_slam_gmapping'):
                self.node_names.append('R2/SLAM')
            elif (node == '/tb3_3/turtlebot3_slam_gmapping'):
                self.node_names_3.append('R3/SLAM')
            #Navigation nodes
            elif (node == '/tb3_1/move_base_1'):
                self.node_names_3.append('R1/Navigation')
            elif (node == '/tb3_2/move_base_2'):
                self.node_names_3.append('R2/Navigation')
            elif (node == '/tb3_3/move_base_3'):
                self.node_names_3.append('R3/Navigation')
            # map_merge node
            elif (node == '/map_merge'):
                self.node_names_3.append('Map_Merging')
            # Object_Detection nodes
            elif (node == '/darknet_ros_1/darknet_ros'):
                self.node_names_3.append('R1/Obj_Detection')
            elif (node == '/darknet_ros_2/darknet_ros'):
                self.node_names_3.append('R2/Obj_Detection')
            elif (node == '/darknet_ros_3/darknet_ros'):
                self.node_names_3.append('R3/Obj_Detection')
        #print (self.node_names_3)


    
    def start(self):
        rospy.loginfo("Scheduler started")
        while not rospy.is_shutdown():
            rate = rospy.Rate(1)
            edge_data = Edgedata()

            # publish data for Edge 1
            edge_data.curr_CPU = self.cpu_perct
            edge_data.curr_mem = self.mem_perct
            edge_data.curr_thpt = self.thrpt_1
            edge_data.current_nodes = self.node_names
            self.e1_pub.publish(edge_data)

            # # publish data for Edge 2
            edge_data.curr_CPU = self.cpu_perct_2
            edge_data.curr_mem = self.mem_perct_2
            edge_data.curr_thpt = self.thrpt_2
            edge_data.current_nodes = self.node_names_2
            self.e2_pub.publish(edge_data)

            # # publish data for Edge 3
            edge_data.curr_CPU = self.cpu_perct_3
            edge_data.curr_mem = self.mem_perct_3
            edge_data.curr_thpt = self.thrpt_3
            edge_data.current_nodes = self.node_names_3
            self.e3_pub.publish(edge_data)
            rate.sleep()
            

if __name__ == '__main__':
    rospy.init_node('executor')
    scheduler_ = Scheduler()
    scheduler_.start()
    rospy.spin()
    