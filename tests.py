import unittest
import sqlite3
import random
import config
from faker import Faker


class Test(unittest.TestCase):
    def setUp(self):
        self.db = None
        try:
            self.db = sqlite3.connect(config.DB_NAME)
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
                          patronymic_name  TEXT ,
                          phone  TEXT,
                          email TEXT,
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
        regions = config.REGIONS_AND_CITIES

        cursor = self.db.cursor()
        i = 1
        # ------------ Добавление регионов и городов в region и city: ----------------------------------
        try:
            for key in regions.keys():
                cursor.execute('INSERT INTO region(name) VALUES(?);', (key,))
                for value in regions[key]:
                    print(key, value)
                    cursor.execute('INSERT INTO city(name, region_id) VALUES(?, ?);', (value, i))
                self.db.commit()
                i += 1
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during region insertion:', e)

        # ------------ Добавление пользователей в user: ----------------------------------
        try:
            for _ in range(10):
                surname = fake.last_name()
                name = fake.first_name()
                patronymic_name = "Отчество"
                phone = fake.phone_number()
                email = fake.safe_email()
                city_id = random.randint(1, 9)

                cursor.execute('''INSERT INTO user(surname, name, patronymic_name, phone, email, city_id) 
                                  VALUES(?, ?, ?, ?, ?, ?)''',
                               (surname, name, patronymic_name, phone, email, city_id))
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during user insertion:', e)


if __name__ == '__main__':
    unittest.main()
