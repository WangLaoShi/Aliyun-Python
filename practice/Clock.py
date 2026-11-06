from time import localtime, sleep

# 终端 ANSI 色：时 / 分 / 秒 各一色（macOS / Linux 默认终端可用）
_COLOR_H = "\033[91m"  # 亮红 — 时
_COLOR_M = "\033[92m"  # 亮绿 — 分
_COLOR_S = "\033[94m"  # 亮蓝 — 秒
_RESET = "\033[0m"


class Clock(object):
    """ 数字时钟 """

    def __init__(self, hour=0, minute=0, second=0):
        """
        初始化方法
        :param hour: 时
        :param minute: 分
        :param second: 秒
        """
        self._hour = hour
        self._minute = minute
        self._second = second

    @classmethod
    def now(cls):
        """用本地系统当前时间构造时钟。"""
        # localtime() 不带参数：返回“此刻”的本地时间，类型是 time.struct_time（像一个小结构体）
        t = localtime()
        # t.tm_hour / tm_min / tm_sec 分别是 时、分、秒（都是整数）
        # cls(...) 等价于用当前类去调构造函数 Clock(时, 分, 秒)，得到一个新的 Clock 对象并返回
        return cls(t.tm_hour, t.tm_min, t.tm_sec)

    def run(self):
        """ 走字 """
        self._second += 1
        if self._second == 60:
            self._second = 0
            self._minute += 1
            if self._minute == 60:
                self._minute = 0
                self._hour += 1
                if self._hour == 24:
                    self._hour = 0

    def show(self, *, color: bool = True) -> str:
        """
        显示时间。``color=True`` 时返回带 ANSI 颜色的字符串（时/分/秒三色，冒号为默认色）。
        """
        h, m, s = self._hour, self._minute, self._second
        if not color:
            return "%02d:%02d:%02d" % (h, m, s)
        return (
            f"{_COLOR_H}{h:02d}{_RESET}"
            f":{_COLOR_M}{m:02d}{_RESET}"
            f":{_COLOR_S}{s:02d}{_RESET}"
        )


def main():
    clock = Clock.now()
    while True:
        # \r 回到行首 + end='' 不换行，同一行刷新；末尾空格可清掉上次多出的字符
        print(f"\r{clock.show()}", end="", flush=True)
        sleep(1)
        clock.run()

if __name__ == '__main__':
    main()
