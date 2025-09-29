from geopandas import GeoDataFrame, points_from_xy
from pandas import read_csv
import csv

if __name__ == '__main__':
    df = read_csv("data/dados.csv", sep=",", engine="python", quoting=csv.QUOTE_NONE)
    # Clean data
    df = df.map(lambda x: x.strip('"') if isinstance(x, str) else x)
    df.columns = df.columns.str.strip('"')
    # Convert to GeoDf
    df['geometry'] = points_from_xy(df['lon'], df['lat'])
    gdf = GeoDataFrame(df, geometry='geometry', crs=4326)