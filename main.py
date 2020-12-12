import time
import random
import requests
from PIL import Image
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains, DesiredCapabilities

start_crop_image = False
refresh = False
success = False
reg_success = 0
login_list = []
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--hide-scrollbars')  # 隐藏滚动条
# options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片
options.add_argument('--disable-gpu')
# options.add_argument('--incognito')
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"


def crop_image(image_file_name):
    # 保存图片
    # 截图验证码图片
    # 定位某个元素在浏览器中的位置
    img = brower.find_element_by_xpath("//*[@class='geetest_canvas_slice geetest_absolute']")
    img_data = img.screenshot_as_png
    with open(image_file_name, 'wb') as f:
        f.write(img_data)
    im = Image.open(image_file_name)
    return im


def compare_pixel(image1, image2, i, j):
    # 判断两个图片像素是否相同
    pixel1 = image1.load()[i, j]
    pixel2 = image2.load()[i, j]

    threshold = 60
    if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
            pixel1[2] - pixel2[2]) < threshold:
        return True
    return False


def find_coordinate(left, img1, img2):
    # 根据判断结果，返回x坐标
    has_find = False
    for i in range(left, img1.size[0]):  # x坐标
        if has_find:  # 找到不一样的位置，退出外层循环
            break
        for j in range(img1.size[1]):  # y坐标（从0开始）
            if not compare_pixel(img1, img2, i, j):  # 比较两张图片在同一位置的值
                left = i
                has_find = True  # 如果两张图片元素不一样，那么就退出内层循环
                break
    return left


def crop_images():
    img1 = crop_image('缺口图片.png')
    img_obj = brower.find_element_by_xpath(
        '//*[@class="geetest_canvas_fullbg geetest_fade geetest_absolute"]')  # 找到图片，建立对象
    img_style = img_obj.get_attribute('style')  # 记录style的值
    # 完整图片
    # JS增删改查操作元素的属性
    # #新增属性
    # driver.execute_script(“arguments[0].%s=arguments[1]” %attributeName,elementObj, value)
    # #修改属性
    # driver.execute_script(“arguments[0].setAttribute(arguments[1],arguments[2])”, elementObj, attributeName, value)
    # #获取属性
    # elementObj.get_attribute(attributeName)
    # #删除属性
    brower.execute_script("arguments[0].removeAttribute(arguments[1])", img_obj, 'style')  # 删除图片属性，显示完整图片
    img2 = crop_image('完整图片.png')
    brower.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", img_obj, 'style',
                          img_style)  # 将style值添加回去，显示缺口图片
    return img1, img2


def slid_verify():
    global refresh
    while True:
        if start_crop_image:
            break
        elif success:
            return True
    if refresh:
        brower.find_element_by_class_name('geetest_refresh_1').click()
        time.sleep(0.5)
        refresh = False
    time.sleep(0.5)
    img1, img2 = crop_images()
    # 获取滑块图片位置
    slid_coor = find_coordinate(0, img1, img2)
    # 获取缺口图片位置
    target_coor = find_coordinate(56, img1, img2)
    print(f'滑块偏移：{slid_coor}，缺口偏移：{target_coor}')

    target_coor -= slid_coor  # 调整偏移量
    track = []  # 用于储存一次拖动滑块的距离（不能一次拖到位，不然会被判定为机器）
    i = 0
    # 分为3断，分别设置不同速度，越接近缺口，越慢
    stagev1 = round((target_coor - slid_coor) / 4)  # 第1段（前3/5）：分为4次（平均距离移动），stafev1为当前阶段的速度
    while i < round(target_coor * 3 / 5):
        i += stagev1
        track.append(stagev1)
    stagev2 = round((target_coor - i) / 7)  # 第2段（3/5到21/25）：分为7次（平均距离移动）
    while i < round(target_coor * 21 / 25):
        i += stagev2
        track.append(stagev2)
    stagev3 = 1
    while i < round(target_coor):  # 第3段（21/25到最后）：按1为单位移动
        i += stagev3
        track.append(stagev3)

    slider = brower.find_element_by_xpath("//div[@class='geetest_slider_button']")  # 找到拖动按钮
    ActionChains(brower).move_to_element(slider).perform()  # 建立拖动对象
    ActionChains(brower).click_and_hold(slider).perform()  # 点击，并按住鼠标不放

    for x in track:
        ActionChains(brower).move_by_offset(xoffset=x, yoffset=0).perform()  # 拖动，x为一次移动的距离
    ActionChains(brower).release().perform()  # 放开鼠标
    return


def t():
    global start_crop_image
    global success
    global refresh
    while True:
        try:
            if brower.find_element_by_class_name('geetest_success_radar_tip_content').text == '验证成功':
                success = True
                break
        except:
            pass
        try:
            if brower.find_element_by_class_name('geetest_result_content').text == '请正确拼合图像':
                start_crop_image = False
                refresh = True
        except:
            pass
        try:
            if brower.find_element_by_class_name('geetest_radar_tip_content').text == '点击按钮进行验证':
                time.sleep(0.5)
                brower.find_element_by_class_name('geetest_radar_tip_content').click()
        except:
            pass
        try:
            if brower.find_element_by_class_name('geetest_slider_tip').text == '拖动滑块完成拼图':
                start_crop_image = True
            else:
                start_crop_image = False
        except:
            pass
        try:
            if brower.find_element_by_class_name('geetest_reset_tip_content').text == '请点击重试':
                start_crop_image = False
                brower.find_element_by_class_name('geetest_reset_tip_content').click()
        except:
            pass


def login(email, passwd):
    url = 'https://v2.freeyes.xyz/auth/login'
    data = {'email': email, 'passwd': passwd}
    headers = {'user-agent': None}
    r = requests.post(url, data=data, headers=headers, timeout=10)
    print(r.json())
    ret = r.json()['ret'] == 1
    cookies = r.cookies.get_dict()
    print(cookies)
    url = 'https://v2.freeyes.xyz/user'
    r = requests.get(url, cookies=cookies)
    print(r.status_code)
    return ret


if __name__ == '__main__':
    code = input('输入邀请码：')
    if not code:
        code = 'eId6'
    url = f'https://v2.freeyes.xyz/auth/register?code={code}'
    print(url)
    chrome = ChromeDriverManager().install()
    while True:
        try:
            success = False
            start_crop_image = True
            brower = webdriver.Chrome(chrome, options=options)
            wait = WebDriverWait(brower, 10)
            # 打开网页
            brower.get(url)
            # 生成随机账号
            name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10))
            wechat = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10))
            email = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10)) + '@qq.com'
            # 填入信息
            wait.until(EC.presence_of_element_located((By.ID, 'name')))
            brower.find_element(By.ID, 'name').send_keys(name)
            wait.until(EC.presence_of_element_located((By.ID, 'email')))
            brower.find_element(By.ID, 'email').send_keys(email)
            wait.until(EC.presence_of_element_located((By.ID, 'passwd')))
            brower.find_element(By.ID, 'passwd').send_keys('11111111')
            wait.until(EC.presence_of_element_located((By.ID, 'repasswd')))
            brower.find_element(By.ID, 'repasswd').send_keys('11111111')
            wait.until(EC.presence_of_element_located((By.ID, 'wechat')))
            brower.find_element(By.ID, 'wechat').send_keys(wechat)
            wait.until(EC.presence_of_element_located((By.ID, 'imtype')))
            brower.find_element(By.ID, 'imtype').click()
            wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='dropdown-menu']/li[last()]/a")))
            # 循环等待列表框加载成功并点击
            while True:
                time.sleep(0.1)
                try:
                    brower.find_element_by_xpath("//ul[@class='dropdown-menu']/li[last()]/a").click()
                except:
                    continue
                break
            # 开启线程循环判断状态
            Thread(target=t).start()
            print('开始验证')
            while True:
                try:
                    if slid_verify():
                        break
                except:
                    pass
            print('验证成功')
            time.sleep(0.5)
            while True:
                try:
                    brower.find_element_by_id('tos').click()
                    break
                except:
                    pass
            time.sleep(0.1)
            while True:
                try:
                    brower.find_element_by_id('reg').click()
                    break
                except:
                    pass
            brower.close()
            if login_list:
                try:
                    print('开始登录')
                    if login(login_list.pop(), '11111111'):
                        reg_success += 1
                        print(f'已成功注册{reg_success}个')
                except:
                    pass
            login_list.append(email)
        except:
            brower.close()
            continue
