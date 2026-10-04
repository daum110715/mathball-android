"""数学球砸砖块 —— 单文件 pygame 竖屏小游戏。"""

import sys
import os
import math
import json
import random
from enum import Enum, auto
from functools import lru_cache

import pygame


# ============================================================
# 常量
# ============================================================
W, H = 720, 1280
FPS = 30
GAME_DURATION = 90.0

IS_MOBILE = sys.platform in ("android", "ios") or "ANDROID_ARGUMENT" in os.environ

GRAVITY = 1600.0
MAX_BALL_SPEED = 1200.0
MAX_COLLISION_SUBSTEPS = 12
VX_DAMPING = 0.985
BALL_RADIUS = 45

BRICK_W = 660
BRICK_H = 90
BRICK_GAP_Y = 35
BRICK_START_Y = 220

BRICK_EXPONENT_POOL = (3, 6, 9, 12, 15, 18, 21, 24)
DEFAULT_BRICK_EXPONENTS = (3, 6, 9, 12, 15, 18)

CHIP_W = 100
CHIP_H = 50
CHIP_GAP_X = 12
CHIP_GAP_Y = 10
CHIP_PAD = 16
CHIP_TITLE_H = 30
_CHIP_PER_ROW = max(
    1, (W - 2 * CHIP_PAD + CHIP_GAP_X) // (CHIP_W + CHIP_GAP_X)
)
CHIP_ROWS_MAX = (len(BRICK_EXPONENT_POOL) + _CHIP_PER_ROW - 1) // _CHIP_PER_ROW
CHIP_PANEL_TOP = 240
CHIP_PANEL_H = (CHIP_TITLE_H
                + CHIP_ROWS_MAX * CHIP_H
                + max(0, CHIP_ROWS_MAX - 1) * CHIP_GAP_Y
                + CHIP_PAD)
CHIP_PANEL_BOTTOM = CHIP_PANEL_TOP + CHIP_PANEL_H
TABS_TOP = CHIP_PANEL_BOTTOM + 10
TAB_H = 50
LIST_TOP_DEFAULT = TABS_TOP + TAB_H + 10

_BACK_KEYS = {pygame.K_ESCAPE, pygame.K_BACKSPACE}
if hasattr(pygame, "K_AC_BACK"):
    _BACK_KEYS.add(pygame.K_AC_BACK)

BRICK_HP_MAX = 1000
MIN_DAMAGE = 10

BOUNCE_VY = -400.0
KILL_BOUNCE_VY = -300.0
SHIELD_BOUNCE_VY = -150.0
SIDE_BOUNCE_DAMPING = 0.9
BOTTOM_BOUNCE_DAMPING = 0.7
SHIELD_PIERCE_RATIO = 0.3

MINION_DAMPING = 0.99
MINION_MAX_SPEED = 1200.0
MINION_INITIAL_VY = -50.0
MINION_DAMAGE_RATIO = 0.15
MINION_BOUNCE_DAMPING = 0.8
MINION_SIDE_RATIO = 1.5

MAX_N = 2000
MAX_VALUE = 10 ** 30

EXPECTED_BALL_COUNT = 30
SKILL_TIMER_CLEANUP_THRESHOLD = 40

SPLIT_X = W // 2
SPLIT_W = 20
BATTLE_BRICK_W = 320
BATTLE_BRICK_H = 70
BATTLE_BRICK_GAP_Y = 20
BATTLE_TRACK_TOP = 400
BATTLE_TRACK_BOTTOM = H - 30
BATTLE_TRACK_A_LEFT = 15
BATTLE_TRACK_A_RIGHT = SPLIT_X - SPLIT_W // 2 - 15
BATTLE_TRACK_B_LEFT = SPLIT_X + SPLIT_W // 2 + 15
BATTLE_TRACK_B_RIGHT = W - 15
BATTLE_LANE_A_LEFT = BATTLE_TRACK_A_LEFT
BATTLE_LANE_A_RIGHT = BATTLE_TRACK_A_RIGHT
BATTLE_LANE_B_LEFT = BATTLE_TRACK_B_LEFT
BATTLE_LANE_B_RIGHT = BATTLE_TRACK_B_RIGHT
BATTLE_HP_CAP_RATIO = 1.5
BATTLE_SEPARATOR_COLOR = (40, 30, 60)
BATTLE_FLAG_COLOR = (230, 230, 230)
BATTLE_FLAG_POLE = (140, 140, 140)
BATTLE_TRACK_BG_COLOR = (25, 30, 46)

COLOR_BG = (15, 15, 30)
COLOR_WHITE = (255, 255, 255)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_DIM = (180, 180, 180)
COLOR_TEXT_DARK = (120, 130, 160)
COLOR_BTN_GREEN = (80, 200, 120)
COLOR_BTN_BLUE = (50, 70, 100)
COLOR_BTN_RED = (200, 90, 90)
COLOR_BTN_GRAY = (70, 70, 90)
COLOR_CAT_HOVER = (60, 90, 120)
COLOR_CAT_NORMAL = (35, 45, 65)
COLOR_PLAYER_A = (120, 220, 150)
COLOR_PLAYER_B = (255, 180, 140)

CATEGORY_COLORS = [(100, 200, 150), (100, 180, 255), (255, 120, 150)]

FONT_HUGE = 70
FONT_BIG = 50
FONT_MID = 34
FONT_SMALL = 24
FONT_TINY = 18


# ============================================================
# 数学序列
# ============================================================
_SEQUENCES = {}


def register_sequence(key):
    def deco(fn):
        _SEQUENCES[key] = fn
        return fn
    return deco


@lru_cache(maxsize=4096)
def _factorial(n):
    return math.factorial(n) if n <= 500 else float('inf')


@lru_cache(maxsize=4096)
def _fibonacci(n):
    if n > 300:
        return float('inf')
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@lru_cache(maxsize=4096)
def _lucas(n):
    if n > 300:
        return float('inf')
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@lru_cache(maxsize=4096)
def _padovan(n):
    if n > 300:
        return float('inf')
    a, b, c = 1, 1, 1
    for _ in range(n):
        a, b, c = b, c, a + b
    return a


@lru_cache(maxsize=4096)
def _prime(n):
    if n > 5000:
        return float('inf')
    count, num = 0, 1
    while count < n:
        num += 1
        if all(num % j for j in range(2, int(num ** 0.5) + 1)):
            count += 1
    return num


@lru_cache(maxsize=4096)
def _catalan(n):
    return math.comb(2 * n, n) // (n + 1) if n <= 500 else float('inf')


@lru_cache(maxsize=4096)
def _bell(n):
    if n > 100:
        return float('inf')
    t = [[0] * (n + 1) for _ in range(n + 1)]
    t[0][0] = 1
    for i in range(1, n + 1):
        t[i][0] = t[i - 1][i - 1]
        for j in range(1, i + 1):
            t[i][j] = t[i - 1][j - 1] + t[i][j - 1]
    return t[n][0]


@lru_cache(maxsize=4096)
def _partition(n):
    if n > 300:
        return float('inf')
    p = [0] * (n + 1)
    p[0] = 1
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            p[j] += p[j - i]
    return p[n]


@lru_cache(maxsize=4096)
def _derangement(n):
    if n == 0:
        return 1
    if n == 1:
        return 0
    if n > 500:
        return float('inf')
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, (i - 1) * (a + b)
    return b


@lru_cache(maxsize=4096)
def _super_fact(n):
    if n > 30:
        return float('inf')
    r = 1
    for i in range(1, n + 1):
        r *= math.factorial(i)
    return r


@lru_cache(maxsize=4096)
def _double_fact(n):
    if n > 300:
        return float('inf')
    r = 1
    for i in range(n, 0, -2):
        r *= i
    return r


@lru_cache(maxsize=4096)
def _triple_fact(n):
    if n > 300:
        return float('inf')
    r = 1
    for i in range(n, 0, -3):
        r *= i
    return r


@lru_cache(maxsize=4096)
def _euler_num(n):
    if n > 100:
        return float('inf')
    e = [0] * (n + 1)
    e[0] = 1
    for i in range(1, n + 1):
        e[i] = sum(math.comb(i - 1, j) * e[j] * e[i - 1 - j] for j in range(i))
    return e[n]


@lru_cache(maxsize=4096)
def _motzkin(n):
    if n > 100:
        return float('inf')
    m = [0] * (n + 1)
    m[0] = 1
    for i in range(1, n + 1):
        if i == 1:
            m[1] = 1
        else:
            m[i] = ((2 * i + 1) * m[i - 1] + (3 * i - 3) * m[i - 2]) // (i + 2)
    return m[n]


@lru_cache(maxsize=4096)
def _stirling(n):
    if n > 100:
        return float('inf')
    k = n // 2
    s = 0
    for j in range(k + 1):
        s += ((-1) ** j) * math.comb(k, j) * (k - j) ** n
    return s // math.factorial(k)


@lru_cache(maxsize=4096)
def _fact_sum(n):
    return sum(math.factorial(i) for i in range(1, n + 1)) if n <= 100 else float('inf')


@lru_cache(maxsize=4096)
def _dfact_sum(n):
    if n > 200:
        return float('inf')
    s = 0
    for i in range(1, n + 1):
        r = 1
        for j in range(i, 0, -2):
            r *= j
        s += r
    return s


@lru_cache(maxsize=4096)
def _catalan_sum(n):
    if n > 200:
        return float('inf')
    return sum(math.comb(2 * i, i) // (i + 1) for i in range(1, n + 1))


@lru_cache(maxsize=4096)
def _bell_sum(n):
    if n > 50:
        return float('inf')
    s = 0
    for i in range(1, n + 1):
        b = [0] * (i + 1)
        b[0] = 1
        for _i in range(1, i + 1):
            b[_i] = sum(math.comb(_i - 1, j) * b[j] for j in range(_i))
        s += b[i]
    return s


@lru_cache(maxsize=4096)
def _euler_phi(n):
    if n <= 0:
        return 0
    res, temp, p = n, n, 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            res -= res // p
        p += 1
    if temp > 1:
        res -= res // temp
    return res


@lru_cache(maxsize=4096)
def _mobius(n):
    s = 0
    for i in range(1, n + 1):
        temp, p, cnt, sq = i, 2, 0, False
        while p * p <= temp:
            if temp % p == 0:
                c = 0
                while temp % p == 0:
                    temp //= p
                    c += 1
                if c > 1:
                    sq = True
                    break
                cnt += 1
            p += 1
        if sq:
            mu = 0
        else:
            if temp > 1:
                cnt += 1
            mu = (-1) ** cnt
        s += mu
    return s


def _bind_all_sequences():
    register_sequence("factorial")(_factorial)
    register_sequence("square")(lambda n: n * n)
    register_sequence("cube")(lambda n: n ** 3)
    register_sequence("fourth_power")(lambda n: n ** 4)
    register_sequence("fifth_power")(lambda n: n ** 5)
    register_sequence("exponential")(lambda n: 2 ** n if n <= 100 else float('inf'))
    register_sequence("fibonacci")(_fibonacci)
    register_sequence("lucas")(_lucas)
    register_sequence("padovan")(_padovan)
    register_sequence("double_fact")(_double_fact)
    register_sequence("triple_fact")(_triple_fact)
    register_sequence("power_tower")(lambda n: n ** n if n <= 50 else float('inf'))
    register_sequence("triangular")(lambda n: n * (n + 1) // 2)
    register_sequence("prime")(_prime)
    register_sequence("catalan")(_catalan)
    register_sequence("super_fact")(_super_fact)
    register_sequence("bell")(_bell)
    register_sequence("derangement")(_derangement)
    register_sequence("euler_num")(_euler_num)
    register_sequence("motzkin")(_motzkin)
    register_sequence("stirling")(_stirling)
    register_sequence("partition")(_partition)
    register_sequence("euler_phi")(_euler_phi)
    register_sequence("fact_sum")(_fact_sum)
    register_sequence("dfact_sum")(_dfact_sum)
    register_sequence("catalan_sum")(_catalan_sum)
    register_sequence("bell_sum")(_bell_sum)
    register_sequence("square_sum")(lambda n: n * (n + 1) * (2 * n + 1) // 6)
    register_sequence("geo_sum")(lambda n: 2 ** (n + 1) - 2 if n <= 100 else float('inf'))
    register_sequence("mobius")(_mobius)


_bind_all_sequences()

_NON_MONOTONIC = {"euler_phi", "mobius"}


def get_value(n, b_type):
    if n <= 0:
        return 0
    if n > MAX_N:
        return float('inf')
    fn = _SEQUENCES.get(b_type)
    if fn is None:
        return n
    try:
        v = fn(n)
    except Exception:
        return float('inf')
    if isinstance(v, (int, float)) and v > MAX_VALUE:
        return float('inf')
    return v


def get_text(n, b_type):
    m = {
        "factorial": f"{n}!", "square": f"{n}^2", "cube": f"{n}^3",
        "fourth_power": f"{n}^4", "fifth_power": f"{n}^5",
        "exponential": f"2^{n}", "fibonacci": f"F{n}", "lucas": f"L{n}",
        "padovan": f"P{n}", "double_fact": f"{n}!!", "triple_fact": f"{n}!!!",
        "power_tower": f"{n}^{n}", "triangular": f"T{n}", "prime": f"P{n}",
        "catalan": f"C{n}", "super_fact": f"sf{n}", "bell": f"B{n}",
        "derangement": f"D{n}", "euler_num": f"E{n}", "motzkin": f"M{n}",
        "stirling": f"S{n}", "partition": f"p{n}", "euler_phi": f"phi({n})",
        "fact_sum": f"Sum{n}!", "dfact_sum": f"Sum{n}!!",
        "catalan_sum": f"SumC{n}", "bell_sum": f"SumB{n}",
        "square_sum": f"Sum{n}^2", "geo_sum": f"Sum2^{n}",
        "mobius": f"mu({n})",
    }
    return m.get(b_type, str(n))


def format_value(v):
    if v == float('inf'):
        return "∞"
    if v >= 10 ** 9:
        e = int(math.log10(v))
        return f"{v / 10 ** e:.2f}e{e}"
    return str(v)


@lru_cache(maxsize=64)
def _scan_max(b_type):
    best, best_n = -float('inf'), 1
    for n in range(1, 201):
        v = get_value(n, b_type)
        if v != float('inf') and v > best:
            best, best_n = v, n
    for n in range(200, MAX_N + 1, 5):
        v = get_value(n, b_type)
        if v != float('inf') and v > best:
            best, best_n = v, n
    lo = max(1, best_n - 5)
    hi = min(MAX_N, best_n + 5)
    for n in range(lo, hi + 1):
        v = get_value(n, b_type)
        if v != float('inf') and v > best:
            best, best_n = v, n
    return best, best_n


@lru_cache(maxsize=128)
def precompute_brick_needs(
    b_type,
    exponents=DEFAULT_BRICK_EXPONENTS,
    max_n=MAX_N,
):
    results = []
    non_mono = b_type in _NON_MONOTONIC

    if non_mono:
        global_max, _ = _scan_max(b_type)
        if global_max <= 0:
            return tuple((e, max_n, float('inf')) for e in exponents)
    else:
        global_max = float('inf')

    for exp in exponents:
        target = 10 ** exp
        if non_mono and target > global_max:
            results.append((exp, max_n, float('inf')))
            continue
        if not non_mono:
            lo, hi = 1, max_n
            while lo < hi:
                mid = (lo + hi) // 2
                v = get_value(mid, b_type)
                if v == float('inf') or v >= target:
                    hi = mid
                else:
                    lo = mid + 1
            need_n = lo
        else:
            need_n = max_n
            for n in range(1, max_n + 1):
                v = get_value(n, b_type)
                if v != float('inf') and v >= target:
                    need_n = n
                    break
        reached = get_value(need_n, b_type)
        if reached == float('inf') or reached < target:
            results.append((exp, need_n, float('inf')))
        else:
            results.append((exp, need_n, reached))
    return tuple(results)


def validate_data(ball_keys):
    return [k for k in ball_keys if k not in _SEQUENCES]


def list_registered_sequences():
    return sorted(_SEQUENCES.keys())


# ============================================================
# 数据：30 个球
# ============================================================
CATEGORIES = [
    {
        "name": "慢速增长", "desc": "多项式级别，增长平缓",
        "color": CATEGORY_COLORS[0],
        "balls": [
            {"key": "square", "name": "平方球", "formula": "n^2",
             "skill": "【专属技能】四两拨千斤\n砸中砖块时，有 25% 概率造成一次等同当前数值的额外伤害。"},
            {"key": "cube", "name": "立方球", "formula": "n^3",
             "skill": "【专属技能】体积压制\n立方球的冲击力惊人，砸碎砖块时震屏效果更强。"},
            {"key": "fourth_power", "name": "四次方球", "formula": "n^4",
             "skill": "【专属技能】降维打击\n无视砖块 10% 的数值要求，更容易砸碎高数值砖块。"},
            {"key": "fifth_power", "name": "五次方球", "formula": "n^5",
             "skill": "【专属技能】层层递进\n连续砸碎 2 个砖块后，第三次砸击的数值额外增加 20%。"},
            {"key": "triangular", "name": "三角数球", "formula": "T(n)",
             "skill": "【专属技能】聚沙成塔\n每次被弹开时，积累一层“沙粒”，砸碎砖块时一次性释放额外伤害。"},
            {"key": "prime", "name": "素数球", "formula": "P(n)",
             "skill": "【专属技能】不可整除\n球值与砖块要求互质时，一击必杀。"},
            {"key": "euler_phi", "name": "欧拉函数球", "formula": "phi(n)",
             "skill": "【专属技能】互素穿透\n砸击时有 20% 概率降低砖块 20% 的数值要求。"},
            {"key": "mobius", "name": "莫比乌斯球", "formula": "mu(n)",
             "skill": "【专属技能】反转乾坤\n每次被弹开时，将砖块的要求值降低 10%。"},
            {"key": "partition", "name": "整数划分球", "formula": "p(n)",
             "skill": "【专属技能】分裂重击\n砸碎砖块时，会分裂出一个小分身自动寻找下一行砖块。"},
            {"key": "euler_num", "name": "欧拉数球", "formula": "E(n)",
             "skill": "【专属技能】锯齿震荡\n砸击时球体震荡，对周围 3 格内的砖块造成 50% 溅射伤害。"},
        ],
    },
    {
        "name": "中速增长", "desc": "指数级别，增长适中",
        "color": CATEGORY_COLORS[1],
        "balls": [
            {"key": "exponential", "name": "指数球", "formula": "2^n",
             "skill": "【专属技能】指数爆炸\n每砸碎一个砖块，下一次下落速度加快 30%。"},
            {"key": "fibonacci", "name": "斐波那契球", "formula": "F(n)",
             "skill": "【专属技能】黄金螺旋\n球体按螺旋轨迹下落，轨迹上的砖块会受到连续碰撞判定。"},
            {"key": "lucas", "name": "卢卡斯球", "formula": "L(n)",
             "skill": "【专属技能】双生共鸣\n砸中砖块时额外造成 15% 最大血量的共鸣伤害。"},
            {"key": "padovan", "name": "帕多瓦球", "formula": "P(n)",
             "skill": "【专属技能】钢筋铁骨\n被弹开时强化向上速度，不损失反弹能量。"},
            {"key": "double_fact", "name": "双阶乘球", "formula": "n!!",
             "skill": "【专属技能】双重打击\n砸碎砖块时，额外对上方砖块造成 30% 伤害。"},
            {"key": "triple_fact", "name": "三阶乘球", "formula": "n!!!",
             "skill": "【专属技能】三重奏\n球体周围环绕 3 个小型卫星球，自动撞击相邻的砖块。"},
            {"key": "power_tower", "name": "幂塔球", "formula": "n^n",
             "skill": "【专属技能】幂次叠加\n每次砸碎砖块，永久提升 10% 的伤害倍率。"},
            {"key": "motzkin", "name": "默慈金球", "formula": "M(n)",
             "skill": "【专属技能】弦之舞\n被弹开时，向屏幕另一侧横向冲击。"},
            {"key": "derangement", "name": "错排球", "formula": "D(n)",
             "skill": "【专属技能】错位闪避\n有 20% 概率削弱反弹速度，直接继续下落。"},
            {"key": "square_sum", "name": "平方和球", "formula": "Sum n^2",
             "skill": "【专属技能】金字塔之力\n每砸碎砖块获得 1 层护盾，可抵挡一次弱弹开。"},
            {"key": "geo_sum", "name": "几何级数球", "formula": "Sum 2^n",
             "skill": "【专属技能】复利增长\n每次成功砸击，永久提升 5% 的伤害。"},
            {"key": "fact_sum", "name": "阶乘和球", "formula": "Sum n!",
             "skill": "【专属技能】全排列打击\n每砸碎砖块，随机召唤一个残影对随机砖块造成 20% 伤害。"},
            {"key": "dfact_sum", "name": "双阶乘和球", "formula": "Sum n!!",
             "skill": "【专属技能】能量累积\n每被弹开一次积累 1 层能量，满 5 层伤害翻倍。"},
            {"key": "catalan_sum", "name": "卡特兰和球", "formula": "Sum C(n)",
             "skill": "【专属技能】括号护盾\n开局获得一层护盾，可抵挡一次数值不够的反弹。"},
        ],
    },
    {
        "name": "快速增长", "desc": "阶乘/超指数级，爆炸增长",
        "color": CATEGORY_COLORS[2],
        "balls": [
            {"key": "factorial", "name": "阶乘球", "formula": "n!",
             "skill": "【专属技能】数值爆炸\n砸碎砖块时，对屏幕内所有砖块造成 30% 的波及伤害。"},
            {"key": "catalan", "name": "卡特兰球", "formula": "C(n)",
             "skill": "【专属技能】剖分打击\n砸击时额外扣减目标砖块 50% 的血量。"},
            {"key": "bell", "name": "贝尔球", "formula": "B(n)",
             "skill": "【专属技能】子集分割\n砸碎砖块时，波及最多 3 个其他砖块各 15% 伤害。"},
            {"key": "stirling", "name": "斯特林球", "formula": "S(n)",
             "skill": "【专属技能】盒子收纳\n每砸碎 5 个砖块，触发一次全屏 50% 伤害的爆发。"},
            {"key": "super_fact", "name": "超阶乘球", "formula": "sf(n)",
             "skill": "【专属技能】超新星爆发\n砸碎砖块时，有 10% 概率直接清空屏幕所有砖块。"},
            {"key": "bell_sum", "name": "贝尔和球", "formula": "Sum B(n)",
             "skill": "【专属技能】裂变连锁\n砸击后，对上下 80 像素内的砖块引发连锁爆炸。"},
        ],
    },
]


def get_all_ball_keys():
    return [b["key"] for cat in CATEGORIES for b in cat.get("balls", [])]


def find_ball_name(key):
    for cat in CATEGORIES:
        for b in cat["balls"]:
            if b["key"] == key:
                return b["name"]
    return key


def find_category_index(ball_key):
    for i, cat in enumerate(CATEGORIES):
        for b in cat.get("balls", []):
            if b["key"] == ball_key:
                return i
    return 0


# ============================================================
# 设置
# ============================================================
def _settings_dir():
    # 安卓 APK 里脚本目录只读，设置必须落到应用私有目录
    private = os.environ.get("ANDROID_PRIVATE")
    if private and os.path.isdir(private):
        return private
    return os.path.dirname(os.path.abspath(__file__))


_SETTINGS_PATH = os.path.join(_settings_dir(), "settings.json")

DEFAULT_SETTINGS = {
    "sound_enabled": True,
    "music_enabled": True,
    "music_volume": 0.7,
    "sfx_volume": 0.8,
    "unlocked_balls": ["square", "cube", "triangular",
                       "exponential", "factorial"],
    "brick_exponents": list(DEFAULT_BRICK_EXPONENTS),
}


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        self.data = dict(DEFAULT_SETTINGS)
        try:
            if os.path.exists(_SETTINGS_PATH):
                with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if isinstance(saved, dict):
                    self.data.update(saved)
        except Exception:
            pass

    def save(self):
        try:
            with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_brick_exponents(self):
        raw = self.data.get("brick_exponents", None)
        default = list(DEFAULT_BRICK_EXPONENTS)
        if not isinstance(raw, (list, tuple)):
            return default
        pool = set(BRICK_EXPONENT_POOL)
        cleaned, seen = [], set()
        for e in raw:
            try:
                ei = int(e)
            except (TypeError, ValueError):
                continue
            if ei in pool and ei not in seen:
                seen.add(ei)
                cleaned.append(ei)
        if not cleaned:
            return default
        cleaned.sort()
        return cleaned

    def set_brick_exponents(self, exps):
        pool = set(BRICK_EXPONENT_POOL)
        cleaned, seen = [], set()
        for e in (exps or []):
            try:
                ei = int(e)
            except (TypeError, ValueError):
                continue
            if ei in pool and ei not in seen:
                seen.add(ei)
                cleaned.append(ei)
        if not cleaned:
            cleaned = list(DEFAULT_BRICK_EXPONENTS)
        cleaned.sort()
        self.set("brick_exponents", cleaned)


# ============================================================
# UI
# ============================================================
_FONT_CACHE = {}


def _find_chinese_font():
    plat = sys.platform
    if plat.startswith("win"):
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyh.ttf",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    elif plat == "darwin":
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    else:
        candidates = [
            "/system/fonts/NotoSansCJK-Regular.ttc",
            "/system/fonts/NotoSansSC-Regular.otf",
            "/system/fonts/DroidSansFallbackFull.ttf",
            "/system/fonts/HarmonyOS_Sans_SC_Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def get_font(size):
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    path = _find_chinese_font()
    font = None
    if path:
        try:
            font = pygame.font.Font(path, size)
        except Exception:
            font = None
    if font is None:
        font = pygame.font.SysFont(None, size)
    _FONT_CACHE[size] = font
    return font


@lru_cache(maxsize=2048)
def _cached_render(text, size, color):
    return get_font(size).render(text, True, color)


def render_text(text, size, color):
    return _cached_render(str(text), int(size), tuple(color))


def clear_text_cache():
    _cached_render.cache_clear()


def wrap_text_pixels(text, size, max_width):
    font = get_font(size)
    lines = []
    for raw in text.split("\n"):
        if not raw:
            lines.append("")
            continue
        cur = ""
        for ch in raw:
            if font.size(cur + ch)[0] > max_width and cur:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
    return lines


class Button:
    def __init__(self, rect, text, callback, color=(80, 200, 120),
                 text_color=(255, 255, 255), font_size=FONT_MID,
                 border_radius=30):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.border_radius = border_radius
        self.hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if getattr(event, "button", 1) in (1, 0, 2, 3):
                if self.rect.collidepoint(event.pos):
                    if self.callback:
                        self.callback()
                    return True
        return False

    def draw(self, surface):
        c = self.color
        if self.hover:
            c = (min(255, c[0] + 30),
                 min(255, c[1] + 30),
                 min(255, c[2] + 30))
        pygame.draw.rect(surface, c, self.rect, border_radius=self.border_radius)
        txt = render_text(self.text, self.font_size, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ============================================================
# 技能系统
# ============================================================
_SKILL_FACTORY = {}


def register_skill(key):
    def deco(cls):
        _SKILL_FACTORY[key] = cls
        return cls
    return deco


def create_skill(b_type):
    cls = _SKILL_FACTORY.get(b_type)
    if cls is None:
        return None
    try:
        return cls()
    except Exception:
        return None


def validate_skills(ball_keys):
    return [k for k in ball_keys if k not in _SKILL_FACTORY]


def list_registered_skills():
    return sorted(_SKILL_FACTORY.keys())


class Skill:
    name = "base"
    MAX_VX = 500.0
    MAX_VY = 800.0

    def on_hit(self, ball, brick, ctx): pass
    def on_bounce(self, ball, brick, ctx): pass
    def on_destroy(self, ball, brick, ctx): pass
    def on_update(self, ball, dt, ctx): pass
    def on_reset(self, ball): pass


@register_skill("square")
class SkillFourTwoThousand(Skill):
    name = "四两拨千斤"

    def on_hit(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "four_two", 0.5):
            return
        if random.random() >= 0.25:
            return
        if ball.value == float('inf') or ball.value <= 0:
            return
        eff = brick.effective_need_value
        if eff <= 0 or eff == float('inf'):
            return
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.10, "four_two")
        else:
            brick.hp -= int(brick.max_hp * min(1.0, ball.value / eff))
            brick.shake()


@register_skill("cube")
class SkillVolumeSuppress(Skill):
    name = "体积压制"

    def on_destroy(self, ball, brick, ctx):
        ctx.shake_screen(10, 0.25)
        ctx.particles.spawn_burst(brick.rect.centerx, brick.rect.centery,
                                  (255, 240, 120), 30)


@register_skill("fourth_power")
class SkillDimensionStrike(Skill):
    name = "降维打击"

    def on_hit(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "dim", 999.0):
            return
        brick.need_value_modifier = min(brick.need_value_modifier, 0.9)


@register_skill("fifth_power")
class SkillLayerByLayer(Skill):
    name = "层层递进"

    def __init__(self):
        self.streak = 0

    def on_reset(self, ball):
        self.streak = 0

    def on_destroy(self, ball, brick, ctx):
        self.streak += 1
        if self.streak >= 3:
            ball.damage_mult = min(2.0, ball.damage_mult * 1.2)
            self.streak = 0


@register_skill("triangular")
class SkillSandPile(Skill):
    name = "聚沙成塔"

    def __init__(self):
        self.sand = 0

    def on_reset(self, ball):
        self.sand = 0

    def on_bounce(self, ball, brick, ctx):
        self.sand = min(10, self.sand + 1)

    def on_destroy(self, ball, brick, ctx):
        if self.sand > 0:
            ball.damage_mult = min(3.0, ball.damage_mult + 0.15 * self.sand)
            self.sand = 0


@register_skill("prime")
class SkillNotDivisible(Skill):
    name = "不可整除"

    def on_hit(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "prime", 0.5):
            return
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.30, "prime")
            return
        eff = brick.effective_need_value
        if eff == float('inf') or eff <= 0:
            return
        if (ball.value != float('inf')
                and math.gcd(int(ball.value), int(eff)) == 1):
            brick.hp = 0
            brick.shake()


@register_skill("euler_phi")
class SkillCoprimePierce(Skill):
    name = "互素穿透"

    def on_hit(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "coprime", 0.5):
            return
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.20, "coprime")
            return
        if random.random() < 0.2:
            brick.need_value_modifier = max(0.3, brick.need_value_modifier * 0.8)


@register_skill("mobius")
class SkillReverseFate(Skill):
    name = "反转乾坤"

    def on_bounce(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "reverse", 0.5):
            return
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.10, "reverse")
            return
        brick.need_value_modifier = max(0.3, brick.need_value_modifier * 0.9)


@register_skill("partition")
class SkillSplitStrike(Skill):
    name = "分裂重击"

    def on_destroy(self, ball, brick, ctx):
        ctx.spawn_minion(ball.x, ball.y, ball.b_type, ball.n)


@register_skill("euler_num")
class SkillZigzagShock(Skill):
    name = "锯齿震荡"
    RANGE_PX = (BRICK_H + BRICK_GAP_Y) * 3

    def on_destroy(self, ball, brick, ctx):
        if ctx.is_battle:
            ctx.boost_all_opponent_bricks(0.50, "zigzag")
            return
        for b in list(ctx.bricks):
            if not b.alive or b is brick:
                continue
            if abs(b.rect.centery - brick.rect.centery) <= self.RANGE_PX:
                if not ctx.can_trigger(b, "zigzag", 0.5):
                    continue
                b.hp -= int(b.max_hp * 0.5)
                b.shake()
                if b.hp <= 0:
                    b.hp = 0
                    ctx.destroy_brick(b)


@register_skill("exponential")
class SkillExpBlast(Skill):
    name = "指数爆炸"

    def on_destroy(self, ball, brick, ctx):
        ball.speed_mult = min(3.0, ball.speed_mult * 1.3)


@register_skill("fibonacci")
class SkillGoldenSpiral(Skill):
    name = "黄金螺旋"

    def on_update(self, ball, dt, ctx):
        if ball.y <= 0:
            return
        ball.spiral_phase += dt * 4
        target = math.sin(ball.spiral_phase) * 200.0
        ball.vx += (target - ball.vx) * min(1.0, dt * 6)
        if abs(ball.vx) > self.MAX_VX:
            ball.vx = self.MAX_VX if ball.vx > 0 else -self.MAX_VX


@register_skill("lucas")
class SkillTwinResonance(Skill):
    name = "双生共鸣"

    def on_hit(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "twin", 0.5):
            return
        if ctx.is_battle:
            ctx.boost_all_opponent_bricks(0.15, "twin")
            return
        if brick.alive:
            extra = int(brick.max_hp * 0.15)
            brick.hp -= extra
            brick.shake()
            if brick.hp <= 0:
                brick.hp = 0


@register_skill("padovan")
class SkillIronBone(Skill):
    name = "钢筋铁骨"

    def on_bounce(self, ball, brick, ctx):
        if ball.vy > BOUNCE_VY:
            ball.vy = BOUNCE_VY


@register_skill("double_fact")
class SkillDoubleStrike(Skill):
    name = "双重打击"

    def on_destroy(self, ball, brick, ctx):
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.30, "double")
            return
        for b in list(ctx.bricks):
            if b.alive and b.rect.centery < brick.rect.centery:
                if not ctx.can_trigger(b, "double", 0.5):
                    continue
                b.hp -= int(b.max_hp * 0.3)
                b.shake()
                if b.hp <= 0:
                    b.hp = 0
                    ctx.destroy_brick(b)
                break


@register_skill("triple_fact")
class SkillTrio(Skill):
    name = "三重奏"

    def on_destroy(self, ball, brick, ctx):
        for _ in range(3):
            ctx.particles.spawn_burst(brick.rect.centerx, brick.rect.centery,
                                      (255, 200, 100), 10)


@register_skill("power_tower")
class SkillPowerStack(Skill):
    name = "幂次叠加"

    def on_destroy(self, ball, brick, ctx):
        ball.damage_mult = min(5.0, ball.damage_mult * 1.1)


@register_skill("motzkin")
class SkillStringDance(Skill):
    name = "弦之舞"

    def on_bounce(self, ball, brick, ctx):
        impulse = 300.0 if ball.x < ctx.W // 2 else -300.0
        ball.vx += impulse
        if abs(ball.vx) > self.MAX_VX:
            ball.vx = self.MAX_VX if ball.vx > 0 else -self.MAX_VX


@register_skill("derangement")
class SkillMissAlign(Skill):
    name = "错位闪避"

    def on_bounce(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "miss", 0.5):
            return
        if random.random() < 0.2:
            ball.vy = -ball.vy * 0.5


@register_skill("square_sum")
class SkillPyramidShield(Skill):
    name = "金字塔之力"

    def on_destroy(self, ball, brick, ctx):
        ball.shield = min(3, ball.shield + 1)


@register_skill("geo_sum")
class SkillCompoundGrowth(Skill):
    name = "复利增长"

    def on_destroy(self, ball, brick, ctx):
        ball.damage_mult = min(3.0, ball.damage_mult + 0.05)


@register_skill("fact_sum")
class SkillFullPermutation(Skill):
    name = "全排列打击"

    def on_destroy(self, ball, brick, ctx):
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.20, "full")
            return
        alive = [b for b in ctx.bricks if b.alive]
        if alive:
            t = random.choice(alive)
            if not ctx.can_trigger(t, "full", 0.5):
                return
            t.hp -= int(t.max_hp * 0.2)
            t.shake()
            if t.hp <= 0:
                t.hp = 0
                ctx.destroy_brick(t)


@register_skill("dfact_sum")
class SkillEnergyAccumulate(Skill):
    name = "能量累积"

    def on_bounce(self, ball, brick, ctx):
        ball.energy += 1
        if ball.energy >= 5:
            ball.damage_mult = min(4.0, ball.damage_mult * 2)
            ball.energy = 0


@register_skill("catalan_sum")
class SkillBracketShield(Skill):
    name = "括号护盾"

    def __init__(self):
        self._granted = False

    def on_reset(self, ball):
        self._granted = False

    def on_update(self, ball, dt, ctx):
        if not self._granted:
            ball.shield = max(ball.shield, 1)
            self._granted = True


@register_skill("factorial")
class SkillNumericExplosion(Skill):
    name = "数值爆炸"

    def on_destroy(self, ball, brick, ctx):
        if ctx.is_battle:
            ctx.boost_all_opponent_bricks(0.30, "num_exp")
            return
        for b in list(ctx.bricks):
            if b.alive and b is not brick:
                if not ctx.can_trigger(b, "num_exp", 0.5):
                    continue
                b.hp -= int(b.max_hp * 0.3)
                b.shake()
                if b.hp <= 0:
                    b.hp = 0
                    ctx.destroy_brick(b)


@register_skill("catalan")
class SkillBrickDissect(Skill):
    name = "剖分打击"

    def on_hit(self, ball, brick, ctx):
        if not ctx.can_trigger(brick, "dissect", 0.5):
            return
        if ctx.is_battle:
            target = ctx.pick_random_opponent_brick()
            if target is not None:
                ctx.boost_brick(target, 0.50, "dissect")
            return
        if brick.alive:
            brick.hp -= int(brick.max_hp * 0.5)
            brick.shake()
            if brick.hp <= 0:
                brick.hp = 0


@register_skill("bell")
class SkillSubsetDivide(Skill):
    name = "子集分割"

    def on_destroy(self, ball, brick, ctx):
        if ctx.is_battle:
            for b in ctx.pick_random_opponent_bricks(3):
                ctx.boost_brick(b, 0.15, "subset")
            return
        cnt = 0
        for b in list(ctx.bricks):
            if b.alive and b is not brick and cnt < 3:
                if not ctx.can_trigger(b, "subset", 0.5):
                    continue
                b.hp -= int(b.max_hp * 0.15)
                b.shake()
                if b.hp <= 0:
                    b.hp = 0
                    ctx.destroy_brick(b)
                cnt += 1


@register_skill("stirling")
class SkillBoxStorage(Skill):
    name = "盒子收纳"

    def on_destroy(self, ball, brick, ctx):
        ball.energy += 1
        if ball.energy >= 5:
            if ctx.is_battle:
                ctx.boost_all_opponent_bricks(0.50, "box")
            else:
                for b in list(ctx.bricks):
                    if b.alive and ctx.can_trigger(b, "box", 0.5):
                        b.hp -= int(b.max_hp * 0.5)
                        b.shake()
                        if b.hp <= 0:
                            b.hp = 0
                            ctx.destroy_brick(b)
            ball.energy = 0
            ctx.shake_screen(15, 0.4)


@register_skill("super_fact")
class SkillSupernova(Skill):
    name = "超新星爆发"

    def on_destroy(self, ball, brick, ctx):
        if random.random() < 0.1:
            if ctx.is_battle:
                ctx.boost_all_opponent_bricks(0.50, "supernova")
            else:
                for b in list(ctx.bricks):
                    if b.alive:
                        b.hp = 0
                        ctx.destroy_brick(b)
            ctx.shake_screen(20, 0.6)


@register_skill("bell_sum")
class SkillChainReaction(Skill):
    name = "裂变连锁"

    def on_destroy(self, ball, brick, ctx):
        if ctx.is_battle:
            ctx.boost_all_opponent_bricks(0.20, "chain")
            return
        for b in list(ctx.bricks):
            if b.alive and abs(b.rect.centery - brick.rect.centery) <= 80:
                if not ctx.can_trigger(b, "chain", 0.5):
                    continue
                b.hp -= int(b.max_hp * 0.2)
                b.shake()
                if b.hp <= 0:
                    b.hp = 0
                    ctx.destroy_brick(b)


# ============================================================
# 实体
# ============================================================
class Ball:
    __slots__ = ("x", "y", "r", "vx", "vy", "n", "b_type", "value", "text",
                 "color", "skill", "speed_mult", "damage_mult", "shield",
                 "energy", "scale", "scale_target", "spiral_phase")

    def __init__(self, x, y, b_type, skill=None):
        self.x = float(x)
        self.y = float(y)
        self.r = BALL_RADIUS
        self.vx = 0.0
        self.vy = 0.0
        self.n = 2
        self.b_type = b_type
        self.value = get_value(self.n, b_type)
        self.text = get_text(self.n, b_type)
        self.color = (80, 200, 255)
        self.skill = skill
        self.speed_mult = 1.0
        self.damage_mult = 1.0
        self.shield = 0
        self.energy = 0
        self.scale = 1.0
        self.scale_target = 1.0
        self.spiral_phase = 0.0

    def upgrade(self):
        self.n += 1
        self.value = get_value(self.n, self.b_type)
        self.text = get_text(self.n, self.b_type)

    def reset(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        if self.skill:
            self.skill.on_reset(self)

    def update_animation(self, dt):
        if abs(self.scale - self.scale_target) > 0.001:
            self.scale += (self.scale_target - self.scale) * min(1.0, 12 * dt)
        else:
            self.scale = self.scale_target
        if self.scale_target > 1.0:
            self.scale_target = max(1.0, self.scale_target - dt * 1.5)


class Brick:
    __slots__ = ("rect", "exp", "need_n", "need_value", "alive",
                 "hp", "max_hp", "color", "shake_timer",
                 "need_value_modifier", "_destroyed", "_skip_skill")

    def __init__(self, rect, exp, need_n, need_value, color):
        self.rect = rect
        self.exp = exp
        self.need_n = need_n
        self.need_value = need_value
        self.alive = True
        self.hp = BRICK_HP_MAX
        self.max_hp = BRICK_HP_MAX
        self.color = color
        self.shake_timer = 0.0
        self.need_value_modifier = 1.0
        self._destroyed = False
        self._skip_skill = False

    @property
    def hp_ratio(self):
        return 0.0 if self.max_hp <= 0 else max(0.0, self.hp / self.max_hp)

    @property
    def effective_need_value(self):
        return self.need_value * self.need_value_modifier

    def shake(self, intensity=0.15):
        self.shake_timer = max(self.shake_timer, intensity)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "active")

    def __init__(self):
        self.x = self.y = self.vx = self.vy = 0.0
        self.life = 0.0
        self.max_life = 1.0
        self.color = (255, 255, 255)
        self.active = False


class ParticlePool:
    def __init__(self, size=600):
        self.particles = [Particle() for _ in range(size)]

    def spawn_burst(self, x, y, color, count=20):
        spawned = 0
        for p in self.particles:
            if p.active:
                continue
            a = random.uniform(0, math.tau)
            sp = random.uniform(50, 300)
            p.x, p.y = float(x), float(y)
            p.vx, p.vy = math.cos(a) * sp, math.sin(a) * sp
            p.life = p.max_life = random.uniform(0.3, 0.8)
            p.color = color
            p.active = True
            spawned += 1
            if spawned >= count:
                break

    def update(self, dt):
        for p in self.particles:
            if not p.active:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 400 * dt
            p.life -= dt
            if p.life <= 0:
                p.active = False

    def draw(self, surface):
        for p in self.particles:
            if not p.active:
                continue
            r = max(1, int(8 * (p.life / max(0.01, p.max_life))))
            pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), r)


# ============================================================
# 游戏逻辑
# ============================================================
def circle_rect_collide(cx, cy, r, rect):
    nx = max(rect.left, min(cx, rect.right))
    ny = max(rect.top, min(cy, rect.bottom))
    dx, dy = cx - nx, cy - ny
    return dx * dx + dy * dy <= r * r


class GameContext:
    def __init__(self, session):
        self._s = session
        self.opponent_session = None

    @property
    def is_battle(self):
        return self.opponent_session is not None

    @property
    def bricks(self):
        if self.is_battle:
            return self.opponent_session.bricks
        return self._s.bricks

    @property
    def particles(self):
        return self._s.particles

    @property
    def W(self):
        return W

    @property
    def H(self):
        return H

    def shake_screen(self, i, d):
        self._s.shake_screen(i, d)

    def spawn_minion(self, x, y, bt, n):
        self._s.spawn_minion(x, y, bt, n)

    def can_trigger(self, brick, key, cd=0.5):
        return self._s.can_trigger_skill(brick, key, cd)

    def destroy_brick(self, brick):
        if self.is_battle:
            return
        self._s._destroy_brick(brick, trigger_skill=True)

    def pick_random_opponent_brick(self):
        if not self.is_battle:
            return None
        alive = [b for b in self.opponent_session.bricks if b.alive]
        return random.choice(alive) if alive else None

    def pick_random_opponent_bricks(self, count):
        if not self.is_battle:
            return []
        alive = [b for b in self.opponent_session.bricks if b.alive]
        random.shuffle(alive)
        return alive[:count]

    def boost_brick(self, brick, ratio, key, cd=0.5):
        if not brick.alive:
            return
        if not self._s.can_trigger_skill(brick, key, cd):
            return
        cap = int(brick.max_hp * BATTLE_HP_CAP_RATIO)
        brick.hp = min(cap, brick.hp + int(brick.max_hp * ratio))
        brick.shake()

    def boost_all_opponent_bricks(self, ratio, key, cd=0.5):
        if not self.is_battle:
            return
        for b in list(self.opponent_session.bricks):
            self.boost_brick(b, ratio, key, cd)


class GameSession:
    def __init__(self, ball_types, is_battle=False, side="A",
                 brick_exponents=None):
        if isinstance(ball_types, str):
            ball_types = [ball_types]
        self.ball_types = list(ball_types)
        self.is_battle = is_battle
        self.side = side

        if brick_exponents is None:
            self.brick_exponents = tuple(Settings().get_brick_exponents())
        else:
            pool = set(BRICK_EXPONENT_POOL)
            cleaned, seen = [], set()
            for e in brick_exponents:
                try:
                    ei = int(e)
                except (TypeError, ValueError):
                    continue
                if ei in pool and ei not in seen:
                    seen.add(ei)
                    cleaned.append(ei)
            if not cleaned:
                cleaned = list(DEFAULT_BRICK_EXPONENTS)
            cleaned.sort()
            self.brick_exponents = tuple(cleaned)

        start_positions = self._compute_start_positions(len(self.ball_types))

        self.balls = []
        for i, b_type in enumerate(self.ball_types):
            x, y = start_positions[i]
            skill = create_skill(b_type)
            b = Ball(x, y, b_type, skill=skill)
            if b.skill:
                b.skill.on_reset(b)
            self.balls.append(b)

        self.particles = ParticlePool(600)
        self.bricks = self._build_bricks()
        self.elapsed = 0.0
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.minions = []
        self._skill_timers = {}
        self.ctx = GameContext(self)
        self.no_targets = (len(self.bricks) == 0)
        self._in_on_destroy = False

        self._sfx_destroy = None
        self._sfx_bounce = None
        self._load_sounds()

    def _lane_bounds(self, r):
        if self.is_battle:
            if self.side == "A":
                return (BATTLE_TRACK_A_LEFT + r, BATTLE_TRACK_A_RIGHT - r)
            else:
                return (BATTLE_TRACK_B_LEFT + r, BATTLE_TRACK_B_RIGHT - r)
        return (r, W - r)

    def _track_center_x(self):
        if self.is_battle:
            if self.side == "A":
                return (BATTLE_TRACK_A_LEFT + BATTLE_TRACK_A_RIGHT) // 2
            else:
                return (BATTLE_TRACK_B_LEFT + BATTLE_TRACK_B_RIGHT) // 2
        return W // 2

    def _compute_start_positions(self, count):
        cx = self._track_center_x()
        if self.is_battle:
            base_y = BATTLE_TRACK_TOP - 60
        else:
            base_y = -50
        if count <= 1:
            return [(cx, base_y)]
        min_x, max_x = self._lane_bounds(BALL_RADIUS)
        span = min((max_x - min_x) // 2 - 10, 50 + 25 * count)
        positions = []
        for i in range(count):
            if count == 1:
                ox = 0
            else:
                ox = -span + (2 * span) * i / (count - 1)
            oy = base_y - i * 80
            positions.append((cx + ox, oy))
        return positions

    def _load_sounds(self):
        if not pygame.mixer.get_init():
            return
        base = os.path.dirname(os.path.abspath(__file__))
        self._sfx_destroy = self._try_load(os.path.join(base, "sfx_destroy.wav"))
        self._sfx_bounce = self._try_load(os.path.join(base, "sfx_bounce.wav"))

    def _try_load(self, path):
        if not os.path.exists(path) or not pygame.mixer.get_init():
            return None
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    def _play(self, snd):
        if snd is None or not pygame.mixer.get_init():
            return
        s = Settings()
        if not s.get("sound_enabled", True):
            return
        try:
            snd.set_volume(s.get("sfx_volume", 0.8))
            snd.play()
        except Exception:
            pass

    def _build_bricks(self):
        # 从已选球类型中，选"能覆盖砖块档位最多"的那一个做主序列
        if self.ball_types:
            best_needs = None
            best_valid = -1
            for bt in self.ball_types:
                needs = precompute_brick_needs(bt, self.brick_exponents)
                valid = sum(1 for _, _, v in needs if v != float('inf'))
                if valid > best_valid:
                    best_valid = valid
                    best_needs = needs
            needs = best_needs
        else:
            needs = precompute_brick_needs("square", self.brick_exponents)

        bricks = []

        if self.is_battle:
            if self.side == "A":
                track_left = BATTLE_TRACK_A_LEFT
                track_right = BATTLE_TRACK_A_RIGHT
            else:
                track_left = BATTLE_TRACK_B_LEFT
                track_right = BATTLE_TRACK_B_RIGHT
            track_w = track_right - track_left
            bx = track_left + (track_w - BATTLE_BRICK_W) // 2
            slot = 0
            for exp, need_n, need_value in needs:
                if need_value == float('inf'):
                    continue
                y = (BATTLE_TRACK_TOP + 20
                     + slot * (BATTLE_BRICK_H + BATTLE_BRICK_GAP_Y))
                if y + BATTLE_BRICK_H > BATTLE_TRACK_BOTTOM - 10:
                    break
                rect = pygame.Rect(bx, y, BATTLE_BRICK_W, BATTLE_BRICK_H)
                color = (random.randint(100, 200),
                         random.randint(80, 180),
                         random.randint(150, 255))
                bricks.append(Brick(rect, exp, need_n, need_value, color))
                slot += 1
            return bricks

        sx = (W - BRICK_W) // 2
        slot = 0
        for exp, need_n, need_value in needs:
            if need_value == float('inf'):
                continue
            rect = pygame.Rect(sx,
                               BRICK_START_Y + slot * (BRICK_H + BRICK_GAP_Y),
                               BRICK_W, BRICK_H)
            color = (random.randint(100, 200),
                     random.randint(80, 180),
                     random.randint(150, 255))
            bricks.append(Brick(rect, exp, need_n, need_value, color))
            slot += 1
        return bricks

    def can_trigger_skill(self, brick, key, cd):
        k = (id(brick), key)
        if self._skill_timers.get(k, 0) > 0:
            return False
        self._skill_timers[k] = cd
        return True

    def _tick_skill_timers(self, dt):
        if not self._skill_timers:
            return
        for k in list(self._skill_timers.keys()):
            self._skill_timers[k] -= dt
            if self._skill_timers[k] <= 0:
                del self._skill_timers[k]

    def _cleanup_skill_timers(self):
        if len(self._skill_timers) <= SKILL_TIMER_CLEANUP_THRESHOLD:
            return
        alive_ids = {id(b) for b in self.bricks if b.alive}
        for k in list(self._skill_timers.keys()):
            if k[0] not in alive_ids:
                del self._skill_timers[k]

    def shake_screen(self, i=10, d=0.25):
        self.shake_intensity = max(self.shake_intensity, i)
        self.shake_timer = max(self.shake_timer, d)

    def spawn_minion(self, x, y, b_type, n):
        if len(self.minions) >= 3:
            return
        m = Ball(x, y, b_type, skill=None)
        m.n = n
        m.value = get_value(n, b_type)
        m.text = get_text(n, b_type)
        m.r = 22
        m.color = (200, 200, 100)
        for b in self.bricks:
            if b.alive and circle_rect_collide(m.x, m.y, m.r, b.rect):
                if m.y < b.rect.centery:
                    m.y = b.rect.top - m.r - 2
                else:
                    m.y = b.rect.bottom + m.r + 2
                break
        m.vy = MINION_INITIAL_VY
        self.minions.append(m)

    def update(self, dt):
        self.elapsed += dt

        for ball in self.balls:
            self._update_single_ball(ball, dt)

        for m in list(self.minions):
            self._update_minion(m, dt)

        for b in self.bricks:
            if b.shake_timer > 0:
                b.shake_timer = max(0.0, b.shake_timer - dt)

        self.particles.update(dt)
        self._tick_skill_timers(dt)

        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

        self._flush_dead()

    def _update_single_ball(self, ball, dt):
        ball.vx *= VX_DAMPING
        max_v = MAX_BALL_SPEED * ball.speed_mult
        ball.vy = min(ball.vy + GRAVITY * dt, max_v)

        if ball.skill:
            ball.skill.on_update(ball, dt, self.ctx)

        min_x, max_x = self._lane_bounds(ball.r)

        total_dx = ball.vx * dt
        total_dy = ball.vy * dt
        steps = max(1, min(int(max(abs(total_dx), abs(total_dy)) / 15),
                           MAX_COLLISION_SUBSTEPS))
        sdx, sdy = total_dx / steps, total_dy / steps
        for _ in range(steps):
            ball.x += sdx
            ball.y += sdy
            if ball.x < min_x:
                ball.x = min_x
                ball.vx = -ball.vx * 0.8
                sdx = -sdx * 0.8
            elif ball.x > max_x:
                ball.x = max_x
                ball.vx = -ball.vx * 0.8
                sdx = -sdx * 0.8
            if self._check_collision_for(ball):
                break

        if self.is_battle:
            out_y = BATTLE_TRACK_BOTTOM + 100
            reset_y = BATTLE_TRACK_TOP - 60
        else:
            out_y = H + 100
            reset_y = -50
        if ball.y > out_y:
            cx = self._track_center_x()
            ball.reset(cx, reset_y)
            ball.upgrade()

        ball.update_animation(dt)

    def _flush_dead(self):
        for b in self.bricks:
            if b.alive and b.hp <= 0:
                b.hp = 0
                self._destroy_brick(b)

    def _update_minion(self, m, dt):
        m.vx *= MINION_DAMPING
        m.vy = min(m.vy + GRAVITY * dt, MINION_MAX_SPEED)

        min_x, max_x = self._lane_bounds(m.r)

        total_dx = m.vx * dt
        total_dy = m.vy * dt
        steps = max(1, int(max(abs(total_dx), abs(total_dy)) / 10))
        sdx, sdy = total_dx / steps, total_dy / steps
        for _ in range(steps):
            m.x += sdx
            m.y += sdy
            if m.x < min_x:
                m.x = min_x
                m.vx = -m.vx * MINION_BOUNCE_DAMPING
                sdx = -sdx * MINION_BOUNCE_DAMPING
            elif m.x > max_x:
                m.x = max_x
                m.vx = -m.vx * MINION_BOUNCE_DAMPING
                sdx = -sdx * MINION_BOUNCE_DAMPING
            if self._minion_collide(m):
                break
        m.update_animation(dt)
        if m.y > H + 100 and m in self.minions:
            self.minions.remove(m)

    def _minion_collide(self, m):
        for b in self.bricks:
            if not b.alive:
                continue
            if circle_rect_collide(m.x, m.y, m.r, b.rect):
                b.hp -= int(b.max_hp * MINION_DAMAGE_RATIO)
                b.shake()
                if b.hp <= 0:
                    b.hp = 0
                    self._destroy_brick(b, trigger_skill=False)
                cy_b = b.rect.centery
                if abs(m.vx) > abs(m.vy) * MINION_SIDE_RATIO:
                    m.vx = -m.vx * MINION_BOUNCE_DAMPING
                    if m.x < b.rect.centerx:
                        m.x = b.rect.left - m.r - 1
                    else:
                        m.x = b.rect.right + m.r + 1
                else:
                    if m.y < cy_b:
                        m.vy = -abs(m.vy)
                        m.y = b.rect.top - m.r - 1
                    else:
                        m.vy = abs(m.vy)
                        m.y = b.rect.bottom + m.r + 1
                return True
        return False

    def is_finished(self, duration):
        if self.no_targets:
            return True
        if all(not b.alive for b in self.bricks):
            return True
        return self.elapsed > duration

    def alive_brick_count(self):
        return sum(1 for b in self.bricks if b.alive)

    def total_hp(self):
        return sum(max(0, b.hp) for b in self.bricks if b.alive)

    def _check_collision_for(self, ball):
        for b in self.bricks:
            if not b.alive:
                continue
            if circle_rect_collide(ball.x, ball.y, ball.r, b.rect):
                self._handle_hit(ball, b)
                return True
        return False

    def _on_killed(self, ball, brick, upgrade=True):
        if upgrade:
            ball.upgrade()
        ball.scale_target = 1.3
        ball.vy = KILL_BOUNCE_VY
        ball.y = brick.rect.top - ball.r - 1

    def _handle_hit(self, ball, brick):
        cy = ball.y
        ctr_y = brick.rect.centery

        from_bottom = cy > ctr_y
        side = (abs(ball.vx) > abs(ball.vy) * MINION_SIDE_RATIO
                and abs(cy - ctr_y) < brick.rect.h * 0.5)

        if side:
            ball.vx = -ball.vx * SIDE_BOUNCE_DAMPING
            if ball.x < brick.rect.centerx:
                ball.x = brick.rect.left - ball.r - 1
            else:
                ball.x = brick.rect.right + ball.r + 1
            brick.hp -= MIN_DAMAGE
            brick.shake()
            if brick.hp <= 0:
                brick.hp = 0
                self._destroy_brick(brick)
            elif ball.skill:
                ball.skill.on_bounce(ball, brick, self.ctx)
            return

        if from_bottom:
            ball.vy = abs(ball.vy) * BOTTOM_BOUNCE_DAMPING
            ball.y = brick.rect.bottom + ball.r + 1
            brick.hp -= MIN_DAMAGE
            brick.shake()
            if brick.hp <= 0:
                brick.hp = 0
                self._destroy_brick(brick)
            elif ball.skill:
                ball.skill.on_bounce(ball, brick, self.ctx)
            return

        if ball.skill:
            ball.skill.on_hit(ball, brick, self.ctx)

        if brick._destroyed:
            self._on_killed(ball, brick, upgrade=True)
            return

        if not brick.alive or brick.hp <= 0:
            brick.hp = 0
            self._destroy_brick(brick)
            self._on_killed(ball, brick, upgrade=True)
            return

        eff = brick.effective_need_value
        val = (float('inf') if ball.value == float('inf')
               else ball.value * ball.damage_mult)
        if eff == float('inf'):
            kill = False
        elif val == float('inf'):
            kill = True
        else:
            kill = val >= eff

        if kill:
            self._destroy_brick(brick)
            ball.color = (random.randint(150, 255),
                          random.randint(150, 255),
                          random.randint(100, 255))
            self._on_killed(ball, brick, upgrade=True)
            return

        if eff == float('inf') or eff <= 0:
            dmg = MIN_DAMAGE
        elif ball.value == float('inf'):
            dmg = brick.max_hp
        else:
            try:
                ratio = val / eff
            except (OverflowError, ZeroDivisionError):
                ratio = 1.0
            dmg = max(MIN_DAMAGE, int(brick.max_hp * min(1.0, ratio)))
        brick.hp -= dmg
        brick.shake()

        if brick.hp <= 0:
            brick.hp = 0
            self._destroy_brick(brick)
            self._on_killed(ball, brick, upgrade=True)
            return

        if ball.shield > 0:
            ball.shield -= 1
            brick.hp -= int(brick.max_hp * SHIELD_PIERCE_RATIO)
            if brick.hp <= 0:
                brick.hp = 0
                self._destroy_brick(brick)
            ball.vy = SHIELD_BOUNCE_VY
            ball.scale_target = 1.1
        else:
            ball.vy = BOUNCE_VY
            ball.scale_target = 1.15
            self._play(self._sfx_bounce)
            if ball.skill:
                ball.skill.on_bounce(ball, brick, self.ctx)

        ball.upgrade()
        ball.y = brick.rect.top - ball.r - 1

    def _destroy_brick(self, brick, trigger_skill=True):
        if brick._destroyed:
            return
        brick._destroyed = True
        brick.alive = False
        brick.hp = 0
        self.particles.spawn_burst(brick.rect.centerx, brick.rect.centery,
                                   brick.color, 20)
        self._play(self._sfx_destroy)
        self._cleanup_skill_timers()

        if trigger_skill:
            self._trigger_on_destroy(brick)
        else:
            brick._skip_skill = True

    def _trigger_on_destroy(self, brick):
        if brick._skip_skill:
            return
        if not self.balls:
            return
        if self._in_on_destroy:
            return
        self._in_on_destroy = True
        try:
            if self.balls[0].skill:
                self.balls[0].skill.on_destroy(
                    self.balls[0], brick, self.ctx)
        finally:
            self._in_on_destroy = False


# ============================================================
# 渲染
# ============================================================
class GameRenderer:
    TEXT_INTERVAL = 0.1

    def __init__(self):
        self._acc = 0.0
        self._time_surf = None
        self._ball_surf_cache = {}

    def update_dynamic_text(self, session, dt):
        self._acc += dt
        if self._acc < self.TEXT_INTERVAL:
            return
        self._acc = 0.0
        remain = max(0.0, GAME_DURATION - session.elapsed)
        self._time_surf = render_text(f"剩余 {remain:.0f}s",
                                      FONT_SMALL, COLOR_TEXT_DIM)

    def _get_ball_surf(self, text, font_size):
        key = (text, font_size)
        surf = self._ball_surf_cache.get(key)
        if surf is None:
            surf = render_text(text, font_size, COLOR_WHITE)
            self._ball_surf_cache[key] = surf
        return surf

    def _draw_bricks_particles_balls(self, surface, session, offset=(0, 0),
                                     battle_mode=False):
        ox, oy = offset
        for brick in session.bricks:
            if not brick.alive:
                continue
            sx = random.randint(-4, 4) if brick.shake_timer > 0 else 0
            rect = brick.rect.move(sx + ox, oy)
            pygame.draw.rect(surface, brick.color, rect, border_radius=15)

            bar = pygame.Rect(rect.x + 20, rect.y + 12, rect.w - 40, 14)
            pygame.draw.rect(surface, (40, 40, 60), bar, border_radius=7)
            ratio = brick.hp_ratio
            bc = ((80, 220, 120) if ratio > 0.6 else
                  (255, 200, 60) if ratio > 0.3 else (255, 80, 80))
            fw = int(bar.w * ratio)
            if fw > 0:
                pygame.draw.rect(surface, bc,
                                 pygame.Rect(bar.x, bar.y, fw, bar.h),
                                 border_radius=7)

            if battle_mode:
                text = f"10^{brick.exp}"
                txt = render_text(text, FONT_SMALL, COLOR_WHITE)
            else:
                text = f"10^{brick.exp}  ({format_value(brick.need_value)})"
                txt = render_text(text, FONT_MID, COLOR_WHITE)
            surface.blit(txt, txt.get_rect(
                center=(rect.centerx, rect.centery + 15)))

        session.particles.draw(surface)

        for m in session.minions:
            pygame.draw.circle(surface, m.color,
                               (int(m.x) + ox, int(m.y) + oy), m.r)

        ball_font = FONT_SMALL if (battle_mode or len(session.balls) > 1) \
            else FONT_BIG
        for ball in session.balls:
            r_scaled = int(ball.r * ball.scale)
            pygame.draw.circle(surface, ball.color,
                               (int(ball.x) + ox, int(ball.y) + oy),
                               r_scaled)
            surf = self._get_ball_surf(ball.text, ball_font)
            surface.blit(surf, surf.get_rect(
                center=(int(ball.x) + ox, int(ball.y) + oy)))

    def draw(self, surface, session, offset=(0, 0)):
        self._draw_bricks_particles_balls(surface, session, offset)
        if self._time_surf is not None:
            surface.blit(self._time_surf,
                         (W - self._time_surf.get_width() - 20, 20))

    def _draw_track_background(self, surface, session, side):
        if side == "A":
            rect = pygame.Rect(
                BATTLE_TRACK_A_LEFT,
                BATTLE_TRACK_TOP,
                BATTLE_TRACK_A_RIGHT - BATTLE_TRACK_A_LEFT,
                BATTLE_TRACK_BOTTOM - BATTLE_TRACK_TOP,
            )
            border_color = COLOR_PLAYER_A
        else:
            rect = pygame.Rect(
                BATTLE_TRACK_B_LEFT,
                BATTLE_TRACK_TOP,
                BATTLE_TRACK_B_RIGHT - BATTLE_TRACK_B_LEFT,
                BATTLE_TRACK_BOTTOM - BATTLE_TRACK_TOP,
            )
            border_color = COLOR_PLAYER_B

        bg_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        bg_surf.fill((*BATTLE_TRACK_BG_COLOR, 255))
        surface.blit(bg_surf, rect.topleft)

        border_dim = (border_color[0] // 3,
                      border_color[1] // 3,
                      border_color[2] // 3)
        pygame.draw.rect(surface, border_dim, rect, width=3, border_radius=10)

        label = f"玩家{side} 赛道"
        label_surf = render_text(label, FONT_TINY, border_color)
        surface.blit(label_surf,
                     (rect.x + 10, rect.y - label_surf.get_height() - 4))

    def draw_battle(self, surface, session_a, session_b, offset=(0, 0)):
        self._draw_track_background(surface, session_a, "A")
        self._draw_track_background(surface, session_b, "B")

        self._draw_bricks_particles_balls(surface, session_a, offset,
                                          battle_mode=True)
        self._draw_bricks_particles_balls(surface, session_b, offset,
                                          battle_mode=True)

        sep_rect = pygame.Rect(SPLIT_X - SPLIT_W // 2,
                               BATTLE_TRACK_TOP, SPLIT_W,
                               BATTLE_TRACK_BOTTOM - BATTLE_TRACK_TOP)
        pygame.draw.rect(surface, BATTLE_SEPARATOR_COLOR, sep_rect)

        dash_len, gap_len = 12, 8
        for y_start in (BATTLE_TRACK_TOP + 4, BATTLE_TRACK_BOTTOM - 4):
            x = SPLIT_X - SPLIT_W // 2 + 4
            end_x = SPLIT_X + SPLIT_W // 2 - 4
            while x < end_x:
                x2 = min(x + dash_len, end_x)
                pygame.draw.line(surface, (140, 130, 180),
                                 (x, y_start), (x2, y_start), 2)
                x = x2 + gap_len

        self._draw_flag(surface, SPLIT_X,
                        (BATTLE_TRACK_TOP + BATTLE_TRACK_BOTTOM) // 2)

        cnt_a = session_a.alive_brick_count()
        cnt_b = session_b.alive_brick_count()
        ta = render_text(f"玩家A 剩 {cnt_a} 块", FONT_SMALL, COLOR_PLAYER_A)
        tb = render_text(f"玩家B 剩 {cnt_b} 块", FONT_SMALL, COLOR_PLAYER_B)
        surface.blit(ta, (20, 40))
        surface.blit(tb, (W - tb.get_width() - 20, 40))

        remain = max(0.0, GAME_DURATION - session_a.elapsed)
        t = render_text(f"对战剩余 {remain:.0f}s", FONT_MID, (255, 255, 255))
        surface.blit(t, (W // 2 - t.get_width() // 2,
                         BATTLE_TRACK_TOP - 80))

    def _draw_flag(self, surface, cx, cy):
        pole_h = 40
        pole_x = cx - 20
        pygame.draw.line(surface, BATTLE_FLAG_POLE,
                         (pole_x, cy - pole_h // 2),
                         (pole_x, cy + pole_h // 2), 3)
        flag_w = 32
        flag_h = 24
        flag_x = pole_x + 2
        flag_y = cy - pole_h // 2
        cell = flag_w // 4
        for row in range(2):
            for col in range(4):
                c = (255, 255, 255) if (row + col) % 2 == 0 else (30, 30, 30)
                pygame.draw.rect(surface, c,
                                 pygame.Rect(flag_x + col * (flag_w // 4),
                                             flag_y + row * (flag_h // 2),
                                             cell, flag_h // 2))
        pygame.draw.rect(surface, BATTLE_FLAG_COLOR,
                         pygame.Rect(flag_x, flag_y, flag_w, flag_h), 2)


# ============================================================
# 场景
# ============================================================
class SceneState(Enum):
    CATEGORY = auto()
    BALL_SELECT = auto()
    ENCYCLOPEDIA = auto()
    PLAYING = auto()
    BATTLE = auto()
    END = auto()
    SETTINGS = auto()


class Scene:
    def __init__(self, game):
        self.game = game
        self._back_btn_rect = pygame.Rect(20, 24, 140, 52)
        self._back_btn_hover = False

    def _handle_back_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in _BACK_KEYS:
            self.on_back()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if getattr(event, "button", 1) in (1, 0, 2, 3):
                if self._back_btn_rect.collidepoint(event.pos):
                    self.on_back()
                    return True
        return False

    def _update_back_hover(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._back_btn_hover = self._back_btn_rect.collidepoint(event.pos)

    def draw_back_button(self, surface, text="◀ 返回"):
        rect = self._back_btn_rect
        col = (95, 135, 195) if self._back_btn_hover else (70, 100, 150)
        pygame.draw.rect(surface, col, rect, border_radius=18)
        surf = render_text(text, FONT_SMALL, (235, 240, 255))
        surface.blit(surf, surf.get_rect(center=rect.center))

    def on_back(self):
        self.game.pop_scene()

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class CategoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.hover = -1
        self.cat_rects = [pygame.Rect(60, 200 + i * 125, W - 120, 110)
                          for i in range(3)]
        self.btn_settings = Button(
            (W - 130, 30, 100, 60), "设置",
            lambda: self.game.push_scene(SceneState.SETTINGS),
            color=(60, 80, 110), text_color=(200, 220, 255),
            font_size=FONT_SMALL, border_radius=20,
        )
        self.btn_battle = Button(
            (W // 2 - 130, 800, 260, 70), "双人对战",
            self._on_battle,
            color=COLOR_BTN_RED, text_color=(255, 240, 240),
            font_size=FONT_MID, border_radius=20,
        )

    def on_back(self):
        self.game.running = False

    def _on_battle(self):
        self.game.push_scene(SceneState.BALL_SELECT, category_index=0,
                             battle_mode=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in _BACK_KEYS:
            self.on_back()
            return
        self.btn_settings.handle_event(event)
        self.btn_battle.handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            self.hover = -1
            for i, r in enumerate(self.cat_rects):
                if r.collidepoint(event.pos):
                    self.hover = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if getattr(event, "button", 1) in (1, 0, 2, 3):
                for i, r in enumerate(self.cat_rects):
                    if r.collidepoint(event.pos):
                        self.game.push_scene(SceneState.BALL_SELECT,
                                             category_index=i)
                        break

    def draw(self, surface):
        title = render_text("数学球砸砖块", FONT_HUGE, COLOR_WHITE)
        surface.blit(title, (W // 2 - title.get_width() // 2, 60))
        sub = render_text("按增长速度分类", FONT_MID, COLOR_TEXT_DIM)
        surface.blit(sub, (W // 2 - sub.get_width() // 2, 150))

        result = _VALIDATE_RESULT
        if result:
            bc = result["ball_count"]
            ec = result["expected_ball_count"]
            sc = result["seq_count"]
            kc = result["skill_count"]
            brick_n = len(Settings().get_brick_exponents())
            ok = (not result["missing_seq"] and not result["missing_skill"]
                  and not result["errors"] and bc == ec)
            color = (120, 200, 140) if ok else (255, 100, 100)
            txt = (f"数据校验：球 {bc}/{ec}，序列 {sc}/{bc}，"
                   f"技能 {kc}/{bc}，砖块 {brick_n} 档")
            surf = render_text(txt, FONT_TINY, color)
            surface.blit(surf, (W // 2 - surf.get_width() // 2, 190))

        for i, cat in enumerate(CATEGORIES):
            r = self.cat_rects[i]
            bg = COLOR_CAT_HOVER if i == self.hover else COLOR_CAT_NORMAL
            pygame.draw.rect(surface, bg, r, border_radius=20)
            pygame.draw.rect(surface, cat["color"], r, width=4, border_radius=20)
            surface.blit(render_text(cat["name"], FONT_BIG, cat["color"]),
                         (r.x + 30, r.y + 5))
            surface.blit(render_text(cat["desc"], FONT_SMALL, COLOR_TEXT),
                         (r.x + 30, r.y + 50))
            surface.blit(render_text(f"共 {len(cat['balls'])} 种球",
                                     FONT_SMALL, (160, 160, 160)),
                         (r.x + 30, r.y + 80))

        info_y = 580
        for i, s in enumerate([
            "游戏玩法：球会自动下落砸砖块。",
            "如果球上的数不够大，会被弹开，",
            "并且球自动增长到下一个数，直到能砸碎砖块。",
        ]):
            surface.blit(render_text(s, FONT_SMALL, COLOR_TEXT),
                         (40, info_y + i * 30))

        tip = render_text("请点击上方分类卡片进入", FONT_MID, (100, 200, 255))
        surface.blit(tip, (W // 2 - tip.get_width() // 2, 740))
        self.btn_settings.draw(surface)
        self.btn_battle.draw(surface)


class BallSelectScene(Scene):
    CARD_H = 95
    GAP = 10
    LIST_TOP = LIST_TOP_DEFAULT
    LIST_BOTTOM_OFFSET = 220

    def __init__(self, game, category_index, battle_mode=False,
                 selected_a_list=None, selected_b_list=None,
                 selected_key=None, selected_exponents=None,
                 selecting="A"):
        super().__init__(game)
        self.cat_idx = category_index
        self.battle_mode = battle_mode
        cat = CATEGORIES[category_index]
        self.balls = cat["balls"]
        self.color = cat["color"]
        self.selected_a_list = list(selected_a_list) if selected_a_list else []
        self.selected_b_list = list(selected_b_list) if selected_b_list else []
        self.selected_key = selected_key or self.balls[0]["key"]
        self.selecting = selecting if selecting in ("A", "B") else "A"

        if selected_exponents is not None:
            pool = set(BRICK_EXPONENT_POOL)
            cleaned, seen = [], set()
            for e in selected_exponents:
                try:
                    ei = int(e)
                except (TypeError, ValueError):
                    continue
                if ei in pool and ei not in seen:
                    seen.add(ei); cleaned.append(ei)
            self.selected_exponents = (sorted(cleaned) if cleaned
                                       else list(DEFAULT_BRICK_EXPONENTS))
        else:
            self.selected_exponents = Settings().get_brick_exponents()
        self._chip_rects = []
        self._layout_chips()
        self._chip_flash = {}
        self._last_chip_tick = 0

        slot_gap = 20
        slot_w = (W - slot_gap * 3) // 2
        self.slot_a_rect = pygame.Rect(slot_gap, 130, slot_w, 65)
        self.slot_b_rect = pygame.Rect(W - slot_gap - slot_w, 130, slot_w, 65)

        self.tabs = []
        tab_w = (W - 40) // 3
        for i, c in enumerate(CATEGORIES):
            rect = pygame.Rect(20 + i * tab_w, TABS_TOP, tab_w - 8, TAB_H)
            self.tabs.append((rect, i, c["name"], c["color"]))
        self.hover_tab = -1

        self.scroll_y = 0.0
        self.velocity = 0.0
        self.card_w = W - 60
        self.list_bottom = H - self.LIST_BOTTOM_OFFSET
        total_h = len(self.balls) * self.CARD_H + (len(self.balls) - 1) * self.GAP
        self.min_scroll = min(0.0, (self.list_bottom - self.LIST_TOP) - total_h)
        self.dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0.0
        self.dragging_moved = False
        self._pending = None

        start_text = "开始对战" if battle_mode else "开始演示"
        self.btn_start = Button((W // 2 - 150, H - 80, 300, 60), start_text,
                                self._on_start, color=COLOR_BTN_GREEN)
        if battle_mode:
            half_w = (W - 40) // 2
            self.btn_reset = Button(
                (20, H - 160, half_w - 10, 60),
                "清空重选", self._on_reset,
                color=COLOR_BTN_GRAY,
                text_color=(220, 220, 220),
                font_size=FONT_SMALL,
            )
            self.btn_all = Button(
                (W // 2 + 10, H - 160, half_w - 10, 60),
                "全选", self._on_select_all,
                color=(70, 110, 160),
                text_color=(230, 240, 255),
                font_size=FONT_SMALL,
            )
            self.btn_ency = None
        else:
            self.btn_reset = None
            self.btn_all = None
            self.btn_ency = Button((W // 2 - 160, H - 160, 320, 60),
                                   "查看全屏球类百科", self._on_open_ency,
                                   color=COLOR_BTN_BLUE,
                                   text_color=(150, 200, 255))

    def _layout_chips(self):
        self._chip_rects = []
        pool = list(BRICK_EXPONENT_POOL)
        per_row = _CHIP_PER_ROW
        rows = [pool[i:i + per_row] for i in range(0, len(pool), per_row)]
        for r, row_items in enumerate(rows):
            n = len(row_items)
            total_w = n * CHIP_W + (n - 1) * CHIP_GAP_X
            x0 = (W - total_w) // 2
            y = CHIP_PANEL_TOP + CHIP_TITLE_H + r * (CHIP_H + CHIP_GAP_Y)
            for c, exp in enumerate(row_items):
                x = x0 + c * (CHIP_W + CHIP_GAP_X)
                self._chip_rects.append(
                    (pygame.Rect(x, y, CHIP_W, CHIP_H), exp))

    def _toggle_exponent(self, exp):
        if exp in self.selected_exponents:
            if len(self.selected_exponents) <= 1:
                self._chip_flash[exp] = ("reject", 0.25)
                return
            self.selected_exponents = [
                e for e in self.selected_exponents if e != exp
            ]
        else:
            self.selected_exponents = sorted(
                self.selected_exponents + [exp]
            )
        self._chip_flash[exp] = ("ok", 0.25)
        Settings().set_brick_exponents(self.selected_exponents)

    def _candidate_positions(self, event):
        """候选坐标：优先信任 event 自身给出的坐标。
        只有明显超出逻辑尺寸，才追加缩放候选，避免误命中。"""
        cands = []
        pos = getattr(event, "pos", None)
        if pos is not None:
            px, py = int(pos[0]), int(pos[1])
            cands.append((px, py))
            if px > W or py > H or px < 0 or py < 0:
                try:
                    ww, wh = pygame.display.get_window_size()
                    if ww and wh and (ww != W or wh != H):
                        cands.append((int(px * W / ww), int(py * H / wh)))
                except Exception:
                    pass
        ex = getattr(event, "x", None)
        ey = getattr(event, "y", None)
        if ex is not None and ey is not None:
            cands.append((int(ex * W), int(ey * H)))
        return cands

    def _try_chip_hit(self, event):
        now = pygame.time.get_ticks()
        for pos in self._candidate_positions(event):
            for rect, exp in self._chip_rects:
                if rect.inflate(CHIP_GAP_X, 14).collidepoint(pos):
                    if self._last_chip_tick > now - 20:
                        return True
                    self._last_chip_tick = now
                    self._toggle_exponent(exp)
                    return True
        return False

    def _handle_ui_click(self, pos):
        """统一处理槽位 / 分类 tab / 底部按钮；命中返回 True。"""
        if self.battle_mode:
            if self.slot_a_rect.collidepoint(pos):
                self.selecting = "A"; return True
            if self.slot_b_rect.collidepoint(pos):
                self.selecting = "B"; return True
        for rect, idx, name, col in self.tabs:
            if rect.collidepoint(pos):
                self._switch_category(idx); return True
        if self.btn_start.rect.collidepoint(pos):
            self._on_start(); return True
        if self.btn_reset is not None and self.btn_reset.rect.collidepoint(pos):
            self._on_reset(); return True
        if self.btn_all is not None and self.btn_all.rect.collidepoint(pos):
            self._on_select_all(); return True
        if self.btn_ency is not None and self.btn_ency.rect.collidepoint(pos):
            self._on_open_ency(); return True
        return False

    def _try_ui_click(self, event):
        for pos in self._candidate_positions(event):
            if self._handle_ui_click(pos):
                return True
        return False

    def on_back(self):
        self.game.pop_scene()

    def _switch_category(self, idx):
        if idx == self.cat_idx:
            return
        # 注意：要把 selecting 一并透传，否则新场景会默认回到 A
        self.game.replace_scene(SceneState.BALL_SELECT,
                                category_index=idx,
                                battle_mode=self.battle_mode,
                                selected_a_list=self.selected_a_list,
                                selected_b_list=self.selected_b_list,
                                selected_key=self.selected_key,
                                selected_exponents=list(self.selected_exponents),
                                selecting=self.selecting)

    def _on_reset(self):
        self.selected_a_list = []
        self.selected_b_list = []
        self.selecting = "A"

    def _on_select_all(self):
        keys = [b["key"] for b in self.balls]
        target_list = (self.selected_a_list if self.selecting == "A"
                       else self.selected_b_list)
        all_selected = all(k in target_list for k in keys)
        if all_selected:
            for k in keys:
                if k in target_list:
                    target_list.remove(k)
        else:
            for k in keys:
                if k not in target_list:
                    target_list.append(k)

    def _on_start(self):
        exps = list(self.selected_exponents)
        if self.battle_mode:
            if not self.selected_a_list or not self.selected_b_list:
                return
            self.game.replace_scene(
                SceneState.BATTLE,
                ball_type_a_list=self.selected_a_list,
                ball_type_b_list=self.selected_b_list,
                brick_exponents=exps,
            )
        else:
            self.game.replace_scene(SceneState.PLAYING,
                                    ball_type=self.selected_key,
                                    brick_exponents=exps)

    def _on_open_ency(self):
        self.game.push_scene(SceneState.ENCYCLOPEDIA,
                             category_index=self.cat_idx)

    def _toggle_ball(self, i):
        key = self.balls[i]["key"]
        target_list = (self.selected_a_list if self.selecting == "A"
                       else self.selected_b_list)
        if key in target_list:
            target_list.remove(key)
        else:
            target_list.append(key)

    def handle_event(self, event):
        if self._handle_back_event(event):
            return
        self._update_back_hover(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # chip 只在 DOWN / FINGERDOWN 处理，避免同一次点击 DOWN+UP 各触发一次
            if self._try_chip_hit(event):
                return
            # tab / slot / 按钮 三路兜底，兼容安卓只发 UP 的情况
            if self._try_ui_click(event):
                return
            btn = getattr(event, "button", 1)
            if btn in (1, 0, 2, 3):
                if self.LIST_TOP <= event.pos[1] <= self.list_bottom:
                    self.dragging = True
                    self.dragging_moved = False
                    self.drag_start_y = event.pos[1]
                    self.drag_start_scroll = self.scroll_y
                    self.velocity = 0.0
                    self._pending = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            # tab / slot / 按钮 兜底：部分设备只发 UP 不发 DOWN
            if self._try_ui_click(event):
                return
            # 列表拖拽 / 点选球卡片
            if self.dragging:
                self.dragging = False
                if not self.dragging_moved and self._pending:
                    for i in range(len(self.balls)):
                        r = self._card_rect(i)
                        if (self.LIST_TOP <= self._pending[1] <= self.list_bottom
                                and r.collidepoint(self._pending)):
                            if self.battle_mode:
                                self._toggle_ball(i)
                            else:
                                self.selected_key = self.balls[i]["key"]
                            break
            self._pending = None

        elif event.type == pygame.FINGERDOWN:
            if self._try_chip_hit(event):
                return
            if self._try_ui_click(event):
                return

        elif event.type == pygame.MOUSEMOTION:
            self.btn_start.hover = self.btn_start.rect.collidepoint(event.pos)
            if self.btn_reset is not None:
                self.btn_reset.hover = self.btn_reset.rect.collidepoint(event.pos)
            if self.btn_all is not None:
                self.btn_all.hover = self.btn_all.rect.collidepoint(event.pos)
            if self.btn_ency is not None:
                self.btn_ency.hover = self.btn_ency.rect.collidepoint(event.pos)
            self.hover_tab = -1
            for rect, idx, name, col in self.tabs:
                if rect.collidepoint(event.pos):
                    self.hover_tab = idx
                    break
            if self.dragging:
                dy = event.pos[1] - self.drag_start_y
                if abs(dy) > 8:
                    self.dragging_moved = True
                new = self.drag_start_scroll + dy
                self.velocity = (new - self.scroll_y) * 30.0
                self.scroll_y = max(min(0, self.min_scroll), min(0, new))

    def update(self, dt):
        if self._chip_flash:
            for k in list(self._chip_flash.keys()):
                kind, t = self._chip_flash[k]
                t -= dt
                if t <= 0:
                    del self._chip_flash[k]
                else:
                    self._chip_flash[k] = (kind, t)
        if self.dragging:
            return
        if abs(self.velocity) > 1.0:
            self.scroll_y += self.velocity * dt
            self.velocity *= max(0.0, 1.0 - 8.0 * dt)
            self.scroll_y = max(min(0, self.min_scroll), min(0, self.scroll_y))
        else:
            self.velocity = 0.0

    def _card_rect(self, i):
        y = self.LIST_TOP + i * (self.CARD_H + self.GAP) + int(self.scroll_y)
        return pygame.Rect(30, y, self.card_w, self.CARD_H)

    def _draw_chip_panel(self, surface):
        panel_rect = pygame.Rect(0, CHIP_PANEL_TOP, W, CHIP_PANEL_H)
        pygame.draw.rect(surface, (25, 30, 45), panel_rect)
        pygame.draw.line(surface, (55, 65, 90),
                         (0, CHIP_PANEL_TOP), (W, CHIP_PANEL_TOP), 2)
        title_surf = render_text("砖块指数（至少保留 1 个）",
                                 FONT_TINY, COLOR_TEXT_DIM)
        surface.blit(title_surf, (CHIP_PAD, CHIP_PANEL_TOP + 6))
        for rect, exp in self._chip_rects:
            sel = exp in self.selected_exponents
            flash = self._chip_flash.get(exp)
            if flash:
                kind, _ = flash
                border = (255, 255, 120) if kind == "ok" else (255, 90, 90)
                border_w = 4
            else:
                border = (150, 195, 255) if sel else (70, 85, 110)
                border_w = 2
            bg = (80, 130, 200) if sel else (45, 55, 75)
            pygame.draw.rect(surface, bg, rect, border_radius=12)
            pygame.draw.rect(surface, border, rect, width=border_w,
                             border_radius=12)
            txt = render_text(f"10^{exp}", FONT_SMALL,
                              (255, 255, 255) if sel else (170, 180, 200))
            surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_slot(self, surface, rect, who, key_list):
        is_active = (self.selecting == who)
        base_color = COLOR_PLAYER_A if who == "A" else COLOR_PLAYER_B
        if is_active:
            bg = (base_color[0] // 5 + 25,
                  base_color[1] // 5 + 25,
                  base_color[2] // 5 + 25)
            border = base_color
            bw = 4
        else:
            bg = (32, 38, 52)
            border = (70, 80, 100)
            bw = 2
        pygame.draw.rect(surface, bg, rect, border_radius=12)
        pygame.draw.rect(surface, border, rect, width=bw, border_radius=12)

        label_surf = render_text(f"玩家{who}", FONT_TINY,
                                 base_color if is_active else (150, 160, 180))
        surface.blit(label_surf, (rect.x + 12, rect.y + 6))

        if key_list:
            count = len(key_list)
            name = (find_ball_name(key_list[0]) if count == 1
                    else f"已选 {count} 个球")
            name_color = (255, 255, 255) if is_active else (210, 220, 230)
        else:
            name = "点此选择（可多选）"
            name_color = (130, 140, 160)
        name_surf = render_text(name, FONT_SMALL, name_color)
        surface.blit(name_surf, (rect.x + 12, rect.y + 32))

        if key_list:
            icon_surf = render_text("✓", FONT_MID, base_color)
            surface.blit(icon_surf,
                         (rect.right - icon_surf.get_width() - 15,
                          rect.y + 15))
        elif is_active:
            icon_surf = render_text("▶", FONT_SMALL, base_color)
            surface.blit(icon_surf,
                         (rect.right - icon_surf.get_width() - 15,
                          rect.y + 20))

    def _draw_tabs(self, surface):
        for rect, idx, name, col in self.tabs:
            is_active = (idx == self.cat_idx)
            is_hover = (idx == self.hover_tab) and not is_active
            if is_active:
                bg = col; txt_col = (20, 20, 30); border_col = col
            elif is_hover:
                bg = (col[0] // 3 + 30, col[1] // 3 + 30, col[2] // 3 + 30)
                txt_col = col; border_col = col
            else:
                bg = (35, 40, 55); txt_col = col; border_col = (70, 80, 100)
            pygame.draw.rect(surface, bg, rect, border_radius=12)
            pygame.draw.rect(surface, border_col, rect, width=2, border_radius=12)
            txt = render_text(name, FONT_SMALL, txt_col)
            surface.blit(txt, txt.get_rect(center=rect.center))

    def draw(self, surface):
        title_txt = "双人对战" if self.battle_mode else CATEGORIES[self.cat_idx]["name"]
        title = render_text(title_txt, FONT_BIG, self.color)
        surface.blit(title, (W // 2 - title.get_width() // 2, 60))

        if self.battle_mode:
            self._draw_slot(surface, self.slot_a_rect, "A", self.selected_a_list)
            self._draw_slot(surface, self.slot_b_rect, "B", self.selected_b_list)
            hint_surf = render_text(
                "点上方槽位切换 A/B，点列表可多选/取消该玩家的球",
                FONT_TINY, COLOR_TEXT_DARK)
            surface.blit(hint_surf,
                         (W // 2 - hint_surf.get_width() // 2, 200))
        else:
            s1 = render_text("上下滑动列表，点击选中球，",
                             FONT_TINY, COLOR_TEXT_DIM)
            surface.blit(s1, (W // 2 - s1.get_width() // 2, 160))
            s2 = render_text("上方可切换分类。",
                             FONT_TINY, COLOR_TEXT_DIM)
            surface.blit(s2, (W // 2 - s2.get_width() // 2, 185))

        self._draw_chip_panel(surface)
        self._draw_tabs(surface)

        clip = pygame.Rect(0, self.LIST_TOP, W,
                           self.list_bottom - self.LIST_TOP)
        old = surface.get_clip()
        surface.set_clip(clip)
        for i, b in enumerate(self.balls):
            r = self._card_rect(i)
            if r.bottom < clip.top or r.top > clip.bottom:
                continue

            if self.battle_mode:
                is_a = (b["key"] in self.selected_a_list)
                is_b = (b["key"] in self.selected_b_list)
                is_sel = is_a or is_b
            else:
                is_sel = (self.selected_key == b["key"])
                is_a = is_b = False

            bg = (60, 90, 130) if is_sel else (35, 42, 60)
            border = self.color if is_sel else (60, 70, 95)
            bw = 4 if is_sel else 2
            pygame.draw.rect(surface, bg, r, border_radius=12)
            pygame.draw.rect(surface, border, r, width=bw, border_radius=12)

            surface.blit(render_text(b["name"], FONT_MID, COLOR_WHITE),
                         (r.x + 25, r.y + 12))
            surface.blit(render_text(f"公式：{b['formula']}",
                                     FONT_SMALL, self.color),
                         (r.x + 25, r.y + 55))

            if self.battle_mode and is_sel:
                if is_a and is_b:
                    badge = render_text("A+B", FONT_SMALL, (255, 255, 120))
                    surface.blit(badge,
                                 (r.right - badge.get_width() - 20, r.y + 20))
                elif is_a:
                    badge = render_text("A", FONT_MID, COLOR_PLAYER_A)
                    surface.blit(badge,
                                 (r.right - badge.get_width() - 25, r.y + 20))
                elif is_b:
                    badge = render_text("B", FONT_MID, COLOR_PLAYER_B)
                    surface.blit(badge,
                                 (r.right - badge.get_width() - 25, r.y + 20))
        surface.set_clip(old)

        if self.btn_all is not None:
            keys = [b["key"] for b in self.balls]
            target_list = (self.selected_a_list if self.selecting == "A"
                           else self.selected_b_list)
            all_selected = keys and all(k in target_list for k in keys)
            self.btn_all.text = "取消全选" if all_selected else "全选"

        self.btn_start.draw(surface)
        if self.btn_reset is not None:
            self.btn_reset.draw(surface)
        if self.btn_all is not None:
            self.btn_all.draw(surface)
        if self.btn_ency is not None:
            self.btn_ency.draw(surface)

        self.draw_back_button(surface)


class EncyclopediaScene(Scene):
    LINE_H = 28
    VIEW_TOP = 110

    def __init__(self, game, category_index):
        super().__init__(game)
        self.cat_idx = category_index
        cat = CATEGORIES[category_index]
        self.balls = cat["balls"]
        self.color = cat["color"]
        self.lines = self._build_lines()
        avail = H - self.VIEW_TOP
        total = len(self.lines) * self.LINE_H
        self.min_scroll = min(0.0, avail - total)
        self.scroll_y = 0.0
        self.velocity = 0.0
        self.dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0.0

    def _build_lines(self):
        max_w = W - 80
        lines = []
        for b in self.balls:
            lines.append(("header", f"【{b['name']}】"))
            for raw in b.get("skill", "").split("\n"):
                if not raw:
                    lines.append(("empty", ""))
                    continue
                for ln in wrap_text_pixels(raw, FONT_TINY, max_w):
                    lines.append(("skill", ln))
            lines.append(("empty", ""))
        return lines

    def on_back(self):
        self.game.pop_scene()

    def handle_event(self, event):
        if self._handle_back_event(event):
            return
        self._update_back_hover(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if getattr(event, "button", 1) in (1, 0, 2, 3):
                self.dragging = True
                self.drag_start_y = event.pos[1]
                self.drag_start_scroll = self.scroll_y
                self.velocity = 0
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dy = event.pos[1] - self.drag_start_y
                new = self.drag_start_scroll + dy
                self.velocity = (new - self.scroll_y) * 30.0
                self.scroll_y = max(min(0, self.min_scroll), min(0, new))
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def update(self, dt):
        if self.dragging:
            return
        if abs(self.velocity) > 1.0:
            self.scroll_y += self.velocity * dt
            self.velocity *= max(0.0, 1.0 - 8.0 * dt)
            self.scroll_y = max(min(0, self.min_scroll), min(0, self.scroll_y))

    def draw(self, surface):
        surface.blit(self.game.bg_surface, (0, 0))
        pygame.draw.rect(surface, (20, 25, 35), (0, 0, W, 100))
        tt = render_text(f"球类百科 - {CATEGORIES[self.cat_idx]['name']}",
                         FONT_BIG, self.color)
        surface.blit(tt, (W // 2 - tt.get_width() // 2, 20))

        clip = pygame.Rect(0, self.VIEW_TOP, W, H - self.VIEW_TOP)
        old = surface.get_clip()
        surface.set_clip(clip)
        y = self.VIEW_TOP + 20 + int(self.scroll_y)
        for kind, text in self.lines:
            if y > H + 40:
                break
            if y + self.LINE_H < self.VIEW_TOP:
                y += self.LINE_H
                continue
            if kind == "empty":
                y += self.LINE_H
                continue
            color = {"header": self.color, "skill": (255, 200, 100)}.get(
                kind, COLOR_TEXT)
            surface.blit(render_text(text, FONT_TINY, color), (40, y))
            y += self.LINE_H
        surface.set_clip(old)

        tip = render_text("↑ 上下滑动查看全部介绍 ↑",
                          FONT_TINY, COLOR_TEXT_DARK)
        surface.blit(tip, (W // 2 - tip.get_width() // 2, H - 30))

        self.draw_back_button(surface)


class PlayingScene(Scene):
    def __init__(self, game, ball_type, brick_exponents=None):
        super().__init__(game)
        self.ball_type = ball_type
        self.brick_exponents = (tuple(brick_exponents)
                                if brick_exponents is not None else None)
        self.session = GameSession([ball_type],
                                   brick_exponents=self.brick_exponents)
        self.renderer = GameRenderer()
        self._finalized = False
        self.paused = False
        self._pause_btns = self._make_pause_buttons()

    def _make_pause_buttons(self):
        bw, bh, gap = 320, 64, 20
        total = 4 * bh + 3 * gap
        y0 = H // 2 - total // 2
        x = W // 2 - bw // 2
        defs = [
            ("继续", self._resume),
            ("重开", self._restart),
            ("返回选球", self._back_select),
            ("返回主菜单", self._back_menu),
        ]
        btns = []
        for i, (text, cb) in enumerate(defs):
            rect = pygame.Rect(x, y0 + i * (bh + gap), bw, bh)
            btns.append(Button(rect, text, cb,
                               color=COLOR_BTN_BLUE,
                               text_color=(220, 230, 255),
                               font_size=FONT_MID,
                               border_radius=16))
        return btns

    def _resume(self):
        self.paused = False

    def _restart(self):
        self.paused = False
        self.game.replace_scene(SceneState.PLAYING,
                                ball_type=self.ball_type,
                                brick_exponents=self.brick_exponents)

    def _back_select(self):
        self.paused = False
        cat_idx = find_category_index(self.ball_type)
        self.game.replace_scene(SceneState.BALL_SELECT,
                                category_index=cat_idx,
                                battle_mode=False,
                                selected_key=self.ball_type)

    def _back_menu(self):
        self.paused = False
        self.game.replace_scene(SceneState.CATEGORY)

    def _finalize(self, scene, **kwargs):
        if self._finalized:
            return
        self._finalized = True
        self.game.replace_scene(scene, **kwargs)

    def on_back(self):
        self.paused = not self.paused

    def handle_event(self, event):
        if self.paused:
            if event.type == pygame.KEYDOWN and event.key in _BACK_KEYS:
                self.paused = False
                return
            for b in self._pause_btns:
                b.handle_event(event)
            return
        if self._handle_back_event(event):
            return
        self._update_back_hover(event)

    def update(self, dt):
        if self._finalized or self.paused:
            return
        self.session.update(dt)
        self.renderer.update_dynamic_text(self.session, dt)
        if self.session.is_finished(GAME_DURATION):
            self._finalize(SceneState.END,
                           ball_type=self.ball_type,
                           brick_exponents=self.brick_exponents)

    def _draw_pause_overlay(self, surface):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        title = render_text("暂停", FONT_HUGE, (255, 255, 255))
        surface.blit(title, (W // 2 - title.get_width() // 2, 300))
        for b in self._pause_btns:
            b.draw(surface)

    def draw(self, surface):
        offset = (0, 0)
        if self.session.shake_timer > 0:
            offset = (random.randint(-int(self.session.shake_intensity),
                                     int(self.session.shake_intensity)),
                      random.randint(-int(self.session.shake_intensity),
                                     int(self.session.shake_intensity)))
        self.renderer.draw(surface, self.session, offset)
        if self.session.no_targets:
            warn = render_text("本关无可用目标", FONT_BIG, (255, 100, 100))
            surface.blit(warn, (W // 2 - warn.get_width() // 2, H // 2))
        if self.paused:
            self._draw_pause_overlay(surface)
        self.draw_back_button(surface)


class BattleScene(Scene):
    def __init__(self, game, ball_type_a_list, ball_type_b_list,
                 brick_exponents=None):
        super().__init__(game)
        self.ball_type_a_list = list(ball_type_a_list)
        self.ball_type_b_list = list(ball_type_b_list)
        self.brick_exponents = (tuple(brick_exponents)
                                if brick_exponents is not None else None)
        self.session_a = GameSession(self.ball_type_a_list,
                                     is_battle=True, side="A",
                                     brick_exponents=self.brick_exponents)
        self.session_b = GameSession(self.ball_type_b_list,
                                     is_battle=True, side="B",
                                     brick_exponents=self.brick_exponents)
        self.session_a.ctx.opponent_session = self.session_b
        self.session_b.ctx.opponent_session = self.session_a
        self.renderer = GameRenderer()
        self._finalized = False
        self._result = None
        self.paused = False
        self._pause_btns = self._make_pause_buttons()

    def _make_pause_buttons(self):
        bw, bh, gap = 320, 64, 20
        total = 4 * bh + 3 * gap
        y0 = H // 2 - total // 2
        x = W // 2 - bw // 2
        defs = [
            ("继续", self._resume),
            ("重开", self._restart),
            ("返回选球", self._back_select),
            ("返回主菜单", self._back_menu),
        ]
        btns = []
        for i, (text, cb) in enumerate(defs):
            rect = pygame.Rect(x, y0 + i * (bh + gap), bw, bh)
            btns.append(Button(rect, text, cb,
                               color=COLOR_BTN_BLUE,
                               text_color=(220, 230, 255),
                               font_size=FONT_MID,
                               border_radius=16))
        return btns

    def _resume(self):
        self.paused = False

    def _restart(self):
        self.paused = False
        self.game.replace_scene(SceneState.BATTLE,
                                ball_type_a_list=self.ball_type_a_list,
                                ball_type_b_list=self.ball_type_b_list,
                                brick_exponents=self.brick_exponents)

    def _back_select(self):
        self.paused = False
        cat_idx = 0
        if self.ball_type_a_list:
            cat_idx = find_category_index(self.ball_type_a_list[0])
        self.game.replace_scene(SceneState.BALL_SELECT,
                                category_index=cat_idx,
                                battle_mode=True,
                                selected_a_list=self.ball_type_a_list,
                                selected_b_list=self.ball_type_b_list)

    def _back_menu(self):
        self.paused = False
        self.game.replace_scene(SceneState.CATEGORY)

    def _finalize(self, scene, **kwargs):
        if self._finalized:
            return
        self._finalized = True
        self.game.replace_scene(scene, **kwargs)

    def on_back(self):
        self.paused = not self.paused

    def handle_event(self, event):
        if self.paused:
            if event.type == pygame.KEYDOWN and event.key in _BACK_KEYS:
                self.paused = False
                return
            for b in self._pause_btns:
                b.handle_event(event)
            return
        if self._handle_back_event(event):
            return
        self._update_back_hover(event)

    def _check_winner(self):
        a_clear = all(not b.alive for b in self.session_a.bricks)
        b_clear = all(not b.alive for b in self.session_b.bricks)
        if a_clear and b_clear:
            self._result = "DRAW"; return True
        if a_clear:
            self._result = "A"; return True
        if b_clear:
            self._result = "B"; return True
        if self.session_a.elapsed > GAME_DURATION:
            ca = self.session_a.alive_brick_count()
            cb = self.session_b.alive_brick_count()
            if ca < cb:
                self._result = "A"
            elif cb < ca:
                self._result = "B"
            else:
                ha = self.session_a.total_hp()
                hb = self.session_b.total_hp()
                if ha < hb:
                    self._result = "A"
                elif hb < ha:
                    self._result = "B"
                else:
                    self._result = "DRAW"
            return True
        return False

    def update(self, dt):
        if self._finalized or self.paused:
            return
        self.session_a.update(dt)
        self.session_b.update(dt)
        self.renderer.update_dynamic_text(self.session_a, dt)
        if self._check_winner():
            self._finalize(SceneState.END,
                           ball_type_a_list=self.ball_type_a_list,
                           ball_type_b_list=self.ball_type_b_list,
                           battle_result=self._result, battle=True,
                           brick_exponents=self.brick_exponents)

    def _draw_pause_overlay(self, surface):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        title = render_text("暂停", FONT_HUGE, (255, 255, 255))
        surface.blit(title, (W // 2 - title.get_width() // 2, 300))
        for b in self._pause_btns:
            b.draw(surface)

    def draw(self, surface):
        offset = (0, 0)
        intensity = 0
        if self.session_a.shake_timer > 0:
            intensity = max(intensity, int(self.session_a.shake_intensity))
        if self.session_b.shake_timer > 0:
            intensity = max(intensity, int(self.session_b.shake_intensity))
        if intensity > 0:
            offset = (random.randint(-intensity, intensity),
                      random.randint(-intensity, intensity))

        self.renderer.draw_battle(surface, self.session_a, self.session_b,
                                   offset)
        if self.paused:
            self._draw_pause_overlay(surface)
        self.draw_back_button(surface)


class EndScene(Scene):
    def __init__(self, game, ball_type=None, battle_result=None, battle=False,
                 ball_type_a_list=None, ball_type_b_list=None,
                 brick_exponents=None):
        super().__init__(game)
        self.ball_type = ball_type
        self.ball_type_a_list = ball_type_a_list
        self.ball_type_b_list = ball_type_b_list
        self.battle_result = battle_result
        self.battle = battle
        self.brick_exponents = (tuple(brick_exponents)
                                if brick_exponents is not None else None)
        self.btn_restart = Button((W // 2 - 150, H // 2 + 40, 300, 70), "重开",
                                  self._on_restart, color=COLOR_BTN_GREEN)
        self.btn_menu = Button((W // 2 - 150, H // 2 + 140, 300, 70), "返回主菜单",
                               self._on_menu, color=COLOR_BTN_BLUE,
                               text_color=(200, 220, 255))

    def on_back(self):
        self._on_menu()

    def _on_restart(self):
        if self.battle:
            self.game.replace_scene(SceneState.BATTLE,
                                    ball_type_a_list=self.ball_type_a_list,
                                    ball_type_b_list=self.ball_type_b_list,
                                    brick_exponents=self.brick_exponents)
        else:
            self.game.replace_scene(SceneState.PLAYING,
                                    ball_type=self.ball_type,
                                    brick_exponents=self.brick_exponents)

    def _on_menu(self):
        self.game.replace_scene(SceneState.CATEGORY)

    def handle_event(self, event):
        if self._handle_back_event(event):
            return
        self._update_back_hover(event)
        self.btn_restart.handle_event(event)
        self.btn_menu.handle_event(event)

    def draw(self, surface):
        surface.blit(self.game.bg_surface, (0, 0))
        if self.battle:
            if self.battle_result == "A":
                txt, col = "玩家 A 胜利！", COLOR_PLAYER_A
            elif self.battle_result == "B":
                txt, col = "玩家 B 胜利！", COLOR_PLAYER_B
            else:
                txt, col = "平局！", (220, 220, 220)
            et = render_text(txt, FONT_HUGE, col)
            surface.blit(et, (W // 2 - et.get_width() // 2, H // 2 - 160))
        else:
            et = render_text("演示结束", FONT_BIG, COLOR_WHITE)
            surface.blit(et, (W // 2 - et.get_width() // 2, H // 2 - 100))
        self.btn_restart.draw(surface)
        self.btn_menu.draw(surface)
        self.draw_back_button(surface)


class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.settings = Settings()
        self.btn_sound = Button((W // 2 - 150, 240, 300, 60),
                                self._sound_text(), self._toggle_sound,
                                color=(60, 80, 110),
                                text_color=(200, 220, 255))
        self.btn_music = Button((W // 2 - 150, 320, 300, 60),
                                self._music_text(), self._toggle_music,
                                color=(60, 80, 110),
                                text_color=(200, 220, 255))
        self.slider = pygame.Rect(W // 2 - 150, 480, 300, 30)
        self.sfx_slider = pygame.Rect(W // 2 - 150, 640, 300, 30)
        self._drag_music = False
        self._drag_sfx = False

    def _sound_text(self):
        return f"音效：{'开' if self.settings.get('sound_enabled', True) else '关'}"

    def _music_text(self):
        return f"音乐：{'开' if self.settings.get('music_enabled', True) else '关'}"

    def _toggle_sound(self):
        self.settings.set("sound_enabled",
                          not self.settings.get("sound_enabled", True))
        self.btn_sound.text = self._sound_text()

    def _toggle_music(self):
        val = not self.settings.get("music_enabled", True)
        self.settings.set("music_enabled", val)
        try:
            if pygame.mixer.get_init():
                if val:
                    pygame.mixer.music.set_volume(
                        self.settings.get("music_volume", 0.7))
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
        except Exception:
            pass
        self.btn_music.text = self._music_text()

    def on_back(self):
        self.game.pop_scene()

    def handle_event(self, event):
        if self._handle_back_event(event):
            return
        self._update_back_hover(event)
        self.btn_sound.handle_event(event)
        self.btn_music.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if getattr(event, "button", 1) in (1, 0, 2, 3):
                if self.slider.inflate(0, 30).collidepoint(event.pos):
                    self._drag_music = True
                    self._update_music(event.pos[0])
                if self.sfx_slider.inflate(0, 30).collidepoint(event.pos):
                    self._drag_sfx = True
                    self._update_sfx(event.pos[0])
        elif event.type == pygame.MOUSEMOTION:
            if self._drag_music:
                self._update_music(event.pos[0])
            if self._drag_sfx:
                self._update_sfx(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag_music = False
            self._drag_sfx = False

    def _update_music(self, x):
        v = max(0.0, min(1.0, (x - self.slider.x) / self.slider.w))
        self.settings.set("music_volume", round(v, 2))
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(v)
        except Exception:
            pass

    def _update_sfx(self, x):
        v = max(0.0, min(1.0, (x - self.sfx_slider.x) / self.sfx_slider.w))
        self.settings.set("sfx_volume", round(v, 2))

    def draw(self, surface):
        surface.blit(self.game.bg_surface, (0, 0))
        title = render_text("设置", FONT_HUGE, COLOR_WHITE)
        surface.blit(title, (W // 2 - title.get_width() // 2, 100))
        self.btn_sound.draw(surface)
        self.btn_music.draw(surface)

        mv = self.settings.get("music_volume", 0.7)
        surface.blit(render_text(f"音乐音量：{int(mv * 100)}%",
                                 FONT_MID, COLOR_TEXT),
                     (self.slider.x, self.slider.y - 50))
        pygame.draw.rect(surface, (40, 45, 65), self.slider, border_radius=15)
        pygame.draw.rect(surface, (100, 180, 255),
                         pygame.Rect(self.slider.x, self.slider.y,
                                     int(self.slider.w * mv),
                                     self.slider.h), border_radius=15)
        pygame.draw.circle(surface, (255, 255, 255),
                           (self.slider.x + int(self.slider.w * mv),
                            self.slider.centery), 16)

        sv = self.settings.get("sfx_volume", 0.8)
        surface.blit(render_text(f"音效音量：{int(sv * 100)}%",
                                 FONT_MID, COLOR_TEXT),
                     (self.sfx_slider.x, self.sfx_slider.y - 50))
        pygame.draw.rect(surface, (40, 45, 65), self.sfx_slider, border_radius=15)
        pygame.draw.rect(surface, (100, 220, 140),
                         pygame.Rect(self.sfx_slider.x, self.sfx_slider.y,
                                     int(self.sfx_slider.w * sv),
                                     self.sfx_slider.h), border_radius=15)
        pygame.draw.circle(surface, (255, 255, 255),
                           (self.sfx_slider.x + int(self.sfx_slider.w * sv),
                            self.sfx_slider.centery), 16)

        self.draw_back_button(surface)


# ============================================================
# 校验
# ============================================================
_VALIDATE_RESULT = {}


def _validate_brick_exponents():
    try:
        s = Settings()
        exps = s.get_brick_exponents()
    except Exception as e:
        return f"brick_exponents 读取失败：{e}"
    if not isinstance(exps, (list, tuple)) or len(exps) < 1:
        return "brick_exponents 必须至少保留 1 档"
    pool = set(BRICK_EXPONENT_POOL)
    for e in exps:
        try:
            if int(e) not in pool:
                return f"brick_exponents 越界：{e}"
        except (TypeError, ValueError):
            return f"brick_exponents 非法值：{e}"
    return None


def validate_project():
    global _VALIDATE_RESULT
    keys = get_all_ball_keys()
    missing_seq = validate_data(keys)
    missing_skill = validate_skills(keys)
    errors = []
    if len(keys) != len(set(keys)):
        seen, dup = set(), []
        for k in keys:
            if k in seen:
                dup.append(k)
            seen.add(k)
        errors.append(f"重复球 key：{dup}")
    if len(keys) != EXPECTED_BALL_COUNT:
        errors.append(f"球数量不匹配：{len(keys)} != {EXPECTED_BALL_COUNT}")

    if "BattleScene" not in globals():
        errors.append("BATTLE 场景 BattleScene 未定义")

    be_err = _validate_brick_exponents()
    if be_err:
        errors.append(be_err)

    _VALIDATE_RESULT = {
        "ball_count": len(keys),
        "expected_ball_count": EXPECTED_BALL_COUNT,
        "seq_count": len(list_registered_sequences()),
        "skill_count": len(list_registered_skills()),
        "missing_seq": missing_seq,
        "missing_skill": missing_skill,
        "errors": errors,
        "brick_exponents_error": be_err,
    }
    r = _VALIDATE_RESULT
    print(f"[INFO] 球数量：{r['ball_count']} / {EXPECTED_BALL_COUNT}")
    print(f"[INFO] 序列注册表：{r['seq_count']}")
    print(f"[INFO] 技能注册表：{r['skill_count']}")
    try:
        bl = Settings().get_brick_exponents()
    except Exception:
        bl = []
    print(f"[INFO] 砖块档位：{bl}")
    if missing_seq:
        print(f"[ERROR] 缺少序列：{missing_seq}")
    if missing_skill:
        print(f"[WARN] 缺少技能：{missing_skill}")
    if be_err:
        print(f"[ERROR] 砖块指数：{be_err}")
    if errors:
        print(f"[WARN] {errors}")
    return r


# ============================================================
# Game 主循环
# ============================================================
class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass
        pygame.display.set_caption("数学球砸砖块")

        flags = pygame.SCALED
        if IS_MOBILE:
            flags |= pygame.FULLSCREEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.display.set_mode((W, H))

        self.clock = pygame.time.Clock()
        self.running = True
        self.bg_surface = self._build_bg()
        self.scene_stack = []

        self._load_bgm()
        self._push(SceneState.CATEGORY)

    def _load_bgm(self):
        if not pygame.mixer.get_init():
            print("[INFO] mixer 未初始化，跳过 BGM")
            return
        try:
            base = os.path.dirname(os.path.abspath(__file__))
            for name in ("bgm.ogg", "bgm.mp3", "bgm.wav"):
                path = os.path.join(base, name)
                if os.path.exists(path):
                    pygame.mixer.music.load(path)
                    s = Settings()
                    pygame.mixer.music.set_volume(s.get("music_volume", 0.7))
                    if s.get("music_enabled", True):
                        pygame.mixer.music.play(-1)
                    print(f"[INFO] 已加载 BGM: {name}")
                    return
            print("[INFO] 未找到 BGM 文件")
        except Exception as e:
            print(f"[WARN] BGM 加载失败：{e}")

    def _build_bg(self):
        surf = pygame.Surface((W, H)).convert()
        surf.fill(COLOR_BG)
        rnd = random.Random(20240501)
        for _ in range(120):
            x, y = rnd.randint(0, W - 1), rnd.randint(0, H - 1)
            c = rnd.randint(20, 60)
            surf.set_at((x, y), (c, c, c + 20))
        return surf

    def _make_scene(self, state, **kw):
        if state == SceneState.CATEGORY:
            return CategoryScene(self)
        if state == SceneState.BALL_SELECT:
            return BallSelectScene(
                self, kw["category_index"],
                battle_mode=kw.get("battle_mode", False),
                selected_a_list=kw.get("selected_a_list"),
                selected_b_list=kw.get("selected_b_list"),
                selected_key=kw.get("selected_key"),
                selected_exponents=kw.get("selected_exponents"),
                selecting=kw.get("selecting", "A"),
            )
        if state == SceneState.ENCYCLOPEDIA:
            return EncyclopediaScene(self, kw["category_index"])
        if state == SceneState.PLAYING:
            return PlayingScene(self, kw["ball_type"],
                                brick_exponents=kw.get("brick_exponents"))
        if state == SceneState.BATTLE:
            return BattleScene(self,
                               kw["ball_type_a_list"],
                               kw["ball_type_b_list"],
                               brick_exponents=kw.get("brick_exponents"))
        if state == SceneState.END:
            return EndScene(self,
                            ball_type=kw.get("ball_type"),
                            battle_result=kw.get("battle_result"),
                            battle=kw.get("battle", False),
                            ball_type_a_list=kw.get("ball_type_a_list"),
                            ball_type_b_list=kw.get("ball_type_b_list"),
                            brick_exponents=kw.get("brick_exponents"))
        if state == SceneState.SETTINGS:
            return SettingsScene(self)
        raise ValueError(state)

    def _push(self, state, **kw):
        clear_text_cache()
        self.scene_stack.append(self._make_scene(state, **kw))

    def push_scene(self, state, **kw):
        self._push(state, **kw)

    def pop_scene(self):
        if len(self.scene_stack) > 1:
            clear_text_cache()
            self.scene_stack.pop()
        else:
            self.running = False

    def replace_scene(self, state, **kw):
        if self.scene_stack:
            self.scene_stack.pop()
        clear_text_cache()
        self._push(state, **kw)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if self.scene_stack:
                    self.scene_stack[-1].handle_event(event)
                if not self.running:
                    break
            if not self.running:
                break
            if self.scene_stack:
                self.scene_stack[-1].update(dt)
            self.screen.blit(self.bg_surface, (0, 0))
            if self.scene_stack:
                self.scene_stack[-1].draw(self.screen)
            pygame.display.flip()

        Settings().save()
        pygame.quit()
        sys.exit(0)


def main():
    r = validate_project()
    if r["missing_seq"]:
        print(f"[FATAL] 序列缺失：{r['missing_seq']}")
        sys.exit(1)
    if r["missing_skill"]:
        print(f"[FATAL] 技能缺失：{r['missing_skill']}")
        sys.exit(1)
    if r.get("brick_exponents_error"):
        print(f"[FATAL] {r['brick_exponents_error']}")
        sys.exit(1)
    if any("重复" in e for e in r["errors"]):
        print(f"[FATAL] 校验错误：{r['errors']}")
        sys.exit(1)
    Game().run()


if __name__ == "__main__":
    main()