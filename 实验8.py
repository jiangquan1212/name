import cv2
import numpy as np
import os

# ========== 1. 设置文件路径（在这里修改你的路径）==========
# YOLO模型文件路径
cfg_path = r'D:\PythonProject2\data\class8-yolo\yolo-coco\yolov3.cfg'  # ← 修改为你的yolov3.cfg路径
weights_path = r'D:\PythonProject2\data\class8-yolo\yolo-coco\yolov3.weights'  # ← 修改为你的yolov3.weights路径
names_path = r'D:\PythonProject2\data\class8-yolo\yolo-coco\coco.names'  # ← 修改为你的coco.names路径

# 视频文件路径
video_path = r'D:\PythonProject2\data\class8-yolo\in.mp4'  # ← 修改为你的输入视频路径
output_path = r'D:\PythonProject2\data\class8-yolo\out_new.mp4'  # ← 修改为你的输出视频路径

# 检查文件是否存在
for path, name in [(cfg_path, "cfg文件"), (weights_path, "权重文件"), (names_path, "类别文件")]:
    if not os.path.exists(path):
        print(f"错误：找不到{name} - {path}")
        exit()

if not os.path.exists(video_path):
    print(f"错误：找不到视频文件 - {video_path}")
    exit()

print("所有文件加载成功")

# ========== 2. 设置参数 ==========
conf_threshold = 0.5  # 置信度阈值
nms_threshold = 0.4  # NMS阈值

# ========== 3. 加载YOLO模型 ==========
net = cv2.dnn.readNet(weights_path, cfg_path)

# 获取输出层名称
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# ========== 4. 加载类别名称 ==========
with open(names_path, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

print(f"模型加载成功，可检测 {len(classes)} 种类别")

# ========== 5. 读取视频 ==========
cap = cv2.VideoCapture(video_path)

# 获取视频属性
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"视频信息: {width}x{height}, {fps}fps, 总帧数: {total_frames}")

# ========== 6. 创建视频保存对象 ==========
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# ========== 7. 处理视频帧 ==========
frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 30 == 0:
        print(f"处理进度: {frame_count}/{total_frames}")

    h, w = frame.shape[:2]

    # 构建blob
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)

    # 前向传播
    outputs = net.forward(output_layers)

    # 解析输出
    boxes = []
    confidences = []
    class_ids = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > conf_threshold:
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                width_box = int(detection[2] * w)
                height_box = int(detection[3] * h)

                x = int(center_x - width_box / 2)
                y = int(center_y - height_box / 2)

                boxes.append([x, y, width_box, height_box])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # NMS非极大值抑制
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # 绘制检测结果
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w_box, h_box = boxes[i]
            label = f"{classes[class_ids[i]]}: {confidences[i]:.2f}"

            # 绘制边框
            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            # 绘制标签背景
            cv2.rectangle(frame, (x, y - 20), (x + len(label) * 12, y), (0, 255, 0), -1)
            # 绘制标签文字
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    # 写入输出视频
    out.write(frame)

    # 显示（可选，会降低处理速度）
    # cv2.imshow("YOLO Detection", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# ========== 8. 释放资源 ==========
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"\n处理完成！")
print(f"输出视频已保存至: {output_path}")