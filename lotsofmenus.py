from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, MenuItem, User, Category

engine = create_engine('postgresql://ubuntu:cookies2018@localhost/itemcatalogappdb')
# engine = create_engine('sqlite:///item-catalog-db.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Fabiman Flechtmann", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/'
             'profile_images/2671170543/'
             '18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

User2 = User(name="Angela Ohlendorf", email="Angela.Ohlendorf@web.de",
             picture='https://pbs.twimg.com/'
             'profile_images/2671170543/'
             '18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

# Create dummy categories
category1 = Category(user_id=1, name="Soccer")
session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Basketball")
session.add(category2)
session.commit()

category3 = Category(user_id=2, name="Ballet")
session.add(category3)
session.commit()

category4 = Category(user_id=2, name="Dancing")
session.add(category4)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Ball",
                     description='A round piece of leather.'
                     'You can kick it around.',
                     category=category1)
session.add(menuItem2)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Soccer-shoes",
                     description="Soccer shoes are used to kick a football.",
                     category=category1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Men's Basketball Hoody",
                     description='Men Basketball Hoody.'
                     ' Makes you look dangerous.',
                     category=category2)

session.add(menuItem2)
session.commit()
menuItem2 = MenuItem(user_id=1, name="Basketball",
                     description='A round piece of leather.'
                     'You can throw it around. Bounces.',
                     category=category2)

session.add(menuItem2)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Basketball Apparel",
                     description="Dazzle Basketball Shorts",
                     category=category2)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=2, name="Luxury Ballet Shoes",
                     description="Shoes to dance Balley, I guess.",
                     category=category3)

session.add(menuItem2)
session.commit()

menuItem2 = MenuItem(user_id=2, name="Luxury Ballet Slippers",
                     description="Shoes to dance ballet, I guess.",
                     category=category3)
session.add(menuItem2)
session.commit()
menuItem2 = MenuItem(user_id=2, name="Dance Shoes",
                     description="Shoes to dance.",
                     category=category4)

session.add(menuItem2)
session.commit()

menuItem2 = MenuItem(user_id=2, name="Rare Dance Shoes",
                     description="Shoes to dance, but rare.",
                     category=category4)
session.add(menuItem2)
session.commit()
print "added Users, Categories and items"
