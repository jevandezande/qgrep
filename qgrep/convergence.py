import numpy as np


class Step:
    """
    An object that stores a convergence result
    """
    def __init__(self, delta_e=None, rms_grad=None,
                 max_grad=None, rms_step=None, max_step=None):
        # TODO: institute better checks
        self.delta_e  = delta_e
        self.rms_grad = rms_grad
        self.max_grad = max_grad
        self.rms_step = rms_step
        self.max_step = max_step

    def __str__(self):
        #form = "{energy:} {delta_e:} {rms_grad:} {max_grad:} {rms_step:} {max_step:}"
        form = "{:> 13.10f} {:> 13.10f} {:> 13.10f} {:> 13.10f} {:> 13.10f}"
        return form.format(self.delta_e, self.rms_grad, self.max_grad,
                           self.rms_step, self.max_step)


class Convergence:
    """
    Stores multiple convergence steps
    """
    def __init__(self, steps, criteria):
        self.steps = steps
        self.criteria = criteria

    def __str__(self):
        header = "         Δ energy     RMS grad      MAX grad      RMS step      MAX Step\n"
        return header + '\n'.join('{:>3}: {}'.format(i, step) for i, step in enumerate(self.steps))

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

        #ax3.axis('off')
        #ax4.set_title('Max Grad')
        #ax4.plot(x, self.max_grad)
        #ax5.set_title('Max Step')
        #ax5.plot(x, self.max_step)
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


if __name__ == '__main__':
    results1 = {
        'delta_e'  : 0.5,
        'rms_e'    : 0.25,
        'max_grad' : 0.5,
        'rms_grad' : 0.7,
        'max_step' : 0.4,
        'rms_step' : 0.3
    }
    step1 = Step(**results1)
    results2 = {
        'delta_e'  : 0.9,
        'rms_e'    : 0.45,
        'max_grad' : 0.7,
        'rms_grad' : 0.8,
        'max_step' : 0.5,
        'rms_step' : 0.6
    }
    step2 = Step(**results2)

    criteria = 1
    conv = Convergence([step1, step2], criteria)
    print(conv)
    conv.plot()
