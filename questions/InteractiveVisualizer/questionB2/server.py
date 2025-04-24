import random
import numpy as np

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
