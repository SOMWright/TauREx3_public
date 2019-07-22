from taurex.log import Logger
import numpy as np
from taurex.output.writeable import Writeable
import math
class Optimizer(Logger):
    """
    A base class that handles fitting and optimization of forward models.
    The class handles the compiling and management of fitting parameters in 
    forward models, in its current form it cannot fit and requires a class derived from it
    to implement the :func:`compute_fit` function.

    Parameters
    ----------
    name:  str
        Name to be used in logging

    observed : :class:`~taurex.data.spectrum.spectrum.BaseSpectrum`, optional
        See :func:`set_observed`
    
    model : :class:`~taurex.model.model.ForwardModel`, optional
        See :func:`set_model`


    """

    def __init__(self,name,observed=None,model=None):
        super().__init__(name)

        self._model = model
        self._observed = observed
        self._model_callback = None

    def set_model(self,model):
        """
        Sets the model to be optimized/fit

        Parameters
        ----------
        model : :class:`~taurex.model.model.ForwardModel`
            The forward model we wish to optimize
        
        """
        self._model = model

    def set_observed(self,observed):
        """
        Sets the observation to optimize the model to

        Parameters
        ----------
        observed : :class:`~taurex.data.spectrum.spectrum.BaseSpectrum`
            Observed spectrum we will optimize to
        
        """
        self._observed = observed


    def compile_params(self):
        """ 


        Goes through and compiles all parameters within the model that
        we will be retrieving. Called before :func:`compute_fit`


        """
        self.info('Initializing parameters')
        self.fitting_parameters=[]
        # param_name,param_latex,
        #                 fget.__get__(self),fset.__get__(self),
        #                         default_fit,default_bounds
        for params in self._model.fittingParameters.values():
            name,latex,fget,fset,mode,to_fit,bounds = params

            self.debug('Checking fitting parameter {}'.format(params))
            if to_fit:
                # #To make sure of any conversions going on lets get the current value
                # c_v = fget()

                # #Get the boundaries
                # bound_min= bounds[0]
                # bound_max = bounds[1]

                # #set them to the internal model
                # fset(bound_min)
                # bound_min = fget()

                # fset(bound_max)
                # bound_max = fget()

                # fset(c_v)

                self.fitting_parameters.append(params)
        
        self.info('-------FITTING---------------')
        self.info('Parameters to be fit:')
        for params in self.fitting_parameters:
            name,latex,fget,fset,mode,to_fit,bounds = params
            self.info('{}: Value: {} Mode:{} Boundaries:{}'.format(name,fget(),mode,bounds))


    def update_model(self,fit_params):
        """
        Updates the model with new parameters
        
        Parameters
        ----------
        fit_params : :obj:`list`
            A list of new values to apply to the model. The list of values are
            assumed to be in the same order as the parameters given by :func:`fit_names`

        
        """

        for value,param in zip(fit_params,self.fitting_parameters):
            name,latex,fget,fset,mode,to_fit,bounds = param
            if mode == 'log':
                value = 10**value
            fset(value)

    @property
    def fit_values_nomode(self):
        """ 
        
        Returns a list of the current values of a fitting parameter. 
        Regardless of the ``mode`` setting

        Returns
        -------
        :obj:`list`:
            List of each value of a fitting parameter
        
        """
        


        


        return [c[2]() for c in self.fitting_parameters]
    @property
    def fit_values(self):
        """ 
        
        Returns a list of the current values of a fitting parameter. This 
        respects the ``mode`` setting

        Returns
        -------
        :obj:`list`:
            List of each value of a fitting parameter
        
        """

        return [c[2]() if c[4]=='linear' else math.log10(c[2]())for c in self.fitting_parameters]

    @property
    def fit_boundaries(self):
        """ 
        
        Returns the fitting boundaries of the parameter

        Returns
        -------
        :obj:`list`:
            List of boundaries for each fitting parameter. It takes the form of
            a python :obj:`tuple` with the form ( ``bound_min`` , ``bound_max`` )
        
        """
        return [c[-1] if c[4]=='linear' else (math.log10(c[-1][0]),math.log10(c[-1][1])) for c in self.fitting_parameters]


    @property
    def fit_names(self):
        """ 
        
        Returns the names of the model parameters we will be fitting

        Returns
        -------
        :obj:`list`:
            List of names of parameters that will be fit
        
        """
        return [c[0] if c[4]=='linear' else 'log_{}'.format(c[0]) for c in self.fitting_parameters]

    @property
    def fit_latex(self):
        """ 
        
        Returns the names of the parameters in LaTeX format

        Returns
        -------
        :obj:`list`
            List of parameter names in LaTeX format
        

        """

        return [c[1] if c[4]=='linear' else 'log({})'.format(c[1]) for c in self.fitting_parameters]

    def enable_fit(self,parameter):
        """
        Enables fitting of the parameter

        Parameters
        ----------
        parameter : str
            Name of the parameter we want to fit
        
        """


        name,latex,fget,fset,mode,to_fit,bounds = self._model.fittingParameters[parameter]
        to_fit = True
        self._model.fittingParameters[parameter]= (name,latex,fget,fset,mode,to_fit,bounds)

    def disable_fit(self,parameter):
        """
        Disables fitting of the parameter

        Parameters
        ----------
        parameter : str
            Name of the parameter we do not want to fit
        
        """
        name,latex,fget,fset,mode,to_fit,bounds = self._model.fittingParameters[parameter]
        to_fit = False
        self._model.fittingParameters[parameter]= (name,latex,fget,fset,mode,to_fit,bounds)
    
    def set_boundary(self,parameter,new_boundaries):
        """
        Sets the boundary of the parameter

        Parameters
        ----------
        parameter : str
            Name of the parameter we want to change
        
        new_boundaries : tuple of float
            New fitting boundaries, with the form ( ``bound_min`` , ``bound_max`` ). These
            should not take into account the ``mode`` setting of a fitting parameter.

        
        """
        name,latex,fget,fset,mode,to_fit,bounds = self._model.fittingParameters[parameter]
        bounds = new_boundaries
        self._model.fittingParameters[parameter]= (name,latex,fget,fset,mode,to_fit,bounds)


    def set_factor_boundary(self,parameter,factors):
        """
        Sets the boundary of the parameter based on a factor

        Parameters
        ----------
        parameter : str
            Name of the parameter we want to change
        
        factor : tuple of float
            To be written


          
        """

        name,latex,fget,fset,mode,to_fit,bounds = self._model.fittingParameters[parameter]

        value = fget()

        # if mode == 'log':
        #     log_value = math.log10(value)

        #     new_boundaries = 10**(log_value/factors[0]),10**(log_value*factors[1])
        # else:
        #     
        new_boundaries = factors[0]*value,factors[1]*value
        
        bounds = new_boundaries
        self._model.fittingParameters[parameter]= (name,latex,fget,fset,mode,to_fit,bounds)

    def set_mode(self,parameter,new_mode):
        """
        Sets the fitting mode of a parameter

        Parameters
        ----------
        parameter : str
            Name of the parameter we want to change
        
        new_mode : ``linear`` or ``log``
            Sets whether the parameter is fit in linear or log space

        

        """
        new_mode = new_mode.lower()
        name,latex,fget,fset,mode,to_fit,bounds = self._model.fittingParameters[parameter]
        if not new_mode in ('log','linear',):
            self.error('Incorrect mode set for fit parameter,')
            raise ValueError

        self._model.fittingParameters[parameter]= (name,latex,fget,fset,new_mode,to_fit,bounds)       


    def chisq_trans(self, fit_params,data,datastd):
        """

        Computes the Chi-Squared between the forward model and
        observation. The steps taken are:
            1. Forward model (FM) is updated with :func:`update_model`
            2. FM is then computed at its native grid then binned.
            3. Chi-squared between FM and observation is computed

        
        Parameters
        ----------
        fit_params : list of parameter values
            List of new parameter values to update the model 

        data : obj:`ndarray`
            Observed spectrum

        datastd : obj:`ndarray`
            Observed spectrum error
        

        Returns
        -------
        float :
            chi-squared


        """
        from taurex.util import bindown
        import numexpr as ne
        self.update_model(fit_params)

        obs_bins= self._observed.wavenumberGrid


        final_model,_,_,_ = self._model.model(obs_bins)
        res = (data.flatten() - final_model.flatten()) / datastd.flatten()
        res = np.nansum(res*res)
        if res == 0:
            res = np.nan
        return res


    def compute_fit(self):
        """
        Unimplemented. When inheriting this should be overwritten
        to perform the actual fit.

        Raises
        ------
        NotImplementedError
            Raised when a derived class does override this function

        """
        raise NotImplementedError


    def fit(self):
        """

        Performs fit.

        """
        from tabulate import tabulate
        self.compile_params()

        fit_names = self.fit_names
        fit_boundaries = self.fit_boundaries

        fit_min = [x[0] for x in fit_boundaries]
        fit_max = [x[1] for x in fit_boundaries]

        fit_values = self.fit_values
        print()
        print('-------------------------------------')
        print('------Retrieval Parameters-----------')
        print('-------------------------------------')
        print()
        print('Dimensionality of fit:',len(fit_names))
        print()
        output = tabulate(zip(fit_names,fit_values,fit_min,fit_max), headers=['Param', 'Value','Bound-min', 'Bound-max'])
        print(output)
        print()



        self.compute_fit()

    def write_optimizer(self,output):
        """

        Writes optimizer settings under the 'Optimizer' heading in an output file

        Parameters
        ----------
        output:  :class:`~taurex.output.output.Output` or :class:`~taurex.output.output.OutputGroup`
            Group (or root) in output file to write to

        Returns
        -------
        :class:`~taurex.output.output.Output` or :class:`~taurex.output.output.OutputGroup`
            Group (or root) in output file written to

        """
        output.write_string('optimizer',self.__class__.__name__)
        
        return output
    
    def write_fit(self,output):
        """
        Writes basic fitting parameters into output

        Parameters
        ----------
        output : :class:`~taurex.output.output.Output` or :class:`~taurex.output.output.OutputGroup`
            Group (or root) in output file to write to

        Returns
        -------
        :class:`~taurex.output.output.Output` or :class:`~taurex.output.output.OutputGroup`
            Group (or root) in output file written to

        """
        output.write_string('fit_format',self.__class__.__name__)
        output.write_string_array('fit_parameter_names',self.fit_names)
        output.write_string_array('fit_parameter_latex',self.fit_latex)
        output.write_list('fit_parameter_values',self.fit_values)
        output.write_list('fit_parameter_values_nomode',self.fit_values_nomode)
        return output


    def write(self,output):
        """
        Creates 'Optimizer' and 'Fitting' groups and writes
        them respectively

        

        Parameters
        ----------
        output : :class:`~taurex.output.output.Output` or :class:`~taurex.output.output.OutputGroup`
            Group (or root) in output file to write to



        """
        opt = output.create_group('Optimizer')
        fit = output.create_group('Fit')

        self.write_optimizer(opt)
        self.write_fit(fit)
        









