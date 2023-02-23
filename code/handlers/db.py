import sqlite3
import datetime
import hashlib


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

        # The max length of a chat message
        self.MAX_MSG_LEN = 200  # Characters

        # Create the tables
        self._create_users_table()
        self._create_groups_table()
        self._create_participants_table()
        self._create_files_table()
        self._create_messages_table()
        self._create_friends_table()

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
        sql = f"CREATE TABLE IF NOT EXISTS messages_table (" \
              f"chat_id INT," \
              f" timestamp TIMESTAMP," \
              f" sender_unique_id INT, " \
              f" message varbinary({self.MAX_MSG_LEN}))"
        self.cursor.execute(sql)

    def _create_friends_table(self):
        sql = f"CREATE TABLE IF NOT EXISTS friends_table (" \
              f"user_id INT," \
              f" friend_id INT," \
              f" primary key (user_id, friend_id))"
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
            # Hash password

            data = [username, password]
            sql = f"INSERT INTO users_table (username, password, picture, status) " \
                  f"VALUES (?, ?, '{self.DEFAULT_PROFILE_PICTURE}', '{self.DEFAULT_STATUS}') "
            self.cursor.execute(sql, data)
            self.con.commit()

        return flag

    def _user_exists(self, username):
        """
        Checks if a user exists on the database by his username
        :param username: The username
        :return: True if exists of False if not
        """
        sql = f"SELECT * from users_table WHERE username=?"
        self.cursor.execute(sql, [username])
        result = self.cursor.fetchall()
        return len(result) == 1

    def _user_exists_id(self, user_id):
        """
        Check if a user exists in the database by his id
        :param user_id: The user's id
        :return: True if exists, false if doesn't
        """
        sql = f"SELECT * from users_table WHERE unique_id=?"
        self.cursor.execute(sql, [user_id])
        result = self.cursor.fetchall()
        return len(result) == 1

    def add_friend(self, username, friend):
        """
        Add a pair of friends to the friends table
        :param username: The username of the first friends
        :param friend: The username of the second friend
        :return:
        """
        user_id = self._get_unique_id(username)
        friend_id = self._get_unique_id(friend)

        if not user_id or not friend_id:
            raise self.USER_DOESNT_EXIST_EXCEPTION

        if not self._are_friends(user_id, friend_id):
            data = [user_id, friend_id]
            sql = f"INSERT INTO friends_table (user_id, friend_id) " \
                  f"VALUES (?, ?)"
            self.cursor.execute(sql, data)
            self.con.commit()

    def remove_friend(self, username, friend):
        """
        Remove a pair of friends from the database
        :param username: The username of the first friend
        :param friend: The username of the second friend
        :return: -
        """
        user_id = self._get_unique_id(username)
        friend_id = self._get_unique_id(friend)

        if not user_id or not friend_id:
            raise self.USER_DOESNT_EXIST_EXCEPTION

        if self._are_friends(user_id, friend_id):
            data = [user_id, friend_id, user_id, friend_id]
            sql = "DELETE FROM friends_table " \
                  "WHERE (user_id=? AND friend_id=?) OR (friend_id=? AND user_id=?)"
            self.cursor.execute(sql, data)
            self.con.commit()

    def _are_friends(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are friends
        :param user1_id: First user's id
        :param user2_id: Seconds user's id
        :return: True if they are friends or false if not
        """
        data = [user1_id, user2_id, user1_id, user2_id]
        sql = f"SELECT * from friends_table WHERE" \
            f" (user_id=? AND friend_id=?)" \
            f" OR" \
            f" (friend_id=? AND user_id=?)"
        self.cursor.execute(sql, data)
        result = self.cursor.fetchall()
        return len(result) == 1

    def get_friends_of(self, username) -> list:
        """
        Get the friends of a user
        :param username: The username
        :return: A list of the user's friends usernames
        """
        user_id = self._get_unique_id(username)
        data = [user_id, user_id]
        sql = f"SELECT * from friends_table WHERE user_id=? OR friend_id=?"
        self.cursor.execute(sql, data)
        results = self.cursor.fetchall()

        friends = []
        for result in results:
            friend_id = result[0] if result[0] != user_id else result[1]
            friends.append(self._get_username(friend_id))

        return friends

    def _get_username(self, user_id: int):
        """
        Get a username of a user by his id
        :param user_id: The user's id
        :return: The username of the user
        """
        username = None

        if self._user_exists_id(user_id):
            sql = f"SELECT username from users_table WHERE unique_id=?"
            self.cursor.execute(sql, [user_id])
            username = self.cursor.fetchall()[0][0]

        return username

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
            data = [new_password, username]
            sql = f"UPDATE users_table SET password=? WHERE username=?"
            self.cursor.execute(sql, data)
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
            data = [picture_path, username]
            sql = f"UPDATE users_table SET picture=? WHERE username=?"
            self.cursor.execute(sql, data)
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
            data = [new_status, username]
            sql = f"UPDATE users_table SET status=? WHERE username=?"
            self.cursor.execute(sql, data)
            self.con.commit()

    def create_group(self, group_name, creator) -> int:
        """
        Create a new group in the database
        :param group_name: The group's name
        :param creator
        :return: The created group's chat id
        """
        # Get the date of today
        date_now = datetime.date.today()
        data = [group_name, date_now]
        # Add the group to the groups table
        sql = f"INSERT INTO groups_table (group_name, date_of_creation) VALUES (?, ?)"
        self.cursor.execute(sql, data)
        self.con.commit()
        # Get the group id
        sql = f"SELECT chat_id from groups_table WHERE group_name =? AND date_of_creation =?"
        self.cursor.execute(sql, data)
        result = self.cursor.fetchall()[-1][0]

        # Add the creator of the group to it
        self._add_to_group(result, creator)

        return result

    def get_group_name(self, chat_id):
        result = None
        if self._group_exists(chat_id):
            sql = f"SELECT group_name from groups_table WHERE chat_id =?"
            self.cursor.execute(sql, [chat_id])
            result = self.cursor.fetchall()[0][0]

        return result

    def add_to_group(self, chat_id, adder, username):
        """
        Adds a user to a group
        :param chat_id: The chat id of the group
        :param adder: The user that added the user to the group
        :param username: The user's username
        :return: True if the user was added to the group, false if not.
        """
        flag = True
        unique_id = self._get_unique_id(username)

        # If the username doesn't exist in the database
        if unique_id is None:
            flag = False

        # The adder is not in the group
        elif not self._is_in_group(chat_id, username=adder):
            flag = False

        # Check if the user is already in the group
        elif self._is_in_group(chat_id, unique_id=unique_id):
            flag = False

        else:
            sql = f"INSERT INTO participants_table (chat_id, participant_unique_id) VALUES (?, ?)"
            self.cursor.execute(sql, [chat_id, unique_id])
            self.con.commit()

    def _add_to_group(self, chat_id, username):
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

        data = [chat_id, unique_id]
        sql = f"SELECT * from participants_table WHERE chat_id=? AND participant_unique_id=?"
        self.cursor.execute(sql, data)
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

            sql = f"SELECT unique_id from users_table WHERE username=?"
            self.cursor.execute(sql, [username])
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

        data = [chat_id, file_name, file_hash]
        sql = f"INSERT INTO files_table (chat_id, file_name, file_hash) VALUES (" \
              f"?, ?, ?)"
        self.cursor.execute(sql, data)
        self.con.commit()

    def add_message(self, chat_id, sender_username, message: bytes):
        if not self._group_exists(chat_id):
            raise self.GROUP_DOESNT_EXIST_EXCEPTION

        unique_id = self._get_unique_id(sender_username)
        if not unique_id:
            raise self.USER_DOESNT_EXIST_EXCEPTION

        timestamp = datetime.datetime.now()

        data = [chat_id, timestamp, unique_id, message]

        sql = f"INSERT INTO messages_table (chat_id, timestamp, sender_unique_id, message) VALUES (" \
              f"?, ?, ?, ?)"
        self.cursor.execute(sql, data)
        self.con.commit()

    def check_credentials(self, username, password) -> bool:
        """
        Checks if there username and the password match a record in the database
        :param username: The username
        :param password: The password
        :return: True if the username and password match, false if not
        """
        data = [username, password]
        sql = f"SELECT * FROM users_table WHERE username=? AND password=?"
        self.cursor.execute(sql, data)
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
    my_db.add_user('doron2', '123')
    my_db.add_user('itay3108', 'dwkodkw')
    my_db.add_user('itamar', '1234j')

    my_db.add_friend('doron2', 'itay3108')
    my_db.add_friend('doron2', 'itamar')
    print(my_db.get_friends_of('doron2'))

