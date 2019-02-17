import datetime
import random
import sys

import faker
from sqlalchemy.orm import load_only
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.expression import func

from addresses.models import Address

from categories.models import Category
from comments.models import Comment
from ecommerce_api.factory import db, bcrypt
from file_uploads.models import ProductImage, TagImage, CategoryImage
from orders.models import Order, OrderItem
from products.models import Product
from roles.models import Role, UserRole
from tags.models import Tag
from users.models import User

fake = faker.Faker()
tags = []
categories = []


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


def encrypt_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def generate_image(model):
    # pattern = "".join([random.choice(['?', '#']) for i in range(0, 10)]) + '.png'
    filename_pattern = "".join(fake.random_choices(elements=('?', '#'),
                                                   length=fake.random_int(min=16, max=32))) + '.png'
    # file_name=fake.md5(raw_output=False) + '.png'
    return model(file_name="".join(fake.random_letters(length=16)) + '.png',
                 file_path=fake.image_url(width=None, height=None),
                 file_size=fake.random_int(min=1000, max=15000),
                 original_name=fake.bothify(text=filename_pattern))


def seed_admin():
    role, created = get_or_create(db.session, Role,
                                  defaults={'description': 'for admin only'},
                                  name='ROLE_ADMIN')
    '''
    # count admin
    admin_count = User.query.filter(User.roles.any(id=role.id)).count()

    # 4 ways of retrieving the admin users
    admin_users = User.query.filter(User.users_roles.any(role_id=role.id)).all()
    admin_users = User.query.filter(User.roles.any(id=role.id)).all()
    admin_users = User.query.filter(User.roles.any(name='ROLE_ADMIN')).all()
    admin_users = User.query.join(User.roles).filter_by(name=role.name).all()
    '''

    user, created = get_or_create(db.session, User, defaults={'first_name': 'adminFN',
                                                              'last_name': 'adminFN',
                                                              'email': 'admin@flaskblogapi.app',
                                                              'password': bcrypt.generate_password_hash('password')},
                                  **{'username': 'admin'})

    db.session.commit()

    if len(user.roles) == 0:
        # user.users_roles.append(UserRole(user_id=user.id, role_id=role.id))
        user.roles.append(role)
        db.session.commit()


def seed_authors():
    role, created = get_or_create(db.session, Role, defaults={'description': 'for authors only'},
                                  name='ROLE_AUTHOR')

    authors_count = db.session.query(User.id).filter(User.roles.any(id=role.id)).count()
    authors_count = User.query.filter(User.roles.any(id=role.id)).count()
    authors_to_seed = 5
    authors_to_seed -= authors_count

    for i in range(0, authors_to_seed):
        profile = fake.profile(fields='username,mail,name')
        username = profile['username']
        first_name = profile['name'].split()[0]
        last_name = profile['name'].split()[1]
        email = profile['mail']
        password = bcrypt.generate_password_hash('password')
        user = User(username=username, first_name=first_name, last_name=last_name, email=email,
                    password=password, roles=[role])
        db.session.add(user)
        db.session.commit()
        # db.session.add(UserRole(user_id=user.id, role_id=role.id))

    db.session.commit()


def seed_users():
    role, created = get_or_create(db.session, Role,
                                  defaults={'description': 'for standard users'},
                                  name='ROLE_USER')
    db.session.commit()
    non_standard_user_ids = db.session.query(User.id) \
        .filter(~User.roles.any(id=role.id)).all()

    all_users_count = db.session.query(func.count(User.id)).all()[0][0]
    all_users_count = db.session.query(User.id).count()

    # User.query.filter(User.roles.any(UserRole.role_id.in_([1,2]))).count()
    standard_users_count = db.session.query(User).filter(User.roles.any(UserRole.role_id.in_([role.id]))).count()
    standard_users_count = db.session.query(User.id).filter(
        User.roles.any(id=role.id)).count()

    users_to_seed = 23
    users_to_seed -= standard_users_count
    sys.stdout.write('[+] Seeding %d users\n' % users_to_seed)

    for i in range(0, users_to_seed):
        profile = fake.profile(fields='username,mail,name')
        username = profile['username']
        # fake.first_name() fake.first_name_male() fake.first_name_female(), same for last_name()
        first_name = profile['name'].split()[0]
        last_name = profile['name'].split()[1]
        email = profile['mail']
        password = bcrypt.generate_password_hash('password')
        user = User(username=username, first_name=first_name, last_name=last_name, email=email,
                    password=password)
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()

    db.session.commit()


def seed_tags():
    sys.stdout.write('[+] Seeding tags\n')
    pairs = []

    tag, created = get_or_create(db.session, Tag, defaults={'description': 'shoes for everyone'}, name='Shoes')
    tags.append(tag)
    pairs.append((tag, created))

    tag, created = get_or_create(db.session, Tag, defaults={'description': 'jeans for everyone'}, name='Jeans')
    tags.append(tag)
    pairs.append((tag, created))

    tag, created = get_or_create(db.session, Tag, defaults={'description': 'jackets for everyone'}, name='Jackets')
    tags.append(tag)
    pairs.append((tag, created))

    tag, created = get_or_create(db.session, Tag, defaults={'description': 'shorts for everyone'}, name='Shorts')
    tags.append(tag)
    pairs.append((tag, created))

    for pair in pairs:
        if pair[1]:  # if created
            for i in range(0, random.randint(1, 2)):
                pi = generate_image(TagImage)
                pair[0].images.append(pi)

    db.session.add_all(tags)
    db.session.commit()


def seed_categories():
    sys.stdout.write('[+] Seeding categories\n')
    pairs = []
    category, created = get_or_create(db.session, Category,
                                      defaults={'description': 'clothes for  men'},
                                      name='Men')
    categories.append(category)
    pairs.append((category, created))

    category, created = get_or_create(db.session, Category,
                                      defaults={'description': 'clothes for women'}, name='Women')
    categories.append(category)
    pairs.append((category, created))

    category, created = get_or_create(db.session, Category,
                                      defaults={'description': 'clothes for kids'}, name='Kids')
    categories.append(category)
    pairs.append((category, created))

    category, created = get_or_create(db.session, Category,
                                      defaults={'description': 'clothes for teenagers'}, name='Teenagers')
    categories.append(category)
    pairs.append((category, created))

    for pair in pairs:
        if pair[1]:  # if created
            for i in range(0, random.randint(1, 2)):
                category_image = generate_image(CategoryImage)
                pair[0].images.append(category_image)

    db.session.add_all(categories)
    db.session.commit()


def seed_products():
    products_count = db.session.query(func.count(Product.id)).all()[0][0]
    products_to_seed = 23
    sys.stdout.write('[+] Seeding %d products\n' % products_to_seed)

    # tag_ids = [tag[0] for tag in db.session.query(Tag.id).all()]
    # category_ids = [category[0] for category in db.session.query(Category.id).all()]

    for i in range(products_count, products_to_seed):
        name = fake.sentence()
        description = fake.text()

        start_date = datetime.date(year=2017, month=1, day=1)
        random_date = fake.date_between(start_date=start_date, end_date='+4y')
        publish_on = random_date
        product = Product(name=name, description=description, price=fake.random_int(min=50, max=2500),
                          stock=fake.random_int(min=5, max=1000), publish_on=publish_on)

        # product.tags.append(db.session.query(Tag).order_by(func.random()).first())

        tags_for_product = []
        categories_for_product = []

        for i in range(0, random.randint(1, 2)):
            tag_to_add = random.choice(tags)
            if tag_to_add.id not in tags_for_product:
                product.tags.append(tag_to_add)
                tags_for_product.append(tag_to_add.id)

        for i in range(0, random.randint(1, 2)):
            category_to_add = random.choice(categories)
            if category_to_add.id not in categories_for_product:
                product.categories.append(category_to_add)
                categories_for_product.append(category_to_add.id)

        for i in range(0, random.randint(1, 2)):
            product_image = generate_image(ProductImage)
            product.images.append(product_image)

        db.session.add(product)
        db.session.commit()


def seed_comments():
    comments_count = db.session.query(func.count(Comment.id)).scalar()
    comments_to_seed = 31
    comments_to_seed -= comments_count
    sys.stdout.write('[+] Seeding %d comments\n' % comments_to_seed)
    comments = []

    user_ids = [user[0] for user in User.query.with_entities(User.id).all()]
    product_ids = [product[0] for product in Product.query.with_entities(Product.id)]
    # equivalent:
    # user_ids = [user[0] for user in db.session.query(User.id).all()]
    # product_ids = [product[0] for product in db.session.query(Product.id).all()]

    for i in range(comments_count, comments_to_seed):
        user_id = random.choice(user_ids)
        product_id = random.choice(product_ids)
        rating = fake.random_int(min=1, max=5) if fake.boolean(chance_of_getting_true=50) else None
        comments.append(Comment(product_id=product_id,
                                user_id=user_id, rating=rating,
                                content=fake.paragraph(nb_sentences=4, variable_nb_sentences=True, ext_word_list=None)))

    db.session.add_all(comments)
    db.session.commit()


def seed_addresses():
    addresses_count = db.session.query(func.count(Address.id)).scalar()
    addresses_to_seed = 30
    user_ids = [user[0] for user in db.session.query(User.id).all()]

    for i in range(addresses_count, addresses_to_seed):
        user_id = random.choice(user_ids) if fake.boolean(chance_of_getting_true=80) else None

        first_name = fake.first_name()
        last_name = fake.last_name()
        zip_code = fake.zipcode_plus4()  # postcode(), postalcode(), zipcode(), postalcode_plus4
        street_address = fake.address()
        phone_number = fake.phone_number()
        city = fake.city()
        country = fake.country()
        db.session.add(Address(user_id=user_id, first_name=first_name, last_name=last_name, zip_code=zip_code,
                               street_address=street_address, phone_number=phone_number, city=city, country=country))

    db.session.commit()


def seed_orders():
    orders_count = db.session.query(func.count(Order.id)).scalar()
    orders_to_seed = 31
    addresses = db.session.query(Address).options(load_only('id', 'user_id')).all()
    products = db.session.query(Product).options(load_only('id', 'name', 'slug', 'price')).all()

    for i in range(orders_count, orders_to_seed):
        address = random.choice(addresses)
        tracking_number = fake.uuid4()
        order_status = fake.random_int(min=0, max=2)
        user_id = address.user_id
        order = Order(tracking_number=tracking_number, order_status=order_status, address_id=address.id,
                      user_id=user_id)

        db.session.add(order)

        '''
        this is to save the order now, so I can have the id to be used in order items
        or the other way is to comment flush(), order_id=order.id, and session.add(oi).
        Instead use order.order_items.append(oi); See below. Both ways lead to the same result
        '''

        db.session.flush()

        for i in range(fake.random_int(min=1, max=6)):
            product = random.choice(products)
            oi = OrderItem(name=product.name, slug=product.slug, price=product.price,
                           order_id=order.id,
                           product_id=product.id, user_id=user_id, quantity=fake.random_int(min=1, max=5))
            db.session.add(oi)

            # order.order_items.append(oi)

        db.session.commit()


if __name__ == '__main__':
    seed_admin()
    seed_users()
    seed_tags()
    seed_categories()
    seed_products()
    seed_comments()
    seed_addresses()
    seed_orders()
