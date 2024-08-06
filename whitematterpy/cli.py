import cmd
from database import Database

class DatabaseCLI(cmd.Cmd):
    intro = "Welcome to the Advanced RocksDB-Lua Database CLI. Type help or ? to list commands.\n"
    prompt = "(rocksdb-lua) "

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_namespace = 'default'
        self.username = None

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

    def do_query(self, arg):
        """Execute a Lua query in the current namespace: query lua_code"""
        if not self.username:
            print("Please login first")
            return
        try:
            result = self.db.execute_query(self.current_namespace, arg)
            print("Result:", result)
        except Exception as e:
            print("Error:", str(e))

    def do_install_package(self, arg):
        """Install a LuaRocks package in the current namespace: install_package package_name"""
        if not self.username:
            print("Please login first")
            return
        success = self.db.install_package(self.current_namespace, arg)
        if success:
            print(f"Package '{arg}' installed successfully in namespace '{self.current_namespace}'")
        else:
            print(f"Failed to install package '{arg}'")

    def do_exit(self, arg):
        """Exit the CLI"""
        print("Goodbye!")
        return True

if __name__ == '__main__':
    DatabaseCLI().cmdloop()