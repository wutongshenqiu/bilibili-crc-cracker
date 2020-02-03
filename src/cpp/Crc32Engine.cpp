#include "../../pybind11/include/pybind11/pybind11.h"
#include "../../pybind11/include/pybind11/stl.h"

namespace py = pybind11;


class Crc32Engine {
public:
	Crc32Engine(uint32_t poly = 0xedb88320) {
		init_table(poly);
		for (int i = 0; i < 100000; i++) {
			uint32_t crc_hash = compute(i);
			full_hash_cache[i] = crc_hash;
			short_hash_buckets[crc_hash >> 16]++;
		}
		cumsum(short_hash_buckets, short_hash_bucket_starts, 65537);

		for (int i = 0; i < 100000; i++) {
			uint32_t idx = --short_hash_bucket_starts[full_hash_cache[i] >> 16];
			rainbow_table_hash[idx] = full_hash_cache[i];
			rainbow_table_value[idx] = i;
		}
	}

	~Crc32Engine() {
		delete crc32_table;
		delete rainbow_table_hash;
		delete rainbow_table_value;
		delete full_hash_cache;
		delete short_hash_buckets;
		delete short_hash_bucket_starts;
	}
	std::vector<uint32_t> crack(std::string hash) {
		std::vector<uint32_t> candidates;
		uint32_t base_hash = 0xffffffff;

		uint32_t crc_hash = ascii_to_hex(hash) ^ base_hash;

		for (int i = 1; i < 10; i++) {
			base_hash = crc32_update(base_hash, 0x30);
			if (i < 6) {
				std::vector<uint32_t> temp;
				lookup(crc_hash ^ base_hash, &temp);
				candidates.insert(candidates.end(), temp.begin(), temp.end());
			}
			else {
				uint32_t start_prefix = pow(10, i - 6);
				uint32_t end_prefix = pow(10, i - 5);

				for (uint32_t prefix = start_prefix; prefix < end_prefix; prefix++) {
					std::vector<uint32_t> temp;
					lookup(crc_hash ^ base_hash ^ compute(prefix, true), &temp);
					for (int j = 0; j < temp.size(); j++) {
						candidates.push_back(prefix * 100000 + temp[j]);
					}
				}
			}
		}
		return candidates;
	}

private:
	uint32_t* crc32_table = new uint32_t[256]();
	uint32_t* rainbow_table_hash = new uint32_t[100000]();
	uint32_t* rainbow_table_value = new uint32_t[100000]();
	uint32_t* full_hash_cache = new uint32_t[100000]();
	uint32_t* short_hash_buckets = new uint32_t[65537]();
	uint32_t* short_hash_bucket_starts = new uint32_t[65537]();

	void init_table(uint32_t poly) {
		for (int i = 0; i < 256; i++) {
			uint32_t temp = i;
			for (int j = 0; j < 8; j++) {
				if (temp & 1) {
					temp = (temp >> 1) ^ poly;
				}
				else {
					temp >>= 1;
				}
			}
			crc32_table[i] = temp;
		}
	}
	uint32_t crc32_update(uint32_t curr_crc, uint32_t code) {
		return (curr_crc >> 8) ^ crc32_table[(curr_crc ^ code) & 0xff];
	}
	void divide_integer(uint32_t integer, std::vector<uint32_t> *int_chr) {
		while (integer > 0) {
			int_chr->push_back(integer % 10);
			integer /= 10;
		}
	}
	uint32_t compute(uint32_t input, bool add_padding = false) {
		uint32_t curr_crc = 0;
		std::vector<uint32_t> int_chr;
		divide_integer(input, &int_chr);

		for (int i = int_chr.size() - 1; ~i; i--) {
			curr_crc = crc32_update(curr_crc, int_chr[i]);
		}

		if (add_padding) {
			for (int i = 0; i < 5; i++) {
				curr_crc = crc32_update(curr_crc, 0);
			}
		}

		return curr_crc;
	}
	void cumsum(uint32_t *iter, uint32_t *sum, uint32_t len) {
		*sum = *iter;
		for (uint32_t i = 1; i < len; i++) {
			*(sum + i) = *(sum + i - 1) + *(iter + i);
		}
	}

	void lookup(uint32_t hash, std::vector<uint32_t>* iter) {
		uint32_t short_hash = hash >> 16;

		for (uint32_t i = short_hash_bucket_starts[short_hash];
			i < short_hash_bucket_starts[short_hash + 1]; i++) {
			if (rainbow_table_hash[i] == hash) {
				iter->push_back(rainbow_table_value[i]);
			}
		}
	}
	uint32_t pow(uint32_t base, uint32_t exp) {
		uint32_t mul = base;

		if (!exp) {
			return 1;
		}

		for (uint32_t i = 1; i < exp; i++) {
			mul *= base;
		}

		return mul;
	}

	uint32_t ascii_to_hex(std::string asc) {
		uint32_t hex = 0;
		uint8_t length = asc.size();
		for (uint8_t i = 0; i < length; i++) {
			if (asc[i] <= '9') {
				hex += (asc[i] - '0') * pow(16, length-i-1);
			}
			else if (asc[i] <= 'F') {
				hex += (asc[i] - 'A' + 10) * pow(16, length-i-1);
			}
			else if (asc[i] <= 'f') {
				hex += (asc[i] - 'a' + 10) * pow(16, length-i-1);
			}
		}
		return hex;
	}

};


PYBIND11_MODULE(Crc32Engine, m) {
	py::class_<Crc32Engine>(m, "Crc32Engine")
		.def(py::init<uint32_t>(), py::arg("poly") = 0xedb88320)
		.def("crack", &Crc32Engine::crack, "calculate the crack number")
		.def("__repr__",
			[](const Crc32Engine &a){
				return "Crc32Engine";
			});
}