import numpy as np
from .simplemodel import SimpleForwardModel


class TransmissionModel(SimpleForwardModel):
    """
    Parameters
    ----------
    name: string
        Name to use in logging

    planet: :obj:`Planet` or :obj:`None`
        Planet object created or None to use the default planet (Jupiter)

    """
    def __init__(self,
                 planet=None,
                 star=None,
                 pressure_profile=None,
                 temperature_profile=None,
                 chemistry=None,
                 nlayers=100,
                 atm_min_pressure=1e-4,
                 atm_max_pressure=1e6):

        super().__init__(self.__class__.__name__, planet,
                         star,
                         pressure_profile,
                         temperature_profile,
                         chemistry,
                         nlayers,
                         atm_min_pressure,
                         atm_max_pressure)

    def compute_path_length(self, dz):

        dl = []

        planet_radius = self._planet.fullRadius
        total_layers = self.nLayers

        z = self.altitudeProfile
        self.debug('Computing path_length: \n z=%s \n dz=%s', z, dz)

        for layer in range(0, total_layers):

            p = (planet_radius+dz[0]/2 + z[layer])**2
            k = np.zeros(shape=(self.nLayers-layer))
            k[0] = np.sqrt((planet_radius + dz[0]/2. + z[layer] +
                            dz[layer]/2.)**2 - p)

            k[1:] = np.sqrt((planet_radius + dz[0]/2 + z[layer+1:] +
                             dz[layer+1:]/2)**2 - p)

            k[1:] -= np.sqrt((planet_radius + dz[0]/2 +
                              z[layer:self.nLayers-1] +
                              dz[layer:self.nLayers-1]/2)**2 - p)

            dl.append(k*2.0)
        return dl

    def path_integral(self, wngrid, return_contrib):

        dz = np.gradient(self.altitudeProfile)

        wngrid_size = wngrid.shape[0]

        path_length = self.compute_path_length(dz)

        density_profile = self.densityProfile

        total_layers = self.nLayers

        path_length = self.compute_path_length(dz)
        self.path_length = path_length

        tau = np.zeros(shape=(total_layers, wngrid_size), dtype=np.float64)

        for layer in range(total_layers):

            self.debug('Computing layer %s', layer)
            dl = path_length[layer]

            endK = total_layers-layer

            for contrib in self.contribution_list:
                if tau[layer].min() > 10:
                    break
                self.debug('Adding contribution from %s', contrib.name)
                contrib.contribute(self, 0, endK, layer, layer,
                                   density_profile, tau, path_length=dl)

        self.debug('tau %s %s', tau, tau.shape)

        absorption, tau = self.compute_absorption(tau, dz)
        return absorption, tau

    def compute_absorption(self, tau, dz):

        tau = np.exp(-tau)
        ap = self.altitudeProfile[:, None]
        pradius = self._planet.fullRadius
        sradius = self._star.radius
        _dz = dz[:, None]

        integral = np.sum((pradius+ap)*(1.0-tau)*_dz*2.0, axis=0)
        return ((pradius**2.0) + integral)/(sradius**2), tau
