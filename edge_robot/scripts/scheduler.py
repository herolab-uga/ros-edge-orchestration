#!/usr/bin/env python3
import rospy
from ast import Add
from pexpect import pxssh
from edge_robot.msg import Edgedata, EdgeNext, TaskStatus
from collections import defaultdict


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
        self.edges_num = 3
        self.UT_curr_nodes_1 = 0
        self.UT_curr_nodes_2 = 0
        self.UT_curr_nodes_3 = 0

        self.exp_e1_CPU = 0
        self.exp_e2_CPU = 0
        self.exp_e3_CPU = 0

        self.exp_e1_Mem = 0
        self.exp_e2_Mem = 0
        self.exp_e3_Mem = 0

        self.exp_e1_Thp = 0
        self.exp_e2_Thp = 0
        self.exp_e3_Thp = 0
       


        # get params from launch file
        self.mode = rospy.get_param('scheduler/mode')
        self.task_seq = rospy.get_param('scheduler/task_seq')
        self.task_req = rospy.get_param('scheduler/task_req')
        self.task_req_seq = rospy.get_param('scheduler/task_req_seq')
        self.weights = rospy.get_param('scheduler/weights')
        
    
        # creating subscribers and one publisher
        self.e1_sub = rospy.Subscriber('/e1/edge_data', Edgedata, self.callback_e1)
        self.e2_sub = rospy.Subscriber('/e2/edge_data', Edgedata, self.callback_e2)
        self.e3_sub = rospy.Subscriber('/e3/edge_data', Edgedata, self.callback_e3)
        self.pub_edge = rospy.Publisher('next_edge',  EdgeNext, queue_size=1)
        

   


    def initialize_metrics(self):
        self.exp_e1_CPU = self.e1_CPU
        self.exp_e2_CPU = self.e2_CPU
        self.exp_e3_CPU = self.e3_CPU

        self.exp_e1_Mem = self.e1_Mem
        self.exp_e2_Mem = self.e2_Mem
        self.exp_e3_Mem = self.e3_Mem

        self.exp_e1_Thp = self.e1_thrp
        self.exp_e2_Thp = self.e2_thrp
        self.exp_e3_Thp = self.e3_thrp

  


    def get_assigned_edge(self):
        rospy.loginfo("Scheduler started")
        rate = rospy.Rate(0.04)
        while not rospy.is_shutdown():
            next_edge = EdgeNext()
            list_nodes = []
            edges_assign = []
            #self.next_assign_list = {} 
            self.initialize_metrics()
            for node in self.task_seq:
                print("Scheduling node: {}".format(node))
                #status_ch = self.status_check(node)
                node_req = self.task_req.get(node)  # get nodes requirement
                assigned_edge = self.calculate_utility(node, node_req) # get the edge for that node with max utility
                print("For node {}, {} has max utility!".format(node, assigned_edge))
                print("------------------------------------------------------------------------")
                list_nodes.append(node) #  node to nodes list 
                edges_assign.append(assigned_edge) # edge to edges list
            next_edge.next_node = list_nodes
            next_edge.assigned_edge = edges_assign
            self.pub_edge.publish(next_edge) 
            rate.sleep()
                
            # for node in range(len(list_nodes)):the maximum all
            #     assign_list[list_nodes[node]] = edges_assign[node] # populate dict from two lists
            # #print(assign_list) 
            # self.pub_allocation(assign_list) # send the list to be published
            # rate.sleep()


          

    def callback_e1(self, msg):
        self.e1_num = msg.edge_num 
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

    def get_nodes_utility_e1(self, n):
        UT_curr_nodes_e1 = 0
        penalty = 0
        
        pre_seq_nodes = self.task_req_seq.get(n) # pre-sequence nodes in the task required sequence
        # check for pre-sequence nodes in the current nodes running on edge 1
        num_pre_seq_nodes = len(list(set(self.e1_nodes_run).intersection(set(pre_seq_nodes))))
        # check for pre-sequence nodes in the current nodes running on edge 2 & 3
        if pre_seq_nodes in self.e2_nodes_run: 
            penalty = len(list(set(self.e2_nodes_run).intersection(set(pre_seq_nodes))))
        elif pre_seq_nodes in self.e3_nodes_run:
            penalty = len(list(set(self.e3_nodes_run).intersection(set(pre_seq_nodes))))
        # add the number to the nodes utility and minus the number of nodes running on other edges 
        UT_curr_nodes_e1 = UT_curr_nodes_e1 + num_pre_seq_nodes - penalty
        return UT_curr_nodes_e1

    

    def get_nodes_utility_e2(self, n):
        UT_curr_nodes_e2 = 0
        penalty = 0
        pre_seq_nodes = self.task_req_seq.get(n)
        num_pre_seq_nodes = len(list(set(self.e2_nodes_run).intersection(set(pre_seq_nodes))))
        if pre_seq_nodes in self.e1_nodes_run: 
            penalty = len(list(set(self.e1_nodes_run).intersection(set(pre_seq_nodes))))
        elif pre_seq_nodes in self.e3_nodes_run:
            penalty = len(list(set(self.e3_nodes_run).intersection(set(pre_seq_nodes))))

        UT_curr_nodes_e2 = UT_curr_nodes_e2 + num_pre_seq_nodes - penalty
        return UT_curr_nodes_e2


    def get_nodes_utility_e3(self, n):
        UT_curr_nodes_e3 = 0
        penalty = 0
        pre_seq_nodes = self.task_req_seq.get(n)
        num_pre_seq_nodes = len(list(set(self.e3_nodes_run).intersection(set(pre_seq_nodes))))
        if pre_seq_nodes in self.e1_nodes_run:
            penalty = len(list(set(self.e1_nodes_run).intersection(set(pre_seq_nodes))))
        elif pre_seq_nodes in self.e2_nodes_run:
            penalty = len(list(set(self.e2_nodes_run).intersection(set(pre_seq_nodes))))
        UT_curr_nodes_e3 = UT_curr_nodes_e3 + num_pre_seq_nodes - penalty
        return UT_curr_nodes_e3 

    def get_rank (self, edge):
        UT_nodes_score = {'Edge 1': self.UT_curr_nodes_1, 'Edge 2': self.UT_curr_nodes_2, 'Edge 3': self.UT_curr_nodes_3}
        ranked_UT_nodes = {key: rank for rank, key in enumerate(sorted(UT_nodes_score, key=UT_nodes_score.get, reverse=True), 1)}
        if edge == list(ranked_UT_nodes)[0]:
            rank_value = (self.edges_num - 1) / self.edges_num 
        elif edge == list(ranked_UT_nodes)[1]:
            rank_value = (self.edges_num - 2) / self.edges_num
        elif edge == list(ranked_UT_nodes)[2]:
            rank_value = (self.edges_num - 3) / self.edges_num
        return rank_value



    def calculate_utility(self, node, n_req):
        self.req_CPU = n_req[0]
        self.req_mem = n_req[1]  # 
        self.req_thpt = n_req[2]

        max_cpu = 100
        max_mem = 100
        max_througput = 100

        
        # # Utility for Edge 1
        UT_CPU_1 = (max_cpu - self.exp_e1_CPU - self.req_CPU) /max_cpu 
        UT_mem_1 = (max_mem - self.exp_e1_Mem - self.req_mem) / max_mem
        UT_thpt_1 = (max_througput - self.exp_e1_Thp - self.req_thpt) / max_througput
        self.UT_curr_nodes_1 = self.get_nodes_utility_e1(node)
        # get rank to get score between 0 & 1
        UT_nodes_1 = self.get_rank('Edge 1')
        # apply weights for the mode set in calculating total utility
        w_ = self.weights.get(self.mode)
        #print(w_)
        self.Total_E1_UT = w_[0]*UT_CPU_1 + w_[1]*UT_mem_1 + w_[2]*UT_thpt_1 + w_[3]*UT_nodes_1
        #print("CPU", self.exp_e1_CPU)
        #print("req cpu", self.req_CPU)


    
        # # Utility for Edge 2
        UT_CPU_2 = (max_cpu - self.exp_e2_CPU - self.req_CPU) / max_cpu
        UT_mem_2 = (max_mem - self.exp_e2_Mem - self.req_mem) / max_mem
        UT_thpt_2 = (max_througput - self.exp_e2_Thp - self.req_thpt) / max_througput
        self.UT_curr_nodes_2 = self.get_nodes_utility_e2(node)
        UT_nodes_2 = self.get_rank('Edge 2')
        self.Total_E2_UT = w_[0]*UT_CPU_2 + w_[1]*UT_mem_2 + w_[2]*UT_thpt_2 + w_[3]*UT_nodes_2
        #print("CPU", self.exp_e2_CPU)

        


        # # Utility for Edge 3 
        UT_CPU_3 = (80 - self.exp_e3_CPU - self.req_CPU) / max_cpu
        UT_mem_3 = (max_mem - self.exp_e3_Mem - self.req_mem) / max_mem
        UT_thpt_3 = (max_througput - self.exp_e3_Thp - self.req_thpt) / max_througput
        self.UT_curr_nodes_3 = self.get_nodes_utility_e3(node)
        UT_nodes_3 = self.get_rank('Edge 3')
        self.Total_E3_UT = w_[0]*UT_CPU_3 + w_[1]*UT_mem_3 + w_[2]*UT_thpt_3 + w_[3]*UT_nodes_3
        #print("CPU", self.exp_e3_CPU)

        Total_UTs = {'E1':self.Total_E1_UT, 'E2':self.Total_E2_UT, 'E3':self.Total_E3_UT}
        print ("Total utilities for all edges: {}".format(Total_UTs))
        self.assigned_edge = max(Total_UTs, key=Total_UTs.get)
        self.max_UT = max(Total_UTs.values())
        #print("Edge {} total utility: {}".format(self.assigned_edge, self.max_UT))
        
        # Update expected metrics 
        if self.assigned_edge == 'E1':
            self.exp_e1_CPU += self.req_CPU 
            self.exp_e1_Mem += self.req_mem
            self.exp_e1_Thp += self.req_thpt
        elif self.assigned_edge == 'E2':
            self.exp_e2_CPU += self.req_CPU 
            self.exp_e2_Mem += self.req_mem
            self.exp_e2_Thp += self.req_thpt
        elif self.assigned_edge == 'E3' :
            self.exp_e3_CPU += self.req_CPU 
            self.exp_e3_Mem += self.req_mem
            self.exp_e3_Thp += self.req_thpt

        return self.assigned_edge


if __name__ == '__main__':
    rospy.init_node('Utility_Calculator')
    utility_calc = Utility_Calculator()
    rospy.spin()
