from pydantic import BaseModel, HttpUrl, EmailStr

class ProjectSubmission(BaseModel):
    name: str
    email: EmailStr
    github_url: HttpUrl
    linkedin_url: HttpUrl
    twitter_url: HttpUrl