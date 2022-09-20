#!/usr/bin/env python3
import rospy
from ast import Add
from pexpect import pxssh
from edge_robot.msg import Edgedata, EdgeNext 
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
        self.e1_nodes_run =''
        self.e2_nodes_run = ''
        self.e3_nodes_run = ''
        self.assigned_edge = ""
        self.N1_pre_req = ('R1/SLAM')
        self.N2_pre_req = ('R1/Navigation')
        self.N3_pre_req = ('R2/SLAM')
        self.N4_pre_req = ('R2/Navigation')
        self.N5_pre_req = ('R3/SLAM')
        self.N6_pre_req = ('R3/Navigation')

        # mode from launch file
        self.mode = rospy.get_param('scheduler/mode')

        self.e1_cpu_sub = rospy.Subscriber('/e1/edge_data', Edgedata, self.callback_e1)
        self.e2_cpu_sub = rospy.Subscriber('/e2/edge_data', Edgedata, self.callback_e2)
        self.e3_cpu_sub = rospy.Subscriber('/e3/edge_data', Edgedata, self.callback_e3)
        self.pub_edge = rospy.Publisher('next_edge',  EdgeNext, queue_size=10)
        



    def pub_assigned_edge(self):
        rospy.loginfo("Scheduler started")
        while not rospy.is_shutdown():
            rate = rospy.Rate(0.4)
            next_edge = EdgeNext()

            priority_nodes = ['N1', 'N2', 'N3', 'N4','N5', 'N6', 'N7']
            for node in priority_nodes:
                print("===============================")
                print ('CHECKING FOR {}'.format(node))
                node_req = self.get_req(node)
                assigned_edge = self.calculate_utility(node, node_req)
                print("For node {}, {} has max utility!".format(node, assigned_edge))
                next_edge.next_node = node
                next_edge.assigned_edge = assigned_edge 
                self.pub_edge.publish(next_edge) 
                print("published!")
                rate.sleep()

    
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

        self.pub_assigned_edge()

    def get_nodes_utility_e1(self, n):
        UT_curr_nodes_e1 = 0
        
        if (n == 'N1'):
            if self.N1_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
        elif (n == 'N2'):
            if self.N1_pre_req and self.N2_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 2
        elif (n == 'N3'):
            if self.N3_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
        elif (n == 'N4'):
            if self.N3_pre_req and self.N4_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
        elif (n == 'N5'):
            if self.N5_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
        elif (n == 'N6'):
            if self.N5_pre_req and self.N6_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
        elif (n =='N7'):
            if self.N1_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
            elif self.N2_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
            elif self.N3_pre_req in self.e1_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 1 ..".format(n))
                UT_curr_nodes_e1 =+ 1
        return UT_curr_nodes_e1
    

    def get_nodes_utility_e2(self, n):
        UT_curr_nodes_e2 = 0       

        if (n == 'N1'):
            if self.N1_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 1
        elif (n == 'N2'):
            if self.N1_pre_req and self.N2_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 2
        elif (n == 'N3'):
            if self.N3_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 1
        elif (n == 'N4'):
            if self.N3_pre_req and self.N4_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 2
        elif (n == 'N5'):
            if self.N5_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 1
        elif (n == 'N6'):
            if self.N5_pre_req and self.N6_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 2
        elif (n =='N7'):
            if self.N1_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 1
            elif self.N2_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2..".format(n))
                UT_curr_nodes_e2 =+ 1
            elif self.N3_pre_req in self.e2_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 2 ..".format(n))
                UT_curr_nodes_e2 =+ 1
        return UT_curr_nodes_e2

    def get_nodes_utility_e3(self, n):
        UT_curr_nodes_e3 = 0
        if (n == 'N1'):
            if self.N1_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 1
        elif (n == 'N2'):
            if self.N1_pre_req and self.N2_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 2
        elif (n == 'N3'):
            if self.N3_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 1
        elif (n == 'N4'):
            if self.N3_pre_req and self.N4_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 2
        elif (n == 'N5'):
            if self.N5_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 1
        elif (n == 'N6'):
            if self.N5_pre_req and self.N6_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 2
        elif (n =='N7'):
            if self.N1_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 1
            elif self.N2_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3..".format(n))
                UT_curr_nodes_e3 =+ 1
            elif self.N3_pre_req in self.e3_nodes_run:
                #print ("Pre-sequence nodes for  {} running already on Edge 3 ..".format(n))
                UT_curr_nodes_e3 =+ 1
        return UT_curr_nodes_e3

    def calculate_utility(self, node, n_req):
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
        UT_curr_nodes_1 = self.get_nodes_utility_e1(node)
        #print('E1 nodes utility : ' + str(UT_curr_nodes_1))

        if self.mode == "CPU":
            self.Total_E1_UT = 0.80*UT_CPU_1+ 0.05*UT_mem_1 + 0.05*UT_thpt_1 + 0.05*UT_curr_nodes_1
        elif self.mode =="Memory":
            self.Total_E1_UT = 0.05*UT_CPU_1 + 0.80*UT_mem_1 + 0.05*UT_thpt_1 + 0.05*UT_curr_nodes_1
        elif self.mode =="Network":
            self.Total_E1_UT = 0.05*UT_CPU_1 + 0.05*UT_mem_1 + 0.80*UT_thpt_1 + 0.05*UT_curr_nodes_1
        elif self.mode =="Nodes":
            self.Total_E1_UT = 0.05*UT_CPU_1 + 0.05*UT_mem_1 + 0.05*UT_thpt_1 + 0.80*UT_curr_nodes_1
        
        #print(UT_CPU_1, UT_mem_1, UT_thpt_1, UT_curr_nodes_1, self.Total_E1_UT)
        #print ('Total E1 Utility: {}'.format(self.Total_E1_UT))

    
        # # Utility for Edge 22
        UT_CPU_2 = abs(self.e2_CPU - self.req_CPU)
        #print('E2 CPU Utility: ' + str(UT_CPU_2)) 
        UT_mem_2 = abs(self.e2_Mem - self.req_mem)
        #print('E2 Memory Utility: ' + str(UT_mem_2)) 
        UT_thpt_2 = abs(20 - self.e2_thrp - self.req_thpt)
        #print('E2 throughput Utility: ' + str(UT_thpt_2)) 
        UT_curr_nodes_2 = self.get_nodes_utility_e2(node)
        #print('E2 nodes utility : ' + str(UT_curr_nodes_2))

        if self.mode == "CPU":
            self.Total_E2_UT = 0.80*UT_CPU_2+ 0.05*UT_mem_2 + 0.05*UT_thpt_2 + 0.05*UT_curr_nodes_2
        elif self.mode =="Memory":
            self.Total_E2_UT = 0.05*UT_CPU_2 + 0.80*UT_mem_2 + 0.05* UT_thpt_2 + 0.05* UT_curr_nodes_2
        elif self.mode =="Network":
            self.Total_E2_UT = 0.05*UT_CPU_2 + 0.05*UT_mem_2 + 0.80*UT_thpt_2 + 0.05*UT_curr_nodes_2
        elif self.mode =="Nodes":
            self.Total_E2_UT = 0.05*UT_CPU_2 + 0.05*UT_mem_2 + 0.05*UT_thpt_2  + 0.80*UT_curr_nodes_2
    
        # print(UT_CPU_2, UT_mem_2, UT_thpt_2, UT_curr_nodes_2, self.Total_E2_UT)
        # print ('Total E2 Utility: {}'.format(self.Total_E2_UT))

        # # Utility for Edge 3 

        UT_CPU_3 = abs(self.e3_CPU - self.req_CPU)
        #print('E3 CPU Utility: ' + str(UT_CPU_3)) 
        UT_mem_3 = abs(self.e3_Mem - self.req_mem)
        #print('E3 Memory Utility:sum(self.tx_mbps_3, self.rx_mbps_3) ' + str(UT_mem_3)) 
        UT_thpt_3 = abs(20 - self.e3_thrp - self.req_thpt)
        #print('E3 throughput Utility: ' + str(UT_thpt_3)) 
        UT_curr_nodes_3 = self.get_nodes_utility_e3(node)
        #print('E3 nodes utility : ' + str(UT_curr_nodes_3))
       
        if self.mode == "CPU":
            self.Total_E3_UT = 0.80*UT_CPU_3 + 0.05*UT_mem_3 + 0.05*UT_thpt_3 + 0.05*UT_curr_nodes_3
        elif self.mode =="Memory":
            self.Total_E3_UT = 0.05*UT_CPU_3 + 0.80*UT_mem_3 + 0.05*UT_thpt_3 + 0.05*UT_curr_nodes_3
        elif self.mode =="Network":
            self.Total_E3_UT = 0.05*UT_CPU_3 + 0.05*UT_mem_3 + 0.80*UT_thpt_3 + 0.05*UT_curr_nodes_3
        elif self.mode =="Nodes":
            self.Total_E3_UT = 0.05*UT_CPU_3 + 0.05*UT_mem_3 + 0.05*UT_thpt_3 + 0.80*UT_curr_nodes_3

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
