from __future__ import division
import codecs
import datetime
import os
import pprint

from datetime import datetime

BROWSING = '0'
BUYING = '1'
FAVORITE = '2'
CART = '3'

SORTED_ORDER = [BUYING, CART, FAVORITE, BROWSING]

SCORE_MAP = {
    BROWSING: 1,
    FAVORITE: 10,
    CART: 50,
}

THRESHOLD_ACTION_TYPE = BUYING

def count_user(file_path='data_source/t_alibaba_data.csv'):
    command = \
        "awk 'BEGIN{FS=","}{if(!($1 in d)){d[$1] = 1}}END{for(i in d){n++} print n}' data_source/t_alibaba_data.csv"


def get_sorted_uid_by_record_number(data):
    return [e[0]['uid'] for e in sorted(data.values(), key=lambda x: len(x), reverse=True)]


def get_file(file_path='data_source/t_alibaba_data.csv'):

    def _convert_time(time_str):
        return datetime.strptime(time_str, '%m-%d')

    result = {}
    with codecs.open(file_path, 'r', encoding='gb18030') as f:
        for line in f.readlines():
            uid, brand_id, action_type, time = list([e.strip() for e in line.split(',')])
            element = {'brand_id': brand_id, 'action_type': action_type, 'time': _convert_time(time), 'uid': uid}
            if uid in result:
                result[uid].append(element)
            else:
                result[uid] = [element]

    return result

def get_user_records_group_by_final_status(data):
    # eg:
    # { 
    #     BROWSING: {
    #         brand_id : [records]
    #         ..
    #     },
    #     FAVORITE: {
    #         brand_id : [records]
    #         ..
    #     },
    #     xxx
    # }
    brand_list = set([item['brand_id'] for item in data])
    action_type_data = _group_by(data, 'action_type')
    brand_data = _group_by(data, 'brand_id')

    action_type_brand_ids = {}
    occupied_brands = []

    for action_type in SORTED_ORDER:
        records = action_type_data.get(action_type, [])
        brands = set([r['brand_id'] for r in records if r['brand_id'] not in occupied_brands])
        occupied_brands += brands
        action_type_brand_ids[action_type] = brands
    result = {}
    for action_type, brands in action_type_brand_ids.iteritems():
        action_type_result = {}
        for brand in brands:
            records = brand_data[brand]
            action_type_result[brand] = records

            # enhance to make count
            sub_action_type_data = _group_by(records, 'action_type')
            tmp_result = {}
            for key, value in sub_action_type_data.iteritems():
                count = len(value)
                tmp_result[key] = count
            action_type_result[brand] = tmp_result 
            # end enhance

        result[action_type] = action_type_result

    return result


def predict(data):
    ###
    # step 1. get average browse times 
    # step 2. make score for every product 
    # step 3. find the threshold value
    # step 4. find the posible prediction

    average = _get_the_avertage_browse_times(data)
    product_score_map = _score_for_product(data, average)
    threshold_score = _calculation_threshold_value(data, product_score_map)
    predict = _get_the_posible_product(data, product_score_map, threshold_score)
    return predict


def _get_the_avertage_browse_times(data):
    brand_group_data = _group_by(data, 'brand_id')
    total_action = sum([len(value) for value in brand_group_data.values()])
    value = total_action/len(brand_group_data.keys())
    return _accuracy(value)


def _score_for_product(data, average):
    group_data = get_user_records_group_by_final_status(data)    
    product_score_map = {}
    for action_type, brands_data in group_data.iteritems():
        for brand, brand_data in brands_data.iteritems():
            brand_score = 0
            for action_type, count in brand_data.iteritems():
                if action_type in SCORE_MAP:
                    value = (int(count) / average)
                    brand_score += _accuracy(value) * SCORE_MAP[action_type]
            product_score_map[brand] = brand_score
    return product_score_map


def _calculation_threshold_value(data, product_score_map):
    group_data = get_user_records_group_by_final_status(data)
    threshold_group_data = \
        [product_score_map[brand] for brand in group_data[THRESHOLD_ACTION_TYPE].keys()]
    if not threshold_group_data:
        return None
    value = sum(threshold_group_data) / len(threshold_group_data)
    return _accuracy(value)


def _get_the_posible_product(data, product_score_map, threshold_score):
    predict = []
    group_data = get_user_records_group_by_final_status(data)
    for action_type, brands_data in group_data.iteritems():
        if action_type is not THRESHOLD_ACTION_TYPE:
            for brand in  brands_data.keys():
                if product_score_map[brand] >= threshold_score:
                    predict.append(brand)
    return predict


def _group_by(data, key_name):
    result = {}
    for line in data:
        key = line[key_name]
        if key in result: 
            result[key].append(line)
        else:
            result[key] = [line]
    return result


def format_print(data):
    pprint.pprint(data)


def _accuracy(data):
    return data

if __name__ == '__main__':
    data = get_file()
    sorted_uids = get_sorted_uid_by_record_number(data)

    for uid in sorted_uids:
        brand_ids = predict(data[uid])
        if brand_ids:
            print '%s \t %s' %  (uid, ','.join(brand_ids))

    # uid = '3257000'
    # brand_ids = predict(data[uid])
    # format_print(get_user_records_group_by_final_status(data[uid]))





