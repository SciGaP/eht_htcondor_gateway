from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import app, db  # Replace 'your_app' with the name of your Flask app

manager = Manager(app)
migrate = Migrate(app, db)

# Command to drop all tables
@manager.command
def drop_all_tables():
    db.drop_all()

if __name__ == '__main__':
    manager.run()
