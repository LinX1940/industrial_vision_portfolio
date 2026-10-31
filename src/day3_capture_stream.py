import os
import time 
import cv2
def main():
    os.makedirs("outputs",exist_ok=True)
    source=0
    cap=cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("[Error]无法打开摄像头或视频源！请检查usbipd挂载状态或视频路径")
        with open("outputs/camera_error_log.txt","w")as f:
            f.write(
                "Error: OpenCV failed to open video source 0. "
                "Check usbipd attach status in Windows host and /dev/video0 permissions"
                " in WSL2."
            )
        return
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_input=cap.get(cv2.CAP_PROP_FPS)
    fps_input=fps_input if fps_input>0 else 30.0    
    print(f"[Info]成功打开视频源 分辨率:{width}*{height}")
    output_path="outputs/demo_stream.mp4"
    fourcc=cv2.VideoWriter_fourcc(*"mp4v")
    out=cv2.VideoWriter(output_path,fourcc,20.0,(width,height))
    prev_time=time.time()
    current_fps=0.0
    print("[Info] 开始捕获视频流。按 'q' 键可随时退出并保存视频。")
    try:
        while True:
            ret,frame=cap.read()
            if not ret or frame is None:
                print("Warning 无法获取当前帧 可能视频流已中断")
                break
            cv2.imshow("Industrial Vision D3 - Live Stream", frame)
            now=time.time()
            diff=now-prev_time
            if diff>0:
                current_fps=1.0/diff
            prev_time=now
            cv2.putText(
                frame,
                f"FPS{current_fps:.1f}",
                (30,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
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
            out.write(frame)
        # 按 'q' 键退出循环
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[Info] 用户主动退出。")
                break

    except KeyboardInterrupt:
        print("[Info] 捕获到中断信号（Ctrl+C），正在退出...")
    finally:
    # 安全释放所有句柄
        if "cap" in locals() and cap.isOpened():
            cap.release()
        if "out" in locals():
            out.release()
        cv2.destroyAllWindows()
        print(f"[Info] 摄像头已安全释放，视频已保存至: {output_path}")


if __name__ == "__main__":
  main()
