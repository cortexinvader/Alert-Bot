from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'crypto',
        ['cpp_modules/crypto.cpp'],
        include_dirs=[pybind11.get_include()],
        language='c++',
        extra_compile_args=['-std=c++11'],
    ),
]

setup(
    name='alertbot-crypto',
    version='1.0.0',
    ext_modules=ext_modules,
)
