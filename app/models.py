from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone
from app import db

class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    content: so.Mapped[str] = so.mapped_column(sa.String(10))
    
    def __repr__(self):
        return '<Message {} at {}>'.format(self.content, self.timestamp)


