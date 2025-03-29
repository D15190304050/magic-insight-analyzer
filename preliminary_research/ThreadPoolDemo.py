from concurrent.futures import ThreadPoolExecutor
import time


# 定义一个模拟任务函数
def task(n):
    print(f"Task {n} is starting...")
    time.sleep(2)  # 模拟耗时操作
    print(f"Task {n} is completed.")
    return f"Result of task {n}"


# 使用线程池执行任务
def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交多个任务到线程池
        futures = [executor.submit(task, i) for i in range(5)]

        # 获取每个任务的结果
        for future in futures:
            print(future.result())


if __name__ == "__main__":
    main()