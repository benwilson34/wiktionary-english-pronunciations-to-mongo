print('starting')
arr = iter(range(5))

for i in range(10):
    current_value = next(arr, None)
    if current_value == None:
        print('no more elements')
        break
    print(f'{current_value}')

print('done.')
