def generate_unsorted_numbers(numofentries: int, max: int, min: int) -> list[int]:
    # generates a bunch of random numbers to have as the enteries that have to be sorted
    returnlst = []
    for _ in range(numofentries):
        newnum = random.randint(min, max)
        returnlst.append(newnum)
    return returnlst


def get_iterations(array):
    #goes array through selection sort
    size = len(array)
    returnval = []

    for i in range(size):
        minval = i

        for j in range(i+1, size):
            if array[j] < array[minval]:
                minval = j

        temp = array[i]
        array[i] = array[minval]
        array[minval] = temp
        curriteration = []
        for k in range(size):
            curriteration.append(array[k])
        returnval.append(curriteration)
    return returnval