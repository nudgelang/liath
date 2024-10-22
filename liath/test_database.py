import unittest
import json
from database import Database
from storage.rocksdb_storage import RocksDBStorage
from storage.leveldb_storage import LevelDBStorage
import os

class TestLiathDatabase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('./test_data'):
            os.makedirs('./test_data')
        self.db = Database(data_dir='./test_data', storage_type='leveldb')
        self.db.create_namespace('test_namespace')

    def tearDown(self):
        # Clean up test data
        import shutil
        shutil.rmtree('./test_data')

    def execute_query(self, query):
        result = self.db.execute_query('test_namespace', query)
        return json.loads(result) if isinstance(result, str) else result

    def test_basic_operations(self):
        # Test put and get
        self.execute_query("db:put('key1', 'value1')")
        result = self.execute_query("return db:get('key1')")
        self.assertEqual(result, 'value1')

        # Test delete
        self.execute_query("db:delete('key1')")
        result = self.execute_query("return db:get('key1')")
        self.assertIsNone(result)

    def test_transactions(self):
        self.execute_query("db:begin_transaction()")
        self.execute_query("db:put('tx_key1', 'tx_value1')")
        self.execute_query("db:put('tx_key2', 'tx_value2')")
        self.execute_query("db:commit_transaction()")

        result1 = self.execute_query("return db:get('tx_key1')")
        result2 = self.execute_query("return db:get('tx_key2')")
        self.assertEqual(result1, 'tx_value1')
        self.assertEqual(result2, 'tx_value2')

        # Test rollback
        self.execute_query("db:begin_transaction()")
        self.execute_query("db:put('tx_key3', 'tx_value3')")
        self.execute_query("db:rollback_transaction()")
        result3 = self.execute_query("return db:get('tx_key3')")
        self.assertIsNone(result3)

    def test_column_families(self):
        self.execute_query("db:create_column_family('cf1')")
        self.execute_query("db:put_cf('cf1', 'cf_key1', 'cf_value1')")
        result = self.execute_query("return db:get_cf('cf1', 'cf_key1')")
        self.assertEqual(result, 'cf_value1')

        cf_list = self.execute_query("return db:list_column_families()")
        self.assertIn('cf1', cf_list)

        self.execute_query("db:delete_cf('cf1', 'cf_key1')")
        result = self.execute_query("return db:get_cf('cf1', 'cf_key1')")
        self.assertIsNone(result)

        self.execute_query("db:drop_column_family('cf1')")
        cf_list = self.execute_query("return db:list_column_families()")
        self.assertNotIn('cf1', cf_list)

    def test_iterator(self):
        self.execute_query("db:put('iter_key1', 'iter_value1')")
        self.execute_query("db:put('iter_key2', 'iter_value2')")
        self.execute_query("db:put('iter_key3', 'iter_value3')")

        iterator_result = self.execute_query("return db:iterator()")
        self.assertIsInstance(iterator_result, list)
        self.assertEqual(len(iterator_result), 3)
        self.assertIn({'iter_key1': 'iter_value1'}, iterator_result)
        self.assertIn({'iter_key2': 'iter_value2'}, iterator_result)
        self.assertIn({'iter_key3': 'iter_value3'}, iterator_result)

    def test_write_batch(self):
        batch_ops = [
            {"type": "put", "key": "batch_key1", "value": "batch_value1"},
            {"type": "put", "key": "batch_key2", "value": "batch_value2"},
            {"type": "delete", "key": "batch_key1"}
        ]
        self.execute_query(f"db:write_batch({json.dumps(batch_ops)})")

        result1 = self.execute_query("return db:get('batch_key1')")
        result2 = self.execute_query("return db:get('batch_key2')")
        self.assertIsNone(result1)
        self.assertEqual(result2, 'batch_value2')

    def test_plugin_availability(self):
        # Test if db plugin is available (should always be true)
        result = self.execute_query("return plugins.db")
        self.assertTrue(result)

        # Test if vdb plugin is available (may be true or false)
        result = self.execute_query("return plugins.vdb")
        self.assertIsInstance(result, bool)

        # Test a query that adapts based on plugin availability
        result = self.execute_query("""
            if plugins.vdb then
                return "VDB plugin is available"
            else
                return "VDB plugin is not available"
            end
        """)
        self.assertIn(result, ["VDB plugin is available", "VDB plugin is not available"])

    def test_conditional_plugin_usage(self):
        # This test demonstrates how to write queries that adapt to plugin availability
        result = self.execute_query("""
            if plugins.vdb then
                vdb:add('test_vector', {1, 2, 3})
                return vdb:count()
            else
                return {count = 0, message = "VDB plugin not available"}
            end
        """)
        
        if 'vdb' in self.db.plugins:
            self.assertEqual(result['count'], 1)
        else:
            self.assertEqual(result['count'], 0)
            self.assertEqual(result['message'], "VDB plugin not available")

if __name__ == '__main__':
    unittest.main()