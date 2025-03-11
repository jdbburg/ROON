import matplotlib.pyplot as plt
import numpy as np

def example_plot(color='blue'):
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    plt.plot(x, y, color=color)
    plt.xlabel('x')
    plt.ylabel('sin(x)')
    plt.show()


def example_histogram():
    data = np.random.randn(1000)
    plt.hist(data, bins=30)
    plt.show()

