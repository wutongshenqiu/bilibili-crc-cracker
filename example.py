import time
import random

from src.py37 import cracker
from Crc32Engine import Crc32Engine


def generate_case():
    characters = "0123456789abcdef"
    length = random.randint(1, 8)

    return "".join(random.sample(characters, length))


if __name__ == '__main__':
    cpp_crc32 = Crc32Engine()
    py_crc32 = cracker.Crc32Engine()

    test_cases = []
    for i in range(100):
        test_cases.append(generate_case())

    first_py = time.time()
    print("python cracker starts")
    py_ans = list(map(py_crc32.crack, test_cases))
    end_py = time.time()
    print(f"python cracker ends, using {end_py-first_py:.2f}s")

    first_cpp = time.time()
    print("cpp cracker starts")
    cpp_ans = list(map(cpp_crc32.crack, test_cases))
    end_cpp = time.time()
    print(f"cpp cracker ends, using {end_cpp-first_cpp:.2f}s")

    # test accuracy
    assert all(py_ans[i] == cpp_ans[i] for i in range(100))

