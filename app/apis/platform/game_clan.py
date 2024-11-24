import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import ClanModel, UserModel
from app.middlewares.celery import task_check_user_basic, task_update_clan_users

class GameClan:
    @ExceptionLogger.handle_program_exception_async
    async def get_clan(region_id: int) -> ResponseDict:
        try:
            data = {
                'clans': None
            }
            result = await ClanModel.get_clan_by_rid(region_id)
            if result.get('code', None) != 1000:
                return result
            data['clans'] = result['data']
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_users_data(clan_users_data: dict) -> ResponseDict:
        try:
            # 首先检查用户是否存在于数据库
            check_user_exist = await UserModel.check_and_insert_missing_users(clan_users_data['clan_users'])
            if check_user_exist.get('code', None) != 1000:
                return check_user_exist
            # 再写入user_clan数据库
            user_id_list = []
            for temp_data in clan_users_data['clan_users']:
                user_id_list.append(temp_data['account_id'])
            task_update_clan_users.delay(clan_users_data['clan_id'], user_id_list)
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

test_data = {
    'clan_id': 2000015816, 
    'region_id': 1, 
    'clan_users': [
        {'account_id': 2004849974, 'region_id': 1, 'nickname': 'haoj8qingxing'}, 
        {'account_id': 2004857521, 'region_id': 1, 'nickname': 'silenceworld'}, 
        {'account_id': 2007721529, 'region_id': 1, 'nickname': 'Yamamoto_Isoko'}, 
        {'account_id': 2008331408, 'region_id': 1, 'nickname': 'aaaabcaaa'}, 
        {'account_id': 2008842768, 'region_id': 1, 'nickname': 'SMyaro97'}, 
        {'account_id': 2009263892, 'region_id': 1, 'nickname': 'ColdRabbit_prpr'}, 
        {'account_id': 2012444271, 'region_id': 1, 'nickname': 'Chen_Zhechun_ProMix'}, 
        {'account_id': 2017713562, 'region_id': 1, 'nickname': 'WCNMB_IFUZE'}, 
        {'account_id': 2017740247, 'region_id': 1, 'nickname': 'Mio__TyPe91'}, 
        {'account_id': 2018820054, 'region_id': 1, 'nickname': 'Shiki_Natsumeprpr'}, 
        {'account_id': 2019839828, 'region_id': 1, 'nickname': 'IoLoco'}, 
        {'account_id': 2019989243, 'region_id': 1, 'nickname': '96Hans'}, 
        {'account_id': 2020181624, 'region_id': 1, 'nickname': 'Incomparable_wcnm'}, 
        {'account_id': 2020228470, 'region_id': 1, 'nickname': 'USSMissouri63'}, 
        {'account_id': 2020647926, 'region_id': 1, 'nickname': 'Niconiconi_6'}, 
        {'account_id': 2020809318, 'region_id': 1, 'nickname': 'F1echaZ'}, 
        {'account_id': 2021095367, 'region_id': 1, 'nickname': 'nihaonihao123_1'}, 
        {'account_id': 2022005980, 'region_id': 1, 'nickname': 'Aimiki'}, 
        {'account_id': 2022576481, 'region_id': 1, 'nickname': 'luna_sakurakouji_my_wife'}, 
        {'account_id': 2023078722, 'region_id': 1, 'nickname': 'Cold_Rabbit'}, 
        {'account_id': 2023191893, 'region_id': 1, 'nickname': 'Ran_An'}, 
        {'account_id': 2023212080, 'region_id': 1, 'nickname': 'Mejiro__McQueen_'}, 
        {'account_id': 2023455015, 'region_id': 1, 'nickname': 'Anon__Chihaya'}, 
        {'account_id': 2023601656, 'region_id': 1, 'nickname': 'Ave_Mujica_Sakiko'}, 
        {'account_id': 2023619512, 'region_id': 1, 'nickname': 'SangonomiyaKokomi_'}, 
        {'account_id': 2024128819, 'region_id': 1, 'nickname': 'MisonoMika_Daisuki'}, 
        {'account_id': 2024140417, 'region_id': 1, 'nickname': 'Sprite_SF'}, 
        {'account_id': 2024274136, 'region_id': 1, 'nickname': 'KIRIFUS'}, 
        {'account_id': 2024482316, 'region_id': 1, 'nickname': 'MMP_defender'}, 
        {'account_id': 2024843403, 'region_id': 1, 'nickname': 'WangDarkLei'}, 
        {'account_id': 2025049465, 'region_id': 1, 'nickname': '1042567503'}, 
        {'account_id': 2025758135, 'region_id': 1, 'nickname': 'E_5_ovO'}, 
        {'account_id': 2025892340, 'region_id': 1, 'nickname': 'WangDeepLei'}, 
        {'account_id': 2025928770, 'region_id': 1, 'nickname': 'W_C_N_M_M'}, 
        {'account_id': 2027585763, 'region_id': 1, 'nickname': 'Tohsaka_Rin_my_wife'}, 
        {'account_id': 2027931605, 'region_id': 1, 'nickname': 'Cirrea_desu'}, 
        {'account_id': 2028135727, 'region_id': 1, 'nickname': 'HGGZ_HYIVIQZ'}, 
        {'account_id': 2028304719, 'region_id': 1, 'nickname': 'RenamedUser_2028304719'}, 
        {'account_id': 2028500100, 'region_id': 1, 'nickname': 'ZenlessZoneZero'}, 
        {'account_id': 2028684947, 'region_id': 1, 'nickname': 'LeberechtHan1214'}, 
        {'account_id': 2029562378, 'region_id': 1, 'nickname': 'DaDaZi'}, 
        {'account_id': 2030261558, 'region_id': 1, 'nickname': '_Hirasawa__Yui'}, 
        {'account_id': 2031702603, 'region_id': 1, 'nickname': 'Yui_Shousetsu'}, 
        {'account_id': 2032122959, 'region_id': 1, 'nickname': 'Adachi_Sakura_MywifePrPr'}, 
        {'account_id': 2033063922, 'region_id': 1, 'nickname': 'Schrodinger_Pigeon'}, 
        {'account_id': 2033703601, 'region_id': 1, 'nickname': 'Hayase_Yuuka_100KG'}, 
        {'account_id': 2037972033, 'region_id': 1, 'nickname': 'Call_me_Lord'}, 
        {'account_id': 2038533205, 'region_id': 1, 'nickname': 'Tau_Neutrino_Fermi'}, 
        {'account_id': 3002359366, 'region_id': 1, 'nickname': 'JusH0u'}
    ]
}