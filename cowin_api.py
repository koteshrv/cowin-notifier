from datetime import datetime, timedelta
from typing import Union, List
from fake_useragent import UserAgent
from requests.exceptions import HTTPError
import requests, const

def today():
    return datetime.now().strftime("%d-%m-%Y")

def filter_centers_by_age_limit(centers: dict, min_age_limit: int):
    original_centers = centers.get('centers')
    filtered_centers = {'centers': []}
    for index, center in enumerate(original_centers):
        filtered_sessions = []
        for session in center.get('sessions'):
            if session.get('min_age_limit') == min_age_limit:
                filtered_sessions.append(session)
        if len(filtered_sessions) > 0:
            center['sessions'] = filtered_sessions
            filtered_centers['centers'].append(center)

    return filtered_centers

def call_api(url) -> Union[HTTPError, dict]:
    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.random}
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return e

    return response.json()

def get_states():
    url = const.states_list_url
    return call_api(url)

def get_districts(state_id: str):
    url = f"{const.districts_list_url}/{state_id}"
    return call_api(url)

def get_availability_by_base(caller: str, areas: Union[str, List[str]], date: str, min_age_limt: int):
    """this function is called by the get availability function
    this is separated out so that the parent functions have the same
    structure and development becomes easier"""
    area_type, base_url = 'pincode', const.availability_by_pin_code_url
    if caller == 'district':
        area_type, base_url = 'district_id', const.availability_by_district_url
    # if the areas is a str, convert to list
    if isinstance(areas, str):
        areas = [areas]
    # make a separate call for each of the areas
    results = []
    for area_id in areas:
        url = f"{base_url}?{area_type}={area_id}&date={date}"
        if min_age_limt:
            curr_result = filter_centers_by_age_limit(call_api(url), min_age_limt)
        else:
            curr_result = call_api(url)
        # append
        if curr_result:
            results += curr_result['centers']

    # return the results in the same format as returned by the api
    return {'centers': results}

def get_availability_by_district(district_id: Union[str, List[str]], date: str = today(), min_age_limt: int = None):
    return get_availability_by_base(caller='district', areas=district_id, date=date, min_age_limt=min_age_limt)

def get_availability_by_pincode(pin_code: Union[str, List[str]], date: str = today(), min_age_limt: int = None):
    return get_availability_by_base(caller='pincode', areas=pin_code, date=date, min_age_limt=min_age_limt)