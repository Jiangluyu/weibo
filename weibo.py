from selenium import webdriver
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
import os


def get_target_uid(url): # url 'follow-page'
    # e.g. https://weibo.com/p/1005051135141971/follow?from=page_100505&wvr=6&mod=headfollow#place
    target_uid = url.split('/')[-2][6:]
    return target_uid


class Login:
    __driver = None
    __account = ''
    __password = ''

    def __init__(self):
        self.__driver = webdriver.Chrome(executable_path='chromedriver.exe')
        self.__driver.implicitly_wait(10)
        self.__driver.maximize_window()

    def __login_settings(self):
        self.__account = input('请输入微博账号：')
        self.__password = input('请输入密码：')

    def get_driver(self):
        return self.__driver

    def auto_login(self):
        self.__login_settings()
        url = 'http://weibo.com'
        self.__driver.get(url)
        input_acnt = self.__driver.find_element_by_id('loginname')
        input_pswd = self.__driver.find_element_by_css_selector('input[type="password"]')
        input_acnt.send_keys(self.__account)
        input_pswd.send_keys(self.__password)
        bt_login = self.__driver.find_element_by_class_name('login_btn')
        bt_login.click()
        sleep(5)


class Like:
    __driver = None

    def __init__(self, driver):
        self.__driver = driver

    def auto_like(self):
        url = input('请输入目标用户的主页\n')
        self.__driver.get(url)
        # like http://weibo.com/u/2398074204

        bt_like_list = self.__driver.find_elements_by_xpath('//div[@class="WB_frame_c"]/div[2]//a[@title="赞"]')
        for bt_like in bt_like_list:
            sleep(10)
            try:
                bt_like.send_keys('\n')
            except Exception as e:
                print(str(e))
                break
            print('liked 1 msg')


class Comment:
    __driver = None

    def __init__(self, driver):
        self.__driver = driver

    def __comment_txt(self, text):
        wd_input = self.__driver.find_element_by_xpath(
            '//div[@class="WB_feed_publish clearfix"]//div[@class="WB_publish"]//div[@class="p_input"]//textarea[@class="W_input"]')
        sleep(3)
        wd_input.send_keys(text)

    def __get_comment_list(self, uid):
        self.__driver.get('http://weibo.com/u/' + uid)
        bt_comment_list = self.__driver.find_elements_by_xpath(
            '//div[@tbinfo="ouid=' + uid + '"]//span[@node-type="comment_btn_text"]')
        sleep(2)
        return bt_comment_list

    def __send_comment(self):
        self.__driver.find_element_by_xpath(
            '//div[@class="WB_feed_publish clearfix"]//div[@class="p_opt clearfix"]//div[@class="btn W_fr"]//a[text()="评论"]').click()

    def auto_comment(self):
        target_url = input('请输入目标用户关注页的url(在主页粉丝数左侧)：')
        uid = get_target_uid(target_url)
        comment_list = self.__get_comment_list(uid)
        word_list = ['可以', '不错', '学到了', '真行', '羡慕']  # 可以更改，仅做测试用
        salt = 0
        for bt_comment in comment_list:
            try:
                webdriver.ActionChains(self.__driver).move_to_element(bt_comment).click(bt_comment).perform()
                self.__comment_txt(word_list[salt % len(word_list)] + str(salt))
                salt += 1
                self.__send_comment()
                sleep(3)
                webdriver.ActionChains(self.__driver).move_to_element(bt_comment).click(bt_comment).perform()
                sleep(3)
            except Exception as e:
                print(str(e))
                break


class Follow:
    __driver = None
    __uid = ''

    def __init__(self, driver):
        self.__driver = driver

    def __get_follow_list(self, page):
        url = 'https://weibo.com/' + self.__uid + '/follow' + '?page=' + str(page)
        self.__driver.get(url)
        follow_list = self.__driver.find_elements_by_xpath('//a[@action-type="follow"]')

        uid_list = []
        for follow_usr in follow_list:
            action_data = follow_usr.get_attribute('action-data')
            if action_data is None:  # 查看未关注的人时，需要忽略对该用户的关注按钮
                continue
            uid = action_data.split('&')[-3].split('=')[1]
            uid_list.append(uid)
        return uid_list

    def __follow(self, follow_uid):
        self.__driver.get('http://weibo.com/u/' + follow_uid)
        focuslink = WebDriverWait(self.__driver, 10).until(
            lambda x: x.find_element_by_xpath('//div[@node-type="focusLink"]/a'))
        focuslink.click()
        try:
            title = WebDriverWait(self.__driver, 10).until(
                lambda x: x.find_element_by_class_name('W_layer_title'))
            title_txt = title.get_attribute('innerHTML')
            if title_txt == '关注成功':
                print('关注用户' + follow_uid + '成功')
            elif title_txt == '请输入验证码':
                print('需要验证码，等待120s自动重试')
                sleep(120)
                print('正在重试')
                self.__follow(follow_uid)
        except:
            pass

    def __follow_uid_list(self, target_uid_list):
        for u in target_uid_list:
            self.__follow(u)

    def auto_follow(self):
        target_url = input('请输入目标用户关注页的url(在主页粉丝数左侧)：')
        self.__uid = get_target_uid(target_url)
        for i in range(5):
            page = i + 1
            uid_list = self.__get_follow_list(page)
            self.__follow_uid_list(uid_list)
            print("page " + str(page) + " finished")


class Unfollow:
    __driver = None

    def __init__(self, driver):
        self.__driver = driver

    def auto_unfollow(self):
        unfollow_limit = input('请输入取关人数：')
        bt_homepage = self.__driver.find_element_by_css_selector(
            '#plc_top > div > div > div.gn_position > div.gn_nav > ul > li:nth-child(5) > a')
        bt_homepage.click()
        bt_followpage = self.__driver.find_element_by_css_selector(
            '#Pl_Core_T8CustomTriColumn__3 > div > div > div > table > tbody > tr > td:nth-child(1) > a > strong')
        bt_followpage.click()
        current_url = self.__driver.current_url
        mobile_cu = current_url.replace('com', 'cn')
        self.__driver.get(mobile_cu)
        try:
            for i in range(int(unfollow_limit)):
                sleep(3)
                bt_unfollow = self.__driver.find_element_by_link_text('取消关注')
                bt_unfollow.click()
                sleep(3)
                bt_confirm = self.__driver.find_element_by_link_text('确定')
                bt_confirm.click()
                sleep(3)
        except Exception as e:
            print(e)
            pass


class Upload:
    __driver = None

    def __init__(self, driver):
        self.__driver = driver

    def __upload_txt(self, text):
        wd_input = self.__driver.find_element_by_xpath('//div[@node-type="textElDiv"]/textarea[@class="W_input"]')
        wd_input.send_keys(text)
        sleep(2)

    def __upload_img(self, path):
        sleep(1)
        os.system('upload_img.au3 ' + path)
        sleep(2)

    def __upload_txt_img(self, text, path_list):
        self.__upload_txt(text)
        bt_img = self.__driver.find_element_by_css_selector('a[action-type="multiimage"]')
        sleep(1)

        if len(path_list) == 0:
            print("Empty image path")
        bt_img.click()
        self.__upload_img(path_list[0])
        count = 2
        if len(path_list) > 1:
            for path in path_list[1:]:
                if path is not None:
                    bt_multiimg = self.__driver.find_element_by_xpath('//li[@node-type="uploadBtn"]')
                    bt_multiimg.click()
                    self.__upload_img(path)
                    count += 1
                elif count > 20:
                    break
                else:
                    pass

    def __send_weibo(self):
        self.__driver.find_element_by_class_name('W_btn_a').click()

    def auto_upload(self):
        img_path = ['C:\\Users\\Teamo\\Desktop\\1.jpg', 'C:\\Users\\Teamo\\Desktop\\2.jpg']  # 需要发送图片的列表
        msg = input('请输入要发布的文本内容：')
        self.__upload_txt_img(msg, img_path)  # 文本消息，图片路径列表
        self.__send_weibo()


if __name__ == '__main__':
    login = Login()
    login.auto_login()

    order = input('请输入所要进行的操作编号:\n'
                  '1 -> 批量点赞\n'
                  '2 -> 批量评论\n'
                  '3 -> 批量关注\n'
                  '4 -> 批量取消关注\n'
                  '5 -> 自动发微博\n'
                  '0 -> 退出\n')

    if order == '1':
        like = Like(login.get_driver())
        like.auto_like()
    elif order == '2':
        comment = Comment(login.get_driver())
        comment.auto_comment()
    elif order == '3':
        follow = Follow(login.get_driver())
        follow.auto_follow()
    elif order == '4':
        unfollow = Unfollow(login.get_driver())
        unfollow.auto_unfollow()
    elif order == '5':
        upload = Upload(login.get_driver())
        upload.auto_upload()
    elif order == '0':
        exit()
    else:
        print('无效操作')
    # login.get_driver().close()
