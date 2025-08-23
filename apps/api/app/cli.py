import os
import typer
from sqlalchemy.orm import Session
from .auth import hash_password
from .db import SessionLocal, init_db
from .models import User, Hobby, HobbyType

app = typer.Typer(name="hobby-showcase")

SEED_HOBBY_TYPES = [
    {
        "key": "photo",
        "title": "Photo",
        "schema_json": '{"type":"object","properties":{"lens":{"type":"string"},"iso":{"type":"integer"},"shutter":{"type":"string"},"aperture":{"type":"string"},"preset":{"type":"string"}}}'
    },
    {
        "key": "audio",
        "title": "Audio",
        "schema_json": '{"type":"object","properties":{"bpm":{"type":"number"},"key":{"type":"string"},"instrument":{"type":"string"}}}'
    },
    {
        "key": "outfit",
        "title": "Outfit",
        "schema_json": '{"type":"object","properties":{"top":{"type":"string"},"bottom":{"type":"string"},"shoes":{"type":"string"},"style":{"type":"string"}}}'
    },
    {
        "key": "book_note",
        "title": "Book Note",
        "schema_json": '{"type":"object","properties":{"author":{"type":"string"},"isbn":{"type":"string"},"quote":{"type":"string"}}}'
    }
]

SEED_HOBBIES = [
    {"name": "Music", "color": "#9b5de5", "icon": "music", "parent_id": None},
    {"name": "Photography", "color": "#00bbf9", "icon": "camera", "parent_id": None},
    {"name": "Videography", "color": "#00f5d4", "icon": "video", "parent_id": None},
    {"name": "Books & Theater & Film", "color": "#fee440", "icon": "book", "parent_id": None},
    {"name": "Fashion", "color": "#ff006e", "icon": "shirt", "parent_id": None},
    {"name": "Tech", "color": "#adb5bd", "icon": "cpu", "parent_id": None}
]


def get_db_session() -> Session:
    return SessionLocal()


@app.command()
def init():
    """Initialize the database and seed with default data"""
    typer.echo("Initializing database...")
    init_db()
    
    session = get_db_session()
    
    try:
        # Create default user if none exists
        existing_user = session.query(User).first()
        if not existing_user:
            username = os.getenv("ADMIN_INITIAL_USERNAME", "admin")
            password = os.getenv("ADMIN_INITIAL_PASSWORD", "change_me")
            
            user = User(
                name=username,
                password_hash=hash_password(password)
            )
            session.add(user)
            typer.echo(f"Created admin user: {username}")
        
        # Seed hobby types
        for type_data in SEED_HOBBY_TYPES:
            existing = session.query(HobbyType).filter(HobbyType.key == type_data["key"]).first()
            if not existing:
                hobby_type = HobbyType(**type_data)
                session.add(hobby_type)
                typer.echo(f"Created hobby type: {type_data['title']}")
        
        # Seed hobbies
        for hobby_data in SEED_HOBBIES:
            existing = session.query(Hobby).filter(Hobby.name == hobby_data["name"]).first()
            if not existing:
                hobby = Hobby(**hobby_data)
                session.add(hobby)
                typer.echo(f"Created hobby: {hobby_data['name']}")
        
        session.commit()
        typer.echo("Database initialization completed!")
        
    except Exception as e:
        session.rollback()
        typer.echo(f"Error during initialization: {e}")
        raise
    finally:
        session.close()


@app.command()
def create_user(
    name: str = typer.Option(..., help="Username"),
    password: str = typer.Option(..., help="Password", hide_input=True)
):
    """Create a new user (for single-user app, this replaces existing user)"""
    session = get_db_session()
    
    try:
        # Delete existing user (single-user app)
        session.query(User).delete()
        
        # Create new user
        user = User(
            name=name,
            password_hash=hash_password(password)
        )
        session.add(user)
        session.commit()
        
        typer.echo(f"Created user: {name}")
        
    except Exception as e:
        session.rollback()
        typer.echo(f"Error creating user: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    app()