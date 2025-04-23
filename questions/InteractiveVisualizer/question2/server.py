import random

def generate(data):
    # theta0 and theta1 values at time step 0
    data["params"]["i"] = 1 #random.randint(-2, 2)
    data["params"]["j"] = -1 #random.randint(-2, 2)

    # learning rate a
    data["params"]["a"] = 0.1 #random.choice([0.1, 0.2, 0.5]) 

    # randomizes values multiplying/exponentiating thetas
    data["params"]["coeff1"] = 3 #random.randint(2, 5)
    data["params"]["exp"] = 2 #random.randint(2, 5)
    data["params"]["coeff2"] = 1 #random.randint(2, 5)


    theta0 = data["params"]["i"]
    theta1 = data["params"]["j"]

    learning_rate = data["params"]["a"]
    
    coeff1 = data["params"]["coeff1"]
    exp = data["params"]["exp"]
    coeff2 = data["params"]["coeff2"]


    def update_rule(theta0, theta1, learning_rate, coeff1, exp, coeff2) -> float:
        # returns the next value for theta0 and theta1
        next_theta0 = theta0 - learning_rate * (coeff1 + exp * theta0 ** (exp - 1) * theta1)
        next_theta1 = theta1 - learning_rate * (theta0 ** exp + coeff2)
        return next_theta0, next_theta1
    
    
    next_theta0, next_theta1 = update_rule(theta0, theta1, learning_rate, coeff1, exp, coeff2)
    data["correct_answers"]["number1"] = next_theta0
    data["correct_answers"]["number2"] = next_theta1

    next_theta0, _ = update_rule(next_theta0, next_theta1, learning_rate, coeff1, exp, coeff2)
    data["correct_answers"]["number3"] = next_theta0
