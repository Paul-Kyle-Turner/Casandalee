import os
from dotenv import load_dotenv
load_dotenv()

class GameConfigurations:
    class Pathfinder2e:
        NAME = 'Pathfinder 2e'
        RULES = 'rules'
        FEATS = 'feats'
        WEAPONS = 'weapons'
        CLASSES = 'classes'
        ARMORS = 'armors'
        EQUIPMENT = 'equipment'
        FEATS = 'feats'
        CURSES = 'curses'
        DISEASES = 'diseases'
        HAZARDS = 'hazards'
        ACTIONS = 'actions'
        CONDITIONS = 'conditions'
        DEITIES = 'deities'
        DOMAINS = 'domains'
        PLANES = 'planes'
        SPELLS = 'spells'
        VEHICLES = 'vehicles'
        SIEGEWEAPONS = 'siegeweapons'
        BACKGROUNDS = 'backgrounds'
        ALL = 'all'
        CATEGORIES = [RULES, WEAPONS, FEATS, CLASSES, ARMORS,
                      EQUIPMENT, FEATS, CURSES, DISEASES, HAZARDS,
                      ACTIONS, CONDITIONS, DEITIES, DOMAINS, PLANES,
                      SPELLS, VEHICLES, SIEGEWEAPONS, BACKGROUNDS]
        MANUAL_RULES = {
            FEATS: ['feat', 'feats'],
            RULES: ['how do i', 'what is the', 'rule', 'rules'],
            CLASSES: ['class', 'classes', 'alchemist', 'barbarian',
                      'bard', 'champion', 'cleric', 'druid', 'fighter',
                      'investigator', 'magus', 'monk', 'oracle', 'psychic',
                      'ranger', 'rogue', 'sorcerer', 'summoner', 'swashbuckler',
                      'thaumaturge', 'witch', 'wizard', 'gunslinger', 'inventor'],
            SIEGEWEAPONS: ['siege weapons', 'siege weapon'],
        }
        NAMESPACES = {
            RULES: 'pathfinder2e-Rules',
            FEATS: 'pathfinder2e-Feats',
            WEAPONS: 'pathfinder2e-Weapons',
            CLASSES: 'pathfinder2e-Classes',
            ARMORS: 'pathfinder2e-Armors',
            EQUIPMENT: 'pathfinder2e-Equipment',
            FEATS: 'pathfinder2e-Feats',
            CURSES: 'pathfinder2e-Curses',
            DISEASES: 'pathfinder2e-Diseases',
            HAZARDS: 'pathfinder2e-Hazards',
            ACTIONS: 'pathfinder2e-Actions',
            CONDITIONS: 'pathfinder2e-Conditions',
            DEITIES: 'pathfinder2e-Deities',
            DOMAINS: 'pathfinder2e-Domains',
            PLANES: 'pathfinder2e-Planes',
            SPELLS: 'pathfinder2e-Spells',
            VEHICLES: 'pathfinder2e-Vehicles',
            SIEGEWEAPONS: 'pathfinder2e-SiegeWeapons',
            BACKGROUNDS: 'pathfinder2e-Backgrounds',
            ALL: 'pathfinder2e-All',
        }
    GAMES = [Pathfinder2e]


class PineconeConfig:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "asia-southeast1-gcp")
    PINECONE_NAME = os.getenv("PINECONE_NAME", "casandalee-index")
    PINECONE_NAMESPACES = ["pathfinder2e-All"]
    EMBEDDING_PACKAGE = os.getenv("EMBEDDING_PACKAGE", "openai")
    EMBEDDING_ENGINE = os.getenv("EMBEDDING_ENGINE", "text-embedding-ada-002")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    NUM_QUERY_RESPONSE = int(os.getenv("NUM_QUERY_RESPONSE", "2"))
    PINECONE_UPSERT_NAMESPACE = os.getenv("PINECONE_UPSERT_NAMESPACE", "None")


class OpenAIConfig:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", None)
    MODEL_ENGINE = os.getenv("OPENAI_MODEL_ENGINE", "gpt-3.5-turbo")
    EMBEDDING_ENGINE = os.getenv("EMBEDDING_ENGINE", "text-embedding-ada-002")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    MAX_RETRY = int(os.getenv("MAX_RETRY", "5"))


class AI21Config:
    AI21_API_KEY = os.getenv("AI21_API_KEY")
    MODEL_ENGINE = os.getenv("AI21_MODEL_ENGINE", "j2-jumbo-instruct")


class AppConfig:

    DEFAULT_GAME='Pathfinder2e'
    # Flask specific varibles
    FLASK_SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "something")
    PORT=os.getenv("PORT", "8080")

    # Openai Streaming
    STREAM=os.getenv("STREAM", "True") == "True"

    # Google specific variables
    GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET", None)

    # Password
    HASH=os.getenv("HASH", "failed-to-find")

    # judge bcuket
    JUDGE_BUCKET=os.getenv("JUDGE_BUCKET", "judge")

    # Test namespace variables
    TEST_NAMESPACE=os.getenv("TEST_NAMESPACE", "test")
    STAGE=os.getenv("STAGE", "dev")
