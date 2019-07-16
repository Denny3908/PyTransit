#  PyTransit: fast and easy exoplanet transit modelling in Python.
#  Copyright (C) 2010-2019  Hannu Parviainen
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from numpy import atleast_2d, zeros, concatenate
from numpy.polynomial.legendre import legvander

from ...param import LParameter, NormalPrior as NP


class LegendreBaseline:
    def __init__(self, nlegendre):
        self.nlegendre = nlegendre
        self.times = []
        self.timea = None
        self.lcslices = None
        self.nlc = 0
        self.ps = None

    def _init_p_baseline(self):
        """Baseline parameter initialisation.
        """

        self.mtimes = [t - t.mean() for t in self.times]
        self.windows = window = concatenate(self.mtimes).ptp()
        self.mtimes = [t / window for t in self.mtimes]
        self.legs = [legvander(t, self.nlegendre) for t in self.mtimes]
        self.ofluxa = self.ofluxa.astype('d')

        bls = []
        for i, tn in enumerate(range(self.nlc)):
            bls.append(LParameter(f'bli_{tn}', f'bl_intercept_{tn}', '', NP(1.0, 0.01), bounds=(0.98, 1.02)))
            for ipoly in range(1, self.nlegendre + 1):
                bls.append(
                    LParameter(f'bls_{tn}_{ipoly}', f'bl_c_{tn}_{ipoly}', '', NP(0.0, 0.001), bounds=(-0.1, 0.1)))
        self.ps.add_lightcurve_block('baseline', self.nlegendre + 1, self.nlc, bls)
        self._sl_bl = self.ps.blocks[-1].slice
        self._start_bl = self.ps.blocks[-1].start

    def baseline(self, pvp):
        """Multiplicative baseline"""
        pvp = atleast_2d(pvp)
        fbl = zeros((pvp.shape[0], self.timea.size))
        for ipv, pv in enumerate(pvp):
            bl = pv[self._sl_bl]
            for itr, sl in enumerate(self.lcslices):
                fbl[ipv, sl] = bl[itr * (self.nlegendre + 1):(itr + 1) * (self.nlegendre + 1)] @ self.legs[itr].T
        return fbl
