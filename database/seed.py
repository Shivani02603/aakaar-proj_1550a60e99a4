import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import engine, SessionLocal, User, Document, DocumentChunk, ChatSession, ChatMessage

def seed_database():
    session = SessionLocal()
    try:
        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="user1@example.com",
            hashed_password="hashed_password_1"
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="user2@example.com",
            hashed_password="hashed_password_2"
        )
        user3 = User(
            id=str(uuid.uuid4()),
            email="user3@example.com",
            hashed_password="hashed_password_3"
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            filename="document1.pdf",
            file_size=1024,
            status="processed"
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            filename="document2.pdf",
            file_size=2048,
            status="uploaded"
        )
        document3 = Document(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            filename="document3.pdf",
            file_size=512,
            status="failed"
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=0,
            content="This is the first chunk of document1.",
            embedding=[0.1] * 1536
        )
        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=1,
            content="This is the second chunk of document1.",
            embedding=[0.2] * 1536
        )
        chunk3 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document2.id,
            chunk_index=0,
            content="This is the first chunk of document2.",
            embedding=[0.3] * 1536
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed ChatSessions
        chat_session1 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            title="Chat with Assistant"
        )
        chat_session2 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            title="Document Review"
        )
        chat_session3 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            title="General Inquiry"
        )
        session.add_all([chat_session1, chat_session2, chat_session3])
        session.commit()

        # Seed ChatMessages
        message1 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=chat_session1.id,
            role="user",
            content="Hello, can you help me?",
            citations=None
        )
        message2 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=chat_session1.id,
            role="assistant",
            content="Sure, what do you need help with?",
            citations=None
        )
        message3 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=chat_session2.id,
            role="user",
            content="Can you review my document?",
            citations=None
        )
        session.add_all([message1, message2, message3])
        session.commit()

        print("Database seeded successfully!")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()