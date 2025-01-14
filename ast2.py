import ast
import os
import javalang
import re

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        # 记录函数调用的位置
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        self.generic_visit(node)

class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}

    def visit_FunctionDef(self, node):
        # 记录函数定义的位置（行号）
        start_lineno = node.lineno
        end_lineno = node.body[-1].lineno if node.body else start_lineno
        self.functions[node.name] = (start_lineno, end_lineno)
        self.generic_visit(node)

def get_function_calls(file_path, target_function_name):
    if file_path.endswith('.py'):
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=file_path)

        # 1. 先找到所有函数的定义位置
        function_def_visitor = FunctionDefVisitor()
        function_def_visitor.visit(tree)

        # 2. 找到目标函数中的函数调用
        function_call_visitor = FunctionCallVisitor()
        function_call_visitor.visit(tree)

        # 3. 输出目标函数中调用的函数及其定义位置
        calls = function_call_visitor.calls
        function_definitions = function_def_visitor.functions

        result = {}
        for call in calls:
            if target_function_name in function_definitions:
                if call == target_function_name:
                    result[call] = function_definitions[call]

        return result
    elif file_path.endswith('.java'):
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = javalang.parse.parse(file.read())

        function_definitions = {}
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            if node.name == target_function_name:
                start_lineno = node.position.line
                end_lineno = node.body[-1].position.line if node.body else start_lineno
                function_definitions[node.name] = (start_lineno, end_lineno)

        # 确保返回一个字典，即使没有找到目标函数
        return {target_function_name: function_definitions.get(target_function_name, None)}
    elif file_path.endswith('.cs'):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 使用正则表达式查找C#方法定义
        pattern = re.compile(r'\b(?:public|private|protected|internal|static|virtual|override|abstract|async|sealed|extern|unsafe|new|partial|ref|readonly|volatile|void|int|float|double|string|bool|char|byte|short|long|decimal|object|dynamic|var)\s+\b' + re.escape(target_function_name) + r'\b\s*\(.*?\)\s*{', re.MULTILINE)
        matches = pattern.finditer(content)

        function_definitions = {}
        for match in matches:
            start_lineno = content.count('\n', 0, match.start()) + 1
            # 简单假设方法体在同一行结束
            end_lineno = start_lineno
            function_definitions[target_function_name] = (start_lineno, end_lineno)

        return {target_function_name: function_definitions.get(target_function_name)}

def scan_directory_for_functions(directory_path, target_function_name):
    # 用于存储所有文件的结果
    all_results = {}

    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # 处理 Python, Java 和 C# 文件
            if file.endswith('.py') or file.endswith('.java') or file.endswith('.cs'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                # 获取当前文件中目标函数调用的函数定义位置
                function_calls = get_function_calls(file_path, target_function_name)
                if function_calls:
                    all_results[file_path] = function_calls

    return all_results

# Example usage:
if __name__ == "__main__":
    directory_path = "./"  # 替换为你的目录路径
    target_function = "count"  # 替换为目标函数名
    results = scan_directory_for_functions(directory_path, target_function)

    print(f"Functions called by {target_function} and their definitions across all files:")
    for file, function_calls in results.items():
        for called_func, definition in function_calls.items():
            if definition is not None:
                print(f"In file {file}:")
                start_line, end_line = definition
                print(f"  {called_func} is defined from line {start_line} to line {end_line}")

