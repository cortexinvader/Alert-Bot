#include <pybind11/pybind11.h>
#include <string>
#include <algorithm>

namespace py = pybind11;

std::string simple_encrypt(const std::string& data, const std::string& key) {
    std::string result = data;
    size_t key_len = key.length();
    
    for (size_t i = 0; i < result.length(); ++i) {
        result[i] = result[i] ^ key[i % key_len];
    }
    
    std::string encoded;
    for (unsigned char c : result) {
        char hex[3];
        snprintf(hex, sizeof(hex), "%02x", c);
        encoded += hex;
    }
    
    return encoded;
}

std::string simple_decrypt(const std::string& encrypted, const std::string& key) {
    std::string decoded;
    for (size_t i = 0; i < encrypted.length(); i += 2) {
        std::string byte = encrypted.substr(i, 2);
        char c = static_cast<char>(std::stoi(byte, nullptr, 16));
        decoded += c;
    }
    
    std::string result = decoded;
    size_t key_len = key.length();
    
    for (size_t i = 0; i < result.length(); ++i) {
        result[i] = result[i] ^ key[i % key_len];
    }
    
    return result;
}

PYBIND11_MODULE(crypto, m) {
    m.doc() = "AlertBot encryption module";
    m.def("encrypt", &simple_encrypt, "Encrypt data with XOR cipher",
          py::arg("data"), py::arg("key"));
    m.def("decrypt", &simple_decrypt, "Decrypt data with XOR cipher",
          py::arg("encrypted"), py::arg("key"));
}
