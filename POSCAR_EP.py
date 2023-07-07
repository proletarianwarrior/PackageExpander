# -*- coding: utf-8 -*-
# @Time : 2023/7/4 19:19
# @Author : DanYang
# @File : POSCAR_EP.py
# @Software : PyCharm
import re
import argparse

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--dim", type=str, help="输入扩展的大小")
args = parser.parse_args()


class PackageExpander:
    def __init__(self, file_path="POSCAR"):
        self.file_path = file_path
        np.set_printoptions(precision=16)
        self.dim = [int(i) for i in args.dim.split(" ")]

    def __load_file(self):
        with open(self.file_path, 'r') as file:
            poscar_text = file.read()
        poscar_text = poscar_text.strip()
        poscar_text = self.__clean_text(poscar_text.split('\n'))
        return poscar_text

    def __clean_text(self, text_list):
        text_list = [text.strip() for text in text_list]
        return text_list

    def __parse_detail(self, text_list):
        scale_factor = float(text_list[0])
        scale_coordinate = np.fromstring('\n'.join(text_list[1:]), dtype="float64", sep=" ").reshape((3, 3))
        return scale_factor, scale_coordinate

    def __parse_location(self, text_list):
        location_coordinate = np.fromstring(' '.join(text_list), dtype="float64", sep=" ").reshape((-1, 3))
        return location_coordinate

    def __parse_atoms(self, text_list):
        atoms_name = re.split("\s+", text_list[0])
        atoms_num = [int(text) for text in re.split("\s+", text_list[1])]
        return dict(zip(atoms_name, atoms_num))

    def _parse_old_file(self):
        text = self.__load_file()
        scale_factor, scale_coordinate = self.__parse_detail(text[1:5])
        atoms = self.__parse_atoms(text[5:7])
        location_coordinate = self.__parse_location(text[8:])
        return (scale_factor, scale_coordinate), atoms, location_coordinate

    def expand_package(self):
        expand_factor = self.dim
        (scale_factor, scale_coordinate), atoms, location_coordinate = self._parse_old_file()
        grid = np.meshgrid(*[range(1, x + 1) for x in expand_factor])
        coords = np.vstack([x.flatten() for x in grid]).T
        new_scale_coordinate = scale_coordinate * expand_factor
        new_coordinate = []
        for vector in location_coordinate:
            for coord in coords:
                new_vector = vector + (np.array(coord) - 1) * scale_factor
                new_coordinate.append(new_vector)
        new_coordinate = np.array(new_coordinate) / expand_factor
        atom_name = "\t".join(atoms.keys())
        atom_num = np.array([i for i in atoms.values()]) * np.prod(expand_factor)
        atom_num = "\t".join([str(i) for i in atom_num])
        with open("POSCAR_EP", "w") as file:
            file.write("generate by PackageExpander\n")
            file.write(str(scale_factor) + "\n")
            file.write(" " + re.sub("[\[\]]", "", str(new_scale_coordinate) + "\n"))
            file.write(atom_name + "\n")
            file.write(atom_num + "\n")
            file.write("Direct\n")
            file.write(" " + re.sub("[\[\]]", "", str(new_coordinate) + "\n"))


a = PackageExpander()
a.expand_package()
