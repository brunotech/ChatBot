from __future__ import unicode_literals
from time import sleep
from chatterbot.input import InputAdapter
from chatterbot.conversation import Statement


class Gitter(InputAdapter):
    """
    An input adapter that allows a ChatterBot instance to get
    input statements from a Gitter room.
    """

    def __init__(self, **kwargs):
        super(Gitter, self).__init__(**kwargs)

        self.gitter_host = kwargs.get('gitter_host', 'https://api.gitter.im/v1/')
        self.gitter_room = kwargs.get('gitter_room')
        self.gitter_api_token = kwargs.get('gitter_api_token')
        self.only_respond_to_mentions = kwargs.get('gitter_only_respond_to_mentions', True)
        self.sleep_time = kwargs.get('gitter_sleep_time', 4)

        authorization_header = f'Bearer {self.gitter_api_token}'

        self.headers = {
            'Authorization': authorization_header,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Join the Gitter room
        room_data = self.join_room(self.gitter_room)
        self.room_id = room_data.get('id')

        user_data = self.get_user_data()
        self.user_id = user_data[0].get('id')
        self.username = user_data[0].get('username')

    def _validate_status_code(self, response):
        code = response.status_code
        if code not in [200, 201]:
            raise self.HTTPStatusException(f'{code} status code recieved')

    def join_room(self, room_name):
        """
        Join the specified Gitter room.
        """
        import requests

        endpoint = f'{self.gitter_host}rooms'
        response = requests.post(
            endpoint,
            headers=self.headers,
            json={'uri': room_name}
        )
        self.logger.info(f'{response.status_code} joining room {endpoint}')
        self._validate_status_code(response)
        return response.json()

    def get_user_data(self):
        import requests

        endpoint = f'{self.gitter_host}user'
        response = requests.get(
            endpoint,
            headers=self.headers
        )
        self.logger.info(f'{response.status_code} retrieving user data {endpoint}')
        self._validate_status_code(response)
        return response.json()

    def mark_messages_as_read(self, message_ids):
        """
        Mark the specified message ids as read.
        """
        import requests

        endpoint = f'{self.gitter_host}user/{self.user_id}/rooms/{self.room_id}/unreadItems'
        response = requests.post(
            endpoint,
            headers=self.headers,
            json={'chat': message_ids}
        )
        self.logger.info(f'{response.status_code} marking messages as read {endpoint}')
        self._validate_status_code(response)
        return response.json()

    def get_most_recent_message(self):
        """
        Get the most recent message from the Gitter room.
        """
        import requests

        endpoint = f'{self.gitter_host}rooms/{self.room_id}/chatMessages?limit=1'
        response = requests.get(
            endpoint,
            headers=self.headers
        )
        self.logger.info(f'{response.status_code} getting most recent message')
        self._validate_status_code(response)
        return data[0] if (data := response.json()) else None

    def _contains_mention(self, mentions):
        return any(self.username == mention.get('screenName') for mention in mentions)

    def should_respond(self, data):
        """
        Takes the API response data from a single message.
        Returns true if the chat bot should respond.
        """
        if data:
            unread = data.get('unread', False)

            if self.only_respond_to_mentions:
                return bool(unread and self._contains_mention(data['mentions']))
            elif unread:
                return True

        return False

    def remove_mentions(self, text):
        """
        Return a string that has no leading mentions.
        """
        import re
        text_without_mentions = re.sub(r'@\S+', '', text)

        # Remove consecutive spaces
        text_without_mentions = re.sub(' +', ' ', text_without_mentions.strip())

        return text_without_mentions

    def process_input(self, statement):
        new_message = False

        while not new_message:
            data = self.get_most_recent_message()
            if self.should_respond(data):
                self.mark_messages_as_read([data['id']])
                new_message = True
            sleep(self.sleep_time)

        text = self.remove_mentions(data['text'])
        statement = Statement(text)

        return statement

    class HTTPStatusException(Exception):
        """
        Exception raised when unexpected non-success HTTP
        status codes are returned in a response.
        """

        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)
