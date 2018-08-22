""" Category-specifc Models (ORM) """
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# pylint: disable=invalid-name,too-few-public-methods

CATEGORY_REPR = '<Category id={} name={}>'
CATEGORY_ITEM_REPR = '''<Category-Item id={}, created={},
                        category_id={}, title={}, description={}>'''

Base = declarative_base()


class Category(Base):
    """ Category model"""
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(16), unique=True, nullable=False)

    def to_dict(self):
        """ Transforms object to dictionary """
        return dict(id=self.id, name=self.name)

    def __repr__(self):
        return CATEGORY_REPR.format(self.id, self.name)


class CategoryItem(Base):
    """ Category Item model """
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key=True)
    title = Column(String(16), unique=True, nullable=False)
    description = Column(String(64), nullable=True)
    created = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id))
    category = relationship(Category, cascade='delete')

    def to_dict(self):
        """ Transforms object to dictionary """
        return dict(id=self.id, title=self.title,
                    description=self.description,
                    created=self.created)

    def __repr__(self):
        return CATEGORY_ITEM_REPR.format(self.id, self.created,
                                         self.category_id, self.title,
                                         self.description)
