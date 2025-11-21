from sqlalchemy import create_engine,inspect
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("POSTGRES_URI"))
inspector = inspect(engine)
print(inspector.get_table_names())
