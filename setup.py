# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("mt5_trading_dll.pyx", language_level=3),
)
