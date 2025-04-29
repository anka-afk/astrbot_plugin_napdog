from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import asyncio
import os
import shutil


@register(
    "astrbot_plugin_napdog_cleaner", "anka", "napdog, 把napcat拉的史全部吃光光", "1.0.0"
)
class NapDog(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        self.config = config
        self.clean_size = config.get("clean_size", 100)
        self.cleanup_interval = config.get("cleanup_interval", 3600)
        self.cleaning_task = None

    async def initialize(self):
        """实例化插件类后, 注册清理的异步任务"""
        # 检查环境
        in_docker = self.is_docker()
        default_path = "/napcat-cache" if in_docker else "/root/.config/QQ/NapCat/temp"
        self.napcat_cache_dir = self.config.get("napcat_cache_dir", default_path)

        self.cleaning_task = asyncio.create_task(self.schedule_cleaning())
        logger.info(
            f"[napdog] napdog插件已加载, 清理路径: {self.napcat_cache_dir}, 清理阈值: {self.clean_size}MB, 清理间隔: {self.cleanup_interval}s"
        )

    async def is_docker(self):
        """
        判断是否在容器环境中运行

        Returns:
            bool: 如果在容器环境中运行则返回True，否则返回False
        """

        if os.path.exists("/.dockerenv"):
            logger.debug("[napdog] 检测到/.dockerenv文件，确认在容器环境中")
            return True

        container_markers = ["docker", "containerd", "kubepods", "libpod", "lxc"]
        cgroup_files = ["/proc/1/cgroup", "/proc/self/cgroup"]

        for cgroup_file in cgroup_files:
            try:
                with open(cgroup_file, "r") as f:
                    content = f.read().lower()
                    if any(marker in content for marker in container_markers):
                        logger.debug(
                            f"[napdog] 在{cgroup_file}中检测到容器标记，确认在容器环境中"
                        )
                        return True
            except (IOError, FileNotFoundError):
                logger.debug(f"[napdog] 无法访问{cgroup_file}文件")

        try:
            with open("/proc/self/mountinfo", "r") as f:
                if "overlay" in f.read():
                    logger.debug("[napdog] 检测到overlay文件系统，可能在容器环境中")
                    return True
        except (IOError, FileNotFoundError):
            logger.debug("[napdog] 无法访问/proc/self/mountinfo文件")

        if os.environ.get("KUBERNETES_SERVICE_HOST"):
            logger.debug("[napdog] 检测到Kubernetes环境变量，确认在容器环境中")
            return True

        return False

    async def get_napcat_cache_size(self):
        """
        获取napcat缓存的大小

        Returns:
            float: napcat缓存的大小, 单位MB
        """

        # 获取napcat缓存目录的大小
        def get_dir_size(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

            return total_size / (1024 * 1024)

        if not os.path.exists(self.napcat_cache_dir):
            logger.warning(f"[napdog] 不存在的napcat缓存目录: {self.napcat_cache_dir}")
            return 0

        return get_dir_size(self.napcat_cache_dir)

    async def clean_napcat(self):
        """一个异步任务, 专门清理napcat的史"""
        # 检查默认路径下, napcat缓存的大小, 如果大于限制, 则删除
        napcat_cache_size = await self.get_napcat_cache_size()

        if napcat_cache_size > self.clean_size:
            logger.info(
                f"[napdog] napcat缓存大小: {napcat_cache_size}MB, 超过限制, 开始清理"
            )
            try:
                shutil.rmtree(self.napcat_cache_dir)
                logger.info(f"[napdog] 清理成功, 删除了{self.napcat_cache_dir}")
            except Exception as e:
                logger.error(f"[napdog] 清理失败: {e}")
        else:
            logger.info(
                f"[napdog] napcat缓存大小: {napcat_cache_size}MB, 未超过限制, 不需要清理"
            )
            return

        os.makedirs(self.napcat_cache_dir, exist_ok=True)

    async def schedule_cleaning(self):
        """定时清理napcat缓存的异步任务"""
        while True:
            await self.clean_napcat()
            await asyncio.sleep(self.cleanup_interval)

    async def terminate(self):
        """终止方法"""
        if self.cleaning_task and not self.cleaning_task.done():
            self.cleaning_task.cancel()
            try:
                await self.cleaning_task
            except asyncio.CancelledError:
                pass
        logger.info("[napdog] napdog插件已卸载")
