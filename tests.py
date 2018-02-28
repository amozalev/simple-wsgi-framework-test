import unittest
import sqlite3
import random
from faker import Faker


class Test(unittest.TestCase):
    def setUp(self):
        self.db = None
        try:
            self.db = sqlite3.connect('sqlite.db')
        except sqlite3.Error:
            print("Error")
        cursor = self.db.cursor()
        cursor.execute('DROP TABLE IF EXISTS user')
        cursor.execute('DROP TABLE IF EXISTS region')
        cursor.execute('DROP TABLE IF EXISTS city')
        cursor.execute('DROP TABLE IF EXISTS comment')

        cursor.execute('''CREATE TABLE user(
                          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          surname TEXT NOT NULL ,
                          name TEXT NOT NULL ,
                          patronymic_name  TEXT NOT NULL ,
                          phone  TEXT NOT NULL ,
                          email TEXT NOT NULL,
                          city_id INTEGER,
                          CONSTRAINT fk_city
                          FOREIGN KEY (city_id)
                          REFERENCES city(id)
                      );''')
        cursor.execute('''CREATE TABLE region(
                          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          name TEXT NOT NULL
                      );''')
        cursor.execute('''CREATE TABLE city(
                          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          name TEXT NOT NULL,
                          region_id INTEGER NOT NULL,
                          CONSTRAINT fk_region
                          FOREIGN KEY (region_id)
                          REFERENCES region(id)
                      );''')
        cursor.execute('''CREATE TABLE comment(
                          id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          body TEXT NOT NULL,
                          user_id INTEGER NOT NULL,
                          CONSTRAINT fk_user
                          FOREIGN KEY (user_id)
                          REFERENCES user(id)
                      );''')

    def tearDown(self):
        pass

    def test_insert_fake_data(self):
        fake = Faker('ru_RU')
        regions = {'Краснодарский край': 0, 'Ростовская область': 1, 'Ставропольский край': 2}

        cursor = self.db.cursor()
        # ------------ Добавление регионов в region: ----------------------------------
        try:
            for key in regions.keys():
                cursor.execute('INSERT INTO region(name) VALUES(?);', (key,))
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during region insertion:', e)

        # ------------ Добавление нас. пунктов в city: ----------------------------------
        try:
            for _ in range(10):
                city = fake.city()
                region_id = random.randint(1, len(regions))

                cursor.execute('INSERT INTO city(name, region_id) VALUES(?, ?);', (city, region_id))
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during city insertion:', e)

        # ------------ Добавление пользователей в user: ----------------------------------
        try:
            for _ in range(10):
                surname = fake.last_name()
                name = fake.first_name()
                patronymic_name = "Отчество"
                phone = fake.phone_number()
                email = fake.safe_email()
                city_id = random.randint(1, 10)

                cursor.execute('''INSERT INTO user(surname, name, patronymic_name, phone, email, city_id) 
                                  VALUES(?, ?, ?, ?, ?, ?)''',
                               (surname, name, patronymic_name, phone, email, city_id))
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during user insertion:', e)


if __name__ == '__main__':
    unittest.main()
