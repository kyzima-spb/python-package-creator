# coding: utf-8

from setuptools import setup, find_packages


setup(
    name="python-package-creator",
    author="Kirill Vercetti",
    author_email="office@kyzima-spb.com",
    license="Apache-2.0",
    url="https://github.com/kyzima-spb/python-package-creator",
    description="",
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': ['ppc=py_package_creator.command_line:ppc']
    }
)
