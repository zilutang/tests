import ast
import os

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
        self.functions[node.name] = node.lineno
        self.generic_visit(node)

def get_function_calls(file_path, target_function_name):
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

def scan_directory_for_functions(directory_path, target_function_name):
    # 用于存储所有文件的结果
    all_results = {}

    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # 仅处理 Python 文件
            if file.endswith('.py'):
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
    target_function = "create_vsdx"  # 替换为目标函数名
    results = scan_directory_for_functions(directory_path, target_function)

    print(f"Functions called by {target_function} and their definitions across all files:")
    for file, function_calls in results.items():
        print(f"In file {file}:")
        for called_func, line_num in function_calls.items():
            print(f"  {called_func} is defined at line {line_num}")