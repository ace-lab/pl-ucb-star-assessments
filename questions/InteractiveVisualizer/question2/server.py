import random

def generate(data):
    # randomizes values multiplying/exponentiating thetas
    # data["params"]["x"] = random.randint(2, 5)
    # data["params"]["y"] = random.randint(2, 5)
    # data["params"]["z"] = random.randint(2, 5)

    # theta0 and theta1 values at time step 0
    data["params"]["i"] = random.randint(-2, 2)
    data["params"]["j"] = random.randint(-2, 2)

    # learning rate a
    data["params"]["a"] = random.choice([0.1, 0.2, 0.5]) 

    def update_rule() -> float:
        # returns the next value for theta0 at time step 1
        theta0 = data["params"]["i"]
        theta1 = data["params"]["j"]
        learning_rate = data["params"]["a"]
        coeff1 = 1
        coeff2 = 2

        return theta0 - learning_rate * (coeff1 + coeff2 * theta0 ** (coeff2 - 1) * theta1)

    data["correct_answers"]["number"] = update_rule()