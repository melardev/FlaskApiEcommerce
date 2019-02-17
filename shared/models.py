from datetime import datetime

from flask_sqlalchemy import Model
from sqlalchemy import DateTime, Column, Integer


class BaseModel(Model):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def get_or_default(self, ident, default=None):
        return self.get(ident) or default


class UpdatedAtMixin(object):
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
