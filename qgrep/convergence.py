import numpy as np

from collections import OrderedDict


class Step:
    """
    An object that stores a convergence result
    """
    def __init__(self, params, criteria):
        self.__dict__.update(params)
        self.params = params
        self.criteria = criteria

    def __str__(self):
        out = ''
        for (key, value), criterion in zip(self.params.items(), self.criteria):
            # integers
            if key in ['scf_steps']:
                pass
            out += f'{value:> 9.2e}'
            out += '*' if abs(value) < criterion else ' '

        out += f'|{value:> 7d}'
        return out


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
            header = "      Δ energy  RMS grad  MAX grad  RMS step  MAX Step | SCF Steps\n"
        else:
            raise NotImplementedError('Congervence currently only implemented for ORCA')

        line = '-'*66 + '\n'
        out = header + line
        for i, step in enumerate(self.steps):
            out += f'{i:>3}: '
            for (key, value), criterion in zip(step.params.items(), step.criteria):
                # integers
                if key in ['scf_steps']:
                    pass
                else:
                    star = '*' if abs(value) < criterion and not (i == 0 and key == 'delta_e') else ' '
                    out += f'{value:> 9.2e}{star}'
            out += f'|{step.scf_steps:> 7d}\n'

        return out + line + '    ' + (' {:> 9.2e}'*len(self.criteria)).format(*self.criteria)

    def plot(self):
        from matplotlib import pyplot as plt

        f, (ax0, ax1) = plt.subplots(1, 2, sharex='col')
        f.suptitle('Convergence', fontsize=16)
        plt.xlabel('Step')
        x = range(len(self.steps))

        ax0.set_yscale('symlog', linthreshy=1e-5)
        ax0.set_title(r'$\Delta$ Energy')
        ax0.plot(x, self.delta_e, label='Energy')
        ax0.legend()

        ax1.set_ylim(0, 1)
        ax1.set_yscale('symlog', linthreshy=1e-4)
        ax1.set_title('Convergence Parameters')
        ax1.plot(x, self.rms_grad, 'b-' , label='RMS Grad')
        ax1.plot(x, self.max_grad, 'b--', label='Max Grad')
        ax1.plot(x, self.rms_step, 'r-' , label='RMS Step')
        ax1.plot(x, self.max_step, 'r--', label='Max Step')
        # TODO: generalize for more than ORCA
        ax1.plot(x, [self.criteria[1]]*len(self.steps), 'k-')
        ax1.plot(x, [self.criteria[1]]*len(self.steps), 'b*')
        ax1.plot(x, [self.criteria[2]]*len(self.steps), 'k--' )
        ax1.plot(x, [self.criteria[2]]*len(self.steps), 'b*' )
        ax1.plot(x, [self.criteria[3]]*len(self.steps), 'k-')
        ax1.plot(x, [self.criteria[3]]*len(self.steps), 'r*')
        ax1.plot(x, [self.criteria[4]]*len(self.steps), 'k--' )
        ax1.plot(x, [self.criteria[4]]*len(self.steps), 'r*' )
        ax1.legend()

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
