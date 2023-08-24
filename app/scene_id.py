

def generate_id(num: int, max_otc_digits: int = 6):
    print(len(str(num)))
    print(max_otc_digits - len(str(num)))
    zeros = [''] * (max_otc_digits + 1 - len(str(num)))
    return '0'.join(zeros) + str(num)
