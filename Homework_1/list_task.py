# Remove equal adjacent elements
#
# Example input: [1, 2, 2, 3]
# Example output: [1, 2, 3]
def remove_adjacent(src_list):
    if len(src_list) == 0:
        return src_list
    dest_list = [src_list[0]]
    for i in range(1, len(src_list)):
        if src_list[i] != src_list[i - 1]:
            dest_list.append(src_list[i])
    return dest_list


# Merge two sorted lists in one sorted list in linear time
#
# Example input: [2, 4, 6], [1, 3, 5]
# Example output: [1, 2, 3, 4, 5, 6]
def linear_merge(list1, list2):
    first_ind = 0
    second_ind = 0
    first_len = len(list1)
    second_len = len(list2)
    merged = []
    while first_ind < first_len or second_ind < second_len:
        if first_ind >= first_len:
            merged.append(list2[second_ind])
            second_ind += 1
        elif second_ind >= second_len:
            merged.append(list1[first_ind])
            first_ind += 1
        elif list1[first_ind] < list2[second_ind]:
            merged.append(list1[first_ind])
            first_ind += 1
        else:
            merged.append(list2[second_ind])
            second_ind += 1
    return merged
