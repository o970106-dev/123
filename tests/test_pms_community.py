import unittest
import os
import sys

# Mock Odoo Environment for testing logic
class MockModel:
    def search(self, domain, limit=None):
        return []
    def create(self, vals):
        return self

class TestPmsCommunity(unittest.TestCase):

    def test_knowledge_structure(self):
        """Test if the knowledge base structure is correct."""
        from odoo.addons.pms_community.models.knowledge import PmsKnowledge
        # We just check the class exists and has fields defined
        self.assertTrue(hasattr(PmsKnowledge, 'name'))
        self.assertTrue(hasattr(PmsKnowledge, 'category'))

    def test_chat_ai_trigger(self):
        """Test if chat messages with '小J' trigger AI responses (logic check)."""
        from odoo.addons.pms_community.models.chat import PmsCommunityChat
        # Mocking the Odoo environment for logic verification
        class DummyChat(PmsCommunityChat):
            def __init__(self):
                self.messages = []
            def create(self, vals):
                self.messages.append(vals)
                class Record:
                    def __init__(self, partner_id, message, create_date):
                        self.partner_id = Record.Partner(partner_id)
                        self.message = message
                        self.create_date = create_date
                    class Partner:
                        def __init__(self, id): self.name = "Test Partner"
                return Record(vals.get('partner_id'), vals.get('message'), "2026-01-28")
            def env_ref(self, ref):
                return type('obj', (), {'id': 1})
            @property
            def env(self):
                return self
            def ref(self, ref):
                return type('obj', (), {'id': 1})

        chat = DummyChat()
        chat.post_message("你好小J")
        self.assertTrue(any("助手小J" in m['message'] for m in chat.messages))

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'odoo19-shadow/addons'))
    unittest.main()
