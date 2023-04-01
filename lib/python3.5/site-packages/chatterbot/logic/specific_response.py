from __future__ import unicode_literals
from .logic_adapter import LogicAdapter


class SpecificResponseAdapter(LogicAdapter):
    """
    Return a specific response to a specific input.
    """

    def __init__(self, **kwargs):
        super(SpecificResponseAdapter, self).__init__(**kwargs)
        from chatterbot.conversation import Statement

        self.input_text = kwargs.get('input_text')

        output_text = kwargs.get('output_text')
        self.response_statement = Statement(output_text)

    def can_process(self, statement):
        return statement == self.input_text

    def process(self, statement):

        self.response_statement.confidence = 1 if statement == self.input_text else 0
        return self.response_statement
