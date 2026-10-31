# D3 阶段：摄像头与视频流输入采集实战全纪录

本文档汇总了 D3 阶段项目的开发需求、演进代码、核心原理分析以及 WSL2 环境下遇到的典型硬件/环境排坑经验，形成完整的项目归档。

---

## 一、 项目需求与背景

1. **目标**：实现本地 USB 摄像头（或视频源）的实时画面拉流、FPS/分辨率动态标注绘制、图形窗口实时渲染展示以及本地 MP4 视频录制落盘。
2. **开发环境**：
   * **操作系统**：WSL2 (Ubuntu 22.04 LTS)
   * **硬件连接**：通过 Windows 宿主机的 `usbipd` 挂载 USB 摄像头至 Linux 内核（`/dev/video0`）。
   * **技术栈**：Python 3, OpenCV (`cv2`), OS, Time。
3. **交付要求**：
   * 稳健的资源释放机制（使用 `try...finally` 防文件损坏）。
   * 代码逐行分析与关键排错经验总结。

---

## 二、 完整运行代码

以下为最终在 WSL2 环境下调试通过的工业级稳健代码：

```python
import os
import time
import cv2


def main():
  # 1. 初始化输出目录
  os.makedirs("outputs", exist_ok=True)

  # 2. 挂载摄像头句柄
  source = 0
  cap = cv2.VideoCapture(source)

  # 3. 关键配置：针对 WSL2 虚拟环境设置 MJPG 编码与标准分辨率
  cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

  # 4. 容灾拦截与错误日志记录
  if not cap.isOpened():
    print(
        "[Error] 无法打开摄像头或视频源！请检查 usbipd 挂载状态或视频路径。"
    )
    with open("outputs/camera_error_log.txt", "w") as f:
      f.write(
          "Error: OpenCV failed to open video source 0. "
          "Check usbipd attach status in Windows host and /dev/video0 permissions"
          " in WSL2."
      )
    return

  # 5. 动态查询摄像头实际生效的分辨率与帧率
  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  fps_input = cap.get(cv2.CAP_PROP_FPS)
  fps_input = fps_input if fps_input > 0 else 30.0
  print(f"[Info] 成功打开视频源，实际生效分辨率: {width}x{height}")

  # 6. 初始化视频录制器 (VideoWriter)
  output_path = "outputs/demo_stream.mp4"
  fourcc = cv2.VideoWriter_fourcc(*"mp4v")
  out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

  prev_time = time.time()
  current_fps = 0.0
  print(
      "[Info] 开始捕获视频流。请注意查看弹出的视频窗口，并在该窗口中按 'q'"
      " 键退出。"
  )

  try:
    while True:
      # 捕获单帧画面
      ret, frame = cap.read()

      # 帧有效性判断（先校验，后使用）
      if not ret or frame is None:
        print("[Warning] 无法获取当前帧，可能视频流已中断。")
        break

      # 实时渲染预览窗口
      cv2.imshow("Industrial Vision D3 - Live Stream", frame)

      # 计算单帧耗时与实时 FPS
      now = time.time()
      diff = now - prev_time
      if diff > 0:
        current_fps = 1.0 / diff
      prev_time = now

      # 在画面上绘制统计文字
      cv2.putText(
          frame,
          f"FPS: {current_fps:.1f}",
          (30, 40),
          cv2.FONT_HERSHEY_SIMPLEX,
          1,
          (0, 255, 0),
          2,
      )
      cv2.putText(
          frame,
          f"Res: {width}x{height}",
          (30, 80),
          cv2.FONT_HERSHEY_SIMPLEX,
          1,
          (0, 255, 0),
          2,
      )

      # 写入视频帧
      out.write(frame)

      # 监听键盘输入（必须在 GUI 窗口处于聚焦状态下按 'q' 键）
      if cv2.waitKey(1) & 0xFF == ord("q"):
        print("[Info] 用户主动退出。")
        break

  except KeyboardInterrupt:
    print("[Info] 捕获到中断信号（Ctrl+C），正在退出...")

  finally:
    # 7. 工业级安全释放机制
    if "cap" in locals() and cap.isOpened():
      cap.release()
    if "out" in locals():
      out.release()
    cv2.destroyAllWindows()
    print(f"[Info] 摄像头已安全释放，视频已保存至: {output_path}")


if __name__ == "__main__":
  main()
```

---

## 三、 遇到的典型问题与解决方案 (Troubleshooting)

### 问题 1：摄像头指示灯不亮、拉流失败或卡死
* **现象**：`cap.isOpened()` 为 `True` 或读帧卡死，硬件摄像头指示灯未开启。
* **原因**：WSL2 使用 `usbipd` 虚拟化网络交换层传输 USB 数据。OpenCV 默认请求的 **YUYV 未压缩数据流** 吞吐量巨大，超出了虚拟 USB 链路的带宽和实时性极限，导致驱动谈判失败。
* **解决**：显式指定 `MJPG` 编码格式进行硬件压缩传输，并锁定 `640x480` 标准分辨率：
  ```python
  cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  ```

### 问题 2：终端狂按 `q` 键程序无法退出
* **现象**：在终端打出一串 `qqqqqqq`，程序无反应。
* **原因**：`cv2.waitKey()` 依赖 GUI 窗口系统，只能捕获 **OpenCV 图形窗口处于最前端/被激活聚焦** 时的键盘事件。
* **解决**：确保代码中添加了 `cv2.imshow(...)` 弹窗渲染，并在脚本运行时用鼠标点击一下弹出的 GUI 窗口使其获得焦点，然后再按下 `q` 键。

### 问题 3：生成的 MP4 视频无法播放 / 提示文件损坏 (`0xC00D36C4`)
* **现象**：播放器提示“文件扩展名不正确或文件已损坏”。
* **原因**：程序在中途被强行终端终止（如强制关闭终端），导致未执行 `out.release()`。MP4 文件的容器元数据（Moov Atom 索引）未成功写入磁盘。
* **解决**：引入 `try...finally` 结构，将 `out.release()` 强行放入 `finally` 块中，无论异常与否均强制闭合文件流。

### 问题 4：在 Windows PowerShell 运行脚本导致找不到设备
* **现象**：报错 `Failed list devices for backend dshow / Camera index out of range`。
* **原因**：`usbipd` 已将硬件交由 Linux 控制，若使用 Windows 端的 Python 解释器运行，Windows 宿主系统自然找不到已被绑定的设备。
* **解决**：必须在 **WSL2 Ubuntu 终端** 中激活虚拟环境（`source venv/bin/activate`）并由 Linux 原生 Python 执行脚本。

---

## 四、 关键设计细节与工业最佳实践

### 1. 为什么 `cap.set()` 后仍需使用 `cap.get()` 确认？
* **原理**：`cap.set()` 是对硬件的**申请**而非强制指令。如果摄像头硬件/驱动不支持请求的分辨率，它会自动回退到系统默认值。
* **风险**：若后续硬编码 `width = 640` 并传入 `VideoWriter`，而摄像头吐出的图像矩阵实际为 `1280x720`，会导致 `out.write(frame)` 尺寸不匹配，进而引发录像崩溃或输出文件损坏。
* **规则**：**先申请 (`set`)，后确认 (`get`)**，确保 `VideoWriter` 的参数永远与底层吐出的矩阵尺寸动态一致。

### 2. `cv2.imshow` 的顺序放置原则
* **规则**：**必须先校验 `ret` 与 `frame` 是否有效，后调用 `cv2.imshow`**。
* **原因**：若在 `frame is None` 的情况下直接执行 `imshow`，OpenCV 底层 C++ 断言将直接触发报错并导致进程崩塌退出。