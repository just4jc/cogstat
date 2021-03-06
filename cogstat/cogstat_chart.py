"""
This module contains functions for creating charts.
"""

import os
import gettext
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import textwrap

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pylab

try:
    from statsmodels.graphics.mosaicplot import mosaic
except:
    pass

from . import cogstat_config as csc
from . import cogstat_stat as cs_stat

matplotlib.pylab.rcParams['figure.figsize'] = csc.fig_size_x, csc.fig_size_y

### Set matplotlib styles ###
# Set the styles
if csc.theme not in plt.style.available:
    csc.theme = sorted(plt.style.available)[0]
    csc.save(['graph', 'theme'], csc.theme)
plt.style.use(csc.theme)

#print plt.style.available
#style_num = 15
#print plt.style.available[style_num]
#plt.style.use(plt.style.available[style_num])
theme_colors = [col['color'] for col in list(plt.rcParams['axes.prop_cycle'])]
#print theme_colors
# this is a workaround, as 'C0' notation does not seem to work

# Overwrite style parameters when needed
# https://matplotlib.org/tutorials/introductory/customizing.html
# Some dashed and dotted axes styles (which are simply line styles) are hard to differentiate, so we overwrite the style
#print matplotlib.rcParams['lines.dashed_pattern'], matplotlib.rcParams['lines.dotted_pattern']
matplotlib.rcParams['lines.dashed_pattern'] = [6.0, 6.0]
matplotlib.rcParams['lines.dotted_pattern'] = [1.0, 3.0]
#print matplotlib.rcParams['axes.spines.left']
#print matplotlib.rcParams['font.size'], matplotlib.rcParams['font.serif'], matplotlib.rcParams['font.sans-serif']
#print matplotlib.rcParams['axes.titlesize'], matplotlib.rcParams['axes.labelsize']
matplotlib.rcParams['axes.titlesize'] = csc.graph_font_size # title of the charts
matplotlib.rcParams['axes.labelsize'] = csc.graph_font_size # labels of the axis
#print matplotlib.rcParams['xtick.labelsize'], matplotlib.rcParams['ytick.labelsize']
#print matplotlib.rcParams['figure.facecolor']
#matplotlib.rcParams['figure.facecolor'] = csc.bg_col
# Make sure that the axes are visible
#print matplotlib.rcParams['axes.facecolor'], matplotlib.rcParams['axes.edgecolor']
if matplotlib.colors.to_rgba(matplotlib.rcParams['figure.facecolor']) == matplotlib.colors.to_rgba(matplotlib.rcParams['axes.edgecolor']):
    #print matplotlib.colors.to_rgba(matplotlib.rcParams['axes.edgecolor'])
    matplotlib.rcParams['axes.edgecolor'] = 'w' if matplotlib.colors.to_rgba(matplotlib.rcParams['axes.edgecolor'])==(0, 0, 0, 0) else 'k'

t = gettext.translation('cogstat', os.path.dirname(os.path.abspath(__file__))+'/locale/', [csc.language], fallback=True)
_ = t.gettext

# matplotlib does not support rtl Unicode yet (http://matplotlib.org/devel/MEP/MEP14.html),
# so we have to handle rtl text on matplotlib plots
rtl_lang = True if csc.language in ['he', 'fa', 'ar'] else False
if rtl_lang:
    from bidi.algorithm import get_display
    _plt = lambda text: get_display(t.gettext(text))
else:
    _plt = t.gettext

def _wrap_labels(labels):
    """
    labels: list of strings
            or list of lists of single strings
    """
    label_n = len(labels)
    max_chars_in_row = 55
        # TODO need a more precise method; should depend on font size and graph size;
        # but cannot be a very precise method unless the font is fixed width
    if isinstance(labels[0], (list, tuple)):
        wrapped_labels = [textwrap.fill(' : '.join(map(str, label)), max(5, max_chars_in_row/label_n)) for label in
                          labels]
    else:
        wrapped_labels = [textwrap.fill(str(label), max(5, max_chars_in_row / label_n)) for label in
                          labels]
        # the width should not be smaller than a min value, here 5
        # use the unicode() to convert potentially numerical labels
        # TODO maybe for many lables use rotation, e.g., http://stackoverflow.com/questions/3464359/is-it-possible-to-wrap-the-text-of-xticks-in-matplotlib-in-python
    return wrapped_labels


def _set_axis_measurement_level (ax, x_measurement_level, y_measurement_level):
    """
    Set the axes types of the graph acording to the measurement levels of the variables.
    :param ax: ax object
    :param x_measurement_type: str 'nom', 'ord' or 'int'
    :param y_measurement_type: str 'nom', 'ord' or 'int'
    :return: nothing, the ax object is modified in place
    """

    # Switch off top and right axes
    ax.tick_params(top=False, right=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Set the style of the bottom and left spines according to the measurement levels
    measurement_level_to_line_styles = {'int': 'solid', 'ord': 'dashed', 'nom': 'dotted'}
    ax.spines['bottom'].set_linestyle(measurement_level_to_line_styles[x_measurement_level])
    ax.spines['left'].set_linestyle(measurement_level_to_line_styles[y_measurement_level])

####################################
### Charts for Explore variables ###
####################################

def create_variable_raw_chart(pdf, data_measlevs, var_name, data):
    """

    :param pdf:
    :param data_measlevs:
    :param var_name:
    :param data:
    :return:
    """
    if data_measlevs[var_name] == 'ord':
        data_value = pdf[var_name].dropna()
        data = pd.Series(stats.rankdata(data_value))

    if data_measlevs[var_name] in ['int', 'ord', 'unk']:
        fig = plt.figure(figsize=(csc.fig_size_x, csc.fig_size_y * 0.25))
        ax = plt.gca()
        # Add individual data
        plt.scatter(data, np.random.random(size=len(data)), color=theme_colors[0], marker='o')
        ax.axes.set_ylim([-1.5, 2.5])
        fig.subplots_adjust(top=0.85, bottom=0.3)
        # Add labels
        if data_measlevs[var_name] == 'ord':
            plt.title(_plt('Rank of the raw data'))
            plt.xlabel(_('Rank of %s') % var_name)
        else:
            plt.title(_plt('Raw data'))
            plt.xlabel(var_name)
        ax.axes.get_yaxis().set_visible(False)
        if data_measlevs[var_name] == 'ord':
            ax.tick_params(top=False, right=False)
            # Create new tick labels, with the rank and the value of the corresponding rank
            ax.set_xticklabels(['%i\n(%s)' % (i, sorted(data_value)[int(i)-1])
                                if i-1 in range(len(data_value)) else '%i' % i for i in ax.get_xticks()])
            _set_axis_measurement_level(ax, 'ord', 'nom')
    elif data_measlevs[var_name] in ['nom']:
        # For nominal variables the histogram is a frequency graph
        plt.figure()
        values = list(set(pdf[var_name]))
        freqs = [list(pdf[var_name]).count(i) for i in values]
        locs = np.arange(len(values))
        plt.title(_plt('Histogram'))
        plt.bar(locs, freqs, 0.9, color=theme_colors[0])
        plt.xticks(locs+0.9/2., _wrap_labels(values))
        plt.ylabel(_plt('Frequency'))
        ax = plt.gca()
        _set_axis_measurement_level(ax, 'nom', 'int')

    return plt.gcf()


def create_histogram_chart(pdf, data_measlevs, var_name):
    """Histogram with individual data and boxplot

    arguments:
    var_name (str): name of the variable
    """
    chart_result = ''
    suptitle_text = None
    max_length = 10  # maximum printing length of an item # TODO print ... if it's exceeded
    data = pdf[var_name].dropna()
    if data_measlevs[var_name] == 'ord':
        data_value = pdf[var_name].dropna()  # The original values of the data
        data = pd.Series(stats.rankdata(data_value))  # The ranks of the data
    if data_measlevs[var_name] in ['int', 'ord', 'unk']:
        categories_n = len(set(data))
        if categories_n < 10:
            freq, edge = np.histogram(data, bins=categories_n)
        else:
            freq, edge = np.histogram(data)
        #        text_result = _(u'Edge\tFreq\n')
        #        text_result += u''.join([u'%.2f\t%s\n'%(edge[j], freq[j]) for j in range(len(freq))])

        # Prepare the frequencies for the plot
        val_count = data.value_counts()
        if max(val_count) > 1:
            suptitle_text = _plt('Largest tick on the x axes displays %d cases.') % max(val_count)
        val_count = (val_count * (max(freq) / max(val_count))) / 20.0

        # Upper part with histogram and individual data
        plt.figure()
        ax_up = plt.axes([0.1, 0.3, 0.8, 0.6])
        plt.hist(data.values, bins=len(edge) - 1, color=theme_colors[0])
        # .values needed, otherwise it gives error if the first case is missing data
        # Add individual data
        plt.errorbar(np.array(val_count.index), np.zeros(val_count.shape),
                     yerr=[np.zeros(val_count.shape), val_count.values],
                     fmt='k|', capsize=0, linewidth=2)
        # plt.plot(np.array(val_count.index), np.zeros(val_count.shape), 'k|', markersize=10, markeredgewidth=1.5)
        # Add labels
        if data_measlevs[var_name] == 'ord':
            plt.title(_plt('Histogram of rank data with individual data and boxplot'))
        else:
            plt.title(_plt('Histogram with individual data and boxplot'))
        if suptitle_text:
            plt.suptitle(suptitle_text, x=0.9, y=0.025, horizontalalignment='right', fontsize=10)
        plt.gca().axes.get_xaxis().set_visible(False)
        plt.ylabel(_plt('Frequency'))
        # Lower part showing the boxplot
        ax_low = plt.axes([0.1, 0.1, 0.8, 0.2], sharex=ax_up)
        box1 = plt.boxplot(data.values, vert=0,
                           whis='range')  # .values needed, otherwise error when the first case is missing data
        plt.gca().axes.get_yaxis().set_visible(False)
        if data_measlevs[var_name] == 'ord':
            plt.xlabel(_('Rank of %s') % var_name)
        else:
            plt.xlabel(var_name)
        plt.setp(box1['boxes'], color=theme_colors[0])
        plt.setp(box1['whiskers'], color=theme_colors[0])
        plt.setp(box1['caps'], color=theme_colors[0])
        plt.setp(box1['medians'], color=theme_colors[0])
        plt.setp(box1['fliers'], color=theme_colors[0])
        if data_measlevs[var_name] == 'ord':
            ax_low.tick_params(top=False, right=False)
            # Create new tick labels, with the rank and the value of the corresponding rank
            ax_low.set_xticklabels(['%i\n(%s)' % (i, sorted(data_value)[int(i - 1)])
                                    if i - 1 in range(len(data_value)) else '%i' % i for i in ax_low.get_xticks()])
            _set_axis_measurement_level(ax_low, 'ord', 'int')
        chart_result = plt.gcf()
    # For nominal variables the histogram is a frequency graph, which has already been displayed in the Raw data, so it
    # is not repeated here
    return chart_result


def create_normality_chart(data, var_name):
    """

    :param data:
    :param var_name:
    :return:
    """
    suptitle_text = None

    # Prepare the frequencies for the plot
    val_count = data.value_counts()
    plt.figure()  # Otherwise the next plt.hist will modify the actual (previously created) graph
    n, bins, patches = plt.hist(data.values, normed=True, color=theme_colors[0])
    if max(val_count) > 1:
        suptitle_text = _plt('Largest tick on the x axes displays %d cases.') % max(val_count)
    val_count = (val_count * (max(n) / max(val_count))) / 20.0

    # Graph
    plt.figure()
    n, bins, patches = plt.hist(data.values, normed=True, color=theme_colors[0])
    plt.plot(bins, matplotlib.pylab.normpdf(bins, np.mean(data), np.std(data)), color=theme_colors[1], linestyle='--',
             linewidth=3)
    plt.title(_plt('Histogram with individual data and normal distribution'))
    if suptitle_text:
        plt.suptitle(suptitle_text, x=0.9, y=0.025, horizontalalignment='right', fontsize=10)
    plt.errorbar(np.array(val_count.index), np.zeros(val_count.shape),
                 yerr=[np.zeros(val_count.shape), val_count.values],
                 fmt='k|', capsize=0, linewidth=2)
    #    plt.plot(data, np.zeros(data.shape), 'k+', ms=10, mew=1.5)
    # individual data
    plt.xlabel(var_name)
    plt.ylabel(_('Normalized relative frequency'))

    # percent on y axes http://matplotlib.org/examples/pylab_examples/histogram_percent_demo.html
    def to_percent(y, position):
        s = str(100 * y)
        return s + r'$\%$' if matplotlib.rcParams['text.usetex'] is True else s + '%'

    from matplotlib.ticker import FuncFormatter
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))

    normality_histogram = plt.gcf()

    # QQ plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    sm.graphics.qqplot(data, line='s', ax=ax)  # TODO set the color
    plt.title(_plt('Quantile-quantile plot'))
    qq_plot = plt.gcf()

    return normality_histogram, qq_plot


def create_variable_population_chart(data, var_name, ci):
    plt.figure(figsize=(csc.fig_size_x, csc.fig_size_y * 0.35))
    plt.barh([1], [data.mean()], xerr=[ci], color=theme_colors[0], ecolor='black')
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel(var_name)  # TODO not visible yet, maybe matplotlib bug, cannot handle figsize consistently
    plt.title(_plt('Mean value with 95% confidence interval'))
    return plt.gcf()


def create_variable_popuplation_chart_2(data, var_name):
    # TODO merge with create_variable_popuplation_chart
    plt.figure(figsize=(csc.fig_size_x, csc.fig_size_y * 0.35))
    plt.barh([1], [np.median(data)], color=theme_colors[0], ecolor='black')  # TODO error bar
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel(var_name)  # TODO not visible yet, maybe matplotlib bug, cannot handle figsize consistently
    plt.title(_plt('Median value'))
    return plt.gcf()


#########################################
### Charts for Explore variable pairs ###
#########################################


def create_variable_pair_chart(data, meas_lev, slope, intercept, x, y, data_frame, raw_data=False):
    """

    :param data:
    :param meas_lev:
    :param slope:
    :param intercept:
    :param x:
    :param y:
    :param data_frame:
    :param raw_data:
    :return:
    """
    if meas_lev in ['int', 'ord']:
        suptitle_text = None

        # Prepare the frequencies for the plot
        xy = [(i, j) for i, j in zip(data.iloc[:, 0], data.iloc[:, 1])]
        xy_set_freq = [[element[0], element[1], xy.count(element)] for element in set(xy)]
        [xvalues, yvalues, xy_freq] = list(zip(*xy_set_freq))
        xy_freq = np.array(xy_freq, dtype=float)
        max_freq = max(xy_freq)
        if max_freq>10:
            xy_freq = (xy_freq-1)/((max_freq-1)/9.0)+1
            # largest dot shouldn't be larger than 10 × of the default size
            # smallest dot is 1 unit size
            suptitle_text = _plt('Largest sign on the graph displays %d cases.') % max_freq
        xy_freq *= 20.0

        # Draw figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        if meas_lev == 'int':
            # Display the data
            ax.scatter(xvalues, yvalues, xy_freq, color=theme_colors[0], marker='o')
            # Display the linear fit for the plot
            if not raw_data:
                fit_x = [min(data.iloc[:, 0]), max(data.iloc[:, 0])]
                fit_y = [slope*i+intercept for i in fit_x]
                ax.plot(fit_x, fit_y, color=theme_colors[0])
            # Set the labels
            plt.title(_plt('Scatterplot of the variables'))
            ax.set_xlabel(x)
            ax.set_ylabel(y)
        elif meas_lev == 'ord':
            # Display the data
            ax.scatter(stats.rankdata(xvalues), stats.rankdata(yvalues),
                       xy_freq, color=theme_colors[0], marker='o')
            ax.set_xlim(0, len(xvalues)+1)
            ax.set_ylim(0, len(yvalues)+1)
            ax.tick_params(top=False, right=False)
            # Create new tick labels, with the rank and the value of the corresponding rank
            ax.set_xticklabels(['%i\n(%s)' % (i, sorted(xvalues)[int(i-1)])
                                if i-1 in range(len(xvalues)) else '%i' % i for i in ax.get_xticks()])
            try:
                ax.set_yticklabels(['%i\n(%s)' % (i, sorted(yvalues)[int(i-1)])
                                if i-1 in range(len(yvalues)) else '%i' % i for i in ax.get_yticks()],
                               wrap=True)
            except:  # for matplotlib before 1.5
                ax.set_yticklabels(['%i\n(%s)' % (i, sorted(yvalues)[int(i-1)])
                                if i-1 in range(len(yvalues)) else '%i' % i for i in ax.get_yticks()])
            _set_axis_measurement_level(ax, 'ord', 'ord')
            # Display the labels
            plt.title(_plt('Scatterplot of the rank of the variables'))
            ax.set_xlabel(_plt('Rank of %s') % x)
            ax.set_ylabel(_plt('Rank of %s') % y)
        if suptitle_text:
            plt.suptitle(suptitle_text, x=0.9, y=0.025, horizontalalignment='right', fontsize=10)
        graph = plt.gcf()
    elif meas_lev in ['nom']:
        cont_table_data = pd.crosstab(data_frame[y], data_frame[x])#, rownames = [x], colnames = [y]) # TODO use data instead?

        #mosaic(data_frame, [x, y])  # Previous version
        if 0 in cont_table_data.values:
            fig, rects = mosaic(cont_table_data.unstack()+1e-9, label_rotation=[0.0, 90.0])
            # this is a workaround for mosaic limitation, which cannot draw cells with 0 frequency
            # see https://github.com/cogstat/cogstat/issues/1
        else:
            fig, rects = mosaic(cont_table_data.unstack(), label_rotation=[0.0, 90.0])
        fig.set_facecolor(csc.bg_col)
        ax = plt.subplot(111)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        plt.title(_plt('Mosaic plot of the variables'))
        _set_axis_measurement_level(ax, 'nom', 'nom')
        try:
            graph = plt.gcf()
        except:  # in some cases mosaic cannot be drawn  # TODO how to solve this?
            print('Error, the mosaic plot can not be drawn with those data.')

    return graph


#########################################
### Charts for Repeated measures vars ###
#########################################


def create_repeated_measures_sample_chart(data, var_names, meas_level, data_frame, raw_data=False):
    """
    :param data:
    :param var_names:
    :param meas_level:
    :param data_frame:
    :param raw_data:
    :return:
    """
    graph = None
    if meas_level in ['int', 'ord', 'unk']:
        # TODO is it OK for ordinals?
        variables = np.array(data)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        if raw_data:
            plt.title(_plt('Individual data of the variables'))
        else:
            plt.title(_plt('Boxplots and individual data of the variables'))
        # Display individual data
        for i in range(len(variables.transpose()) - 1):  # for all pairs
            # Prepare the frequencies for the plot
            xy = [(x, y) for x, y in zip(variables.transpose()[i], variables.transpose()[i + 1])]
            xy_set_freq = [[element[0], element[1], xy.count(element)] for element in set(xy)]
            [xvalues, yvalues, xy_freq] = list(zip(*xy_set_freq))
            xy_freq = np.array(xy_freq, dtype=float)
            max_freq = max(xy_freq)
            print(max_freq)
            if max_freq > 10:
                xy_freq = (xy_freq - 1) / ((max_freq - 1) / 9.0) + 1
                # largest dot shouldn't be larger than 10 × of the default size
                # smallest dot is 1 unit size
                # TODO put text to chart
                intro_result = '\n' + _('Thickest line displays %d cases.') % max_freq + '\n'
            for data1, data2, data_freq in zip(xvalues, yvalues, xy_freq):
                plt.plot([i + 1, i + 2], [data1, data2], '-', color=csc.ind_line_col, lw=data_freq)

        # Display boxplots
        if not raw_data:
            box1 = ax.boxplot(variables, whis='range')
            # ['medians', 'fliers', 'whiskers', 'boxes', 'caps']
            plt.setp(box1['boxes'], color=theme_colors[0])
            plt.setp(box1['whiskers'], color=theme_colors[0])
            plt.setp(box1['caps'], color=theme_colors[0])
            plt.setp(box1['medians'], color=theme_colors[0])
            plt.setp(box1['fliers'], color=theme_colors[0])
        else:
            ax.set_xlim(0.5, len(var_names) + 0.5)
        plt.xticks(list(range(1, len(var_names) + 1)), _wrap_labels(var_names))
        plt.ylabel(_('Value'))
        graph = plt.gcf()
    elif meas_level == 'nom':
        import itertools
        graph = []
        for var_pair in itertools.combinations(var_names, 2):
            # workaround to draw mosaic plots with zero cell, see #1
            # fig, rects = mosaic(data_frame, [var_pair[1], var_pair[0]]) # previous version
            ct = pd.crosstab(data_frame[var_pair[0]], data_frame[var_pair[1]]).sort_index(axis='index',
                                                                                          ascending=False) \
                .unstack()
            if 0 in ct.values:
                fig, rects = mosaic(ct + 1e-9, label_rotation=[0.0, 90.0])
            else:
                fig, rects = mosaic(ct, label_rotation=[0.0, 90.0])
            fig.set_facecolor(csc.bg_col)
            ax = plt.subplot(111)
            ax.set_xlabel(var_pair[1])
            ax.set_ylabel(var_pair[0])
            plt.title(_plt('Mosaic plot of the variables'))
            _set_axis_measurement_level(ax, 'nom', 'nom')
            try:
                graph.append(plt.gcf())
            except:  # in some cases mosaic cannot be drawn  # TODO how to solve this?
                intro_result = '\n' + _('Sorry, the mosaic plot can not be drawn with those data.')
    return graph


def create_repeated_measures_population_chart(data, var_names, meas_level, data_frame):
    """Draw means with CI for int vars, and medians for ord vars.
    """
    graph = None
    if meas_level in ['int', 'unk']:
        # ord is excluded at the moment
        fig = plt.figure()
        ax = fig.add_subplot(111)

        if meas_level in ['int', 'unk']:
            plt.title(_plt('Means and 95% confidence intervals for the variables'))
            means = np.mean(data)
            cis, cils, cihs = cs_stat.confidence_interval_t(data, ci_only=False)
            ax.bar(list(range(len(data.columns))), means, 0.5, yerr=cis, align='center',
                   color=theme_colors[0], ecolor='0')

        elif meas_level in ['ord']:
            plt.title(_plt('Medians for the variables'))
            medians = np.median(data)
            ax.bar(list(range(len(data.columns))), medians, 0.5, align='center',
                   color=theme_colors[0], ecolor='0')
        plt.xticks(list(range(len(var_names))), _wrap_labels(var_names))
        plt.ylabel(_plt('Value'))
        graph = plt.gcf()
    return graph


#################################
### Charts for Compare groups ###
#################################


def create_compare_groups_sample_chart(data_frame, meas_level, var_names, groups, group_levels, raw_data_only=False):
    """Display the boxplot of the groups with individual data or the mosaic plot

    :param data_frame: The data frame
    :param meas_level:
    :param var_names:
    :param groups: List of names of the grouping variables
    :param group_levels: List of lists or tuples with group levels (1 grouping variable) or group level combinations
    (more than 1 grouping variables)
    :param raw_data_only: Only the raw data are displayed
    :return:
    """
    if meas_level in ['int', 'ord']:  # TODO 'unk'?
        # TODO is this OK for ordinal?
        # Get the data to display
        # group the raw the data according to the level combinations
        if len(groups) == 1:
            group_levels = [[group_level] for group_level in group_levels]
        variables = [data_frame[var_names[0]][(data_frame[groups] == pd.Series({group: level for group, level in zip(groups, group_level)})).all(axis=1)].dropna() for group_level in group_levels]
        if meas_level == 'ord':  # Calculate the rank information # FIXME is there a more efficient way to do this?
            index_ranks = dict(list(zip(pd.concat(variables).index, stats.rankdata(pd.concat(variables)))))
            variables_value = pd.concat(variables).values  # original values
            for var_i in range(len(variables)):  # For all groups
                for i in variables[var_i].index:  # For all values in that group
                    variables[var_i][i] = index_ranks[i]
                    #print i, variables[var_i][i], index_ranks[i]
        # TODO graph: mean, etc.
        #means = [np.mean(self.data_values[self.data_names.index(var_name)]) for var_name in var_names]
        #stds = [np.std(self.data_values[self.data_names.index(var_name)]) for var_name in var_names]
        #rects1 = ax.bar(range(1,len(variables)+1), means, color=theme_colors[0], yerr=stds)
        # Create graph
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # Add boxplot
        if not raw_data_only:
            box1 = ax.boxplot(variables, whis='range')
            plt.setp(box1['boxes'], color=theme_colors[0])
            plt.setp(box1['whiskers'], color=theme_colors[0])
            plt.setp(box1['caps'], color=theme_colors[0])
            plt.setp(box1['medians'], color=theme_colors[0])
            plt.setp(box1['fliers'], color=theme_colors[0])
        # Display individual data
        for var_i in range(len(variables)):
            val_count = variables[var_i].value_counts()
            max_freq = max(val_count)
            if max_freq>10:
                val_count = (val_count-1)/((max_freq-1)/9.0)+1
                # largest dot shouldn't be larger than 10 × of the default size
                # smallest dot is 1 unit size
                plt.suptitle(_plt('Largest individual sign displays %d cases.') % max_freq, x=0.9, y=0.025,
                             horizontalalignment='right', fontsize=10)
            ax.scatter(np.ones(len(val_count))+var_i, val_count.index, val_count.values*5, color='#808080', marker='o')
            #plt.plot(np.ones(len(variables[i]))+i, variables[i], '.', color = '#808080', ms=3) # TODO color should be used from ini file
        # Add labels
        plt.xticks(list(range(1, len(group_levels)+1)), _wrap_labels([' : '.join(map(str, group_level)) for group_level in group_levels]))
        plt.xlabel(' : '.join(groups))
        if meas_level == 'ord':
            plt.ylabel(_('Rank of %s') % var_names[0])
            if raw_data_only:
                plt.title(_plt('Individual data of the rank data of the groups'))
            else:
                plt.title(_plt('Boxplots and individual data of the rank data of the groups'))
            ax.tick_params(top=False, right=False)
            # Create new tick labels, with the rank and the value of the corresponding rank
            try:
                ax.set_yticklabels(['%i\n(%s)' % (i, sorted(variables_value)[int(i)-1])
                                    if i-1 in range(len(variables_value)) else '%i' % i for i in ax.get_yticks()],
                                   wrap=True)
            except:  # for matplotlib before 1.5
                ax.set_yticklabels(['%i\n(%s)' % (i, sorted(variables_value)[int(i)-1])
                                    if i-1 in range(len(variables_value)) else '%i' % i for i in ax.get_yticks()])
            _set_axis_measurement_level(ax, 'nom', 'ord')
        else:
            plt.ylabel(var_names[0])
            if raw_data_only:
                plt.title(_plt('Individual data of the groups'))
            else:
                plt.title(_plt('Boxplots and individual data of the groups'))
            _set_axis_measurement_level(ax, 'nom', 'int')
        graph = fig
    elif meas_level in ['nom']:
        # workaround to draw mosaic plots with zero cell, see #1
        #fig, rects = mosaic(data_frame, [groups[0], var_names[0]])  # previous version
        ct = pd.crosstab(data_frame[var_names[0]], [data_frame[groups[i]] for i in range(len(groups))]).sort_index(axis='index', ascending=False).unstack()
        #print ct
        if 0 in ct.values:
            fig, rects = mosaic(ct+1e-9, label_rotation=[0.0, 90.0])
        else:
            fig, rects = mosaic(ct, label_rotation=[0.0, 90.0])
        fig.set_facecolor(csc.bg_col)
        ax = plt.subplot(111)
        ax.set_xlabel(' : '.join(groups))
        ax.set_ylabel(var_names[0])
        plt.title(_plt('Mosaic plot of the groups'))
        _set_axis_measurement_level(ax, 'nom', 'nom')
        try:
            graph = fig
        except:  # in some cases mosaic cannot be drawn  # TODO how to solve this?
            print('Sorry, the mosaic plot can not be drawn with those data.')
    else:
        graph = None
    return graph


def create_compare_groups_population_chart(data_frame, meas_level, var_names, groups, group_levels):
    """Draw means with CI for int vars, and medians for ord vars.
    """
    graph = None
    #    if len(groups) == 1:
    #        group_levels = [[group_level] for group_level in group_levels]
    if meas_level in ['int', 'unk']:
        # ord is excluded at the moment
        fig = plt.figure()
        ax = fig.add_subplot(111)

        pdf = data_frame.dropna(subset=[var_names[0]])[[var_names[0]] + groups]
        if meas_level in ['int', 'unk']:
            plt.title(_plt('Means and 95% confidence intervals for the groups'))
            means = pdf.groupby(groups, sort=False).aggregate(np.mean)[var_names[0]]
            cis = pdf.groupby(groups, sort=False).aggregate(cs_stat.confidence_interval_t)[var_names[0]]
            ax.bar(list(range(len(means.values))), means.reindex(group_levels), 0.5,
                   yerr=np.array(cis.reindex(group_levels)),
                   align='center', color=theme_colors[0], ecolor='0')
            # pandas series is converted to np.array to be able to handle numeric indexes (group levels)
            _set_axis_measurement_level(ax, 'nom', 'int')
        elif meas_level in ['ord']:
            plt.title(_plt('Medians for the groups'))
            medians = pdf.groupby(groups[0], sort=False).aggregate(np.median)[var_names[0]]
            ax.bar(list(range(len(medians.values))), medians.reindex(group_levels), 0.5, align='center',
                   color=theme_colors[0], ecolor='0')
        if len(groups) == 1:
            group_levels = [[group_level] for group_level in group_levels]
        plt.xticks(list(range(len(group_levels))),
                   _wrap_labels([' : '.join(map(str, group_level)) for group_level in group_levels]))
        plt.xlabel(' : '.join(groups))
        plt.ylabel(var_names[0])
        graph = fig
    return graph
