import math
import socket
import threading
import time
import cv2
import d3dshot
import turbojpeg

# import pyautogui as pg
from Protocol import *


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2 ** 16 - 64
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown
    # ENCODE_PARAM_JPEG = [int(cv2.IMWRITE_JPEG_QUALITY), 50, int(cv2.IMWRITE_JPEG_PROGRESSIVE), 0,
    #                     int(cv2.IMWRITE_JPEG_OPTIMIZE), 0]
    # ENCODE_PARAM_PNG = [int(cv2.IMWRITE_PNG_COMPRESSION), 7]
    # ENCODE_PARAM_WEBP = [int(cv2.IMWRITE_WEBP_QUALITY), 101]
    JPEG = turbojpeg.TurboJPEG()

    def __init__(self, sock, addr, port):
        threading.Thread.__init__(self)
        self.s = sock
        self.scn = gpu_screenshots()
        self.signal = True
        self.datagram_builder = DatagramBuilder('!I?')
        self.seq = -1
        self.addr = addr
        self.port = port
        self.scn.start()

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        while self.signal:
            img = self.scn.get_latest_frame()[1]
            if img is not None:
                # compress_img = cv2.imencode('.jpg', img, self.ENCODE_PARAM_JPEG)[1]
                # dat = compress_img.tobytes()
                dat = self.JPEG.encode(img, quality=60)
                size = len(dat)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                raw_data = b''
                while count:
                    self.seq += 1
                    self.seq %= 1024
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    now = time.time()
                    send_data = self.datagram_builder.pack(self.seq,
                                                           True if count == 1 else False) + dat[array_pos_start:array_pos_end]
                    self.s.sendto(send_data, (self.addr, self.port))
                    array_pos_start = array_pos_end
                    count -= 1
                    # time.sleep(10)
            else:
                # print("Sleeping...")
                time.sleep(0.01)

    def stop(self):
        self.signal = False
        self.scn.stop()


class gpu_screenshots():
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=3)

    def start(self):
        self.d.capture()

    def get_latest_frame(self):
        r = self.d.get_latest_frame()
        r = cv2.cvtColor(r, cv2.COLOR_BGR2RGB) if r is not None else None
        return True if r is not None else False, r

    def stop(self):
        self.d.stop()


class StartServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.s = None
        self.fs = None
        self.signal = True
        self.remoteHost = None
        self.remotePort = None

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port = 12345
        self.s.bind(('', port))

        revcData, (self.remoteHost, self.remotePort) = self.s.recvfrom(1024)
        while revcData != b'R':
            revcData, (self.remoteHost, self.remotePort) = self.s.recvfrom(1024)
        self.s.sendto(b'A', (self.remoteHost, self.remotePort))
        revcData, (self.remoteHost, self.remotePort) = self.s.recvfrom(1024)
        while revcData != b'A':
            revcData, (self.remoteHost, self.remotePort) = self.s.recvfrom(1024)
        self.fs = FrameSegment(self.s, self.remoteHost, self.remotePort)
        self.fs.start()
        while self.signal:
            time.sleep(2)
        self.fs.stop()
        self.s.close()

    def stop(self):
        self.signal = False

    def get_addr(self):
        return self.remoteHost


def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345
    s.bind(('', port))

    revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    while revcData != b'R':
        revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    s.sendto(b'A', (remoteHost, remotePort))
    revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    while revcData != b'A':
        revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    fs = FrameSegment(s, remoteHost, remotePort)
    fs.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        fs.stop()
    s.close()


if __name__ == "__main__":
    main()