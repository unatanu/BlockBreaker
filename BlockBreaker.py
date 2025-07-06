import random
import sys
from pygame.locals import *
from pygame import mixer
import pygame
import math
import time
import serial

# pygame初期化
pygame.init()


# 操作方法
# 0: 矢印キー, 1: 可変抵抗
control_mode = 0
control_name = ["Key", "Resist"]
if control_mode < 0 or control_mode > len(control_name) - 1:
    print("control mode must be 1 or 2")
    exit()


# シリアル通信の設定
if control_name[control_mode] == "Resist":
    ser = serial.Serial('COM7', 9600)
    not_used = ser.readline()
    Resist_MAX = 1023  # 可変抵抗の最大値
    Resist_MIN = 0  # 可変抵抗の最小値


# 画面サイズの設定
screen_Width = 600     #  幅
screen_Height = 600    #  高さ（上から下向きに伸びる）
blank = 10
game_screen_W = screen_Width * 2 // 3
game_screen_H = screen_Height - 4*blank
info_screen_W = screen_Width // 4
info_screen_H = screen_Height // 3

# 画面の作成
screen = pygame.display.set_mode((screen_Width, screen_Height))
line_width = 4  # ゲーム画面の枠線の太さ
game_x = 2*blank  # ゲーム画面の左上x座標
game_y = blank  # ゲーム画面の左上y座標
info_x = 3*blank + game_screen_W  # 情報ボックスの左上x座標
info_y = blank  # 情報ボックスの左上y座標


# ボールの設定
RADIUS = 10             # 半径
x0 = game_screen_W/2    # 初期x座標
y0 = game_screen_H*2/3  # 初期y座標
Ball_Speed = 1.0        # 移動速度
Ball_num = 2            # ボールの個数
Ball_delay = 1.0    # ボールが複数個でゲームを開始したとき、動き始めのタイミングをずらす時間
Ball_score = 100        # ボールが最後まで残ったときのボーナス得点


# ブロックの設定
Block_num_B = 5  # 横に並べるブロックの数
Block_num_V = 10  # 縦
Block_pos_lim = game_screen_H // 2  # ブロックを配置する高さの制限
Block_Width = (game_screen_W - line_width) // Block_num_B  # 幅
Block_Height = Block_pos_lim // Block_num_V  # 高さ


# バーの設定
Bar_Width = 150  # バーの幅
Bar_Height = 20  # バーの高さ
Bar_posy = game_screen_H - 10  # バーの底のy座標


# 色の定義
COLOR_SET_1 = ["red","blue","forestgreen","gold"]
COLOR_SET_2 = ["darkorange","deepskyblue","lime","yellow"]
COLOR_SET_3 = ["blueviolet","dodgerblue","gold","orange"]
COLOR_SET_4 = ["limegreen","magenta","slateblue","cyan"]
COLORS = random.choice([COLOR_SET_1, COLOR_SET_2, COLOR_SET_3, COLOR_SET_4])  # カラーセットの中からランダムに一つのセットを選ぶ


# fps = 120
# clock = pygame.time.Clock()



# 効果音
class Sound:
    def __init__(self):
        # 効果音の設定
        mixer.init()
        name = ["select", "decide", "break"]
        # path_SE = "C:/Users/hikaru/VSC/LAB/BrockBreaker/Sound_Effect/"
        path_SE = "./Sound_Effect/"
        self.Sound_select = mixer.Sound(path_SE + name[0] + ".mp3")
        self.Sound_decide = mixer.Sound(path_SE + name[1] + ".mp3")
        self.Sound_break = mixer.Sound(path_SE + name[2] + ".mp3")

    def select(self):
        self.Sound_select.play()
        time.sleep(0.1)

    def decide(self):
        self.Sound_decide.play()
        time.sleep(0.2)

    def breaks(self):
        self.Sound_break.play()
        time.sleep(0.01)
sound = Sound()



# バー
class Bar:
    def __init__(self, screen, init_x):
        self.screen = screen
        self.x = init_x
        self.y = Bar_posy
        self.color_center = "crimson"
        self.color = "silver"

        # 指定した位置に矩形を表示
        pygame.draw.rect(self.screen, self.color, (self.x - Bar_Width/2, self.y - Bar_Height, Bar_Width, Bar_Height))
        pygame.draw.rect(self.screen, self.color_center, (self.x - Bar_Width/6, self.y - Bar_Height, Bar_Width/3, Bar_Height))  # 真ん中は色を変える

    def move(self, pre_x, new_x):
        self.pre_x = pre_x
        self.new_x = new_x
        pygame.draw.rect(self.screen, "white", (self.pre_x - Bar_Width/2, self.y - Bar_Height, Bar_Width, Bar_Height))  # 移動前のバーを削除
        pygame.draw.rect(self.screen, self.color, (self.new_x - Bar_Width/2, self.y - Bar_Height, Bar_Width, Bar_Height))  # 移動後のバーを表示
        pygame.draw.rect(self.screen, self.color_center, (self.new_x - Bar_Width/6, self.y - Bar_Height, Bar_Width/3, Bar_Height))

    def input_key(self, move_right, move_left, BAR_x):
        # 矢印キーが押されている間バーを動かし続けるための処理
        for event in pygame.event.get():
            if event.type == QUIT:  # ×が押されたらゲームを終了
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:  # キーが押されたとき
                if event.key == K_ESCAPE:  # escキーでゲームを終了
                    pygame.quit()
                    sys.exit()

                if event.key == K_LEFT:
                    move_left = True
                elif event.key == K_RIGHT:
                    move_right = True

            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    move_left = False
                elif event.key == K_RIGHT:
                    move_right = False

        pre_x = BAR_x
        if move_left:
            if BAR_x - Bar_Width/2 <= game_x + line_width: # バーが画面外にはみ出たとき
                BAR_x -= 0
                
            else:
                BAR_x -= 3
        elif move_right:
            if BAR_x + Bar_Width/2 >= game_x + game_screen_W - line_width:  # バーが画面外にはみ出たとき
                BAR_x += 0
            else:
                BAR_x += 3

        return move_right, move_left, BAR_x, pre_x
    
    """
    def input_resist(self, BAR_x):
        pre_x = BAR_x  # 動かす前のバーのx座標を保存
        data = ser.readline().decode().strip()  # データを文字列として受信し、空白文字を除去する
        try:
            value = int(data)
            BAR_x = game_x + Bar_Width/2 + (game_screen_W - line_width - Bar_Width) * round((Resist_MAX - value) / (Resist_MAX - Resist_MIN), 2)
            message.info(SCORE, val_decoded)
            return BAR_x, pre_x
        except ValueError:
            continue
    """


        # val_arduino = ser.readline()  # シリアル通信でarduinoから値を読み込む
        # val_decoded = int(repr(val_arduino.decode())[1:-5])  # 読み込んだ値から数値のみ取り出す
        # 抵抗の値をバーの座標に変換
        

        



# ボール
class Ball:
    def __init__(self, screen, x, y):
        # 関数内の変数と外部の変数の紐づけ
        self.screen = screen
        self.x = x
        self.y = y

        self.degree = math.radians(random.randint(45,135))  # ボールの射出角度
        self.vel_x = Ball_Speed * math.cos(self.degree)
        self.vel_y = Ball_Speed * math.sin(self.degree)
        self.r = RADIUS
        self.accel = 1.0  # ボールの加速度（下の方でこの値をいじっている）

        # ボールとその枠線の描画
        pygame.draw.circle(screen, "yellow", (self.x, self.y), self.r)
        pygame.draw.circle(screen, "black", (self.x, self.y), self.r, width=1)

    # ボールの位置を更新
    def move(self):
        self.x += self.vel_x * self.accel
        self.y += self.vel_y * self.accel
        # 移動前のボールを削除
        pygame.draw.circle(screen, "white", (self.x - self.vel_x * self.accel, self.y - self.vel_y * self.accel), self.r)
        # 移動後のボールを描画
        pygame.draw.circle(screen, "yellow", (self.x, self.y), self.r)
        pygame.draw.circle(screen, "black", (self.x, self.y), self.r, width=1)

    # ボールの衝突判定
    def check_collision(self):

        # ボールが画面の側面に当たったとき
        if self.x - self.r <= game_x + line_width or self.x + self.r >= game_x + game_screen_W - line_width:
            self.vel_x *= -1
        # ボールが画面の上部に当たったとき
        if self.y - self.r <= game_y + line_width:
            self.vel_y *= -1
        
        # バーの衝突判定
        if (Bar_posy - Bar_Height <= self.y + self.r <= Bar_posy) and self.vel_y >= 0:  # バーの高さにきたとき　かつ　ボールが下向きに動いているとき

            if BAR_x - Bar_Width/6 <= self.x <= BAR_x + Bar_Width/6:  # 真ん中らへんに当たったとき
                self.vel_y *= -1

            else:
                self.degree = math.atan2(self.vel_y, self.vel_x)  # ぶつかる瞬間のボールの角度を計算（右向きから時計回り、ラジアン）
                theta = math.radians(30)  # バーの端の方に当たったときに変化させる角度

                if BAR_x - Bar_Width/2 <= self.x <= BAR_x - Bar_Width/6:  # 左側に当たったとき
                    if self.vel_x >= 0:
                        self.degree += -2*self.degree - theta  # 垂直寄りに変化
                    else:
                        self.degree += 2*(math.pi - self.degree) - theta  # 角度を浅く変化
            
                elif BAR_x + Bar_Width/6 <= self.x <= BAR_x + Bar_Width/2:  # 右側に当たったとき
                    if self.vel_x >= 0:
                        self.degree += -2*self.degree + theta  # 角度を浅く変化
                    else:
                        self.degree += 2*(math.pi - self.degree) + theta  # 垂直寄りに変化
            
                self.vel_x = Ball_Speed * math.cos(self.degree) * self.accel
                self.vel_y = Ball_Speed * math.sin(self.degree) * self.accel


      
# ブロック
class Block:

    def __init__(self, screen, x, y, color):
        # 関数内の変数と外部の変数の紐づけ
        self.screen = screen
        self.x1 = x
        self.y1 = y
        self.x2 = x + Block_Width
        self.y2 = y + Block_Height
        self.color = color

        # 指定した位置に矩形を表示
        pygame.draw.rect(self.screen,self.color,(self.x1, self.y1, Block_Width, Block_Height))

    # ボールとブロックの衝突判定
    def check_collision_x(self, ball_x, ball_y):  # x方向判定
        self.ball_x = ball_x
        self.ball_y = ball_y

        if ((self.x1 <= self.ball_x - RADIUS <= self.x2) and (self.y1 <= self.ball_y <= self.y2)) or ((self.x1 <= self.ball_x + RADIUS <= self.x2) and (self.y1 <= self.ball_y <= self.y2)):
            pygame.draw.rect(self.screen,"white",(self.x1, self.y1, Block_Width, Block_Height))
            return True
        return False
    def check_collision_y(self, ball_x, ball_y):  # y方向判定
        self.ball_x = ball_x
        self.ball_y = ball_y

        if ((self.x1 <= self.ball_x <= self.x2) and (self.y1 <= self.ball_y - RADIUS <= self.y2)) or ((self.x1 <= self.ball_x <= self.x2) and (self.y1 <= self.ball_y + RADIUS <= self.y2)):
            pygame.draw.rect(self.screen,"white",(self.x1, self.y1, Block_Width, Block_Height))
            return True
        return False
    


# メッセージ
class Message:
    def __init__(self):
        self.font_title = pygame.font.SysFont(None, 70)
        self.font_message = pygame.font.SysFont(None, 45)
        self.font_common = pygame.font.SysFont(None, 35)


    # タイトル画面に表示する文字
    def title(self):
        self.text_title = self.font_title.render("BROCK BREAKER", True, "black")
        self.text_start = self.font_message.render("PRESS SPACE TO START", True, "black")
        self.rect_title = self.text_title.get_rect(center=(screen_Width // 2, screen_Height // 3))
        self.rect_start = self.text_start.get_rect(center=(screen_Width // 2, screen_Height // 2))
        screen.blit(self.text_title, self.rect_title)
        screen.blit(self.text_start, self.rect_start)

        self.words = ["", "OPTION", "QUIT"]
        for i in range(len(self.words)):
            self.text = self.font_common.render(self.words[i], True, "black")
            self.rect = self.text.get_rect(center=(screen_Width // 2, screen_Height // 2 + 40*(i+1)))
            screen.blit(self.text, self.rect)


    # タイトル画面の選択肢部分に表示する文字
    def select(self):
        pygame.draw.rect(screen,"white",(0, game_y + game_screen_H // 2 + 40, screen_Width, game_screen_H // 2))  # 選択肢部分のみ白く塗りつぶし
        for i in range(len(self.words)):
            if i == select_num:  # 選ばれている選択肢の文字を大きくする
                self.text_selected = self.font_message.render(self.words[i], True, "black")
                self.rect_selected = self.text_selected.get_rect(center=(screen_Width // 2, screen_Height // 2 + 40*(i+1)))
                screen.blit(self.text_selected, self.rect_selected)
            else:
                self.text_other = self.font_common.render(self.words[i], True, "black")
                self.rect_other = self.text_other.get_rect(center=(screen_Width // 2, screen_Height // 2 + 40*(i+1)))
                screen.blit(self.text_other, self.rect_other)


    # タイトル画面のオプションを開いたときに表示する文字
    def option(self, Ball_num, Ball_Speed):
        pygame.draw.rect(screen,"white",(0, game_y + game_screen_H // 2 + 40, screen_Width, game_screen_H // 2))
        self.options = ["", "NUM BALL", "BALL SPEED", "TITLE"]
        for i in range(len(self.options)):
            if i == select_num:  # 選ばれている選択肢の文字を大きくする
                self.text_selected = self.font_message.render(self.options[i], True, "black")
                self.rect_selected = self.text_selected.get_rect(center=(screen_Width // 2, screen_Height // 2 + 40*(i+1)))
                screen.blit(self.text_selected, self.rect_selected)
            else:
                self.text_other = self.font_common.render(self.options[i], True, "black")
                self.rect_other = self.text_other.get_rect(center=(screen_Width // 2, screen_Height // 2 + 40*(i+1)))
                screen.blit(self.text_other, self.rect_other)


        # 数字の横につける矢印の表示
        self.font_path = pygame.font.match_font('Arial')
        self.font = pygame.font.Font(self.font_path, 35)
        self.num = [Ball_num, Ball_Speed]
        self.arrow = ["<", ">"]
        for j in range(len(self.options) - 2):
            # 矢印の表示
            for k in range(len(self.arrow)):
                self.text_arrow = self.font.render(self.arrow[k], True, "black")
                self.rect_arrow = self.text_arrow.get_rect(center=(screen_Width // 2 + 100 + 60*k, screen_Height // 2 + 40*(j+2)))
                screen.blit(self.text_arrow, self.rect_arrow)
            # 数字の表示
            self.text_num = self.font_common.render(f"{self.num[j]}", True, "black")
            self.rect_num = self.text_num.get_rect(center=(screen_Width // 2 + 100 + 30, screen_Height // 2 + 40*(j+2)))
            screen.blit(self.text_num, self.rect_num)


    # 画面右上の情報を表示
    def info(self, SCORE, resist):
        pygame.draw.rect(screen, "white", (info_x + line_width, info_y + line_width, info_screen_W - 2*line_width, info_screen_H - 2*line_width))
        self.font_info = pygame.font.SysFont(None, 30)
        self.text_score = self.font_info.render(f"SCORE: {SCORE}", True, "black")
        self.rect_score = self.text_score.get_rect(center=(info_screen_W // 2 + info_x, info_screen_H // 2 + info_y -20))
        screen.blit(self.text_score, self.rect_score)

        self.text_resist = self.font_info.render(f"RESIST: {resist}", True, "black")
        self.rect_resist = self.text_resist.get_rect(center=(info_screen_W // 2 + info_x, info_screen_H // 2 + info_y + 20))
        screen.blit(self.text_resist, self.rect_resist)


    # ゲームオーバーになったときの文字
    def gameover(self):
        transparent_surface = pygame.Surface((300, 100), pygame.SRCALPHA)  # メッセージボックス（幅、高さ）
        transparent_surface.fill((255, 50, 50, 200))  # メッセージボックスの色と透明度

        self.text_gameover = self.font_message.render("GAME OVER!", True, "black")
        self.text_score = self.font_message.render(f"SCORE: {SCORE}", True, "black")
        self.text_back = self.font_common.render("ENTER: BACK TO TITLE", True, "black")
        
        self.rect_message = self.text_gameover.get_rect(center=(transparent_surface.get_width() // 2, transparent_surface.get_height() // 2))
        self.rect1 = self.text_start.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y + 60))
        self.rect2 = self.text_score.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y + 120))
        self.rect3 = self.text_back.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y + 160))

        transparent_surface.blit(self.text_gameover, self.rect_message)
        screen.blit(transparent_surface, (game_screen_W // 2 + game_x - transparent_surface.get_width() // 2, game_screen_H // 2 + game_y - transparent_surface.get_height() // 2 - 100))
        screen.blit(self.text_start, self.rect1)
        screen.blit(self.text_score, self.rect2)
        screen.blit(self.text_back, self.rect3)


    # クリアしたときの文字
    def clear(self):
        self.text_clear = self.font_message.render("CLEAR!", True, "black")
        self.text_score = self.font_message.render(f"SCORE: {SCORE}", True, "black")
        self.text_back = self.font_common.render("ENTER: BACK TO TITLE", True, "black")

        self.rect_message = self.text_clear.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y - 100 ))
        self.rect1 = self.text_score.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y + 60))
        self.rect2 = self.text_start.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y + 120))
        self.rect3 = self.text_back.get_rect(center=(game_screen_W // 2 + game_x, game_screen_H // 2 + game_y + 160))

        screen.blit(self.text_clear, self.rect_message)
        screen.blit(self.text_score, self.rect1)
        screen.blit(self.text_start, self.rect2)
        screen.blit(self.text_back, self.rect3)




class Block
# フラグの初期設定
running = True          # プログラムを進行させるかを示す
game_started = False    # ゲームが開始されたかどうかを示す
is_gameover = False     # ゲームオーバーになったかを示す
is_clear = False        # クリアしたかを示す
is_title = True         # タイトル画面かを示す

select_num = 0  # 何番目の選択肢を選んでいるか
option_window = 0  # 何番目の選択肢階層にいるか
message = Message()


while running:

    # ゲームが開始されていない場合
    while not game_started:

        # メッセージの表示
        if not is_gameover and not is_clear:  # タイトル画面
            screen.fill("white")
            message.title()
        else:
            if is_gameover and not is_clear:  # ゲームオーバーしたとき
                message.gameover()
            else:  # クリアしたとき
                message.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:  # escキーでゲームを終了
                        pygame.quit()
                        sys.exit()

                    if event.key == K_RETURN:  # enterが押されたとき
                        screen.fill("white")
                        message.title()
                        sound.decide()
                        is_title = True
                        select_num = 0

                    elif event.key == K_SPACE:
                        sound.decide()
                        game_started = True

        pygame.display.update()

        # ------------------------------------------------------------------------------------------------------------------
        # タイトル画面での処理
        while is_title:
            # ゲーム開始の処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:  # escキーでゲームを終了
                        pygame.quit()
                        sys.exit()

                    # タイトル画面でオプションを選んでいるとき
                    if option_window == 0:
                        # 矢印キーの上下が押されたとき、対応する選択肢の文字を大きくする
                        if event.key == K_DOWN:
                            select_num += 1
                            sound.select()
                        elif event.key == K_UP:
                            select_num -= 1
                            sound.select()
                        select_num = select_num % len(message.words)  # 値が大きすぎたりマイナスになるのを回避
                        message.select()
                        pygame.display.update()

                        # 選択肢が選ばれたとき
                        if event.key == K_RETURN:  # enterが押されたとき
                            if message.words[select_num] == "OPTION":
                                select_num = 0
                                option_window = 1
                                sound.decide()
                                message.option(Ball_num, Ball_Speed)
                                pygame.display.update()
                            elif message.words[select_num] == "QUIT":
                                sound.decide()
                                pygame.quit()
                                sys.exit()
                    
                    # オプションの中身を表示している場合
                    if option_window == 1:
                        # 矢印キーを押したとき、対応する文字を大きくするための変数管理
                        if event.key == K_DOWN:
                            select_num += 1
                            sound.select()
                        elif event.key == K_UP:
                            select_num -= 1
                            sound.select()
                        select_num = select_num % len(message.options) 

                        # 該当するオプションの数値を増減させる
                        if event.key == K_RIGHT:
                            if message.options[select_num] == "NUM BALL":
                                Ball_num += 1
                                sound.select()
                            elif message.options[select_num] == "BALL SPEED":
                                Ball_Speed += .1
                                sound.select()
                        elif event.key == K_LEFT:
                            if message.options[select_num] == "NUM BALL":
                                Ball_num -= 1
                                sound.select()
                            elif message.options[select_num] == "BALL SPEED":
                                Ball_Speed -= .1
                                sound.select()
                        Ball_num = Ball_num % 11  # 0~10の範囲内のみ
                        Ball_Speed = Ball_Speed % 5.1  # 0.0~5.0の範囲内のみ
                        Ball_Speed = round(Ball_Speed, 2)  # 少数第2位を四捨五入

                        message.option(Ball_num, Ball_Speed)
                        pygame.display.update()

                        # 選択肢が選ばれたとき
                        if event.key == K_RETURN:  # enterが押されたとき
                            if message.options[select_num] == "TITLE":
                                select_num = 0
                                option_window = 0
                                sound.decide()
                                message.select()
                                pygame.display.update()

                    # スペースキーが押されたらゲームを開始する
                    if event.key == pygame.K_SPACE:
                        sound.decide()
                        game_started = True
                        is_title = False


    # ゲームが開始されている場合
    set_up = False
    is_gameover = False
    is_clear = False
    while game_started:

        # ------------------------------------------------------------------------------------------------------------------
        # ゲーム開始時の初回設定
        if not set_up:
            screen.fill("white")
            # ゲーム画面、インフォメーション画面の作成
            pygame.draw.rect(screen, "black", Rect(game_x, game_y, game_screen_W, game_screen_H),4)
            pygame.draw.rect(screen, "black", Rect(info_x, info_y, info_screen_W, info_screen_H), line_width)

            # 各ブロック、各ボールの生成
            blocks = [Block(screen, ix*Block_Width + game_x + line_width, iy*Block_Height + game_y, random.choice(COLORS)) for ix in range(game_screen_W//Block_Width) for iy in range(Block_pos_lim//Block_Height)]
            balls = [Ball(screen,x0,y0) for i in range(Ball_num)]
            # バーの位置の初期化
            BAR_x = game_screen_W/2  # バーの中心x座標
            bar = Bar(screen, BAR_x)
            move_left = False
            move_right = False
            val_decoded = 0

            SCORE = 0  # スコア
            message.info(SCORE, 0)  # スコアの表示
            pre_time = time.time()  # 現在の時刻を取得
            limit_num = 0  # 開始直後に動けるボールの数（下の方で増える処理がある）

            set_up = True  # 準備完了
            pygame.display.update()
            pygame.time.delay(500)

        

        # メインループ
        if not is_gameover or not is_clear:
            # clock.tick(fps)
            # ------------------------------------------------------ bar ------------------------------------------------------------
            if control_name[control_mode] == "Key":
                move_right, move_left, BAR_x, pre_x = bar.input_key(move_right, move_left, BAR_x)
            elif control_name[control_mode] == "Resist":
                pre_x = BAR_x  # 動かす前のバーのx座標を保存
                data = ser.readline().decode().strip()  # データを文字列として受信し、空白文字を除去する
                try:
                    value = int(data)
                    BAR_x = game_x + Bar_Width/2 + (game_screen_W - line_width - Bar_Width) * round((Resist_MAX - value) / (Resist_MAX - Resist_MIN), 2)
                    message.info(SCORE, val_decoded)
                except ValueError:
                    continue

            bar.move(pre_x, BAR_x)

            # ------------------------------------------------------ ball ------------------------------------------------------------
            for index, ball in enumerate(balls):  # 動かすボールとそのインデックスを取得
                ball.move()
                ball.check_collision()
                # ブロックとの接触判定
                for block in blocks:
                    if block.check_collision_x(ball.x, ball.y):
                        blocks.remove(block)
                        sound.breaks()
                        SCORE += 10
                        message.info(SCORE, val_decoded)
                        ball.vel_x *= -1
                    elif block.check_collision_y(ball.x, ball.y):
                        blocks.remove(block)
                        sound.breaks()
                        SCORE += 10
                        message.info(SCORE, val_decoded)
                        ball.vel_y *= -1


                # 残りのブロック数が少なくなるほどボールスピードが速くなる
                ball.accel = round(2.0 - len(blocks) / (Block_num_B * Block_num_V), 3)


                # ボールが画面底部を抜けたとき
                if ball.y - ball.r >= game_screen_H:
                    balls.remove(ball)
                    pygame.draw.circle(screen, "white", (ball.x, ball.y), ball.r)
                    if len(balls) == 0:  # ボールが全てなくなったとき
                        is_gameover = True
                        game_started = False


                # ゲーム開始時のボール待機の処理
                if limit_num < Ball_num - 1:
                    now_time = time.time()  # 現在の時刻を取得
                    index += 1  # 現在動いているボールの番号

                    # ここでブレイクすることで、後続のボールが動く前に次のループに入る
                    if index > limit_num:
                        if now_time - pre_time < Ball_delay:  # 経過時間が待機時間より短いとき
                            break
                        else:  # 充分待機したとき
                            pre_time = now_time
                            limit_num += 1  # 何番のボールまで動けるかを数える
                            break

            # ------------------------------------------------------ clear ------------------------------------------------------------
            # 残りのブロック数が0になったとき（クリアしたとき）
            if len(blocks) == 0:
                SCORE += len(balls) * Ball_score  # 残りのボールの数得点が加算
                is_clear = True
                game_started = False
            
            
            # 画面を更新する
            pygame.draw.rect(screen, "black", Rect(2*blank, blank, game_screen_W, game_screen_H),4)  # なぜか欠けるからゲーム画面の枠線を書き直し
            pygame.display.update()
            pygame.time.delay(1)
        

# Pygameの終了
pygame.quit()
sys.exit()














# # フラグの初期設定
# running = True          # プログラムを進行させるかを示す
# game_started = False    # ゲームが開始されたかどうかを示す
# is_gameover = False     # ゲームオーバーになったかを示す
# is_clear = False        # クリアしたかを示す
# is_title = True         # タイトル画面かを示す

# select_num = 0  # 何番目の選択肢を選んでいるか
# option_window = 0  # 何番目の選択肢階層にいるか
# message = Message()


# while running:

#     # ゲームが開始されていない場合
#     while not game_started:

#         # メッセージの表示
#         if not is_gameover and not is_clear:  # タイトル画面
#             screen.fill("white")
#             message.title()
#         else:
#             if is_gameover and not is_clear:  # ゲームオーバーしたとき
#                 message.gameover()
#             else:  # クリアしたとき
#                 message.clear()

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.KEYDOWN:
#                     if event.key == K_ESCAPE:  # escキーでゲームを終了
#                         pygame.quit()
#                         sys.exit()

#                     if event.key == K_RETURN:  # enterが押されたとき
#                         screen.fill("white")
#                         message.title()
#                         sound.decide()
#                         is_title = True
#                         select_num = 0

#                     elif event.key == K_SPACE:
#                         sound.decide()
#                         game_started = True

#         pygame.display.update()

#         # ------------------------------------------------------------------------------------------------------------------
#         # タイトル画面での処理
#         while is_title:
#             # ゲーム開始の処理
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.KEYDOWN:
#                     if event.key == K_ESCAPE:  # escキーでゲームを終了
#                         pygame.quit()
#                         sys.exit()

#                     # タイトル画面でオプションを選んでいるとき
#                     if option_window == 0:
#                         # 矢印キーの上下が押されたとき、対応する選択肢の文字を大きくする
#                         if event.key == K_DOWN:
#                             select_num += 1
#                             sound.select()
#                         elif event.key == K_UP:
#                             select_num -= 1
#                             sound.select()
#                         select_num = select_num % len(message.words)  # 値が大きすぎたりマイナスになるのを回避
#                         message.select()
#                         pygame.display.update()

#                         # 選択肢が選ばれたとき
#                         if event.key == K_RETURN:  # enterが押されたとき
#                             if message.words[select_num] == "OPTION":
#                                 select_num = 0
#                                 option_window = 1
#                                 sound.decide()
#                                 message.option(Ball_num, Ball_Speed)
#                                 pygame.display.update()
#                             elif message.words[select_num] == "QUIT":
#                                 sound.decide()
#                                 pygame.quit()
#                                 sys.exit()
                    
#                     # オプションの中身を表示している場合
#                     if option_window == 1:
#                         # 矢印キーを押したとき、対応する文字を大きくするための変数管理
#                         if event.key == K_DOWN:
#                             select_num += 1
#                             sound.select()
#                         elif event.key == K_UP:
#                             select_num -= 1
#                             sound.select()
#                         select_num = select_num % len(message.options) 

#                         # 該当するオプションの数値を増減させる
#                         if event.key == K_RIGHT:
#                             if message.options[select_num] == "NUM BALL":
#                                 Ball_num += 1
#                                 sound.select()
#                             elif message.options[select_num] == "BALL SPEED":
#                                 Ball_Speed += .1
#                                 sound.select()
#                         elif event.key == K_LEFT:
#                             if message.options[select_num] == "NUM BALL":
#                                 Ball_num -= 1
#                                 sound.select()
#                             elif message.options[select_num] == "BALL SPEED":
#                                 Ball_Speed -= .1
#                                 sound.select()
#                         Ball_num = Ball_num % 11  # 0~10の範囲内のみ
#                         Ball_Speed = Ball_Speed % 5.1  # 0.0~5.0の範囲内のみ
#                         Ball_Speed = round(Ball_Speed, 2)  # 少数第2位を四捨五入

#                         message.option(Ball_num, Ball_Speed)
#                         pygame.display.update()

#                         # 選択肢が選ばれたとき
#                         if event.key == K_RETURN:  # enterが押されたとき
#                             if message.options[select_num] == "TITLE":
#                                 select_num = 0
#                                 option_window = 0
#                                 sound.decide()
#                                 message.select()
#                                 pygame.display.update()

#                     # スペースキーが押されたらゲームを開始する
#                     if event.key == pygame.K_SPACE:
#                         sound.decide()
#                         game_started = True
#                         is_title = False


#     # ゲームが開始されている場合
#     set_up = False
#     is_gameover = False
#     is_clear = False
#     while game_started:

#         # ------------------------------------------------------------------------------------------------------------------
#         # ゲーム開始時の初回設定
#         if not set_up:
#             screen.fill("white")
#             # ゲーム画面、インフォメーション画面の作成
#             pygame.draw.rect(screen, "black", Rect(game_x, game_y, game_screen_W, game_screen_H),4)
#             pygame.draw.rect(screen, "black", Rect(info_x, info_y, info_screen_W, info_screen_H), line_width)

#             # 各ブロック、各ボールの生成
#             blocks = [Block(screen, ix*Block_Width + game_x + line_width, iy*Block_Height + game_y, random.choice(COLORS)) for ix in range(game_screen_W//Block_Width) for iy in range(Block_pos_lim//Block_Height)]
#             balls = [Ball(screen,x0,y0) for i in range(Ball_num)]
#             # バーの位置の初期化
#             BAR_x = game_screen_W/2  # バーの中心x座標
#             bar = Bar(screen, BAR_x)
#             move_left = False
#             move_right = False
#             val_decoded = 0

#             SCORE = 0  # スコア
#             message.info(SCORE, 0)  # スコアの表示
#             pre_time = time.time()  # 現在の時刻を取得
#             limit_num = 0  # 開始直後に動けるボールの数（下の方で増える処理がある）

#             set_up = True  # 準備完了
#             pygame.display.update()
#             pygame.time.delay(500)

        

#         # メインループ
#         if not is_gameover or not is_clear:
#             # clock.tick(fps)
#             # ------------------------------------------------------ bar ------------------------------------------------------------
#             if control_name[control_mode] == "Key":
#                 move_right, move_left, BAR_x, pre_x = bar.input_key(move_right, move_left, BAR_x)
#             elif control_name[control_mode] == "Resist":
#                 pre_x = BAR_x  # 動かす前のバーのx座標を保存
#                 data = ser.readline().decode().strip()  # データを文字列として受信し、空白文字を除去する
#                 try:
#                     value = int(data)
#                     BAR_x = game_x + Bar_Width/2 + (game_screen_W - line_width - Bar_Width) * round((Resist_MAX - value) / (Resist_MAX - Resist_MIN), 2)
#                     message.info(SCORE, val_decoded)
#                 except ValueError:
#                     continue

#             bar.move(pre_x, BAR_x)

#             # ------------------------------------------------------ ball ------------------------------------------------------------
#             for index, ball in enumerate(balls):  # 動かすボールとそのインデックスを取得
#                 ball.move()
#                 ball.check_collision()
#                 # ブロックとの接触判定
#                 for block in blocks:
#                     if block.check_collision_x(ball.x, ball.y):
#                         blocks.remove(block)
#                         sound.breaks()
#                         SCORE += 10
#                         message.info(SCORE, val_decoded)
#                         ball.vel_x *= -1
#                     elif block.check_collision_y(ball.x, ball.y):
#                         blocks.remove(block)
#                         sound.breaks()
#                         SCORE += 10
#                         message.info(SCORE, val_decoded)
#                         ball.vel_y *= -1


#                 # 残りのブロック数が少なくなるほどボールスピードが速くなる
#                 ball.accel = round(2.0 - len(blocks) / (Block_num_B * Block_num_V), 3)


#                 # ボールが画面底部を抜けたとき
#                 if ball.y - ball.r >= game_screen_H:
#                     balls.remove(ball)
#                     pygame.draw.circle(screen, "white", (ball.x, ball.y), ball.r)
#                     if len(balls) == 0:  # ボールが全てなくなったとき
#                         is_gameover = True
#                         game_started = False


#                 # ゲーム開始時のボール待機の処理
#                 if limit_num < Ball_num - 1:
#                     now_time = time.time()  # 現在の時刻を取得
#                     index += 1  # 現在動いているボールの番号

#                     # ここでブレイクすることで、後続のボールが動く前に次のループに入る
#                     if index > limit_num:
#                         if now_time - pre_time < Ball_delay:  # 経過時間が待機時間より短いとき
#                             break
#                         else:  # 充分待機したとき
#                             pre_time = now_time
#                             limit_num += 1  # 何番のボールまで動けるかを数える
#                             break

#             # ------------------------------------------------------ clear ------------------------------------------------------------
#             # 残りのブロック数が0になったとき（クリアしたとき）
#             if len(blocks) == 0:
#                 SCORE += len(balls) * Ball_score  # 残りのボールの数得点が加算
#                 is_clear = True
#                 game_started = False
            
            
#             # 画面を更新する
#             pygame.draw.rect(screen, "black", Rect(2*blank, blank, game_screen_W, game_screen_H),4)  # なぜか欠けるからゲーム画面の枠線を書き直し
#             pygame.display.update()
#             pygame.time.delay(1)
        

# # Pygameの終了
# pygame.quit()
# sys.exit()