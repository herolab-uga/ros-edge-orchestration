#!/usr/bin/env python
  
import rospy
# the following line depends upon the
# type of message you are trying to publish
from edge_robot.msg import Edgeinfo
import socket, time, datetime, psutil
import os 

  
  
def publisher():

    # define the actions the publisher will make
    pub = rospy.Publisher('master/cpu_usage', Edgeinfo, queue_size=10)
    # initialize the publishing node
    rospy.init_node('master_cpu_mem_usage', anonymous=True)
      
    # define how many times per second will the data be published
    # let's say 10 times/second or 10Hz
    rate = rospy.Rate(10)
    # to keep publishing as long as the core is running
    while not rospy.is_shutdown():
        hostname = socket.gethostname()
        # CPU Info
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory Info
        memory_stats = psutil.virtual_memory()
        memory_total = memory_stats.total/1e+6
        memory_used = memory_stats.used/1e+6
        memory_used_percent = memory_stats.percent
    
        # Time Info
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        uptime = int(time.time() - psutil.boot_time())
    
        #Load Average 
        load1, load5, load15 = os.getloadavg()

        cpu_msg = Edgeinfo()
          
          
        # publish the cpu_msg to the topic using publish()
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
        rospy.loginfo("Publishing data on rostopic ... ")
        rospy.loginfo(cpu_msg)
        # keep a buffer based on the rate defined earlier
        rate.sleep()
  
  
if __name__ == '__main__':

    try:
        publisher()
    except rospy.ROSInterruptException:        # you could simultaneously display the data
        # on the terminal and to the log file
        pass