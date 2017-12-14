#!/usr/bin/env python
import base.config
import discord
import sys
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Boolean, String, BigInteger, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from base import util

engine = create_engine(base.config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base()
Model.query = db_session.query_property()

def create_all():
    Model.metadata.create_all(engine)


class DiscordUser(Model):
    __tablename__ = 'discord_user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    discriminator = Column(String(4))
    snowflake = Column(BigInteger())
    balance = Column(BigInteger())
    address = Column(String(34))

    def __init__(self, username, discriminator, snowflake):
        self.username = username
        self.discriminator = discriminator
        self.snowflake = snowflake
        self.balance = 0

    def __repr__(self):
        return '<DiscordUser %r#%r (%s)>' % (self.username, self.discriminator, str(self.snowflake))

    @classmethod
    def get_or_create(cls, username_, discriminator_, snowflake_):
        user = cls.query.filter_by(snowflake=snowflake_).first()
        if user is None:
            user = cls(username_, discriminator_, snowflake_)
            db_session.add(user)
            db_session.commit()
        return user

    def update_balance(self, balance:float):
        self.balance = util.coin_float_to_bignum(balance)
        db_session.commit()
        return self.balance

class Deposit(Model):
    __tablename__ = 'deposit'
    id = Column(Integer, primary_key=True)
    discord_user_id = Column(Integer, ForeignKey('discord_user.id'))
    discord_user = relationship("DiscordUser")
    address_from = Column(String(34))
    address_to = Column(String(34))
    balance = Column(BigInteger())

class Withdrawal(Model):
    __tablename__ = 'withdrawal'
    id = Column(Integer, primary_key=True)
    discord_user_id = Column(Integer, ForeignKey('discord_user.id'))
    discord_user = relationship("DiscordUser")
    address_from = Column(String(34))
    address_to = Column(String(34))
    balance = Column(BigInteger())

class Tip(Model):
    __tablename__ = 'tip'
    id = Column(Integer, primary_key=True)
    discord_user_from_id = Column(Integer, ForeignKey('discord_user.id'))
    discord_user_from = relationship("DiscordUser", foreign_keys=[discord_user_from_id])
    discord_user_to_id = Column(Integer, ForeignKey('discord_user.id'))
    discord_user_to = relationship("DiscordUser", foreign_keys=[discord_user_to_id])
    balance = Column(BigInteger())

class Server(Model):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    server_id = Column(String(18), unique=True)
    can_soak = Column(Boolean())

    def __init__(self, server: discord.Server):
        self.server_id = str(server.id)
        self.can_soak = bool(server.large)

    @classmethod
    def get_or_create(cls, server: discord.Server):
        s = cls.query.filter_by(server_id=str(server.id)).first()
        if s is None:
            s = cls(server)
            db.add(s)
        return s

    @classmethod
    def remove(cls, server: discord.Server):
        Channel.query.filter_by(server_id=str(server.id)).delete(synchronize_session=False)
        cls.query.filter_by(server_id=str(server.id)).delete(synchronize_session=False)

class Channel(Model):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey('server.id'))
    server = relationship("Server", foreign_keys=[server_id])
    channel_id = Column(String(18))
    is_active = Column(Boolean())

    def __init__(self, server: discord.Server, channel: discord.Channel):
        s = Server.get_or_create(server)
        self.server = s
        self.is_active = True
        self.channel_id = str(channel.id)


    @classmethod
    def remove(cls, channel):
        cls.query.filter_by(channel_id=str(channel.id)).delete(synchronize_session=False)

