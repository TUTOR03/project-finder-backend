from typing import List, Optional
from pydantic import Field
from pydantic.main import BaseModel
from models.UserModel import UserBase
from models.BaseModel import BaseModelWithId, BaseModelWithIdConfig, RegisterModelExcInc
from models.SkillTagModel import SkillTagListRequired

class ProjectBase(SkillTagListRequired):
	title: str = Field(min_length=3, max_length=35)
	description: str = Field(default='', max_length=500)
	location: str = Field(default='', max_length=35)
	canRemote: bool = Field(default=False)
	slug: str = Field(min_length=3, max_length=35)
	user: UserBase
	avatarUrl: str = Field(default='')
	coverUrl: str = Field(default='')

class ProjectInDB(BaseModelWithId, ProjectBase):
	class Config(BaseModelWithIdConfig):
		schema_extra = {
		    'example': {
		        'title': 'Our cool project',
		        'description': 'Really cool description of really cool project',
		        'skillTags': [{
		            'label': 'ReactJS'
		        }],
		        'slug': 'our_cool_project',
		        'user': {
		            'username': 'My goodName',
		            'name': 'MyName',
		            'lastname': 'MyLastname',
		            'contact': {
		                'email': 'MyEmail',
		                'telegram': 'MyTelegram',
		                'website': 'MyWebsite'
		            },
		            'gender': 0,
		            'birthDate': '13.12.1337',
		            'location': 'MyLocation',
		            'information': 'MyInformation',
		            'skillTags': [{
		                'label': 'ReactJS'
		            }],
		            'avatarUrl': '/media/avatars/adwada.jpg',
		            'coverUrl': '/media/avatars/akdlakldklakl.jpeg'
		        },
		        'avatarUrl': '/media/avatars/adwad.jpg',
		        'coverUrl': '/media/avatars/adwadaw.jpg'
		    }
		}

# Project Create POST (/api/project/create)
class ProjectCreateReq(ProjectBase):
	class Config:
		include = {'title', 'description', 'skillTags', 'location', 'canRemote'}

RegisterModelExcInc(ProjectCreateReq)

class ProjectChangeRes(ProjectBase):
	pass

# Project My GET (/api/project/my)

class ProjectMyRes(ProjectBase):
	class Config:
		exclude = {'user'}

RegisterModelExcInc(ProjectMyRes)

# Project My POST (/api/project/my)

class ProjectChangeMyReq(ProjectBase):
	class Config:
		include = {'description', 'skillTags', 'location', 'canRemote'}

RegisterModelExcInc(ProjectChangeMyReq)

class ProjectChangeMyRes(ProjectBase):
	pass

# Project Info GET (/api/project/<slug>)

class ProjectInfoRes(ProjectBase):
	pass

# Project List Suitable GET (/api/project/list_suitable)

class ProjectListSuitableReq(BaseModel):
	skip: int = Field(default=0)
	limit: int = Field(default=20)

class ProjectListSuitableRes(ProjectBase):
	pass

# User List Suitable POST (/api/user/list_suitable)
class UserListSuitableReq(ProjectBase):
	limit: int = Field(default=20)
	skip: int = Field(default=0)

	class Config:
		include = {'slug', 'limit', 'skip'}

RegisterModelExcInc(UserListSuitableReq)

# User Me GET (/api/user/me)

class UserSelfRes(UserBase):
	projects: List[ProjectMyRes]
