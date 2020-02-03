import numpy as np

CRC32_POLY = 0xedb88320


class Crc32Engine:

    def __init__(self):
        self.crc32_table = np.array(Crc32Engine.init_table(), np.uint32)
        self.rainbow_table_hash = np.zeros(100000, np.uint32)
        self.rainbow_table_value = np.zeros(100000, np.uint32)

        full_hash_cache = np.zeros(100000, np.uint32)
        short_hash_buckets = np.zeros(65537, np.uint32)

        for i in range(100000):
            crc_hash = self.compute(str(i))
            full_hash_cache[i] = crc_hash
            short_hash_buckets[crc_hash >> 16] += 1

        self.short_hash_bucket_starts = np.cumsum(short_hash_buckets)
        for i in range(100000):
            index = full_hash_cache[i] >> 16
            self.short_hash_bucket_starts[index] -= 1
            idx = self.short_hash_bucket_starts[index]
            self.rainbow_table_hash[idx] = full_hash_cache[i]
            self.rainbow_table_value[idx] = i

    @staticmethod
    def init_table():
        table = []
        for i in range(256):
            crc = i
            for j in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ CRC32_POLY
                else:
                    crc >>= 1
            table.append(crc & 0xffffffff)

        return table

    def compute(self, words: str, add_padding=False):
        crc = 0
        for word in words:
            crc = self.crc32_update(crc, int(word))

        if add_padding:
            for i in range(5):
                crc = self.crc32_update(crc, 0)

        return crc

    def crc32_update(self, crc, code):
        return (crc >> 8) ^ self.crc32_table[(crc ^ code) & 0xff]

    # TODO
    # add crackers in dict
    def crack(self, crc_hash_str: str):
        candidates = []
        base_hash = 0xffffffff
        crc_hash = int(crc_hash_str, base=16) ^ base_hash

        for i in range(1, 10):
            base_hash = self.crc32_update(base_hash, 0x30)
            if i < 6:
                candidates.extend(self.lookup(crc_hash ^ base_hash))
            else:
                start_prefix = 10 ** (i - 6)
                end_prefix = 10 ** (i - 5)

                for prefix in range(start_prefix, end_prefix):
                    for postfix in self.lookup(crc_hash ^ base_hash ^ self.compute(str(prefix), True)):
                        candidates.append(prefix * 100000 + postfix)

        return candidates

    def lookup(self, crc_hash):
        candidates = []
        short_hash = crc_hash >> 16
        for i in range(self.short_hash_bucket_starts[short_hash], self.short_hash_bucket_starts[short_hash+1]):
            if self.rainbow_table_hash[i] == crc_hash:
                candidates.append(self.rainbow_table_value[i])

        return candidates


if __name__ == '__main__':
    crc_cracker = Crc32Engine()
    print(crc_cracker.crack("11"))
