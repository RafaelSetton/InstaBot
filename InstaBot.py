from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep, time
from random import choice, random


class InstaBot:
    def __init__(self, username, password):
        self.username = username
        self.driver = webdriver.Chrome()
        self.find_xpath = lambda xpath: self.__delay(lambda: self.driver.find_element_by_xpath(xpath))

        self.driver.get('https://www.instagram.com/')

        self.find_xpath("//input[@name=\"username\"]").send_keys(username)
        self.find_xpath("//input[@name=\"password\"]").send_keys(password)
        self.find_xpath("//button[@type=\"submit\"]").click()

        self.find_xpath("//button[contains(text(), 'Agora não')]").click()

        try:
            sleep(1)
            self.driver.find_element_by_xpath("//button[contains(text(), 'Agora não')]").click()
        except NoSuchElementException:
            pass

        self.xpaths = {
            'home': "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[1]/div/a",
            'profile': "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[5]/a",
            'explore': "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[3]/a",
            'followers': "/html/body/div[1]/section/main/div/header/section/ul/li[2]/a",
            'following': "/html/body/div[1]/section/main/div/header/section/ul/li[3]/a",

        }

    def __scroll_to_end(self, scroll_box, stop=-1):
        if stop == -1:
            last_height, height = 0, 1
            while last_height != height:
                last_height = height  # Scroll down until end
                sleep(1)
                height = self.driver.execute_script("""
                                    arguments[0].scrollTo(0, arguments[0].scrollHeight);
                                    return arguments[0].scrollHeight;
                                """, scroll_box)
        else:
            for _ in range(stop):
                sleep(1)
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_box)

    def __get_names(self):
        scroll_box = self.find_xpath("/html/body/div[4]/div/div[2]")

        self.__scroll_to_end(scroll_box)

        links = scroll_box.find_elements_by_tag_name('a')
        names = [name.text for name in links if name.text != '']  # List all Names
        self.find_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click()  # Close
        return names

    @staticmethod
    def __sleep_rand(base=1, var=1):
        return base + random()*var

    @staticmethod
    def __delay(func, intervalo=1):
        ini = time()
        while True:
            try:
                return func()
            except NoSuchElementException:
                sleep(intervalo)
                if time() - ini > 5:
                    raise RuntimeWarning

    def go_to_home(self):
        self.find_xpath(self.xpaths['home']).click()  # Go to Home
        sleep(1)

    def go_to_profile(self):
        self.find_xpath(self.xpaths['profile']).click()  # Go to Profile
        sleep(1)

    def get_non_followers(self, print_result=True):
        self.go_to_profile()
        sleep(1)

        self.find_xpath(self.xpaths['followers']).click()
        sleep(1)  # Open Followers
        followers = self.__get_names()

        self.find_xpath(self.xpaths['following']).click()
        sleep(1)  # Open Following
        following = self.__get_names()

        self.go_to_home()

        result = [user for user in following if user not in followers]

        if print_result:
            print(result)

        return result

    def follow_bot(self):
        tempo = time()
        users = []
        self.find_xpath(self.xpaths['explore']).click()
        sleep(3)

        def seguir():
            self.__sleep_rand(1, 2)
            follow_button_path = "/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button"
            follow_button = self.__delay(lambda: self.find_xpath(follow_button_path))  # Load
            self.__sleep_rand()
            follow_button.click()  # Follow

            with open('follows.txt', 'a') as follows:
                username_path = "/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a"
                username = self.find_xpath(username_path).text      # Anota
                follows.write(username + '\n')
                users.append(username)

            self.__sleep_rand(1, 1)
            self.find_xpath("/html/body/div[4]/div[3]/button").click()  # Close

        def gera_relatorio(list_users, tempo_inicio):
            relatorio = "# " * 20 + '\n'
            for user in list_users:
                relatorio += f"# Usuário: {user:26} #\n"
            relatorio += "# " * 20 + '\n'
            relatorio += f"# Tempo Gasto: {round(time() - tempo_inicio, 3):21}s #\n"
            relatorio += "# " * 20 + '\n'
            return relatorio

        antes, depois = 0, 1
        images = self.driver.find_elements_by_class_name("eLAPa")
        while antes != depois:
            images = self.driver.find_elements_by_class_name("eLAPa")
            antes, depois = depois, len(images)

        for i in range(0, len(images)+1, 5):

            try:
                selection = images[i:i+5]
            except IndexError:
                break

            if selection:
                image = choice(selection)
                image.click()  # Abre a imagem
                seguir()
                self.__sleep_rand(2, 3)

        return gera_relatorio(users, tempo)

    def unfollow_bot(self):

        usernames = []
        with open('follows.txt', 'r') as follows:
            for username in follows:
                usernames.append(username[:-1])

        self.go_to_profile()

        self.find_xpath(self.xpaths['following']).click()

        sleep(1)
        followings = self.driver.find_elements_by_xpath("/html/body/div[4]/div/div[2]/ul/div/li")
        print(followings)

        deleted = []  # Parar de Seguir
        for following in followings:
            username = following.find_element_by_tag_name("a").text
            scroll_box = self.find_xpath("/html/body/div[4]/div/div[2]")
            self.driver.execute_script("arguments[0].scrollBy(0, arguments[1].height)", scroll_box, following)
            print(username)

            if username in usernames:
                following.find_element_by_tag_name("button").click()
                self.find_xpath("/html/body/div[5]/div/div/div[3]/button[1]").click()
                deleted.append(username)

                sleep(0.5)

        # Refazer o Arquivo
        with open('follows.txt', 'w+') as follows:
            new = []
            for name in usernames:
                if name not in deleted:
                    new.append(name)

            follows.write('\n'.join(new))


if __name__ == '__main__':
    my_username = ""
    my_password = ""

    bot = InstaBot(my_username, my_password)
