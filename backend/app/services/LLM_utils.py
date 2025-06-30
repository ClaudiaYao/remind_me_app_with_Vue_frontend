
from openai import OpenAI
from sqlalchemy import func
from app.services import database, config
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select

class LLM_Generate_Summary:
    def __init__(self, api_key: str, base_url: str = "https://api.deepinfra.com/v1/openai",
                 model: str = "Qwen/Qwen2.5-7B-Instruct", temperature: float = 0.7):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.temperature = temperature
        self.total_tokens = 0

    def generate(self, person_name, relationship, description: str) -> str:
        prompt = f"""You are the AI reminder of the dementia patient. The following is a person information in the patient's social 
        network. 
        person_name: {person_name},
        relationship: {relationship},
        descriptin: {description}
        Please summarize the person's relationship with the patient and recall what they have done together. Use conforting and torching tune
        as if you are talking with the dementia person.
        Your response should be within 100 words."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=256,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in API call: {e}")
            return "", 0
        

# Database Engine & Session
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_accumulated_descriptions_for_remindee(user_id, remindee_name):
    
    try:
        db = SessionLocal()
        
        if config.USE_POSTGRESQL == "1":
            results = db.query(
                    func.array_agg(func.distinct(database.UserRemindee.relationship)).label("unique_relationships"),
                    func.array_agg(func.distinct(database.UserRemindee.summary)).label("accumulated_summary")
                    # func.string_agg(database.UserRemindee.summary, ',').label("accumulated_summary")
                ).filter(database.UserRemindee.user_id == user_id, database.UserRemindee.person_name == remindee_name).first()
        else:
            results = db.query(
                func.group_concat(func.distinct(database.UserRemindee.relationship)).label("unique_relationships"),
                func.group_concat(func.distinct(database.UserRemindee.summary)).label("accumulated_summary")
                ).filter(database.UserRemindee.user_id == user_id, database.UserRemindee.person_name == remindee_name).first()
        
        return ', '.join(results[0]), ", ".join(results[1])
    except Exception as e:
        print(f"{e}")
    finally:
        db.close() 
    
# generate summary for remindee, meanwhile, update database
def generate_summary_for_remindee(user_id, remindee_name, relationship, accumulated_summary):
    llm_model = LLM_Generate_Summary(api_key=config.LLM_MODEL_KEY)
    try:
        db = SessionLocal() 

        gen_summary = llm_model.generate(person_name=remindee_name, relationship=relationship, description=accumulated_summary)

        if len(gen_summary) < 8:
            gen_summary = "You AI assistant needs more images of your remindee to generate summary. Please feed me more pictures and words." 
            
        stmt = select(database.RemindeeSummary).where((database.RemindeeSummary.user_id == user_id) & (database.RemindeeSummary.person_name == remindee_name))
        result = db.execute(stmt).scalar_one_or_none()

        if result:
            # Record exists — update
            setattr(result, "summary", gen_summary)
        else:
            # new record
            new_entry = database.RemindeeSummary(
                            user_id = user_id,
                            person_name=remindee_name,
                            summary=gen_summary)
            db.add(new_entry)
            db.commit()
        
        
        stmt = select(database.UserRemindee).where((database.UserRemindee.user_id == user_id) & (database.UserRemindee.person_name == remindee_name)).order_by(func.random()).limit(1)
        result = db.execute(stmt).scalar_one_or_none()
        
        return gen_summary, result.image_object_key
    except Exception as e:
        print(f"{e}")
    finally:
        db.close()
        
        
        
        
        
