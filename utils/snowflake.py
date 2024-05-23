import datetime
import time
import string
from config.config import settings

"""
  簡化版的雪花算法
  可以用來產生 1 到 2^64-1 之間的 ID
  使用 41 位時間戳 + 8 位序列號，以生成 6 位短網址
"""

# 定義Base62字符集
BASE62 = string.digits + string.ascii_letters
BASE62_MAX_VALUE = 62**6  # 56800235584

# 雪花算法起始時間
SINCE_TIMESTAMP = int(
    time.mktime(
        datetime.datetime.strptime(
            settings.SNOWFLAKE_SINCE_TIME, "%Y-%m-%dT%H:%M:%SZ"
        ).timetuple()
    )
)


class SimplifiedSnowflake:
    def __init__(self, sequence=0):
        self.sequence = sequence
        self.epoch = SINCE_TIMESTAMP  # 自定義的開始時間
        self.sequence_bits = 8  # 只使用8位的序列號
        self.timestamp_bits = 41  # 使用41位的時間戳

        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)
        self.timestamp_shift = self.sequence_bits

        self.last_timestamp = -1  # 上一次生成 ID 的時間戳

    def _current_time(self):
        return int(time.time() * 1000)

    # 等待下一個毫秒，以防當前毫秒的序列號已經用完
    def _wait_for_next_millis(self, last_timestamp):
        timestamp = self._current_time()
        while timestamp <= last_timestamp:
            timestamp = self._current_time()
        return timestamp

    # 產生一個新的 id
    def generate_id(self):
        timestamp = self._current_time()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id")

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self._wait_for_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        id = (timestamp - self.epoch) << self.timestamp_shift | self.sequence
        return id


# 將10進制數字轉換為Base62
def encode_base62(num):
    if num == 0:
        return BASE62[0]
    arr = []
    base = len(BASE62)
    while num:
        num, rem = divmod(num, base)
        arr.append(BASE62[rem])
    arr.reverse()
    return "".join(arr)


# 產生短網址，6碼Base62
def generate_short_url(id):
    num = id % BASE62_MAX_VALUE
    short_url = encode_base62(num)
    return short_url.zfill(6)


simple_snowflake_generator = SimplifiedSnowflake()
