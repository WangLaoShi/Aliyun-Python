"""第一章综合示例。仅依赖标准库；输出路径以本文件所在目录为基准。"""
import csv
import json
import math
from pathlib import Path


RAW_STUDENTS = [
    {"name": "小林", "score": "85"},
    {"name": "小陈", "score": 58},
    {"name": "小周", "score": 92},
    {"name": "小吴", "score": 60},
    {"name": "小许", "score": "缺考"},
    {"name": "小郑", "score": 101},
]


def validate_students(records):
    """约定 records 是由字典组成的列表；逐条返回有效数据与无效原因。"""
    valid = []
    invalid = []
    for row_number, record in enumerate(records, start=1):
        try:
            name = record.get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError("姓名必须为非空字符串")
            raw_score = record.get("score")
            if isinstance(raw_score, bool):
                raise ValueError("布尔值不能作为分数")
            score = float(raw_score)
            if not math.isfinite(score) or not 0 <= score <= 100:
                raise ValueError("分数必须是 0～100 之间的有限数")
        except (TypeError, ValueError) as error:
            invalid.append({
                "row": row_number,
                "name": record.get("name"),
                "raw_score": record.get("score"),
                "reason": str(error),
            })
        else:
            valid.append({"name": name.strip(), "score": score})
    return valid, invalid


def summarize(students):
    """输入已校验记录；及格率返回 0～1 小数，空数据返回 None。"""
    scores = [student["score"] for student in students]
    count = len(scores)
    passed = sum(score >= 60 for score in scores)
    return {
        "valid_count": count,
        "passed_count": passed,
        "average": sum(scores) / count if count else None,
        "pass_rate": passed / count if count else None,
    }


def save_report(summary, invalid, folder):
    folder.mkdir(parents=True, exist_ok=True)
    report_path = folder / "summary.json"
    report_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    with (folder / "invalid_records.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=["row", "name", "raw_score", "reason"])
        writer.writeheader()
        writer.writerows(invalid)
    return report_path


def main():
    valid, invalid = validate_students(RAW_STUDENTS)
    summary = summarize(valid)
    summary["total_count"] = len(RAW_STUDENTS)
    summary["invalid_count"] = len(invalid)
    # 小样本的人工预期：85 + 58 + 92 + 60 = 295，平均分 73.75。
    assert summary["valid_count"] == 4
    assert summary["invalid_count"] == 2
    assert summary["passed_count"] == 3
    assert math.isclose(summary["average"], 73.75)
    assert math.isclose(summary["pass_rate"], 0.75)
    assert summary["total_count"] == summary["valid_count"] + summary["invalid_count"]
    assert summarize([])["average"] is None
    output = Path(__file__).resolve().parent.parent / "output"
    report_path = save_report(summary, invalid, output)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"报告已保存：{report_path}")


if __name__ == "__main__":
    main()
