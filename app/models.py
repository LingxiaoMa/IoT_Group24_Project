from typing import Optional
import sqlalchemy as sa  # SQLAlchemy is used to define ORM models and work with the database
import sqlalchemy.orm as so  # SQLAlchemy ORM-related functionality
from datetime import datetime, timezone  # Used to handle timestamps
from app import db  # Import the db object from the Flask app
import pytz  # pytz library is used to handle timezones

# Define the Message model, which represents a table in the database
class Message(db.Model):
    # Primary key field 'id', automatically generated and unique for each record
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    
    # Timestamp field, indexed for fast querying
    # Automatically sets the current time in the 'Asia/Shanghai' timezone and removes microseconds
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')).replace(microsecond=0))
    
    # Content field, stores a string value of up to 10 characters (e.g., "True" or "False")
    content: so.Mapped[str] = so.mapped_column(sa.String(10))
    
    # This method is used to represent the Message object as a string
    def __repr__(self):
        # Returns a string representation of the Message, including the content and timestamp
        return '<Message {} at {}>'.format(self.content, self.timestamp)


