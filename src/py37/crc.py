from dataclasses import dataclass


@dataclass
class CrcParameters:
    """the parameters of crc

    The meaning of the parameters could be find in https://blog.csdn.net/yl019283/article/details/88548451
    """
    name: str
    width: int
    poly: int
    starter: int
    refin: bool
    refout: bool
    xorout: int


class Crc:
    """Driving table method to implement crc

    Attributes:
        table: the precomputed list to save computing time
        p: the parameters that need in crc standard
    """

    def __init__(self, params):
        self.p = CrcParameters(**params)
        self.table = self._build_table()

    @staticmethod
    def reverse_integer(value, length):
        """reverse an integer with certain length

        Args:
            value: the integer to be reverse
            length: the length of the integer in binary

        Returns:
            the reversed integer
        """
        if 2 ** length < value:
            raise ValueError("incompatible between value and length!")

        result = 0
        for i in range(1, length+1):
            remainder = value % 2
            result += remainder * (2 ** (length-i))
            value = value // 2

        return result

    def _build_table(self):
        """build the table previously"""
        if self.p.refin:
            poly = self.reverse_integer(self.p.poly, length=self.p.width)
        else:
            poly = self.p.poly

        max_num = 2 ** self.p.width - 1
        left_shift = 2 ** (self.p.width-1)
        if self.p.refin:
            place = 0
        else:
            place = self.p.width - 8

        table = []
        for i in range(256):
            crc = i << place
            for j in range(8):
                if self.p.refin:
                    if crc & 0x1:
                        crc = (crc >> 1) ^ poly
                    else:
                        crc >>= 1
                else:
                    if crc & left_shift:
                        crc = (crc << 1) ^ poly
                    else:
                        crc <<= 1
            table.append(crc & max_num)

        return table

    def cal_ascii(self, text: str) -> int:
        """calculate the check value of text"""
        crc = self.p.starter

        if self.p.refin:
            right_shift = 0
        else:
            right_shift = self.p.width - 8
        max_num = 2 ** self.p.width - 1

        for word in text:
            t = ((crc >> right_shift) & 0xff) ^ ord(word)
            if self.p.refin:
                crc = crc >> 8
            else:
                crc = crc << 8
            crc = crc ^ self.table[t]
            crc &= max_num

        if self.p.refout ^ self.p.refin:
            crc = self.reverse_integer(crc, length=self.p.width)

        crc = crc ^ self.p.xorout

        return crc


if __name__ == '__main__':
    params = {
        "1": {
            "name": "crc32",
            "width": 32,
            "poly": 0x04c11db7,
            "starter": 0xffffffff,
            "refin": True,
            "refout": True,
            "xorout": 0xffffffff,
        },
        "2": {
            "name": "crc16",
            "width": 16,
            "poly": 0x1021,
            "starter": 0x0000,
            "refin": False,
            "refout": False,
            "xorout": 0x0000
        }
    }

    crc1 = Crc(params.get("1"))
    print(hex(crc1.cal_ascii("123456789")))
    crc2 = Crc(params.get("2"))
    print(hex(crc2.cal_ascii("123456789")))