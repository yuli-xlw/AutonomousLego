########## 多线程版物体检测系统 ##########
import os
import argparse
import cv2
import numpy as np
import time
import threading
import queue
from pyboard import Pyboard
from motionLego import MotionLego

# 硬件配置
DEVICE = '/dev/ttyACM0'
BAUDRATE = 115200

# 多线程配置
FRAME_QUEUE_SIZE = 2      # 帧缓冲区大小
DETECTION_INTERVAL = 0.1  # 检测间隔（秒）
CONTROL_INTERVAL = 1.0    # 控制指令间隔

# 共享队列
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
detection_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
control_queue = queue.Queue(maxsize=1)
display_queue = queue.Queue(maxsize=1)

# 线程控制事件
exit_event = threading.Event()

class VideoStream:
    """视频采集线程"""
    def __init__(self, resolution=(640, 480), framerate=30):
        self.stream = cv2.VideoCapture(0)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(3, resolution[0])
        self.stream.set(4, resolution[1])
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if grabbed and not frame_queue.full():
                rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
                frame_queue.put(rotated_frame.copy())
            time.sleep(1/30)  # 近似帧率控制

    def stop(self):
        self.stopped = True
        self.stream.release()

class DetectionThread(threading.Thread):
    """物体检测线程"""
    def __init__(self, interpreter, input_details, output_details):
        super().__init__(daemon=True)
        self.interpreter = interpreter
        self.input_details = input_details
        self.output_details = output_details
        self.running = True

    def run(self):
        while self.running and not exit_event.is_set():
            try:
                frame = frame_queue.get(timeout=0.5)
                
                # 预处理
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, 
                                         (self.input_details[0]['shape'][2], 
                                          self.input_details[0]['shape'][1]))
                input_data = np.expand_dims(frame_resized, axis=0)
                
                # 归一化
                if self.input_details[0]['dtype'] == np.float32:
                    input_data = (np.float32(input_data) - 127.5) / 127.5
                
                # 推理
                self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                self.interpreter.invoke()
                
                # 获取结果
                boxes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
                classes = self.interpreter.get_tensor(self.output_details[3]['index'])[0]
                scores = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                
                detection_data = {
                    'frame': frame,
                    'boxes': boxes,
                    'classes': classes,
                    'scores': scores,
                    'timestamp': time.time()
                }
                detection_queue.put(detection_data)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Detection error: {e}")

    def stop(self):
        self.running = False

class ProcessingThread(threading.Thread):
    """结果处理线程"""
    def __init__(self, labels, imW, imH, min_conf):
        super().__init__(daemon=True)
        self.labels = labels
        self.imW = imW
        self.imH = imH
        self.min_conf = min_conf
        self.running = True

    def run(self):
        while self.running and not exit_event.is_set():
            try:
                data = detection_queue.get(timeout=0.5)
                frame = data['frame']
                processed_frame = frame.copy()
                
                for i in range(len(data['scores'])):
                    score = data['scores'][i]
                    if score < self.min_conf:
                        continue
                    
                    # 坐标转换
                    ymin = int(max(1, data['boxes'][i][0] * self.imH))
                    xmin = int(max(1, data['boxes'][i][1] * self.imW))
                    ymax = int(min(self.imH, data['boxes'][i][2] * self.imH))
                    xmax = int(min(self.imW, data['boxes'][i][3] * self.imW))
                    
                    # 物体信息
                    class_id = int(data['classes'][i])
                    object_name = self.labels[class_id]
                    
                    # 计算指标
                    box_area = (xmax - xmin) * (ymax - ymin)
                    area_ratio = box_area / (self.imW * self.imH)
                    center_x = (xmin + xmax) // 2
                    center_y = (ymin + ymax) // 2
                    offset_x = center_x - self.imW//2
                    offset_y = center_y - self.imH//2
                    
                    # 绘制信息
                    cv2.rectangle(processed_frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                    label = f"{object_name} {score*100:.1f}% Area:{area_ratio*100:.1f}%"
                    cv2.putText(processed_frame, label, (xmin, ymin-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                    
                    # 生成控制指令
                    if object_name in ['orange', 'person'] and control_queue.empty():
                        control_data = {
                            'object': object_name,
                            'area_ratio': area_ratio,
                            'offset_x': offset_x,
                            'timestamp': time.time()
                        }
                        control_queue.put(control_data)
                
                # 传递显示帧
                if display_queue.empty():
                    display_queue.put(processed_frame)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")

    def stop(self):
        self.running = False

class ControlThread(threading.Thread):
    """运动控制线程"""
    def __init__(self, motion_ctrl):
        super().__init__(daemon=True)
        self.motion = motion_ctrl
        self.last_ctrl = 0
        self.running = True

    def run(self):
        while self.running and not exit_event.is_set():
            try:
                data = control_queue.get(timeout=1)
                
                # 控制频率限制
                if time.time() - self.last_ctrl < CONTROL_INTERVAL:
                    continue
                
                if data['object'] == 'orange':
                    if data['area_ratio'] > 0.1:  # 面积阈值
                        self.motion.stop()
                    else:
                        offset_threshold = self.motion.imW * 0.15
                        if data['offset_x'] < -offset_threshold:
                            self.motion.left(15)
                        elif data['offset_x'] > offset_threshold:
                            self.motion.right(15)
                        else:
                            self.motion.forward(15)
                elif data['object'] == 'person':
                    self.motion.stop()
                
                self.last_ctrl = time.time()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Control error: {e}")

    def stop(self):
        self.running = False

def main():
    # 初始化硬件
    pyb = Pyboard(DEVICE, BAUDRATE)
    pyb.enter_raw_repl()
    motion = MotionLego(pyb)
    
    # 初始化模型
    interpreter = Interpreter(model_path=args.model_file)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # 启动线程
    video_stream = VideoStream(resolution=(imW, imH)).start()
    detection_thread = DetectionThread(interpreter, input_details, output_details)
    processing_thread = ProcessingThread(labels, imW, imH, min_conf_threshold)
    control_thread = ControlThread(motion)
    
    detection_thread.start()
    processing_thread.start()
    control_thread.start()
    
    # 主显示循环
    try:
        while not exit_event.is_set():
            if not display_queue.empty():
                frame = display_queue.get()
                cv2.imshow('Object Detection', frame)
            
            if cv2.waitKey(1) == ord('q'):
                exit_event.set()
                
    finally:
        # 清理资源
        video_stream.stop()
        detection_thread.stop()
        processing_thread.stop()
        control_thread.stop()
        
        detection_thread.join()
        processing_thread.join()
        control_thread.join()
        
        pyb.exit_raw_repl()
        pyb.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # 参数解析（同原代码）
    parser = argparse.ArgumentParser()
    parser.add_argument('--modeldir', required=True)
    parser.add_argument('--graph', default='detect.tflite')
    parser.add_argument('--labels', default='labelmap.txt')
    parser.add_argument('--threshold', type=float, default=0.5)
    parser.add_argument('--resolution', default='640x480')
    args = parser.parse_args()
    
    # 解析分辨率
    imW, imH = map(int, args.resolution.split('x'))
    
    # 加载标签
    with open(os.path.join(args.modeldir, args.labels), 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    if labels[0] == '???': del labels[0]
    
    main()