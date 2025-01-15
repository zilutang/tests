-- 示例函数1：计算两个数的和
function add(a, b)
    return a + b
end

-- 示例函数2：计算一个数的平方
function square(number)
    return number * number
end

-- 示例函数3：打印数组的所有元素
function printArray(arr)
    for i = 1, #arr do
        print(arr[i])
    end
end

-- 主程序部分
local sum = add(10, 20)
print("Sum of 10 and 20: " .. sum)

local squared = square(5)
print("Square of 5: " .. squared)

local arr = {1, 2, 3, 4, 5}
print("Array elements:")
printArray(arr)
