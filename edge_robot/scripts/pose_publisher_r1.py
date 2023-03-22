#!/usr/bin/env python3
import rospy
from roslib import message
#from yolov7_ros.msg import BoundingBox
from detection_msgs.msg import BoundingBox, BoundingBoxes
from sensor_msgs.msg import PointCloud2, CameraInfo, Image
import image_geometry 
import ros_numpy
import tf
from geometry_msgs.msg import Point, PointStamped
import sensor_msgs.point_cloud2 as pc2
import numpy
from edge_robot.msg import ObjectFound, ObjectPose


class PosePublisher():
    def __init__(self):
        self.pc = None
        self.tf_listener = tf.TransformListener()
        self.camera_model = None
        self.pc2_point = Point()
        self.objects = ['chair', 'fire hydrant', 'bicycle', 'stop sign', 'person', 'car', 'traffic light', 'airplane']
        self.poses = {}
        self.dist_thresh = 3.5
        self.detected_obj = set()
        


    def publish(self):
        self.obj_pub = rospy.Publisher("/tb3_1/Objects_found", ObjectFound, queue_size=10)
        self.obj_pose_pub = rospy.Publisher("tb3_1/Objects_poses", ObjectPose, queue_size=10)
        self.pub_rate = rospy.Rate(10)

    def subscribe(self):
        self.bbox_sub = rospy.Subscriber('/tb3_1/yolov5/detections', BoundingBoxes, self.bbox_callback)
        self.pc_sub = rospy.Subscriber('/tb3_1/camera/depth/points', PointCloud2, self.pc_callback)
        self.info_sub = rospy.Subscriber('/tb3_1/camera/depth/camera_info', CameraInfo, self.info_callback)
    
    def bbox_callback(self, data):
        # xmin = data.xmin
        # ymin = data.ymin
        # xmax = data.xmax
        # ymax = data.ymax
        # self.box_class = data.Class

        for box in data.bounding_boxes:
            xmin = box.xmin
            ymin = box.ymin
            xmax = box.xmax
            ymax = box.ymax
            self.box_class = box.Class
            #print("R3 object detected:", self.box_class)

            # calculate center pixel 
            pixel_x = (xmin + xmax) / 2
            pixel_y = (ymin + ymax) / 2
            centroid = (pixel_x, pixel_y)

            obj_pos = self.obj_coord(centroid)
        

    def info_callback(self, data):
        # Get a camera model object using image_geometry and the camera_info topic
        self.camera_model = image_geometry.PinholeCameraModel()
        self.camera_model.fromCameraInfo(data)
        self.info_sub.unregister() #Only subscribe once

    def get_depth(self, x, y):
        gen = pc2.read_points(self.pc, field_names='z', skip_nans=False, uvs=[(x, y)]) 
        #print (gen)
        return next(gen)

    def pc_callback(self, data):
        # get pointcloud
        self.pc = data

    def obj_coord(self, centroid):
        # Find the centroid in the point cloud
        x = int(centroid[0])
        y = int(centroid[1])
        depth = self.get_depth(x, y)

        # Convert tuple to float
        dist = float('.'.join(str(ele) for ele in depth))
        #print(dist)

        # Get pixel points in camera units and multiply depth with the vector X and Y value
        v = self.camera_model.projectPixelTo3dRay((x, y))
        d_cam = numpy.concatenate((depth*numpy.array(v), numpy.ones(1))).reshape((4, 1))
        

        # convert 3D xyz to pointStamped 
        self.pc2_point.x = d_cam[0]
        self.pc2_point.y = d_cam[1]
        self.pc2_point.z = d_cam[2] 
        


        point_pub = rospy.Publisher('/tb3_1/target_point', PointStamped, queue_size=1)
        pc2_point_msg = PointStamped()
        pc2_point_msg.header.frame_id = "/tb3_1/camera_rgb_optical_frame"
        pc2_point_msg.header.stamp = rospy.Time(0)
        pc2_point_msg.point = self.pc2_point

        # get transform
        self.tf_listener.waitForTransform('/tb3_1/camera_rgb_optical_frame', '/map', rospy.Time(), rospy.Duration(4))
        p = self.tf_listener.transformPoint("/map", pc2_point_msg)
        pos_x = float(p.point.x)
        pos_y = float(p.point.y)
        #print("{} detected at {}, {}".format(self.box_class, p.point.x, p.point.y))
        if dist <= self.dist_thresh:
            if self.box_class in self.objects:
                # populate objectposes into ObjectPose message
                obj_pose = ObjectPose()
                obj_pose.object_name = self.box_class
                obj_pose.obj_x = pos_x
                obj_pose.obj_y = pos_y
                obj_pose.distance = dist
                self.obj_pose_pub.publish(obj_pose)
                # for printing purpose only
                self.poses[self.box_class] = [pos_x, pos_y, dist]
                print("Objects collected by R1: {}".format(self.poses))
                print("----------------------------------------------")
                # update found objects list
                self.detected_obj.add(self.box_class)
                
        # publish a list of objects found
        obj_msg = ObjectFound()
        obj_msg.obj_found = self.detected_obj
        self.obj_pub.publish(obj_msg)
        


        
       

def main():
    rospy.init_node("R1_pose_publisher")
    pose_calc = PosePublisher()
    pose_calc.subscribe()
    pose_calc.publish()
    rate = rospy.Rate(10)
        
                



if __name__ == "__main__":
    main()
    rospy.spin()