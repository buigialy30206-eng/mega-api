"""
Random User Generator API
Generate fake user profiles for testing.
"""

import random, string

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
async def root():
    return {"service": "Random User Generator API", "version": "1.0.0", "related": ["UUID Generator API", "Email Validator API"]}

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

FIRST_NAMES = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda","David","Elizabeth","William","Barbara","Richard","Susan","Joseph","Jessica","Thomas","Sarah","Christopher","Karen","Daniel","Lisa","Matthew","Nancy","Anthony","Betty","Mark","Margaret","Donald","Sandra","Steven","Ashley","Paul","Kimberly","Andrew","Emily","Joshua","Donna","Kenneth","Michelle","Kevin","Carol","Brian","Amanda","George","Dorothy","Timothy","Melissa","Ronald","Deborah"]

LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores","Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts"]

DOMAINS = ["gmail.com","yahoo.com","hotmail.com","outlook.com","proton.me"]

JOBS = ["Software Engineer","Data Analyst","Product Manager","Designer","Marketing Manager","Sales Representative","Teacher","Nurse","Accountant","Consultant","Writer","Developer","Manager","Director","Coordinator"]

class RandomUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    job: str
    username: str

def gen_user() -> RandomUser:
    f = random.choice(FIRST_NAMES)
    l = random.choice(LAST_NAMES)
    return RandomUser(
        first_name=f, last_name=l,
        email=f"{f.lower()}.{l.lower()}{random.randint(1,999)}@{random.choice(DOMAINS)}",
        phone=f"+1-{random.randint(200,999)}-{random.randint(100,9999)}",
        job=random.choice(JOBS),
        username=f"{f.lower()}{l.lower()}{random.randint(1,99)}",
    )

@router.get("/generate-batch")
async def generate_batch(count: int = Query(10, ge=1, le=100)):
    return {"users": [gen_user().model_dump() for _ in range(count)]}
