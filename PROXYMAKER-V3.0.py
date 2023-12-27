import csv
import os
import sys
import time
import subprocess
from tabulate import tabulate



day = ''
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
all_teachers_list = []
absent_teachers_list = []
vacancy_list = [0,0,0,0,0,0,0,0]
teacher_availibity_list=[0,0,0,0,0,0,0,0]
class_availibility =[0,0,0,0,0,0,0,0]
selected_teachs = []
proxy_teacher_list = []


def day_finder():
    global day
    while True:
        day = input("what is today's Day ? : ").upper().replace(" ","")
        days = ['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY']
        if day == "Q":
            exit()
        elif day in days:
            break
        else:
            day = ""
            print("Enter a valid date !! ")
            time.sleep(0.5)
            refresh_screen()
            main_menu()
def generate_absent_list(teacher, db_reader):
    global absent_teachers_list
    Teacher_db.seek(0)
    n= 4
    while n>0:
        next(db_reader)
        n -= 1

    for row in db_reader:
        teacher_name = row[1].replace(" ", "").lower().lstrip()
        part = teacher_name.split("(")
        cleaned_teacher_name = part[0].lower().replace("ms.", "").replace("mr.", "").replace(" ","")
        cleaned_teacher_initial = part[1].replace(")","")
        if cleaned_teacher_name in teacher or cleaned_teacher_initial in teacher:
            absent_teachers_list.append(row)

    return absent_teachers_list

def convrt_str_to_list(l):
    simple_list = list(l.replace(" ","").split(","))
    return simple_list

def refresh_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    logo()

def enclose_boxes(prin_txt):
    command = f'echo {prin_txt} | boxes -d parchment | lolcat -f'
    try:
        output = subprocess.run(command, shell=True, text=True, capture_output=True)
        print(output.stdout)
    except subprocess.CalledProcessError as e:
        print(f"command failed with error ",{e})

def colorize(prin_txt):
    command = f"echo {prin_txt} |lolcat -a -d 100 -F 10000000000000000000"
    output = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(output.stdout)

def get_all_teachers(db_reader):
    global all_teachers_list 
    all_teachers_list = []
    Teacher_db.seek(0)
    n= 4
    while n>0:
        next(db_reader)
        n= n-1

    for row in db_reader:
        teacher_name = row[1].replace(" ","").lower()
        if teacher_name == "":
            continue
        all_teachers_list.append(f"{teacher_name}")
        # print(all_teachers_list)                   debuggging line 
    return all_teachers_list

def absent_teachers(absent_teachers_name, db_reader):
    print("------------------------------")
    for name in absent_teachers_name:
        print(f"   Checking for {name}")
    generate_absent_list(absent_teachers_name, db_reader)
    print(f"\n>>> Absent Teachers List generated successfully....")
    print("------------------------------")
    create_proxies() 
    return

def i_reduce_redundancy(period_no,other_teacher_in_same_period):   # generates a list of teachers who are present in some random period
    if teacher_availibity_list[period_no-1] != 0:
        if (teacher_availibity_list[period_no-1].count(other_teacher_in_same_period[0])) > 0:
            None
        else:
            teacher_availibity_list[period_no-1] = teacher_availibity_list[period_no-1] + f",{other_teacher_in_same_period[0]}"

    else:
        teacher_availibity_list[period_no-1] = other_teacher_in_same_period[0]

def div_list(unprocessed_list):
    list_len = len(unprocessed_list)
    n = list_len // 5  

    if list_len % 5 != 0:
        n += 1  # Increment n if there's a remainder

    processed_lists = []
    for i in range(0, n):
        processed_list = unprocessed_list[i*5 : (i+1)*5]  
        processed_lists.append(processed_list)

    return processed_lists

def centre_txt(text,artifacts):
    if artifacts: # specially use this for notorios strings and arts that just wont print correctly 
        logo_lines = text.split("\n")
 
        max_line_width = max(len(line) for line in logo_lines) # This calculates the maximum width of any line, almost killed me haaaaah

        terminal_width = os.get_terminal_size().columns
        padding = (terminal_width - max_line_width) // 2
        for line in logo_lines:
            centered_line = " " * padding + line
            print(centered_line)
    else:
        terminal_width = os.get_terminal_size().columns
        padding = (terminal_width - len(text)) // 2
        centered_text = " " * padding + text
        print(centered_text)

def centre_table(table,type,header=False):
    if not header:
        table_str = tabulate(table,tablefmt=type,showindex=False)
    else:
        table_str = tabulate(table,tablefmt=type,showindex=False, headers=header)
    # head_out = tabulate(Header, tablefmt='grid',showindex=False)     just for reference yeah
    terminal_width = os.get_terminal_size().columns
    padding = (terminal_width - len(table_str.split("\n")[0])) // 2

    # Print the table with centered padding ,, don't forget 
    for line in table_str.split("\n"):
        centered_table = " " * padding + line
        print(centered_table)


def create_proxies():
    global db_reader

    # print(absent_teachers_list)
    for teacher_info in absent_teachers_list:  
        centre_txt("==================================================================================================", False)
        centre_txt(f"Alloting proxy classes for {teacher_info[1]}.......", False)
        centre_table([["Default schedule"]],"fancy_grid")
        centre_table([teacher_info[2:]], "fancy_grid")
        period_no = 0
        

        for classes in teacher_info[2:]:
            if classes != "BREAK" and classes != "SHORT BREAK" :
                period_no += 1

            if classes != "" and classes != "BREAK" and classes != "SHORT BREAK":
                # print(f"{period_no} period is in class {classes} ")
                reallocation = True
                vacancy_list[period_no-1] += 1
            else:
                reallocation = False

            # print(f"{classes} , reallocation variable is {reallocation} ")

            if reallocation is True:
                Teacher_db.seek(0)
                next(db_reader)
                next(db_reader)
                # print(">>> Free teachers in this period are as follows:")
                global proxy_teacher_list
                proxy_teacher_list = []
                # print(f"i was executed at {period_no} 1 " )
                for other_teacher_in_same_period in db_reader:
                    
                    compare_name = other_teacher_in_same_period[1].replace(" ", "").lower().replace("ms.","").replace("mr.","").split("(")[0]
                    compare_alias = other_teacher_in_same_period[1].replace(" ", "").lower().replace("ms.","").replace("mr.","").split("(")[-1].replace(")","")
                    # compare_alias = other_teacher_in_same_period[1].replace(" ", "").lower().replace("ms.","").replace("mr.","").split("(")[1].replace(")","")  # debugging Flags 
                    # # comp_teacher_name = comp_value[0]
                    # print("comparision name : ",compare_name,"compare alias :",compare_alias)      # debugging Flags  
                    if compare_name in selected_teachs or compare_alias in selected_teachs:
                        # print(f"i was executed at {period_no} 2 " )
                        continue

                    
                    if period_no > 6:
                        # print(f"i was executed at {period_no} 4")
                        # print(other_teacher_in_same_period[period_no+2], end="")
                        # print(other_teacher_in_same_period[period_no+3])
                        # print(f"i was executed at {period_no} 3")
                        
                        if other_teacher_in_same_period[period_no+3] == "":
                            proxy_teacher_list.append([other_teacher_in_same_period[1]])
                            # print(f"    {other_teacher_in_same_period[1]}")
                            # i_reduce_redundancy(period_no,other_teacher_in_same_period)
                        

                    elif period_no > 3:     # definately blasted my head 

                        if other_teacher_in_same_period[period_no+2] == "":
                            proxy_teacher_list.append([other_teacher_in_same_period[1]])
                            # print(f"    {other_teacher_in_same_period[1]}")
                            # i_reduce_redundancy(period_no,other_teacher_in_same_period)

                    else:
                        if other_teacher_in_same_period[period_no+1] == "":
                            proxy_teacher_list.append([other_teacher_in_same_period[1]])
                            # print(f"    {other_teacher_in_same_period[1]}")
                            # i_reduce_redundancy(period_no,other_teacher_in_same_period)
            if classes != "BREAK" and classes != "SHORT BREAK" and reallocation:  
                if str(period_no)[-1] == "1":
                    centre_table(proxy_teacher_list, header=[f"Teacher Available in {period_no}st period"], type="fancy_grid")  
                elif str(period_no)[-1] == "2":
                    centre_table(proxy_teacher_list, header=[f"Teacher Available in {period_no}nd period"], type="fancy_grid")  
                elif str(period_no)[-1] == "3":
                    centre_table(proxy_teacher_list, header=[f"Teacher Available in {period_no}rd period"], type="fancy_grid")
                else:
                    
                    centre_table(proxy_teacher_list, header=[f"Teacher Available in {period_no}th period"], type="fancy_grid")
                   
                   
                    # save_reallocation_data(realloctaed_list)  
        # if teacher_availibity_list[period_no-1] == 0:
        #     Available_teachers = teacher_availibity_list[period_no-1]   #for later usage 
        #     # print(Available_teachers)
        #     print("    No, Teachers are available !!")
        print()
        period_no = 0

        centre_txt("==================================================================================================",False)
    
    return

def logo():
    global day
    logo = f"""
   _ (`-.  _  .-')              ) (`-.                        _   .-')      ('-.    .-. .-')     ('-.  _  .-')              (`-.                         
  ( (OO  )( \( -O )              ( OO ).                     ( '.( OO )_   ( OO ).-.\  ( OO )  _(  OO)( \( -O )           _(OO  )_                       
 _.`     \ ,------.  .-'),-----.(_/.  \_)-. ,--.   ,--.       ,--.   ,--.) / . --. /,--. ,--. (,------.,------.       ,--(_/   ,. \ .-----.     .----.   
(__...--'' |   /`. '( OO'  .-.  '\  `.'  /   \  `.'  /        |   `.'   |  | \-.  \ |  .'   /  |  .---'|   /`. '      \   \   /(__//  -.   \   /  ..  \  
 |  /  | | |  /  | |/   |  | |  | \     /\ .-')     /         |         |.-'-'  |  ||      /,  |  |    |  /  | |       \   \ /   / '-' _'  |  .  /  \  . 
 |  |_.' | |  |_.' |\_) |  |\|  |  \   \ |(OO  \   /          |  |'.'|  | \| |_.'  ||     ' _)(|  '--. |  |_.' |        \   '   /,    |_  <   |  |  '  | 
 |  .___.' |  .  '.'  \ |  | |  | .'    \_)|   /  /\_         |  |   |  |  |  .-.  ||  .   \   |  .--' |  .  '.'         \     /__).-.  |  |  '  \  /  ' 
 |  |      |  |\  \    `'  '-'  '/  .'.  \ `-./  /.__)        |  |   |  |  |  | |  ||  |\   \  |  `---.|  |\  \           \   /    \ `-'   /.-.\  `'  /  
 `--'      `--' '--'     `-----''--'   '--'  `--'             `--'   `--'  `--' `--'`--' '--'  `------'`--' '--'           `-'      `----'' `-' `---''   
"""
    centre_txt(logo,artifacts=True)
    print(f"Day: {day}")

def main_menu():
    main_menu = """
+----------------------------------+
|               Options            |
+----------------------------------+
| 1. Genreate Proxies              |
| 2. Change Day                    |
| 3. Credits                       |
| Q. Quit                          |
|                                  |
+----------------------------------+"""     
    
    centre_txt(main_menu,artifacts=True)

def sub_menu():
    sub_menu = """
+-----------------------------------------+
|               Options                   |
+-----------------------------------------+
| 1. View All Teachers                    |
| 2. Add Teacher                          |
| 3. Edit Selection                       |
| 4. Clear Selection                      |
| 5. Generate Proxies                     |
| 6. Clear Entire Screen                  |
| 7. Go Back To Previous Menu             |
| Q. Quit                                 |
|                                         |
+-----------------------------------------+"""
    centre_txt(sub_menu,artifacts=True)

def edit_sub_menu():
    edit_sub_menu = """
+----------------------------------+
|               Options            |
+----------------------------------+
| 1. Remove Teachers               |
| 2. Sort in order (A~Z)           |
| 3. Save Selection                |
|                                  |
+----------------------------------+"""
    centre_txt(edit_sub_menu,artifacts=True)
def credits():
    refresh_screen()
    credit = '''
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                               x                                 x                                │
│       │                                                                  ┌┐                  x                               x                   │
│       │       ┌───────────────────────────────────────────────────       ││                             x            x            x         x    │
│       │       │                                                          ││   Proxy Maker V3.0                                                   │
│       │       │                                                          ││                         x                                    x       │
│       │       │                                                          ││                                    x                                 │
│       │       │          ┌────────────────────────────────               ││   Created by : Sameer Sekhar sahu             x                      │
│       │       │          │                                       │       ││                            x             x           x               │
│       │       │          │                                       │       ││   Class      : XII-AP                                                │
│       │       │          │                                       │       ││                                                                  x   │
│       │       │          │                   ┌──────────         │       ││   Project Code : PRXMAKEV3120          x          x                  │
│       │       │          │                   │                   │       ││                                              x             x         │
│       │       │          │                   │                   │       ││   Email : Sameer.sahu8527@gamil.com                                  │
│       │       │          │                   │                   │       ││                       x                                              │
│       │       │          │                   │                   │       ││   GitHub Profile : https://github.com/pokewizardSAM    x             │
│       │       │          │                   │                   │       ││                                                                   x  │
│       │       └──────────┴───────────────────┴───────────────────┤       ││            x                                                         │
│       │                                                          │       ││                  x                                                   │
│       │                                                          │       ││       x                    x     x        x              x           │
│       │                                                          │       ││                   x     x                       x               x    │
│       │                                                          │       ││   x                                                  x               │
│       └──────────────────────────────────────────────────────────┘       ││           x                            x                    x        │
│                                                                          ││                    x             x             x                     │
│                                                                          └┘                             x                                        │
│                                                                                x                                                    x          x │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
'''
    centre_txt(credit,artifacts=True)
    Press_enter_to_continue = input("press enter to continue")
def editing_selection():
    while True:
        refresh_screen()
        edit_sub_menu()
        print(f">>> Your Selection : {selected_teachs}") 
        user_choice = input('select your options:')
        if user_choice == '1':
            rem_list = list(input("enter the position number of teachers you want to remove:").replace(" ","").split(","))
            for i in rem_list:
                i = int(i)
                del selected_teachs[i-1]
        elif user_choice == '2':
            print("yet to be implemented ")
            time.sleep(0.5)
        elif user_choice == '3':
            break
        else: 
            print("wrong input..")
            time.sleep(0.5)
def main():
    main_menu()
    global day
    day_finder()
    global db_reader
    global Teacher_db
    global selected_teachs
    global absent_teachers_list
    while True:
        refresh_screen()
        main_menu()
        usr_choice = input("Enter your choice: ")
        if usr_choice == "1":
            refresh_screen()
            try:
                while True:  # /Users/sameer/Desktop/PYTHON PROJECTS/PROXY MAKER /PROXYMAKER-V1.1.2.py
                    with open(f"{script_directory}/TIME TABLE 2023-24 - {day}.csv", "r+", newline="") as Teacher_db:
                        db_reader = csv.reader(Teacher_db)
                        # next(db_reader)
                        sub_menu()
                        if selected_teachs:
                            print(f"\n\n>>> Your Selection : {selected_teachs}") 
                        sub_user_choice = input("Choose your option:")

                        if sub_user_choice == "1":
                            refresh_screen()
                            # sub_menu()
                            centre_table(["ALL TEACHERS"],'grid')
                            centre_table(div_list(get_all_teachers(db_reader)),"fancy_grid")
                        elif sub_user_choice == "2":
                            simple_list = input('Enter the Names or Initials of the teachers separated by "," : ')
                            selected_teachs.extend(convrt_str_to_list(simple_list))
                            refresh_screen()
                        elif sub_user_choice == "3":
                            refresh_screen()    
                            editing_selection()
                            refresh_screen()
                        elif sub_user_choice == "4":
                            selected_teachs = []
                            absent_teachers_list = []
                            refresh_screen()
                        elif sub_user_choice == "5":
                            refresh_screen()
                            absent_teachers_list = []
                            absent_teachers(selected_teachs, db_reader)
                        elif sub_user_choice  == "q" or sub_user_choice == "Q":
                            exit()
                        elif sub_user_choice == "6":
                            refresh_screen()
                        elif sub_user_choice == "f":
                            print("OOPS!!! looks like you have found out some secret keys, well done. \n This part is still under construction so you can expect the features to be added in the next release")
                            print(f"This is the vacancy teller for every period from 1-8 : {vacancy_list}")
                            print(f"This right here prints the names of different teachers availabke in different periods: {teacher_availibity_list}")
                        elif sub_user_choice == "7":
                            break
                        else :
                            print("wrong input !!")
                            time.sleep(0.5)
                            refresh_screen()
            except FileNotFoundError:
                print(f"The File at {script_directory}/TIME TABLE 2023-24 - {day}.csv is missing. Perhaps you forgot putting it the parent directory ")
                time.sleep(4)

            print("\n\nAll proxies have been alloted successfully...........")
        elif usr_choice == "2":
            day_finder()
        elif usr_choice == "3":
            credits()
        elif usr_choice == "Q" or usr_choice== "q":
            exit()
        
        else:
            print(">>>invalid input")
            time.sleep(0.5)


refresh_screen()
main()


