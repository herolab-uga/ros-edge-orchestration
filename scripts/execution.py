#!/usr/bin/env python3
import rospy
from ast import Add
from pexpect import pxssh
from edge_robot.msg import Edgedata
import time


class Utility_Calculator:
    def __init__(self):
        self.e1_CPU = 0
        self.e2_CPU = 0
        self.e3_CPU = 0
        self.e1_Mem = 0
        self.e2_Mem = 0
        self.e3_Mem = 0
        self.e1_thrp =0
        self.e2_thrp =0
        self.e3_thrp =0
        self.assigned_edge = ""
        

        self.e1_cpu_sub = rospy.Subscriber('/e1/edge_data', Edgedata, self.callback_e1)
        self.e2_cpu_sub = rospy.Subscriber('/e2/edge_data', Edgedata, self.callback_e2)
        self.e3_cpu_sub = rospy.Subscriber('/e3/edge_data', Edgedata, self.callback_e3)



    def get_assigned_edge(self):
        priority_nodes = ['N1', 'N2', 'N3', 'N4','N5', 'N6', 'N7']
        N1 = 'nohup roslaunch edge_robot navigation_1.launch &'
        N2 = 'nohup roslaunch edge_robot tb3_1_yolov3.launch &'
        N3 = 'nohup roslaunch edge_robot navigation_2.launch &'
        N4 = 'nohup roslaunch edge_robot tb3_2_yolov3.launch &'
        N5 = 'nohup roslaunch edge_robot navigation_3.launch &'
        N6 = 'nohup roslaunch edge_robot tb3_3_yolov3.launch &'
        N7 = 'nohup roslaunch edge_robot multi_tb3_mapmerge.launch &'
        

        for node in priority_nodes:
            node_req = self.get_req(node)
            next_edge = self.calculate_utility(node_req)
            print("For node {}, {} has max utility!".format(node, next_edge))
            #print(next_edge) 
            if node =='N1':
                self.execute_task(N1, next_edge)
                time.sleep(20)
            elif node =='N2':
                self.execute_task(N2, next_edge)
                time.sleep(20)
            elif node =='N3':
                self.execute_task(N3, next_edge)
                time.sleep(20)
            elif node =='N4':
                self.execute_task(N4, next_edge)
                time.sleep(20)
            elif node =='N5':
                self.execute_task(N5, next_edge)
                time.sleep(20)
            elif node =='N6':
                self.execute_task(N6, next_edge)
                time.sleep(20)
            elif node =='N7':
                self.execute_task(N7, next_edge)
                time.sleep(20)
            
                

    def execute_task(self, task, edge):
        if edge == 'E1':
            self.GetHostname('192.168.1.122', 'hero', edge, task)
        elif edge == 'E2':
            self.GetHostname('192.168.1.120', 'hero-edge2', edge, task)
        elif edge == 'E3':
            self.GetHostname('192.168.1.121', 'nano1', edge, task)
            



    def GetHostname (self, ipaddr, uname, e,  command):
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
           

    
    def get_req(self, n):
        if n == 'N1' or n == 'N3' or n == 'N5':
            req = [69.92, 47, 66.83]   # [CPU%, Mem%, (frequency* bandwidth)]
        elif n =='N2' or n=='N4' or n =='N6':
            req = [80.4, 62.53, 3.204]
        elif n =='N7':
            req = [39.79, 45.7, 3369.812]
        return req 



    def callback_e1(self, msg):
        self.e1_CPU = msg.curr_CPU
        self.e1_Mem = msg.curr_mem
        self.e1_thrp = msg.curr_thpt
        self.e1_nodes_run = msg.current_nodes

        

   

    def callback_e2(self, msg):
        self.e2_CPU = msg.curr_CPU
        self.e2_Mem = msg.curr_mem
        self.e2_thrp = msg.curr_thpt
        self.e2_nodes_run = msg.current_nodes



    def callback_e3(self, msg):
        self.e3_CPU = msg.curr_CPU
        self.e3_Mem = msg.curr_mem
        self.e3_thrp = msg.curr_thpt
        self.e3_nodes_run = msg.current_nodes

        self.get_assigned_edge()



    def calculate_utility(self, n_req):
        self.req_CPU = n_req[0]
        self.req_mem = n_req[1]
        self.req_thpt = n_req[2]

        # # Utility for Edge 1
        UT_CPU_1 = abs(self.e1_CPU - self.req_CPU)
        #print('E1 CPU Utility: ' + str(UT_CPU_1)) 
        UT_mem_1 = abs(self.e1_Mem - self.req_mem)
        #print('E1 Memory Utility: ' + str(UT_mem_1)) 
        UT_thpt_1 = abs( 20 - self.e1_thrp - self.req_thpt)
        #print('E1 throughput Utility: ' + str(UT_thpt_1)) 
        self.Total_E1_UT = UT_CPU_1 + UT_mem_1 + UT_thpt_1
        #print(UT_CPU_1, UT_mem_1, UT_thpt_1, self.Total_E1_UT)
        #print ('Total E1 Utility: {}'.format(self.Total_E1_UT))

    
        # # Utility for Edge 2
        UT_CPU_2 = abs(self.e2_CPU - self.req_CPU)
        #print('E2 CPU Utility: ' + str(UT_CPU_2)) 
        UT_mem_2 = abs(self.e2_Mem - self.req_mem)
        #print('E2 Memory Utility: ' + str(UT_mem_2)) 
        UT_thpt_2 = abs(20 - self.e2_thrp - self.req_thpt)
        #print('E2 throughput Utility: ' + str(UT_thpt_2)) 
        self.Total_E2_UT = UT_CPU_2 + UT_mem_2 + UT_thpt_2
        #print(UT_CPU_2, UT_mem_2, UT_thpt_2, self.Total_E2_UT)
        #print ('Total E2 Utility: {}'.format(self.Total_E2_UT))

        # # Utility for Edge 3 

        UT_CPU_3 = abs(self.e3_CPU - self.req_CPU)
        #print('E3 CPU Utility: ' + str(UT_CPU_3)) 
        UT_mem_3 = abs(self.e3_Mem - self.req_mem)
        #print('E3 Memory Utility:sum(self.tx_mbps_3, self.rx_mbps_3) ' + str(UT_mem_3)) 
        UT_thpt_3 = abs(20 - self.e3_thrp - self.req_thpt)
        #print('E3 throughput Utility: ' + str(UT_thpt_3)) 
        self.Total_E3_UT = UT_CPU_3 + UT_mem_3 + UT_thpt_3
        #print(UT_CPU_3, UT_mem_3, UT_thpt_3, self.Total_E3_UT)
        #print ('Total E3 Utility: {}'.format(self.Total_E3_UT))


        Total_UTs = {'E1':self.Total_E1_UT, 'E2':self.Total_E2_UT, 'E3':self.Total_E3_UT}
        self.assigned_edge = max(Total_UTs, key=Total_UTs.get)
        self.max_UT = max(Total_UTs.values())
        #print(self.max_UT)
        #print(self.assigned_edge)
        return self.assigned_edge



if __name__ == '__main__':
    rospy.init_node('Utility_Calculator')
    utility_calc = Utility_Calculator()
    rospy.spin()