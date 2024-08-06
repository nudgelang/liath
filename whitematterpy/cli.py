import cmd
from database import Database
import json
import yaml
import argparse

class DatabaseCLI(cmd.Cmd):
    intro = "Welcome to the WhiteMatter Database CLI. Type help or ? to list commands.\n"
    prompt = "(whitematter) "

    def __init__(self, storage_type='auto'):
        super().__init__()
        self.db = Database(storage_type=storage_type)
        self.current_namespace = 'default'
        self.username = None
        self.return_format = 'dict'

    def do_login(self, arg):
        """Login to the database: login username password"""
        username, password = arg.split()
        if self.db.authenticate_user(username, password):
            self.username = username
            print(f"Logged in as {username}")
        else:
            print("Invalid username or password")

    def do_create_user(self, arg):
        """Create a new user: create_user username password"""
        username, password = arg.split()
        try:
            self.db.create_user(username, password)
            print(f"User {username} created successfully")
        except ValueError as e:
            print(str(e))

    def do_use(self, arg):
        """Switch to a different namespace: use namespace_name"""
        if arg in self.db.list_namespaces():
            self.current_namespace = arg
            print(f"Switched to namespace: {arg}")
        else:
            print(f"Namespace '{arg}' does not exist")

    def do_create_namespace(self, arg):
        """Create a new namespace: create_namespace namespace_name"""
        self.db.create_namespace(arg)
        print(f"Created namespace: {arg}")

    def do_list_namespaces(self, arg):
        """List all namespaces"""
        print("Namespaces:", ', '.join(self.db.list_namespaces()))

    def do_set_format(self, arg):
        """Set the return format: set_format [dict|json|yaml|markdown]"""
        if arg in ['dict', 'json', 'yaml', 'markdown']:
            self.return_format = arg
            print(f"Return format set to: {arg}")
        else:
            print("Invalid format. Choose from: dict, json, yaml, markdown")

    def do_query(self, arg):
        """Execute a Lua query in the current namespace: query lua_code"""
        if not self.username:
            print("Please login first")
            return
        try:
            result = self.db.execute_query(self.current_namespace, arg, self.return_format)
            if self.return_format == 'dict':
                print(result)
            elif self.return_format == 'json':
                print(json.dumps(json.loads(result), indent=2))
            elif self.return_format == 'yaml':
                print(result)
            elif self.return_format == 'markdown':
                print(result)
        except Exception as e:
            print("Error:", str(e))

    def do_exit(self, arg):
        """Exit the CLI"""
        print("Goodbye!")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WhiteMatter Database CLI")
    parser.add_argument('--storage', choices=['auto', 'rocksdb', 'leveldb'], default='auto',
                        help="Specify the storage backend to use")
    args = parser.parse_args()

    DatabaseCLI(storage_type=args.storage).cmdloop()