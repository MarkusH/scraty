from django.test import LiveServerTestCase
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .models import Card, Story, User


class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def go_to_board(self):
        self.selenium.get(self.live_server_url)
        return WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "board"))
        )

    def test_empty_board_renders(self):
        board = self.go_to_board()

        board_cols = board.find_elements_by_tag_name("col")
        self.assertEqual(len(board_cols), 5)
        self.assertEqual(board_cols[0].get_attribute("style"), "width: 200px;")
        self.assertEqual(board_cols[1].get_attribute("style"), "width: 25%;")
        self.assertEqual(board_cols[2].get_attribute("style"), "width: 25%;")
        self.assertEqual(board_cols[3].get_attribute("style"), "width: 25%;")
        self.assertEqual(board_cols[4].get_attribute("style"), "")

        rows = board.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].text, "Go Offline Todo In Progress Verify Done")

    def test_go_offline(self):
        self.go_to_board()
        story_obj = Story.objects.create(title="My first Story")

        WebDriverWait(self.selenium, 11).until(
            EC.presence_of_element_located((By.ID, story_obj.pk))
        )

        toggle_polling = self.selenium.find_element_by_name("toggle-polling")
        self.assertEqual(toggle_polling.text, "Go Offline")
        self.assertIn("success", toggle_polling.get_attribute("class"))
        toggle_polling.click()
        self.assertEqual(toggle_polling.text, "Go Online")
        self.assertIn("alert", toggle_polling.get_attribute("class"))

        card_obj = Card.objects.create(text="My first Task", story=story_obj)

        self.assertRaises(
            TimeoutException,
            WebDriverWait(self.selenium, 11).until,
            EC.presence_of_element_located((By.ID, card_obj.pk)),
        )

    def test_go_online(self):
        self.go_to_board()
        toggle_polling = self.selenium.find_element_by_name("toggle-polling")
        toggle_polling.click()
        self.assertEqual(toggle_polling.text, "Go Online")
        self.assertIn("alert", toggle_polling.get_attribute("class"))

        story_obj = Story.objects.create(title="My first Story")

        self.assertRaises(
            TimeoutException,
            WebDriverWait(self.selenium, 11).until,
            EC.presence_of_element_located((By.ID, story_obj.pk)),
        )

        toggle_polling.click()
        self.assertEqual(toggle_polling.text, "Go Offline")
        self.assertIn("success", toggle_polling.get_attribute("class"))

        WebDriverWait(self.selenium, 11).until(
            EC.presence_of_element_located((By.ID, story_obj.pk))
        )

    def test_add_story_button_click(self):
        board = self.go_to_board()

        add_story_btn = self.selenium.find_element_by_id("add-story")
        add_story_btn.click()

        rows = board.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 2)
        story = rows[-1]
        story.find_element_by_name("title").send_keys("My first Story")
        story.find_element_by_name("link").send_keys("https://google.com")
        story.find_element_by_name("save").click()

        story_obj = Story.objects.get()
        self.assertEqual(story_obj.title, "My first Story")
        self.assertEqual(story_obj.link, "https://google.com")

        story = board.find_element_by_id(story_obj.pk)
        title = story.find_element_by_css_selector(".display .title")
        self.assertEqual(title.text, "My first Story")
        link = story.find_element_by_css_selector(".display .link a")
        self.assertEqual(link.text, "Link")
        self.assertEqual(link.get_attribute("href"), "https://google.com/")

    def test_add_story_button_click_twice_empty(self):
        """
        Clicking the "Add a story" button twice should not add two empty rows
        with story forms.
        """
        board = self.go_to_board()

        add_story_btn = self.selenium.find_element_by_id("add-story")
        add_story_btn.click()
        self.assertEqual(len(board.find_elements_by_tag_name("tr")), 2)
        add_story_btn.click()
        self.assertEqual(len(board.find_elements_by_tag_name("tr")), 2)

    def test_add_story_button_click_twice(self):
        """
        Clicking the "Add a story" button twice should only add another empty
        row when the previous story was saved.
        """
        board = self.go_to_board()

        add_story_btn = self.selenium.find_element_by_id("add-story")
        add_story_btn.click()

        story = board.find_elements_by_tag_name("tr")[1]
        story.find_element_by_name("title").send_keys("My first Story")
        story.find_element_by_name("save").click()
        add_story_btn.click()
        self.assertEqual(len(board.find_elements_by_tag_name("tr")), 3)

    def test_add_card(self):
        story_obj = Story.objects.create(title="My first Story")
        User.objects.create(name="Jane", color="55d4f5")

        board = self.go_to_board()

        story = board.find_element_by_id(story_obj.pk)
        story.find_element_by_name("new-card").click()
        card = board.find_element_by_class_name("card")
        card.find_element_by_name("text").send_keys("My first Task")
        card.find_element_by_name("user").send_keys("Jane")
        card.find_element_by_name("save").click()

        card_obj = Card.objects.select_related("user").get()
        self.assertEqual(card_obj.text, "My first Task")
        self.assertEqual(card_obj.user.name, "Jane")
        self.assertEqual(card_obj.story_id, story_obj.pk)

        card = board.find_element_by_id(card_obj.pk)
        self.assertEqual(
            card.get_attribute("style"), "background-color: rgb(85, 212, 245);"
        )
        title = card.find_element_by_css_selector(".display .text")
        self.assertEqual(title.text, "My first Task")
        link = story.find_element_by_css_selector(".display .user")
        self.assertEqual(link.text, "Jane")
