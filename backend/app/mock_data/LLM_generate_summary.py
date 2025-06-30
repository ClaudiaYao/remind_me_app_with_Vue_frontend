
from sqlalchemy import func
from app.services import database, config, LLM_utils
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Database Engine & Session
engine = create_engine(config.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

def get_accumulated_descriptions():
    
    try:
        db = SessionLocal()
        
        results = db.query(
            database.UserRemindee.user_id,
                database.UserRemindee.person_name,
                func.array_agg(func.distinct(database.UserRemindee.relationship)).label("unique_relationships"),
                func.array_agg(func.distinct(database.UserRemindee.summary)).label("accumulated_summary")
            ).group_by(database.UserRemindee.user_id, database.UserRemindee.person_name).all()
        
        return results
    except Exception as e:
        print(f"e")
    finally:
        db.close() 
    

def generate_summaries(results):
    llm_model = LLM_utils.LLM_Generate_Summary(api_key=config.LLM_MODEL_KEY)
    try:
        db = SessionLocal() 
        
        for result in results:
            gen_summary = llm_model.generate(person_name=result[1], relationship=','.join(result[2]), description=','.join(result[3]))
            new_entry = database.RemindeeSummary(
                        user_id= result[0],
                        person_name=result[1],
                        summary=gen_summary
                    )
            db.add(new_entry)
        db.commit()
    except Exception as e:
        print(f"{e}")
    finally:
        db.close()
        

results = get_accumulated_descriptions()
print(results)
print(f"totally there are {len(results)} remindees.")

print(results[0])

generate_summaries(results)
print("generated AI summaries for all the existing users")

