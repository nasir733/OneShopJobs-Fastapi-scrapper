from fastapi import FastAPI,BackgroundTasks
from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from stackoverflowscrapper import extract_jobs
from fastapi.responses import JSONResponse

import time
import os
import asyncio
from models import JobCategory, Jobs_Pydantic, Jobs
import uvicorn
# from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware
# config = dotenv_values(".env")
config ={}
app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:9000",
    'http://'
]


@app.get("/get-jobs")
async def getJobs():
    return await Jobs_Pydantic.from_queryset(Jobs.all())

@app.get("/")
async def index(background_tasks: BackgroundTasks):
    return {"message": "Hello World"}
@app.get("/create-category")
async def createCategory():
    return await JobCategory.create(name="Python")


@app.get("/scrape-stackoverflow")
async def scrapeStackOverflow(background_tasks: BackgroundTasks):
    background_tasks.add_task(startAsyncScrapper)
    return {"message": "the scrapping has started"}


async def startAsyncScrapper():
    print("hello from stackoverflow jobs section")

    actions = []
    start_time = time.time()
    jobsName = await JobCategory.all()
    print(jobsName)
    jobsNames = ['python', 'javascript', 'django', 'channels']
    # print(jobsName)
    for job in jobsName:
        url = f"https://stackoverflow.com/jobs?q={job}"
        actions.append(asyncio.ensure_future(extract_jobs(9, url, job)))
    await asyncio.gather(*actions)
    total_time = time.time() - start_time

    return JSONResponse(f'the async stackoverflow scrapper is done in {total_time} seconds   ')


register_tortoise(
    app,
    db_url=f'postgres://{ os.environ.get("USER")}:{ os.environ.get("PASSWORD")}@{ os.environ.get("HOST")}:5432/{ os.environ.get("NAME")}',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == "__main__":
    uvicorn.run(app,  port=4000)
