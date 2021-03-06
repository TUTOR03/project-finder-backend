from typing import List
from bson.objectid import ObjectId
from pymongo.database import Database
from core.config import pwdContext
import aiofiles.os
from fastapi import UploadFile

from models.UserModel import UserSelfChangeReq, UserInDB, UserRegisterReq

def getUserByUsername(db: Database, username: str):
	user = db.users.find_one({'username': username})
	if user:
		return UserInDB(**user)

def getUsersBySkillTags(db: Database, username: str, skillTags: List[str], skip: int = 0, limit: int = 20):
	users = db.users.aggregate([{
	    '$match': {
	        'skillTags.label': {
	            '$in': skillTags
	        },
	        'username': {
	            '$ne': username
	        }
	    }
	}, {
	    '$addFields': {
	        '__order': {
	            '$size': {
	                '$setIntersection': ['$skillTags.label', skillTags]
	            }
	        }
	    }
	}, {
	    '$sort': {
	        '__order': -1
	    }
	}, {
	    '$skip': skip,
	}, {
	    '$limit': limit
	}])
	return list(map(lambda ob: UserInDB(**ob), users))

def createUser(db: Database, user: UserRegisterReq, slugUsername: str):
	hashedPassword = generatePasswordHash(user.password)
	newUser = UserInDB(**{**user.dict(), 'username': slugUsername, 'passwordHash': hashedPassword})
	db.users.insert_one(newUser.dict())

def changeUser(db: Database, username: str, userChange: UserSelfChangeReq):
	user = db.users.find_one_and_update({'username': username}, {'$set': userChange.dict()})
	return user

def generatePasswordHash(password: str):
	return pwdContext.hash(password)

def checkPasswordHash(password: str, passwordHash: str):
	return pwdContext.verify(password, passwordHash)

async def setUserAvatar(db: Database, user: UserInDB, avatarFile: UploadFile, fileName: str):
	async with aiofiles.open(f'./media/avatars/{fileName}', 'wb') as outFile:
		while content := await avatarFile.read(1024):
			await outFile.write(content)
	db.users.find_one_and_update({'_id': user.id}, {'$set': {'avatarUrl': f'/media/avatars/{fileName}'}})

async def removeUserAvatar(db: Database, user: UserInDB):
	if user.avatarUrl:
		db.users.find_one_and_update({'_id': user.id}, {'$set': {'avatarUrl': ''}})
		await aiofiles.os.remove(f'.{user.avatarUrl}')