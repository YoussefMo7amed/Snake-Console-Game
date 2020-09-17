from time import time as current_time
import curses as cur
from curses import textpad as txp
from random import randint as ran
from pandas import read_csv
from pandas import DataFrame
from datetime import datetime


def settings(level):
    # 150 = easy
    df = DataFrame({"default": 150, "user": level}, index=[0])
    df.to_csv("settings.csv", index=False)


class levels:
    easy = int(150)
    normal = int(100)
    hard = int(50)
    current = read_csv("settings.csv")["user"]


class keys:
    up = cur.KEY_UP
    down = cur.KEY_DOWN
    right = cur.KEY_RIGHT
    left = cur.KEY_LEFT
    enter = cur.KEY_ENTER
    exit = cur.KEY_EXIT


def token_time(start, end):
    token = int(end - start)
    h, m, s = 0, 0, 0
    h = int(token / (60 * 60))
    token = (token % (60 * 60))
    m = int(token / 60)
    token = token % 60
    s = token
    time = "{:02d}:{:02d}:{:02d}".format(h, m, s)
    return time


def getting_food(snake, box):
    food = None
    while food is None:
        # random position between [Upper Y + 1 , Lower Y - 1], [Left X + 1, Right X - 1]
        food = [ran(box[0][0] + 1, box[1][0] - 1), ran(box[0][1] + 1, box[1][1] - 1)]
        if food in snake:
            food = None
    return food


def lose(snake, box):
    # if snake touches the box borders
    # snake_head_y in box_upper_y, box_lower_y or snake_head_x in box_upper_x, box_lower_x
    if snake[0][0] in (box[0][0], box[1][0]) or snake[0][1] in (box[0][1], box[1][1]):
        return True
    # if snake touches itself
    # snake_y_x in snake_body_ys_xs
    if snake[0] in snake[1:]:
        return True
    return False


def play(scr):
    score = 0

    cur.curs_set(0)
    # will not wait the user to enter any thing
    scr.nodelay(1)
    # just wait the user 500 msec to press something then it begin
    lvl = int(levels.current)
    scr.timeout(lvl)
    # get screen max height and width
    sh, sw = scr.getmaxyx()
    # border from the max h, w
    c = 3
    # center of the screen (must be integer)
    center_y, center_x = sh // 2, sw // 2
    box = [[c, c], [sh - c, sw - c]]
    # screen, upper_left_Y, upper_left_X, lower_Right_Y, lower_Right_X
    txp.rectangle(scr, box[0][0], box[0][1], box[1][0], box[1][1])

    # initial position for the snake is the (center),
    # the snake has three '#' each one has its own (y, x) position
    # [head[y,x], center[y,x], tail[y,x]]
    snake = [[center_y, center_x + 1], [center_y, center_x], [center_y, center_x - 1]]
    # initial direction = right
    dirct = keys.right

    start_time = current_time()
    for y, x in snake:
        scr.addstr(y, x, "0")
    # always work till snake hit the box
    food = getting_food(snake, box)
    scr.addstr(food[0], food[1], "x")
    HI = int(highest_score(scr))

    # the variable is to calculate specific period of time before speed goes up
    # start time
    time_to_speed_start = current_time()
    while True:
        time_to_speed_end = current_time()
        rate = 5
        new_period = 7
        # increase speed every "new_period" seconds by "rate" speed
        if time_to_speed_end - time_to_speed_start >= new_period and lvl >= 30:
            time_to_speed_start = time_to_speed_end
            lvl -= rate
            scr.timeout(lvl)

        score_message = "Your Score is ({})".format(score)
        scr.addstr(1, center_x - len(score_message) // 2, score_message)

        TIME = token_time(start_time, current_time())
        TIME = str(TIME)
        scr.addstr((box[1][0] + 1), box[0][1] + 1, TIME)

        HI_text = "HI: {:02d}".format(int(HI))
        scr.addstr((box[1][0] + 1), box[1][1] - len(HI_text), HI_text)

        key = scr.getch()

        # if the snake going left and user press right key, the snake eats its second cell in the body
        # e.g.
        # <###  snake going left
        # user press right
        # >###  snake eats its second cell
        # snake dies
        # so here the code ignore that, because its so annoying, but if you want to cancel it
        # just put " dirct = key " and the big if condition and add "up" and "down" keys to the condition
        if key in [keys.right, keys.left]:
            if dirct == keys.right and key == keys.left:
                dirct = keys.right
            elif dirct == keys.left and key == keys.right:
                dirct == keys.left
            else:
                dirct = key
        if key in [keys.down, keys.up]:
            if dirct == keys.down and key == keys.up:
                dirct = keys.down
            elif dirct == keys.up and key == keys.down:
                dirct == keys.up
            else:
                dirct = key

        snake_head = snake[0]

        if dirct == keys.right:
            new_head = [snake_head[0], snake_head[1] + 1]
        elif dirct == keys.left:
            new_head = [snake_head[0], snake_head[1] - 1]
        elif dirct == keys.down:
            new_head = [snake_head[0] + 1, snake_head[1]]
        elif dirct == keys.up:
            new_head = [snake_head[0] - 1, snake_head[1]]

        snake.insert(0, new_head)
        # print the new head cell
        scr.addstr(new_head[0], new_head[1], "0")

        if snake[0] == food:
            score += 1
            food = getting_food(snake, box)
            scr.addstr(food[0], food[1], "x")
        else:
            # hide the tail cell (because the snake moved one cell)
            scr.addstr(snake[-1][0], snake[-1][1], " ")
            # pop the tail cell
            snake.pop()

        # if snake lose by touching borders or itself
        if lose(snake, box):
            TIME = token_time(start_time, current_time())
            all_time = "finished in {}".format(TIME)
            message = "Game Over!"
            scr.addstr(center_y, center_x - len(message) // 2, message)
            scr.addstr(center_y + 2, center_x - len(score_message) // 2, score_message)
            scr.addstr(center_y + 4, center_x - len(all_time) // 2, all_time)
            scr.nodelay(0)
            scr.getch()
            return score, TIME
        scr.refresh()


def prev_score(scr):
    title = (" # | {:{align}{width}} | {:{align}{width}} |"
             " {:{align}{width}}|".format("Date", "Score", "Time", align='^', width=20))
    scr.clear()
    h, w = scr.getmaxyx()
    y, x = 0, w // 2
    scr.addstr(y, x - len(title) // 2, title)
    y += 1
    scr.addstr(y, x - len(title) // 2, "_" * len(title))
    y += 1

    h -= 2
    st = 0
    df = read_csv("scores.csv")
    lnth = len(df)

    if lnth >= h:
        st = lnth - h
    df = df.iloc[st:lnth]
    for i in range(len(df)):
        date, score, TIME = df.iloc[i]["date"], df.iloc[i]["score"], df.iloc[i]["time_token"]
        row = ("{:02d} | {:{align}{width}} | {:{align}{width}} |"
               " {:{align}{width}}|".format(i + 1, date, score, TIME, align='^', width=20))
        scr.addstr(y + i, x - len(row) // 2, row)


def print_highest_score(scr):
    mx = highest_score(scr)
    h, w = scr.getmaxyx()
    y, x = h // 2, w // 2
    message = "The Highest Score is"
    scr.addstr(y, x - len(message) // 2, message)
    scr.addstr(y + 2, x - len(str(mx)), str(mx))


def highest_score(scr):
    df = read_csv("scores.csv")
    mx = df["score"].max()
    if str(mx) == 'nan':
        mx = 0
    return int(mx)


def navigate(scr, menu):
    select_idx = 0
    print_menu(scr, select_idx, menu)
    while True:
        key = scr.getch()
        if key == keys.up:
            select_idx -= 1
            if select_idx < 0:
                select_idx = len(menu) - 1
            select_idx %= len(menu)
        elif key == keys.down:
            select_idx += 1
            if select_idx == len(menu):
                select_idx = 0
            select_idx %= len(menu)
        elif key == keys.enter or key in [10, 13]:
            return select_idx
        print_menu(scr, select_idx, menu)


def print_level(scr):
    select_idx = 0
    menu = ["Easy", "Normal", "Hard", "back"]
    print_menu(scr, select_idx, menu)
    select_idx = navigate(scr, menu)
    if select_idx == 0:
        levels.current = levels.easy
        settings(levels.current)
    elif select_idx == 1:
        levels.current = levels.normal
        settings(levels.current)
    elif select_idx == 2:
        levels.current = levels.hard
        settings(levels.current)
    else:
        return
    scr.refresh()


def are_u_sure(scr):
    scr.clear()
    menu = ["YES: Delete All Scores", "Cancel (back)"]
    message = "Are you sure?"
    scr.addstr(0, scr.getmaxyx()[1] // 2 - len(message) // 2, message)
    scr.refresh()
    select_idx = navigate(scr, menu)
    while True:
        scr.refresh()
        if select_idx == 0:
            return True
        else:
            return False


def options(scr):
    # levels, reset scores
    scr.clear()
    menu = ["difficulty", "reset scores", "back"]
    select_idx = navigate(scr, menu)
    while True:
        scr.refresh()
        if select_idx == 0:
            print_level(scr)
        elif select_idx == 1:
            response = are_u_sure(scr)
            if response:
                reset_data()
            else:
                return
        else:
            return
        select_idx = navigate(scr, menu)


def print_menu(scr, selected_id, menu):
    # screen height, screen width
    scr.clear()
    h, w = scr.getmaxyx()
    for idx, row in enumerate(menu):
        x = w // 2 - len(row) // 2
        y = h // 2 - len(menu) // 2 + idx
        if idx == selected_id:
            scr.attron(cur.color_pair(1))
            scr.addstr(y, x, row)
            scr.attroff(cur.color_pair(1))
        else:
            scr.addstr(y, x, row)
    scr.refresh()


def add_score(score, time_token):
    df = read_csv("scores.csv")
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ls = [date, score, time_token]
    row = DataFrame(dict(zip(df.columns, ls)), index=[0])
    df = df.append(row, ignore_index=True)
    df.to_csv("scores.csv", index=False)


def reset_data():
    df = read_csv("scores.csv")
    df = DataFrame(columns=df.columns)
    df.to_csv("scores.csv", index=False)


# play, prev scores and highest score, Options ,exit
def main_scr(scr):
    cur.curs_set(0)
    menu = ["Play", "Previous Scores", "Highest Score", "Options", "Exit"]

    # id, font, font-background
    cur.init_pair(1, cur.COLOR_BLACK, cur.COLOR_WHITE)

    select_idx = 0
    # to print the menu
    print_menu(scr, select_idx, menu)

    while 1:
        # read keyboard
        key = scr.getch()
        if key == keys.up:
            select_idx -= 1
            if select_idx < 0:
                select_idx = len(menu) - 1
            select_idx %= len(menu)  # if it reaches the top then it appears in bottom
        elif key == keys.down:
            select_idx += 1
            if select_idx == len(menu):
                select_idx = 0
            select_idx %= len(menu)  # if it reaches the bottom then it appears in top
        # when user press "Enter" key
        elif key == keys.enter or key in [10, 13]:
            # clear the screen; so i can print other sceens
            scr.clear()
            if select_idx == 0:
                score, TIME = play(scr)
                add_score(score, TIME)
            elif select_idx == 1:
                prev_score(scr)
            elif select_idx == 2:
                print_highest_score(scr)
            elif menu[select_idx] == menu[3]:
                options(scr)
            else:
                exit()
            scr.refresh()
            scr.getch()
        print_menu(scr, select_idx, menu)
        scr.refresh()


def main(scr):
    # this function from curses to handle all changes with the terminal after finishing the program
    cur.wrapper(scr)


if __name__ == '__main__':
    # passing "main_scr" function to "main" function; so it runs curses
    main(main_scr)
