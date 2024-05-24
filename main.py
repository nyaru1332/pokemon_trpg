import streamlit as st
import pandas as pd
import sqlite3
import requests
from glob import glob 
from PIL import Image
from os.path import join
from decimal import Decimal, ROUND_HALF_UP
#初期値
my_grade = ('グレード1')
enemy_grade = ('グレード1')
speed = 0
enemy_speed = 0
skill_point_speed = 0
enemy_skill_point_speed = 0
st.title('ポケモンtrpgダメージ計算ツール')
# データベースの接続設定
# データベースに接続する（データベースが存在しない場合は新しく作成される）
conn = sqlite3.connect('pokemon_id_data.db')

#ダメージ計算の関数攻撃用<グレード差＋(攻撃/特攻ー防御/特防)＋威力＋能力ランク差>×タイプ相性
def damage_check_attack(attack,skill_point_attack,enemy_defense,enemy_skill_point_defense,skill_power,types_boost,item_boost,skill_boost,ability_rank_boost,grade_number,enemy_grade_number):
    one_tenth_attack = attack/10
    one_tenth_attack = int(Decimal(str(one_tenth_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_enemy_defense = enemy_defense/10
    one_tenth_enemy_defense = int(Decimal(str(one_tenth_enemy_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_skill_power = skill_power/10
    one_tenth_skill_power = int(Decimal(str(one_tenth_skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = one_tenth_skill_power * types_boost * item_boost * skill_boost
    offensive_power = one_tenth_attack + skill_point_attack - (one_tenth_enemy_defense + enemy_skill_point_defense)
    attack_answer = int((grade_number - enemy_grade_number + offensive_power + skill_total + ability_rank_boost)*types_boost)
    return attack_answer

#ダメージ計算関数急所用
def damage_check_attack_critical(attack,skill_point_attack,enemy_defense,enemy_skill_point_defense,skill_power,types_boost,item_boost,skill_boost,ability_rank,grade_number,enemy_grade_number):
    one_tenth_attack = attack/10
    one_tenth_attack = int(Decimal(str(one_tenth_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_enemy_defense = enemy_defense/10
    one_tenth_enemy_defense = int(Decimal(str(one_tenth_enemy_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_skill_power = skill_power/10
    one_tenth_skill_power = int(Decimal(str(one_tenth_skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = one_tenth_skill_power * types_boost * item_boost * skill_boost
    offensive_power = one_tenth_attack + skill_point_attack - (one_tenth_enemy_defense + enemy_skill_point_defense)
    attack_answer = int((grade_number - enemy_grade_number + offensive_power + skill_total + ability_rank)*types_boost)
    return attack_answer

#ダメージ計算関数特攻用
def damage_check__special_attack(skill_power,special_attack,skill_point_special_attack,enemy_special_defense,enemy_skill_point_special_defense,types_boost,item_boost,skill_boost,ability_rank_boost,grade_number,enemy_grade_number):
    one_tenth_skill_power = skill_power/10
    one_tenth_skill_power = int(Decimal(str(one_tenth_skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_special_attack = special_attack/10
    one_tenth_special_attack = int(Decimal(str(one_tenth_special_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_enemy_special_defense = enemy_special_defense/10
    one_tenth_enemy_special_defense = int(Decimal(str(one_tenth_enemy_special_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = one_tenth_skill_power * types_boost * item_boost * skill_boost
    special_offensive_power = one_tenth_special_attack + skill_point_special_attack - (one_tenth_enemy_special_defense + enemy_skill_point_special_defense)
    special_attack_answer = int((grade_number - enemy_grade_number + special_offensive_power + skill_total + ability_rank_boost)*types_boost)
    return special_attack_answer

#ダメージ計算関数特攻急所用
def damage_check__special_attack_critical(skill_power,special_attack,skill_point_special_attack,enemy_special_defense,enemy_skill_point_special_defense,types_boost,item_boost,grade_number,enemy_grade_number,skill_boost,ability_rank):
    one_tenth_skill_power = skill_power/10
    one_tenth_skill_power = int(Decimal(str(one_tenth_skill_power)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_special_attack = special_attack/10
    one_tenth_special_attack = int(Decimal(str(one_tenth_special_attack)).quantize(Decimal('0'), ROUND_HALF_UP))
    one_tenth_enemy_special_defense = enemy_special_defense/10
    one_tenth_enemy_special_defense = int(Decimal(str(one_tenth_enemy_special_defense)).quantize(Decimal('0'), ROUND_HALF_UP))
    skill_total = one_tenth_skill_power * types_boost * item_boost * skill_boost
    special_offensive_power = one_tenth_special_attack + skill_point_special_attack - (one_tenth_enemy_special_defense + enemy_skill_point_special_defense)
    special_attack_answer = int((grade_number - enemy_grade_number + special_offensive_power + skill_total + ability_rank)*types_boost)
    return special_attack_answer

#グレード一覧
grade = ['グレード1','グレード2','グレード3','グレード4','グレード5','グレード6','グレード7','グレード8','グレード9','グレード10']
#ボール一覧
type_of_ball_list = ['モンスターボール','スーパーボール','ハイパーボール']
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
                    pokemon_img = f'18type_icon/{type_name}.png' 
                    pokemon_types_image = Image.open(pokemon_img)
                    cols[i].write(type_name)
                    cols[i].image(pokemon_types_image,20,20)
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
        #努力値を入力
            st.markdown('努力値')
            col1, col2, col3,col4, col5, col6 = st.columns([1,1,1,1,1,1])
            skill_point_HP = col1.number_input('HP',value=0)  # 体力入力
            skill_point_attack = col2.number_input('こうげき',value=0)  # こうげき入力
            skill_point_deffense = col3.number_input('ぼうぎょ',value=0)  #ぼうぎょ入力
            skill_point_special_attack = col4.number_input('とくこう',value=0)  # とくこう入力
            skill_point_special_diffence = col5.number_input('とくぼう',value=0)  # とくぼう入力
            skill_point_speed = col6.number_input('すばやさ',value=0)  # すばやさ入力
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
                    enemy_img = f'18type_icon/{type_name}.png' 
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
        #敵の努力値を入力
            col1, col2, col3,col4, col5, col6 = st.columns([1,1,1,1,1,1])
            enemy_skill_point_HP = col1.number_input('HP ',value=0,step=1)  # 体力入力
            enemy_skill_point_attack = col2.number_input('こうげき ',value=0)  # こうげき入力
            enemy_skill_point_defense = col3.number_input('ぼうぎょ ',value=0)  #ぼうぎょ入力
            enemy_skill_point_special_attack = col4.number_input('とくこう ',value=0)  # とくこう入力
            enemy_skill_point_special_defense = col5.number_input('とくぼう ',value=0)  # とくぼう入力
            enemy_skill_point_speed = col6.number_input('すばやさ ',value=0)  # すばやさ入力
            enemy_total_HP = enemy_hp + enemy_skill_point_HP
            enemy_total_attack = enemy_attack + enemy_skill_point_attack
            enemy_total_defense = enemy_defense + enemy_skill_point_defense
            enemy_total_special_attack = enemy_special_attack + enemy_skill_point_special_attack
            enemy_total_special_defense = enemy_special_defense + enemy_skill_point_defense
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
    check_button = st.form_submit_button("計算!")#イベントの発火に使用してます。消したら壊れます

    #計算!ボタンが押されたらダメージ計算の結果を呼び出す
    if check_button == True:
        if attack_type == "こうげき":
            if critical == True:
                result_attack = damage_check_attack_critical(attack,skill_point_attack,enemy_defense,enemy_skill_point_defense,skill_power,types_boost,item_boost,skill_boost,ability_rank,grade_number,enemy_grade_number)
                st.write(str(result_attack),'d6')
            else:
                result_attack = damage_check_attack(attack,skill_point_attack,enemy_defense,enemy_skill_point_defense,skill_power,types_boost,item_boost,grade_number,skill_boost,ability_rank_boost,enemy_grade_number)
                st.write(str(result_attack),'d6')
        elif attack_type == "とくこう":
            if critical ==True:
                result_special_attack = damage_check__special_attack_critical(skill_power,special_attack,skill_point_special_attack,enemy_special_defense,enemy_skill_point_special_defense,types_boost,item_boost,skill_boost,ability_rank_boost,grade_number,enemy_grade_number)
                st.write(str(result_special_attack),'d6')
            else:
                result_special_attack = damage_check__special_attack(skill_power,special_attack,skill_point_special_attack,enemy_special_defense,enemy_skill_point_special_defense,types_boost,item_boost,skill_boost,ability_rank_boost,grade_number,enemy_grade_number)
                st.write(str(result_special_attack),'d6')
        else:
            st.error('攻撃タイプが選択されてません')
with st.form(key='capture_decision_form'):
    #捕獲判定:ボールの捕獲係数×トレーナーランク＋与えたダメージ割合＋（状態異常なら１０）＋（トレーナーランク－相手のグレード）×５
    type_of_ball = st.sidebar.selectbox('ボールタイプ ',type_of_ball_list)
    status_condition = st.sidebar.checkbox('状態異常')
    Current_HP = int(st.sidebar.number_input("現在のHP",value=0))
    type_of_ball_number = type_of_ball_list.index(type_of_ball)
    capture_decision_button = st.form_submit_button("計算!")
    if capture_decision_button == True:
        if status_condition == True:
            capture_decision = int(type_of_ball_number + 100 -Current_HP/(enemy_total_HP + enemy_grade_number * 15)*100 + 10 + (grade_number - enemy_grade_number) * 5)
        else:
            capture_decision = int(type_of_ball_number +100 - Current_HP/(enemy_total_HP + enemy_grade_number * 15)*100 + (grade_number - enemy_grade_number) * 5)
        st.write(str(capture_decision))
#逃走成功率＝(トレーナーの足の速さの半分 or ポケモンの素早さ-相手の素早さ+5)×10
one_tenth_speed = speed/10
one_tenth_speed = int(Decimal(str(one_tenth_speed)).quantize(Decimal('0'), ROUND_HALF_UP))
one_tenth_enemy_speed = enemy_speed/10
one_tenth_enemy_speed = int(Decimal(str(one_tenth_enemy_speed)).quantize(Decimal('0'), ROUND_HALF_UP))
escape_success_rate = (one_tenth_speed + skill_point_speed - (one_tenth_enemy_speed + enemy_skill_point_speed)+5) * 10
st.write('逃走成功率')
st.write(str(escape_success_rate))
# データベース接続を閉じる
conn.close()