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
    install_requires=[
        'appdirs>=1.4',
        'opensource>=1.0',
        'prompt-toolkit>=1.0',
        'Pygments>=2.2',
        'six>=1.10'
    ],
    entry_points={
        'console_scripts': ['ppc=py_package_creator.command_line:ppc']
    }
)
