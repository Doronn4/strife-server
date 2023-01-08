import sqlite3
import datetime


class DBHandler:
    """
    Class for handling the server's database
    """

    def __init__(self, db_name):
        # The database's name
        self.db_name = db_name
        # Connect to the database file
        self.con = sqlite3.connect(self.db_name + '.db')
        self.cursor = self.con.cursor()

        # Create the tables
        self._create_users_table()
        self._create_groups_table()
        self._create_participants_table()
        self._create_files_table()
        self._create_messages_table()

        # Default profile pic and status for new users
        self.DEFAULT_PROFILE_PICTURE = '\\default_pic.png'
        self.DEFAULT_STATUS = 'I love strife!'

        # Exceptions
        self.GROUP_DOESNT_EXIST_EXCEPTION = Exception("Group doesn't exist in the database.")
        self.NOT_ENOUGH_PARAMETERS_EXCEPTION = Exception('Not enough parameters given.')
        self.USER_DOESNT_EXIST_EXCEPTION = Exception("User doesn't exist.")

    def _create_users_table(self):
        """
        Creates the users table in the db
        :return:-
        """
        # TODO: Check what type the password (hashed) field needs to be
        sql = f"CREATE TABLE IF NOT EXISTS users_table (" \
              f"unique_id INTEGER PRIMARY KEY," \
              f" username TEXT," \
              f" password CHAR(64)," \
              f" picture TEXT, " \
              f"status TEXT) "
        self.cursor.execute(sql)

    def _create_groups_table(self):
        """
        Creates the groups table in the db
        :return:-
        """
        sql = f"CREATE TABLE IF NOT EXISTS groups_table (" \
              f"chat_id INTEGER PRIMARY KEY," \
              f" group_name TEXT," \
              f" date_of_creation DATE) "
        self.cursor.execute(sql)

    def _create_participants_table(self):
        """
        Creates the participants table in the db
        :return: -
        """
        sql = f"CREATE TABLE IF NOT EXISTS participants_table (" \
              f"participant_unique_id INT," \
              f" chat_id INT)"
        self.cursor.execute(sql)

    def _create_files_table(self):
        """
        Creates the files table in the db
        :return: -
        """
        sql = f"CREATE TABLE IF NOT EXISTS files_table (" \
              f"file_name TEXT," \
              f" chat_id INT," \
              f" file_hash CHAR(64))"
        self.cursor.execute(sql)

    def _create_messages_table(self):
        """
        Creates the messages table in the db
        :return: -
        """
        # TODO: Check what type the message field needs to be
        sql = f"CREATE TABLE IF NOT EXISTS messages_table (" \
              f"chat_id INT," \
              f" timestamp TIMESTAMP," \
              f" sender_unique_id INT, " \
              f"message TEXT) "
        self.cursor.execute(sql)

    def add_user(self, username, password):
        """
        Adds a user to the users table.
        :param username: The user's username
        :param password: The user's password
        :return: True if the user was added, false if not
        """
        flag = True

        # Check if the username already exists
        if self._user_exists(username):
            flag = False
        else:
            sql = f"INSERT INTO users_table (username, password, picture, status) " \
                  f"VALUES ('{username}', '{password}', '{self.DEFAULT_PROFILE_PICTURE}', '{self.DEFAULT_STATUS}') "
            self.cursor.execute(sql)
            self.con.commit()

        return flag

    def _user_exists(self, username):
        """
        Checks if a user exists on the database by his username
        :param username: The username
        :return: True if exists of False if not
        """
        sql = f"SELECT * from users_table WHERE username='{username}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return len(result) == 1

    def update_user_password(self, username, new_password):
        """
        Updates a user’s password
        :param username: The user's username
        :param new_password: The user's new password
        :return: -
        """

        # Check if user exists
        if not self._user_exists(username):
            raise self.USER_DOESNT_EXIST_EXCEPTION

        else:
            sql = f"UPDATE users_table SET password='{new_password}' WHERE username='{username}'"
            self.cursor.execute(sql)
            self.con.commit()

    def update_user_picture(self, username, picture_path):
        """
        Updates a user’s password
        :param username: The user's username
        :param picture_path: The path of the new profile picture
        :return: -
        """
        # Check if user exists
        if not self._user_exists(username):
            raise self.USER_DOESNT_EXIST_EXCEPTION

        else:
            sql = f"UPDATE users_table SET picture='{picture_path}' WHERE username='{username}'"
            self.cursor.execute(sql)
            self.con.commit()

    def update_user_status(self, username, new_status):
        """
        Updates a user’s status
        :param username: The user's username
        :param new_status: The new status
        :return: -
        """
        # Check if user exists
        if not self._user_exists(username):
            raise self.USER_DOESNT_EXIST_EXCEPTION

        else:
            sql = f"UPDATE users_table SET status='{new_status}' WHERE username='{username}'"
            self.cursor.execute(sql)
            self.con.commit()

    def create_group(self, group_name) -> int:
        """
        Create a new group in the database
        :param group_name: The group's name
        :return: The created group's chat id
        """
        # Get the date of today
        date_now = datetime.date.today()
        # Add the group to the groups table
        sql = f"INSERT INTO groups_table (group_name, date_of_creation) VALUES ('{group_name}', '{date_now}')"
        self.cursor.execute(sql)
        self.con.commit()
        # Get the group id
        sql = f"SELECT chat_id from groups_table WHERE group_name ='{group_name}' AND date_of_creation ='{date_now}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()[-1][0]
        return result

    def add_to_group(self, chat_id, username):
        """
        Adds a user to a group
        :param chat_id: The chat id of the group
        :param username: The user's username
        :return: True if the user was added to the group, false if not.
        """
        flag = True
        unique_id = self._get_unique_id(username)

        # If the username doesn't exist in the database
        if unique_id is None:
            flag = False

        # Check if the user is already in the group
        elif self._is_in_group(chat_id, unique_id=unique_id):
            flag = False

        else:
            sql = f"INSERT INTO participants_table (chat_id, participant_unique_id) VALUES ('{chat_id}', '{unique_id}')"
            self.cursor.execute(sql)
            self.con.commit()

        return flag

    def _is_in_group(self, chat_id, username=None, unique_id=None):
        """
        Check if a user is in a group
        :param chat_id: The chat id of the group
        :param username: The username
        :param unique_id: The unique id of the user
        :return: True if the user is in the group, false if not
        """
        # Check if either the username of the unique id were passed
        if unique_id is None and username is None:
            raise self.NOT_ENOUGH_PARAMETERS_EXCEPTION

        # Check if the group exists
        if not self._group_exists(chat_id):
            raise self.GROUP_DOESNT_EXIST_EXCEPTION

        # If only the username was passed, get the unique id of the user
        if unique_id is None:
            unique_id = self._get_unique_id(username)

        # If the username doesn't exist
        if unique_id is None:
            raise self.USER_DOESNT_EXIST_EXCEPTION

        sql = f"SELECT * from participants_table WHERE chat_id='{chat_id}' AND participant_unique_id='{unique_id}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return len(result) == 1

    def _get_unique_id(self, username):
        """
        Get the unique id of a user
        :param username: The user's username
        :return: The user's unique id (if the user exists - otherwise None)
        """
        result = None
        # Check if user exists
        if self._user_exists(username):

            sql = f"SELECT unique_id from users_table WHERE username='{username}'"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()[0][0]

        return result

    def _group_exists(self, chat_id):
        """
        Check if a group exists
        :param chat_id: The group's chat id
        :return: True if the group exists, false if not
        """
        sql = f"SELECT * from groups_table WHERE chat_id='{chat_id}'"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        return len(answer) == 1

    def add_file(self, chat_id, file_name, file_hash):
        if not self._group_exists(chat_id):
            raise self.GROUP_DOESNT_EXIST_EXCEPTION

        sql = f"INSERT INTO files_table (chat_id, file_name, file_hash) VALUES (" \
              f"'{chat_id}', '{file_name}', '{file_hash}')"
        self.cursor.execute(sql)
        self.con.commit()

    def add_message(self, chat_id, sender_username, message):
        if not self._group_exists(chat_id):
            raise self.GROUP_DOESNT_EXIST_EXCEPTION

        unique_id = self._get_unique_id(sender_username)
        if not unique_id:
            raise self.USER_DOESNT_EXIST_EXCEPTION

        timestamp = datetime.datetime.now()

        sql = f"INSERT INTO messages_table (chat_id, timestamp, sender_unique_id, message) VALUES (" \
              f"'{chat_id}', '{timestamp}', '{unique_id}', '{message}')"
        self.cursor.execute(sql)
        self.con.commit()

    def check_credentials(self, username, password) -> bool:
        """
        Checks if there username and the password match a record in the database
        :param username: The username
        :param password: The password
        :return: True if the username and password match, false if not
        """
        sql = f"SELECT * FROM users_table WHERE username='{username}' AND password='{password}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return len(result) == 1

    def get_chat_history(self, chat_id):
        """
        Get the chat history of a group/chat
        :param chat_id: The chat id
        :return: A list of
        """
        if not self._group_exists(chat_id):
            raise self.GROUP_DOESNT_EXIST_EXCEPTION

        sql = f"SELECT sender_unique_id, message FROM messages_table WHERE chat_id='{chat_id}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        return result


if __name__ == '__main__':
    # Test adding user and logging in
    my_db = DBHandler('test_db')
    my_db.add_user('doron', 'hello123')
    assert my_db.check_credentials('doron', 'hello123')

    # Test adding user to group
    chat_id = my_db.create_group('testimgroup')
    print(chat_id)
    my_db.add_to_group(chat_id, 'doron')

    # Test adding message in group
    my_db.add_message(chat_id, 'doron', 'first message!')
    print(my_db.get_chat_history(chat_id))

    # Creating another group
    new_chat_id = my_db.create_group('testimgroup')
    print(new_chat_id)
    assert new_chat_id != chat_id

    my_db.update_user_status('doron', 'pigs')


