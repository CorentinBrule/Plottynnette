# coding: utf-8

import argparse
import cv2
import serial
import time, sys
# sys.settrace
from threadutils import run_async
import numpy as np
from bs4 import BeautifulSoup
import extracthocr
import csv
import my_gui

test_img = cv2.imread("L.png")
print(test_img)

def overlayImage(src, overlay, posx, posy):
    sHeight, sWidth, sChannels = src.shape
    oHeight, oWidth, oChannels = overlay.shape
    y1, y2 = posy, posy + overlay.shape[0]
    x1, x2 = posx, posx + overlay.shape[1]
    src[posy:posy + overlay.shape[0], posx:posx + overlay.shape[1]] = overlay

def over(src, overlay, x_offset, y_offset):
    src[y_offset:y_offset + overlay.shape[0], x_offset:x_offset + overlay.shape[1]] = overlay
    return src

class Sensor():
    def __init__(self):
        pass

class Photoresistor(Sensor):
    def __init__(self, port, baud, output_size=[100, 100]):
        self.name = "photoresistor"
        # serial attributes
        self.ser = serial.Serial()
        self.baud = baud
        self.port = port
        self.connected = False
        # image attributes
        self.output_size = output_size
        self.img = np.zeros((self.output_size[0], self.output_size[1], 3), np.uint8)
        self.capture_file = False
        self.writer = False

        self.connect()

    def init_capture(self):
        self.capture_file = open('capture-{}.csv'.format(time.strftime("%Y%m%d-%H%M%S")), 'wb')
        self.writer = csv.writer(self.capture_file)
        self.writer.writerow(["x","y","value"])

    def stop_capture(self):
        if self.capture_file:
            self.capture_file.close()


    def connect(self):
        self.ser.baudrate = self.baud
        self.ser.port = self.port
        self.ser.open()
        self.ser.flushInput()
        self.connected = True

    def disconnect(self):
        self.connected = False
        self.ser.close()
        self.stop_capture()

    def read(self):
        self.ser.write("L")
        tmp = self.ser.readline().strip()
        self.raw_value = tmp

        # self.raw_value = self.ser.readline()
        self.value = int(float(self.raw_value)/1024.0*256.0)
        # print(self.value)
        cv2.rectangle(self.img, (0,0), (self.output_size[0],self.output_size[1]), (self.value,self.value,self.value), -1)
        return self.img

    def capture(self, x, y):
        self.read()
        print(x,y,self.value)
        if not self.writer:
            self.init_capture()
        self.writer.writerow([x, y, self.value])

class Webcam(Sensor):
    def __init__(self, port):
        self.name = "webcam"
        self.cam = cv2.VideoCapture()
        self.connected = False
        self.port = port
        self.connect()

    def connect(self):
        self.cam.open(0)
        self.connected = True

    def disconnect(self):
        self.cam.release()

    def read(self):
        self.ret_val, self.img = self.cam.read()
        return self.img

    def capture(self,x,y):
        if not self.img:
            self.read()
        img_name = time.strftime("%Y%m%d-%H%M%S") + ".jpg"
        cv2.imwrite(img_name, self.img)

    def stop_capture(self):
        pass

class Mover():
    def __init__(self):
        pass


class CNC(Mover):
    """docstring for CNC."""

    def __init__(self, port, baud):  # size?
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baud
        self.connected = False
        self.step = 10

    def connect(self):
        #self.ser.baudrate = baud
        #self.ser.port = port
        self.ser.open()
        # if ser.is_open:
        self.ser.write('\r\n\r\n')
        time.sleep(2)
        self.ser.flushInput()
        self.connected = True
        print("CNC connect")

    def disconnect(self):
        self.moveToAbs(0, 0)
        self.ser.close()
        self.connected = False
        print("CNC disconnect")

    def moveToAbs(self, x, y, s=10000):
        # protection pour ne pas lancer le mouvement si la cible est en dehors du plateau ?
        if self.connected == True:
            self.ser.write("G21 G90 G01 X{} Y{} F{}\n".format(x, y, s))
            grbl_out = self.ser.readline()
            print(">" + grbl_out.strip())
        else:
            print("cnc not connected")

    def moveToRel(self, x, y, s=10000):
        if self.connected == True:
            self.ser.write("G21 G91 G01 X{} Y{} F{}\n".format(x, y, s))
            grbl_out = self.ser.readline()
            print(">" + grbl_out.strip())
        else:
            print("cnc not connected")

    def adjustZ(self, z):
        if self.connected == True:
            self.ser.write("G00 G21 G91 Z{}\n".format(z))
            grbl_out = self.ser.readline()
            print(">" + grbl_out.strip())

    def sendGcode(self, gcode):
        if self.connected:
            self.ser.write('{}\n'.format(gcode))
            grbl_out = self.ser.readline()
            print(">" + grbl_out.strip())



class Microplot():
    """docstring for Plottype."""

    def __init__(self, movers, sensors):
        self.movers = movers
        self.canvas = np.zeros((512, 512, 3), np.uint8)
        self.sensors = sensors
        self.status = ""
        self.debug = False
        self.x = 0
        self.y = 0
        self.z = 0
        self.hocr = None
        self.image = None

    @run_async
    def show_sensors(self, mirror=False):
        print("run sensors")
        while self.status is not 'QUIT' and len(self.sensors) > 0:
            for sensor in self.sensors:
                img = sensor.read()
                if mirror:
                    img = cv2.flip(img, 1)
                cv2.imshow(sensor.name, img)

    @run_async
    def capture(self,x,y):
        for sensor in self.sensors:
            sensor.capture(x, y)

    def stop_capture(self):
        for sensor in self.sensors:
            sensor.stop_capture()

    @run_async
    def take_movie(self):
        movie_name = time.strftime("%Y%m%d-%H%M%S") + ".avi"
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter(movie_name, fourcc, 30.0, (640, 480))

        while self.status is not 'QUIT' and self.cam is not None:
            ret_val, frame = self.cam.read()
            out.write(frame)


    @run_async
    def draw_canvas(self):
        print("run canvas")
        while self.status is not 'QUIT':
            canvas = np.zeros((1000, 1000, 3), np.uint8)
            if self.hocr is not None:
                if self.image is not None:
                    overlayImage(canvas, self.image, 0, 0)
            if self.status.find("SCAN") != -1:
                scanX, scanY, scanW, scanH, scanDV, scanDH = [int(c) for c in self.status[5:-1].split(",")]
                cv2.rectangle(canvas, (scanX, scanY), (scanX + scanW, scanY + scanH), (255, 0, 0))

            cv2.circle(canvas, (int(self.x), int(self.y)), 5, (0, 0, 255), -1)
            # canvas = self.sensor_on_canvas(self.sensors[0], canvas)

            cv2.imshow('canvas', canvas)
            time.sleep(0.1)

    @run_async
    def listen_event(self):
        while self.status is not "QUIT":
            self.key_event(cv2.waitKey(100))

    @run_async
    def scan(self, args):
        args = [int(a) for a in args]
        if len(args) == 7:
            xo, yo, w, h, wd, hd, steptostart = args
        else:
            xo, yo, w, h, wd, hd = args
            steptostart = 0
        x = xo
        y = yo
        hsteps = w / wd + 1
        vsteps = h / hd + 1
        steps = hsteps * vsteps
        currentVstep = 0
        currentstep = 0
        self.status = "SCAN{}".format(args)
        for vs in range(vsteps):
            if currentVstep % 2 == 0:
                x = xo
            else:
                x = wd * hsteps + xo
            for hs in range(hsteps + 1):

                if self.status == "QUIT":
                    break

                if currentstep >= steptostart:
                    self.moveToAbs(x, y)
                    # time.sleep(0.8)
                    #time.sleep(0.03)
                    self.capture(x,y)

                if currentVstep % 2 == 0:
                    x += wd
                else:
                    x -= wd
                currentstep += 1
                print(currentstep)
            y += hd
            currentVstep -= 1
        self.stop_capture()
        #self.status = "QUIT"

    @run_async
    def read(self, node):
        print(node)
        if node["class"][0] != "ocr_line":
            for l in node.find_all(attrs={"class": u"ocr_line"}):
                self.read_line(l)
        else:
            self.read_line(node)

    def sensor_on_canvas(self,sensor,canvas):
        sensor_img = sensor.img
        canvas = over(canvas, sensor_img, int(self.x), int(self.y))
        return canvas

    def read_line(self,node):
        nodecoords = extracthocr.getTitleAttribute(node, "bbox")
        print(nodecoords)
        xo = extracthocr.pixels2mm(nodecoords[0], 500)
        yo = extracthocr.pixels2mm(nodecoords[1], 500)
        w = extracthocr.pixels2mm(nodecoords[2], 500) - xo
        h = extracthocr.pixels2mm(nodecoords[3], 500) - yo
        y = yo + h / 2
        self.moveToAbs(xo, y)
        self.moveToRel(w, 0, 500)

    def connect(self):
        # port = self.tty.get()
        #port = '/dev/ttyUSB1'
        #baudrate = 115200
        self.movers[0].connect()

        self.movers[0].moveToAbs(self.x, self.y)
        # self.resetZ()

        for sensor in self.sensors:
            if sensor.connected is False:
                sensor.connect()

    def disconnect(self):
        for m in self.movers:
            m.disconnect()

    def moveToAbs(self, x, y, s=10000):
        for m in self.movers:
            m.moveToAbs(x, y, s)
        self.x = x
        self.y = y

    def moveToRel(self, x, y, s=10000):
        for m in self.movers:
            m.moveToRel(x, y, s)
        self.x += x
        self.y += y

    def adjustZ(self, z):
        for m in self.movers:
            m.adjustZ(z)
        self.z += z

    def key_event(self, key):
        if self.debug == True:
            print(key)
        if key == 1113937:
            print("left")
            self.moveToRel(-1, 0)
        if key == 1113938:
            print("top")
            self.moveToRel(0, -1)
        if key == 1113939:
            print("right")
            self.moveToRel(1, 0)
        if key == 1113940:
            print("down")
            self.moveToRel(0, 1)
        if key == 1114027:
            print("zoom")
            self.adjustZ(0.1)
        if key == 1114029:
            print("dezoom")
            self.adjustZ(-0.1)
        if key == 1048603 or key == 1048689:  # q escape
            self.status = "QUIT"
        if key == 1048675:  # c
            self.connect()
        if key == 1048676:  # d
            # self.disconnect()
            self.debug = not self.debug
        if key == 1048673:  # a
            self.capture()
        if key == 1048692:  # t
            self.test()

    def click_event(self, event, x, y, flags, param):
        if event == 7:
            self.moveToAbs(x, y)

    @run_async
    def test(self):
        '''
        #nodeGlyphs = self.hocr.find_all(attrs={"class": u"ocrx_cinfo"})
        node = self.hocr.find(attrs={"class": u"ocrx_cinfo"})
        nodecoords = extracthocr.getTitleAttribute(node, "bbox")
        x = extracthocr.pixels2mm(nodecoords[0],300)
        y = extracthocr.pixels2mm(nodecoords[1],300)
        self.moveToAbs(int(x), int(y))
        '''
        '''
        question = my_gui.Window("coucou")
        search = question.input
        resultNode = eval("self.hocr."+search)
        '''
        '''
        resultNode = self.hocr.find_all(attrs={"class": u"ocr_page"})[0]
        nodecoords = extracthocr.getTitleAttribute(resultNode, "bbox")
        print(nodecoords)
        xo = extracthocr.pixels2mm(nodecoords[0], 500)
        yo = extracthocr.pixels2mm(nodecoords[1], 500)
        w = extracthocr.pixels2mm(nodecoords[2], 500) - xo
        h = extracthocr.pixels2mm(nodecoords[3], 500) - yo
        print(nodecoords)
        print([xo,yo,w,h])
        #self.scan([xo, yo, w, h, 3, 3])
        self.read(resultNode)
        '''
        self.take_movie()


def main(args):
    sensors = []
    if args.cam is True:
        sensors.append(Webcam(""))
    if args.photo is True:
        sensors.append(Photoresistor("/dev/ttyACM0",9600))
    movers = [CNC('/dev/ttyUSB0',115200)]

    microplot = Microplot(movers, sensors)
    sensorThread = microplot.show_sensors()
    cv2.namedWindow("canvas")
    cv2.setMouseCallback("canvas", microplot.click_event)
    canvasThread = microplot.draw_canvas()
    # keyboardThread = microplot.keyboard_management()
    # microplot.key_event(cv2.waitKey(10))

    if args.scan is not None:
        microplot.connect()
        microplot.scan(args.scan)
    elif args.gcode is not None:
        microplot.connect()
        microplot.movers[0].sendGcode(args.gcode)

    if args.hocr is not None:
        with open(args.hocr, "rb") as fp:
            microplot.hocr = BeautifulSoup(fp, "lxml")
    if args.image is not None:
        img = cv2.imread(args.image, 3)
        factor = 1 / 2.5
        microplot.image = cv2.resize(img, (210, 297))

    while microplot.status is not "QUIT":
        microplot.key_event(cv2.waitKey(100))

    microplot.disconnect()
    sensorThread.join()
    canvasThread.join()
    # keyboardThread.join()

    for s in sensors:
        s.disconnect()

    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cam", action="store_true")
    parser.add_argument("--photo", action="store_true")
    parser.add_argument("-s", "--scan", help="scan a document : xorigine, yorigine, w, h, wDelta, hDelta", nargs='+')
    parser.add_argument("-g", "--gcode", help="send gcode commande")
    parser.add_argument("-i", "--image", help="add image in canvas feedback")
    parser.add_argument("--hocr", help="add hocr file")
    args = parser.parse_args()

    if args.scan is not None:
        if len(args.scan) >= 6:
            print(args.scan)
        else:
            print("invalid scan arguments")
            quit()

    main(args)
