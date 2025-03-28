import logging
import logging.config
import yaml
import os

# 获取应用程序根目录
app_root = os.path.dirname(os.path.abspath(__file__))

# 从 YAML 文件加载日志配置
with open('../logging_config.yaml', 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f.read())
    log_file_path = os.path.join(app_root, config['handlers']['file']['filename'])
    config['handlers']['file']['filename'] = log_file_path
    logging.config.dictConfig(config)


# 获取 module1、module2 和未配置的 module3 的 logger
logger1 = logging.getLogger('module1')
logger2 = logging.getLogger('module2')
logger3 = logging.getLogger('module3')  # 未在配置文件中定义

# module1 会使用特定配置
logger1.debug("This is a DEBUG message from module1")
logger1.info("This is an INFO message from module1")
logger1.warning("This is a WARNING message from module1")

# module2 会使用特定配置
logger2.debug("This is a DEBUG message from module2")  # 不会输出，因为级别是 WARNING
logger2.info("This is an INFO message from module2")  # 不会输出，因为级别是 WARNING
logger2.warning("This is a WARNING message from module2")

# module3 没有特定配置，会使用 root 的通用配置
logger3.debug("This is a DEBUG message from module3")  # 不会输出，因为级别是 INFO
logger3.info("This is an INFO message from module3")
logger3.warning("This is a WARNING message from module3")
