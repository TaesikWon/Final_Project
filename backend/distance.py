import math
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    """
    Haversine 거리 계산 (미터 단위).
    단일 숫자 또는 pandas Series 모두 지원.
    """
    R = 6371000  # 지구 반지름 (m)

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def haversine_df(df_lat, df_lon, target_lat, target_lon):
    """
    pandas DataFrame 형태로 벡터 연산 (빠름)
    """
    R = 6371000  # meters

    lat1 = df_lat * (math.pi / 180)
    lon1 = df_lon * (math.pi / 180)
    lat2 = target_lat * (math.pi / 180)
    lon2 = target_lon * (math.pi / 180)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (np.sin(dlat/2)**2 +
         np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    return R * c
