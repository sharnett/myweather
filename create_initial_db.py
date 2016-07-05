import main

with main.app.app_context():
    main.db.create_all()
