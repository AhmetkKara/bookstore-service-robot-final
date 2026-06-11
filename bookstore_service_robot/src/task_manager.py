#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import yaml
import os
import actionlib

from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction
from move_base_msgs.msg import MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from tf.transformations import quaternion_from_euler


class TaskManager:
    def __init__(self):
        rospy.init_node("task_manager")

        self.mission_file = rospy.get_param("~mission_file")
        self.report_file = rospy.get_param("~report_file", "/tmp/mission_report.txt")

        self.last_qr_text = ""
        rospy.Subscriber("/qr_text", String, self.qr_callback)

        self.load_mission()

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("move_base bekleniyor...")
        self.client.wait_for_server()
        rospy.loginfo("move_base hazır.")

        self.results = []

    def qr_callback(self, msg):
        self.last_qr_text = msg.data

    def load_mission(self):
        with open(self.mission_file, "r") as f:
            self.mission = yaml.safe_load(f)

        self.locations = self.mission["locations"]
        settings = self.mission.get("settings", {})

        self.move_timeout = float(settings.get("move_timeout", 90))
        self.move_retries = int(settings.get("move_retries", 1))
        self.qr_retries = int(settings.get("qr_retries", 2))
        self.qr_timeout = float(settings.get("qr_timeout", 10))

        rospy.loginfo("Mission yüklendi: %s", self.locations)

    def create_goal(self, x, y, yaw):
        q = quaternion_from_euler(0, 0, yaw)

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.position.z = 0.0

        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        return goal

    def go_to_location(self, location_name):
        goal_data = self.mission[location_name]["goal"]

        x = float(goal_data["x"])
        y = float(goal_data["y"])
        yaw = float(goal_data["yaw"])

        for attempt in range(self.move_retries + 1):
            rospy.loginfo("%s noktasına gidiliyor. Deneme: %d", location_name, attempt + 1)

            goal = self.create_goal(x, y, yaw)
            self.client.send_goal(goal)

            finished = self.client.wait_for_result(rospy.Duration(self.move_timeout))

            if not finished:
                rospy.logwarn("%s için süre doldu.", location_name)
                self.client.cancel_goal()
                rospy.sleep(1)
                continue

            state = self.client.get_state()

            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("%s noktasına ulaşıldı.", location_name)
                return True

            rospy.logwarn("%s noktasına gidilemedi. State: %s", location_name, state)
            rospy.sleep(1)

        return False

    def verify_qr(self, location_name):
        expected = self.mission[location_name]["qr_expected"]

        for attempt in range(self.qr_retries + 1):
            rospy.loginfo("QR_VERIFY: %s bekleniyor. Deneme: %d", expected, attempt + 1)

            self.last_qr_text = ""
            start_time = rospy.Time.now()

            while not rospy.is_shutdown():
                elapsed = (rospy.Time.now() - start_time).to_sec()

                if self.last_qr_text:
                    rospy.loginfo("QR okundu: %s", self.last_qr_text)

                    if self.last_qr_text.strip() == expected.strip():
                        rospy.loginfo("Görev noktası doğrulandı: %s", location_name)
                        return True
                    else:
                        rospy.logwarn("Yanlış QR. Beklenen: %s | Okunan: %s",
                                      expected, self.last_qr_text)
                        break

                if elapsed > self.qr_timeout:
                    rospy.logwarn("QR timeout: %s", location_name)
                    break

                rospy.sleep(0.2)

            rospy.sleep(1)

        return False

    def save_report(self):
        report_dir = os.path.dirname(self.report_file)

        if report_dir and not os.path.exists(report_dir):
            os.makedirs(report_dir)

        with open(self.report_file, "w") as f:
            f.write("BOOKSTORE SERVICE ROBOT MISSION REPORT\n")
            f.write("=====================================\n\n")

            for item in self.results:
                f.write("{}: {}\n".format(item["location"], item["status"]))

        rospy.loginfo("Rapor kaydedildi: %s", self.report_file)

    def run(self):
        rospy.loginfo("Task Manager başladı.")

        for location in self.locations:
            nav_success = self.go_to_location(location)

            if not nav_success:
                rospy.logerr("REPORT: %s -> FAIL", location)
                self.results.append({"location": location, "status": "FAIL"})
                continue

            qr_success = self.verify_qr(location)

            if qr_success:
                rospy.loginfo("REPORT: %s -> SUCCESS", location)
                self.results.append({"location": location, "status": "SUCCESS"})
            else:
                rospy.logwarn("REPORT: %s -> SKIPPED", location)
                self.results.append({"location": location, "status": "SKIPPED"})

        self.save_report()
        rospy.loginfo("Tüm görevler bitti.")

        rospy.loginfo("========== FINAL REPORT ==========")
        for item in self.results:
            rospy.loginfo("%s -> %s", item["location"], item["status"])


if __name__ == "__main__":
    manager = TaskManager()
    manager.run()
