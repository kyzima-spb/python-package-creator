# coding: utf-8

from py_package_creator import Creator


def ppc():
    creator = Creator()
    creator.run()
    creator.write_setup_file()
