"""
Database configuration and models for i18n-l10n app
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class LanguageCode(enum.Enum):
    """Language codes following ISO 639-1 standard (2 characters) + region (3 characters)"""
    EN_US = "en-US"  # English (United States)
    EN_GB = "en-GB"  # English (United Kingdom)
    ES_ES = "es-ES"  # Spanish (Spain)
    ES_MX = "es-MX"  # Spanish (Mexico)
    FR_FR = "fr-FR"  # French (France)
    FR_CA = "fr-CA"  # French (Canada)
    DE_DE = "de-DE"  # German (Germany)
    IT_IT = "it-IT"  # Italian (Italy)
    PT_BR = "pt-BR"  # Portuguese (Brazil)
    PT_PT = "pt-PT"  # Portuguese (Portugal)
    RU_RU = "ru-RU"  # Russian (Russia)
    JA_JP = "ja-JP"  # Japanese (Japan)
    KO_KR = "ko-KR"  # Korean (South Korea)
    ZH_CN = "zh-CN"  # Chinese Simplified (China)
    ZH_TW = "zh-TW"  # Chinese Traditional (Taiwan)
    AR_SA = "ar-SA"  # Arabic (Saudi Arabia)
    HI_IN = "hi-IN"  # Hindi (India)
    NL_NL = "nl-NL"  # Dutch (Netherlands)
    SV_SE = "sv-SE"  # Swedish (Sweden)
    NO_NO = "no-NO"  # Norwegian (Norway)
    DA_DK = "da-DK"  # Danish (Denmark)
    FI_FI = "fi-FI"  # Finnish (Finland)
    PL_PL = "pl-PL"  # Polish (Poland)
    CS_CZ = "cs-CZ"  # Czech (Czech Republic)
    HU_HU = "hu-HU"  # Hungarian (Hungary)
    RO_RO = "ro-RO"  # Romanian (Romania)
    BG_BG = "bg-BG"  # Bulgarian (Bulgaria)
    HR_HR = "hr-HR"  # Croatian (Croatia)
    SK_SK = "sk-SK"  # Slovak (Slovakia)
    SL_SI = "sl-SI"  # Slovenian (Slovenia)
    ET_EE = "et-EE"  # Estonian (Estonia)
    LV_LV = "lv-LV"  # Latvian (Latvia)
    LT_LT = "lt-LT"  # Lithuanian (Lithuania)
    EL_GR = "el-GR"  # Greek (Greece)
    TR_TR = "tr-TR"  # Turkish (Turkey)
    UK_UA = "uk-UA"  # Ukrainian (Ukraine)
    TH_TH = "th-TH"  # Thai (Thailand)
    VI_VN = "vi-VN"  # Vietnamese (Vietnam)
    ID_ID = "id-ID"  # Indonesian (Indonesia)
    MS_MY = "ms-MY"  # Malay (Malaysia)
    TL_PH = "tl-PH"  # Filipino (Philippines)


class User(Base):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class TranslationTag(Base):
    """TranslationTag that's used to put together translations"""
    __tablename__ = 'translation_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    application = Column(String(255), nullable=False)
    tag = Column(Text, nullable=False)
    context = Column(String(500), nullable=True)  # Context for the translation key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Translation(Base):
    """Translation model for storing i18n/l10n translations"""
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    translation_tag_id = Column(Integer, nullable=False, index=True)
    language = Column(Enum(LanguageCode), nullable=False, index=True)  # Language code (5 characters)
    text = Column(Text, nullable=False)  # Translated text
    is_plural = Column(Boolean, default=False)  # Whether this is a plural form
    plural_form = Column(String(50), nullable=True)  # Plural form identifier (e.g., 'one', 'other')
    author_id = Column(Integer, nullable=True)  # User who created/updated this translation
    is_active = Column(Boolean, default=True)  # Whether this translation is active
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint on translation_tag_id + language + plural_form
    __table_args__ = (
        {'extend_existing': True}
    )


class APIKey(Base):
    """APIKey model for storing API keys"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    application = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

class DatabaseManager:
    """Database manager for handling connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        # Don't initialize database on startup - wait for first access
        logger.info("Database manager created - will initialize on first access")
    
    def _get_database_url(self):
        """Get database URL from environment variables"""
        # Log all relevant environment variables for debugging
        logger.info(f"Environment variables - DB_HOST: {os.getenv('DB_HOST')}, DB_CONNECTION_NAME: {os.getenv('DB_CONNECTION_NAME')}")
        logger.info(f"Environment variables - DB_NAME: {os.getenv('DB_NAME')}, DB_USER: {os.getenv('DB_USER')}")
        
        # Check if we have direct database connection details (preferred for Cloud Run)
        db_host = os.getenv('DB_HOST')
        if db_host:
            db_port = os.getenv('DB_PORT', '3306')
            db_name = os.getenv('DB_NAME', 'i18n_l10n_db')
            db_user = os.getenv('DB_USER', 'appuser')
            db_password = os.getenv('DB_PASSWORD', 'password')
            
            logger.info(f"Using direct database connection to {db_host}:{db_port}")
            return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Check if we're running in Cloud Run with Cloud SQL Proxy
        connection_name = os.getenv('DB_CONNECTION_NAME')
        if connection_name:
            # Use Unix socket for Cloud SQL Proxy
            db_user = os.getenv('DB_USER', 'appuser')
            db_password = os.getenv('DB_PASSWORD', '')
            db_name = os.getenv('DB_NAME', 'i18n_l10n_db')
            
            # Cloud SQL Proxy creates a Unix socket at /cloudsql/CONNECTION_NAME
            unix_socket_path = f'/cloudsql/{connection_name}'
            
            logger.info(f"Using Cloud SQL Proxy connection: {unix_socket_path}")
            return f'mysql+pymysql://{db_user}:{db_password}@/{db_name}?unix_socket={unix_socket_path}'
        
        # No fallback - raise exception if we can't determine database connection
        logger.error("Unable to determine database connection - no DB_HOST or DB_CONNECTION_NAME found")
        raise ValueError("Database connection not configured: missing DB_HOST or DB_CONNECTION_NAME environment variable")
    
    def _ensure_database_initialized(self):
        """Ensure database is initialized, initialize if needed"""
        if self.engine is None or self.SessionLocal is None:
            import time
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting to initialize database (attempt {attempt + 1}/{max_retries})")
                    self._setup_database()
                    return
                except Exception as e:
                    logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Failed to initialize database after {max_retries} attempts")
                        raise
    
    def _setup_database(self):
        """Set up database connection and create tables"""
        try:
            database_url = self._get_database_url()
            logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
            
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified successfully")
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise e
    
    
    def get_session(self):
        """Get a database session"""
        self._ensure_database_initialized()
        return self.SessionLocal()
    
    def save_greeting(self, greeting_text, user_id=None, ip_address=None):
        """Save a greeting to the database"""
        try:
            with self.get_session() as session:
                greeting = Greeting(
                    user_id=user_id,
                    greeting_text=greeting_text,
                    ip_address=ip_address
                )
                session.add(greeting)
                session.commit()
                return greeting.id
        except Exception as e:
            logger.error(f"Failed to save greeting: {e}")
            return None
    
    def get_recent_greetings(self, limit=10):
        """Get recent greetings from the database"""
        try:
            with self.get_session() as session:
                greetings = session.query(Greeting).order_by(Greeting.created_at.desc()).limit(limit).all()
                return greetings
        except Exception as e:
            logger.error(f"Failed to get greetings: {e}")
            return []
    
    def save_counter(self, session_id, counter_value):
        """Save or update counter value"""
        try:
            with self.get_session() as session:
                counter = session.query(Counter).filter(Counter.session_id == session_id).first()
                if counter:
                    counter.counter_value = counter_value
                    counter.updated_at = datetime.utcnow()
                else:
                    counter = Counter(session_id=session_id, counter_value=counter_value)
                    session.add(counter)
                session.commit()
                return counter.id
        except Exception as e:
            logger.error(f"Failed to save counter: {e}")
            return None
    
    def get_counter(self, session_id):
        """Get counter value for a session"""
        try:
            with self.get_session() as session:
                counter = session.query(Counter).filter(Counter.session_id == session_id).first()
                return counter.counter_value if counter else 0
        except Exception as e:
            logger.error(f"Failed to get counter: {e}")
            return 0
    
    def save_translation(self, translation_tag_id, language, text, is_plural=False, plural_form=None, author_id=None):
        """Save a translation to the database"""
        try:
            with self.get_session() as session:
                # Check if translation already exists
                existing = session.query(Translation).filter(
                    Translation.translation_tag_id == translation_tag_id,
                    Translation.language == language,
                    Translation.plural_form == plural_form
                ).first()
                
                if existing:
                    # Update existing translation
                    existing.text = text
                    existing.is_plural = is_plural
                    existing.author_id = author_id
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new translation
                    translation = Translation(
                        translation_tag_id=translation_tag_id,
                        language=language,
                        text=text,
                        is_plural=is_plural,
                        plural_form=plural_form,
                        author_id=author_id
                    )
                    session.add(translation)
                
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save translation: {e}")
            return False
    
    def get_translation(self, translation_tag_id, language, plural_form=None):
        """Get a translation for a specific tag and language"""
        try:
            with self.get_session() as session:
                translation = session.query(Translation).filter(
                    Translation.translation_tag_id == translation_tag_id,
                    Translation.language == language,
                    Translation.plural_form == plural_form,
                    Translation.is_active == True
                ).first()
                return translation.text if translation else None
        except Exception as e:
            logger.error(f"Failed to get translation: {e}")
            return None
    
    def get_translations_for_tag(self, translation_tag_id):
        """Get all translations for a specific tag"""
        try:
            with self.get_session() as session:
                translations = session.query(Translation).filter(
                    Translation.translation_tag_id == translation_tag_id,
                    Translation.is_active == True
                ).all()
                return {t.language.value: t.text for t in translations}
        except Exception as e:
            logger.error(f"Failed to get translations for tag: {e}")
            return {}
    
    def get_available_languages(self):
        """Get all available languages in the system"""
        try:
            with self.get_session() as session:
                languages = session.query(Translation.language).distinct().all()
                return [lang[0] for lang in languages]
        except Exception as e:
            logger.error(f"Failed to get available languages: {e}")
            return []
    
    def create_translation_tag(self, application, tag, context=None):
        """Create a new translation tag"""
        try:
            with self.get_session() as session:
                translation_tag = TranslationTag(application=application, tag=tag, context=context)
                session.add(translation_tag)
                session.commit()
                return translation_tag.id
        except Exception as e:
            logger.error(f"Failed to create translation tag: {e}")
            return None
    
    def create_api_key(self, key, application, description=None, user_id=None, expires_at=None):
        """Create a new API key"""
        try:
            with self.get_session() as session:
                api_key = APIKey(
                    key=key,
                    application=application,
                    description=description,
                    user_id=user_id,
                    expires_at=expires_at
                )
                session.add(api_key)
                session.commit()
                return api_key.id
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            return None
    
    def get_api_key(self, key):
        """Get API key by key value"""
        try:
            with self.get_session() as session:
                api_key = session.query(APIKey).filter(
                    APIKey.key == key,
                    APIKey.is_active == True
                ).first()
                return api_key
        except Exception as e:
            logger.error(f"Failed to get API key: {e}")
            return None
    
    def validate_api_key(self, key):
        """Validate an API key and update last_used_at"""
        try:
            with self.get_session() as session:
                api_key = session.query(APIKey).filter(
                    APIKey.key == key,
                    APIKey.is_active == True
                ).first()
                
                if not api_key:
                    return False
                
                # Check if expired
                if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                    return False
                
                # Update last used timestamp
                api_key.last_used_at = datetime.utcnow()
                session.commit()
                
                return True
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return False
    
    def deactivate_api_key(self, key):
        """Deactivate an API key"""
        try:
            with self.get_session() as session:
                api_key = session.query(APIKey).filter(APIKey.key == key).first()
                if api_key:
                    api_key.is_active = False
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to deactivate API key: {e}")
            return False
    
    def get_user_api_keys(self, user_id):
        """Get all API keys for a user"""
        try:
            with self.get_session() as session:
                api_keys = session.query(APIKey).filter(
                    APIKey.user_id == user_id,
                    APIKey.is_active == True
                ).all()
                return api_keys
        except Exception as e:
            logger.error(f"Failed to get user API keys: {e}")
            return []
    
    def get_application_api_keys(self, application):
        """Get all API keys for an application"""
        try:
            with self.get_session() as session:
                api_keys = session.query(APIKey).filter(
                    APIKey.application == application,
                    APIKey.is_active == True
                ).all()
                return api_keys
        except Exception as e:
            logger.error(f"Failed to get application API keys: {e}")
            return []
    
    def get_all_translation_tags(self):
        """Get all translation tags with their translations"""
        self._ensure_database_initialized()
        try:
            with self.get_session() as session:
                # Query all translation tags
                tags = session.query(TranslationTag).all()
                
                result = []
                for tag in tags:
                    # Get translations for this tag
                    translations = session.query(Translation).filter(
                        Translation.translation_tag_id == tag.id
                    ).all()
                    
                    # Convert to dictionary format
                    tag_data = {
                        'id': tag.id,
                        'application': tag.application,
                        'tag': tag.tag,
                        'context': tag.context,
                        'created_at': tag.created_at.isoformat() if tag.created_at else None,
                        'translations': [
                            {
                                'id': t.id,
                                'language': t.language.value if t.language else None,
                                'text': t.text,
                                'is_plural': t.is_plural,
                                'plural_form': t.plural_form,
                                'author_id': t.author_id,
                                'is_active': t.is_active,
                                'created_at': t.created_at.isoformat() if t.created_at else None,
                                'updated_at': t.updated_at.isoformat() if t.updated_at else None
                            }
                            for t in translations
                        ]
                    }
                    result.append(tag_data)
                
                return result
        except Exception as e:
            logger.error(f"Failed to get all translation tags: {e}")
            return []


# Global database manager instance (lazy-loaded)
db_manager = None

def get_db_manager():
    """Get the database manager instance, creating it if needed"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
