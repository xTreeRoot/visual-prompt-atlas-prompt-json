"""命令行入口与参数定义。"""

from __future__ import annotations

import argparse
import sys

from .compose import command_compose
from .constants import LIBRARIES
from .errors import AtlasCliError
from .maintenance import command_ids_backfill, command_ids_next, command_ingest
from .search import command_search, command_stats
from .validation import command_validate


class ChineseArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        return super().format_help().replace("usage:", "用法:", 1)

    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "用法:", 1)

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: 错误: {localize_argparse_error(message)}\n")


def localize_argparse_error(message: str) -> str:
    replacements = {
        "the following arguments are required:": "缺少必需参数:",
        "unrecognized arguments:": "无法识别的参数:",
        "invalid choice:": "无效取值:",
        "expected one argument": "需要一个参数",
        "choose from": "可选值",
        "argument": "参数",
    }
    for source, target in replacements.items():
        message = message.replace(source, target)
    return message


def localize_argparse(parser: argparse.ArgumentParser) -> None:
    parser._positionals.title = "位置参数"
    parser._optionals.title = "选项"
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            action.help = "显示帮助信息并退出"
        if isinstance(action, argparse._SubParsersAction):
            action.title = "子命令"
            for subparser in action.choices.values():
                localize_argparse(subparser)


def build_parser() -> argparse.ArgumentParser:
    parser = ChineseArgumentParser(description="视觉提示词图谱数据集工具")
    subparsers = parser.add_subparsers(dest="command", required=True, parser_class=ChineseArgumentParser)

    stats = subparsers.add_parser("stats", help="统计数据规模和高频标签")
    stats.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    stats.set_defaults(func=command_stats)

    validate = subparsers.add_parser("validate", help="校验必需文件和数据结构")
    validate.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    validate.set_defaults(func=command_validate)

    search = subparsers.add_parser("search", help="搜索提示词条目")
    search.add_argument("library", choices=["all", *LIBRARIES.keys()])
    search.add_argument("query", nargs="?", help="搜索文本")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--mood")
    search.add_argument("--min-mood", type=int, default=1, help="情绪最低分")
    search.add_argument("--category", help="场景分类筛选")
    search.add_argument("--occasion", help="服装适用场合筛选")
    search.add_argument("--pose-type", help="动作 pose.type 筛选，例如 站 或 坐")
    search.add_argument("--interaction-min", type=int, help="动作 interaction.level 最低值")
    search.add_argument("--dynamic-max", type=int, help="动作 dynamic.intensity 最高值")
    search.add_argument("--full", action="store_true", help="JSON 输出中包含完整源条目")
    search.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    search.set_defaults(func=command_search)

    ids = subparsers.add_parser("ids", help="生成或回填稳定条目 id")
    ids_subparsers = ids.add_subparsers(dest="ids_command", required=True, parser_class=ChineseArgumentParser)

    ids_backfill = ids_subparsers.add_parser("backfill", help="为缺少 id 的条目回填稳定 id")
    ids_backfill.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    ids_backfill.add_argument("--write", action="store_true", help="写入 id 回填结果")
    ids_backfill.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    ids_backfill.set_defaults(func=command_ids_backfill)

    ids_next = ids_subparsers.add_parser("next", help="预览某个库后续可用的稳定 id")
    ids_next.add_argument("library", choices=list(LIBRARIES))
    ids_next.add_argument("--count", type=int, default=1)
    ids_next.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    ids_next.set_defaults(func=command_ids_next)

    ingest = subparsers.add_parser("ingest", help="校验并追加新条目，同时自动分配稳定 id")
    ingest.add_argument("library", choices=list(LIBRARIES))
    ingest.add_argument("input", help="待入库 JSON 文件，可为对象、数组或带顶层库 key 的对象")
    ingest.add_argument("--dry-run", action="store_true", help="只预览入库结果，不写入")
    ingest.add_argument("--write", action="store_true", help="将通过校验的条目追加到目标库")
    ingest.add_argument(
        "--allow-duplicate-description",
        action="store_true",
        help="允许入库时出现完全相同的 description",
    )
    ingest.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    ingest.set_defaults(func=command_ingest)

    compose = subparsers.add_parser("compose", help="从图谱组合真实感图像提示词")
    compose.add_argument("--mood", help="偏好的情绪标签，例如 温柔、甜美、清纯")
    compose.add_argument("--min-mood", type=int, default=3, help="使用 --mood 时的最低情绪分")
    compose.add_argument("--scene-name", action="append", help="场景名或文本筛选，可重复")
    compose.add_argument("--scene-category", help="场景分类筛选")
    compose.add_argument("--occasion", help="服装适用场合筛选")
    compose.add_argument("--pose-type", help="动作 pose.type 筛选")
    compose.add_argument("--interaction-min", type=int, help="动作 interaction.level 最低值")
    compose.add_argument("--dynamic-max", type=int, help="动作 dynamic.intensity 最高值")
    compose.add_argument("--scene-index", type=int, help="使用指定 scenes index")
    compose.add_argument("--outfit-index", type=int, help="使用指定 outfits index")
    compose.add_argument("--action-index", type=int, help="使用指定 actions index")
    compose.add_argument("--expression-index", type=int, help="使用指定 expressions index")
    compose.add_argument("--scene-id", help="使用指定 scenes id")
    compose.add_argument("--outfit-id", help="使用指定 outfits id")
    compose.add_argument("--action-id", help="使用指定 actions id")
    compose.add_argument("--expression-id", help="使用指定 expressions id")
    compose.add_argument("--identity-slot", help="读取本地身份槽 id，并把身份描述加入生成提示词")
    compose.add_argument(
        "--strict-compatible",
        action="store_true",
        help="要求场景和服装得到正向兼容匹配",
    )
    compose.add_argument("--count", type=int, default=1)
    compose.add_argument("--seed", type=int, default=7)
    compose.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    compose.set_defaults(func=command_compose)

    localize_argparse(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except AtlasCliError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2
