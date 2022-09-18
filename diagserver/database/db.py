import os
from sqlalchemy import Column, ForeignKey, create_engine, String, Float, Integer, SmallInteger, LargeBinary, DateTime, event
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


CATE_NORMAL = 1

CATE_POSITION = 2


class TreeNode(Base):
    __tablename__ = "tree_node"

    id = Column(Integer, primary_key=True)

    parent_id = Column(Integer)

    name = Column(String(128))

    category = Column(SmallInteger)


class VibrationFeature(Base):
    __tablename__ = "vibration_feature"




class VibrationSamples(Base):
    __tablename__ = "vibration_samples"

    id = Column(BigInteger, primary_key)

    parent_id = Column(Integer)

    timestamp = Column(DateTime)

    samples = Column(LargeBinary)