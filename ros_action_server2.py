#!/usr/bin/python

import numpy as np
import rospy
from rospy import Duration

import tf
from geometry_msgs.msg import TransformStamped, Point, Pose
import time
import turtlesim.msg
from std_msgs.msg import String
#from tf2_msgs.msg import TFMessage
import tf2_msgs.msg
import sys
import signal

from pycrazyswarm import *
import uav_trajectory
import actionlib
import actionlib_tutorials.msg
import actionlib_tutorials.srv

from math import pow, atan2, sqrt
# from gtts import gTTS
# import playsound
# try:
#     from urllib.parse import urlparse
# except ImportError:
#      from urlparse import urlparse

import pyttsx3
global engine 
engine = pyttsx3.init()


#from six.moves.urllib import parse

def signal_handler(signal, frame):
	sys.exit(0)

def speak(engine, text):
    

    # tts = gTTS(text=text, lang="en")
    # filename = "voice.mp3"
    # tts.save(filename)
    # playsound.playsound(filename)
    engine.say(text)
    engine.runAndWait()

class PerimeterMonitor(object):

    def __init__(self, name):
        print("name is", name)
        #self._action_name = name

        self.swarm = Crazyswarm()
        #self.timeHelper = swarm.timeHelper
        self.allcfs = self.swarm.allcfs
        #speak (engine, "Action server activated.")

        # self._goal = actionlib_tutorials.msg.MoveToGoal().point
        # print ("point should be", self._goal)
        # self.waypoint = np.array([self._goal.x, self._goal.y, self._goal.z])
        # self.pos = Point()
        # self.pos = self._goal

        # self.pos.x = 0.5
        # self.pos.y = 0.0
        # self.pos.z = 0.5

        # when a message of type Pose is received.
        #self.ttl1_subscriber = rospy.Subscriber('/turtle1/pose',
        #                                                Pose, self.update_pose1)

        self.cf2_subscriber = rospy.Subscriber('/tf', tf2_msgs.msg.TFMessage, self.cf2_callback)
        self.cf2_pose = Point()
        self.cf3_pose = Point()

        self.success = False

        self._feedback2 = actionlib_tutorials.msg.doTrajFeedback()
        self._result2 = actionlib_tutorials.msg.doTrajResult()
        self._action_name2 = 'trajectory_action2'
        print (self._action_name2)
        self._as2 = actionlib.SimpleActionServer(self._action_name2, actionlib_tutorials.msg.doTrajAction, execute_cb=self.execute_cb2, auto_start = False)
        self._as2.start()

        self._feedback = actionlib_tutorials.msg.my_newFeedback()
        self._result = actionlib_tutorials.msg.my_newResult()
        self._action_name = 'detect_perimeter2'
        print (self._action_name)
        self._as = actionlib.SimpleActionServer(self._action_name, actionlib_tutorials.msg.my_newAction, execute_cb=self.execute_cb, auto_start = False)
        self._as.start()
        print("Ready to send move messages.")
        self.setupKillService()



    # def update_pose1(self, data):
    #     """Callback function which is called when a new message of type Pose is
    #     received by the subscriber."""
    #     #print("UPDATE TT1")
    #     self.turtle1_pose = data
    #     self.turtle1_pose.x = round(self.turtle1_pose.x, 4)
    #     self.turtle1_pose.y = round(self.turtle1_pose.y, 4)
	#     #print("turtle1:")

    def handleKillService(self, req):
        for cf in self.allcfs.crazyflies:
            if cf.id == 2:
                print(cf.id)
                cf.cmdStop()
        #print("Returning [%s + %s = %s]"%(req.a, req.b, (req.a + req.b)))
        return 1.0

    def setupKillService(self):
        #rospy.init_node('setupKillService')
        s = rospy.Service('kill_service', actionlib_tutorials.srv.killMotors(), self.handleKillService)
        self._as.start()
        print("ready to kill.")
        #ros.AsyncSpinner.spinner(4)#; // Use 4 threads
        #spinner.start()#;
        #ros::waitForShutdown()#;
        #rospy.spin()

    def cf2_callback(self, data):

    	#cf2 is a : cf2=tf2_msgs.msg.TFMessage([t])
    	#with t : t=geometry_msgs.msg.TransformStamped()

    	#create cf to be a TransformStamped:
    	cf = data.transforms[0]
        if cf.child_frame_id == 'cf2':
            self.cf2_pose.x = cf.transform.translation.x
            self.cf2_pose.y = cf.transform.translation.y
            self.cf2_pose.z = cf.transform.translation.z
        if cf.child_frame_id == 'cf3':
            self.cf3_pose.x = cf.transform.translation.x
            self.cf3_pose.y = cf.transform.translation.y
            self.cf3_pose.z = cf.transform.translation.z
    	print("cf2_pose:", self.cf2_pose)
    	print("cf3_pose:", self.cf3_pose)

    def execute_cb2(self, goal):
        speak (engine, "Spiral trajectory.")
        traj1 = uav_trajectory.Trajectory()
        traj1.loadcsv("helicoidale.csv")
       # helper variables
        #r = rospy.Rate(10)
        rospy.wait_for_message('/tf', tf2_msgs.msg.TFMessage, timeout=None)

        # append the seeds for the fibonacci sequence
        self._feedback.time_elapsed = Duration(5)
        self.success == False

        # publish info to the console for the user
        #rospy.loginfo('%s: Now with tolerance %i with current pose [%s]' % (self._action_name, goal.order, ','.join(map(str,self._feedback.sequence))))

        # check that preempt has not been requested by the client


        # start executing the action
        # x = TurtleBot()

        TRIALS = 1
        TIMESCALE = 0.5
        for cf in self.allcfs.crazyflies:
            cf.takeoff(targetHeight=0.6, duration=3.0)
            cf.uploadTrajectory(0, 0, traj1)
            #timeHelper.sleep(2.5)
            self.allcfs.crazyflies[0].startTrajectory(0, timescale=TIMESCALE)
            #timeHelper.sleep(1.0)
            print("press button to continue...")
            self.swarm.input.waitUntilButtonPressed()

            self.allcfs.crazyflies[0].land(targetHeight=0.06, duration=2.0)
            #timeHelper.sleep(3.0)

            if self._as.is_preempt_requested():
                rospy.loginfo('%s: Preempted' % self._action_name)
                self._as.set_preempted()
                success = False
                break


            #now we test if he has reached the desired point.
        #self.takeoff_transition()


        if self.success == False:

            print ("Not yet...")

            try:

                ###self._feedback.sequence.append(currentPose)
                # publish the feedback
                self._as.publish_feedback(self._feedback)
                #rospy.loginfo('%s: Now with tolerance %i with current pose [%s]' % (self._action_name, goal.order, ','.join(map(str,self._feedback.sequence))))

            except rospy.ROSInterruptException:
                print("except clause opened")
                rospy.loginfo('Feedback did not go through.')
                pass


        if self.success == True:
            for cf in self.allcfs.crazyflies:
                #print(cf.id)
                #print("press button to continue")
                #self.swarm.input.waitUntilButtonPressed()
                cf.land(0.04, 2.5)
            print("Reached the perimeter!!")

            self._result.time_elapsed = Duration(5)
            self._result.updates_n = 1
            rospy.loginfo('My feedback: %s' % self._feedback)
            rospy.loginfo('%s: Succeeded' % self._action_name)
            self._as.set_succeeded(self._result)

    def execute_cb(self, goal):
        #speak (engine, "Moving to point.")
        rospy.wait_for_message('/tf', tf2_msgs.msg.TFMessage, timeout=None)

        self._goal = goal.point
        self.cf_id = goal.id
        print ("point should be", self._goal)
        print("id is " + str(goal.id))
        self.waypoint = np.array([self._goal.x, self._goal.y, self._goal.z])
        self._feedback.position = Pose()

        self._feedback.time_elapsed = Duration(5)
        self.success == False

        
        #speak("sending drone number " + str(goal.id) + " to x " + str(self._goal.x) + " y " + str(self._goal.y) + " z " + str(self._goal.z))
        

        speak (engine, "YO")
        for cf in self.allcfs.crazyflies:
            if cf.id == goal.id:
                print(cf.id)
                self._feedback.position.position.x = cf.position()[0]
                self._feedback.position.position.y = cf.position()[1]
                self._feedback.position.position.z = cf.position()[2]
                cf.takeoff(0.5, 5.0)
                cf.goTo(self.waypoint, yaw=0, duration=5.0)

            #now we test if he has reached the desired point.
        self.takeoff_transition()


        while self.success == False:


            if self._as.is_preempt_requested():
                rospy.loginfo('%s: Preempted' % self._action_name)
                self._as.set_preempted()
                success = False
                break

            print ("Not yet...")

            try:

                #self._feedback.updates_n.append(currentPose)
                # publish the feedback
                #self._as.publish_feedback(self._feedback)
                i = 0
                while (i < 4):
                    self._as.publish_feedback(self._feedback)
                    i+=1
                    rospy.sleep(0.1)
                #rospy.loginfo('%s: Now with tolerance %i with current pose [%s]' % (self._action_name, goal.order, ','.join(map(str,self._feedback.sequence))))

            except rospy.ROSInterruptException:
                rospy.loginfo("except clause opened")
                pass


        if self.success == True:
            #for cf in self.allcfs.crazyflies:
                #print(cf.id)
                #print("press button to continue")
                #self.swarm.input.waitUntilButtonPressed()
                #cf.land(0.04, 2.5)
            print("Reached the perimeter!!")
            self._result.time_elapsed = Duration(5)
            self._result.updates_n = 1
            rospy.loginfo('My feedback: %s' % self._feedback)
            rospy.loginfo('%s: Succeeded' % self._action_name)


            i = 0
            while (i < 4):
                self._as.set_succeeded(self._result)
                i+=1
                rospy.sleep(0.1)


            

    def euclidean_distance(self, goal_pose, id):
        """Euclidean distance between current pose and the goal."""
        if id == 2:
            print ("cf2")
            euclidean_distance= sqrt(pow((goal_pose.x - self.cf2_pose.x), 2) + pow((goal_pose.y - self.cf2_pose.y), 2) + pow((goal_pose.z - self.cf2_pose.z), 2))
        if id == 3:
            print("cf3")
            euclidean_distance= sqrt(pow((goal_pose.x - self.cf3_pose.x), 2) + pow((goal_pose.y - self.cf3_pose.y), 2) + pow((goal_pose.z - self.cf3_pose.z), 2))
        else:
            print ("no id detected... aborting?")
        #euclidean_distance= sqrt(pow((goal_pose.x - self.cf2_pose.x), 2) + pow((goal_pose.y - self.cf2_pose.y), 2) + pow((goal_pose.z - self.cf2_pose.z), 2))
        print("distance to goal is", round(euclidean_distance, 4))
        return euclidean_distance

    def takeoff_transition(self):
        distance_tolerance = 0.2
        #goal = Point()
        #goal.x = 0.0
        #goal.y = 0.0
        #goal.z = 0.
        print (self._goal)

        #while self.euclidean_distance(self._goal, self.cf_id) >= distance_tolerance:
        #    self.success = False

        if self.euclidean_distance(self._goal, self.cf_id) < distance_tolerance:
            self.success = True
            print("success is", self.success)
            #return success

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    #rospy.init_node('hi') # this is a maybe

    #swarm = Crazyswarm()
    #timeHelper = swarm.timeHelper
    #allcfs = swarm.allcfs
    print ("sup", rospy.get_name())
    perimeter_server = PerimeterMonitor(rospy.get_name())

    #server = FibonacciAction('detect_perimeter')
    rospy.spin()
