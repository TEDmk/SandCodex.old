import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

requires = ["docker==4.1.0"]

tests_require = ["pytest", "pycov"]

dev_require = ["flake8", "black"]

setup(
    name="SandCodex",
    version="0.0.0",
    description="Execute code in a container-based sandbox",
    packages=["sand_codex"],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extra_requires={"test": tests_require, "dev": dev_require},
)
