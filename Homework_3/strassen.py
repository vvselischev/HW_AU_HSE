import numpy as np
from math import log

def _strassen(first, second):
    matrix_len = len(first)
    if matrix_len == 1:
        return np.full((1, 1), first[0][0] * second[0][0])

    new_len = matrix_len // 2
    a = _split_matrix(first, new_len)
    b = _split_matrix(second, new_len)

    p_1 = _strassen(a[0, 0] + a[1, 1], b[0, 0] + b[1, 1])
    p_2 = _strassen(a[1, 0] + a[1, 1], b[0, 0])
    p_3 = _strassen(a[0, 0], b[0, 1] - b[1, 1])
    p_4 = _strassen(a[1, 1], b[1, 0] - b[0, 0])
    p_5 = _strassen(a[0, 0] + a[0, 1], b[1, 1])
    p_6 = _strassen(a[1, 0] - a[0, 0], b[0, 0] + b[0, 1])
    p_7 = _strassen(a[0, 1] - a[1, 1], b[1, 0] + b[1, 1])

    result = _combine_matrix(p_1 + p_4 - p_5 + p_7, p_3 + p_5,
                             p_2 + p_4, p_1 - p_2 + p_3 + p_6)
    return result

def _combine_matrix(left_top, right_top, left_bottom, right_bottom):
    result = np.hstack((left_top, right_top))
    result = np.vstack((result, np.hstack((left_bottom, right_bottom))))
    return result

def _split_matrix(matrix, part_len):
    result = _combine_matrix([[matrix[:part_len, :part_len]]],
                             [[matrix[:part_len, part_len:]]],
                             [[matrix[part_len:, :part_len]]],
                             [[matrix[part_len:, part_len:]]])
    return result

def _is_pow2(x):
    log2 = log(x, 2)
    return log2 == int(log2)

def _get_new_len(old_len):
    new_len = old_len
    while not _is_pow2(new_len):
        new_len += 1
    return new_len

def _prepare_matrix(matrix, old_len, new_len):
    delta_len = new_len - old_len
    matrix = np.hstack([matrix, np.zeros((old_len, delta_len))])
    matrix = np.vstack([matrix, np.zeros((delta_len, new_len))])
    return matrix

def strassen_algorithm(first, second):
    old_len = len(first)
    new_len = _get_new_len(old_len)
    
    first_prepared = _prepare_matrix(first, old_len, new_len)
    second_prepared = _prepare_matrix(second, old_len, new_len)

    result_strassen = _strassen(first_prepared, second_prepared)
    result = result_strassen[:old_len, :old_len]
    return result

def _read_matrix(matrix_len):
    matrix = np.empty((matrix_len, matrix_len))
    for row in range(matrix_len):
        row_values = input().split()
        matrix[row] = [int(value) for value in row_values]
    return matrix

def _print_matrix(matrix):
    matrix_len = len(matrix)
    for row in range(matrix_len):
        print(" ".join(map(str, map(int, matrix[row]))))

def main():
    matrix_len = int(input())
    first = _read_matrix(matrix_len)
    second = _read_matrix(matrix_len)
    result = strassen_algorithm(first, second)
    _print_matrix(result)
    
if __name__ == '__main__':
    main()
