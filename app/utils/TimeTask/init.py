# 在你的主Flask应用文件中
# 假设你已经有了 app = Flask(__name__)



def init_scheduler(app):
    """初始化和配置定时任务调度器"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    import atexit

    # 导入你的任务函数
    from app.utils.TimeTask.initProviceData import getProviceBox


    scheduler = BackgroundScheduler()
    from app.utils.TimeTask.timely_box import getTimelyBox
    # 添加定时任务，每20秒执行一次
    scheduler.add_job(
        func=getProviceBox,
        trigger=IntervalTrigger(seconds=20),
        id='get_province_box',
        name='获取省份票房数据',
        replace_existing=True
    )

    scheduler.add_job(
        func=getTimelyBox,
        trigger=IntervalTrigger(seconds=20),
        id='get_timely_box',
        name='获取实时票房数据',
        replace_existing=True
    )

    # 启动调度器
    scheduler.start()

    # 确保应用终止时调度器也会关闭
    atexit.register(lambda: scheduler.shutdown())

    # 将调度器保存在app的配置中以便于其他地方访问
    app.scheduler = scheduler

    return scheduler