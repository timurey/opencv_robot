import cv2

# font
font = cv2.FONT_HERSHEY_SIMPLEX
# org
org = (80, 50)
# fontScale
fontScale = 1
# Blue color in BGR
color = (0, 0, 255)
# Line thickness of 2 px
thickness = 2


class OSDModule():
    def __init__(self, name):
        if bool(name):
            self.name = name
        else:
            self.name = "zrak"
        self.batteryCharge = [0]
        self.orgsBattery = [(420, 320), (420+1038-200, 320)]

    def setName(self, name_):
        self.name = name_

    def setBatteryCharging(self, battery, charging):
        self.batteryCharge[battery] = charging

    def doOSD(self, frame, stereo):
        frame = cv2.putText(frame, 'bat0[' + str(self.batteryCharge[0]) + '%]', self.orgsBattery[0],
                            font, fontScale, color, thickness, cv2.LINE_AA)
        if stereo==True:
            frame = cv2.putText(frame, 'bat0[' + str(self.batteryCharge[0]) + '%]', self.orgsBattery[1],
                                font, fontScale, color, thickness, cv2.LINE_AA)
        return frame


# if __name__ == "__main__":
#     osd_module = OSDModule("name")
    # body_module.main()
