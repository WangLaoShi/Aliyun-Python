clearinfo_doc = """
Convert Markdown to IPython Notebook (M2I) (.md -> .ipynb)
Author: ShizuriYuki
Version: 0.1
Created at: 2023-10-21 17:45
Last modified at: 2023-10-21 17:45

Github: https://github.com/ShizuriYuki/markdown_to_ipynb
License: GPL-3.0 License

Usage:
    python markdown_to_ipynb.py <markdown_file_or_folder> [-o <ipynb_file>]

    <markdown_file_or_folder>       Input Markdown file or folder
    -o, --output                    Output IPython Notebook file or folder (default: <markdown_file_or_folder>)
    -y, --yes                       Do not ask for confirmation (default: False)
    -v, --version                   Show version
    -h, --help                      Show help
    
Example:
    python markdown_to_ipynb.py test.md
    python markdown_to_ipynb.py test.md -o test.ipynb
    python markdown_to_ipynb.py test.md --output test.ipynb
    python markdown_to_ipynb.py ./markdown/
    python markdown_to_ipynb.py ./ -o ./ipynb/ -y
"""

__version__ = "0.1"

import nbformat
from nbformat import v4
import re
import argparse
import os


def markdown_to_ipynb(markdown_file, ipynb_file):
    with open(markdown_file, "r", encoding="utf-8") as md_file:
        markdown_content = md_file.read()

    cells = []
    code_block_pattern = re.compile(r"```(?:\s*\w+)?\s*\n(.*?)\n```", re.DOTALL)

    # Split content by code blocks
    parts = code_block_pattern.split(markdown_content)

    for i in range(0, len(parts), 2):
        # Text content
        text_content = parts[i].strip()
        if text_content:
            cells.append(v4.new_markdown_cell(text_content))

        # Code content
        if i + 1 < len(parts):
            code_content = parts[i + 1]
            code_lines = code_content.split("\n")
            # Remove leading empty lines
            while code_lines and not code_lines[0].strip():
                code_lines.pop(0)
            # Remove trailing empty lines
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()
            cells.append(v4.new_code_cell("\n".join(code_lines)))

    nb = v4.new_notebook(cells=cells, metadata={"language_info": {"name": "python"}})

    with open(ipynb_file, "w", encoding="utf-8") as ipynb:
        nbformat.write(nb, ipynb)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to IPython Notebook (.ipynb)"
    )
    parser.add_argument("input", help="Input Markdown file or folder", type=str)
    parser.add_argument(
        "-o", "--output", help="Output IPython Notebook file or folder", type=str
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="Convert Markdown to IPython Notebook (M2I)  |  Version: " + __version__,
        help="Show version",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not ask for confirmation",
        default=False,
    )
    parser.add_argument("-u", "--usage", action="store_true", help="Show usage", default=False, dest="usage")
    
    args = parser.parse_args()
    
    if args.usage:
        print(info_doc)
        return

    """ Chinese version of the comments
    1. 先检查 input 是否存在, 不存在则报错并退出
    2. 检查 input 是文件还是文件夹:
        - 如果是文件, 则检查文件后缀名是否为 .md, 如果不是则报错并退出
        - 如果是文件夹, 则检查文件夹内是否有 .md 文件, 如果没有则报错并退出
    3. 检查 output 是否为 None
        - 如果是 None, 则：
            - 如果 input 是文件, 则 output = input 的文件名
            - 如果 input 是文件夹, 则 output = input
        - 如果不是 None, 则：
            1. 检查 output 是否存在
                - 如果 output 不存在，则检查它是否有后缀
                    - 如果没有后缀，则认为它是一个文件夹
                    - 如果有后缀，则认为它是一个文件
                - 如果 output 存在，则检查它是文件还是文件夹, 根据不同的情况进行处理
            2. 根据 output 的类型进行处理：
                - 如果 output 是文件：
                    - input 是文件：则检查 output 的后缀名是否为 .ipynb, 如果不是则警告文件后缀名不是 .ipynb, 询问是否继续
                    - input 是文件夹：报错并退出
                - 如果 output 是文件夹, 则检查 output 是否存在, 不存在则询问是否创建
    4. 情况分析：
        1. input 是文件, output 是文件
            运行一次 markdown_to_ipynb
        2. input 是文件, output 是文件夹
            运行一次 markdown_to_ipynb
        3. input 是文件夹, output 是文件夹
            遍历 input 文件夹内的所有 .md 文件, 运行 markdown_to_ipynb
    """
    """ English version of the comments
    1. First, check if the input exists. If it doesn't, raise an error and exit.
    2. Check whether the input is a file or a folder:
        - If it's a file, check if the file extension is .md. If not, raise an error and exit.
        - If it's a folder, check if there are .md files inside. If not, raise an error and exit.
    3. Check if the output is None:
        - If it's None:
            - If the input is a file, set output to the input file name.
            - If the input is a folder, set output to the input folder.
        - If it's not None:
            1. Check if the output exists:
                - If the output doesn't exist, check if it has an extension:
                    - If it doesn't have an extension, consider it a folder.
                    - If it has an extension, consider it a file.
                - If the output exists, check if it's a file or a folder and handle accordingly.
            2. Process based on the type of output:
                - If the output is a file:
                    - If the input is a file, check if the output file extension is .ipynb. If not, warn that the file extension is not .ipynb and ask whether to continue.
                    - If the input is a folder, raise an error and exit.
                - If the output is a folder, check if it exists. If it doesn't, ask whether to create it.
    4. Scenarios:
        1. Input is a file, output is a file.
            Run markdown_to_ipynb once.
        2. Input is a file, output is a folder.
            Run markdown_to_ipynb once.
        3. Input is a folder, output is a folder.
            Traverse all .md files in the input folder and run markdown_to_ipynb.
    """
    # Check the input file or folder exists
    if not os.path.exists(args.input):
        print("Error: Input file or folder does not exist!")
        return

    # Check the input is a file or a folder
    input_type = "file"
    if os.path.isdir(args.input):
        input_type = "folder"
        # Check the folder has .md files
        md_files = []
        for file in os.listdir(args.input):
            if os.path.splitext(file)[1] == ".md":
                md_files.append(file)
        if len(md_files) == 0:
            print("Error: Input folder does not have .md files!")
            return
    else:
        # Check the file's extension name is .md
        if os.path.splitext(args.input)[1] != ".md":
            print("Error: Input file's extension name is not .md!")
            return

    # Check the output is None
    if args.output is None:
        if input_type == "file":
            output_type = "file"
            args.output = os.path.splitext(args.input)[0] + ".ipynb"
        else:
            output_type = "folder"
            args.output = args.input
    else:
        # Check the output is a file or a folder
        output_type = "file"
        if not os.path.exists(args.output):
            if os.path.splitext(args.output)[1] == "":
                output_type = "folder"
            else:
                output_type = "file"
        else:
            if os.path.isdir(args.output):
                output_type = "folder"
            else:
                output_type = "file"

        # According to the output type, check the output
        if output_type == "file":
            # Check the input is a file
            if input_type == "file":
                # Check the output's extension name is .ipynb
                if os.path.splitext(args.output)[1] != ".ipynb":
                    print(
                        f"Warning: The extension name of uutput file {args.output} is not .ipynb!"
                    )
                    print("Do you want to continue? (y/n)")
                    if not args.yes:
                        answer = input()
                        if answer.lower() != "y":
                            return
                    else:
                        print("y")
            else:
                print("Error: Output is a file, but input is a folder!")
                return
        else:
            # Check the output folder exists
            if not os.path.exists(args.output):
                print("Warning: Output folder does not exist!")
                print("Do you want to create it? (y/n)")
                if not args.yes:
                    answer = input()
                    if answer.lower() != "y":
                        return
                else:
                    print("y")
                os.makedirs(args.output)

    # Convert markdown to ipynb
    if input_type == "file" and output_type == "file":
        markdown_to_ipynb(args.input, args.output)
    elif input_type == "file" and output_type == "folder":
        markdown_to_ipynb(
            args.input,
            os.path.join(
                args.output, os.path.basename(args.input).replace(".md", ".ipynb")
            ),
        )
    elif input_type == "folder" and output_type == "folder":
        for idx, file in enumerate(md_files):
            # print the file info: Converting: file_name
            # print the progress
            print(f"Converted {idx} / {len(md_files)} files  |  Converting: {file}.")
            markdown_to_ipynb(
                os.path.join(args.input, file),
                os.path.join(args.output, file.replace(".md", ".ipynb")),
            )
            if idx == len(md_files) - 1:
                print(f"Converted {idx + 1} / {len(md_files)} files")
    else:
        print("Error: Unknown error!")
        return
    print("Done!")


if __name__ == "__main__":
    main()
