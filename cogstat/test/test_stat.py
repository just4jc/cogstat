# -*- coding: utf-8 -*-

import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
print(sys.path)
import numpy as np
import pandas as pd
from cogstat import cogstat as cs

print(cs.__file__)
print(cs.__version__)
print(os.path.abspath(cs.__file__))

"""
- All statistical value should be tested at least once.
- All leafs of the decision tree should be tested once.
- Tests shouldn't give p<0.001 results, because exact values cannot be tested. 
- No need to test the details of the statistical methods imported from other modules, 
because that is the job of that specific module.
- All variables should be used with 3 digits decimal precision, to ensure that copying 
the data for validation no additional rounding happens.
"""

#cs.output_type = 'do not format'

np.random.seed(555)
# https://docs.scipy.org/doc/numpy/reference/routines.random.html
# Make sure to use round function to have the same precision of the data when copied to other software
data_np = np.vstack((
    np.round(np.random.normal(loc=3, scale=3, size=30), 3),
    np.round(np.random.lognormal(mean=3, sigma=3, size=30), 3),
    np.random.randint(3, size=30),
    np.random.randint(3, size=30),
    np.round(np.random.normal(loc=3, scale=3, size=30), 3),
    np.round(np.random.lognormal(mean=1.4, sigma=0.6, size=30), 3),
    np.round(np.random.normal(loc=6, scale=3, size=30), 3),
    np.round(np.random.normal(loc=7, scale=6, size=30), 3),
    np.random.randint(2, size=30),
    np.random.randint(2, size=30),
    np.random.randint(2, size=30),
    np.concatenate((np.round(np.random.normal(loc=3, scale=3, size=15), 3),
                    np.round(np.random.normal(loc=4, scale=3, size=15), 3))),
    np.array([1]*15+[2]*15),
    np.array([1]+[2]*29),
    np.concatenate((np.round(np.random.normal(loc=3, scale=3, size=15), 3),
                    np.round(np.random.lognormal(mean=1.5, sigma=2.0, size=15), 3))),
    np.concatenate((np.round(np.random.normal(loc=3, scale=3, size=15), 3),
                    np.round(np.random.normal(loc=3, scale=7, size=15), 3))),
    np.array([1]*10+[2]*8+[3]*12),
    np.concatenate((np.round(np.random.normal(loc=3, scale=3, size=10), 3),
                    np.round(np.random.normal(loc=3, scale=3, size=8), 3),
                    np.round(np.random.normal(loc=6, scale=3, size=12), 3)))
    ))
data_pd = pd.DataFrame(data_np.T, columns=
                       ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r'])
data = cs.CogStatData(data=data_pd, measurement_level=
                      'int int nom nom int int int int nom nom nom int nom nom int int int int')


class CogStatTestCase(unittest.TestCase):
    """Unit tests for CogStat."""

    def test_explore_variables(self):
        """Test explore variables"""

        # Int variable
        result = data.explore_variable('a', 1, 2.0)
        #for i, res in enumerate(result): print i, res
        self.assertTrue('N of valid cases: 30' in result[2])
        self.assertTrue('N of missing cases: 0' in result[2])
        self.assertTrue('<td>Mean</td>      <td>3.1438</td>' in result[4])
        self.assertTrue('<td>Standard deviation</td>      <td>3.2152</td>' in result[4])
        self.assertTrue('<td>Skewness</td>      <td>0.3586</td>' in result[4])
        self.assertTrue('<td>Kurtosis</td>      <td>0.0446</td>' in result[4])
        self.assertTrue('<td>Range</td>      <td>12.7840</td>' in result[4])
        self.assertTrue('<td>Maximum</td>      <td>9.9810</td>' in result[4])
        self.assertTrue('<td>Upper quartile</td>      <td>4.3875</td>' in result[4])
        self.assertTrue('<td>Median</td>      <td>2.8545</td>' in result[4])
        self.assertTrue('<td>Lower quartile</td>      <td>1.4190</td>' in result[4])
        self.assertTrue('<td>Minimum</td>      <td>-2.8030</td>' in result[4])
        # Shapiro-Wilk normality
        self.assertTrue('<i>W</i> = 0.959' in result[6])
        self.assertTrue('<i>p</i> = 0.287' in result[6])

        # Population estimation and one sample t-test
        self.assertTrue('[1.9227, 4.3649]' in result[9])  # CI of the mean
        self.assertTrue('3.2702' in result[9])  # SD
        self.assertTrue('t</i>(29) = 1.92' in result[11])
        self.assertTrue('p</i> = 0.065' in result[11])

        # Wilcoxon signed-rank test for non-normal interval variable
        result = data.explore_variable('b', 0, 20.0)
        self.assertTrue('T</i> = 203' in result[11])
        self.assertTrue('p</i> = 0.551' in result[11])

        # Ord variable
        data.data_measlevs['a'] = 'ord'
        result = data.explore_variable('a', 1, 2.0)
        self.assertTrue('N of valid cases: 30' in result[2])
        self.assertTrue('N of missing cases: 0' in result[2])
        self.assertTrue('<td>Maximum</td>      <td>9.9810</td>' in result[4])
        self.assertTrue('<td>Upper quartile</td>      <td>4.3875</td>' in result[4])
        self.assertTrue('<td>Median</td>      <td>2.8545</td>' in result[4])
        self.assertTrue('<td>Lower quartile</td>      <td>1.4190</td>' in result[4])
        self.assertTrue('<td>Minimum</td>      <td>-2.8030</td>' in result[4])

        # Wilcoxon signed-rank test
        self.assertTrue('T</i> = 145' in result[9])
        self.assertTrue('p</i> = 0.074' in result[9])
        data.data_measlevs['a'] = 'int'

    def test_explore_variable_pairs(self):
        """Test explore variable pairs"""

        # Int variables
        result = data.explore_variable_pair('a', 'b')
        self.assertTrue('N of valid pairs: 30' in result[1])
        self.assertTrue('N of missing pairs: 0' in result[1])
        self.assertTrue('-0.141' in result[5])
        self.assertTrue('[-0.477, 0.231]' in result[6])
        self.assertTrue("Pearson's correlation: <i>r</i>(28) = -0.141, <i>p</i> = 0.456" in result[7])
        self.assertTrue('y = -21.811x + 300.505' in result[3])
        self.assertTrue('-0.363' in result[5])
        self.assertTrue('[-0.640, -0.003]' in result[6])
        self.assertTrue("Spearman's rank-order correlation: <i>r<sub>s</sub></i>(28) = -0.363, <i>p</i> = 0.048" in result[7])

        # Ord variables
        data.data_measlevs['a'] = 'ord'
        data.data_measlevs['b'] = 'ord'
        result = data.explore_variable_pair('a', 'b')
        self.assertTrue('-0.363' in result[4])
        self.assertTrue('[-0.640, -0.003]' in result[5])
        self.assertTrue("Spearman's rank-order correlation: <i>r<sub>s</sub></i>(28) = -0.363, <i>p</i> = 0.048" in result[6])
        data.data_measlevs['a'] = 'int'
        data.data_measlevs['b'] = 'int'

        # Nom variables
        result = data.explore_variable_pair('c', 'd')
        self.assertTrue('N of valid pairs: 30' in result[1])
        self.assertTrue('N of missing pairs: 0' in result[1])
        # Cramer's V
        self.assertTrue('<sub>c</sub></i> = 0.372' in result[4])
        # Chi-square
        self.assertTrue('(4, <i>N</i> = 30) = 8.312' in result[6])
        self.assertTrue('<i>p</i> = 0.081' in result[6])

    def test_compare_variables(self):
        """Test compare variables"""

        # 2 Int variables
        result = data.compare_variables(['a', 'e'])
        self.assertTrue('N of valid cases: 30' in result[1])
        self.assertTrue('N of missing cases: 0' in result[1])
        self.assertTrue('<td>3.1438</td>      <td>3.0502</td>' in result[3])
        self.assertTrue('<i>W</i> = 0.954, <i>p</i> = 0.215' in result[7])
        self.assertTrue('<i>t</i>(29) = 0.11, <i>p</i> = 0.913' in result[7])

        # 2 Int variables - non-normal
        result = data.compare_variables(['e', 'f'])
        self.assertTrue('<i>W</i> = 0.915, <i>p</i> = 0.019' in result[7])
        self.assertTrue('<i>T</i> = 110, <i>p</i> = 0.012' in result[7])

        # 3 Int variables
        result = data.compare_variables(['a', 'e', 'g'])
        self.assertTrue('<td>3.1438</td>      <td>3.0502</td>      <td>5.7295</td>' in result[3])
        self.assertTrue('a: <i>W</i> = 0.959, <i>p</i> = 0.287' in result[7])
        self.assertTrue('e: <i>W</i> = 0.966, <i>p</i> = 0.435' in result[7])
        self.assertTrue('g: <i>W</i> = 0.946, <i>p</i> = 0.133' in result[7])
        self.assertTrue('sphericity: <i>W</i> = 0.975, <i>p</i> = 0.703' in result[7])
        self.assertTrue('<i>F</i>(2, 58) = 6.17, <i>p</i> = 0.004' in result[7])
        self.assertTrue('0.11, <i>p</i> = 0.913' in result[7])  # TODO keep the order of the variables, and have a fixed sign
        self.assertTrue('3.17, <i>p</i> = 0.011' in result[7])
        self.assertTrue('2.88, <i>p</i> = 0.015' in result[7])

        # 3 Int variables, sphericity violated
        result = data.compare_variables(['a', 'e', 'h'])
        self.assertTrue('<td>3.1438</td>      <td>3.0502</td>      <td>6.5786</td>' in result[3])
        self.assertTrue('a: <i>W</i> = 0.959, <i>p</i> = 0.287' in result[7])
        self.assertTrue('e: <i>W</i> = 0.966, <i>p</i> = 0.435' in result[7])
        self.assertTrue('h: <i>W</i> = 0.98, <i>p</i> = 0.824' in result[7])
        self.assertTrue('sphericity: <i>W</i> = 0.793, <i>p</i> = 0.039' in result[7])
        self.assertTrue('<i>F</i>(1.66, 48) = 6.16, <i>p</i> = 0.007' in result[7])
        self.assertTrue('0.11, <i>p</i> = 0.913' in result[7])  # TODO keep the order of the variables, and have a fixed sign
        self.assertTrue('2.68, <i>p</i> = 0.024' in result[7])
        self.assertTrue('2.81, <i>p</i> = 0.026' in result[7])

        # 3 Int variables, non-normal
        result = data.compare_variables(['a', 'e', 'f'])
        self.assertTrue('<td>3.1438</td>      <td>3.0502</td>      <td>5.3681</td>' in result[3])
        self.assertTrue('a: <i>W</i> = 0.959, <i>p</i> = 0.287' in result[7])
        self.assertTrue('e: <i>W</i> = 0.966, <i>p</i> = 0.435' in result[7])
        self.assertTrue('f: <i>W</i> = 0.818, <i>p</i> &lt; 0.001' in result[7])
        self.assertTrue('&chi;<sup>2</sup>(2, <i>N</i> = 30) = 6.47, <i>p</i> = 0.039' in result[7])

        # 2 Ord variables
        data.data_measlevs['a'] = 'ord'
        data.data_measlevs['e'] = 'ord'
        data.data_measlevs['f'] = 'ord'
        result = data.compare_variables(['e', 'f'])
        self.assertTrue('<td>2.3895</td>      <td>4.2275</td>' in result[3])
        self.assertTrue('<i>T</i> = 110, <i>p</i> = 0.012' in result[6])

        # 3 Ord variables
        result = data.compare_variables(['a', 'e', 'f'])
        self.assertTrue('<td>2.8545</td>      <td>2.3895</td>      <td>4.2275</td>' in result[3])
        self.assertTrue('&chi;<sup>2</sup>(2, <i>N</i> = 30) = 6.47, <i>p</i> = 0.039' in result[6])
        data.data_measlevs['a'] = 'int'
        data.data_measlevs['e'] = 'int'
        data.data_measlevs['f'] = 'int'

        # 2 Nom variables
        result = data.compare_variables(['i', 'j'])
        # TODO on Linux the row labels are 0.0 and 1.0 instead of 0 and 1
        self.assertTrue('<td>0.0</td>      <td>4</td>      <td>9</td>    </tr>    <tr>      <td>1.0</td>      <td>9</td>' in result[3])
        self.assertTrue('&chi;<sup>2</sup>(1, <i>N</i> = 30) = 0.0556, <i>p</i> = 0.814' in result[5])

        # 3 Nom variables
        result = data.compare_variables(['i', 'j', 'k'])
        self.assertTrue('<i>Q</i>(2, <i>N</i> = 30) = 0.783, <i>p</i> = 0.676' in result[7])

    def test_compare_groups(self):
        """Test compare groups"""

        # 2 Int groups
        result = data.compare_groups('l', ['m'])
        self.assertTrue('<td>2.5316</td>      <td>4.5759</td>' in result[3])
        self.assertTrue('(m: 1.0): <i>W</i> = 0.959, <i>p</i> = 0.683' in result[7])
        self.assertTrue('(m: 2.0): <i>W</i> = 0.984, <i>p</i> = 0.991' in result[7])
        self.assertTrue('<i>W</i> = 0.305, <i>p</i> = 0.585' in result[7])
        self.assertTrue('-2.0443, 95% confidence interval [-4.2157, 0.1272]' in result[7])
        self.assertTrue('<i>t</i>(28) = -1.93, <i>p</i> = 0.064' in result[7])

        # Non-normal group
        result = data.compare_groups('o', ['m'])
        self.assertTrue('(m: 2.0): <i>W</i> = 0.808, <i>p</i> = 0.005' in result[7])
        self.assertTrue('<i>U</i> = 51, <i>p</i> = 0.011' in result[7])

        # Heteroscedastic groups
        result = data.compare_groups('p', ['m'])
        self.assertTrue('<i>t</i>(25.3) = 0.119, <i>p</i> = 0.907' in result[7])


        # TODO single case vs. group

        # 3 Int groups
        result = data.compare_groups('r', ['q'])
        self.assertTrue('<td>3.2869</td>      <td>5.0400</td>      <td>7.2412</td>' in result[3])
        self.assertTrue('<i>W</i> = 0.675, <i>p</i> = 0.517' in result[7])  # TODO this might be incorrect
        self.assertTrue('<i>F</i>(2, 27) = 4, <i>p</i> = 0.030' in result[7])
        self.assertTrue('&omega;<sup>2</sup> = 0.167' in result[8])
        # TODO post-hoc

        # 3 Int groups with assumption violation
        result = data.compare_groups('o', ['q'])
        self.assertTrue('&chi;<sup>2</sup>(2, <i>N</i> = 30) = 8.37, <i>p</i> = 0.015' in result[7])

        # 2 Ord groups
        data.data_measlevs['o'] = 'ord'
        result = data.compare_groups('o', ['m'])
        self.assertTrue('<i>U</i> = 51, <i>p</i> = 0.011' in result[6])

        # 3 Ord groups
        data.data_measlevs['o'] = 'ord'
        result = data.compare_groups('o', ['q'])
        self.assertTrue('&chi;<sup>2</sup>(2, <i>N</i> = 30) = 8.37, <i>p</i> = 0.015' in result[6])
        data.data_measlevs['o'] = 'int'

        # 2 Nom groups
        result = data.compare_groups('i', ['j'])
        self.assertTrue('&phi;<i><sub>c</sub></i> = 0.154' in result[3])  # TODO validate
        self.assertTrue('&chi;<sup>2</sup></i>(1, <i>N</i> = 30) = 0.710, <i>p</i> = 0.399' in result[5])  # TODO validate

        # 3 Nom groups
        result = data.compare_groups('i', ['c'])
        self.assertTrue('&phi;<i><sub>c</sub></i> = 0.009' in result[3])  # TODO validate
        self.assertTrue('&chi;<sup>2</sup></i>(2, <i>N</i> = 30) = 0.002, <i>p</i> = 0.999' in result[5])  # TODO validate

        # 3 × 3 Int groups
        result = data.compare_groups('a', ['c', 'd'])
        self.assertTrue('<td>Mean</td>      <td>1.0695</td>      <td>1.8439</td>      <td>2.3693</td>' in result[3])
        self.assertTrue('<td>Standard deviation</td>      <td>2.7005</td>      <td>2.0891</td>      <td>4.2610</td>' in result[3])
        self.assertTrue('<td>Maximum</td>      <td>4.4130</td>      <td>4.7890</td>      <td>9.1600</td>' in result[3])
        self.assertTrue('<td>Upper quartile</td>      <td>3.0000</td>      <td>3.0213</td>      <td>4.4028</td>' in result[3])
        self.assertTrue('<td>Median</td>      <td>1.3340</td>      <td>2.4590</td>      <td>0.9015</td>' in result[3])
        self.assertTrue('<td>Lower quartile</td>      <td>-0.5965</td>      <td>0.8870</td>      <td>-1.1320</td>' in result[3])
        self.assertTrue('<td>Minimum</td>      <td>-2.8030</td>      <td>-2.2890</td>      <td>-1.4860</td>' in result[3])
        # TODO the two main effefcts differ from the SPSS result, see issue #91
        self.assertTrue('<i>F</i>(2, 21) = 2.35, <i>p</i> = 0.120' in result[7])
        self.assertTrue('<i>F</i>(2, 21) = 0.185, <i>p</i> = 0.832' in result[7])
        self.assertTrue('<i>F</i>(4, 21) = 1.15, <i>p</i> = 0.363' in result[7])

    def test_single_case(self):

        # Test for the slope stat
        data = cs.CogStatData(data='''group	slope	slope_SE
Patient	0.247	0.069
Control	0.492	0.106
Control	0.559	0.108
Control	0.63	0.116
Control	0.627	0.065
Control	0.674	0.105
Control	0.538	0.107''')
        result = data.compare_groups('slope', ['group'], ['slope_SE'], 25)
        self.assertTrue('Test d.2: <i>t</i>(42.1) = -4.21, <i>p</i> &lt; 0.001' in result[7])
        result = data.compare_groups('slope', ['group'])
        self.assertTrue('<i>t</i>(5) = -5.05, <i>p</i> = 0.004' in result[7])

if __name__ == '__main__':
    unittest.main()
