# from app import app,db
# from models import User,Role

# with app.app_context():
#     roles = []
#     admin_role = Role(
#         role_name = 'admin'
#     )
#     roles.append(admin_role)

#     teacher_role = Role(
#         role_name = 'teacher'
#     )
#     roles.append(teacher_role)

#     student_role = Role(
#         role_name = 'student'
#     )
#     roles.append(student_role)
#     db.session.add_all(roles)
#     db.session.commit()
#     admin = User(
#         first_name='Koin',
#         last_name = 'Barclay',
#         email = 'koin@gmail.com',
#         department = 'software eng',
#         course='web dev',
#         password='12345',
#         phone_number = 125378293,
#         role_id= 1
#     )
#     db.session.add(admin)
#     db.session.commit()





from app import app, db
from models import User, Role
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

with app.app_context():
    # Seed roles
    roles = []
    for role_name in ['admin', 'teacher', 'student']:
        role = Role(role_name=role_name)
        roles.append(role)
    # db.session.add_all(roles)
    # db.session.commit()

    # Retrieve role IDs
    admin_role_id = Role.query.filter_by(role_name='admin').first().id

    # Seed admin user
    admin_password_hash = bcrypt.generate_password_hash('12345').decode('utf-8')
    admin = User(
        first_name='Koin',
        last_name='Barclay',
        email='koin@gmail.com',
        department='software eng',
        course='web dev',
        password=admin_password_hash,
        phone_number=125378293,
        role_id=admin_role_id
    )
    # db.session.add(admin)
    # db.session.commit()

