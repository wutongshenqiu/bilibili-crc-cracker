import numpy as np
from typing import List
import time
import functools
import colorama

colorama.init(autoreset=True)


def get_binary(num, length=8) -> List:
    """get the binary of a integer with a certain length

    Returns:
        the list of the binary
    """
    if num >= 2**length:
        raise ValueError("the number is too big")
    bin_list = [0 for i in range(length)]

    i = length - 1
    while num > 0:
        bin_list[i] = num % 2
        num //= 2
        i -= 1

    return bin_list


def ascii_to_bin(text: str) -> np.ndarray:
    """get the binary form of the str(can be denoted by ascii)

    Args:
        text: the strings

    Return:
        the binary form of original data denoted by numpy
    """
    asciis = []
    for word in text:
        asciis.append(get_binary(ord(word)))

    return np.hstack(asciis)


def clock(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        begin = time.strftime("%Y-%m-%d %H:%M:%S")
        begin_time = time.time()
        print("=" * 100)
        print(
            f"{colorama.Fore.GREEN}function {colorama.Fore.RED}{func.__name__} {colorama.Fore.GREEN}starts at {begin}")
        result = func(*args, **kwargs)
        end = time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = time.time()
        print(f"{colorama.Fore.GREEN}function {colorama.Fore.RED}{func.__name__} {colorama.Fore.GREEN}ends at {end}")
        print(f"{colorama.Fore.BLUE}function {colorama.Fore.RED}{func.__name__} {colorama.Fore.BLUE}runs "
              f"last {end_time - begin_time:.2f} seconds")
        print("=" * 100)
        return result

    return wrapper


def tab_to_space(path, new_path, space=4):
    f_old = open(path, "r", encoding="utf8")
    f_new = open(new_path, "w", encoding="utf8")
    for line in f_old:
        for word in line:
            if word == "\t":
                f_new.write(" " * space)
            else:
                f_new.write(word)
    f_new.close()
    f_old.close()


if __name__ == '__main__':
    tab_to_space(r"swig-learn/Crc32Engine.h", r"swig-learn/Crc32Engine_reformat.h")