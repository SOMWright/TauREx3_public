import unittest
from unittest.mock import patch
from unittest import mock
import numpy as np
from taurex.data.profiles.chemistry.gas.constantgas import ConstantGas
from taurex.data.profiles.chemistry.gas.twopointgas import TwoPointGas
from taurex.data.profiles.chemistry.gas.twolayergas import TwoLayerGas
from taurex.data.profiles.chemistry.taurexchemistry import TaurexChemistry


class TaurexChemistryTest(unittest.TestCase):

    def test_init(self):
        tc = TaurexChemistry()
        
        params = tc.fitting_parameters()
        self.assertIn('H2_He',params)

    def test_add(self):
        from taurex.cache import OpacityCache
        with patch.object(OpacityCache,"find_list_of_molecules") as mock_my_method:
            mock_my_method.return_value = ['H2O','CH4','C2H2']
            tc = TaurexChemistry()
        tc.addGas(ConstantGas('H2O'))
        tc.addGas(TwoLayerGas('CH4'))
        tc.addGas(TwoPointGas('C2H2'))
        tc.addGas(ConstantGas('N2'))
        test_layers = 100

        pres_prof = np.arange(1,test_layers+1)*200

        tc.initialize_chemistry(test_layers,pres_prof,pres_prof,pres_prof)

        params = tc.fitting_parameters()

        self.assertIn('N2',params)
        self.assertIn('H2_He',params)

        self.assertIn('H2O',params)
        self.assertEqual(params['H2O'][2](),1e-5)
        self.assertIn('CH4_T',params)
        self.assertIn('CH4_S',params)
        self.assertIn('C2H2_T',params)
        self.assertIn('C2H2_S',params)
        self.assertIn('CH4_P',params)

        self.assertIsNotNone(tc.muProfile)

    

    def test_fill_gas(self):
       tc = TaurexChemistry(fill_gases='CH4')

       
