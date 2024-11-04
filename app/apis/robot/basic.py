from typing import Optional

from app.models import UserModel, ClanModel
from app.utils import UtilityFunctions
from app.network import BasicAPI
from app.response import JSONResponse

async def main(
    account_id: int,
    region_id: str,
    use_ac: bool,
    ac: Optional[str]
):
    '''获取用户的基本数据

    参数：
        account_id: 用户id
        region_id: 服务器id
        use_ac: 是否使用ac查询数据
        ac: ac值

    返回：
        API_1000_Success
        API_1001_UserNotExist
        API_1003_IllegalAccoutIDorRegionID
        API_1005_UserHiddenProfite

    错误：
        2000-5000: 
    '''

    '''
    请求处理逻辑/
    ├── 0. 收到请求并检查参数合法性
    ├── 1. 从数据库中读取数据(user_basic,user_clan,clan_basic)
    ├── 2. 首次请求接口获取用户和工会的基础数据/
    │   └── (后台任务) 更新user_clan表和clan_basic表
    ├── 3. 从用户基础数据，判断用户的状态(is_acctive,is_public等)/
    │   └── (后台任务) 更新user_info表
    ├── 4. 再次请求接口获取用户详细信息
    └── 5. 将获取的数据进行处理并返回结果
    '''
    user_basic = {
        'id': account_id,
        'name': f'User_{account_id}',
        'karma': 0,
        'crated_at': 0,
        'dog_tag': {},
    }
    user_info = {
        'is_active': True,
        'active_level': 0,
        'is_public': True,
        'total_battles': 0,
        'last_battle_time': 0
    }
    clan_basic = {
        'id': None,
        'tag': None,
        'league': None
    }
    '''
    下面这部分逻辑看起来很复杂，但其实一点也不简单
    '''
    # 检查参数合法性
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 获取用户的username
    user_basic_result: dict = await UserModel.get_user_basic(account_id, region_id)
    if user_basic_result.get('code',None) != 1000:
        return user_basic_result
    user_basic['name'] = user_basic_result['data']['nickname']
    # 获取用户所在工会的clan_id
    user_clan_result: dict = await UserModel.get_user_clan(account_id)
    if user_clan_result.get('code',None) != 1000:
        return user_clan_result
    # 工会数据
    valid_clan = True
    # 判断用户所在工会数据是否有效
    if UtilityFunctions.check_clan_vaild(user_clan_result['data']['updated_at']):
        valid_clan = False
    # 工会的tag和league
    clan_basic_result = None
    if valid_clan and user_clan_result['data']['clan_id']:
        # 如果有效则获取工会tag和league
        clan_basic_result = ClanModel.get_clan_tag_and_league(
            user_clan_result['data']['clan_id'],
            region_id
        )
        # 判断工会数据是否有效
        if UtilityFunctions.check_clan_vaild(clan_basic_result['data']['updated_at']):
            valid_clan = False
        else:
            clan_basic['id'] = user_clan_result['data']['clan_id']
            clan_basic['tag'] = clan_basic_result['data']['tag']
            clan_basic['league'] = clan_basic_result['data']['league']
    # 如果clan数据有效则只请求user数据，否则请求user和clan数据
    if valid_clan:
        basic_data = await BasicAPI.get_user_basic(account_id,region_id,use_ac,ac)
    else:
        basic_data = await BasicAPI.get_user_basic_and_clan(account_id,region_id,use_ac,ac)

    for response in basic_data:
        if response['code'] != 1000 and response['code'] != 1001:
            return response
    # 用户数据
    if basic_data[0]['code'] == 1001:
        # 用户数据不存在
        user_info['is_active'] = False
        # TODO: 更新user_info表
        return JSONResponse.API_1001_UserNotExist
    if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
        # 隐藏战绩
        user_info['is_public'] = False
        user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
        # TODO: 更新user_info表
        return JSONResponse.API_1005_UserHiddenProfite
    user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
    if (
        user_basic_data == {} or
        user_basic_data['basic'] == {} or
        user_basic_data['basic']['leveling_points'] == 0
    ):
        # 用户没有数据
        user_info['total_battles'] = 0
        user_info['last_battle_time'] = 0
        user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
        # TODO: 更新user_info表
        return JSONResponse.API_1006_UserDataisNone
    
    if user_basic['name'] != basic_data[0]['data'][str(account_id)]['name']:
        user_basic['name'] = basic_data[0]['data'][str(account_id)]['name']
        # TODO: 更新user_basic表
    user_info['total_battles'] = user_basic_data['basic']['leveling_points']
    user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
    user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
    # TODO: 更新user_info表
    user_basic['karma'] = user_basic_data['basic']['karma']
    user_basic['dog_tag'] = basic_data[0]['data'][str(account_id)]['dog_tag']
    if not valid_clan:
        #处理工会信息
        user_clan_data = basic_data[1]['data']
        if user_clan_data['clan_id'] != None:
            clan_basic['id'] = user_clan_result['data']['clan_id']
            clan_basic['tag'] = clan_basic_result['data']['tag']
            clan_basic['league'] = UtilityFunctions.get_league_by_color(user_clan_data['clan']['color'])
            # TODO: 更新user_clan表
            # TODO: 更新clan_basic表
    
    # 此处



    
    
    # 检查用户是否存在于数据库
    # 从数据库获取用户信息及用户所在工会
    # 判断用户工会信息是否需要更新
    # 请求获取用户基本信息，并判断相关数据
    # 更新用户数据库（后台任务
    # 获取用户详细数据
    # 处理数据