from __future__ import unicode_literals
from chatterbot.adapters import Adapter


class InputAdapter(Adapter):
    """
    This is an abstract class that represents the
    interface that all input adapters should implement.
    """

    def process_input(self, *args, **kwargs):
        """
        Returns a statement object based on the input source.
        """
        raise self.AdapterMethodNotImplementedError()

    def process_input_statement(self, *args, **kwargs):
        """
        Return an existing statement object (if one exists).
        """
        input_statement = self.process_input(*args, **kwargs)
        self.logger.info(f'Recieved input statement: {input_statement.text}')

        if existing_statement := self.chatbot.storage.find(input_statement.text):
            self.logger.info(f'"{input_statement.text}" is a known statement')
            input_statement = existing_statement
        else:
            self.logger.info(f'"{input_statement.text}" is not a known statement')

        return input_statement
