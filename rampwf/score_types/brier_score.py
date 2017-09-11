from .base import BaseScoreType
import numpy as np


class BrierScore(BaseScoreType):
    is_lower_the_better = True
    minimum = 0.0
    maximum = 1.0

    def __init__(self, name='brier_score', precision=3):
        self.name = name
        self.precision = precision

    def score_function(self, ground_truths, predictions, valid_indexes=None):
        """A hybrid score.

        It tests the the predicted _probability_ of the second class
        against the true _label index_ (which is 0 if the first label is the
        ground truth, and 1 if it is not, in other words, it is the
        tru probabilty of the second class). Thus we have to override the
        `Base` function here
        """
        if valid_indexes is None:
            valid_indexes = slice(None, None, None)
        y_proba = predictions.y_pred[valid_indexes][:, 1]
        y_true_proba = ground_truths.y_pred_label_index[valid_indexes]
        self.check_y_pred_dimensions(y_true_proba, y_proba)
        return self.__call__(y_true_proba, y_proba)

    def __call__(self, y_true_proba, y_proba):
        return np.mean((y_proba - y_true_proba) ** 2)


class BrierSkillScore(BaseScoreType):
    is_lower_the_better = False
    minimum = -1.0
    maximum = 1.0

    def __init__(self, name='brier_score', precision=3):
        self.name = name
        self.precision = precision

    def score_function(self, ground_truths, predictions, valid_indexes=None):
        """A hybrid score.

        It tests the the predicted _probability_ of the second class
        against the true _label index_ (which is 0 if the first label is the
        ground truth, and 1 if it is not, in other words, it is the
        tru probabilty of the second class). Thus we have to override the
        `Base` function here
        """
        if valid_indexes is None:
            valid_indexes = slice(None, None, None)
        y_proba = predictions.y_pred[valid_indexes][:, 1]
        y_true_proba = ground_truths.y_pred_label_index[valid_indexes]
        self.check_y_pred_dimensions(y_true_proba, y_proba)
        return self.__call__(y_true_proba, y_proba)

    def __call__(self, y_true_proba, y_proba):
        bs = np.mean((y_proba - y_true_proba) ** 2) 
        bs_c = np.mean((y_true_proba.mean() - y_true_proba) ** 2) 
        return 1 - bs / bs_c


class BrierScoreReliability(BaseScoreType):
    is_lower_the_better = True
    minimum = 0.0
    maximum = 1.0

    def __init__(self, name='brier_score', precision=3, bins=np.arange(0, 1.2, 0.1)):
        self.name = name
        self.precision = precision
        self.bins = bins
        self.bin_centers = (bins[1:] - bins[:-1]) * 0.05
        self.bin_centers[self.bin_centers > 1] = 1
        self.bin_centers[self.bin_centers < 0] = 0

    def score_function(self, ground_truths, predictions, valid_indexes=None):
        """A hybrid score.

        It tests the the predicted _probability_ of the second class
        against the true _label index_ (which is 0 if the first label is the
        ground truth, and 1 if it is not, in other words, it is the
        tru probabilty of the second class). Thus we have to override the
        `Base` function here
        """
        if valid_indexes is None:
            valid_indexes = slice(None, None, None)
        y_proba = predictions.y_pred[valid_indexes][:, 1]
        y_true_proba = ground_truths.y_pred_label_index[valid_indexes]
        self.check_y_pred_dimensions(y_true_proba, y_proba)
        return self.__call__(y_true_proba, y_proba)

    def __call__(self, y_true_proba, y_proba):
        pos_obs_freq = np.histogram(y_proba[y_true_proba == 1], bins=self.bins)[0]
        fore_freq = np.histogram(y_proba, bins=self.bins)[0]
        with np.errstate(divide='ignore'):
            pos_obs_rel_freq = pos_obs_freq / fore_freq
            score = 1 / float(y_proba.size) * np.nansum(fore_freq  * (self.bin_centers - pos_obs_rel_freq) ** 2)
        return score


class BrierScoreResolution(BaseScoreType):
    is_lower_the_better = False
    minimum = 0.0
    maximum = 1.0

    def __init__(self, name='brier_score', precision=3, bins=np.arange(0, 1.2, 0.1)):
        self.name = name
        self.precision = precision
        self.bins = bins
        self.bin_centers = (bins[1:] - bins[:-1]) * 0.05
        self.bin_centers[self.bin_centers > 1] = 1
        self.bin_centers[self.bin_centers < 0] = 0

    def score_function(self, ground_truths, predictions, valid_indexes=None):
        """A hybrid score.

        It tests the the predicted _probability_ of the second class
        against the true _label index_ (which is 0 if the first label is the
        ground truth, and 1 if it is not, in other words, it is the
        tru probabilty of the second class). Thus we have to override the
        `Base` function here
        """
        if valid_indexes is None:
            valid_indexes = slice(None, None, None)
        y_proba = predictions.y_pred[valid_indexes][:, 1]
        y_true_proba = ground_truths.y_pred_label_index[valid_indexes]
        self.check_y_pred_dimensions(y_true_proba, y_proba)
        return self.__call__(y_true_proba, y_proba)

    def __call__(self, y_true_proba, y_proba):
        np.seterr(divide="ignore")
        pos_obs_freq = np.histogram(y_proba[y_true_proba == 1], bins=self.bins)[0]
        fore_freq = np.histogram(y_proba, bins=self.bins)[0]
        climo = y_true_proba.mean()
        unc = climo * (1 - climo)
        with np.errstate(divide="ignore"):
            pos_obs_rel_freq = pos_obs_freq / fore_freq
            score = 1 / float(y_proba.size) * np.nansum(fore_freq  * (pos_obs_rel_freq - climo) ** 2)
        return score / unc

