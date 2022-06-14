def processIsNotFinishedStatic(finished, number_of_samples):
    l = len(finished)
    # label = Label()
    if (l >= number_of_samples):
        print('Progress: 100%')
        return False
    else:
        print('Progress: ' + str(round(l * 100 / number_of_samples, 2)) + '%')
        return True