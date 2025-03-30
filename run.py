from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()  # Esto crea las tablas si no existen

if __name__ == "__main__":
    app.run()
