from unittest.main import main
from django.http import response
from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from .models import Post, Category, Tag

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_tjsgh = User.objects.create_user(username='tjsgh',password='somepassword')
        self.user_seonho = User.objects.create_user(username='seonho',password='somepassword')
        self.user_tjsgh.is_staff = True
        self.user_tjsgh.save()
        self.category_programming = Category.objects.create(name='programming',slug='programming')
        self.category_music = Category.objects.create(name='music',slug='music')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')
      
        self.post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = "Hello World. We are the World",
            category = self.category_programming,
            author  = self.user_tjsgh,
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content = '1등이 전부는 아니잖아요?',
            category = self.category_music,
            author = self.user_seonho,
        )
        self.post_003 = Post.objects.create(
            title = '세 번째 포스트입니다.',
            content = '카테고리가 없소요.',
            author = self.user_tjsgh,
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)


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

    def category_card_test(self,soup):
        categories_card = soup.find('div',id='categories-card')
        self.assertIn('Categories',categories_card.text)
        self.assertIn(f'{self.category_programming.name}({self.category_programming.post_set.count()})',categories_card.text)
        self.assertIn(f'{self.category_music.name}({self.category_music.post_set.count()})',categories_card.text)
        self.assertIn(f'미분류 (1)',categories_card.text)

    def test_post_list(self):
        #포스트가 있는 경우

        self.assertEqual(Post.objects.count(),3)
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div',id='main-area')
        self.assertNotIn('아직 게시물이 없습니다',main_area.text)
        
        post_001_card = main_area.find('div',id='post-1')
        self.assertIn(self.post_001.title,post_001_card.text)
        self.assertIn(self.post_001.category.name,post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div',id='post-2')
        self.assertIn(self.post_002.title,post_002_card.text)
        self.assertIn(self.post_002.category.name,post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div',id='post-3')
        self.assertIn('미분류',post_003_card.text)
        self.assertIn(self.post_003.title,post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_tjsgh.username.upper(),main_area.text)
        self.assertIn(self.user_seonho.username.upper(),main_area.text)

        #포스트가 없는 경우

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content,'html.parser')

        main_area = soup.find('div',id='main-area')
        self.assertIn('아직 게시물이 없습니다.',main_area.text)


    def test_post_detail(self):
        #1.1
        #1.2
        self.assertEqual(self.post_001.get_absolute_url(),'/blog/1/')

        #2.1
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content,'html.parser')

        #2.2
        self.navbar_test(soup)
        self.category_card_test(soup)

        #2.3
        self.assertIn(self.post_001.title,soup.title.text)

        #2.4
        main_area = soup.find('div',id='main-area')
        post_area = main_area.find('div',id='post-area')
        self.assertIn(self.post_001.title,post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        
        #2.5

        #2.6
        self.assertIn(self.post_001.content,post_area.text)
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        self.assertIn(self.user_tjsgh.username.upper(), post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
        
    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        response = self.client.get('/blog/create_post')
        self.assertNotEqual(response.status_code,200)

        self.client.login(username='seonho', password ='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='tjsgh', password='somepassword')

        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content':'Post Form 페이지를 만듭시다.',
                'tags_str':'new tag; 한글 태그, python'
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title,"Post Form 만들기")
        self.assertEqual(last_post.author.username, 'tjsgh')

        self.assertEqual(last_post.tags.count(),3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(),5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 x
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        #로그인 o 작성자가 x
        self.assertNotEqual(self.post_003.author, self.user_seonho)
        self.client.login(
            username = self.user_seonho.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        #작성자
        self.client.login(
            username=self.post_003.author.username,
            password='somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post',main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부;python', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title':'세 번째 포스트를 수정했습니다.',
                'content':'안녕 세계? 우린 하나!',
                'category':self.category_music.pk,
                'tags_str':'파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div',id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.',main_area.text)
        self.assertIn('안녕 세계? 우린 하나!',main_area.text)
        self.assertIn(self.category_music.name,main_area.text)
        self.assertIn('파이썬 공부',main_area.text)
        self.assertIn('some tag',main_area.text)
        self.assertIn('한글 태그',main_area.text)
        self.assertNotIn('python',main_area.text)