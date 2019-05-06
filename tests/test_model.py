
import unittest
import shutil, tempfile
from os import path
from unittest.mock import patch, mock_open
from taurex.model.model import ForwardModel
from taurex.model.simplemodel import SimpleForwardModel
import numpy as np
import pickle

class ForwardModelTest(unittest.TestCase):
    pass



class SimpleForwardModelTest(unittest.TestCase):


    def test_init(self):
        model = SimpleForwardModel('test')