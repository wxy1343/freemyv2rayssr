import io
import json
import os
import random
import time
import traceback
from threading import Thread

import func_timeout
import requests
import selenium
from PIL import Image
from func_timeout import func_set_timeout
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def login(email, passwd):
    url = 'https://v2.freeyes.xyz/auth/login'
    data = {'email': email, 'passwd': passwd}
    headers = {'user-agent': None}
    try:
        r = requests.post(url, data=data, headers=headers, timeout=10)
    except requests.exceptions.ReadTimeout:
        return
    try:
        if r.json()['ret'] == 0:
            return
    except json.decoder.JSONDecodeError:
        return
    cookies = r.cookies.get_dict()
    print(cookies)
    return cookies


class register:
    __species = None
    chrome = None

    def __new__(cls, *args, **kwargs):
        if not cls.__species:
            cls.__species = object.__new__(cls)
            cls.chrome = ChromeDriverManager().install()
        return object.__new__(cls)

    def __init__(self, code=None):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--start-maximized")
        self.__start_crop_image = False
        self.__refresh = False
        self.__success = False
        self.__completed = False
        if not code:
            code = 'eId6'
        self.url = f'https://v2.freeyes.xyz/auth/register?code={code}'
        print(self.url)

    def __del__(self):
        self.__completed = True
        try:
            self.browser.close()
        except (NameError, ImportError, AttributeError, selenium.common.exceptions.InvalidSessionIdException,
                selenium.common.exceptions.NoSuchWindowException, selenium.common.exceptions.WebDriverException):
            pass
        except KeyboardInterrupt:
            os._exit(0)
        except:
            traceback.print_exc()
        del self

    def __call__(self):
        try:
            return self.__reg()
        except func_timeout.exceptions.FunctionTimedOut:
            print('运行超时')
            self.__del__()
        except KeyboardInterrupt:
            os._exit(0)
        except:
            traceback.print_exc()
            self.__del__()

    @func_set_timeout(100)
    def __reg(self):
        print('开始注册')
        self.browser = webdriver.Chrome(self.chrome, options=self.options)
        print('创建浏览器驱动成功')
        wait = WebDriverWait(self.browser, 10)
        # 打开网页
        print('打开网页')
        self.browser.get(self.url)
        print('打开网页成功')
        # 生成随机账号
        self.name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10))
        self.wechat = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10))
        self.email = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10)) + '@qq.com'
        self.passwd = '11111111'
        # 填入信息
        print('填入信息')
        wait.until(EC.presence_of_element_located((By.ID, 'name')))
        self.browser.find_element(By.ID, 'name').send_keys(self.name)
        wait.until(EC.presence_of_element_located((By.ID, 'email')))
        self.browser.find_element(By.ID, 'email').send_keys(self.email)
        wait.until(EC.presence_of_element_located((By.ID, 'passwd')))
        self.browser.find_element(By.ID, 'passwd').send_keys(self.passwd)
        wait.until(EC.presence_of_element_located((By.ID, 'repasswd')))
        self.browser.find_element(By.ID, 'repasswd').send_keys(self.passwd)
        wait.until(EC.presence_of_element_located((By.ID, 'wechat')))
        self.browser.find_element(By.ID, 'wechat').send_keys(self.wechat)
        wait.until(EC.presence_of_element_located((By.ID, 'imtype')))
        self.browser.find_element(By.ID, 'imtype').click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='dropdown-menu']/li[last()]/a")))
        print('填入信息成功')
        # 循环等待列表框加载成功并点击
        while True:
            time.sleep(0.1)
            try:
                self.browser.find_element_by_xpath("//ul[@class='dropdown-menu']/li[last()]/a").click()
            except:
                continue
            break
        # 开启线程循环判断状态
        Thread(target=self.__t, args=(self,)).start()
        print('开始验证')
        while True:
            try:
                if self.__slid_verify():
                    break
            except:
                pass
        print('验证成功')
        time.sleep(0.5)
        while True:
            try:
                self.browser.find_element_by_id('tos').click()
                break
            except:
                pass
        time.sleep(0.5)
        while True:
            try:
                self.browser.find_element_by_id('reg').click()
                break
            except:
                pass
        time.sleep(0.5)
        self.__del__()
        return True

    @classmethod
    def __t(cls, self):
        while True:
            try:
                if self.browser.find_element_by_class_name('geetest_success_radar_tip_content').text == '验证成功':
                    self.__success = True
                    break
            except:
                pass
            try:
                if self.browser.find_element_by_class_name('geetest_result_content').text == '请正确拼合图像':
                    self.__start_crop_image = False
                    self.__refresh = True
            except:
                pass
            try:
                if self.browser.find_element_by_class_name('geetest_radar_tip_content').text == '点击按钮进行验证':
                    time.sleep(0.5)
                    self.browser.find_element_by_class_name('geetest_radar_tip_content').click()
            except:
                pass
            try:
                if self.browser.find_element_by_class_name('geetest_slider_tip').text == '拖动滑块完成拼图':
                    self.__start_crop_image = True
                else:
                    self.__start_crop_image = False
            except:
                pass
            try:
                if self.browser.find_element_by_class_name('geetest_reset_tip_content').text == '请点击重试':
                    self.__start_crop_image = False
                    self.browser.find_element_by_class_name('geetest_reset_tip_content').click()
            except:
                pass
            if self.__completed:
                break

    def __crop_image(self, image_file_name):
        # 保存图片
        # 截图验证码图片
        # 定位某个元素在浏览器中的位置
        img = self.browser.find_element_by_xpath("//*[@class='geetest_canvas_slice geetest_absolute']")
        img_data = img.screenshot_as_png
        with open(image_file_name, 'wb') as f:
            f.write(img_data)
        im = Image.open(io.BytesIO(img_data))
        return im

    def __crop_images(self):
        img1 = self.__crop_image('缺口图片.png')
        img_obj = self.browser.find_element_by_xpath(
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
        self.browser.execute_script("arguments[0].removeAttribute(arguments[1])", img_obj, 'style')  # 删除图片属性，显示完整图片
        img2 = self.__crop_image('完整图片.png')
        self.browser.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", img_obj, 'style',
                                    img_style)  # 将style值添加回去，显示缺口图片
        return img1, img2

    def __slid_verify(self):
        while True:
            if self.__start_crop_image:
                break
            elif self.__success:
                return True
        if self.__refresh:
            self.browser.find_element_by_class_name('geetest_refresh_1').click()
            time.sleep(0.5)
            self.__refresh = False
        time.sleep(0.5)
        img1, img2 = self.__crop_images()
        # 获取滑块图片位置
        slid_coor = self.__find_coordinate(0, img1, img2)
        # 获取缺口图片位置
        target_coor = self.__find_coordinate(56, img1, img2)
        print(f'滑块偏移：{slid_coor}，缺口偏移：{target_coor}')
        target_coor -= slid_coor  # 调整偏移量
        track = self.__get_track(target_coor)
        slider = self.browser.find_element_by_xpath("//div[@class='geetest_slider_button']")  # 找到拖动按钮
        ActionChains(self.browser).move_to_element(slider).perform()  # 建立拖动对象
        ActionChains(self.browser).click_and_hold(slider).perform()  # 点击，并按住鼠标不放
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()  # 拖动，x为一次移动的距离
        ActionChains(self.browser).release().perform()  # 放开鼠标
        return

    def __get_track(self, distance):
        tracks = []  # 用于储存一次拖动滑块的距离（不能一次拖到位，不然会被判定为机器）
        i = 0
        # 分为3断，分别设置不同速度，越接近缺口，越慢
        stagev1 = round((distance) / 4)  # 第1段（前3/5）：分为4次（平均距离移动），stafev1为当前阶段的速度
        while i < round(distance * 3 / 5):
            i += stagev1
            tracks.append(stagev1)
        stagev2 = round((distance - i) / 7)  # 第2段（3/5到21/25）：分为7次（平均距离移动）
        while i < round(distance * 21 / 25):
            i += stagev2
            tracks.append(stagev2)
        stagev3 = 1
        while i < round(distance):  # 第3段（21/25到最后）：按1为单位移动
            i += stagev3
            tracks.append(stagev3)
        return tracks

    def __compare_pixel(self, image1, image2, i, j):
        # 判断两个图片像素是否相同
        pixel1 = image1.load()[i, j]
        pixel2 = image2.load()[i, j]

        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        return False

    def __find_coordinate(self, left, img1, img2):
        # 根据判断结果，返回x坐标
        has_find = False
        for i in range(left, img1.size[0]):  # x坐标
            if has_find:  # 找到不一样的位置，退出外层循环
                break
            for j in range(img1.size[1]):  # y坐标（从0开始）
                if not self.__compare_pixel(img1, img2, i, j):  # 比较两张图片在同一位置的值
                    left = i
                    has_find = True  # 如果两张图片元素不一样，那么就退出内层循环
                    break
        return left


if __name__ == '__main__':
    reg_success = 0
    login_list = []
    code = input('输入邀请码(没有留空)：')
    while True:
        reg = register(code)
        # reg.options.add_argument('--headless')
        if reg():
            if login_list:
                print('开始登录')
                if login(login_list.pop(), reg.passwd):
                    reg_success += 1
                    print(f'已成功注册{reg_success}个')
            login_list.append(reg.email)
            with open('output.txt', 'a') as f:
                f.write(f'{reg.email} {reg.passwd}\n')
        else:
            print('注册失败')
