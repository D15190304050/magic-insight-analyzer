from concurrent.futures import ThreadPoolExecutor


# 定义一个任务函数，使用关键字参数
def task(message):
    print(f"Received message: {message}")
    return f"Processed: {message}"


# 主函数
def main():
    message_value = "Hello, ThreadPool!"

    # 创建线程池并提交任务
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(task, message=message_value)

        # 获取任务结果
        result = future.result()
        print(result)


if __name__ == "__main__":
    main()