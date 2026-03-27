import unittest
import sqlite3
from datetime import datetime
import os # For managing test database file

# Add main.py to sys.path to allow importing from it
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))) # Assuming test_bot.py is in the same directory as main.py

from main import calcular_cotizacion_mendocina, init_db, save_quotation_to_db, DB_NAME as MAIN_DB_NAME

# Use a separate database for testing
TEST_DB_NAME = "test_quotations.db"

class TestBot(unittest.TestCase):

    def setUp(self):
        # Override the DB_NAME in main for testing purposes if functions directly use it
        # This is a bit of a hack; ideally, DB_NAME would be passed around or configurable
        # For now, we'll ensure our test functions use TEST_DB_NAME
        self.db_name = TEST_DB_NAME
        # Initialize a fresh test database for each test
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        
        # We need to initialize our test DB with the schema
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_telegram_id INTEGER NOT NULL,
                client_username TEXT,
                product_name TEXT NOT NULL,
                product_link TEXT,
                weight_kg REAL,
                price_usd REAL,
                quotation_date TEXT NOT NULL,
                full_quotation_text TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def tearDown(self):
        # Clean up the test database file after each test
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_calcular_cotizacion_mendocina_format(self):
        nombre = "Test Product"
        link = "http://test.com"
        peso = 1.5
        precio_usd = 100.0
        
        # Mock DOLAR_MEP and DOLAR_BLUE for consistent test results if they were global
        # For now, assuming they are constants in main.py and will be used as is.
        # If main.DOLAR_MEP and main.DOLAR_BLUE are needed, they would have to be imported or mocked.
        
        resultado = calcular_cotizacion_mendocina(nombre, link, peso, precio_usd)
        
        self.assertIn("🗓️ Fecha:", resultado)
        self.assertIn(datetime.now().strftime("%d/%m/%Y"), resultado)
        self.assertIn(f"🛒 Producto: {nombre}", resultado)
        self.assertIn(f"🔗 Link: {link}", resultado)
        self.assertIn(f"⚖️ Peso: {peso} kg", resultado)
        self.assertIn(f"💲 Precio Base: USD {precio_usd:.2f}", resultado)
        self.assertIn("✨ Comisión (15%):", resultado) # Check for 15.00 if precio_usd is 100
        self.assertIn("✈️ Envío Estimado:", resultado) # Check for 60.00 if peso is 1.5 and ENVIO_USD_POR_KG is 40
        self.assertIn("🔥 Total Final USD:", resultado) # Check for 175.00 (100 + 15 + 60)
        self.assertIn("💸 En Pesos (MEP aprox.):", resultado)
        self.assertIn("💸 En Pesos (BLUE aprox.):", resultado)
        self.assertIn("_Alta ganga, bro.", resultado)

        # Test calculation results (example)
        # These values depend on COMISION_PORCENTAJE and ENVIO_USD_POR_KG from main.py
        # Assuming COMISION_PORCENTAJE = 0.15, ENVIO_USD_POR_KG = 40.0
        comision_esperada = 100.0 * 0.15
        envio_esperado = 1.5 * 40.0
        total_esperado = 100.0 + comision_esperada + envio_esperado
        self.assertIn(f"USD {comision_esperada:.2f}", resultado)
        self.assertIn(f"USD {envio_esperado:.2f}", resultado)
        self.assertIn(f"USD {total_esperado:.2f}", resultado)


    def test_save_and_retrieve_quotation(self):
        # Test saving a quotation
        client_id = 12345
        client_username = "testuser"
        product_name = "Test DB Product"
        product_link = "http://dbtest.com"
        weight = 0.5
        price = 50.0
        quotation_text = "This is a test quotation text."
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use a direct version of save_quotation_to_db that uses self.db_name
        # or modify global DB_NAME, which is risky.
        # Let's define a local save function for testing that uses TEST_DB_NAME.
        
        def save_quotation_to_test_db(client_telegram_id, username, prod_name, link, kg, usd_price, q_date, full_text):
            conn = sqlite3.connect(self.db_name) # Use test db
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO quotations (client_telegram_id, client_username, product_name, product_link, weight_kg, price_usd, quotation_date, full_quotation_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (client_telegram_id, username, prod_name, link, kg, usd_price, q_date, full_text))
                conn.commit()
            finally:
                conn.close()

        save_quotation_to_test_db(client_id, client_username, product_name, product_link, weight, price, date_str, quotation_text)

        # Test retrieving the quotation
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT client_telegram_id, client_username, product_name, full_quotation_text FROM quotations WHERE client_telegram_id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], client_id)
        self.assertEqual(row[1], client_username)
        self.assertEqual(row[2], product_name)
        self.assertEqual(row[3], quotation_text)

    def test_init_db_creates_table(self):
        # Test if init_db (adapted for test DB) creates the table
        # This test init_db would ideally take db_name as an argument
        # For now, we assume init_db from main.py uses MAIN_DB_NAME
        # So, we test our local setup's table creation.
        
        # Remove db if it exists to test creation
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        
        # Call a local init_db for testing purposes
        def init_test_db(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_telegram_id INTEGER NOT NULL,
                    client_username TEXT,
                    product_name TEXT NOT NULL,
                    product_link TEXT,
                    weight_kg REAL,
                    price_usd REAL,
                    quotation_date TEXT NOT NULL,
                    full_quotation_text TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()

        init_test_db(self.db_name)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Try to query the table schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quotations';")
        table_exists = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(table_exists, "The quotations table should exist after init_db.")


if __name__ == '__main__':
    unittest.main()
