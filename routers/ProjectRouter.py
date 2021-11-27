from typing import List
from fastapi import APIRouter, status, Depends, Body, HTTPException
from pymongo.database import Database
from controllers.ProjectController import createProject, getProjectBySlug, getProjectsBySkillTags, getSelfProjects, updateProject
from controllers.TokenController import getAuthorizedUser
from core.errors import API_ERRORS
from core.utils import slugifyString
from db.mongodb import getDatabase
from models.ProjectModel import ProjectBase, ProjectBaseWithoutUser, ProjectChangeReq, ProjectCreateReq
from models.UserModel import UserInDB

projectRouter = APIRouter(prefix='/project', tags=['project'])

@projectRouter.post('/create', status_code=status.HTTP_201_CREATED, response_model=ProjectBase)
async def create(project: ProjectCreateReq = Body(...),
                 user: UserInDB = Depends(getAuthorizedUser),
                 db: Database = Depends(getDatabase)):
	slugTitle = slugifyString(project.title, True)
	predictProject = getProjectBySlug(db, slugTitle)
	if predictProject:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=API_ERRORS['project.AlreadyExists'])
	createProject(db, project, slugTitle, user)
	return {**project.dict(), 'slug': slugTitle, 'user': user.dict()}

@projectRouter.get('/my', status_code=status.HTTP_200_OK, response_model=List[ProjectBaseWithoutUser])
async def selfProjects(user: UserInDB = Depends(getAuthorizedUser), db: Database = Depends(getDatabase)):
	projects = getSelfProjects(db, user.username)
	return projects

@projectRouter.get('/list_suitable', status_code=status.HTTP_200_OK, response_model=List[ProjectBase])
async def listSuitable(user: UserInDB = Depends(getAuthorizedUser), db: Database = Depends(getDatabase)):
	userSkillTags = list(map(lambda ob: ob['label'], user.dict()['skillTags']))
	suitableProject = getProjectsBySkillTags(db, user.username, userSkillTags)
	return suitableProject

@projectRouter.get('/{slug}', status_code=status.HTTP_200_OK, response_model=ProjectBase)
async def getProject(slug: str,
                     user: UserInDB = Depends(getAuthorizedUser),
                     db: Database = Depends(getDatabase)):
	project = getProjectBySlug(db, slug)
	if not project:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=API_ERRORS['project.NotFound'])
	return project

@projectRouter.post('/{slug}', status_code=status.HTTP_200_OK, response_model=ProjectBase)
async def changeProject(slug: str,
                        projectChange: ProjectChangeReq = Body(...),
                        user: UserInDB = Depends(getAuthorizedUser),
                        db: Database = Depends(getDatabase)):
	project = getProjectBySlug(db, slug)
	if not project:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=API_ERRORS['project.NotFound'])
	if project.user.username != user.username:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=API_ERRORS['project.NoAccess'])
	updateProject(db, slug, projectChange)
	return getProjectBySlug(db, slug)
