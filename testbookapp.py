import unittest
import app as appModule
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

#Grap book review app
app = appModule.app

# Set app to use local mongoDB database
app.config.update({
    'TESTING': True,
    'WTF_CSRF_ENABLED': False,
    'MONGO_URI': 'mongodb://localhost:27017/testBookDb'})

mongo = PyMongo(app)  # setup PyMongo object
appModule.mongo = mongo  # overwrite app.py mongo object with this modifed version


class MongoDbTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client(self)

    def tearDown(self):
        # Remove all test database entries
        mongo.db.books.delete_many({})

    def test_insert_book(self):
        # Test when book inserted its contents appears on viewbooks.html
        self.app.post('insert_book', follow_redirects=True, data=dict(title= 'my test title',
                                                               author= 'author test',
                                                               rating= '5',
                                                               reviews= [],
                                                               link= 'www.testlink.com',
                                                               buy_link= 'www.testbuylink.com',
                                                               genre= 'test genre',
                                                               summary= 'test summary'))
        response = self.app.get("/")
        self.assertTrue(b'my test title' in response.data)
        self.assertTrue(b'Author Test' in response.data)
        self.assertTrue(b'www.testlink.com' in response.data)
        self.assertTrue(b'www.testbuylink.com' in response.data)
        self.assertTrue(b'test summary' in response.data)


class AppRouteTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client(self)

    def tearDown(self):
        # Remove all test database entries
        mongo.db.books.delete_many({})

    def test_index_page(self):
        # Check index loads with content
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        # Turn searched message into bytes literal and find in response
        self.assertTrue(b'Click a cover for more info' in response.data)

    def test_add_book_page(self):
        # Check addbook.html loads with content
        response = self.app.get("/add_book")
        self.assertEqual(response.status_code, 200)
        # Turn searched message into bytes literal and find in response
        self.assertTrue(b'Add a book' in response.data)

    def test_add_review_page(self):
        # Add test book to database and get its id
        add_test_book_to_db()
        book = mongo.db.books.find({'title': 'my test title'})[0]
        bookId = (book['_id'])
        # Check addreview.html page loads with content from given book id
        response = self.app.get("/add_review/{}".format(bookId))
        self.assertEqual(response.status_code, 200)
        # Turn searched message into bytes literal and find in response
        self.assertTrue(b'Write a review for' in response.data)


class TestReviewScoreValidation(unittest.TestCase):

    def test_score_too_high(self):
        result = appModule.check_review_score(90)
        self.assertEqual(result, 10)


def add_test_book_to_db():
    mongo.db.books.insert_one({'title': 'my test title',
                               'author': 'author test',
                               'rating': 0,
                               'link': 'www.testlink.com',
                               'buy_link': 'www.testbuylink.com',
                               'genre': 'test genre',
                               'summary': 'test summary',
                               'reviews': []})


#Look inside database TEMP
books = mongo.db.books.find()
for each in books:
    print(each)
colls = mongo.db.list_collection_names()
for each in colls:
    print(each)
print('')

if __name__ == "__main__":
    unittest.main