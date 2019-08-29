from scipy import stats

class BayesianUpdate:
    prior = 1

    def __init__(self, goodg, badg, goodd, badd):
        self.good_gap = stats.gaussian_kde(goodg)
        self.bad_gap = stats.gaussian_kde(badg)
        self.good_duration = stats.gaussian_kde(goodd)
        self.bad_duration = stats.gaussian_kde(badd)
        self.prior_list = []
        self.durations = []
        self.gaps = []

    def predict(self, gap, duration):

        self.prior = (.5*(self.good_gap(gap)/self.bad_gap(gap))) * \
                     (.5*(self.good_duration(duration)/self.bad_duration(duration))) * self.prior
        self.prior_list.append(self.prior)
        self.durations.append(duration)
        self.gaps.append(gap)
        return self.evaluate()

    def evaluate(self):

        if self.prior > 1:
            return True
        else:
            return False

    def setPrior(self, prior):
        """
        Sets prior
        :param prior: (Float) prior
        :return: None
        """
        self.prior = prior
        self.prior_list= []
        self.durations = []

    def getPrior(self):
        """
        Returns collected log of priors
        :return: (list) log of priors
        """
        return self.prior_list

    def getDurations(self):
        """
        Returns collected log of durations
        :return: (list) log of durations
        """
        return self.durations

    def getGaps(self):
        return self.gaps


