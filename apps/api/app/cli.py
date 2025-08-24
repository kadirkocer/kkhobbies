import os
import json
import random
import typer
from datetime import datetime
from sqlalchemy.orm import Session
from .auth import hash_password
from .db.session import SessionLocal
from .db.fts import ensure_fts
from .models import User, Hobby, HobbyType, Entry, EntryProp
from .services.hobby_tree import slugify, ensure_unique_slug

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
    },
    {
        "key": "book",
        "title": "Book",
        "schema_json": '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","properties":{"author":{"type":"string"},"isbn":{"type":"string"},"publisher":{"type":"string"},"year":{"type":"integer"},"cover_url":{"type":"string","format":"uri"},"source":{"type":"string","enum":["google_books","manual"]},"link":{"type":"string","format":"uri"},"rating":{"type":"number","minimum":0,"maximum":5},"notes":{"type":"string"}},"required":["author"]}'
    },
    {
        "key": "bookmark",
        "title": "Bookmark",
        "schema_json": '{"type":"object","properties":{"url":{"type":"string","format":"uri"},"title":{"type":"string"},"favicon":{"type":"string"},"notes":{"type":"string"}},"required":["url"]}'
    },
    {
        "key": "brand_link",
        "title": "Brand Link",
        "schema_json": '{"type":"object","properties":{"brand":{"type":"string"},"url":{"type":"string","format":"uri"},"category":{"type":"string"},"notes":{"type":"string"}},"required":["brand","url"]}'
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
    
    session = get_db_session()
    
    try:
        # Ensure FTS5 setup
        ensure_fts(session)
        
        # Create default user if none exists
        existing_user = session.query(User).first()
        if not existing_user:
            username = os.getenv("ADMIN_INITIAL_USERNAME", "admin")
            password = os.getenv("ADMIN_INITIAL_PASSWORD", "change_me")
            
            user = User(
                username=username,
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

        # Seed hierarchical hobbies (v2.1)
        hierarchy = [
            {"name": "Müzik", "children": ["Gitar", "Bateri", "Piyano", "Prodüksiyon", "DJ", "Vokal"]},
            {"name": "Kitap & Sahne Sanatları & Sinema", "children": ["Kitap", "Tiyatro", "Müzik", "Tragedya", "Bilim", "Fotoğrafçılık", "Sinema"]},
            {"name": "Fotoğraf", "children": ["Fotoğraf Çekme", "Color grading", "Photoediting"]},
            {"name": "Videografi", "children": []},
            {"name": "Kaykay", "children": ["Skateboard", "Fingerboard"]},
            {"name": "Card", "children": ["Cardistry", "Magician"]},
            {"name": "Moda", "children": ["Sytlist", "Saat", "Kıyafet", "Sneaker", "High Fashion", "Street Style"]},
            {"name": "Teknoloji", "children": ["Coding", "AI", "Linux"]}
        ]

        def upsert(name: str, parent_id: int | None, sort_order: int) -> Hobby:
            existing = session.query(Hobby).filter(Hobby.name == name).first()
            if existing:
                return existing
            base = slugify(name)
            slug = ensure_unique_slug(session, base)
            h = Hobby(name=name, parent_id=parent_id, sort_order=sort_order, slug=slug)
            session.add(h)
            session.flush()
            return h

        for i, parent in enumerate(hierarchy):
            p = upsert(parent["name"], None, i)
            for j, child in enumerate(parent.get("children", [])):
                upsert(child, p.id, j)

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
            username=name,
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




@app.command()
def starter(
    count: int = typer.Option(10, help="Number of demo entries to create"),
    hobby: str = typer.Option("Photography", help="Hobby name to attach entries to"),
    type_key: str = typer.Option("photo", help="Hobby type key to use for entries"),
):
    """Generate demo entries with reasonable props (AI-style starter seed)."""
    session = get_db_session()
    try:
        # Ensure hobby exists
        h = session.query(Hobby).filter(Hobby.name == hobby).first()
        if not h:
            h = Hobby(name=hobby, color="#00bbf9", icon="camera")
            session.add(h)
            session.flush()

        # Ensure type exists
        t = session.query(HobbyType).filter(HobbyType.key == type_key).first()
        if not t:
            t = HobbyType(
                key=type_key,
                title=type_key.title(),
                schema_json='{"type":"object","properties":{"lens":{"type":"string"},"iso":{"type":"integer"},"shutter":{"type":"string"},"aperture":{"type":"string"}}}'
            )
            session.add(t)
            session.flush()

        # Parse schema for prop keys
        try:
            schema = json.loads(t.schema_json)
            prop_defs = schema.get("properties", {})
        except Exception:
            prop_defs = {}

        lenses = ["50mm", "35mm", "85mm", "24-70mm", "70-200mm"]
        shutt = ["1/100", "1/250", "1/500", "1/60"]
        apert = ["f/1.8", "f/2.8", "f/4", "f/5.6"]

        for i in range(count):
            title = f"Demo Shot #{random.randint(1000,9999)}"
            desc = random.choice([
                "Natural light portrait session.",
                "Street photo walk.",
                "Golden hour landscape.",
                "Low-light test image.",
            ])
            tags = ", ".join(random.sample(["portrait", "bokeh", "city", "nature", "test"], 3))

            e = Entry(hobby_id=h.id, type_key=t.key, title=title, description=desc, tags=tags)
            session.add(e)
            session.flush()

            # Create props based on schema
            props = []
            for key, pdef in prop_defs.items():
                v = None
                if pdef.get("type") == "integer":
                    v = str(random.choice([100, 200, 400, 800, 1600]))
                elif pdef.get("type") == "number":
                    v = str(random.choice([90.0, 120.0]))
                elif key.lower() == "lens":
                    v = random.choice(lenses)
                elif key.lower() == "shutter":
                    v = random.choice(shutt)
                elif key.lower() == "aperture":
                    v = random.choice(apert)
                else:
                    v = random.choice(["auto", "manual", "custom"])

                props.append(EntryProp(entry_id=e.id, key=key, value_text=v))

            session.add_all(props)

        session.commit()
        typer.echo(f"Created {count} demo entries for hobby '{hobby}' of type '{type_key}'.")
    except Exception as e:
        session.rollback()
        typer.echo(f"Error creating starter entries: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    app()
