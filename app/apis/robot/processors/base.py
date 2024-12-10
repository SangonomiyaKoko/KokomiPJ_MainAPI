from app.utils import ColorUtils, Rating_Algorithm

class BaseFormatData:
    def format_basic_processed_data(
        algo_type: str | None,
        processed_data: dict,
        show_eggshell: bool = False,
        show_rating_details: bool = False
    ):
        '''格式化处理好的数据

        根据需要来启用是否启用彩蛋
        
        '''
        if show_rating_details:
            result = {
                'battles_count': 0,
                'win_rate': 0.0,
                'avg_damage': 0,
                'avg_frags': 0.0,
                'avg_exp': 0,
                'rating': 0,
                'rating_class': 0,
                'rating_next': 0,
                'win_rate_color': '#808080',
                'avg_damage_color': '#808080',
                'avg_frags_color': '#808080',
                'rating_color': '#808080'
            }
            result['battles_count'] = processed_data['battles_count']
            result['win_rate'] = round(processed_data['wins']/processed_data['battles_count']*100,2)
            result['avg_damage'] = int(processed_data['damage_dealt']/processed_data['battles_count'])
            result['avg_frags'] = round(processed_data['frags']/processed_data['battles_count'],2)
            result['avg_exp'] = int(processed_data['original_exp']/processed_data['battles_count'])
            if not algo_type:
                result['rating'] = -2
                rating_class, rating_next = Rating_Algorithm.get_rating_class(algo_type,-2,show_eggshell)
                result['rating_class'] = rating_class
                result['rating_next'] = rating_next
                result['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
                result['avg_damage_color'] = ColorUtils.get_rating_color(1,-2)
                result['avg_frags_color'] = ColorUtils.get_rating_color(2,-2)
                result['rating_color'] = ColorUtils.get_rating_color(3,-2)
            elif processed_data['value_battles_count'] != 0:
                result['rating'] = int(processed_data['personal_rating']/processed_data['value_battles_count'])
                rating_class, rating_next = Rating_Algorithm.get_rating_class(algo_type,result['rating'],show_eggshell)
                result['rating_class'] = rating_class
                result['rating_next'] = rating_next
                result['win_rate_color'] = ColorUtils.get_rating_color(0,result['win_rate'])
                result['avg_damage_color'] = ColorUtils.get_rating_color(1,processed_data['n_damage_dealt']/processed_data['value_battles_count'])
                result['avg_frags_color'] = ColorUtils.get_rating_color(2,processed_data['n_frags']/processed_data['value_battles_count'])
                result['rating_color'] = ColorUtils.get_rating_color(3,processed_data['personal_rating']/processed_data['value_battles_count'])
            else:
                result['rating'] = -1
                rating_class, rating_next = Rating_Algorithm.get_rating_class(algo_type,-1,show_eggshell)
                result['rating_class'] = rating_class
                result['rating_next'] = rating_next
                result['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
                result['avg_damage_color'] = ColorUtils.get_rating_color(1,-1)
                result['avg_frags_color'] = ColorUtils.get_rating_color(2,-1)
                result['rating_color'] = ColorUtils.get_rating_color(3,-1)
            result['win_rate_color'] = "#{:02X}{:02X}{:02X}".format(*result['win_rate_color'])
            result['avg_damage_color'] = "#{:02X}{:02X}{:02X}".format(*result['avg_damage_color'])
            result['avg_frags_color'] = "#{:02X}{:02X}{:02X}".format(*result['avg_frags_color'])
            result['rating_color'] = "#{:02X}{:02X}{:02X}".format(*result['rating_color'])
            result['battles_count'] = '{:,}'.format(result['battles_count']).replace(',', ' ')
            result['win_rate'] = '{:.2f}%'.format(result['win_rate'])
            result['avg_damage'] = '{:,}'.format(result['avg_damage']).replace(',', ' ')
            result['avg_frags'] = '{:.2f}'.format(result['avg_frags'])
            result['avg_exp'] = '{:,}'.format(result['avg_exp']).replace(',', ' ')
            result['rating'] = '{:,}'.format(result['rating']).replace(',', ' ')
        else:
            result = {
                'battles_count': 0,
                'win_rate': 0.0,
                'avg_damage': 0,
                'avg_frags': 0.0,
                'rating': 0,
                'win_rate_color': '#808080',
                'avg_damage_color': '#808080',
                'avg_frags_color': '#808080',
                'rating_color': '#808080'
            }
            result['battles_count'] = processed_data['battles_count']
            result['win_rate'] = round(processed_data['wins']/processed_data['battles_count']*100,2)
            result['avg_damage'] = int(processed_data['damage_dealt']/processed_data['battles_count'])
            result['avg_frags'] = round(processed_data['frags']/processed_data['battles_count'],2)
            if not algo_type:
                result['rating'] = -2
                result['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
                result['avg_damage_color'] = ColorUtils.get_rating_color(1,-2)
                result['avg_frags_color'] = ColorUtils.get_rating_color(2,-2)
                result['rating_color'] = ColorUtils.get_rating_color(3,-2)
            elif processed_data['value_battles_count'] != 0:
                result['rating'] = int(processed_data['personal_rating']/processed_data['value_battles_count'])
                result['win_rate_color'] = ColorUtils.get_rating_color(0,result['win_rate'])
                result['avg_damage_color'] = ColorUtils.get_rating_color(1,processed_data['n_damage_dealt']/processed_data['value_battles_count'])
                result['avg_frags_color'] = ColorUtils.get_rating_color(2,processed_data['n_frags']/processed_data['value_battles_count'])
                result['rating_color'] = ColorUtils.get_rating_color(3,processed_data['personal_rating']/processed_data['value_battles_count'])
            else:
                result['rating'] = -1
                result['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
                result['avg_damage_color'] = ColorUtils.get_rating_color(1,-1)
                result['avg_frags_color'] = ColorUtils.get_rating_color(2,-1)
                result['rating_color'] = ColorUtils.get_rating_color(3,-1)
            result['win_rate_color'] = "#{:02X}{:02X}{:02X}".format(*result['win_rate_color'])
            result['avg_damage_color'] = "#{:02X}{:02X}{:02X}".format(*result['avg_damage_color'])
            result['avg_frags_color'] = "#{:02X}{:02X}{:02X}".format(*result['avg_frags_color'])
            result['rating_color'] = "#{:02X}{:02X}{:02X}".format(*result['rating_color'])
            result['battles_count'] = '{:,}'.format(result['battles_count']).replace(',', ' ')
            result['win_rate'] = '{:.2f}%'.format(result['win_rate'])
            result['avg_damage'] = '{:,}'.format(result['avg_damage']).replace(',', ' ')
            result['avg_frags'] = '{:.2f}'.format(result['avg_frags'])
            result['rating'] = '{:,}'.format(result['rating']).replace(',', ' ')
        return result