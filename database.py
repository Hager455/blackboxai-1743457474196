from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class VerificationRecord(Base):
    __tablename__ = 'verifications'
    
    id = Column(Integer, primary_key=True)
    verification_id = Column(String(64), unique=True, nullable=False)
    face_encoding_path = Column(String(256), nullable=False)
    image_path = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    wallet_address = Column(String(42))  # For blockchain integration
    is_active = Column(Integer, default=1)

class Database:
    def __init__(self):
        db_path = os.environ.get('DATABASE_URI', 'sqlite:///verifications.db')
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_verification(self, verification_id, encoding_path, image_path=None, wallet=None):
        session = self.Session()
        try:
            record = VerificationRecord(
                verification_id=verification_id,
                face_encoding_path=encoding_path,
                image_path=image_path,
                wallet_address=wallet
            )
            session.add(record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Database error: {str(e)}")
            return False
        finally:
            session.close()

    def get_verification(self, verification_id):
        session = self.Session()
        try:
            return session.query(VerificationRecord)\
                .filter_by(verification_id=verification_id, is_active=1)\
                .first()
        finally:
            session.close()

    def deactivate_verification(self, verification_id):
        session = self.Session()
        try:
            record = session.query(VerificationRecord)\
                .filter_by(verification_id=verification_id)\
                .first()
            if record:
                record.is_active = 0
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Database error: {str(e)}")
            return False
        finally:
            session.close()

# Example usage:
# db = Database()
# db.create_verification('vid123', 'path/to/encoding.npy', 'path/to/image.jpg')
# record = db.get_verification('vid123')