from __future__ import annotations

from typing import Any, List

from raindrop_digest.summarizer import Summarizer


class FakeOpenAI:
    def __init__(self):
        self.last_messages: List[Any] | None = None
        self.chat = self.Chat(self)

    class Chat:
        def __init__(self, outer: "FakeOpenAI"):
            self.completions = outer.Completions(outer)

    class Completions:
        def __init__(self, outer: "FakeOpenAI"):
            self._outer = outer

        def create(self, model, messages, temperature):
            self._outer.last_messages = messages

            class Choice:
                def __init__(self):
                    self.message = type("msg", (), {"content": "dummy"})

            class Response:
                def __init__(self):
                    self.choices = [Choice()]

            return Response()


def test_sends_user_content_as_plain_text():
    fake_client = FakeOpenAI()
    s = Summarizer(api_key="dummy", model="gpt-4.1-mini", client=fake_client)
    s.summarize("短いテキスト")
    user_content = fake_client.last_messages[1]["content"]  # type: ignore[index]
    assert user_content == "短いテキスト"


def test_openai_retry_on_503():
    class E(Exception):
        def __init__(self):
            self.status_code = 503

    class FlakyOpenAI(FakeOpenAI):
        def __init__(self):
            super().__init__()
            self.calls = 0
            self.chat = self.Chat(self)

        class Completions(FakeOpenAI.Completions):
            def create(self, model, messages, temperature):
                self._outer.calls += 1
                if self._outer.calls == 1:
                    raise E()
                return super().create(model, messages, temperature)

    fake_client = FlakyOpenAI()
    s = Summarizer(api_key="dummy", model="gpt-4.1-mini", client=fake_client)
    assert s.summarize("短いテキスト") == "dummy"
