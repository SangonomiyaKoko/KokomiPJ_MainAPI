from datetime import datetime

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import ClanModel, UserModel
from app.network import BasicAPI
from app.utils import UtilityFunctions
from app.middlewares.celery import celery_app

class GameClan:
    @ExceptionLogger.handle_program_exception_async
    async def get_clan_max_number() -> ResponseDict:
        try:
            result = await ClanModel.get_clan_max_number()
            return result
        except Exception as e:
            raise e

    @ExceptionLogger.handle_program_exception_async
    async def get_clan_basic(
        clan_id: int, 
        region_id: int
    ):
        '''返回工会基本数据'''
        try:
            # 返回数据的格式
            data = {
                'clan': {},
                'season': {},
                'statistics': {}
            }
            # 请求获取user和clan数据
            # 返回的user和clan数据格式
            clan_basic = {
                'id': clan_id,
                'tag': UtilityFunctions.get_clan_default_name(),
                'name': None,
                'level': 0,
                'members': 0
            }
            clan_season = {
                'is_active': True,
                'league': 4, 
                'division': 2, 
                'division_rating': 0, 
                'stage_type': None,
                'stage_process': None
            }
            # 用于后台更新user_info表的数据
            clan_info = {
                'clan_id': clan_id,
                'region_id': region_id,
                'is_active': True,
                'season_number': 0,
                'public_rating': 1100, 
                'league': 4, 
                'division': 2, 
                'division_rating': 0, 
                'last_battle_at': None
            }
            clan_basic_result = await ClanModel.get_clan_tag_and_league(clan_id, region_id)
            if clan_basic_result.get('code',None) != 1000:
                return clan_basic_result
            clan_basic['tag'] = clan_basic_result['data']['tag']
            # 获取claninfo
            basic_data = await BasicAPI.get_clan_basic(clan_id, region_id)
            for response in basic_data:
                if response['code'] != 1000 and response['code'] != 1002:
                    return response
            # 工会数据
            if basic_data[0]['code'] == 1002 or 'tag' not in basic_data[0]['data']['clan']:
                # 工会数据不存在
                clan_info['is_active'] = False
                celery_app.send_task(name="check_clan_info", args=[clan_info])
                return JSONResponse.API_1002_ClanNotExist
            if clan_basic_result['data']['tag'] != basic_data[0]['data']['clan']['tag']:
                # 工会名称改变
                clan_basic['tag'] = basic_data[0]['data']['clan']['tag']
            clan_basic['name'] = basic_data[0]['data']['clan']['name']
            clan_basic['level'] = basic_data[0]['data']['clan']['leveling']
            clan_basic['members'] = basic_data[0]['data']['clan']['members_count']
            # 工会赛季数据
            clan_info['season_number'] = basic_data[0]['data']['wows_ladder']['season_number']
            clan_info['public_rating'] = basic_data[0]['data']['wows_ladder']['public_rating']
            clan_info['league'] = basic_data[0]['data']['wows_ladder']['league']
            clan_info['division'] = basic_data[0]['data']['wows_ladder']['division']
            clan_info['division_rating'] = basic_data[0]['data']['wows_ladder']['division_rating']
            if basic_data[0]['data']['wows_ladder']['last_battle_at']:
                clan_info['last_battle_at'] = int(
                    datetime.fromisoformat(basic_data[0]['data']['wows_ladder']['last_battle_at']).timestamp()
                )
            if basic_data[0]['data']['wows_ladder']['battles_count'] == 0:
                clan_season['league'] = basic_data[0]['data']['wows_ladder']['league']
                clan_season['division'] = basic_data[0]['data']['wows_ladder']['division']
                clan_season['division_rating'] = basic_data[0]['data']['wows_ladder']['division_rating']
            else:
                season_number = basic_data[0]['data']['wows_ladder']['season_number']
                team_number = basic_data[0]['data']['wows_ladder']['team_number']
                for index in basic_data[0]['data']['wows_ladder']['ratings']:
                    if (
                        season_number == index['season_number'] and
                        team_number == index['team_number']
                    ):
                        clan_season['league'] = index['league']
                        clan_season['division'] = index['division']
                        clan_season['division_rating'] = index['division_rating']
                        if index['stage'] is None:
                            break
                        if index['stage']['type'] == 'promotion':
                            clan_season['stage_type'] = '1'
                        else:
                            clan_season['stage_type'] = '2'
                        stage_progress = []
                        for progress in index['stage']['progress']:
                            if progress == 'victory':
                                stage_progress.append(1)
                            else:
                                stage_progress.append(0)
                        clan_season['stage_progress'] = str(stage_progress)
                        break
            if (
                clan_basic_result['data']['tag'] != basic_data[0]['data']['clan']['tag'] or 
                clan_basic_result['data']['league'] != basic_data[0]['data']['wows_ladder']['league']
            ):
                celery_app.send_task(
                    name="check_clan_basic_and_info", 
                    args=[{
                        'clan_id': clan_id,
                        'region_id': region_id,
                        'tag': clan_basic['tag'],
                        'league': clan_info['league']
                    },
                    clan_info]
                )
            else:
                celery_app.send_task(name="check_clan_info", args=[clan_info])
            data['clan'] = clan_basic
            data['season'] = clan_season
            
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e

    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def update_clan_data(self, clan_data: dict) -> ResponseDict:
        try:
            if clan_data.get('clan_basic', None) and clan_data.get('clan_users', None):
                result = await self.update_clan_basic_data(clan_data['clan_basic'])
                if result.get('code', None) != 1000:
                    return result
            elif clan_data.get('clan_basic', None):
                result = await self.update_clan_basic_data(clan_data['clan_basic'])
                return result
            if clan_data.get('clan_info', None):
                result = await self.update_clan_info_data(clan_data['clan_info'])
                return result
            if clan_data.get('clan_users', None):
                result = await self.update_clan_users_data(clan_data['clan_users'])
                if result.get('code', None) != 1000:
                    return result
            if clan_data.get('clan_season', None):
                result = await self.update_clan_season_data(clan_data['clan_season'])
                if result.get('code', None) != 1000:
                    return result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_basic_data(clan_basic: dict) -> ResponseDict:
        try:
            update_result = await ClanModel.update_clan_basic(clan_basic)
            if update_result.get('code', None) != 1000:
                return update_result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_users_data(clan_users_data: dict) -> ResponseDict:
        try:
            # 首先检查用户是否存在于数据库
            if len(clan_users_data['clan_users']) != 0:
                check_user_exist = await UserModel.check_and_insert_missing_users(clan_users_data['clan_users'])
                if check_user_exist.get('code', None) != 1000:
                    return check_user_exist
            celery_app.send_task(
                name="update_clan_users", 
                args=[clan_users_data['clan_id'], clan_users_data['hash_value'], clan_users_data['user_list']]
            )
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
    
    @ExceptionLogger.handle_program_exception_async
    async def update_clan_season_data(clan_season: dict) -> ResponseDict:
        try:
            update_result = await ClanModel.update_clan_season(clan_season)
            if update_result.get('code', None) != 1000:
                return update_result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_info_data(clan_data: dict) -> ResponseDict:
        try:
            result = await ClanModel.update_clan_info_batch(clan_data['region_id'], clan_data['season_number'], clan_data['clan_list'])
            if result.get('code', None) != 1000:
                return result
            return JSONResponse.get_success_response(result['data'])
        except Exception as e:
            raise e