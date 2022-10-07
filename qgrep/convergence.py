from dataclasses import dataclass

import numpy as np


@dataclass
class Step:
    """
    An object that stores a geometry convergence step
    :param params: convergence parameters
    :param criteria: criteria for convergence
    """

    params: dict[str, float]
    criteria: list[float]

    def __post_init__(self):
        self.__dict__ |= self.params
        assert len(self.params) == len(self.criteria)
        print(list(zip(self.params.items(), self.criteria)))

    def __iter__(self):
        yield from zip(self.params.items(), self.criteria)

    def __str__(self):
        out = ""
        for (key, value), criterion in self:
            if key in ["scf_steps"]:
                pass
            out += f"{value:> 9.2e}"
            out += "*" if abs(value) < criterion else " "

        return out + f"|{value:> 7d}"


@dataclass
class Convergence:
    """
    Stores multiple geometry convergence steps
    :param steps: list of Steps
    :param criteria: criteria for convergence
    :param program: the program the results are from
    """

    steps: list[Step]
    criteria: list
    program: str = "orca"

    def __iter__(self):
        yield from self.steps

    def __len__(self):
        return len(self.steps)

    def __str__(self):
        if self.program != "orca":
            raise NotImplementedError("Convergence currently only implemented for ORCA")

        header = "      Δ energy  RMS grad  MAX grad  RMS step  MAX Step | SCF Steps\n"

        line = "-" * 66 + "\n"
        out = header + line
        for i, step in enumerate(self):
            out += f"{i:>3}: "
            for (key, value), criterion in step:
                if key in ["scf_steps"]:
                    pass
                star = " "
                if abs(value) < criterion and (i != 0 or key != "delta_e"):
                    star = "*"
                out += f"{value:> 9.2e}{star}"
            out += f"|{step.scf_steps:> 7d}\n"

        form = " {:> 9.2e}" * len(self.criteria)
        return out + line + "    " + form.format(*self.criteria)

    def plot(self, show: bool = True):
        """
        Generate a plot of the convergence
        :param show: show the plot
        """
        from matplotlib import pyplot as plt

        f, (ax0, ax1) = plt.subplots(1, 2, sharex="col")
        f.suptitle("Convergence", fontsize=16)
        plt.xlabel("Step")
        x = np.arange(len(self))

        ax0.set_yscale("symlog", linthreshy=1e-5)
        ax0.set_title(r"$\Delta$ Energy")
        ax0.plot(x, self.delta_e, label="Energy")
        ax0.legend()

        ax1.set_ylim(0, 1)
        ax1.set_yscale("symlog", linthreshy=1e-4)
        ax1.set_title("Convergence Parameters")
        ax1.plot(x, self.rms_grad, "b-", label="RMS Grad")
        ax1.plot(x, self.max_grad, "b--", label="Max Grad")
        ax1.plot(x, self.rms_step, "r-", label="RMS Step")
        ax1.plot(x, self.max_step, "r--", label="Max Step")
        # TODO: generalize for more than ORCA
        ax1.plot(x, [self.criteria[1]] * len(self), "k-")
        ax1.plot(x, [self.criteria[1]] * len(self), "b*")
        ax1.plot(x, [self.criteria[2]] * len(self), "k--")
        ax1.plot(x, [self.criteria[2]] * len(self), "b*")
        ax1.plot(x, [self.criteria[3]] * len(self), "k-")
        ax1.plot(x, [self.criteria[3]] * len(self), "r*")
        ax1.plot(x, [self.criteria[4]] * len(self), "k--")
        ax1.plot(x, [self.criteria[4]] * len(self), "r*")
        ax1.legend()

        if show:
            plt.show()

    @property
    def delta_e(self):
        return np.fromiter((step.delta_e for step in self), dtype=float)

    @property
    def rms_e(self):
        return np.fromiter((step.rms_e for step in self), dtype=float)

    @property
    def max_grad(self):
        return np.fromiter((step.max_grad for step in self), dtype=float)

    @property
    def rms_grad(self):
        return np.fromiter((step.rms_grad for step in self), dtype=float)

    @property
    def max_step(self):
        return np.fromiter((step.max_step for step in self), dtype=float)

    @property
    def rms_step(self):
        return np.fromiter((step.rms_step for step in self), dtype=float)
