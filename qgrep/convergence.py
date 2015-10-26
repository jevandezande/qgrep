import numpy as np


class Step:
    """
    An object that stores a convergence result
    """
    def __init__(self, delta_e=None, rms_grad=None,
                 max_grad=None, rms_step=None, max_step=None):
        # TODO: institue better checks
        self.delta_e  = delta_e
        self.rms_grad = rms_grad
        self.max_grad = max_grad
        self.rms_step = rms_step
        self.max_step = max_step

    def __str__(self):
        #form = "{energy:} {delta_e:} {rms_grad:} {max_grad:} {rms_step:} {max_step:}"
        form = "{:> 10.8f} {:> 10.8f} {:> 10.8f} {:> 10.8f} {:> 10.8f}"
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
        header = "  Δ energy   RMS energy   RMS grad    MAX grad    RMS step    MAX Step\n"
        return header + '\n'.join(str(step) for step in self.steps)

    def plot(self):
        try:
            from matplotlib import pyplot as plt

            f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col', sharey='row')
            x = range(len(self.steps))
            #f.set_title('Convergence')
            ax1.set_title(r'$\Delta$ Energy')
            ax1.plot(x, self.delta_e)
            ax2.set_title('RMS Grad')
            ax2.plot(x, self.rms_grad)
            ax3.set_title('RMS Step')
            ax3.plot(x, self.rms_step)

            #ax4.set_title('RMS Energy')
            #ax4.plot(x, self.rms_energy)
            ax5.set_title('Max Grad')
            ax5.plot(x, self.max_grad)
            ax6.set_title('Max Step')
            ax6.plot(x, self.max_step)
            plt.show()
        except:
            raise ImportError("No module named 'matplotlib'")

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
