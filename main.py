from src.map import *

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
