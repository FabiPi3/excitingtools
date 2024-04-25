"""Parser for output files generated by taskGroup of GW."""

from ast import literal_eval
from typing import Dict

import numpy as np
from numpy.typing import NDArray


def __parse_file_with_matrix(file_name: str) -> NDArray[np.complex128]:
    """Parser for files containing matrices.

    This file looks like:
     1st line: 2 (rank=2)
     2nd line: fours integers i,j,m,n with the ranges: matrix[i:m,j:n]
     next lines: matrix elements (complex numbers)

    :param file_name: name of the file
    :return: matrix read from file
    """
    with open(file_name) as file:
        dim = int(file.readline().split()[0])
        m_ini, n_ini, m_end, n_end = (int(x) for x in file.readline().split())
        assert dim == 2 and m_ini == 1 and n_ini == 1, "file should contain a full matrix"
        matrix = np.zeros((m_end, n_end), dtype=complex)

        counter = 0
        for line in file:
            for data in line.split():
                matrix[np.unravel_index(counter, (m_end, n_end), order="F")] = complex(*literal_eval(data))
                counter += 1
    return matrix


def __parse_file_with_array_of_rank_3(file_name: str) -> NDArray[np.complex128]:
    """Parser for files containing arrays of rank 3.

    This file looks like:
     1st line: 3 (rank=3)
     2nd line: six integers i,j,k,m,n,p with the ranges: matrix[i:m,j:n,k:p]
     next lines: array elements (complex numbers)

    :param file_name: name of the file
    :return: array read from file
    """
    with open(file_name) as file:
        dim = int(file.readline().split()[0])
        m_ini, n_ini, p_ini, m_end, n_end, p_end = (int(x) for x in file.readline().split())
        assert dim == 3 and m_ini == 1 and n_ini == 1 and p_ini == 1, "file should contain a full array"
        array = np.zeros((m_end, n_end, p_end), dtype=complex)

        counter = 0
        for line in file:
            for data in line.split():
                array[np.unravel_index(counter, (m_end, n_end, p_end), order="F")] = complex(*literal_eval(data))
                counter += 1
    return array


def __square_matrix(a: NDArray) -> NDArray:
    """Square a matrix.

    :param a: input matrix
    :return: the result product
    """
    return np.matmul(a.T.conj(), a)


def parse_barc(file_name: str) -> Dict[str, NDArray[np.complex128]]:
    """Parser for BARC_*.OUT, where * is an integer.

    The file contains the product: M*(v^1/2), where M is a matrix with
    eigenvectors, and v is a diagonal matrix with the eigenvalues.
    Since the definition of M is not unique, we must return A^H*A,
    where A is the matrix read.

    :param file_name: name of the file
    :return: parsed data as dictionary
    """
    return {"CoulombMatrix": __square_matrix(__parse_file_with_matrix(file_name))}


def parse_sgi(file_name: str) -> Dict[str, NDArray[np.complex128]]:
    """Parser for SGI_*.OUT, where * is an integer.

    This file contains the vectors $\tilde{S_{Gi}}$, defined in Eq. (41) of
    Computer Phys. Comm. 184, 348 (2013).
    By reading the matrix A as stored, and performing A^H*A, one gets the overlap
    matrix between basis elements defined for the interstitial region.

    :param file_name: name of the file
    :return: parsed data as dictionary
    """
    return {"OverlapMatrix": __square_matrix(__parse_file_with_matrix(file_name))}


def parse_epsilon(file_name: str) -> Dict[str, NDArray[np.complex128]]:
    """Parser for the gw-epsilon files, which contain the dielectric function, its head or wings.:
      - EPSH.OUT,
      - EPSW1.OUT,
      - EPSW2.OUT,
      - EPSILON-GW_Q*.OUT, where * is an integer

    :param file_name: name of the file
    :return: parsed data as dictionary
    """
    return {"epsilon_tensor": __parse_file_with_array_of_rank_3(file_name)}


def parse_inverse_epsilon(file_name: str) -> Dict[str, NDArray[np.complex128]]:
    """Parser for the gw-inverse-epsilon files, which contain the inverse of the
    dielectric function, its head or wings:
      - INVERSE-EPSH.OUT,
      - INVERSE-EPSW1.OUT,
      - INVERSE-EPSW2.OUT,
      - INVERSE-EPSILON_Q*.OUT, where * is an integer

    :param file_name: name of the file
    :return: parsed data as dictionary
    """
    return {"inverse_epsilon_tensor": __parse_file_with_array_of_rank_3(file_name)}
