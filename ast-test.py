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

        # 提取函数的内容
        function_content = ast.unparse(node) if hasattr(ast, 'unparse') else compile(ast.Expression(node), '', 'exec')

        # 保存函数的定义位置和内容
        self.functions[node.name] = {
            'start_lineno': start_lineno,
            'end_lineno': end_lineno,
            'content': function_content
        }
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
            lines = file.readlines()

        tree = javalang.parse.parse(''.join(lines))

        function_definitions = {}
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            if node.name == target_function_name:
                start_lineno = node.position.line
                end_lineno = node.body[-1].position.line if node.body else start_lineno

                # 获取从start_lineno到end_lineno的文件内容
                method_content = ''.join(lines[start_lineno - 1:end_lineno]) if node.body else ""

                function_definitions[node.name] = {
                    'start_lineno': start_lineno,
                    'end_lineno': end_lineno,
                    'content': method_content
                }

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
            # 查找方法体结束的行号
            brace_count = 1
            end_pos = match.end()
            while brace_count > 0 and end_pos < len(content):
                if content[end_pos] == '{':
                    brace_count += 1
                elif content[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1
            end_lineno = content.count('\n', 0, end_pos) + 1
            function_content = content[match.start():end_pos]
            function_definitions[target_function_name] = {
                'start_lineno': start_lineno,
                'end_lineno': end_lineno,
                'content': function_content
            }

        return {target_function_name: function_definitions.get(target_function_name)}
    elif file_path.endswith('.cpp'):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 使用正则表达式查找C++函数定义
        pattern = re.compile(r'\b(?:void|int|float|double|string|bool|char|byte|short|long|unsigned|signed|const|static|inline|virtual|template|typename|class|struct)\s+\b' + re.escape(target_function_name) + r'\b\s*\(.*?\)\s*{', re.MULTILINE)
        matches = pattern.finditer(content)

        function_definitions = {}
        for match in matches:
            start_lineno = content.count('\n', 0, match.start()) + 1
            # 查找方法体结束的行号
            brace_count = 1
            end_pos = match.end()
            while brace_count > 0 and end_pos < len(content):
                if content[end_pos] == '{':
                    brace_count += 1
                elif content[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1
            end_lineno = content.count('\n', 0, end_pos) + 1
            function_content = content[match.start():end_pos]
            function_definitions[target_function_name] = {
                'start_lineno': start_lineno,
                'end_lineno': end_lineno,
                'content': function_content
            }

        return {target_function_name: function_definitions.get(target_function_name)}
    elif file_path.endswith('.lua'):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 使用正则表达式查找Lua函数定义
        pattern = re.compile(r'\bfunction\s+' + re.escape(target_function_name) + r'\b\s*\(.*?\)', re.MULTILINE)
        matches = pattern.finditer(content)

        function_definitions = {}
        for match in matches:
            start_lineno = content.count('\n', 0, match.start()) + 1
            # 查找函数体的结束行
            end_pos = match.end()
            while end_pos < len(content) and content[end_pos:end_pos+3] != 'end':
                end_pos += 1
            end_pos += 3  # 跳过'end'
            end_lineno = content.count('\n', 0, end_pos) + 1
            function_content = content[match.start():end_pos]
            function_definitions[target_function_name] = {
                'start_lineno': start_lineno,
                'end_lineno': end_lineno,
                'content': function_content
            }

        return {target_function_name: function_definitions.get(target_function_name)}

def scan_directory_for_functions(directory_path, target_function_name):
    # 用于存储所有文件的结果
    all_results = {}

    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # 处理 Python, Java, C#, C++ 和 Lua 文件
            if file.endswith('.py') or file.endswith('.java') or file.endswith('.cs') or file.endswith('.cpp') or file.endswith('.lua'):
                file_path = os.path.join(root, file)

                # 获取当前文件中目标函数调用的函数定义位置
                function_calls = get_function_calls(file_path, target_function_name)
                if function_calls:
                    all_results[file_path] = function_calls

    return all_results

def print_function_calls(directory_path, target_function):
    results = scan_directory_for_functions(directory_path, target_function)
    print(f"Functions called by {target_function} and their definitions across all files:")
    for file, function_calls in results.items():
        for called_func, definition in function_calls.items():
            if definition is not None:
                start_line, end_line, content = definition['start_lineno'], definition['end_lineno'], definition['content']
                print(f"In file {file}:")
                print(f"  {called_func} is defined from line {start_line} to line {end_line}")
                print(f"  Function content:\n{content}\n")

# Example usage:
if __name__ == "__main__":
    directory_path = "./"  # 替换为你的目录路径

    target_functions = ["execute", "create_vsdx", "LoadOrbitalElements", "squareRoot", "printArray"]
    for target_function in target_functions:
        print_function_calls(directory_path, target_function)
