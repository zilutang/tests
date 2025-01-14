#include <iostream>
#include <cmath>

// 示例函数1：计算两个数的和
int add(int a, int b) {
    return a + b;
}

// 示例函数2：计算一个数的平方根
double squareRoot(double number) {
    if (number < 0) {
        std::cerr << "Error: Negative input for square root." << std::endl;
        return -1;
    }
    return std::sqrt(number);
}

// 示例函数3：打印一个数组的内容
void printArray(int arr[], int size) {
    for (int i = 0; i < size; ++i) {
        std::cout << arr[i] << " ";
    }
    std::cout << std::endl;
}

int main() {
    // 使用示例函数1：加法
    int sum = add(5, 10);
    std::cout << "Sum of 5 and 10: " << sum << std::endl;

    // 使用示例函数2：平方根
    double result = squareRoot(16.0);
    if (result != -1) {
        std::cout << "Square root of 16: " << result << std::endl;
    }

    // 使用示例函数3：打印数组
    int arr[] = {1, 2, 3, 4, 5};
    int size = sizeof(arr) / sizeof(arr[0]);
    std::cout << "Array elements: ";
    printArray(arr, size);

    return 0;
}
