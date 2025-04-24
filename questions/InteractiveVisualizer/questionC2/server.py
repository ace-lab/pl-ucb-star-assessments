import random
import numpy as np
import matplotlib.pyplot as plt
import io

def generate(data):

    data["params"]["i"] = 2 # init theta0
    data["params"]["j"] = -3 # init theta1
    data["params"]["a"] = 0.5 # learning rate
    data["params"]["x"] = 1
    data["params"]["y"] = 4

    theta0 = data["params"]["i"]
    theta1 = data["params"]["j"]
    learning_rate = data["params"]["a"]
    x = data["params"]["x"]
    y = data["params"]["y"]


    def update_theta(theta0, theta1, learning_rate, x, y):
        y_pred = theta0 + theta1 * x
        error = y - y_pred

        grad0 = -2 * error
        grad1 = -2 * error * x

        next_theta0 = theta0 - learning_rate * grad0
        next_theta1 = theta1 - learning_rate * grad1

        return next_theta0, next_theta1


    data["params"]["k"], data["params"]["l"] = update_theta(theta0, theta1, learning_rate, x, y)  

    data["correct_answers"]["number"] = learning_rate


def file(data):
    # dynamically render graph
    if data["filename"] == "figure.png":

        def loss_function(theta0, theta1):
            return (4 - (theta0 + theta1 * 1))**2
            
        # generate a grid of theta0 and theta1 values
        theta0 = np.linspace(-3, 3, 1000)
        theta1 = np.linspace(-3, 3, 1000)
        Theta0, Theta1 = np.meshgrid(theta0, theta1)
        Loss = loss_function(Theta0, Theta1)

        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        ax.plot_surface(Theta0, Theta1, Loss, vmin=Loss.min() * 2, cmap='viridis', edgecolor='none')

        # title and labels
        ax.set_title('Loss Landscape', pad=0)
        ax.set_xlabel(r'$\theta_0$', labelpad=5)
        ax.set_ylabel(r'$\theta_1$', labelpad=5)
        ax.set_zlabel(r'$\tilde{L}(\theta)$', labelpad=-28)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        return buf