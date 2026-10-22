import sqlite3
import unittest
from incidentdesk import add_incident, html_report, initialize, list_incidents, update_status


class IncidentDeskTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        initialize(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_and_update(self):
        incident_id = add_incident(self.conn, 'Teste de alerta', 'high')
        self.assertTrue(update_status(self.conn, incident_id, 'resolved'))
        self.assertEqual(len(list_incidents(self.conn, 'resolved')), 1)

    def test_rejects_invalid_severity(self):
        with self.assertRaises(ValueError):
            add_incident(self.conn, 'Teste', 'urgent')

    def test_escapes_html(self):
        add_incident(self.conn, '<script>alert(1)</script>', 'low')
        output = html_report(list_incidents(self.conn))
        self.assertIn('&lt;script&gt;', output)
        self.assertNotIn('<script>', output)


if __name__ == '__main__':
    unittest.main()
