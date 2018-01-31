import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


data = np.array([0, 1, 3, 7, 3, 1, 0, 0.1, 0.3, 0.7, 0.3, 0.1, 0])

# Initial guess
p0 = [7, 3, 3]

# Define a model function
def gaussian(A, μ, σ):
    return lambda x: A*np.exp(-(x-μ)**2/(2*σ**2))
    

def f(x, *params):
    if len(params) % 3:
        raise Exception('Invalid number of parameters; should be divisible by 3.')
    y = 0
    params = [params[i:i+3] for i in range(0, len(params), 3)]
    for A, μ, σ in params:
        y += gaussian(A, μ, σ)(x)

    return y


coeff, var_matrix = curve_fit(f, range(len(data)), data, p0=p0)

print('Coeff')
print(coeff)
print('Var Matrix')
print(var_matrix)

#plt.show()

# Get the fitted curve
plt.plot(data)
plt.plot(f(data, *coeff))

# Finally, lets get the fitting parameters, i.e. the mean and standard deviation:
print('Fitted mean = ', coeff[1])
print('Fitted standard deviation = ', coeff[2])

plt.show()
