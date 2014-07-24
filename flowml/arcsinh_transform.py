# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from __future__ import division
import numpy as np
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
# Follows example 
# http://matplotlib.org/examples/api/custom_scale_example.html?highlight=custom_scale_example

from matplotlib.ticker import (NullLocator, LogLocator, AutoLocator,
                               SymmetricalLogLocator)
from matplotlib.ticker import (NullFormatter, ScalarFormatter,
                               LogFormatterMathtext)

class ArcsinhScale(mscale.ScaleBase):
    name = 'arcsinh'
    
    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)
        self.cofactor = kwargs.pop('cofactor', 5.)
        self.base = kwargs.pop('base', 10.)
        self.subs = kwargs.pop('subs', np.arange(2,10)) 
    def get_transform(self):
        return self.ArcsinhTransform(self.cofactor)

    def set_default_locators_and_formatters(self, axis):
        # Copy of LogScale version of this function
        axis.set_major_locator(LogLocator(self.base))
        axis.set_major_formatter(LogFormatterMathtext(self.base))
        axis.set_minor_locator(LogLocator(self.base, self.subs))
        axis.set_minor_formatter(NullFormatter())

    class ArcsinhTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, cofactor):
            mtransforms.Transform.__init__(self)
            self.cofactor = cofactor

        def transform_non_affine(self, a):
            return np.arcsinh(self.cofactor*a)
        
        def inverted(self):
            return ArcsinhScale.InvertedArcsinhTransform(self.cofactor)

    class InvertedArcsinhTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True
        
        def __init__(self, cofactor):
            mtransforms.Transform.__init__(self)
            self.cofactor = cofactor
        
        def transform_non_affine(self, a):
            return np.sinh(a / self.cofactor)

        def inverted(self):
            return ArcsinhScale.ArcsinhTransform(self.cofactor)


mscale.register_scale(ArcsinhScale)  

