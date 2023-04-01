from __future__ import unicode_literals
from .logic_adapter import LogicAdapter


class BestMatch(LogicAdapter):
    """
    A logic adater that returns a response based on known responses to
    the closest matches to the input statement.
    """

    def get(self, input_statement):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        statement_list = self.chatbot.storage.get_response_statements()

        if not statement_list:
            if not self.chatbot.storage.count():
                raise self.EmptyDatasetException()

            # Use a randomly picked statement
            self.logger.info(
                'No statements have known responses. ' +
                'Choosing a random response to return.'
            )
            random_response = self.chatbot.storage.get_random()
            random_response.confidence = 0
            return random_response
        closest_match = input_statement
        closest_match.confidence = 0

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)

            if confidence > closest_match.confidence:
                statement.confidence = confidence
                closest_match = statement

        return closest_match

    def can_process(self, statement):
        """
        Check that the chatbot's storage adapter is available to the logic
        adapter and there is at least one statement in the database.
        """
        return self.chatbot.storage.count()

    def process(self, input_statement):

        # Select the closest match to the input statement
        closest_match = self.get(input_statement)
        self.logger.info(
            f'Using "{input_statement.text}" as a close match to "{closest_match.text}"'
        )

        if response_list := self.chatbot.storage.filter(
            in_response_to__contains=closest_match.text
        ):
            self.logger.info(
                f'Selecting response from {len(response_list)} optimal responses.'
            )
            response = self.select_response(input_statement, response_list)
            response.confidence = closest_match.confidence
            self.logger.info(f'Response selected. Using "{response.text}"')
        else:
            response = self.chatbot.storage.get_random()
            self.logger.info(
                f'No response to "{closest_match.text}" found. Selecting a random response.'
            )

            # Set confidence to zero because a random response is selected
            response.confidence = 0

        return response
