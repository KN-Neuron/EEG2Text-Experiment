import platform
import ctypes

from ctypes.util import find_library
from os import listdir, getcwd
from os.path import isfile, join
from shutil import which

from brainaccess.utils.exceptions import BrainAccessException


def get_lib_name(name: str) -> str:
    platform_name = platform.uname()[0]
    if platform_name == "Windows":
        return name + ".dll"
    elif platform_name == "Linux":
        return "lib" + name + ".so"
    else:
        raise BrainAccessException(f'Unsupported platform "{platform_name}"')


def load_library(name: str) -> ctypes.CDLL:
    dll_name = get_lib_name(name)
    try:
        onlyfiles = [f for f in listdir(".") if isfile(join(".", f))]
        if dll_name in onlyfiles:
            return ctypes.CDLL(join(getcwd(), dll_name))
        else:
            _lib = find_library(dll_name)
            if _lib:
                return ctypes.CDLL(_lib)
            else:
                lib = which(dll_name)
                if lib:
                    return ctypes.CDLL(lib)
                else:
                    raise BrainAccessException("Could not find " + dll_name)
    except OSError:
        raise BrainAccessException("Could not load " + dll_name)
