from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_tjsgh = User.objects.create_user(username='tjsgh',password='somepassword')
        self.user_seonho = User.objects.create_user(username='seonho',password='somepassword')

    def navbar_test(self,soup):
        navbar = soup.nav
        self.assertIn('Blog',navbar.text)
        self.assertIn('About Me',navbar.text)

        home_btn = navbar.find('a',text="Home") # home이라는 a요소를 찾아서 href 속성을 체크
        self.assertEqual(home_btn.attrs['href'],'/')

        blog_btn = navbar.find('a',text="Blog")
        self.assertEqual(blog_btn.attrs['href'],'/blog/')

        about_me_btn = navbar.find('a',text="About Me")
        self.assertEqual(about_me_btn.attrs['href'],'/about_me/')

    def test_post_list(self):
        #1.1
        response = self.client.get('/blog/')
        #1.2
        self.assertEqual(response.status_code,200)
        #1.3
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text,'Blog')
        #1.4
        self.navbar_test(soup)

        #2.1
        self.assertEqual(Post.objects.count(),0)
        #2.2
        main_area = soup.find('div',id='main-area')
        self.assertIn('아직 게시물이 없습니다.',main_area.text)

        #3.1
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = "Hello World. We are the World",
            author  = self.user_tjsgh,
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content = '1등이 전부는 아니잖아요?',
            author = self.user_seonho,
        )
        self.assertEqual(Post.objects.count(),2)

        #3.2
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content,'html.parser')
        self.assertEqual(response.status_code,200)
        #3.3
        main_area = soup.find('div',id='main-area')
        self.assertIn(post_001.title,main_area.text)
        self.assertIn(post_002.title, main_area.text)
        #3.4
        self.assertNotIn('아직 게시물이 없습니다',main_area.text)

        self.assertIn(self.user_tjsgh.username.upper(),main_area.text)
        self.assertIn(self.user_seonho.username.upper(),main_area.text)


    def test_post_detail(self):
        #1.1
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World. We are the world.',
            author = self.user_tjsgh,
        )
        #1.2
        self.assertEqual(post_001.get_absolute_url(),'/blog/1/')

        #2.1
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content,'html.parser')

        #2.2
        self.navbar_test(soup)

        #2.3
        self.assertIn(post_001.title,soup.title.text)

        #2.4
        main_area = soup.find('div',id='main-area')
        post_area = main_area.find('div',id='post-area')
        self.assertIn(post_001.title,post_area.text)
        
        #2.5

        #2.6
        self.assertIn(post_001.content,post_area.text)

        self.assertIn(self.user_tjsgh.username.upper(), post_area.text)
