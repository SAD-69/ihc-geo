import os
import csv
import folium
import folium.plugins as fp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
from branca.element import Template, MacroElement
from tools import df_to_geo, read_data, convert_to_numeric

DATA_DIR = "data/dados.csv"
OUT_DIR = "maps"
OUT_HTML_MAP = os.path.join(OUT_DIR, "mapa.html")

os.makedirs(OUT_DIR, exist_ok=True)

def create_bar_icon(pol_a, pol_b, max_val=10):
    """Cria ícone de barras verticais para pol_a e pol_b"""
    
    # Normalizar valores para altura das barras (0-100%)
    height_a = min(100, (pol_a / max_val) * 100) if pd.notna(pol_a) else 0
    height_b = min(100, (pol_b / max_val) * 100) if pd.notna(pol_b) else 0
    
    # Cores para as barras
    color_a = '#e74c3c'  # Vermelho para pol_a
    color_b = '#3498db'  # Azul para pol_b
    
    html = f'''
    <div style="
        position: relative;
        width: 30px;
        height: 30px;
        background: rgba(255,255,255,0.8);
        border: 2px solid #2c3e50;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <div style="
            position: absolute;
            bottom: 5px;
            left: 7px;
            width: 6px;
            height: {height_a * 10}%;
            background: {color_a};
            border-radius: 1px;
            max-height: 20px;
        "></div>
        <div style="
            position: absolute;
            bottom: 5px;
            right: 7px;
            width: 6px;
            height: {height_b * 10}%;
            background: {color_b};
            border-radius: 1px;
            max-height: 20px;
        "></div>
    </div>
    '''
    return folium.DivIcon(html=html, icon_size=(30, 30), icon_anchor=(15, 15))

def create_timeseries_chart(station_data, station_name, max_val=10):
    """Cria gráfico de série temporal para uma estação"""
    
    if len(station_data) < 2:
        return None
    
    # Ordenar por data
    station_data = station_data.sort_values('sample_dt')
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Converter datas para datetime
    dates = pd.to_datetime(station_data['sample_dt'])
    
    # Plotar pol_a
    if 'pol_a' in station_data.columns and not station_data['pol_a'].isna().all():
        ax.plot(dates, station_data['pol_a'], 
                color='#e74c3c', marker='o', linewidth=2, label='pol_a', markersize=4)
    
    # Plotar pol_b
    if 'pol_b' in station_data.columns and not station_data['pol_b'].isna().all():
        ax.plot(dates, station_data['pol_b'], 
                color='#3498db', marker='s', linewidth=2, label='pol_b', markersize=4)
    
    # Configurar o gráfico
    ax.set_title(f'Variação Temporal - {station_name}', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'Concentração ({station_data["unit"].iloc[0]})', fontsize=10)
    ax.set_xlabel('Data', fontsize=10)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Formatar datas no eixo x
    plt.xticks(rotation=45, ha='right')
    fig.tight_layout()
    
    # Converter para base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    plt.close(fig)
    
    return base64.b64encode(image_png).decode()

def create_simple_timeseries_chart(station_data, station_name):
    """Cria gráfico de série temporal simplificado (alternativa)"""
    
    if len(station_data) < 2:
        return None
    
    # Ordenar por data
    station_data = station_data.sort_values('sample_dt')
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(5, 3))
    
    # Converter datas
    dates = pd.to_datetime(station_data['sample_dt'])
    
    # Plotar dados disponíveis
    has_pol_a = 'pol_a' in station_data.columns and not station_data['pol_a'].isna().all()
    has_pol_b = 'pol_b' in station_data.columns and not station_data['pol_b'].isna().all()
    
    if has_pol_a:
        ax.plot(dates, station_data['pol_a'], 
                color='#e74c3c', marker='o', linewidth=2, label='pol_a', markersize=3)
    
    if has_pol_b:
        ax.plot(dates, station_data['pol_b'], 
                color='#3498db', marker='s', linewidth=2, label='pol_b', markersize=3)
    
    # Configurações simplificadas
    ax.set_title(f'{station_name}', fontsize=10, fontweight='bold')
    ax.set_ylabel('Concentração', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Formatar datas
    ax.xaxis.set_tick_params(rotation=45, labelsize=7)
    ax.yaxis.set_tick_params(labelsize=7)
    ax.legend(fontsize=7)
    
    fig.tight_layout()
    
    # Converter para base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    plt.close(fig)
    
    return base64.b64encode(image_png).decode()

def create_legend_template():
    """Cria template HTML para a legenda do mapa"""
    
    template = """
    {% macro html(this, kwargs) %}
    <div id='legend' style='
        position: fixed; 
        bottom: 20px; 
        left: 20px; 
        z-index: 1000; 
        background: white; 
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        font-size: 12px;
    '>
        <h4 style='margin: 0 0 10px 0;'>Legenda</h4>
        
        <div style='margin-bottom: 8px;'>
            <div style='display: inline-block; width: 20px; height: 15px; background: #e74c3c; margin-right: 5px;'></div>
            <span>pol_a</span>
        </div>
        
        <div style='margin-bottom: 8px;'>
            <div style='display: inline-block; width: 20px; height: 15px; background: #3498db; margin-right: 5px;'></div>
            <span>pol_b</span>
        </div>
        
        <div style='margin-bottom: 8px;'>
            <strong>Heatmap:</strong> Concentração de pol_a
        </div>
        
        <div style='margin-bottom: 8px;'>
            <strong>Análise Temporal (📈):</strong> Estações com dados históricos
        </div>
        
        <div style='font-size: 10px; color: #666;'>
            Clique nos ícones 📈 para ver gráficos temporais
        </div>
    </div>
    {% endmacro %}
    """
    
    return template

def create_station_analysis(df):
    """Agrupa dados por estação para análise temporal"""
    
    station_analysis = {}
    
    # Agrupar por nome da estação
    for station_name, group in df.groupby('station_name'):
        if len(group) > 1:  # Só analisar estações com múltiplas medições
            station_analysis[station_name] = group.sort_values('sample_dt')
    
    return station_analysis

def create_text_summary(station_data, station_name):
    """Cria resumo textual da análise temporal"""
    
    if len(station_data) < 2:
        return "Dados insuficientes para análise temporal"
    
    station_data = station_data.sort_values('sample_dt')
    
    # Calcular estatísticas básicas
    date_range = f"{station_data['sample_dt'].min().strftime('%d/%m/%Y')} a {station_data['sample_dt'].max().strftime('%d/%m/%Y')}"
    num_measurements = len(station_data)
    
    stats_text = f"<b>{station_name}</b><br>"
    stats_text += f"<b>Período:</b> {date_range}<br>"
    stats_text += f"<b>Medições:</b> {num_measurements}<br><br>"
    
    # Estatísticas para pol_a
    if 'pol_a' in station_data.columns and not station_data['pol_a'].isna().all():
        pol_a_data = station_data['pol_a'].dropna()
        if len(pol_a_data) > 0:
            stats_text += f"<b>pol_a:</b><br>"
            stats_text += f"• Mín: {pol_a_data.min():.2f}<br>"
            stats_text += f"• Máx: {pol_a_data.max():.2f}<br>"
            stats_text += f"• Méd: {pol_a_data.mean():.2f}<br>"
            stats_text += f"• Var: {pol_a_data.var():.2f}<br><br>"
    
    # Estatísticas para pol_b
    if 'pol_b' in station_data.columns and not station_data['pol_b'].isna().all():
        pol_b_data = station_data['pol_b'].dropna()
        if len(pol_b_data) > 0:
            stats_text += f"<b>pol_b:</b><br>"
            stats_text += f"• Mín: {pol_b_data.min():.2f}<br>"
            stats_text += f"• Máx: {pol_b_data.max():.2f}<br>"
            stats_text += f"• Méd: {pol_b_data.mean():.2f}<br>"
            stats_text += f"• Var: {pol_b_data.var():.2f}<br>"
    
    return stats_text

if __name__ == '__main__':
    # Ler e processar dados
    df = read_data(DATA_DIR)
   
    int_cols = ['lat', 'lon', 'pol_a', 'pol_b']
    df = convert_to_numeric(df, int_cols)

    gdf = df_to_geo(df)
    
    # Calcular centro do mapa
    center_lat = gdf.union_all().centroid.y
    center_lon = gdf.union_all().centroid.x
    
    # Encontrar valor máximo para normalização
    max_pol_a = df['pol_a'].max() if not df['pol_a'].isna().all() else 10
    max_pol_b = df['pol_b'].max() if not df['pol_b'].isna().all() else 10
    max_val = max(max_pol_a, max_pol_b, 10)
    
    # Criar mapa base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # === CAMADA DE CONCENTRAÇÃO (MINI-BARRAS) ===
    concentration_layer = folium.FeatureGroup(name='📊 Estações (Mini-barras)', show=True)
    
    for idx, row in df.iterrows():
        if pd.notna(row['lat']) and pd.notna(row['lon']):
            # Criar ícone de barras
            icon = create_bar_icon(row['pol_a'], row['pol_b'], max_val)
            
            # Tooltip com informações
            tooltip_text = f"""
            <b>Estação:</b> {row['station_name']}<br>
            <b>ID:</b> {row['station_id']}<br>
            <b>pol_a:</b> {row['pol_a']:.2f} {row['unit']}<br>
            <b>pol_b:</b> {row['pol_b']:.2f} {row['unit']}<br>
            <b>Data:</b> {row['sample_dt'].strftime('%Y-%m-%d')}
            """
            
            # Adicionar marcador
            folium.Marker(
                location=[row['lat'], row['lon']],
                icon=icon,
                tooltip=folium.Tooltip(tooltip_text, sticky=True),
                popup=folium.Popup(tooltip_text, max_width=300)
            ).add_to(concentration_layer)
    
    concentration_layer.add_to(m)
    
    # === CAMADA DE HEATMAP ===
    heatmap_data = []
    
    for idx, row in df.iterrows():
        if (pd.notna(row['lat']) and pd.notna(row['lon']) and 
            pd.notna(row['pol_a']) and row['pol_a'] > 0):
            heatmap_data.append([row['lat'], row['lon'], row['pol_a']])
    
    if heatmap_data:
        heatmap_layer = fp.HeatMap(
            heatmap_data,
            name='🔥 Heatmap pol_a',
            min_opacity=0.3,
            max_opacity=0.8,
            radius=60,
            blur=15,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        )
        heatmap_layer.add_to(m)
    
    # === CAMADA DE CLUSTERIZAÇÃO ===
    cluster_layer = folium.FeatureGroup(name='📦 Clusters', show=False)
    
    marker_cluster = fp.MarkerCluster(
        options={
            'maxClusterRadius': 80,
            'spiderfyOnMaxZoom': True,
            'showCoverageOnHover': True
        }
    ).add_to(cluster_layer)
    
    # Adicionar marcadores individuais ao cluster
    for idx, row in df.iterrows():
        if pd.notna(row['lat']) and pd.notna(row['lon']):
            tooltip_text = f"""
            <b>Estação:</b> {row['station_name']}<br>
            <b>pol_a:</b> {row['pol_a']:.2f} {row['unit']}<br>
            <b>pol_b:</b> {row['pol_b']:.2f} {row['unit']}
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                tooltip=folium.Tooltip(tooltip_text, sticky=True),
                popup=folium.Popup(tooltip_text, max_width=300)
            ).add_to(marker_cluster)
    
    cluster_layer.add_to(m)
    
    # === CAMADA DE ANÁLISE TEMPORAL ===
    analysis_layer = folium.FeatureGroup(name='📈 Análise Temporal', show=True)
    
    # Agrupar dados por estação para análise
    station_analysis = create_station_analysis(df)
    
    # Para cada estação com múltiplas medições, criar marcador de análise
    for station_name, station_data in station_analysis.items():
        if len(station_data) > 1:
            # Usar a localização mais recente
            latest_data = station_data.iloc[-1]
            lat, lon = latest_data['lat'], latest_data['lon']
            
            # Calcular estatísticas
            num_measurements = len(station_data)
            date_range = f"{station_data['sample_dt'].min().strftime('%d/%m/%Y')} a {station_data['sample_dt'].max().strftime('%d/%m/%Y')}"
            
            # Tentar criar gráfico
            chart_base64 = create_simple_timeseries_chart(station_data, station_name)
            
            # HTML do popup
            if chart_base64:
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; max-width: 1600px;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                        {station_name}
                    </h3>
                    <p><b>📅 Período:</b> {date_range}</p>
                    <p><b>📊 Medições:</b> {num_measurements}</p>
                    <div style="text-align: center; margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                        <img src="data:image/png;base64,{chart_base64}" 
                             style="width: 100%; max-width: 1500px; height: auto; border: 1px solid #ddd; border-radius: 5px;">
                    </div>
                    <div style="margin-top: 10px; padding: 10px; background: #e8f4f8; border-radius: 5px;">
                        <p style="margin: 0; font-size: 12px; color: #2c3e50;">
                            <span style="color: #e74c3c;">● pol_a</span> | 
                            <span style="color: #3498db;">● pol_b</span>
                        </p>
                    </div>
                </div>
                """
            else:
                # Fallback: mostrar apenas estatísticas textuais
                stats_text = create_text_summary(station_data, station_name)
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; max-width: 400px;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px;">{station_name}</h3>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                        {stats_text}
                    </div>
                    <p style="font-size: 11px; color: #666; margin-top: 10px;">
                        Gráfico não disponível - dados insuficientes
                    </p>
                </div>
                """
            
            # Tooltip
            tooltip_text = f"""
            <b>📈 {station_name}</b><br>
            <b>Medições:</b> {num_measurements}<br>
            <b>Período:</b> {date_range}<br>
            <i>Clique para análise temporal</i>
            """
            
            # Ícone especial para estações com análise temporal
            icon_html = f'''
            <div style="
                position: relative;
                width: 35px;
                height: 35px;
                background: rgba(46, 204, 113, 0.9);
                border: 2px solid #27ae60;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 16px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            ">
                📈
            </div>
            '''
            
            icon = folium.DivIcon(html=icon_html, icon_size=(35, 35), icon_anchor=(17, 17))
            
            folium.Marker(
                location=[lat, lon],
                icon=icon,
                tooltip=folium.Tooltip(tooltip_text, sticky=True),
                popup=folium.Popup(popup_html, max_width=1600)
            ).add_to(analysis_layer)
    
    analysis_layer.add_to(m)
    
    # === CONTROLE DE CAMADAS ===
    folium.LayerControl(collapsed=False).add_to(m)
    
    # === LEGENDA PERSONALIZADA ===
    legend_template = create_legend_template()
    macro = MacroElement()
    macro._template = Template(legend_template)
    m.get_root().add_child(macro)
    
    # === INFORMAÇÕES ADICIONAIS ===
    num_stations_temporal = len(station_analysis)
    title_html = f'''
    <div style="
        position: fixed; 
        top: 10px; 
        left: 50px; 
        z-index: 1000; 
        background: white; 
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        font-size: 14px;
        max-width: 350px;
    ">
        <h3 style="margin: 0 0 10px 0;">Mapa de Monitoramento</h3>
        <p style="margin: 5px 0;"><b>Total de estações:</b> {len(df['station_name'].unique())}</p>
        <p style="margin: 5px 0;"><b>Com dados temporais:</b> {num_stations_temporal}</p>
        <p style="margin: 5px 0;"><b>Período total:</b> {df['sample_dt'].min().strftime('%d/%m/%Y')} a {df['sample_dt'].max().strftime('%d/%m/%Y')}</p>
        <p style="margin: 5px 0; font-size: 12px; color: #666;">
            Clique nos ícones <span style="color: #27ae60;">📈</span> para ver gráficos temporais
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Salvar mapa
    m.save(OUT_HTML_MAP)
