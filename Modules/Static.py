def processIsNotFinishedStatic(finished, number_of_samples, iterator):
    l = len(finished)
    if l >= number_of_samples:
        print('Progress: 100%')
        return False
    else:
        if iterator % 2000 == 1:
            print('Progress: ' + str(round(l * 100 / number_of_samples, 2)) + '%')
        return True
