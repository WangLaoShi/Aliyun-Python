try:
    from ..funs import average, intercept, vlookup, combine
except ImportError:  # 用 python 某脚本.py 直接运行时没有父包，相对导入会失败
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from funs import average, intercept, vlookup, combine

print(average([1, 2, 3, 4, 5]))
print(intercept("1234567890", 3, "-"))
print(vlookup("1234567890", [["1234567890", "1234567890"], ["1234567890", "1234567890"]]))
print(combine(["1234567890", "1234567890"], ["1234567890", "1234567890"]))