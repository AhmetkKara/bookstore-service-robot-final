#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import cv2

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


class QRReader:
    def __init__(self):
        rospy.init_node("qr_reader")

        self.bridge = CvBridge()
        self.detector = cv2.QRCodeDetector()

        self.image_topic = rospy.get_param("~image_topic", "/camera/rgb/image_raw")
        self.qr_pub = rospy.Publisher("/qr_text", String, queue_size=10)

        rospy.Subscriber(self.image_topic, Image, self.image_callback)

        self.last_data = ""
        self.last_publish_time = rospy.Time.now()

        rospy.loginfo("QR Reader başladı.")
        rospy.loginfo("Image topic: %s", self.image_topic)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            data, bbox, _ = self.detector.detectAndDecode(frame)

            if data:
                now = rospy.Time.now()

                if data != self.last_data or (now - self.last_publish_time).to_sec() > 2.0:
                    rospy.loginfo("QR okundu: %s", data)
                    self.qr_pub.publish(data)
                    self.last_data = data
                    self.last_publish_time = now

        except Exception as e:
            rospy.logwarn("QR okuma hatası: %s", str(e))


if __name__ == "__main__":
    try:
        QRReader()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
