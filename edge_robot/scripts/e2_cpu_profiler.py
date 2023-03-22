#!/usr/bin/env python3

import rospy
from edge_robot.msg import Edgeinfo
import socket, time, datetime, psutil
import os


def publisher():
    pub =  rospy.Publisher('e2/cpu_usage', Edgeinfo, queue_size=10)
    rospy.init_node('e2_cpu_profiler', anonymous = True)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        hostname = socket.gethostname()
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)

        # memory infor
        memory_stats = psutil.virtual_memory()
        memory_total = memory_stats.total/1e+6
        memory_used = memory_stats.used/1e+6
        memory_used_percent = memory_stats.percent

        #Time info
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        uptime = int(time.time() - psutil.boot_time())

        # load average
        load1, load5, load15 = os.getloadavg()

        cpu_msg = Edgeinfo()

        # publish the cpu_msg to the topc using publish()
        cpu_msg.Hostname = hostname
        cpu_msg.CPU_Count = cpu_count
        cpu_msg.CPU_usage_perct = cpu_usage
        cpu_msg.Mem_usage_perct = memory_used_percent
        cpu_msg.total_mem = memory_total
        cpu_msg.mbs_used = memory_used
        cpu_msg.uptime = uptime
        cpu_msg.load1 = load1
        cpu_msg.load5 = load5
        cpu_msg.load15 = load15
        pub.publish(cpu_msg)
        rospy.loginfo("Publishing data on rostopic ...")
        rospy.loginfo(cpu_msg)
        rate.sleep()

if __name__=='__main__':
    try:
        publisher()
    except rospy.ROSInterruptException:
        pass