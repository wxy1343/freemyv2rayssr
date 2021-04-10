from api import login, buy

if __name__ == '__main__':
    user_list = []
    with open('output.txt', 'r') as f:
        while True:
            result = f.readline()
            if not result:
                break
            user_list.append(result.rstrip('\n').split())
    print('\n'.join([' '.join(i) for i in user_list]))
    print(f'共获取到{len(user_list)}个账号')
    for user in user_list:
        cookies = login(*user)
        if cookies:
            print(f'{user[0]}登录成功')
            print(buy(cookies)[1])
        else:
            print(f'{user[0]}登录失败')
            with open('output_fail.txt', 'a') as f:
                f.write(f'{user[0]} {user[1]}\n')
