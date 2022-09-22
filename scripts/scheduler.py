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
        self.edges_num = 3
        self.UT_curr_nodes_1 = 0
        self.UT_curr_nodes_2 = 0
        self.UT_curr_nodes_3 = 0


        # get params from launch file
        self.mode = rospy.get_param('scheduler/mode')
        self.task_seq = rospy.get_param('scheduler/task_seq')
        self.task_req = rospy.get_param('scheduler/task_req')
        self.weights = rospy.get_param('scheduler/weights')
        
    
        # creating subscribers and one publisher
        self.e1_sub = rospy.Subscriber('/e1/edge_data', Edgedata, self.callback_e1)
        self.e2_sub = rospy.Subscriber('/e2/edge_data', Edgedata, self.callback_e2)
        self.e3_sub = rospy.Subscriber('/e3/edge_data', Edgedata, self.callback_e3)
        self.pub_edge = rospy.Publisher('next_edge',  EdgeNext, queue_size=10)
        



    def pub_assigned_edge(self):
        rospy.loginfo("Scheduler started")
        while not rospy.is_shutdown():
            rate = rospy.Rate(0.4)
            next_edge = EdgeNext()

            for node in self.task_seq:
                print("===============================")
                print ('CHECKING FOR {}'.format(node))
                node_req = self.task_req.get(node)
                assigned_edge = self.calculate_utility(node, node_req)
                print("For node {}, {} has max utility!".format(node, assigned_edge))
                next_edge.next_node = node
                next_edge.assigned_edge = assigned_edge 
                # publish it for the executor 
                self.pub_edge.publish(next_edge) 
                #print("published!")
                rate.sleep()



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
        penalty = 0
        index = self.task_seq.index(n)
        pre_seq_nodes = self.task_seq[0:index] # pre-sequence nodes in the task sequence
        # check for pre-sequence nodes in the current nodes running on edge
        num_pre_seq_nodes = len(list(set(self.e1_nodes_run).intersection(set(pre_seq_nodes))))
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
        index = self.task_seq.index(n)
        pre_seq_nodes = self.task_seq[0:index] 
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
        index = self.task_seq.index(n)
        pre_seq_nodes = self.task_seq[0:index] 
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
            rank_value = (self.edges_num - 2)/ self.edges_num
        elif edge == list(ranked_UT_nodes)[2]:
            rank_value = (self.edges_num - 3) / self.edges_num
        return rank_value



    def calculate_utility(self, node, n_req):
        self.req_CPU = n_req[0]
        self.req_mem = n_req[1]  # 
        # for e in range(1,4):
        #     sub_edge_data = rospy.Subscriber('/e'+(str(e))+'/edge_data', Edgedata, self.callback_edge)
        max_cpu = 100
        max_mem = 100
        max_througput = 100

        
        # # Utility for Edge 1
        UT_CPU_1 = abs(max_cpu - self.e1_CPU - self.req_CPU) /max_cpu 
        UT_mem_1 = abs(max_mem - self.e1_Mem - self.req_mem) / max_mem
        UT_thpt_1 = abs(max_througput - self.e1_thrp - self.req_thpt) / max_througput
        self.UT_curr_nodes_1 = self.get_nodes_utility_e1(node)
        # get rank to get score between 0 & 1
        UT_nodes_1 = self.get_rank('Edge 1')
        # apply weights for the mode set in calculating total utility
        w_ = self.weights.get(self.mode)
        self.Total_E1_UT = w_[0]*UT_CPU_1 + w_[1]*UT_mem_1 + w_[2]*UT_thpt_1 + w_[3]*UT_nodes_1


    
        # # Utility for Edge 2
        UT_CPU_2 = abs(max_cpu - self.e2_CPU - self.req_CPU) / max_cpu
        UT_mem_2 = abs(max_mem - self.e2_Mem - self.req_mem) / max_mem
        UT_thpt_2 = abs(max_througput - self.e2_thrp - self.req_thpt) / max_througput
        self.UT_curr_nodes_2 = self.get_nodes_utility_e2(node)
        UT_nodes_2 = self.get_rank('Edge 2')
        self.Total_E2_UT = w_[0]*UT_CPU_2 + w_[1]*UT_mem_2 + w_[2]*UT_thpt_2 + w_[3]*UT_nodes_2



        # # Utility for Edge 3 
        UT_CPU_3 = abs(max_cpu - self.e3_CPU - self.req_CPU) / max_cpu
        UT_mem_3 = abs(max_mem - self.e3_Mem - self.req_mem) / max_mem
        UT_thpt_3 = abs(max_througput - self.e3_thrp - self.req_thpt) / max_througput
        self.UT_curr_nodes_3 = self.get_nodes_utility_e3(node)
        UT_nodes_3 = self.get_rank('Edge 3')
        self.Total_E3_UT = w_[0]*UT_CPU_3 + w_[1]*UT_mem_3 + w_[2]*UT_thpt_3 + w_[3]*UT_nodes_3


        Total_UTs = {'E1':self.Total_E1_UT, 'E2':self.Total_E2_UT, 'E3':self.Total_E3_UT}
        self.assigned_edge = max(Total_UTs, key=Total_UTs.get)
        self.max_UT = max(Total_UTs.values())
        return self.assigned_edge
       

        
   
 
    



if __name__ == '__main__':
    rospy.init_node('Utility_Calculator')
    utility_calc = Utility_Calculator()
    rospy.spin()

