#SQLAlchemy
def init_sql_alchemy():
    from app import db, app
    with app.app_context():
        db.create_all()
        from app import User
        bob = User(name='Bob' , about='ten vetsi kralik')
        bobek = User(name='Bobek', about='ten mensi kralik')
        db.session.add(bob)
        db.session.add(bobek)
        db.session.commit()
    
    print("DB created")


if __name__ == '__main__':
    init_sql_alchemy()
