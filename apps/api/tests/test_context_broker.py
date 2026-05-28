from atlas_api.services.context_broker import ContextBroker


def test_context_broker_limits_discussion_context():
    broker = ContextBroker()
    broker.discussion_max_chars = 100
    packet = broker.build_role_packet("discussion", "x" * 500)
    assert packet["max_chars"] == 100
    assert len(packet["content"]) == 100

