import csv

from pandas import DataFrame, to_datetime, to_numeric, read_csv
from geopandas import GeoDataFrame, points_from_xy

WGS_EPSG = 4326

def convert_to_numeric(df: DataFrame, col_list: list[str, str], date_col: str = 'sample_dt') -> DataFrame:
    cdf = df.copy()
    cdf[col_list] = cdf[col_list].apply(to_numeric, errors='coerce')
    cdf[date_col] = to_datetime(cdf[date_col], errors='coerce', dayfirst=False)
    return cdf

def df_to_geo(df: DataFrame, lon_col: str = 'lon', lat_col: str = 'lat') -> GeoDataFrame:
    cdf = df.copy()
    cdf = cdf.dropna(subset=[lat_col, lon_col])
    cdf['geometry'] = points_from_xy(cdf[lon_col], cdf[lat_col])
    return GeoDataFrame(cdf, geometry='geometry', crs=WGS_EPSG)

def read_data(csv_path: str) -> DataFrame:
    df = read_csv(csv_path, sep=",", engine="python", quoting=csv.QUOTE_NONE)
    df = df.map(lambda x: x.strip('"') if isinstance(x, str) else x)
    df.columns = df.columns.str.strip('"')
    return df