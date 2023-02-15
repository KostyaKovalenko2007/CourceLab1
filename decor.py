import datetime
def decorator(old_function):
    def new_function(*args, **kwargs):
        with open('logs.log', 'a') as file:
            file.write(f'Start: {datetime.datetime.now()}')
            file.write(f'{old_function.__name__}')
            file.write(f'{args=}')
            file.write(f'{kwargs=}')
            result = old_function(*args, **kwargs)
            file.write(f'{result=}')
            file.write(f'Finish:{datetime.datetime.now()}')
        return result

    return new_function()