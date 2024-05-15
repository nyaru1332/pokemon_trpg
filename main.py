import streamlit as st
import pandas as pd
import sqlite3
import requests
from glob import glob 
from PIL import Image
from os.path import join
from sqlalchemy import create_engine
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
#初期値
my_grade = ("グレード1")

st.title('ポケモンtrpgダメージ計算ツール')
# データベースの接続設定
# データベースに接続する（データベースが存在しない場合は新しく作成される）
conn = sqlite3.connect('pokemon_id_data.db')

#ダメージ計算の関数攻撃用<グレード差＋(攻撃/特攻ー防御/特防)＋威力＋能力ランク差>×タイプ相性
def damage_check_attack():
    one_tenth_attack = total_attack/10
    one_tenth_enemy_defense = total_defense/10
    skill_power = skill_power/10
    skill_power = int(Decimal(str(skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_attack = int(Decimal(str(one_tenth_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_enemy_defense = int(Decimal(str(one_tenth_enemy_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = skill_power * types_boost * item_boost
    offensive_power = one_tenth_attack - one_tenth_enemy_defense
    attack_answer = (grade_number - enemy_grade_number + offensive_power + skill_total + ability_rank_boost)*types_boost
    return attack_answer
#ダメージ計算関数急所用
def damage_check_attack_critical():
    skill_power = skill_power/10
    skill_power = int(Decimal(str(skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_attack = total_attack/10
    one_tenth_enemy_defense = enemy_total_defense/10
    one_tenth_attack = int(Decimal(str(one_tenth_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_enemy_defense = int(Decimal(str(one_tenth_enemy_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = skill_power * types_boost * item_boost
    offensive_power = one_tenth_attack - one_tenth_enemy_defense
    attack_answer = (grade_number - enemy_grade_number + offensive_power + skill_total + ability_rank)*types_boost
    return attack_answer

#ダメージ計算関数特攻用
def damaage_check__special_attack():
    skill_power = skill_power/10
    skill_power = int(Decimal(str(skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_special_attack = total_special_attack/10
    one_tenth_enemy_special_defense = enemy_total_defense/10
    one_tenth_special_attack = int(Decimal(str(one_tenth_special_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_special_enemy_defense = int(Decimal(str(one_tenth_enemy_special_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = skill_power * types_boost * item_boost
    special_offensive_power = one_tenth_special_attack - one_tenth_special_enemy_defense
    attack_answer = (grade_number - enemy_grade_number + special_offensive_power + skill_total + ability_rank_boost)*types_boost
    return attack_answer
#ダメージ計算関数特攻急所用
def damaage_check_special_attack_critical():
    skill_power = skill_power/10
    skill_power = int(Decimal(str(skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_special_attack = total_special_attack/10
    one_tenth_enemy_special_defense = enemy_total_defense/10
    one_tenth_special_attack = int(Decimal(str(one_tenth_special_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_special_enemy_defense = int(Decimal(str(one_tenth_enemy_special_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = skill_power * types_boost * item_boost
    special_offensive_power = one_tenth_special_attack - one_tenth_enemy_special_defense
    attack_answer = (grade_number - enemy_grade_number + special_offensive_power + skill_total + ability_rank)*types_boost
    return attack_answer
#グレード一覧
grade = ['グレード1','グレード2','グレード3','グレード4','グレード5','グレード6','グレード7','グレード8','グレード9','グレード10']

# カーソルオブジェクトを作成
c = conn.cursor()

pokemon_name = st.text_input('ポケモンの名前を入力してください:', '')

#情報取得と表示
#データベースでポケモンのIDを検索
if pokemon_name != '':
    c.execute(f"SELECT id FROM id_name WHERE name LIKE '{pokemon_name}%'")
    id_result = c.fetchone()
    st.session_state[id_result] = 0
    if id_result:
        # PokeAPIを用いてポケモンの詳細情報を取得
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{id_result[0]}/')
        if response.status_code == 200:
            pokemon_data = response.json()
            pokemon_image = pokemon_data['sprites']['front_default']
            types = [t['type']['name'] for t in pokemon_data['types']]
            stats = pokemon_data['stats']
            hp = next((item['base_stat'] for item in stats if item['stat']['name'] == 'hp'), None)
            attack = next((item['base_stat'] for item in stats if item['stat']['name'] == 'attack'), None)
            defense = next((item['base_stat'] for item in stats if item['stat']['name'] == 'defense'), None)
            special_attack = next((item['base_stat'] for item in stats if item['stat']['name'] == 'special-attack'), None)
            special_defense = next((item['base_stat'] for item in stats if item['stat']['name'] == 'special-defense'), None)
            speed = next((item['base_stat'] for item in stats if item['stat']['name'] == 'speed'), None)
        #取得したデータを表示
            col1, col2,col3 = st.columns(3)
            with col1:
                st.image(pokemon_image)
            with col2:
                cols = st.columns(len(types))
                for i, type_name in enumerate(types):
                    enemy_img = f'18type_icon\{type_name}.png' 
                    enemy_pokemon_types_image = Image.open(enemy_img)
                    cols[i].write(type_name)
                    cols[i].image(enemy_pokemon_types_image,20,20)
            with col3:
                my_grade = st.selectbox('グレード',grade)
                grade_number = grade.index(my_grade)
            st.markdown('種族値') 
            col1, col2, col3,col4, col5, col6, = st.columns(6)
            with col1:
                st.markdown('HP')
                st.markdown(hp)  # 体力
            with col2:
                st.markdown('こうげき')
                st.markdown(attack)  # 攻撃力
            with col3:
                st.markdown('ぼうぎょ')
                st.markdown(defense)  # 防御
            with col4:
                st.markdown('とくこう')
                st.markdown(special_attack)  # 特攻
            with col5:
                st.markdown('とくぼう')
                st.markdown(special_defense)  # 特防
            with col6:
                st.markdown('すばやさ')
                st.markdown(speed)   # 速さ

            st.markdown('努力値')
            col1, col2, col3,col4, col5, col6 = st.columns([1,1,1,1,1,1])
            skill_point_HP = col1.number_input('HP',value=0)  # 体力入力
            skill_point_attack = col2.number_input('こうげき',value=0)  # こうげき入力
            skill_point_deffense = col3.number_input('ぼうぎょ',value=0)  #ぼうぎょ入力
            skill_point_special_attack = col4.number_input('とくこう',value=0)  # とくこう入力
            skill_point_special_diffence = col5.number_input('とくぼう',value=0)  # とくぼう入力
            skill_point_speed = col6.number_input('すばやさ',value=0)  # すばやさ入力
            total_hp = hp + skill_point_HP
            total_attack = attack + skill_point_attack
            total_defense = defense + skill_point_deffense
            total_special_attack = special_attack + skill_point_special_attack
            total_special_defense = special_defense + skill_point_special_diffence
            total_speed = speed + skill_point_speed

        else:
            st.error('PokeAPIでポケモンの詳細情報が見つかりませんでした。')
    else:
        st.error('指定された名前のポケモンがデータベースに見つかりません。別の名前で試してください。')



pokemon_name = st.text_input('敵ポケモンの名前を入力してください:', '')
if pokemon_name != '':
    c.execute(f"SELECT id FROM id_name WHERE name LIKE '{pokemon_name}%'")
    enemy_id_result = c.fetchone()
    st.session_state[enemy_id_result] = 0
    if enemy_id_result:
        # PokeAPIを用いてポケモンの詳細情報を取得
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{enemy_id_result[0]}/')
        if response.status_code == 200:
            pokemon_data = response.json()
            pokemon_image = pokemon_data['sprites']['front_default']
            types = [t['type']['name'] for t in pokemon_data['types']]
            stats = pokemon_data['stats']
            enemy_hp = next((item['base_stat'] for item in stats if item['stat']['name'] == 'hp'), None)
            enemy_attack = next((item['base_stat'] for item in stats if item['stat']['name'] == 'attack'), None)
            enemy_defense = next((item['base_stat'] for item in stats if item['stat']['name'] == 'defense'), None)
            enemy_special_attack = next((item['base_stat'] for item in stats if item['stat']['name'] == 'special-attack'), None)
            enemy_special_defense = next((item['base_stat'] for item in stats if item['stat']['name'] == 'special-defense'), None)
            enemy_speed = next((item['base_stat'] for item in stats if item['stat']['name'] == 'speed'), None)
        #取得した敵データを表示
            col1, col2,col3 = st.columns(3)
            with col1:
                st.image(pokemon_image)
            with col2:
                cols = st.columns(len(types))
                for i, type_name in enumerate(types):
                    enemy_img = f'18type_icon\{type_name}.png' 
                    enemy_pokemon_types_image = Image.open(enemy_img)
                    cols[i].write(type_name)
                    cols[i].image(enemy_pokemon_types_image,20,20)
            with col3:
                enemy_grade = st.selectbox('グレード ',grade)
                enemy_grade_number = grade.index(enemy_grade)

            col1, col2, col3,col4, col5, col6, = st.columns(6)
            with col1:
                st.markdown('HP')
                st.markdown(enemy_hp)  # 体力
            with col2:
                st.markdown('こうげき')
                st.markdown(enemy_attack)  # 攻撃力
            with col3:
                st.markdown('ぼうぎょ')
                st.markdown(enemy_defense)  # 防御
            with col4:
                st.markdown('とくこう')
                st.markdown(enemy_special_attack)  # 特攻
            with col5:
                st.markdown('とくぼう')
                st.markdown(enemy_special_defense)  # 特防
            with col6:
                st.markdown('すばやさ')
                st.markdown(enemy_speed)   # 速さ 
            st.markdown('努力値')
            col1, col2, col3,col4, col5, col6 = st.columns([1,1,1,1,1,1])
            enemy_skill_point_HP = col1.number_input('HP ',value=0,step=1)  # 体力入力
            enemy_skill_point_attack = col2.number_input('こうげき ',value=0)  # こうげき入力
            enemy_skill_point_defense = col3.number_input('ぼうぎょ ',value=0)  #ぼうぎょ入力
            enemy_skill_point_special_attack = col4.number_input('とくこう ',value=0)  # とくこう入力
            enemy_skill_point_special_diffence = col5.number_input('とくぼう ',value=0)  # とくぼう入力
            enemy_skill_point_speed = col6.number_input('すばやさ ',value=0)  # すばやさ入力
            enemy_total_HP = enemy_hp + enemy_skill_point_HP
            enemy_total_attack = enemy_attack + enemy_skill_point_attack
            enemy_total_defense = enemy_defense + enemy_skill_point_defense
            enemy_total_special_attack = enemy_special_attack + enemy_skill_point_special_attack
            enemy_total_special_defence = enemy_special_defense + enemy_skill_point_defense
        else:
            st.error('ポケモンの詳細情報が見つかりませんでした。')
    else:
        st.error('指定された名前のポケモンがデータベースに見つかりません。別の名前で試してください。')

with st.form(key='damage_boost_form'):
    st.sidebar.write("ダメージ")
    attack_type = st.sidebar.selectbox('攻撃タイプ ',["こうげき","とくこう"])
    skill_power = st.sidebar.number_input("技威力",value=0)
    critical = st.sidebar.checkbox('急所')
    types_boost = st.sidebar.selectbox('タイプ相性倍率',[1,1.5,2])
    ability_rank = st.sidebar.selectbox('自分の能力ランク',range(1,11))
    enemy_ability_rank = st.sidebar.selectbox('相手の能力ランク',range(1,11))
    ability_rank_boost = ability_rank - enemy_ability_rank
    skill_boost = st.sidebar.number_input("特性倍率",value=1.0)
    item_boost = st.sidebar.number_input("持ち物倍率",value=1.0)
    check_button = st.form_submit_button("計算!")
    if check_button == True:
        if attack_type == "こうげき":
            if critical == True:
                total_attack = damage_check_attack_critical()
                st.markdown(total_attack)
            else:
                total_attack = damage_check_attack()
                st.markdown(total_attack)
        elif attack_type == "とくこう":
            if critical ==True:
                st.header(damaage_check_special_attack_critical)
            else:
                st.header(damaage_check__special_attack)
        else:
            st.error('攻撃タイプが選択されてません')

# データベース接続を閉じる
conn.close()