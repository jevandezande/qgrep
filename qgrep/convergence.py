import numpy as np
from collections import OrderedDict


class Step:
    """
    An object that stores a convergence result
    """
    def __init__(self, params):
        self.__dict__ = dict(params)
        self.params = params

    def __str__(self):
        return ' '.join("{:> 9.2e}".format(value) for key, value in self.params.items())


class Convergence:
    """
    Stores multiple convergence steps
    """
    def __init__(self, steps, criteria, program='orca'):
        self.steps = steps
        self.criteria = criteria
        self.program = program

    def __str__(self):
        if self.program == 'orca':
            header = "      Δ energy  RMS grad  MAX grad  RMS step  MAX Step\n"
        else:
            raise NotImplementedError('Congervence currently only implemented for ORCA')

        line = '-'*54 + '\n'
        out = header + line
        out += ''.join('{:>3}: {}\n'.format(i, step) for i, step in enumerate(self.steps))

        return out + line + '    ' + (' {:> 9.2e}'*len(self.criteria)).format(*self.criteria)

    def plot(self):
        from matplotlib import pyplot as plt

        f, (ax0, ax1) = plt.subplots(1, 2, sharex='col')
        f.suptitle('Convergence', fontsize=16)
        plt.xlabel('Step')
        x = range(len(self.steps))

        ax0.set_yscale('symlog', linthreshy=1e-5)
        ax0.set_title(r'$\Delta$ Energy')
        ax0.plot(x, self.delta_e)

        ax1.set_ylim(0, 1)
        ax1.set_yscale('symlog', linthreshy=1e-6)
        ax1.set_title('Gradient')
        ax1.plot(x, self.rms_grad, 'b-')
        ax1.plot(x, self.max_grad, 'b--')
        ax1.plot(x, self.rms_step, 'r-')
        ax1.plot(x, self.max_step, 'r--')
        # TODO: generalize for more than ORCA
        ax1.plot(x, [self.criteria[1]]*len(self.steps), 'b-.')
        ax1.plot(x, [self.criteria[2]]*len(self.steps), 'b:')
        ax1.plot(x, [self.criteria[3]]*len(self.steps), 'r-.')
        ax1.plot(x, [self.criteria[4]]*len(self.steps), 'r:')

        plt.show()

    @property
    def delta_e(self):
        return np.array([step.delta_e for step in self.steps])

    @property
    def rms_e(self):
        return np.array([step.rms_e for step in self.steps])

    @property
    def max_grad(self):
        return np.array([step.max_grad for step in self.steps])

    @property
    def rms_grad(self):
        return np.array([step.rms_grad for step in self.steps])

    @property
    def max_step(self):
        return np.array([step.max_step for step in self.steps])

    @property
    def rms_step(self):
        return np.array([step.rms_step for step in self.steps])
