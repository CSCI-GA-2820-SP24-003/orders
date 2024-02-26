"""
Persistent Base class for database CRUD functions
"""

import logging
from abc import abstractmethod
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################


class PersistentBase(db.Model):
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    @classmethod
    def init_db(cls, app: Flask):
        """
        Initializes a database
        """
        logger.info("Initializing database")
        cls.app = app
        db.init_app(app)
        app.app_context().push()
        db.create_all()
